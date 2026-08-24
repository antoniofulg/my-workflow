"""Spec-derived tests for durable blocker-fingerprint convergence."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents/skills/tlc-spec-driven/scripts"))
import review_convergence


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
