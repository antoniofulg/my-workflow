"""Runnable fake-Orca checks for the shipped assisted coordinator probe."""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
from pathlib import Path
from typing import Callable

import orca_assisted_probe as probe


ROOT = Path(__file__).resolve().parent


def test_mutations_are_one_shot_and_reads_reconcile() -> None:
    calls: list[list[str]] = []
    read_attempts = 0
    original = probe.raw

    def fake(argv: list[str], timeout: float = 30.0) -> dict[str, object]:
        nonlocal read_attempts
        calls.append(argv)
        if probe._is_mutation(argv):
            raise probe.ProbeError("induced transient mutation failure")
        read_attempts += 1
        if read_attempts < 3:
            raise probe.ProbeError("induced transient read failure")
        return {"ok": True}

    probe.raw = fake  # type: ignore[assignment]
    try:
        for command in (
            ["orca", "worktree", "create"],
            ["orca", "terminal", "send"],
            ["orca", "worktree", "set"],
            ["orca", "terminal", "stop"],
            ["orca", "worktree", "rm"],
        ):
            try:
                probe.resilient_run(command, attempts=3, interval=0)
            except probe.ProbeError:
                pass
        probe.resilient_run(["orca", "terminal", "show"], attempts=3, interval=0)
    finally:
        probe.raw = original  # type: ignore[assignment]

    mutation_calls = [call for call in calls if probe._is_mutation(call)]
    assert len(mutation_calls) == 5
    assert [call[2] for call in mutation_calls] == ["create", "send", "set", "stop", "rm"]
    assert calls[-3:] == [["orca", "terminal", "show"]] * 3


def test_pointer_transport_excludes_packet_body_and_import_is_inert() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        calls = root / "calls"
        fake = root / "orca"
        fake.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' \"$*\" >> \"$CALLS\"\n"
            "case \"$*\" in\n"
            "  *worktree\\ set*) printf '%s\\n' '{\"ok\":false}' ;;\n"
            "  *worktree\\ show*) printf '%s\\n' '{\"result\":{\"worktree\":{\"comment\":\"parked\"}}}' ;;\n"
            "  *terminal\\ stop*) printf '%s\\n' '{\"ok\":false}' ;;\n"
            "  *terminal\\ list*) printf '%s\\n' '{\"result\":{\"terminals\":[]}}' ;;\n"
            "  *worktree\\ rm*) printf '%s\\n' '{\"ok\":false}' ;;\n"
            "  *worktree\\ list*) printf '%s\\n' '{\"result\":{\"worktrees\":[]}}' ;;\n"
            "  *terminal\\ send*) printf '%s\\n' '{\"ok\":false,\"result\":{\"send\":{\"accepted\":false}}}' ;;\n"
            "  *) printf '%s\\n' '{\"ok\":true}' ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)
        packet = root / "coordinator-packet.md"
        worktree = root / "slice-worktree"
        worktree.mkdir()
        packet.write_text("SECRET_PACKET_BODY\n" + ("body line\n" * 80)
                          + "TURN_DONE PHASE head=<current exact 40-hex HEAD>\n", encoding="utf-8")
        log = root / "probe.jsonl"
        env = {**os.environ, "CALLS": str(calls)}
        completed = subprocess.run(
            [sys.executable, str(ROOT / "orca_assisted_probe.py"), "--orca", str(fake), "--repo", "repo",
             "send-pointer", "--handle", "term-1", "--packet", str(packet), "--worktree", str(worktree), "--log", str(log)],
            capture_output=True, text=True, env=env, check=False,
        )
        assert completed.returncode == 0, completed.stderr
        sent = calls.read_text(encoding="utf-8")
        assert sent.count("terminal send") == 1
        assert f"read {packet.resolve()} and execute it as your packet" in sent
        assert "SECRET_PACKET_BODY" not in sent
        records = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
        assert records[0]["pointer_chars"] < records[0]["packet_body_chars"]

        for command, options in (
            ("set-comment", ["--worktree", "owned", "--comment", "parked"]),
            ("stop", ["--handle", "owned-terminal"]),
            ("rm", ["--worktree", "owned"]),
        ):
            completed = subprocess.run(
                [sys.executable, str(ROOT / "orca_assisted_probe.py"), "--orca", str(fake), "--repo", "repo",
                 command, *options], capture_output=True, text=True, env=env, check=False,
            )
            assert completed.returncode == 0, completed.stderr

        import_result = subprocess.run(
            [sys.executable, "-c", f"import runpy; runpy.run_path({str(ROOT / 'orca_assisted_probe.py')!r})"],
            capture_output=True, text=True, env=env, check=False,
        )
        assert import_result.returncode == 0, import_result.stderr
        sent_calls = calls.read_text(encoding="utf-8").splitlines()
        assert sum("terminal send" in call for call in sent_calls) == 1
        assert sum("worktree set" in call for call in sent_calls) == 1
        assert sum("terminal stop" in call for call in sent_calls) == 1
        assert sum("worktree rm" in call for call in sent_calls) == 1


def test_create_reconciles_late_effect_without_duplicate_worktree() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        (root / "seed").write_text("seed\n", encoding="utf-8")
        subprocess.run(["git", "add", "seed"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        state = root / "created"
        calls = root / "calls"
        fake = root / "orca"
        candidate = json.dumps({"id": "owned", "repoId": "repo", "displayName": "slice-a",
                                "instanceId": "instance", "path": str(root),
                                "branch": "refs/heads/slice-a", "head": head})
        candidate_payload = json.dumps({"result": {"worktrees": [json.loads(candidate)]}})
        terminal = '{"handle":"owned-terminal","connected":true,"writable":true}'
        fake.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' \"$*\" >> '" + str(calls) + "'\n"
            "case \"$*\" in\n"
            "  *worktree\\ create*) touch '" + str(state) + "'; printf '%s\\n' '{\"ok\":false}' ;;\n"
            "  *worktree\\ list*) if test -e '" + str(state) + "'; then printf '%s\\n' '" + candidate_payload.replace("'", "'\\''") + "'; else printf '%s\\n' '{\"result\":{\"worktrees\":[]}}'; fi ;;\n"
            "  *terminal\\ list*--worktree*) printf '%s\\n' '{\"result\":{\"terminals\":[" + terminal + "]}}' ;;\n"
            "  *terminal\\ list*) printf '%s\\n' '{\"result\":{\"terminals\":[]}}' ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)
        receipt = root / "receipt.json"
        args = SimpleNamespace(repo="repo", orca=str(fake), name="slice-a", base="main",
                               receipt=str(receipt), log=str(root / "log"), create_timeout=1.0,
                               settle_window=0.1, interval=0.0)
        with contextlib.redirect_stdout(io.StringIO()):
            probe.create(args)
        assert calls.read_text(encoding="utf-8").count("worktree create") == 1
        assert json.loads(receipt.read_text(encoding="utf-8"))["id"] == "owned"


def test_route_requires_two_consecutive_screen_frames_after_reset() -> None:
    assert probe.route_command("codex", "gpt-5.6-luna", "low") == (
        "exec codex --model gpt-5.6-luna -c model_reasoning_effort=low"
    )
    assert probe.route_command("claude", "sonnet", "medium") == (
        "exec claude --model sonnet --effort medium"
    )
    assert probe.route_command("cursor", "gpt-5.6-luna", "high") == (
        "exec cursor agent --model 'gpt-5.6-luna[effort=high]'"
    )
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        receipt = root / "receipt.json"
        receipt.write_text(json.dumps({"id": "lane", "path": str(root), "branch": "branch",
                                       "pre_head": "a" * 40, "startupTerminal": {"handle": "h"},
                                       "before": {"terminals": {}}}), encoding="utf-8")
        reads = [
            {"source": "screen", "text": "Claude Code Sonnet 5 with low effort"},
            {"source": "ansi", "text": "Claude Code Sonnet 5 with low effort"},
            {"source": "screen", "text": "Claude Code Sonnet 5 with low effort"},
            {"source": "screen", "text": "Claude Code Sonnet 5 with low effort"},
        ]
        read_index = 0
        sends: list[list[str]] = []
        original_raw = probe.raw
        original_run = probe.OrcaProbe.run

        def fake_raw(argv: list[str], timeout: float = 30.0) -> dict[str, object]:
            sends.append(argv)
            return {"ok": False}

        def fake_run(self: object, argv: list[str], timeout: float = 30.0) -> dict[str, object]:
            nonlocal read_index
            if "list" in argv:
                return {"result": {"terminals": [{"handle": "h"}]}}
            if "wait" in argv:
                return {"ok": True}
            if "read" in argv:
                value = reads[min(read_index, len(reads) - 1)]
                read_index += 1
                return {"result": {"terminal": value}}
            return {"result": {"terminal": {"handle": "h", "connected": True,
                                                "writable": True, "agentWait": None, "preview": "❯"}}}

        probe.raw = fake_raw  # type: ignore[assignment]
        probe.OrcaProbe.run = fake_run  # type: ignore[assignment]
        args = SimpleNamespace(repo="repo", orca="orca", receipt=str(receipt), log=str(root / "route.log"),
                               provider="claude", model="sonnet", effort="low", timeout=1.0,
                               send_timeout=1.0, interval=0.0)
        try:
            with contextlib.redirect_stdout(io.StringIO()) as output:
                probe.route(args)
        finally:
            probe.raw = original_raw  # type: ignore[assignment]
            probe.OrcaProbe.run = original_run  # type: ignore[assignment]
        assert len([call for call in sends if "send" in call]) == 1
        assert read_index == 4
        assert output.getvalue().count('"status": "accepted"') == 1


def test_cleanup_refuses_when_owned_branch_ref_remains() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        receipt = root / "receipt.json"
        head = "a" * 40
        receipt.write_text(json.dumps({"id": "lane", "path": str(root), "branch": "refs/heads/lane",
                                       "instance": "instance", "pre_head": head,
                                       "startupTerminal": {"handle": "h"}, "before": {"terminals": {}}}), encoding="utf-8")
        before = {"worktrees": {"lane": {"id": "lane", "repoId": "repo", "instanceId": "instance",
                                           "path": str(root.resolve()), "branch": "refs/heads/lane"}}, "terminals": {}}
        original_inventory = probe.OrcaProbe.inventory
        original_terminals = probe.OrcaProbe.worktree_terminals
        original_git = probe.git
        probe.OrcaProbe.inventory = lambda self: before  # type: ignore[assignment]
        probe.OrcaProbe.worktree_terminals = lambda self, worktree_id: []  # type: ignore[assignment]

        def fake_git(path: str | Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
            if args[:2] == ("show-ref", "--verify"):
                return subprocess.CompletedProcess([], 0, "", "")
            if args[:2] == ("rev-parse", "HEAD") or args[:2] == ("rev-parse", "refs/heads/lane"):
                return subprocess.CompletedProcess([], 0, head + "\n", "")
            return subprocess.CompletedProcess([], 0, "", "")

        probe.git = fake_git  # type: ignore[assignment]
        args = probe.parser().parse_args(["--repo", "repo", "cleanup", "--receipt", str(receipt),
                                          "--integration-head", head, "--settle-window", "0"])
        try:
            try:
                probe.cleanup(args)
            except probe.ProbeError as error:
                assert "branch ref remains" in str(error)
            else:
                raise AssertionError("cleanup must fail closed while owned ref remains")
        finally:
            probe.OrcaProbe.inventory = original_inventory  # type: ignore[assignment]
            probe.OrcaProbe.worktree_terminals = original_terminals  # type: ignore[assignment]
            probe.git = original_git  # type: ignore[assignment]


def test_cleanup_stops_only_owned_handle_and_preserves_foreign_worktree() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        worktree = root / "lane"
        worktree.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=worktree, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=worktree, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=worktree, check=True)
        (worktree / "seed").write_text("seed\n", encoding="utf-8")
        subprocess.run(["git", "add", "seed"], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=worktree, check=True)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=worktree, text=True).strip()
        subprocess.run(["git", "branch", "owned"], cwd=worktree, check=True)
        receipt_path = root / "receipt.json"
        receipt_path.write_text(
            json.dumps({
                "id": "owned-worktree", "path": str(worktree), "branch": "refs/heads/owned",
                "instance": "owned-instance", "pre_head": head, "startupTerminal": {"handle": "owned-terminal"},
                "before": {"terminals": {}, "worktrees": {}},
            }), encoding="utf-8",
        )
        before = {"worktrees": {"owned-worktree": {"id": "owned-worktree", "repoId": "repo", "instanceId": "owned-instance", "path": str(worktree.resolve()), "branch": "refs/heads/owned"}, "foreign": {"id": "foreign"}}, "terminals": {"owned-terminal": {"handle": "owned-terminal"}, "foreign-terminal": {"handle": "foreign-terminal"}}}
        after = {"worktrees": {"foreign": {"id": "foreign"}}, "terminals": {"foreign-terminal": {"handle": "foreign-terminal"}}}
        inventories = iter((before, after, after))
        calls: list[list[str]] = []
        state = {"stopped": False}
        original_raw = probe.raw
        original_inventory = probe.OrcaProbe.inventory
        original_terminals = probe.OrcaProbe.worktree_terminals
        def fake_raw(argv: list[str], timeout: float = 30.0) -> dict[str, object]:
            calls.append(argv)
            if len(argv) > 2 and argv[2] == "stop":
                state["stopped"] = True
            if len(argv) > 2 and argv[2] == "rm":
                shutil.rmtree(worktree)
            return {"ok": False}

        probe.raw = fake_raw  # type: ignore[assignment]
        probe.OrcaProbe.inventory = lambda self: next(inventories)  # type: ignore[assignment]
        probe.OrcaProbe.worktree_terminals = lambda self, worktree_id: [] if state["stopped"] else [{"handle": "owned-terminal"}]  # type: ignore[assignment]
        args = probe.parser().parse_args(["--repo", "repo", "cleanup", "--receipt", str(receipt_path), "--integration-head", head])
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                probe.cleanup(args)
        finally:
            probe.raw = original_raw  # type: ignore[assignment]
            probe.OrcaProbe.inventory = original_inventory  # type: ignore[assignment]
            probe.OrcaProbe.worktree_terminals = original_terminals  # type: ignore[assignment]
        assert [call[2] for call in calls] == ["stop", "rm"]
        assert calls[0][4] == "owned-terminal"
        assert calls[1][4] == "id:owned-worktree"
        assert "foreign" in after["worktrees"]
        assert "foreign-terminal" in after["terminals"]


def _cleanup_failure_case(*, retain_owned: bool, remove_foreign: bool) -> str:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        foreign_path = root.parent / f"foreign-{root.name}"
        foreign_path.write_text("foreign\n", encoding="utf-8")
        head = "a" * 40
        receipt_path = root / "receipt.json"
        receipt_path.write_text(json.dumps({"id": "lane", "path": str(root), "branch": "refs/heads/lane",
                                            "instance": "instance", "pre_head": head,
                                            "startupTerminal": {"handle": "owned-terminal"},
                                            "before": {"terminals": {}}}), encoding="utf-8")
        before = {"worktrees": {"lane": {"id": "lane", "repoId": "repo", "instanceId": "instance",
                                           "path": str(root.resolve()), "branch": "refs/heads/lane"},
                                 "foreign": {"id": "foreign"}},
                  "terminals": {"owned-terminal": {"handle": "owned-terminal"},
                                "foreign-terminal": {"handle": "foreign-terminal"}}}
        settled = {"worktrees": {"foreign": {"id": "foreign"}},
                   "terminals": {"foreign-terminal": {"handle": "foreign-terminal"}}}
        final = before if retain_owned else settled
        inventories = iter((before, settled, final))
        stopped = {"value": False}
        original_raw = probe.raw
        original_inventory = probe.OrcaProbe.inventory
        original_terminals = probe.OrcaProbe.worktree_terminals
        original_git = probe.git

        def fake_raw(argv: list[str], timeout: float = 30.0) -> dict[str, object]:
            if len(argv) > 2 and argv[2] == "stop":
                stopped["value"] = True
            if len(argv) > 2 and argv[2] == "rm":
                if remove_foreign:
                    foreign_path.unlink()
                    shutil.rmtree(root)
            return {"ok": False}

        def fake_git(path: str | Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
            if args[:2] == ("show-ref", "--verify"):
                return subprocess.CompletedProcess([], 1, "", "")
            if args[:2] in (("rev-parse", "HEAD"), ("rev-parse", "refs/heads/lane")):
                return subprocess.CompletedProcess([], 0, head + "\n", "")
            if args[:1] == ("for-each-ref",):
                return subprocess.CompletedProcess([], 0, "refs/heads/lane\nrefs/heads/foreign\n", "")
            return subprocess.CompletedProcess([], 0, "", "")

        probe.raw = fake_raw  # type: ignore[assignment]
        probe.OrcaProbe.inventory = lambda self: next(inventories)  # type: ignore[assignment]
        probe.OrcaProbe.worktree_terminals = lambda self, worktree_id: [] if stopped["value"] else [{"handle": "owned-terminal"}]  # type: ignore[assignment]
        probe.git = fake_git  # type: ignore[assignment]
        args = probe.parser().parse_args(["--repo", "repo", "cleanup", "--receipt", str(receipt_path),
                                          "--integration-head", head, "--foreign-path", str(foreign_path),
                                          "--settle-window", "0.01", "--interval", "0"])
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                probe.cleanup(args)
        except probe.ProbeError as error:
            return str(error)
        finally:
            probe.raw = original_raw  # type: ignore[assignment]
            probe.OrcaProbe.inventory = original_inventory  # type: ignore[assignment]
            probe.OrcaProbe.worktree_terminals = original_terminals  # type: ignore[assignment]
            probe.git = original_git  # type: ignore[assignment]
            if foreign_path.exists():
                foreign_path.unlink()
        raise AssertionError("cleanup unexpectedly reported success")


def test_cleanup_refuses_owned_residue_after_rm() -> None:
    assert "owned residue" in _cleanup_failure_case(retain_owned=True, remove_foreign=False)


def test_cleanup_refuses_foreign_resource_change() -> None:
    assert "foreign resource" in _cleanup_failure_case(retain_owned=False, remove_foreign=True)


def test_effect_reconciliation_accepts_one_same_handle_commit() -> None:
    with tempfile.TemporaryDirectory() as directory:
        worktree = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=worktree, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=worktree, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=worktree, check=True)
        (worktree / "change.txt").write_text("before\n", encoding="utf-8")
        subprocess.run(["git", "add", "change.txt"], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=worktree, check=True)
        pre_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=worktree, text=True).strip()
        (worktree / "change.txt").write_text("after\n", encoding="utf-8")
        subprocess.run(["git", "add", "change.txt"], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-qm", "feat: one slice"], cwd=worktree, check=True)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=worktree, text=True).strip()
        receipt = {"id": "lane", "path": str(worktree), "startupTerminal": {"handle": "same-handle"}}
        args = SimpleNamespace(
            phase="A_FINAL", timeout=1.0, log=str(worktree.parent / "effect-log"), pre_head=pre_head,
            expected_count=1, expected_subject=["feat: one slice"], expected_task=[],
            allow_path=["change.txt"], task_file="tasks.md", gate=["true"], park_comment="",
        )
        original_marker_frame = probe.marker_frame
        original_worktree_comment = probe.worktree_comment
        probe.marker_frame = lambda _probe, handle, phase: (head, None,
            {"result": {"terminal": {"handle": handle, "connected": True}}},
            {"result": {"terminal": {"handle": handle, "source": "screen"}}},
            f"TURN_DONE {phase} head={head}")
        probe.worktree_comment = lambda *_args: ""
        configured = probe.OrcaProbe("repo")
        configured.run = lambda _argv, timeout=30.0: {"ok": True}  # type: ignore[method-assign]
        try:
            result = probe.effect(args, configured, receipt, {"ok": False})
        finally:
            probe.marker_frame = original_marker_frame
            probe.worktree_comment = original_worktree_comment
        assert result["checks"]["same_handle"] is True
        assert result["checks"]["commit_subjects"] is True
        assert result["checks"]["paths"] is True


def test_effect_reconciliation_rejects_foreign_second_frame_handle() -> None:
    with tempfile.TemporaryDirectory() as directory:
        worktree = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=worktree, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=worktree, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=worktree, check=True)
        (worktree / "change.txt").write_text("before\n", encoding="utf-8")
        subprocess.run(["git", "add", "change.txt"], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=worktree, check=True)
        pre_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=worktree, text=True).strip()
        (worktree / "change.txt").write_text("after\n", encoding="utf-8")
        subprocess.run(["git", "add", "change.txt"], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "-qm", "feat: one slice"], cwd=worktree, check=True)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=worktree, text=True).strip()
        receipt = {"id": "lane", "path": str(worktree), "startupTerminal": {"handle": "same-handle"}}
        args = SimpleNamespace(phase="A_FINAL", timeout=1.0, log=str(worktree.parent / "foreign-log"),
                              pre_head=pre_head, expected_count=1, expected_subject=["feat: one slice"],
                              expected_task=[], allow_path=["change.txt"], task_file="tasks.md",
                              gate=["true"], park_comment="")
        frames = iter(("same-handle", "foreign-handle"))
        original_marker_frame = probe.marker_frame
        original_worktree_comment = probe.worktree_comment
        probe.marker_frame = lambda _probe, handle, phase: (
            head, None,
            {"result": {"terminal": {"handle": next(frames), "connected": True}}},
            {"result": {"terminal": {"handle": handle, "source": "screen"}}},
            f"TURN_DONE {phase} head={head}",
        )
        probe.worktree_comment = lambda *_args: ""
        configured = probe.OrcaProbe("repo")
        configured.run = lambda _argv, timeout=30.0: {"ok": True}  # type: ignore[method-assign]
        try:
            try:
                probe.effect(args, configured, receipt, {"ok": False})
            except probe.ProbeError as error:
                assert "incomplete or ambiguous effect" in str(error)
            else:
                raise AssertionError("foreign handle must fail reconciliation")
        finally:
            probe.marker_frame = original_marker_frame
            probe.worktree_comment = original_worktree_comment


def test_sync_moves_dependent_lane_to_exact_producer_commit_and_gate() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        (root / "seed").write_text("seed\n", encoding="utf-8")
        subprocess.run(["git", "add", "seed"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
        seed = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        subprocess.run(["git", "switch", "-c", "producer"], cwd=root, check=True, capture_output=True)
        (root / "producer").write_text("producer\n", encoding="utf-8")
        subprocess.run(["git", "add", "producer"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "producer"], cwd=root, check=True)
        producer = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        subprocess.run(["git", "switch", "-c", "dependent", seed], cwd=root, check=True, capture_output=True)
        args = SimpleNamespace(worktree=str(root), commit=producer, gate=["true"])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            probe.sync_commit(args)
        assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip() == producer
        assert '"status": "synchronized"' in output.getvalue()


def main() -> None:
    checks: tuple[Callable[[], None], ...] = tuple(
        value for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    )
    executed = 0
    for check in checks:
        check()
        executed += 1
    if executed != len(checks):
        raise AssertionError(f"executed {executed} of {len(checks)} declared checks")
    print(f"orca assisted probe contract: {executed}/{len(checks)} passed")


if __name__ == "__main__":
    main()
