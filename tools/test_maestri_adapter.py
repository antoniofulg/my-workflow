"""Spec-derived tests for the fail-closed Maestri capability adapter."""

from __future__ import annotations

import shutil
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents/skills/autonomous/scripts"))
import maestri_adapter
import parallel_execute


def test_missing_environment_reports_capabilities_without_mutation() -> None:
    root = Path(tempfile.mkdtemp())
    original_which = maestri_adapter.shutil.which
    try:
        maestri_adapter.shutil.which = lambda _: None  # type: ignore[assignment]
        adapter = maestri_adapter.MaestriAdapter(root, "fixture", environment={})
        result = adapter.probe()
        assert result["status"] == "unsupported"
        assert result["reason"] == "missing-capabilities"
        assert result["missing_capabilities"] == list(maestri_adapter.REQUIRED_CAPABILITIES)
        assert not list(root.iterdir())
    finally:
        maestri_adapter.shutil.which = original_which  # type: ignore[assignment]
        shutil.rmtree(root)


def test_current_cli_manifest_stays_unsupported_for_unstructured_lifecycle() -> None:
    root = Path(tempfile.mkdtemp())
    original_which = maestri_adapter.shutil.which
    try:
        maestri_adapter.shutil.which = lambda _: "/usr/local/bin/maestri"  # type: ignore[assignment]
        adapter = maestri_adapter.MaestriAdapter(
            root,
            "fixture",
            terminal_id="terminal-A",
            socket_path="/tmp/maestri.sock",
            capabilities=["terminal_identity", "daemon_socket", "cli_path", "agent_dismissal"],
        )
        result = adapter.probe()
        assert result["status"] == "unsupported"
        assert result["missing_capabilities"] == [
            "structured_floor_receipts", "structured_agent_receipts", "structured_completion_events", "floor_deletion",
        ]
        assert result["proof"]["cleanup"] == "not-run"
    finally:
        maestri_adapter.shutil.which = original_which  # type: ignore[assignment]
        shutil.rmtree(root)


def test_complete_structured_manifest_stays_unsupported_without_cli_mutation() -> None:
    root = Path(tempfile.mkdtemp())
    original_which = maestri_adapter.shutil.which
    try:
        maestri_adapter.shutil.which = lambda _: "/usr/local/bin/maestri"  # type: ignore[assignment]
        result = maestri_adapter.MaestriAdapter(
            root,
            "fixture",
            terminal_id="terminal-A",
            socket_path="/tmp/maestri.sock",
            capabilities=list(maestri_adapter.REQUIRED_CAPABILITIES),
        ).probe()
        assert result["status"] == "unsupported"
        assert result["reason"] == "host-owned-execution-unimplemented"
        assert result["proof"]["cleanup"] == "not-run"
        assert not list(root.iterdir())
    finally:
        maestri_adapter.shutil.which = original_which  # type: ignore[assignment]
        shutil.rmtree(root)


def test_complete_manifest_cannot_reach_generic_git_worktree_execution() -> None:
    root = Path(tempfile.mkdtemp())
    original_which = maestri_adapter.shutil.which
    try:
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        (root / "seed").write_text("seed\n", encoding="utf-8")
        subprocess.run(["git", "add", "seed"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        feature_dir = root / ".specs" / "features" / "fixture"
        feature_dir.mkdir(parents=True)
        (feature_dir / "tasks.md").write_text(
            "### T1: first\n**Status:** pending\n**Slice:** A\n**Where:** src/a.py\n**Depends on:** None\n",
            encoding="utf-8",
        )
        (feature_dir / "workflow.json").write_text(json.dumps({
            "feature": "fixture", "git_head": head,
            "parallelization": {"mode": "safe"}, "version": 2,
        }), encoding="utf-8")
        maestri_adapter.shutil.which = lambda _: "/usr/local/bin/maestri"  # type: ignore[assignment]
        host = maestri_adapter.MaestriAdapter(
            root, "fixture", terminal_id="terminal-A", socket_path="/tmp/maestri.sock",
            capabilities=list(maestri_adapter.REQUIRED_CAPABILITIES),
        )
        coordinator = parallel_execute.Coordinator(
            root, "fixture", adapter_factory=lambda: host,
            worktree_creator=lambda *_: (_ for _ in ()).throw(AssertionError("Maestri must not create Git worktrees")),
        )
        coordinator._plan = lambda: {"fallback": False, "lanes": [{
            "id": "slice-A", "slice": "A", "task": "T1", "status": "ready", "sync_after": [], "resources": [],
        }]}  # type: ignore[method-assign]
        result = coordinator.start()
        assert result["fallback"] is True
        assert result["reason"] == "maestri:host-owned-execution-unimplemented"
        assert not list(root.parent.glob(f".{root.name}-parallel-slices"))
    finally:
        maestri_adapter.shutil.which = original_which  # type: ignore[assignment]
        shutil.rmtree(root)


def test_malformed_manifest_is_rejected_without_parsing_human_output() -> None:
    root = Path(tempfile.mkdtemp())
    try:
        result = maestri_adapter.MaestriAdapter(
            root, "fixture", environment={"MAESTRI_CAPABILITIES_JSON": "floor create succeeded"}
        ).probe()
        assert result["status"] == "unsupported"
        assert result["reason"] == "malformed-capability-manifest"
        assert result["missing_capabilities"] == list(maestri_adapter.REQUIRED_CAPABILITIES)
    finally:
        shutil.rmtree(root)


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"{len(tests)} passed, 0 failed")
