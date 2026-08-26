"""Spec-derived tests for the fail-closed Maestri capability adapter."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents/skills/autonomous/scripts"))
import maestri_adapter


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


def test_complete_structured_manifest_is_machine_compatible_without_cli_mutation() -> None:
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
        assert result["status"] == "compatible"
        assert result["reason"] == "capability-manifest-complete"
        assert result["proof"]["cleanup"] == "clean"
        assert not list(root.iterdir())
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
