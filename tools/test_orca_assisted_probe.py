"""Runnable fake-Orca checks for the shipped assisted coordinator probe."""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
from types import SimpleNamespace
from pathlib import Path

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
            "printf '%s\\n' '{\"ok\":false,\"result\":{\"send\":{\"accepted\":false}}}'\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)
        packet = root / "coordinator-packet.md"
        packet.write_text("SECRET_PACKET_BODY\n" + ("body line\n" * 80)
                          + "TURN_DONE PHASE head=<current exact 40-hex HEAD>\n", encoding="utf-8")
        log = root / "probe.jsonl"
        env = {**os.environ, "CALLS": str(calls)}
        completed = subprocess.run(
            [sys.executable, str(ROOT / "orca_assisted_probe.py"), "--orca", str(fake), "--repo", "repo",
             "send-pointer", "--handle", "term-1", "--packet", str(packet), "--log", str(log)],
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


def test_public_dispatch_persists_packet_and_inspect_is_read_only() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        calls = root / "calls"
        fake = root / "orca"
        fake.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' \"$*\" >> \"$CALLS\"\n"
            "case \"$*\" in\n"
            "  *terminal\\ send*) printf '%s\\n' '{\"ok\":true}' ;;\n"
            "  *terminal\\ show*) printf '%s\\n' '{\"result\":{\"terminal\":{\"handle\":\"term-1\",\"connected\":true}}}' ;;\n"
            "  *) printf '%s\\n' '{\"ok\":true}' ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)
        marker = "DISPATCH_PACKET_MARKER"
        request = root / "request.json"
        state = root / "state.json"
        request.write_text(json.dumps({
            "schema_version": 1, "repository": "repo-1", "repository_root": str(root),
            "slice_id": "S4", "task_id": "T5", "operation_id": "op-1",
            "terminal_handle": "term-1", "packet_path": str(root / "packet.md"),
            "packet_body": marker,
            "log_path": str(root / "probe.jsonl"),
        }), encoding="utf-8")
        env = {**os.environ, "CALLS": str(calls)}
        dispatched = subprocess.run(
            [sys.executable, str(ROOT / "orca_assisted_probe.py"), "--orca", str(fake),
             "dispatch", "--request", str(request), "--state", str(state)],
            capture_output=True, text=True, env=env, check=False,
        )
        assert dispatched.returncode == 0, dispatched.stderr
        assert (root / "packet.md").read_text(encoding="utf-8") == marker
        assert marker not in calls.read_text(encoding="utf-8")
        inspected = subprocess.run(
            [sys.executable, str(ROOT / "orca_assisted_probe.py"), "--orca", str(fake),
             "inspect", "--state", str(state)],
            capture_output=True, text=True, env=env, check=False,
        )
        assert inspected.returncode == 0, inspected.stderr
        assert json.loads(inspected.stdout)["status"] == "inspected"
        call_lines = calls.read_text(encoding="utf-8").splitlines()
        assert len(call_lines) == 2
        assert call_lines[0].startswith("terminal send --terminal term-1 --text read ")
        assert call_lines[0].endswith(" and execute it as your packet --enter --json")
        assert call_lines[1] == "terminal show --terminal term-1 --json"


def test_cleanup_stops_only_owned_handle_and_preserves_foreign_worktree() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        receipt_path = root / "receipt.json"
        receipt_path.write_text(
            json.dumps({
                "id": "owned-worktree", "path": str(root), "branch": "refs/heads/owned",
                "pre_head": "a" * 40, "startupTerminal": {"handle": "owned-terminal"},
                "before": {"terminals": {}, "worktrees": {}},
            }), encoding="utf-8",
        )
        before = {"worktrees": {"owned-worktree": {"id": "owned-worktree"}, "foreign": {"id": "foreign"}}, "terminals": {}}
        after = {"worktrees": {"foreign": {"id": "foreign"}}, "terminals": {}}
        inventories = iter((before, after))
        calls: list[list[str]] = []
        original_raw = probe.raw
        original_inventory = probe.OrcaProbe.inventory
        original_terminals = probe.OrcaProbe.worktree_terminals
        probe.raw = lambda argv, timeout=30.0: calls.append(argv) or {"ok": True}  # type: ignore[assignment]
        probe.OrcaProbe.inventory = lambda self: next(inventories)  # type: ignore[assignment]
        probe.OrcaProbe.worktree_terminals = lambda self, worktree_id: [{"handle": "owned-terminal"}]  # type: ignore[assignment]
        args = probe.parser().parse_args(["--repo", "repo", "cleanup", "--receipt", str(receipt_path)])
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                probe.cleanup(args)
        finally:
            probe.raw = original_raw  # type: ignore[assignment]
            probe.OrcaProbe.inventory = original_inventory  # type: ignore[assignment]
            probe.OrcaProbe.worktree_terminals = original_terminals  # type: ignore[assignment]
        assert [call[2] for call in calls] == ["stop", "rm"]
        assert "foreign" in after["worktrees"]


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
            phase="A_FINAL", timeout=1.0, log=str(worktree / "log"), pre_head=pre_head,
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


def main() -> None:
    test_mutations_are_one_shot_and_reads_reconcile()
    test_pointer_transport_excludes_packet_body_and_import_is_inert()
    test_public_dispatch_persists_packet_and_inspect_is_read_only()
    test_cleanup_stops_only_owned_handle_and_preserves_foreign_worktree()
    print("orca assisted probe contract: 5/5 passed")


if __name__ == "__main__":
    main()
