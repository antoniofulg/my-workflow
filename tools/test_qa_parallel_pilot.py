"""Contract test for the disposable E2E-001 pilot handoff."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
HANDOFF = ROOT / ".specs/features/parallel-slice-executor/qa-pilot.md"
HARNESS = ROOT / "tools/qa_parallel_pilot.py"


def test_pilot_handoff_uses_disposable_safe_fixture_and_dry_run_two_lanes() -> None:
    handoff = HANDOFF.read_text(encoding="utf-8")
    assert "qa_parallel_pilot.py setup" in handoff
    assert "qa_parallel_pilot.py dry-run" in handoff
    assert "qa_parallel_pilot.py cleanup" in handoff
    assert "--feature parallel-slice-executor" not in handoff
    setup = subprocess.run([sys.executable, str(HARNESS), "setup"], text=True, capture_output=True, check=True)
    fixture = json.loads(setup.stdout)["root"]
    fixture_root = Path(fixture)
    try:
        dry_run = subprocess.run(
            [sys.executable, str(HARNESS), "dry-run", "--root", fixture],
            text=True,
            capture_output=True,
            check=True,
        )
        result = json.loads(dry_run.stdout)
        assert result["mode"] == "safe"
        assert result["validated"] is True
        assert len(result["lanes"]) == 2
        assert all(lane["resources"] == [] for lane in result["lanes"])
        assert all(lane["status"] == "ready" for lane in result["lanes"])
    finally:
        subprocess.run([sys.executable, str(HARNESS), "cleanup", "--root", fixture], check=True)
    assert not fixture_root.exists()


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
