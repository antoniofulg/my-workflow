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
        assert result["repository_head"] == result["source_git_head"]
        assert len(result["lanes"]) == 2
        assert all(lane["resources"] == [] for lane in result["lanes"])
        assert all(lane["status"] == "ready" for lane in result["lanes"])
    finally:
        first_cleanup = subprocess.run([sys.executable, str(HARNESS), "cleanup", "--root", fixture], text=True, capture_output=True, check=True)
        assert json.loads(first_cleanup.stdout)["idempotent"] is False
        second_cleanup = subprocess.run([sys.executable, str(HARNESS), "cleanup", "--root", fixture], text=True, capture_output=True, check=True)
        assert json.loads(second_cleanup.stdout)["idempotent"] is True
        (fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned").unlink()
    assert not fixture_root.exists()


def test_pilot_dry_run_rejects_frozen_head_mutation_and_unmarked_cleanup() -> None:
    setup = subprocess.run([sys.executable, str(HARNESS), "setup"], text=True, capture_output=True, check=True)
    fixture = json.loads(setup.stdout)["root"]
    fixture_root = Path(fixture)
    try:
        workflow = fixture_root / ".specs/features/parallel-pilot/workflow.json"
        payload = json.loads(workflow.read_text(encoding="utf-8"))
        payload["git_head"] = "0" * 40
        workflow.write_text(json.dumps(payload), encoding="utf-8")
        rejected = subprocess.run([sys.executable, str(HARNESS), "dry-run", "--root", fixture], text=True, capture_output=True, check=False)
        assert rejected.returncode != 0
        arbitrary = fixture_root.parent / "parallel-slice-pilot-unmarked"
        arbitrary.mkdir()
        try:
            refused = subprocess.run([sys.executable, str(HARNESS), "cleanup", "--root", str(arbitrary)], text=True, capture_output=True, check=False)
            assert refused.returncode != 0
            assert arbitrary.exists()
        finally:
            arbitrary.rmdir()
    finally:
        subprocess.run([sys.executable, str(HARNESS), "cleanup", "--root", fixture], check=True)
        (fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned").unlink(missing_ok=True)


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
