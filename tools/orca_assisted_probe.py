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
import shlex
import shutil
import subprocess
import sys
import tempfile
from copy import deepcopy
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


ORCA = os.environ.get("ORCA", "orca")
DEFAULT_INTERVAL = 0.25
DEFAULT_SETTLE_WINDOW = 60.0
DEFAULT_TURN_WINDOW = 300.0
EFFORTS = ("low", "medium", "high")
MUTATIONS = {"create", "send", "rm", "set", "stop"}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
STATE_SCHEMA = 2
STATE_FIELDS = (
    "schema_version", "repository", "repository_root", "slice_id", "task_id",
    "operation_id", "instance", "terminal_handle", "route", "commit_id", "lease_id",
    "worktree_id", "worktree_path", "branch", "pre_head", "gitdir",
    "worktree_gitdir", "packet_path", "log_path", "receipt_path",
)
RECEIPT_FIELDS = (
    "repository", "repository_root", "slice_id", "task_id", "operation_id", "instance",
    "id", "path", "branch", "pre_head", "gitdir", "worktree_gitdir", "terminal_handle",
    "route", "commit_id", "lease_id", "startupTerminal", "before",
)


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
        runner: Callable[..., dict[str, Any]] | None = None,
    ) -> None:
        if not repo:
            raise ProbeError("repository identity is required")
        self.repo = repo
        self.orca = orca
        self.interval = interval
        self.read_attempts = read_attempts
        self.runner = runner or raw

    def run(self, argv: list[str], timeout: float = 30.0) -> dict[str, Any]:
        if self.runner is raw:
            return resilient_run(argv, timeout, attempts=self.read_attempts, interval=self.interval)
        if _is_mutation(argv):
            return self.runner(argv, timeout=timeout)
        last: Exception | None = None
        for attempt in range(self.read_attempts):
            try:
                return self.runner(argv, timeout=timeout)
            except Exception as error:  # noqa: BLE001 - read-only retry boundary
                last = error
                if attempt + 1 < self.read_attempts:
                    time.sleep(self.interval)
        assert last is not None
        raise last

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
    return f"read {shlex.quote(str(packet))} and execute it as your packet"


def _send_pointer_once(
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
    command = [
            probe.orca,
            "terminal",
            "send",
            "--terminal",
            handle,
            "--text",
            payload,
            "--enter",
            "--json",
        ]
    try:
        sent = raw(command, timeout=20.0)
    except Exception as error:  # noqa: BLE001 - one-shot mutation; caller reconciles effect
        sent = {"ok": False, "error": str(error)}
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


def mutate_once(
    probe: OrcaProbe,
    argv: list[str],
    reconcile: Any,
    *,
    timeout: float,
    settle_window: float,
    interval: float,
) -> dict[str, Any]:
    """Issue one mutation, then reconcile its same-resource effect with read-only calls."""
    try:
        receipt = raw(argv, timeout=timeout)
    except Exception as error:  # noqa: BLE001 - missing receipt is an ambiguous effect
        receipt = {"ok": False, "error": str(error)}
    deadline = time.monotonic() + settle_window
    samples = 0
    while time.monotonic() < deadline:
        samples += 1
        try:
            state = reconcile()
        except Exception as error:  # noqa: BLE001 - read-only reconciliation
            state = {"complete": False, "error": str(error)}
        if isinstance(state, dict) and state.get("complete") is True:
            return {"receipt": receipt, "reconciled": True, "samples": samples, "state": state}
        time.sleep(interval)
    raise ProbeError(f"mutation effect not reconciled after {samples} read-only samples")


def route_command(provider: str, model: str, effort: str) -> str:
    """Build the provider-specific frozen route sent to the verified shell."""
    if provider == "codex":
        setting = shlex.quote(f"model_reasoning_effort={effort}")
        return f"exec codex --model {shlex.quote(model)} -c {setting}"
    if provider == "claude":
        return f"exec claude --model {shlex.quote(model)} --effort {shlex.quote(effort)}"
    if provider == "cursor":
        cursor_model = f"{model}[effort={effort}]"
        return f"exec cursor agent --model {shlex.quote(cursor_model)}"
    raise ProbeError(f"unsupported provider route: {provider}")


def _receipt(path: Path, *, repository: str | None = None) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProbeError(f"invalid receipt: {path}") from error
    if not isinstance(value, dict):
        raise ProbeError("receipt must be an object")
    for key in ("repository", "id", "instance", "path", "branch", "pre_head", "gitdir", "worktree_gitdir", "startupTerminal", "before"):
        if key not in value:
            raise ProbeError(f"receipt missing {key}")
    if not isinstance(value["repository"], str) or not value["repository"]:
        raise ProbeError("receipt repository is required")
    if repository is not None and value["repository"] != repository:
        raise ProbeError("receipt repository does not match requested repository")
    if not isinstance(value["instance"], str) or not value["instance"]:
        raise ProbeError("receipt instance is required")
    before = value["before"]
    if not isinstance(before, dict):
        raise ProbeError("receipt before inventory must be an object")
    for key in ("terminals", "worktrees"):
        if not isinstance(before.get(key), dict):
            raise ProbeError(f"receipt before.{key} inventory must be an object")
    handle = value["startupTerminal"].get("handle") if isinstance(value["startupTerminal"], dict) else None
    if not isinstance(handle, str) or not handle:
        raise ProbeError("receipt startupTerminal.handle is required")
    if not isinstance(value["pre_head"], str) or not SHA40.fullmatch(value["pre_head"]):
        raise ProbeError("receipt pre_head must be a 40-hex SHA")
    return value


def make_receipt(
    probe: OrcaProbe,
    candidate: dict[str, Any],
    before: dict[str, Any],
    startup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    worktree_id = str(candidate.get("id", ""))
    instance = candidate.get("instanceId")
    if not worktree_id or not isinstance(instance, str) or not instance:
        raise ProbeError("create candidate lacks immutable Orca identity")
    listed = probe.worktree_terminals(worktree_id)
    previous = set(before.get("terminals", {}))
    new = [value for value in listed if value.get("handle") not in previous]
    selected = startup or (new[0] if len(new) == 1 else None)
    if len(new) != 1 or not isinstance(selected, dict) or selected.get("handle") != new[0].get("handle"):
        raise ProbeError(f"startup handle ambiguous: {len(new)}")
    candidate_path = Path(str(candidate.get("path", "")))
    if not candidate_path.is_dir() or candidate_path.is_symlink():
        raise ProbeError("create candidate path is unavailable or symlinked")
    path = candidate_path.resolve()
    try:
        gitdir = git(path, "rev-parse", "--git-common-dir").stdout.strip()
        worktree_gitdir = git(path, "rev-parse", "--absolute-git-dir").stdout.strip()
    except ProbeError as error:
        raise ProbeError("create candidate lacks complete Git checkout identity") from error
    common = Path(gitdir)
    if not common.is_absolute():
        common = path / common
    common = common.resolve()
    linked = Path(worktree_gitdir).resolve()
    if not common.is_dir() or not linked.is_dir():
        raise ProbeError("create candidate Git directories are unavailable")
    gitdir = str(common)
    worktree_gitdir = str(linked)
    branch = candidate.get("branch")
    head = candidate.get("head")
    if not isinstance(branch, str) or not branch or not isinstance(head, str) or not SHA40.fullmatch(head):
        raise ProbeError("create candidate lacks complete branch and HEAD identity")
    actual_head = git(path, "rev-parse", "HEAD").stdout.strip()
    if actual_head != head:
        raise ProbeError("create candidate HEAD does not match Orca inventory")
    return {
        "repository": probe.repo,
        "id": worktree_id,
        "instance": instance,
        "name": candidate.get("displayName"),
        "path": str(path),
        "gitdir": gitdir,
        "worktree_gitdir": worktree_gitdir,
        "branch": branch,
        "pre_head": head,
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

    try:
        final = probe.inventory()
    except Exception as error:  # noqa: BLE001 - never adopt stale cumulative evidence
        append(log, {"event": "deadline_audit_error", "at": now(), "error": str(error),
                     "recovery": "receipt-not-written"})
        raise ProbeError("final inventory unavailable; create receipt not written") from error
    cumulative.update({key: value for key, value in final["worktrees"].items() if key not in before["worktrees"]})
    matches = [
        value
        for value in cumulative.values()
        if value.get("repoId") == probe.repo and value.get("displayName") == args.name
    ]
    append(log, {"event": "deadline_audit", "at": now(), "matching": [value.get("id") for value in matches],
                 "foreign_new": [value.get("id") for value in cumulative.values() if value not in matches]})
    if len(matches) != 1:
        _cleanup_late_candidates(probe, matches, before, log, args)
        raise ProbeError(f"matching candidates={len(matches)}")
    startup = None
    if result:
        nested = result.get("result", result)
        if isinstance(nested, dict) and isinstance(nested.get("startupTerminal"), dict):
            startup = nested["startupTerminal"]
    try:
        receipt = make_receipt(probe, matches[0], before, startup)
    except ProbeError:
        _cleanup_late_candidates(probe, matches, before, log, args)
        raise
    receipt["create_receipt_present"] = result is not None
    Path(args.receipt).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "created", "id": receipt["id"], "path": receipt["path"],
                      "branch": receipt["branch"], "pre_head": receipt["pre_head"],
                      "handle": receipt["startupTerminal"]["handle"], "settle_samples": sample,
                      "create_receipt_present": result is not None}, sort_keys=True))


def _cleanup_late_candidates(
    probe: OrcaProbe,
    candidates: list[dict[str, Any]],
    before: dict[str, Any],
    log: Path,
    args: argparse.Namespace,
) -> None:
    """Remove only exact, newly observed create candidates before serial fallback."""
    prior_handles = set(before.get("terminals", {}))
    for candidate in candidates:
        worktree_id = str(candidate.get("id", ""))
        if not worktree_id:
            continue
        listed = probe.worktree_terminals(worktree_id)
        cleanup_ready = True
        for value in listed:
            handle = value.get("handle")
            if not isinstance(handle, str) or not handle:
                continue
            if handle in prior_handles:
                cleanup_ready = False
                append(log, {"event": "late_handle_ambiguous", "at": now(),
                             "worktree": worktree_id, "handle": handle,
                             "recovery": "candidate-retained"})
                continue
            try:
                result = mutate_once(
                    probe,
                    [probe.orca, "terminal", "stop", "--terminal", handle, "--json"],
                    lambda handle=handle: {"complete": all(
                        value.get("handle") != handle for value in probe.worktree_terminals(worktree_id)
                    )},
                    timeout=args.create_timeout,
                    settle_window=args.settle_window,
                    interval=args.interval,
                )
                append(log, {"event": "late_stop_reconciled", "at": now(), "worktree": worktree_id,
                             "handle": handle, "samples": result["samples"]})
            except Exception as error:  # noqa: BLE001 - preserve the original fail-closed error
                cleanup_ready = False
                append(log, {"event": "late_stop_failed", "at": now(), "worktree": worktree_id,
                             "handle": handle, "error": str(error)})
        if not cleanup_ready:
            continue
        try:
            result = mutate_once(
                probe,
                [probe.orca, "worktree", "rm", "--worktree", f"id:{worktree_id}", "--json"],
                lambda: {"complete": worktree_id not in probe.inventory()["worktrees"]},
                timeout=args.create_timeout,
                settle_window=args.settle_window,
                interval=args.interval,
            )
            append(log, {"event": "late_rm_reconciled", "at": now(), "worktree": worktree_id,
                         "samples": result["samples"]})
        except Exception as error:  # noqa: BLE001 - preserve the original fail-closed error
            append(log, {"event": "late_rm_failed", "at": now(), "worktree": worktree_id, "error": str(error)})


def ownership(probe: OrcaProbe, receipt: dict[str, Any], log: Path) -> str:
    handle = receipt["startupTerminal"]["handle"]
    listed = probe.worktree_terminals(str(receipt["id"]))
    shown = probe.run([probe.orca, "terminal", "show", "--terminal", handle, "--json"])
    current = terminal(shown)
    preview = str(current.get("preview") or "")
    activity = re.compile(
        r"(?i)(ask\s+\w+\s+to do anything|working|processing|running|executing|thinking|loading|queued|busy|in progress|esc to interrupt|default task|agent)"
    )
    proof = {
        "new": handle not in receipt["before"].get("terminals", {}),
        "sole": len(listed) == 1 and listed[0].get("handle") == handle,
        "same_handle": current.get("handle") == handle,
        "unused": current.get("connected") is True and current.get("writable") is True
        and current.get("agentWait") in (None, False) and preview.rstrip().endswith("❯")
        and activity.search(preview) is None,
    }
    append(log, {"event": "startup_proof", "at": now(), **proof, "shown": shown})
    if not all(proof.values()):
        raise ProbeError("startup ownership/unused proof failed")
    return handle


def route(args: argparse.Namespace) -> None:
    probe = OrcaProbe(args.repo, orca=args.orca, interval=args.interval)
    log = Path(args.log)
    _validate_timing(args.timeout, args.interval, maximum=DEFAULT_SETTLE_WINDOW)
    receipt = _receipt(Path(args.receipt), repository=args.repo)
    handle = ownership(probe, receipt, log)
    route_cmd = route_command(args.provider, args.model, args.effort)
    executable = {"codex": "codex", "claude": "claude", "cursor": "cursor"}[args.provider]
    if shutil.which(executable) is None:
        raise ProbeError(f"provider executable unavailable: {executable}")
    try:
        availability = subprocess.run([executable, "--help"], capture_output=True, text=True, shell=False, timeout=5, check=False)
    except (OSError, subprocess.SubprocessError) as error:
        raise ProbeError(f"provider availability check failed: {executable}") from error
    if availability.returncode != 0:
        raise ProbeError(f"provider availability check failed: {executable}")
    try:
        sent = raw([probe.orca, "terminal", "send", "--terminal", handle, "--text", route_cmd,
                    "--enter", "--json"], timeout=args.send_timeout)
    except Exception as error:  # noqa: BLE001 - one-shot mutation; reconcile its effect
        sent = {"ok": False, "error": str(error)}
    append(log, {"event": "route_sent_once", "at": now(), "handle": handle, "route": route_cmd, "receipt": sent})
    consecutive = 0
    deadline = time.monotonic() + args.timeout
    sample = 0
    while time.monotonic() < deadline:
        sample += 1
        shown = probe.run([probe.orca, "terminal", "show", "--terminal", handle, "--json"])
        read = probe.run([probe.orca, "terminal", "read", "--terminal", handle, "--screen", "--json"])
        text = screen_text(read)
        lowered = text.lower()
        current = terminal(shown)
        rendered = terminal(read)
        match = (current.get("handle") == handle and rendered.get("handle") == handle
                 and current.get("connected") is True and rendered.get("source") == "screen"
                 and rendered_route_matches(text, args.provider, args.model, args.effort))
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


def rendered_route_matches(text: str, provider: str, model: str, effort: str) -> bool:
    """Accept only exact token-bounded provider/model/effort values from the screen."""
    if not provider or not model or effort not in EFFORTS:
        return False
    def token(value: str) -> str:
        return rf"(?<![A-Za-z0-9_.-]){re.escape(value)}(?![A-Za-z0-9_.-])"
    lines = text.lower().splitlines()
    for line in lines:
        if not re.search(token(provider.lower()), line) or not re.search(token(model.lower()), line):
            continue
        if not (re.search(rf"\bwith\s+{re.escape(effort.lower())}\s+effort\b", line)
                or re.search(rf"\beffort\s*[=:]\s*{re.escape(effort.lower())}\b", line)):
            continue
        if any(
            re.search(rf"\bwith\s+{re.escape(other)}\s+effort\b", line)
            or re.search(rf"\beffort\s*[=:]\s*{re.escape(other)}\b", line)
            for other in EFFORTS if other != effort
        ):
            continue
        return True
    return False


def _validate_timing(timeout: Any, interval: Any, *, maximum: float) -> None:
    if not isinstance(timeout, (int, float)) or not isinstance(interval, (int, float)):
        raise ProbeError("timing values must be numeric")
    if not (0 < timeout <= maximum) or not (0 <= interval <= timeout) or not (timeout == timeout and interval == interval):
        raise ProbeError("timing values are outside the bounded probe window")


def _idle_receipt(payload: dict[str, Any], handle: str) -> bool:
    return payload.get("ok") is True and terminal(payload).get("handle") == handle


def marker_frame(probe: OrcaProbe, handle: str, phase: str) -> tuple[str | None, str | None, dict[str, Any], dict[str, Any], str]:
    shown = probe.run([probe.orca, "terminal", "show", "--terminal", handle, "--json"])
    read = probe.run([probe.orca, "terminal", "read", "--terminal", handle, "--screen", "--json"])
    current = terminal(shown)
    rendered = terminal(read)
    text = screen_text(read)
    matches = re.findall(rf"TURN_DONE\s+{re.escape(phase)}\s+head=([0-9a-f]{{40}})", text)
    if current.get("connected") is not True:
        return None, "disconnected", shown, read, text
    if current.get("handle") != handle or rendered.get("handle") != handle:
        return None, "handle-mismatch", shown, read, text
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


def ref_exists(path: str | Path, ref: str) -> bool:
    """Return ref presence; only git's proven absent status is accepted as false."""
    try:
        result = git(path, "show-ref", "--verify", "--quiet", ref, check=False)
    except Exception as error:  # noqa: BLE001 - fail closed on an unavailable ref audit
        raise ProbeError("could not verify repository ref state") from error
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    raise ProbeError("could not verify repository ref state")


def worktree_registrations(common_git_dir: Path) -> set[Path]:
    result = git(common_git_dir.parent, "--git-dir", str(common_git_dir),
                 "worktree", "list", "--porcelain", check=False)
    if result.returncode != 0:
        raise ProbeError("could not enumerate Git worktree registrations")
    registrations: set[Path] = set()
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            registrations.add(Path(line.removeprefix("worktree ")).resolve())
    return registrations


def worktree_gitdirs(common_git_dir: Path) -> set[Path]:
    admin_root = common_git_dir / "worktrees"
    if not admin_root.is_dir():
        return set()
    return {entry.resolve() for entry in admin_root.iterdir() if entry.is_dir()}


def task_states(path: str | Path, task_file: str = "tasks.md") -> dict[str, str]:
    file = Path(path) / task_file
    if not file.is_file():
        return {}
    result: dict[str, str] = {}
    current: str | None = None
    for line in file.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"\s*###\s+(T\d+)\b", line)
        if heading:
            current = heading.group(1)
            result[current] = "pending"
            continue
        if current:
            status = re.match(r"\s*\*\*Status:\*\*\s*(\S+)", line)
            if status:
                result[current] = status.group(1).lower()
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
    expected_tasks = list(args.expected_task)
    if not expected_tasks:
        raise ProbeError("expected task ids are required")
    expected_count = int(args.expected_count)
    expected_subjects = list(args.expected_subject)
    if expected_count <= 0:
        raise ProbeError("expected commit count must be positive")
    if not expected_subjects or len(expected_subjects) != expected_count:
        raise ProbeError("expected commit subjects must match expected commit count")
    expected_commits = list(getattr(args, "expected_commit", []))
    if len(expected_commits) != expected_count or any(not SHA40.fullmatch(value) for value in expected_commits):
        raise ProbeError("expected commit identities must match expected commit count")
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
            states = task_states(path, args.task_file)
            checks = {
                "second_frame": second_error is None and second_head == head,
                "idle": idle.get("ok") is True and terminal(idle).get("handle") == handle,
                "head": actual_head == head,
                "descends": ancestry,
                "commit_count": len(rows) == expected_count,
                "commit_subjects": [row[1] for row in rows] == expected_subjects,
                "commit_identities": [row[0] for row in rows] == expected_commits,
                "paths": changed.issubset(set(args.allow_path)),
                "tasks": all(states.get(task) == "complete" for task in expected_tasks),
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
    receipt = _receipt(Path(args.receipt), repository=args.repo)
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
    command = [probe.orca, "worktree", "set", "--worktree", f"id:{args.worktree}",
               "--comment", args.comment, "--json"]
    result = mutate_once(
        probe,
        command,
        lambda: {"complete": worktree_comment(probe, args.worktree) == args.comment},
        timeout=args.timeout,
        settle_window=getattr(args, "settle_window", DEFAULT_SETTLE_WINDOW),
        interval=getattr(args, "interval", DEFAULT_INTERVAL),
    )
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
        git(args.worktree, "merge", "--ff-only", args.commit)
    result = gate(args.worktree, args.gate)
    if result["passed"] is not True:
        raise ProbeError("affected gate failed after producer sync")
    print(json.dumps({"status": "synchronized", "commit": args.commit,
                      "already_present": already_present, "gate": result}, sort_keys=True))


def stop(args: argparse.Namespace) -> None:
    probe = OrcaProbe(args.repo, orca=args.orca)
    def stopped() -> dict[str, Any]:
        listed = items(probe.run([probe.orca, "terminal", "list", "--json"]), "terminals")
        return {"complete": all(value.get("handle") != args.handle for value in listed)}

    result = mutate_once(
        probe,
        [probe.orca, "terminal", "stop", "--terminal", args.handle, "--json"],
        stopped,
        timeout=args.timeout,
        settle_window=getattr(args, "settle_window", DEFAULT_SETTLE_WINDOW),
        interval=getattr(args, "interval", DEFAULT_INTERVAL),
    )
    print(json.dumps(result, sort_keys=True))


def remove(args: argparse.Namespace) -> None:
    probe = OrcaProbe(args.repo, orca=args.orca)
    def removed() -> dict[str, Any]:
        inventory = probe.inventory()
        return {"complete": str(args.worktree) not in inventory["worktrees"]}

    result = mutate_once(
        probe,
        [probe.orca, "worktree", "rm", "--worktree", f"id:{args.worktree}", "--json"],
        removed,
        timeout=args.timeout,
        settle_window=getattr(args, "settle_window", DEFAULT_SETTLE_WINDOW),
        interval=getattr(args, "interval", DEFAULT_INTERVAL),
    )
    print(json.dumps(result, sort_keys=True))


def cleanup(args: argparse.Namespace) -> None:
    """Stop and remove only a clean, integrated, exactly-owned worktree."""
    probe = OrcaProbe(args.repo, orca=args.orca)
    receipt = _receipt(Path(args.receipt), repository=args.repo)
    state_payload = getattr(args, "state_payload", None)
    if isinstance(state_payload, dict):
        embedded = _receipt_from_state(state_payload)
        if any(receipt.get(field) != embedded.get(field) for field in RECEIPT_FIELDS):
            raise ProbeError("persisted cleanup receipt identity mismatch")
    before = probe.inventory()
    worktree_id = str(receipt["id"])
    known = receipt["startupTerminal"]["handle"]
    entry = before["worktrees"].get(worktree_id)
    if not isinstance(entry, dict):
        raise ProbeError("owned worktree is absent from the inventory")
    raw_path = Path(str(receipt["path"]))
    if raw_path.is_symlink():
        raise ProbeError("owned worktree path is unavailable or symlinked")
    path = raw_path.resolve()
    if isinstance(state_payload, dict):
        root = Path(state_payload["repository_root"]).resolve()
        _owned_path(str(raw_path), root, "worktree path")
    expected = {
        "repoId": probe.repo,
        "instanceId": receipt["instance"],
        "path": str(path),
        "branch": receipt.get("branch"),
    }
    for key, value in expected.items():
        if entry.get(key) not in (value, str(value)):
            raise ProbeError(f"immutable ownership mismatch: {key}")
    if not path.is_dir():
        raise ProbeError("owned worktree path is unavailable or symlinked")
    if git(path, "status", "--porcelain").stdout:
        raise ProbeError("owned worktree is dirty")
    meta_result = git(path, "rev-parse", "--git-dir")
    meta_dir = Path(meta_result.stdout.strip())
    if not meta_dir.is_absolute():
        meta_dir = path / meta_dir
    for marker in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply"):
        if (meta_dir / marker).exists():
            raise ProbeError("owned worktree has an operation in progress")
    current_head = git(path, "rev-parse", "HEAD").stdout.strip()
    if not SHA40.fullmatch(current_head):
        raise ProbeError("owned worktree HEAD is malformed")
    if git(path, "cat-file", "-e", receipt["pre_head"], check=False).returncode != 0:
        raise ProbeError("receipt pre_head is absent from owned checkout")
    if git(path, "merge-base", "--is-ancestor", receipt["pre_head"], current_head, check=False).returncode != 0:
        raise ProbeError("owned HEAD does not descend from receipt pre_head")
    branch = str(receipt["branch"] or "")
    ref = branch if branch.startswith("refs/heads/") else f"refs/heads/{branch}"
    branch_tip = git(path, "rev-parse", ref, check=False)
    if branch_tip.returncode != 0 or branch_tip.stdout.strip() != current_head:
        raise ProbeError("owned branch tip does not match current HEAD")
    integration_head = args.integration_head or receipt.get("integration_head")
    if not isinstance(integration_head, str) or not SHA40.fullmatch(integration_head):
        raise ProbeError("integration head is required for cleanup proof")
    if git(path, "merge-base", "--is-ancestor", current_head, integration_head, check=False).returncode != 0:
        raise ProbeError("owned slice head is not integrated")
    stored_gitdir = str(receipt.get("gitdir") or "")
    if not stored_gitdir:
        raise ProbeError("receipt common Git directory is required")
    common_git_dir = Path(stored_gitdir).resolve()
    if not common_git_dir.is_dir():
        raise ProbeError("common Git directory is unavailable")
    stored_worktree_gitdir = str(receipt.get("worktree_gitdir") or "")
    if not stored_worktree_gitdir:
        raise ProbeError("receipt linked-worktree Git directory is required")
    worktree_gitdir = Path(stored_worktree_gitdir).resolve()
    admin_root = (common_git_dir / "worktrees").resolve()
    try:
        worktree_gitdir.relative_to(admin_root)
    except ValueError as error:
        raise ProbeError("receipt linked-worktree Git directory is outside repository") from error
    if not worktree_gitdir.is_dir():
        raise ProbeError("linked-worktree Git directory is unavailable")
    registration = worktree_gitdir / "gitdir"
    registered_path = registration.read_text(encoding="utf-8").strip() if registration.is_file() else ""
    if not registered_path or Path(registered_path).resolve() != (path / ".git").resolve():
        raise ProbeError("linked-worktree registration does not match checkout")
    discovered_gitdir = git(path, "rev-parse", "--git-common-dir").stdout.strip()
    discovered_gitdir_path = Path(discovered_gitdir)
    if not discovered_gitdir_path.is_absolute():
        discovered_gitdir_path = path / discovered_gitdir_path
    discovered_gitdir_path = discovered_gitdir_path.resolve()
    if discovered_gitdir_path != common_git_dir:
        raise ProbeError("receipt common Git directory does not match checkout")
    registrations_before = worktree_registrations(common_git_dir)
    if path not in registrations_before:
        raise ProbeError("owned worktree registration is absent")
    foreign_registrations_before = registrations_before - {path}
    foreign_gitdirs_before = worktree_gitdirs(common_git_dir) - {worktree_gitdir}
    refs_before_result = git(common_git_dir.parent, "--git-dir", str(common_git_dir), "for-each-ref",
                             "--format=%(refname)", "refs/heads/", check=False)
    if refs_before_result.returncode != 0:
        raise ProbeError("could not enumerate repository refs before cleanup")
    refs_before = set(refs_before_result.stdout.splitlines())
    extra_refs = receipt.get("extra_refs", state_payload.get("extra_refs", []) if isinstance(state_payload, dict) else [])
    if not isinstance(extra_refs, list) or extra_refs:
        raise ProbeError("cleanup has extra owned refs")
    foreign_paths_before = {str(Path(value).resolve()): Path(value).exists() for value in args.foreign_path}
    listed = probe.worktree_terminals(str(receipt["id"]))
    owned = [value for value in listed if value.get("handle") == known]
    globally_known = before["terminals"].get(known)
    if globally_known is not None and (len(owned) != 1 or len(listed) != 1):
        raise ProbeError("owned terminal handle is missing, moved, or ambiguous")
    if known not in before["terminals"] and listed:
        raise ProbeError("unexpected terminal remains on owned worktree")
    if isinstance(globally_known, dict):
        status = str(globally_known.get("status", globally_known.get("state", ""))).lower()
        if (globally_known.get("running") is True or globally_known.get("active") is True
                or globally_known.get("busy") is True or status in {"running", "active", "busy", "processing"}):
            raise ProbeError("owned terminal process is active")
    lease_id = state_payload.get("lease_id") if isinstance(state_payload, dict) else receipt.get("lease_id")
    provider_value = state_payload.get("resource_provider") if isinstance(state_payload, dict) else None
    if lease_id is not None:
        if not isinstance(provider_value, str):
            raise ProbeError("owned lease provider is missing")
        provider_root = Path(state_payload["repository_root"]).resolve() if isinstance(state_payload, dict) else path.parent
        provider = _owned_path(provider_value, provider_root, "lease provider")
        lease_observed = state_payload.get("lease", state_payload.get("lease_receipt")) if isinstance(state_payload, dict) else None
        if lease_observed is not None:
            if not isinstance(lease_observed, dict) or any(lease_observed.get(field) != expected for field, expected in {
                "lease_id": lease_id, "repository": receipt["repository"], "worktree": receipt["id"],
                "operation_id": receipt.get("operation_id"),
            }.items()):
                raise ProbeError("owned lease identity mismatch")
            if lease_observed.get("released") is True:
                raise ProbeError("owned lease is already released")
            if lease_observed.get("live") is False:
                raise ProbeError("owned lease is not live")
    stopped = False
    lease_released = False
    effect_state_path = getattr(args, "state_path", None)
    if not isinstance(state_payload, dict) or not isinstance(effect_state_path, Path):
        raise ProbeError("cleanup requires persisted state")
    runner = MutationRunner(args, state_payload, effect_state_path)

    if owned:
        stopped_result = runner.issue(
            {"effect_id": f"{receipt['operation_id']}:cleanup-stop", "kind": "orca",
             "argv": ["terminal", "stop", "--terminal", known, "--json"]},
            observe=lambda: all(value.get("handle") != known for value in probe.worktree_terminals(worktree_id)),
        )
        stopped = True
    if lease_id is not None:
        provider_root = Path(state_payload["repository_root"]).resolve() if isinstance(state_payload, dict) else path.parent
        provider = _owned_path(provider_value, provider_root, "lease provider")
        def lease_reconciled() -> bool:
            result = subprocess.run(
                [str(provider)], cwd=str(provider_root),
                input=json.dumps({"operation": "inspect", "lease_id": lease_id,
                                  "repository": receipt["repository"], "worktree": receipt["id"]}),
                capture_output=True, text=True, shell=False, timeout=args.timeout, check=False,
            )
            if result.returncode != 0:
                return False
            observed = json.loads(result.stdout or "{}")
            return isinstance(observed, dict) and observed.get("lease_id") == lease_id and observed.get("released") is True
        cleanup_lease = {"effect_id": f"{receipt['operation_id']}:cleanup-lease", "kind": "lease",
                         "provider": str(provider), "operation": "release"}
        cleanup_lease_result = runner.issue(
            cleanup_lease,
            observe=lease_reconciled,
            success=lambda value: isinstance(value, dict) and value.get("lease_id") == lease_id and value.get("released") is True,
        )
        del cleanup_lease_result
        lease_released = True
    else:
        lease_released = True
    if git(path, "symbolic-ref", "--quiet", "--short", "HEAD", check=False).stdout.strip() == branch.removeprefix("refs/heads/"):
        runner.issue(
            {"effect_id": f"{receipt['operation_id']}:cleanup-detach", "kind": "git", "path": str(path), "argv": ["switch", "--detach", current_head]},
            success=lambda value: value.get("returncode") == 0,
            observe=lambda: git(path, "symbolic-ref", "--quiet", "--short", "HEAD", check=False).returncode != 0,
        )
    runner.issue(
        {"effect_id": f"{receipt['operation_id']}:cleanup-branch", "kind": "git", "path": str(path), "argv": ["branch", "--delete", branch.removeprefix("refs/heads/")]},
        success=lambda value: value.get("returncode") == 0,
        observe=lambda: not ref_exists(common_git_dir.parent, ref),
    )
    if ref_exists(common_git_dir.parent, ref):
        raise ProbeError("owned branch ref remains after deletion")

    removed_result = runner.issue(
        {"effect_id": f"{receipt['operation_id']}:cleanup-rm", "kind": "orca",
         "argv": ["worktree", "rm", "--worktree", f"id:{worktree_id}", "--json"]},
        observe=lambda: worktree_id not in probe.inventory()["worktrees"],
    )
    after = probe.inventory()
    foreign_before = set(before["worktrees"]) - {worktree_id}
    foreign_after = set(after["worktrees"]) - {worktree_id}
    foreign_terminals_before = set(before["terminals"]) - {known}
    foreign_terminals_after = set(after["terminals"]) - {known}
    refs_after_result = git(common_git_dir.parent, "--git-dir", str(common_git_dir), "for-each-ref",
                            "--format=%(refname)", "refs/heads/", check=False)
    if refs_after_result.returncode != 0:
        raise ProbeError("could not enumerate repository refs after cleanup")
    refs_after = set(refs_after_result.stdout.splitlines())
    registrations_after = worktree_registrations(common_git_dir)
    foreign_registrations_after = registrations_after - {path}
    foreign_gitdirs_after = worktree_gitdirs(common_git_dir) - {worktree_gitdir}
    foreign_refs_before = refs_before - {ref}
    foreign_refs_after = refs_after - {ref}
    foreign_paths_after = {key: Path(key).exists() for key in foreign_paths_before}
    if (foreign_before != foreign_after or foreign_terminals_before != foreign_terminals_after
            or foreign_refs_before != foreign_refs_after or foreign_paths_before != foreign_paths_after
            or foreign_registrations_before != foreign_registrations_after
            or foreign_gitdirs_before != foreign_gitdirs_after):
        raise ProbeError("cleanup changed a foreign resource")
    if (worktree_id in after["worktrees"] or known in after["terminals"] or path.exists()
            or path in registrations_after or worktree_gitdir.exists()):
        raise ProbeError("owned residue remains after cleanup")
    if ref_exists(common_git_dir.parent, ref):
        raise ProbeError("owned branch ref remains after cleanup")
    print(json.dumps({"status": "cleaned", "worktree": worktree_id, "handle": known,
                      "stopped": stopped, "foreign_preserved": True,
                      "stop_reconciled": bool(stopped_result) if owned else True,
                      "rm_reconciled": bool(removed_result), "lease_released": lease_released,
                      "residue": []}, sort_keys=True))


def transport(args: argparse.Namespace) -> None:
    probe = OrcaProbe(args.repo, orca=args.orca, interval=args.interval)
    worktree = Path(args.worktree).resolve()
    sent = send_pointer(probe, args.handle, Path(args.packet), Path(args.log), worktree=worktree)
    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        shown = probe.run([probe.orca, "terminal", "show", "--terminal", args.handle, "--json"])
        read = probe.run([probe.orca, "terminal", "read", "--terminal", args.handle, "--screen", "--json"])
        text = screen_text(read)
        if terminal(shown).get("handle") == args.handle and terminal(read).get("handle") == args.handle \
                and terminal(shown).get("connected") is True and terminal(read).get("source") == "screen" \
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
    route_cmd = route_command(args.provider, args.model, args.effort)
    _validate_timing(args.timeout, args.interval, maximum=DEFAULT_SETTLE_WINDOW)
    if shutil.which(args.provider) is None:
        raise ProbeError(f"provider executable unavailable: {args.provider}")
    try:
        sent = raw([probe.orca, "terminal", "send", "--terminal", args.handle, "--text", route_cmd,
                    "--enter", "--json"], timeout=args.send_timeout)
    except Exception as error:  # noqa: BLE001 - one-shot mutation; caller reconciles route
        sent = {"ok": False, "error": str(error)}
    consecutive = 0
    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        shown = probe.run([probe.orca, "terminal", "show", "--terminal", args.handle, "--json"])
        read = probe.run([probe.orca, "terminal", "read", "--terminal", args.handle, "--screen", "--json"])
        current, rendered = terminal(shown), terminal(read)
        text = screen_text(read)
        match = (current.get("handle") == args.handle and rendered.get("handle") == args.handle
                 and current.get("connected") is True and rendered.get("source") == "screen"
                 and rendered_route_matches(text, args.provider, args.model, args.effort))
        consecutive = consecutive + 1 if match else 0
        if consecutive >= 2:
            print(json.dumps({"status": "accepted", "handle": args.handle, "route": route_cmd,
                              "send_receipt_ok": sent.get("ok")}, sort_keys=True))
            return
        time.sleep(probe.interval)
    raise ProbeError(f"rendered verifier route timeout: {route_cmd}")


def verifier_send(args: argparse.Namespace) -> None:
    probe = OrcaProbe(args.repo, orca=args.orca)
    result = send_pointer(probe, args.handle, Path(args.packet), Path(args.log),
                          worktree=Path(args.worktree).resolve(), phase="VERIFIER", slice=args.slice)
    print(json.dumps(result, sort_keys=True))


def wait_text(args: argparse.Namespace) -> None:
    probe = OrcaProbe(args.repo, orca=args.orca, interval=args.interval)
    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        shown = probe.run([probe.orca, "terminal", "show", "--terminal", args.handle, "--json"])
        read = probe.run([probe.orca, "terminal", "read", "--terminal", args.handle, "--screen", "--json"])
        text = screen_text(read)
        found = (terminal(shown).get("handle") == args.handle and terminal(read).get("handle") == args.handle
                 and terminal(shown).get("connected") is True and terminal(read).get("source") == "screen"
                 and text.count(args.marker) == 1 and not is_working(text))
        if found:
            idle = probe.run([probe.orca, "terminal", "wait", "--terminal", args.handle,
                              "--for", "tui-idle", "--timeout-ms", "300000", "--json"], timeout=305)
            if not _idle_receipt(idle, args.handle):
                raise ProbeError("tui-idle receipt is malformed or uncorrelated")
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


def verify_effect(args: argparse.Namespace) -> None:
    """Reconcile a previously sent packet without issuing another mutation."""
    probe = OrcaProbe(args.repo, orca=args.orca, interval=args.interval)
    receipt = _receipt(Path(args.receipt), repository=args.repo)
    effect(args, probe, receipt, {"ok": False, "reconciled_only": True})


def audit(args: argparse.Namespace) -> None:
    """Prove one receipt's owned resources are absent without touching foreign resources."""
    probe = OrcaProbe(args.repo, orca=args.orca)
    receipt = _receipt(Path(args.receipt), repository=args.repo)
    inventory = probe.inventory()
    worktree_id = str(receipt["id"])
    handle = str(receipt["startupTerminal"]["handle"])
    path = Path(str(receipt["path"])).resolve()
    common_git_dir = Path(str(receipt["gitdir"])).resolve()
    linked_git_dir = Path(str(receipt["worktree_gitdir"])).resolve()
    branch = str(receipt.get("branch") or "").removeprefix("refs/heads/")
    ref = f"refs/heads/{branch}" if branch else ""
    residue = {
        "worktree": worktree_id in inventory["worktrees"],
        "terminal": handle in inventory["terminals"],
        "path": path.exists(),
        "branch": bool(ref and ref_exists(common_git_dir.parent, ref)),
        "registration": path in worktree_registrations(common_git_dir),
        "gitdir": linked_git_dir.exists(),
    }
    if any(residue.values()):
        raise ProbeError(f"owned residue remains: {residue}")
    print(json.dumps({"status": "clean", "residue": residue}, sort_keys=True))


def _json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProbeError(f"invalid JSON input: {path.name}") from error
    if not isinstance(value, dict):
        raise ProbeError("JSON input must be an object")
    return value


def _token(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 256:
        raise ProbeError(f"invalid {label}")
    if any(character.isspace() or ord(character) < 32 or ord(character) == 127 for character in value):
        raise ProbeError(f"invalid {label}")
    return value


def _route(value: Any) -> str:
    if not isinstance(value, str) or not value or len(value) > 1024 or any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ProbeError("invalid route")
    return value


def _owned_path(value: Any, root: Path, label: str, *, allow_missing: bool = False) -> Path:
    candidate = Path(_token(value, label))
    if not candidate.is_absolute():
        candidate = root / candidate
    root = root.resolve()
    # A resolved path is not enough: a symlink below the repository can be
    # swapped between validation and write.  Ancestors such as /tmp are not
    # repository-owned and therefore are intentionally outside this check.
    try:
        relative = candidate.absolute().relative_to(root)
    except ValueError:
        relative = None
    if relative is not None:
        current = root
        for part in relative.parts:
            current /= part
            if current.is_symlink():
                raise ProbeError(f"{label} is symlinked")
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ProbeError(f"{label} escapes repository") from error
    if not allow_missing and not resolved.exists():
        raise ProbeError(f"{label} is missing")
    return resolved


def _state_identity(value: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(value.get(field) for field in STATE_FIELDS)


def _identity(value: Mapping[str, Any], *, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProbeError(f"{label} must be an object")
    missing = [field for field in STATE_FIELDS if field not in value]
    if missing:
        raise ProbeError(f"{label} missing identity: {missing[0]}")
    if value.get("schema_version") != STATE_SCHEMA:
        raise ProbeError(f"{label} schema_version must be {STATE_SCHEMA}")
    for field in ("repository", "repository_root", "slice_id", "task_id", "operation_id",
                  "instance", "terminal_handle", "worktree_id", "worktree_path", "branch",
                  "packet_path", "log_path", "receipt_path"):
        _token(value[field], field.replace("_", " "))
    _route(value["route"])
    for field in ("commit_id", "pre_head"):
        current = value[field]
        if current is not None and (not isinstance(current, str) or not SHA40.fullmatch(current)):
            raise ProbeError(f"{field} must be a 40-hex SHA or null")
    if value["lease_id"] is not None:
        _token(value["lease_id"], "lease id")
    return value


def _receipt_from_state(state: dict[str, Any]) -> dict[str, Any]:
    receipt = state.get("receipt")
    if not isinstance(receipt, dict):
        raise ProbeError("state cleanup receipt is missing")
    missing = [field for field in RECEIPT_FIELDS if field not in receipt]
    if missing:
        raise ProbeError(f"state cleanup receipt is incomplete: {missing[0]}")
    if not isinstance(receipt["startupTerminal"], dict) or not isinstance(receipt["before"], dict):
        raise ProbeError("state cleanup receipt has malformed nested identity")
    expected = {
        "repository": state["repository"], "repository_root": state["repository_root"],
        "slice_id": state["slice_id"], "task_id": state["task_id"],
        "operation_id": state["operation_id"], "instance": state.get("instance"),
        "id": state["worktree_id"], "path": state["worktree_path"],
        "branch": state["branch"], "pre_head": state["pre_head"],
        "gitdir": state["gitdir"], "worktree_gitdir": state["worktree_gitdir"],
        "terminal_handle": state["terminal_handle"], "route": state["route"],
        "commit_id": state["commit_id"], "lease_id": state["lease_id"],
    }
    for field, value in expected.items():
        if receipt.get(field) != value:
            raise ProbeError(f"state cleanup receipt identity mismatch: {field}")
    if receipt["startupTerminal"].get("handle") != state["terminal_handle"]:
        raise ProbeError("state cleanup handle mismatch")
    return receipt


def _write_json(path: Path, value: dict[str, Any]) -> None:
    """Atomically replace state so a sink never sees a half-written issue record."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _effect_record(state: dict[str, Any], effect_id: str) -> dict[str, Any] | None:
    return next((item for item in state.get("effects", []) if item.get("effect_id") == effect_id), None)


def _reconcile_effect(
    args: argparse.Namespace,
    state: dict[str, Any],
    state_path: Path,
    effect: dict[str, Any],
) -> dict[str, Any]:
    """Settle an issued/unknown effect with bounded reads; never issue it again."""
    observe = effect.get("observe")
    if not isinstance(observe, list) or not observe or any(not isinstance(item, str) for item in observe):
        raise ProbeError(f"effect {effect.get('effect_id')} has no read-only reconciliation")
    if _is_mutation(observe):
        raise ProbeError("effect observation must be read-only")
    attempts = max(1, min(int(getattr(args, "attempts", 3)), 3))
    interval = max(0.0, float(getattr(args, "interval", DEFAULT_INTERVAL)))
    for attempt in range(attempts):
        try:
            kind = effect.get("kind")
            if kind == "orca":
                payload = OrcaProbe(state["repository"], orca=args.orca, interval=interval,
                                    read_attempts=1).run([args.orca, *observe])
                _observation_identity(payload, state, "effect observation")
                complete = True
            elif kind == "git":
                complete = git(state["repository_root"], *observe, check=False).returncode == 0
            elif kind == "lease":
                provider = _owned_path(effect.get("provider"), Path(state["repository_root"]), "lease provider")
                result = subprocess.run(
                    [str(provider)], cwd=state["repository_root"],
                    input=json.dumps({"operation": effect.get("observe_operation", "inspect"),
                                      "lease_id": state["lease_id"], "repository": state["repository"],
                                      "slice": state["slice_id"], "task": state["task_id"],
                                      "operation_id": state["operation_id"]}),
                    capture_output=True, text=True, shell=False, timeout=30, check=False,
                )
                if result.returncode:
                    complete = False
                else:
                    observed = json.loads(result.stdout or "{}")
                    if not isinstance(observed, dict) or observed.get("lease_id") != state["lease_id"]:
                        raise ProbeError("effect lease observation is uncorrelated")
                    complete = True
            else:
                raise ProbeError("unknown effect kind")
            if complete:
                effect["status"] = "settled"
                effect["settle_samples"] = attempt + 1
                _write_json(state_path, state)
                return effect
        except (OSError, ProbeError, ValueError, json.JSONDecodeError):
            if attempt + 1 == attempts:
                break
        if attempt + 1 < attempts:
            time.sleep(interval)
    effect["status"] = "unknown"
    effect["settle_samples"] = attempts
    _write_json(state_path, state)
    raise ProbeError(f"effect {effect.get('effect_id')} was not reconciled")


class MutationRunner:
    """Own the only transition from a durable effect intent to a physical mutation."""

    def __init__(self, args: argparse.Namespace, state: dict[str, Any], state_path: Path) -> None:
        self.args = args
        self.state = state
        self.state_path = state_path

    def _sink(self, effect: dict[str, Any]) -> dict[str, Any]:
        kind = effect.get("kind")
        argv = effect.get("argv")
        if kind == "orca":
            if not isinstance(argv, list) or not argv or any(not isinstance(item, str) for item in argv):
                raise ProbeError("malformed Orca mutation")
            command = [self.args.orca, *argv] if isinstance(argv, list) else []
            if effect.get("pointer"):
                    return _send_pointer_once(
                    OrcaProbe(self.state["repository"], orca=self.args.orca),
                    str(effect["handle"]), Path(str(effect["packet"])), Path(str(effect["log"])),
                )
            return raw(command, timeout=float(getattr(self.args, "timeout", 30.0)))
        if kind == "git":
            if not isinstance(argv, list):
                raise ProbeError("malformed Git mutation")
            result = git(effect.get("path", self.state["repository_root"]), *argv, check=True)
            return {"returncode": result.returncode}
        if kind == "lease":
            provider = _owned_path(effect.get("provider"), Path(self.state["repository_root"]), "lease provider")
            operation = effect.get("operation", "acquire")
            result = subprocess.run(
                [str(provider)], cwd=self.state["repository_root"], input=json.dumps({
                    "operation": operation, "lease_id": self.state["lease_id"],
                    "repository": self.state["repository"], "slice": self.state["slice_id"],
                    "task": self.state["task_id"], "operation_id": self.state["operation_id"],
                }), capture_output=True, text=True, shell=False,
                timeout=float(getattr(self.args, "timeout", 30.0)), check=False,
            )
            if result.returncode:
                raise ProbeError("resource provider mutation failed")
            try:
                value = json.loads(result.stdout or "{}")
            except json.JSONDecodeError as error:
                raise ProbeError("resource provider returned malformed JSON") from error
            if not isinstance(value, dict):
                raise ProbeError("resource provider returned malformed JSON")
            return value
        raise ProbeError("unknown mutation kind")

    def issue(
        self,
        effect: dict[str, Any],
        sink: Callable[[], dict[str, Any]] | None = None,
        observe: Callable[[], bool] | None = None,
        success: Callable[[dict[str, Any]], bool] | None = None,
    ) -> dict[str, Any]:
        """Persist in-flight attempt one, issue once, or reconcile an existing effect."""
        effect_id = _token(effect.get("effect_id"), "effect id")
        existing = _effect_record(self.state, effect_id)
        if existing is not None:
            if existing.get("status") == "settled":
                return existing
            reader = observe or (lambda: self._read_effect(existing))
            return _settle_callback(self.args, self.state, self.state_path, existing, reader)
        record = {key: effect[key] for key in ("effect_id", "kind", "argv", "path", "provider", "operation", "observe", "observe_operation", "pointer", "handle", "packet", "log") if key in effect}
        record.update({"effect_id": effect_id, "kind": effect.get("kind"), "status": "in_flight", "attempts": 1})
        original = deepcopy(self.state)
        self.state.setdefault("effects", []).append(record)
        self.state.setdefault("effect_ids", []).append(effect_id)
        try:
            _write_json(self.state_path, self.state)
        except Exception:
            self.state.clear()
            self.state.update(original)
            raise
        try:
            receipt = (sink or (lambda: self._sink(effect)))()
        except Exception as error:  # noqa: BLE001 - preserve ambiguous post-effect state
            record.update({"status": "unknown", "error": str(error)})
            _write_json(self.state_path, self.state)
            raise
        record.update({"status": "issued", "receipt": receipt})
        _write_json(self.state_path, self.state)
        if success is not None and not success(receipt):
            record.update({"status": "unknown", "error": "mutation receipt was not accepted"})
            _write_json(self.state_path, self.state)
            raise ProbeError(f"effect {effect_id} receipt was not accepted")
        reader = observe or (lambda: self._read_effect(record))
        if observe is not None or isinstance(effect.get("observe"), list):
            return _settle_callback(self.args, self.state, self.state_path, record, reader)
        record["status"] = "settled"
        _write_json(self.state_path, self.state)
        return record

    def _read_effect(self, effect: dict[str, Any]) -> bool:
        return _reconcile_effect(self.args, self.state, self.state_path, effect).get("status") == "settled"


def _persisted_effect(
    args: argparse.Namespace,
    state: dict[str, Any],
    state_path: Path,
    effect_spec: dict[str, Any],
    invoke: Callable[[], dict[str, Any]],
    *,
    success: Callable[[dict[str, Any]], bool] | None = None,
    reconcile: Callable[[], bool] | None = None,
) -> dict[str, Any]:
    """Compatibility adapter; all issuance is delegated to MutationRunner.issue."""
    return MutationRunner(args, state, state_path).issue(effect_spec, sink=invoke, observe=reconcile, success=success)


def _settle_callback(
    args: argparse.Namespace,
    state: dict[str, Any],
    state_path: Path,
    effect: dict[str, Any],
    reader: Callable[[], bool],
) -> dict[str, Any]:
    attempts = max(1, min(int(getattr(args, "attempts", 3)), 3))
    interval = max(0.0, float(getattr(args, "interval", DEFAULT_INTERVAL)))
    for attempt in range(attempts):
        try:
            if reader():
                effect["status"] = "settled"
                effect["settle_samples"] = attempt + 1
                _write_json(state_path, state)
                return effect
        except Exception:  # noqa: BLE001 - read-only reconciliation boundary
            pass
        if attempt + 1 < attempts:
            time.sleep(interval)
    effect["status"] = "unknown"
    effect["settle_samples"] = attempts
    _write_json(state_path, state)
    raise ProbeError(f"effect {effect.get('effect_id')} was not reconciled")


def _observation_identity(payload: dict[str, Any], state: dict[str, Any], source: str) -> None:
    """Require all persisted identities when a provider exposes correlation data."""
    values = payload.get("correlation", payload)
    if values is payload and isinstance(payload.get("result"), dict):
        result = payload["result"]
        values = result.get("correlation", result)
    if not isinstance(values, dict):
        raise ProbeError(f"{source} correlation is malformed")
    aliases = {
        "repository": ("repository", "repo", "repoId"),
        "repository_root": ("repository_root", "root"),
        "worktree_id": ("worktree_id", "worktree", "id"),
        "worktree_path": ("worktree_path", "path"),
        "instance": ("instance", "instance_id", "instanceId"),
        "branch": ("branch",), "pre_head": ("pre_head",),
        "gitdir": ("gitdir", "git_dir"), "worktree_gitdir": ("worktree_gitdir", "worktree_git_dir"),
        "terminal_handle": ("terminal_handle", "handle"),
        "route": ("route",), "slice_id": ("slice_id", "slice"),
        "task_id": ("task_id", "task"), "operation_id": ("operation_id", "operation"),
        "commit_id": ("commit_id", "commit", "head"), "lease_id": ("lease_id", "lease"),
    }
    for field, names in aliases.items():
        marker = object()
        found = next((values[name] for name in names if name in values), marker)
        if found is marker:
            raise ProbeError(f"{source} correlation missing: {field}")
        if found != state[field]:
            raise ProbeError(f"{source} correlation mismatch: {field}")


def dispatch(args: argparse.Namespace) -> None:
    """Persist a complete packet before sending one short pointer."""
    request_path = Path(args.request)
    state_path = Path(args.state)
    request = _json_object(request_path.resolve())
    root_value = request.get("repository_root")
    if not isinstance(root_value, str):
        raise ProbeError("repository root is required")
    root_candidate = Path(root_value)
    if root_candidate.is_symlink():
        raise ProbeError("repository root is unavailable or symlinked")
    root = root_candidate.resolve()
    if not root.is_dir():
        raise ProbeError("repository root is unavailable or symlinked")
    _owned_path(str(request_path), root, "request path")
    _owned_path(str(state_path), root, "state path", allow_missing=True)
    required = ("schema_version", "repository", "slice_id", "task_id", "operation_id",
                "terminal_handle", "packet_path", "packet_body", "route", "commit_id", "lease_id",
                "worktree_id", "worktree_path", "branch", "pre_head", "gitdir",
                "worktree_gitdir")
    if any(key not in request for key in required) or request["schema_version"] != STATE_SCHEMA:
        raise ProbeError(f"dispatch request schema_version {STATE_SCHEMA} and complete identity are required")
    body = request["packet_body"]
    if not isinstance(body, str) or not body:
        raise ProbeError("packet body is required")
    packet_path = _owned_path(request["packet_path"], root, "packet path", allow_missing=True)
    log_path = _owned_path(request.get("log_path", "orca-probe.jsonl"), root, "log path", allow_missing=True)
    receipt_path = _owned_path(request.get("receipt_path", "orca-receipt.json"), root,
                               "receipt path", allow_missing=True)
    worktree_path = _owned_path(request["worktree_path"], root, "worktree path")
    state: dict[str, Any] = {
        "schema_version": STATE_SCHEMA, "repository": _token(request["repository"], "repository"),
        "repository_root": str(root), "slice_id": _token(request["slice_id"], "slice id"),
        "task_id": _token(request["task_id"], "task id"),
        "operation_id": _token(request["operation_id"], "operation id"),
        "terminal_handle": _token(request["terminal_handle"], "terminal handle"),
        "route": _route(request["route"]), "commit_id": request["commit_id"],
        "lease_id": request["lease_id"], "worktree_id": _token(request["worktree_id"], "worktree id"),
        "worktree_path": str(worktree_path), "branch": _token(request["branch"], "branch"),
        "pre_head": request["pre_head"], "gitdir": _token(request["gitdir"], "gitdir"),
        "worktree_gitdir": _token(request["worktree_gitdir"], "worktree gitdir"),
        "packet_path": str(packet_path), "log_path": str(log_path), "receipt_path": str(receipt_path),
        "status": "packet_persisted", "effect_ids": [], "effects": [],
        "instance": _token(request.get("instance", request["operation_id"]), "instance"),
    }
    _identity(state, label="dispatch state")
    if state["lease_id"] is not None:
        state["lease_id"] = _token(state["lease_id"], "lease id")
    if state_path.exists():
        previous = _json_object(state_path)
        if _state_identity(previous) != _state_identity(state):
            raise ProbeError("operation state identity was reused or changed")
        if previous.get("status") in {"pointer_sent", "settled"}:
            print(json.dumps({"status": previous["status"], "operation_id": state["operation_id"],
                              "replayed": True}, sort_keys=True))
            return
        state = previous
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(body, encoding="utf-8")
    receipt = {
        "repository": state["repository"], "id": state["worktree_id"],
        "repository_root": state["repository_root"], "slice_id": state["slice_id"],
        "task_id": state["task_id"], "operation_id": state["operation_id"],
        "instance": state["instance"],
        "path": state["worktree_path"], "branch": state["branch"], "pre_head": state["pre_head"],
        "gitdir": state["gitdir"], "worktree_gitdir": state["worktree_gitdir"],
        "terminal_handle": state["terminal_handle"], "route": state["route"],
        "commit_id": state["commit_id"], "lease_id": state["lease_id"],
        "startupTerminal": {"handle": state["terminal_handle"]},
        "before": request.get("before", {"terminals": {}, "worktrees": {}}),
    }
    state["receipt"] = receipt
    if request.get("resource_provider") is not None:
        state["resource_provider"] = str(_owned_path(request["resource_provider"], root, "resource provider"))
    state["status"] = "send_started"
    _write_json(state_path, state)
    declared = request.get("effects", [])
    if not isinstance(declared, list):
        raise ProbeError("effects must be an array")
    runner = MutationRunner(args, state, state_path)
    for effect_spec in declared:
        if not isinstance(effect_spec, dict):
            raise ProbeError("malformed declared mutation")
        runner.issue(
            effect_spec,
            success=lambda receipt: isinstance(receipt, dict) and receipt.get("ok", True) is not False,
        )
    pointer_spec = {"effect_id": f"{state['operation_id']}:pointer", "kind": "orca",
                    "argv": ["terminal", "send"], "pointer": True,
                    "handle": state["terminal_handle"], "packet": str(packet_path),
                    "log": str(log_path), "observe": request.get("pointer_observe")}
    sent_record = runner.issue(
        pointer_spec,
        success=lambda receipt: isinstance(receipt, dict) and receipt.get("ok") is True,
    )
    sent = sent_record.get("receipt", {})
    state["status"] = "pointer_sent"
    state["send_ok"] = sent.get("ok")
    _write_json(state_path, state)
    _write_json(receipt_path, receipt)
    print(json.dumps({"status": state["status"], "operation_id": state["operation_id"],
                      "slice_id": state["slice_id"], "task_id": state["task_id"],
                      "pointer_path": str(packet_path), "state_path": str(state_path),
                      "receipt_path": str(receipt_path), "effect_ids": state["effect_ids"]}, sort_keys=True))


def inspect(args: argparse.Namespace) -> None:
    """Perform bounded read-only reconciliation for the persisted handle."""
    state_path = Path(args.state).resolve()
    state = _json_object(state_path)
    _identity(state, label="state")
    _receipt_from_state(state)
    root = Path(state["repository_root"]).resolve()
    _owned_path(str(state_path), root, "state path")
    for field in ("packet_path", "log_path", "receipt_path"):
        _owned_path(state[field], root, field.replace("_", " "), allow_missing=True)
    repository = _token(state["repository"], "repository")
    handle = _token(state["terminal_handle"], "terminal handle")
    probe = OrcaProbe(repository, orca=args.orca, interval=args.interval,
                      read_attempts=args.attempts)
    shown = terminal(probe.run([args.orca, "terminal", "show", "--terminal", handle, "--json"]))
    _observation_identity(shown, state, "terminal")
    worktree = probe.run([args.orca, "worktree", "show", "--worktree", f"id:{state['worktree_id']}", "--json"])
    _observation_identity(worktree, state, "worktree")
    git_head = git(state["worktree_path"], "rev-parse", "HEAD").stdout.strip()
    if git_head != state["commit_id"]:
        raise ProbeError("git commit identity mismatch")
    git_correlation = {field: state[field] for field in (
        "repository", "repository_root", "slice_id", "task_id", "operation_id", "instance",
        "worktree_id", "worktree_path", "branch", "pre_head", "gitdir", "worktree_gitdir",
        "terminal_handle", "route", "lease_id")}
    git_correlation["commit_id"] = git_head
    _observation_identity({"correlation": git_correlation}, state, "git")
    for effect in state.get("effects", []):
        if effect.get("status") == "pending":
            raise ProbeError("pending mutation effect requires reconciliation")
        if effect.get("status") in {"unknown", "issued"}:
            _reconcile_effect(args, state, state_path, effect)
        if effect.get("status") != "settled":
            raise ProbeError("unsettled mutation effect remains")
    state["status"] = "settled"
    _write_json(state_path, state)
    print(json.dumps({"status": "inspected", "operation_id": state["operation_id"],
                      "slice_id": state["slice_id"], "task_id": state["task_id"],
                      "handle": handle, "connected": shown.get("connected")}, sort_keys=True))


def cleanup_entry(args: argparse.Namespace) -> None:
    if args.state:
        state_path = Path(args.state)
        state = _json_object(state_path)
        if not args.repo:
            args.repo = state.get("repository", "")
        _identity(state, label="state")
        root_candidate = Path(state["repository_root"])
        if root_candidate.is_symlink():
            raise ProbeError("repository root is unavailable or symlinked")
        root = root_candidate.resolve()
        _owned_path(str(state_path), root, "state path")
        receipt_path = state.get("receipt_path")
        if not isinstance(receipt_path, str):
            raise ProbeError("state receipt path is missing")
        embedded = _receipt_from_state(state)
        args.receipt = str(_owned_path(receipt_path, root, "receipt path"))
        persisted = _receipt(Path(args.receipt), repository=args.repo)
        if any(persisted.get(field) != embedded.get(field) for field in RECEIPT_FIELDS):
            raise ProbeError("persisted cleanup receipt identity mismatch")
        args.state_payload = state
        args.state_path = state_path
    if not args.receipt:
        raise ProbeError("cleanup requires --state or --receipt")
    cleanup(args)


def _positive_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("value must be numeric") from error
    if not (0 < parsed < float("inf")):
        raise argparse.ArgumentTypeError("value must be finite and positive")
    return parsed


def _interval_float(value: str) -> float:
    parsed = _positive_float(value)
    if parsed != DEFAULT_INTERVAL:
        raise argparse.ArgumentTypeError("route interval must be exactly 0.25 seconds")
    return parsed


def _route_timeout(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("timeout must be numeric") from error
    if not (0 < parsed <= DEFAULT_SETTLE_WINDOW):
        raise argparse.ArgumentTypeError("timeout must be within 60 seconds")
    return parsed


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--orca", default=ORCA)
    root.add_argument("--repo", default="")
    sub = root.add_subparsers(dest="command", required=True)

    dispatch_parser = sub.add_parser("dispatch")
    dispatch_parser.add_argument("--request", required=True)
    dispatch_parser.add_argument("--state", required=True)
    dispatch_parser.set_defaults(function=dispatch)

    inspect_parser = sub.add_parser("inspect")
    inspect_parser.add_argument("--state", required=True)
    inspect_parser.add_argument("--attempts", type=int, default=3)
    inspect_parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL)
    inspect_parser.set_defaults(function=inspect)
    cleanup_parser = sub.add_parser("cleanup")
    cleanup_parser.add_argument("--state", required=True)
    cleanup_parser.add_argument("--integration-head", default="")
    cleanup_parser.add_argument("--foreign-path", action="append", default=[])
    cleanup_parser.add_argument("--timeout", type=float, default=30.0)
    cleanup_parser.add_argument("--settle-window", type=float, default=DEFAULT_SETTLE_WINDOW)
    cleanup_parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL)
    cleanup_parser.set_defaults(function=cleanup_entry)
    return root


def main(argv: list[str] | None = None) -> None:
    args = parser().parse_args(argv)
    try:
        args.function(args)
    except (ProbeError, OSError, subprocess.SubprocessError) as error:
        raise SystemExit(f"FAIL_CLOSED {error}") from error


if __name__ == "__main__":
    main()
