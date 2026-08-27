#!/usr/bin/env python3
"""Run the coordinator-owned, pointer-only assisted Orca lifecycle.

The module is deliberately stdlib-only and inert when imported.  Mutating Orca
commands are issued once per logical operation; retries are limited to
read-only inspections needed to settle a late or incomplete receipt.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ORCA = os.environ.get("ORCA", "orca")
DEFAULT_INTERVAL = 0.25
DEFAULT_SETTLE_WINDOW = 60.0
DEFAULT_TURN_WINDOW = 300.0
EFFORTS = ("low", "medium", "high")
MUTATIONS = {"create", "send", "rm", "set", "stop"}
SHA40 = re.compile(r"^[0-9a-f]{40}$")


class ProbeError(RuntimeError):
    """A command or proof failed closed."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _is_mutation(argv: Iterable[str]) -> bool:
    return bool(MUTATIONS.intersection(str(value) for value in argv))


def raw(argv: list[str], timeout: float = 30.0) -> dict[str, Any]:
    """Execute fixed argv without a shell and decode one JSON response."""
    completed = subprocess.run(
        argv, capture_output=True, text=True, shell=False, timeout=timeout, check=False
    )
    if completed.returncode != 0:
        raise ProbeError(completed.stderr.strip() or f"command failed: {' '.join(argv)}")
    try:
        value = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError as error:
        raise ProbeError(f"invalid JSON from {' '.join(argv)}") from error
    if not isinstance(value, dict):
        raise ProbeError(f"non-object JSON from {' '.join(argv)}")
    return value


def resilient_run(
    argv: list[str],
    timeout: float = 30.0,
    *,
    attempts: int = 3,
    interval: float = DEFAULT_INTERVAL,
) -> dict[str, Any]:
    """Retry only read-only calls; mutation argv is always a single attempt."""
    if _is_mutation(argv):
        return raw(argv, timeout)
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            return raw(argv, timeout)
        except Exception as error:  # noqa: BLE001 - read-only retry boundary
            last = error
            if attempt + 1 < attempts:
                time.sleep(interval)
    assert last is not None
    raise last


def items(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    result = payload.get("result", payload)
    if not isinstance(result, dict):
        return []
    value = result.get(key, [])
    return value if isinstance(value, list) else []


def terminal(payload: dict[str, Any]) -> dict[str, Any]:
    result = payload.get("result", payload)
    if not isinstance(result, dict):
        return {}
    value = result.get("terminal", result)
    return value if isinstance(value, dict) else {}


def strings(value: Any, depth: int = 0) -> list[str]:
    """Extract visible strings, including JSON fragments returned as strings."""
    if depth > 12:
        return []
    if isinstance(value, dict):
        result: list[str] = []
        for key, child in value.items():
            result.append(str(key))
            result.extend(strings(child, depth + 1))
        return result
    if isinstance(value, list):
        result = []
        for child in value:
            result.extend(strings(child, depth + 1))
        return result
    if not isinstance(value, str):
        return []
    result = [value]
    try:
        decoded = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        decoded = None
    if decoded is not None and decoded != value:
        result.extend(strings(decoded, depth + 1))
    return result


def screen_text(payload: dict[str, Any]) -> str:
    return "\n".join(strings(payload))


def append(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, sort_keys=True) + "\n")


class OrcaProbe:
    """Small configured façade shared by every CLI operation."""

    def __init__(
        self,
        repo: str,
        *,
        orca: str = ORCA,
        interval: float = DEFAULT_INTERVAL,
        read_attempts: int = 3,
    ) -> None:
        if not repo:
            raise ProbeError("repository identity is required")
        self.repo = repo
        self.orca = orca
        self.interval = interval
        self.read_attempts = read_attempts

    def run(self, argv: list[str], timeout: float = 30.0) -> dict[str, Any]:
        return resilient_run(argv, timeout, attempts=self.read_attempts, interval=self.interval)

    def inventory(self) -> dict[str, Any]:
        worktrees = items(
            self.run([self.orca, "worktree", "list", "--repo", f"id:{self.repo}", "--json"]),
            "worktrees",
        )
        terminals = items(self.run([self.orca, "terminal", "list", "--json"]), "terminals")
        return {
            "at": now(),
            "worktrees": {str(value.get("id")): value for value in worktrees if value.get("id")},
            "terminals": {
                str(value.get("handle")): value for value in terminals if value.get("handle")
            },
        }

    def worktree_terminals(self, worktree_id: str) -> list[dict[str, Any]]:
        return items(
            self.run([
                self.orca,
                "terminal",
                "list",
                "--worktree",
                f"id:{worktree_id}",
                "--json",
            ]),
            "terminals",
        )


def pointer(packet_file: Path, *, worktree: Path | None = None) -> str:
    """Return the sole transport payload and reject packets inside a slice checkout."""
    packet = packet_file.resolve()
    if not packet.is_file():
        raise ProbeError(f"packet_file missing: {packet}")
    if worktree is not None:
        root = worktree.resolve()
        try:
            packet.relative_to(root)
        except ValueError:
            pass
        else:
            raise ProbeError("packet_file must be outside the slice worktree")
    return f"read {packet} and execute it as your packet"


def send_pointer(
    probe: OrcaProbe,
    handle: str,
    packet_file: Path,
    log: Path,
    *,
    worktree: Path | None = None,
    **extra: Any,
) -> dict[str, Any]:
    """Send one short pointer.  This function has no retry or fallback path."""
    payload = pointer(packet_file, worktree=worktree)
    body = packet_file.read_text(encoding="utf-8")
    sent = raw(
        [
            probe.orca,
            "terminal",
            "send",
            "--terminal",
            handle,
            "--text",
            payload,
            "--enter",
            "--json",
        ],
        timeout=20.0,
    )
    append(
        log,
        {
            "event": "pointer_sent_once",
            "at": now(),
            "handle": handle,
            "packet_file": str(packet_file.resolve()),
            "pointer": payload,
            "pointer_chars": len(payload),
            "packet_body_chars": len(body),
            "receipt": sent,
            **extra,
        },
    )
    return sent


def _receipt(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProbeError(f"invalid receipt: {path}") from error
    if not isinstance(value, dict):
        raise ProbeError("receipt must be an object")
    for key in ("id", "path", "branch", "pre_head", "startupTerminal", "before"):
        if key not in value:
            raise ProbeError(f"receipt missing {key}")
    handle = value["startupTerminal"].get("handle") if isinstance(value["startupTerminal"], dict) else None
    if not isinstance(handle, str) or not handle:
        raise ProbeError("receipt startupTerminal.handle is required")
    return value


def make_receipt(
    probe: OrcaProbe,
    candidate: dict[str, Any],
    before: dict[str, Any],
    startup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    worktree_id = str(candidate.get("id", ""))
    listed = probe.worktree_terminals(worktree_id)
    previous = set(before.get("terminals", {}))
    new = [value for value in listed if value.get("handle") not in previous]
    selected = startup or (new[0] if len(new) == 1 else None)
    if len(new) != 1 or not isinstance(selected, dict) or selected.get("handle") != new[0].get("handle"):
        raise ProbeError(f"startup handle ambiguous: {len(new)}")
    path = Path(str(candidate.get("path", ""))).resolve()
    gitdir = ""
    if path.is_dir():
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--absolute-git-dir"],
            capture_output=True,
            text=True,
            shell=False,
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            gitdir = result.stdout.strip()
    return {
        "repository": probe.repo,
        "id": worktree_id,
        "instance": candidate.get("instanceId"),
        "name": candidate.get("displayName"),
        "path": str(path),
        "gitdir": gitdir,
        "branch": candidate.get("branch"),
        "pre_head": candidate.get("head"),
        "startupTerminal": selected,
        "before": before,
        "created_at": now(),
    }


def create(args: argparse.Namespace) -> None:
    probe = OrcaProbe(args.repo, orca=args.orca, interval=args.interval)
    log = Path(args.log)
    before = probe.inventory()
    append(log, {"event": "before", **before})
    command = [
        probe.orca,
        "worktree",
        "create",
        "--repo",
        f"id:{probe.repo}",
        "--name",
        args.name,
        "--base-branch",
        args.base,
        "--setup",
        "inherit",
        "--json",
    ]
    result: dict[str, Any] | None = None
    try:
        result = raw(command, timeout=args.create_timeout)
        append(log, {"event": "create_result", "at": now(), "payload": result})
    except Exception as error:  # noqa: BLE001 - enter settle window, never retry create
        append(log, {"event": "create_missing_receipt", "at": now(), "error": str(error)})

    cumulative: dict[str, dict[str, Any]] = {}
    deadline = time.monotonic() + args.settle_window
    sample = 0
    while time.monotonic() < deadline:
        sample += 1
        try:
            current = probe.inventory()
        except Exception as error:  # noqa: BLE001 - transient read-only inventory
            append(log, {"event": "settle_sample_error", "at": now(), "sample": sample, "error": str(error)})
            time.sleep(probe.interval)
            continue
        cumulative.update({key: value for key, value in current["worktrees"].items() if key not in before["worktrees"]})
        matches = [
            value
            for value in cumulative.values()
            if value.get("repoId") == probe.repo and value.get("displayName") == args.name
        ]
        append(log, {"event": "settle_sample", "at": now(), "sample": sample,
                     "matching": [value.get("id") for value in matches],
                     "foreign_new": [value.get("id") for value in cumulative.values() if value not in matches]})
        if len(matches) == 1:
            break
        time.sleep(probe.interval)

    final = probe.inventory()
    cumulative.update({key: value for key, value in final["worktrees"].items() if key not in before["worktrees"]})
    matches = [
        value
        for value in cumulative.values()
        if value.get("repoId") == probe.repo and value.get("displayName") == args.name
    ]
    append(log, {"event": "deadline_audit", "at": now(), "matching": [value.get("id") for value in matches],
                 "foreign_new": [value.get("id") for value in cumulative.values() if value not in matches]})
    if len(matches) != 1:
        raise ProbeError(f"matching candidates={len(matches)}")
    startup = None
    if result:
        nested = result.get("result", result)
        if isinstance(nested, dict) and isinstance(nested.get("startupTerminal"), dict):
            startup = nested["startupTerminal"]
    receipt = make_receipt(probe, matches[0], before, startup)
    receipt["create_receipt_present"] = result is not None
    Path(args.receipt).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "created", "id": receipt["id"], "path": receipt["path"],
                      "branch": receipt["branch"], "pre_head": receipt["pre_head"],
                      "handle": receipt["startupTerminal"]["handle"], "settle_samples": sample,
                      "create_receipt_present": result is not None}, sort_keys=True))


def ownership(probe: OrcaProbe, receipt: dict[str, Any], log: Path) -> str:
    handle = receipt["startupTerminal"]["handle"]
    listed = probe.worktree_terminals(str(receipt["id"]))
    shown = probe.run([probe.orca, "terminal", "show", "--terminal", handle, "--json"])
    current = terminal(shown)
    preview = str(current.get("preview") or "")
    proof = {
        "new": handle not in receipt["before"].get("terminals", {}),
        "sole": len(listed) == 1 and listed[0].get("handle") == handle,
        "unused": current.get("connected") is True and current.get("writable") is True
        and current.get("agentWait") is None and preview.rstrip().endswith("❯")
        and re.search(r"(?i)(ask\s+\w+\s+to do anything|working|processing)", preview) is None,
    }
    append(log, {"event": "startup_proof", "at": now(), **proof, "shown": shown})
    if not all(proof.values()):
        raise ProbeError("startup ownership/unused proof failed")
    return handle


def route(args: argparse.Namespace) -> None:
    probe = OrcaProbe(args.repo, orca=args.orca, interval=args.interval)
    log = Path(args.log)
    receipt = _receipt(Path(args.receipt))
    handle = ownership(probe, receipt, log)
    route_cmd = f"exec {args.provider} --model {args.model} --effort {args.effort}"
    sent = raw([probe.orca, "terminal", "send", "--terminal", handle, "--text", route_cmd,
                "--enter", "--json"], timeout=args.send_timeout)
    append(log, {"event": "route_sent_once", "at": now(), "handle": handle, "route": route_cmd, "receipt": sent})
    consecutive = 0
    deadline = time.monotonic() + args.timeout
    sample = 0
    while time.monotonic() < deadline:
        sample += 1
        shown = probe.run([probe.orca, "terminal", "show", "--terminal", handle, "--json"])
        read = probe.run([probe.orca, "terminal", "read", "--terminal", handle, "--screen", "--json"])
        text = screen_text(read)
        current = terminal(shown)
        rendered = terminal(read)
        match = (current.get("connected") is True and rendered.get("source") == "screen"
                 and args.provider in text and args.model in text and f"with {args.effort} effort" in text
                 and all(f"with {effort} effort" not in text for effort in EFFORTS if effort != args.effort))
        consecutive = consecutive + 1 if match else 0
        append(log, {"event": "route_sample", "at": now(), "sample": sample, "match": match,
                     "consecutive": consecutive, "connected": current.get("connected"),
                     "source": rendered.get("source"), "tail": text[-2000:]})
        if consecutive == 1:
            try:
                hint = probe.run([probe.orca, "terminal", "wait", "--terminal", handle,
                                  "--for", "tui-idle", "--timeout-ms", "5000", "--json"], timeout=7)
                append(log, {"event": "idle_hint", "at": now(), "receipt": hint})
            except Exception as error:  # noqa: BLE001 - hint only
                append(log, {"event": "idle_hint_failed", "at": now(), "error": str(error)})
        if consecutive >= 2:
            print(json.dumps({"status": "accepted", "handle": handle, "samples": sample,
                              "provider": args.provider, "model": args.model, "effort": args.effort}, sort_keys=True))
            return
        time.sleep(probe.interval)
    raise ProbeError(f"rendered route timeout: {route_cmd}")


def is_working(text: str) -> bool:
    return bool(re.search(r"(?i)(esc to interrupt|working|processing)", text))


def marker_frame(probe: OrcaProbe, handle: str, phase: str) -> tuple[str | None, str | None, dict[str, Any], dict[str, Any], str]:
    shown = probe.run([probe.orca, "terminal", "show", "--terminal", handle, "--json"])
    read = probe.run([probe.orca, "terminal", "read", "--terminal", handle, "--screen", "--json"])
    current = terminal(shown)
    rendered = terminal(read)
    text = screen_text(read)
    matches = re.findall(rf"TURN_DONE\s+{re.escape(phase)}\s+head=([0-9a-f]{{40}})", text)
    if current.get("connected") is not True:
        return None, "disconnected", shown, read, text
    if rendered.get("source") != "screen":
        return None, "source-not-screen", shown, read, text
    if len(matches) != 1:
        return None, f"marker-count={len(matches)}", shown, read, text
    if is_working(text):
        return None, "working", shown, read, text
    return matches[0], None, shown, read, text


def git(path: str | Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True,
                            shell=False, timeout=30, check=False)
    if check and result.returncode != 0:
        raise ProbeError(result.stderr.strip() or "git command failed")
    return result


def task_states(path: str | Path, task_file: str = "tasks.md") -> dict[str, str]:
    file = Path(path) / task_file
    if not file.is_file():
        return {}
    result: dict[str, str] = {}
    for line in file.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\s*- \[([ xX])\]\s+([^ —–]+)", line)
        if match:
            result[match.group(2)] = "complete" if match.group(1).lower() == "x" else "pending"
    return result


def gate(path: str | Path, command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, cwd=path, capture_output=True, text=True, shell=False,
                            timeout=300, check=False)
    return {"passed": result.returncode == 0, "returncode": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}


def worktree_comment(probe: OrcaProbe, worktree_id: str) -> str:
    payload = probe.run([probe.orca, "worktree", "show", "--worktree", f"id:{worktree_id}", "--json"])
    value = payload.get("result", payload)
    value = value.get("worktree", value) if isinstance(value, dict) else {}
    return str(value.get("comment") or "") if isinstance(value, dict) else ""


def effect(args: argparse.Namespace, probe: OrcaProbe, receipt: dict[str, Any], sent: dict[str, Any]) -> dict[str, Any]:
    handle = receipt["startupTerminal"]["handle"]
    deadline = time.monotonic() + args.timeout
    sample = 0
    while time.monotonic() < deadline:
        sample += 1
        head, error, shown, read, text = marker_frame(probe, handle, args.phase)
        append(Path(args.log), {"event": "effect_sample", "at": now(), "phase": args.phase,
                                "sample": sample, "head": head, "error": error, "tail": text[-2500:]})
        if head:
            idle = probe.run([probe.orca, "terminal", "wait", "--terminal", handle,
                              "--for", "tui-idle", "--timeout-ms", "300000", "--json"], timeout=305)
            second_head, second_error, second_show, second_read, second_text = marker_frame(probe, handle, args.phase)
            path = receipt["path"]
            actual_head = git(path, "rev-parse", "HEAD").stdout.strip()
            ancestry = git(path, "merge-base", "--is-ancestor", args.pre_head, head, check=False).returncode == 0
            rows = [line.split("\t", 1) for line in git(path, "log", "--reverse", "--format=%H%x09%s",
                                                          f"{args.pre_head}..{head}").stdout.splitlines()]
            changed = set(git(path, "diff", "--name-only", f"{args.pre_head}..{head}").stdout.splitlines())
            expected_subjects = list(args.expected_subject)
            checks = {
                "second_frame": second_error is None and second_head == head,
                "idle": idle.get("ok") is not False,
                "head": actual_head == head,
                "descends": ancestry,
                "commit_count": len(rows) == args.expected_count,
                "commit_subjects": [row[1] for row in rows] == expected_subjects,
                "paths": changed.issubset(set(args.allow_path)),
                "tasks": all(task_states(path, args.task_file).get(task) == "complete" for task in args.expected_task),
                "gate": gate(path, args.gate).get("passed") is True,
                "clean": git(path, "status", "--porcelain").stdout == "",
                "same_handle": terminal(second_show).get("handle") == handle,
            }
            expected_comment = args.park_comment.format(head=head) if args.park_comment and args.phase == "B_PARKED" else ""
            actual_comment = worktree_comment(probe, str(receipt["id"])) if expected_comment else ""
            checks["comment"] = not expected_comment or actual_comment == expected_comment
            record = {"event": "effect_reconciled", "at": now(), "phase": args.phase,
                      "handle": handle, "send_receipt_ok": sent.get("ok"), "head": head,
                      "checks": checks, "commits": rows, "changed": sorted(changed),
                      "comment": actual_comment, "second_tail": second_text[-2500:]}
            append(Path(args.log), record)
            if all(checks.values()):
                print(json.dumps({"status": "complete", "phase": args.phase, "head": head,
                                  "handle": handle, "send_receipt_ok": sent.get("ok")}, sort_keys=True))
                return record
            raise ProbeError("incomplete or ambiguous effect")
        time.sleep(probe.interval)
    raise ProbeError(f"effect timeout: {args.phase}")


def turn(args: argparse.Namespace) -> None:
    probe = OrcaProbe(args.repo, orca=args.orca, interval=args.interval)
    receipt = _receipt(Path(args.receipt))
    path = Path(receipt["path"])
    actual_pre = git(path, "rev-parse", "HEAD").stdout.strip()
    packet = Path(args.packet)
    body = packet.read_text(encoding="utf-8")
    if actual_pre != args.pre_head:
        raise ProbeError("pre_head mismatch")
    if re.search(r"TURN_DONE\s+\S+\s+head=[0-9a-f]{40}", body):
        raise ProbeError("concrete marker leaked into packet")
    if f"TURN_DONE {args.phase} head=<current exact 40-hex HEAD>" not in body:
        raise ProbeError("packet_file missing required marker requirement")
    append(Path(args.log), {"event": "packet_before", "at": now(), "phase": args.phase,
                            "turn_id": args.turn_id, "handle": receipt["startupTerminal"]["handle"],
                            "pre_head": actual_pre, "delivery": "pointer",
                            "expected_tasks": args.expected_task, "expected_count": args.expected_count,
                            "expected_subjects": args.expected_subject, "allowed_paths": args.allow_path})
    sent = send_pointer(probe, receipt["startupTerminal"]["handle"], packet, Path(args.log), worktree=path,
                        phase=args.phase, turn_id=args.turn_id)
    effect(args, probe, receipt, sent)


def set_comment(args: argparse.Namespace) -> None:
    probe = OrcaProbe(args.repo, orca=args.orca)
    result = raw([probe.orca, "worktree", "set", "--worktree", f"id:{args.worktree}",
                  "--comment", args.comment, "--json"], timeout=args.timeout)
    print(json.dumps(result, sort_keys=True))


def sync_commit(args: argparse.Namespace) -> None:
    """Bring one verified producer commit into a private dependent checkout."""
    if not SHA40.fullmatch(args.commit):
        raise ProbeError("producer commit must be a 40-hex SHA")
    current = git(args.worktree, "rev-parse", "HEAD").stdout.strip()
    if git(args.worktree, "status", "--porcelain").stdout:
        raise ProbeError("dependent worktree is dirty")
    already_present = git(args.worktree, "merge-base", "--is-ancestor", args.commit, current,
                           check=False).returncode == 0
    if not already_present:
        git(args.worktree, "cherry-pick", "--no-edit", args.commit)
    result = gate(args.worktree, args.gate)
    if result["passed"] is not True:
        raise ProbeError("affected gate failed after producer sync")
    print(json.dumps({"status": "synchronized", "commit": args.commit,
                      "already_present": already_present, "gate": result}, sort_keys=True))


def stop(args: argparse.Namespace) -> None:
    probe = OrcaProbe(args.repo, orca=args.orca)
    result = raw([probe.orca, "terminal", "stop", "--terminal", args.handle, "--json"], timeout=args.timeout)
    print(json.dumps(result, sort_keys=True))


def remove(args: argparse.Namespace) -> None:
    probe = OrcaProbe(args.repo, orca=args.orca)
    result = raw([probe.orca, "worktree", "rm", "--worktree", f"id:{args.worktree}", "--json"], timeout=args.timeout)
    print(json.dumps(result, sort_keys=True))


def cleanup(args: argparse.Namespace) -> None:
    """Stop and remove only the exact receipt resources, preserving foreign inventory entries."""
    probe = OrcaProbe(args.repo, orca=args.orca)
    receipt = _receipt(Path(args.receipt))
    before = probe.inventory()
    known = receipt["startupTerminal"]["handle"]
    listed = probe.worktree_terminals(str(receipt["id"]))
    owned = [value for value in listed if value.get("handle") == known]
    if len(owned) > 1:
        raise ProbeError("ambiguous owned terminal")
    stopped = False
    if owned:
        raw([probe.orca, "terminal", "stop", "--terminal", known, "--json"], timeout=args.timeout)
        stopped = True
    raw([probe.orca, "worktree", "rm", "--worktree", f"id:{receipt['id']}", "--json"], timeout=args.timeout)
    after = probe.inventory()
    foreign_before = set(before["worktrees"]) - {str(receipt["id"])}
    foreign_after = set(after["worktrees"]) - {str(receipt["id"])}
    foreign_terminals_before = set(before["terminals"]) - {known}
    foreign_terminals_after = set(after["terminals"]) - {known}
    if foreign_before != foreign_after or foreign_terminals_before != foreign_terminals_after:
        raise ProbeError("cleanup changed a foreign resource")
    print(json.dumps({"status": "cleaned", "worktree": receipt["id"], "handle": known,
                      "stopped": stopped, "foreign_preserved": True}, sort_keys=True))


def transport(args: argparse.Namespace) -> None:
    probe = OrcaProbe(args.repo, orca=args.orca, interval=args.interval)
    sent = send_pointer(probe, args.handle, Path(args.packet), Path(args.log))
    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        shown = probe.run([probe.orca, "terminal", "show", "--terminal", args.handle, "--json"])
        read = probe.run([probe.orca, "terminal", "read", "--terminal", args.handle, "--screen", "--json"])
        text = screen_text(read)
        if terminal(shown).get("connected") is True and terminal(read).get("source") == "screen" \
                and args.marker in text and not is_working(text):
            print(json.dumps({"status": "delivered", "send_receipt_ok": sent.get("ok")}, sort_keys=True))
            return
        time.sleep(probe.interval)
    raise ProbeError("pointer transport proof timeout")


def terminal_new(args: argparse.Namespace) -> None:
    """Create one verifier terminal in an existing owned worktree and settle its receipt."""
    probe = OrcaProbe(args.repo, orca=args.orca, interval=args.interval)
    before = {value.get("handle") for value in probe.worktree_terminals(args.worktree)}
    created = raw([probe.orca, "terminal", "create", "--worktree", f"id:{args.worktree}",
                   "--title", args.title, "--json"], timeout=args.timeout)
    deadline = time.monotonic() + args.settle_window
    found: list[dict[str, Any]] = []
    while time.monotonic() < deadline:
        found = [value for value in probe.worktree_terminals(args.worktree)
                 if value.get("handle") not in before]
        if len(found) == 1:
            break
        time.sleep(probe.interval)
    if len(found) != 1:
        raise ProbeError(f"verifier terminal candidates={len(found)}")
    if args.out:
        Path(args.out).write_text(json.dumps(found[0], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "created", "handle": found[0]["handle"], "receipt": created}, sort_keys=True))


def verifier_route(args: argparse.Namespace) -> None:
    """Prove a verifier's rendered provider/model/effort route on its exact handle."""
    probe = OrcaProbe(args.repo, orca=args.orca, interval=args.interval)
    route_cmd = f"exec {args.provider} --model {args.model} --effort {args.effort}"
    sent = raw([probe.orca, "terminal", "send", "--terminal", args.handle, "--text", route_cmd,
                "--enter", "--json"], timeout=args.send_timeout)
    consecutive = 0
    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        shown = probe.run([probe.orca, "terminal", "show", "--terminal", args.handle, "--json"])
        read = probe.run([probe.orca, "terminal", "read", "--terminal", args.handle, "--screen", "--json"])
        current, rendered = terminal(shown), terminal(read)
        text = screen_text(read)
        match = (current.get("connected") is True and rendered.get("source") == "screen"
                 and args.provider in text and args.model in text
                 and f"with {args.effort} effort" in text)
        consecutive = consecutive + 1 if match else 0
        if consecutive >= 2:
            print(json.dumps({"status": "accepted", "handle": args.handle, "route": route_cmd,
                              "send_receipt_ok": sent.get("ok")}, sort_keys=True))
            return
        time.sleep(probe.interval)
    raise ProbeError(f"rendered verifier route timeout: {route_cmd}")


def verifier_send(args: argparse.Namespace) -> None:
    probe = OrcaProbe(args.repo, orca=args.orca)
    result = send_pointer(probe, args.handle, Path(args.packet), Path(args.log), phase="VERIFIER",
                          slice=args.slice)
    print(json.dumps(result, sort_keys=True))


def wait_text(args: argparse.Namespace) -> None:
    probe = OrcaProbe(args.repo, orca=args.orca, interval=args.interval)
    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        shown = probe.run([probe.orca, "terminal", "show", "--terminal", args.handle, "--json"])
        read = probe.run([probe.orca, "terminal", "read", "--terminal", args.handle, "--screen", "--json"])
        text = screen_text(read)
        found = (terminal(shown).get("connected") is True and terminal(read).get("source") == "screen"
                 and text.count(args.marker) == 1 and not is_working(text))
        if found:
            probe.run([probe.orca, "terminal", "wait", "--terminal", args.handle,
                       "--for", "tui-idle", "--timeout-ms", "300000", "--json"], timeout=305)
            second = probe.run([probe.orca, "terminal", "read", "--terminal", args.handle,
                                "--screen", "--json"])
            second_text = screen_text(second)
            if second_text.count(args.marker) != 1 or is_working(second_text):
                raise ProbeError("marker effect incomplete")
            if args.require_file:
                required = Path(args.require_file)
                if not required.is_file() or (args.require_text and args.require_text not in required.read_text(encoding="utf-8")):
                    raise ProbeError("required file/text missing")
            print(json.dumps({"status": "complete", "marker": args.marker}, sort_keys=True))
            return
        time.sleep(probe.interval)
    raise ProbeError(f"marker timeout: {args.marker}")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--orca", default=ORCA)
    root.add_argument("--repo", required=True)
    sub = root.add_subparsers(dest="command", required=True)

    create_parser = sub.add_parser("create")
    create_parser.add_argument("--name", required=True); create_parser.add_argument("--base", required=True)
    create_parser.add_argument("--receipt", required=True); create_parser.add_argument("--log", required=True)
    create_parser.add_argument("--create-timeout", type=float, default=60.0)
    create_parser.add_argument("--settle-window", type=float, default=DEFAULT_SETTLE_WINDOW)
    create_parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL); create_parser.set_defaults(function=create)

    route_parser = sub.add_parser("route")
    route_parser.add_argument("--receipt", required=True); route_parser.add_argument("--log", required=True)
    route_parser.add_argument("--provider", required=True); route_parser.add_argument("--model", required=True)
    route_parser.add_argument("--effort", required=True, choices=EFFORTS); route_parser.add_argument("--timeout", type=float, default=90.0)
    route_parser.add_argument("--send-timeout", type=float, default=20.0); route_parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL); route_parser.set_defaults(function=route)

    turn_parser = sub.add_parser("turn")
    for name in ("receipt", "packet", "phase", "log", "pre-head", "turn-id"):
        turn_parser.add_argument(f"--{name}", required=True)
    turn_parser.add_argument("--expected-task", action="append", default=[]); turn_parser.add_argument("--expected-count", type=int, required=True)
    turn_parser.add_argument("--expected-subject", action="append", default=[]); turn_parser.add_argument("--allow-path", action="append", default=[])
    turn_parser.add_argument("--task-file", default="tasks.md"); turn_parser.add_argument("--gate", nargs="+", required=True)
    turn_parser.add_argument("--park-comment", default=""); turn_parser.add_argument("--timeout", type=float, default=DEFAULT_TURN_WINDOW)
    turn_parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL); turn_parser.set_defaults(function=turn)

    pointer_parser = sub.add_parser("send-pointer")
    pointer_parser.add_argument("--handle", required=True); pointer_parser.add_argument("--packet", required=True); pointer_parser.add_argument("--log", required=True)
    pointer_parser.add_argument("--worktree"); pointer_parser.set_defaults(function=lambda args: print(json.dumps(send_pointer(OrcaProbe(args.repo, orca=args.orca), args.handle, Path(args.packet), Path(args.log), worktree=Path(args.worktree) if args.worktree else None), sort_keys=True)))

    transport_parser = sub.add_parser("transport")
    transport_parser.add_argument("--handle", required=True); transport_parser.add_argument("--packet", required=True); transport_parser.add_argument("--marker", required=True); transport_parser.add_argument("--log", required=True)
    transport_parser.add_argument("--timeout", type=float, default=DEFAULT_TURN_WINDOW); transport_parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL); transport_parser.set_defaults(function=transport)

    terminal_parser = sub.add_parser("terminal-new")
    terminal_parser.add_argument("--worktree", required=True); terminal_parser.add_argument("--title", required=True)
    terminal_parser.add_argument("--out", default=""); terminal_parser.add_argument("--timeout", type=float, default=60.0)
    terminal_parser.add_argument("--settle-window", type=float, default=DEFAULT_SETTLE_WINDOW); terminal_parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL); terminal_parser.set_defaults(function=terminal_new)

    verifier_route_parser = sub.add_parser("verifier-route")
    verifier_route_parser.add_argument("--handle", required=True); verifier_route_parser.add_argument("--provider", required=True)
    verifier_route_parser.add_argument("--model", required=True); verifier_route_parser.add_argument("--effort", required=True, choices=EFFORTS)
    verifier_route_parser.add_argument("--timeout", type=float, default=90.0); verifier_route_parser.add_argument("--send-timeout", type=float, default=20.0); verifier_route_parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL); verifier_route_parser.set_defaults(function=verifier_route)

    verifier_send_parser = sub.add_parser("verifier-send")
    verifier_send_parser.add_argument("--handle", required=True); verifier_send_parser.add_argument("--packet", required=True); verifier_send_parser.add_argument("--slice", required=True); verifier_send_parser.add_argument("--log", required=True); verifier_send_parser.set_defaults(function=verifier_send)

    wait_parser = sub.add_parser("wait-text")
    wait_parser.add_argument("--handle", required=True); wait_parser.add_argument("--marker", required=True); wait_parser.add_argument("--timeout", type=float, default=DEFAULT_TURN_WINDOW); wait_parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL); wait_parser.add_argument("--require-file"); wait_parser.add_argument("--require-text"); wait_parser.set_defaults(function=wait_text)

    for name, function, option in (("set-comment", set_comment, "worktree"), ("stop", stop, "handle"), ("rm", remove, "worktree")):
        command_parser = sub.add_parser(name); command_parser.add_argument(f"--{option}", required=True)
        if name == "set-comment": command_parser.add_argument("--comment", required=True)
        command_parser.add_argument("--timeout", type=float, default=30.0); command_parser.set_defaults(function=function)

    sync_parser = sub.add_parser("sync")
    sync_parser.add_argument("--worktree", required=True); sync_parser.add_argument("--commit", required=True)
    sync_parser.add_argument("--gate", nargs="+", required=True); sync_parser.set_defaults(function=sync_commit)

    cleanup_parser = sub.add_parser("cleanup"); cleanup_parser.add_argument("--receipt", required=True); cleanup_parser.add_argument("--timeout", type=float, default=30.0); cleanup_parser.set_defaults(function=cleanup)
    return root


def main(argv: list[str] | None = None) -> None:
    args = parser().parse_args(argv)
    try:
        args.function(args)
    except (ProbeError, OSError, subprocess.SubprocessError) as error:
        raise SystemExit(f"FAIL_CLOSED {error}") from error


if __name__ == "__main__":
    main()
