"""Contract test for the disposable E2E-001 pilot handoff."""

from __future__ import annotations

import json
import shutil
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
        original_snapshot = dict(payload)
        ownership_path = fixture_root / ".parallel-slice-qa-ownership.json"
        ownership = json.loads(ownership_path.read_text(encoding="utf-8"))
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
        workflow.write_text(json.dumps(original_snapshot), encoding="utf-8")
        ownership_path.write_text(json.dumps(ownership), encoding="utf-8")
        subprocess.run([sys.executable, str(HARNESS), "cleanup", "--root", fixture], check=True)
        (fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned").unlink(missing_ok=True)


def test_cleanup_removes_exact_owned_worktree_and_preserves_unowned_sibling() -> None:
    setup = subprocess.run([sys.executable, str(HARNESS), "setup"], text=True, capture_output=True, check=True)
    fixture = json.loads(setup.stdout)["root"]
    fixture_root = Path(fixture)
    sibling_root = fixture_root.parent / f".{fixture_root.name}-parallel-slices"
    owned = sibling_root / "parallel-pilot" / "A-T1"
    unowned = sibling_root / "parallel-pilot" / "unowned"
    try:
        owned.parent.mkdir(parents=True)
        subprocess.run(["git", "worktree", "add", "--detach", str(owned), "HEAD"], cwd=fixture_root, check=True, capture_output=True)
        unowned.mkdir()
        sentinel = unowned / "sentinel"
        sentinel.write_text("preserve\n", encoding="utf-8")
        cleanup = subprocess.run([sys.executable, str(HARNESS), "cleanup", "--root", fixture], text=True, capture_output=True, check=False)
        assert cleanup.returncode != 0
        assert not owned.exists()
        assert sentinel.read_text(encoding="utf-8") == "preserve\n"
    finally:
        if fixture_root.exists():
            subprocess.run(["git", "worktree", "remove", "--force", str(owned)], cwd=fixture_root, check=False, capture_output=True)
        if fixture_root.exists():
            subprocess.run([sys.executable, str(HARNESS), "cleanup", "--root", fixture], check=False)
        if sibling_root.exists():
            shutil.rmtree(sibling_root)
        (fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned").unlink(missing_ok=True)


def test_cleanup_rejects_source_head_only_attestation_tamper_before_deletion() -> None:
    setup = subprocess.run([sys.executable, str(HARNESS), "setup"], text=True, capture_output=True, check=True)
    fixture = json.loads(setup.stdout)["root"]
    fixture_root = Path(fixture)
    ownership_path = fixture_root / ".parallel-slice-qa-ownership.json"
    original = json.loads(ownership_path.read_text(encoding="utf-8"))
    owned = fixture_root.parent / f".{fixture_root.name}-parallel-slices" / "parallel-pilot" / "A-T1"
    try:
        owned.parent.mkdir(parents=True)
        subprocess.run(["git", "worktree", "add", "--detach", str(owned), "HEAD"], cwd=fixture_root, check=True, capture_output=True)
        tampered = dict(original)
        tampered["source_git_head"] = "0" * 40
        ownership_path.write_text(json.dumps(tampered), encoding="utf-8")
        rejected = subprocess.run(
            [sys.executable, str(HARNESS), "cleanup", "--root", fixture],
            text=True,
            capture_output=True,
            check=False,
        )
        assert rejected.returncode != 0
        assert fixture_root.exists()
        assert (fixture_root / ".parallel-slice-qa-ownership.json").exists()
        assert owned.exists()
    finally:
        if fixture_root.exists():
            ownership_path.write_text(json.dumps(original), encoding="utf-8")
            subprocess.run([sys.executable, str(HARNESS), "cleanup", "--root", fixture], check=True)
        (fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned").unlink(missing_ok=True)


def test_cleanup_retry_preserves_residual_failure_until_residual_is_gone() -> None:
    setup = subprocess.run([sys.executable, str(HARNESS), "setup"], text=True, capture_output=True, check=True)
    fixture = json.loads(setup.stdout)["root"]
    fixture_root = Path(fixture)
    sibling_root = fixture_root.parent / f".{fixture_root.name}-parallel-slices"
    residual = sibling_root / "parallel-pilot" / "unowned" / "sentinel"
    residual.parent.mkdir(parents=True)
    residual.write_text("preserve\n", encoding="utf-8")
    attestation = fixture_root.parent / f".{fixture_root.name}.parallel-pilot-cleaned"
    try:
        first = subprocess.run(
            [sys.executable, str(HARNESS), "cleanup", "--root", fixture],
            text=True,
            capture_output=True,
            check=False,
        )
        first_result = json.loads(first.stdout)
        assert first.returncode != 0
        assert first_result["cleaned"] is False
        assert str(residual) in first_result["residual_paths"]
        record = json.loads(attestation.read_text(encoding="utf-8"))
        assert record["status"] == "cleaned-with-residual"
        assert str(residual) in record["residual_paths"]

        retry = subprocess.run(
            [sys.executable, str(HARNESS), "cleanup", "--root", fixture],
            text=True,
            capture_output=True,
            check=False,
        )
        retry_result = json.loads(retry.stdout)
        assert retry.returncode != 0
        assert retry_result["cleaned"] is False
        assert retry_result["residual_paths"] == first_result["residual_paths"]
        assert residual.read_text(encoding="utf-8") == "preserve\n"

        residual.unlink()
        residual.parent.rmdir()
        residual.parent.parent.rmdir()
        cleaned = subprocess.run(
            [sys.executable, str(HARNESS), "cleanup", "--root", fixture],
            text=True,
            capture_output=True,
            check=True,
        )
        cleaned_result = json.loads(cleaned.stdout)
        assert cleaned_result["cleaned"] is True
        assert cleaned_result["idempotent"] is True
    finally:
        if fixture_root.exists():
            subprocess.run([sys.executable, str(HARNESS), "cleanup", "--root", fixture], check=False)
        if sibling_root.exists():
            shutil.rmtree(sibling_root)
        attestation.unlink(missing_ok=True)


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
