"""Spec-derived tests for durable blocker-fingerprint convergence."""

from __future__ import annotations

import shutil
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents/skills/workflow-spec-driven/scripts"))
import review_convergence


def test_feature_path_is_strict_kebab_and_bounded() -> None:
    root = Path(tempfile.mkdtemp())
    try:
        for feature in ("../escape", "feature/sub", ".", "Feature", "feature_name", "feature."):
            try:
                review_convergence.state_path(root, feature)
            except ValueError:
                pass
            else:
                raise AssertionError(f"unsafe feature slug accepted: {feature}")
        path = review_convergence.state_path(root, "parallel-slice-executor")
        assert path.resolve().parent == (root / ".specs/features/parallel-slice-executor").resolve()
    finally:
        shutil.rmtree(root)


def test_previous_fingerprint_must_exist_and_belong_to_same_requirement() -> None:
    root = Path(tempfile.mkdtemp())
    try:
        try:
            review_convergence.record_failure(root, "fixture", "EXE-08", "root", "path", previous_fingerprint="unknown")
        except ValueError as exc:
            assert "previous" in str(exc)
        else:
            raise AssertionError("unknown previous fingerprint must not create state")
        first = review_convergence.record_failure(root, "fixture", "EXE-08", "root", "path")
        try:
            review_convergence.record_failure(root, "fixture", "EXE-09", "changed", "path", previous_fingerprint=first["fingerprint"])
        except ValueError as exc:
            assert "requirement" in str(exc)
        else:
            raise AssertionError("foreign previous fingerprint must halt")
    finally:
        shutil.rmtree(root)


def test_python_gate_discovers_every_tools_test_suite() -> None:
    package = json.loads((Path(__file__).resolve().parent.parent / "package.json").read_text(encoding="utf-8"))
    script = package["scripts"]["test:python"]
    assert "find tools" in script and "test_*.py" in script and "sort" in script
    discovered = sorted(path.name for path in (Path(__file__).resolve().parent).rglob("test_*.py"))
    assert Path(__file__).name in discovered


def test_same_fingerprint_counts_failed_verifier_even_when_gate_is_green_and_halts_third() -> None:
    root = Path(tempfile.mkdtemp())
    try:
        first = review_convergence.record_failure(root, "fixture", "EXE-08", "release ordering", "worker-release", gate_passed=True)
        second = review_convergence.record_failure(root, "fixture", "EXE-08", "release ordering", "worker-release", gate_passed=True)
        third = review_convergence.record_failure(root, "fixture", "EXE-08", "release ordering", "worker-release", gate_passed=True)
        assert first["failed_remediations"] == 1
        assert second["failed_remediations"] == 2
        assert third["failed_remediations"] == 3
        assert third["status"] == "halted"
    finally:
        shutil.rmtree(root)


def test_distinct_fingerprints_are_independent_and_pass_does_not_increment() -> None:
    root = Path(tempfile.mkdtemp())
    try:
        first = review_convergence.record_failure(root, "fixture", "EXE-08", "release ordering", "worker-release")
        passed = review_convergence.record_result(root, "fixture", "EXE-08", "release ordering", "worker-release", verifier_failed=False, gate_passed=False)
        distinct = review_convergence.record_failure(root, "fixture", "EXE-09", "waiter state", "follow-up")
        assert first["failed_remediations"] == 1
        assert passed["failed_remediations"] == 1
        assert distinct["failed_remediations"] == 1
        assert first["fingerprint"] != distinct["fingerprint"]
    finally:
        shutil.rmtree(root)


def test_reopen_with_rewording_preserves_identity_and_count_after_restart() -> None:
    root = Path(tempfile.mkdtemp())
    try:
        first = review_convergence.record_failure(root, "fixture", "EXE-08", "release ordering", "worker-release")
        review_convergence.record_failure(root, "fixture", "EXE-08", "release ordering", "worker-release")
        reopened = review_convergence.record_failure(
            root, "fixture", "EXE-08", "release acceptance order", "worker-release", previous_fingerprint=first["fingerprint"]
        )
        assert reopened["fingerprint"] == first["fingerprint"]
        assert reopened["failed_remediations"] == 3
        assert reopened["status"] == "halted"
    finally:
        shutil.rmtree(root)


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
