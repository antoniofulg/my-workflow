"""Spec-derived checks for progress-aware post-cap remediation."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents/skills/autonomous"))
import remediation


def test_normalizes_failing_identifiers_to_a_stable_signature() -> None:
    result = remediation.transition_remediation(
        None,
        [
            "/tmp/project/specs/case.test.ts:12:4 > beta (12ms)",
            " /tmp/project/specs/case.test.ts:9:2 > alpha (8ms) ",
            "case.test.ts:9:2 > alpha",
        ],
    )
    assert result["failing_tests"] == ["case.test.ts > alpha", "case.test.ts > beta"]
    assert result["failing_signature"] == "case.test.ts > alpha | case.test.ts > beta"


def test_normalizes_mixed_language_and_ordinary_path_identifiers() -> None:
    result = remediation.normalize_failing_tests(
        [
            "/tmp/project/tools/test_adopt.py:123:4 > python",
            "tests/unit/widget.js(12,4): javascript",
            "relative/widget.js:8 > javascript",
            "tests/fixtures/ordinary.js > plain",
        ]
    )
    assert result == [
        "ordinary.js > plain",
        "test_adopt.py > python",
        "widget.js > javascript",
    ]


def test_uses_live_threshold_and_zero_is_unbounded() -> None:
    initial = remediation.transition_remediation(None, ["a"], stall_attempts=3)
    unbounded = remediation.transition_remediation(initial, ["a"], stall_attempts=0)
    still_unbounded = remediation.transition_remediation(unbounded, ["a"], stall_attempts=0)
    lowered = remediation.transition_remediation(still_unbounded, ["a"], stall_attempts=1)
    assert unbounded["stall_attempts"] == 0 and not unbounded["halted"]
    assert still_unbounded["consecutive_stalls"] == 2 and not still_unbounded["halted"]
    assert lowered["stall_attempts"] == 1 and lowered["halted"]


def test_equal_size_or_larger_sets_stall_and_strict_subset_resets() -> None:
    initial = remediation.transition_remediation(None, ["a", "b", "c"], stall_attempts=3)
    reordered = remediation.transition_remediation(initial, ["c", "b", "a"])
    renamed = remediation.transition_remediation(reordered, ["x", "y", "z"])
    reset = remediation.transition_remediation(renamed, ["a"])
    assert reordered["consecutive_stalls"] == 1
    assert renamed["consecutive_stalls"] == 2
    assert reset["status"] == "progress" and reset["consecutive_stalls"] == 0
    assert reset["minimum_failing_count"] == 1
    assert reset["minimum_failing_tests"] == ["a"]


def test_unrelated_smaller_set_is_a_stall_and_retains_the_minimum_set() -> None:
    initial = remediation.transition_remediation(None, ["a", "b", "c"])
    unrelated = remediation.transition_remediation(initial, ["x", "y"])
    assert unrelated["status"] == "stalled"
    assert unrelated["consecutive_stalls"] == 1
    assert unrelated["minimum_failing_tests"] == ["a", "b", "c"]
    assert unrelated["minimum_failing_count"] == 3


def test_halts_with_signature_attempt_count_and_fixes() -> None:
    state = remediation.transition_remediation(None, ["a"], fixes_tried=["guard input"])
    state = remediation.transition_remediation(state, ["a"], fixes_tried=["retry"])
    state = remediation.transition_remediation(state, ["a"], fixes_tried=["split test"])
    state = remediation.transition_remediation(state, ["a"], fixes_tried=["split again"])
    assert state["halted"] and state["reason"] == "stall_threshold_reached"
    assert state["attempt_count"] == 4
    assert state["report"] == {
        "reason": "stall_threshold_reached",
        "failing_signature": "a",
        "attempt_count": 4,
        "fixes_tried": ["guard input", "retry", "split test", "split again"],
    }


def test_unavailable_gate_halts_without_incrementing_stalls() -> None:
    state = remediation.transition_remediation(
        {"attempt_count": 4, "consecutive_stalls": 2, "failing_tests": ["a"]},
        ["a", "b"],
        gate_available=False,
        fixes_tried=["inspect output"],
    )
    assert state["halted"] and state["reason"] == "scoped_gate_unavailable"
    assert state["consecutive_stalls"] == 2
    assert state["attempt_count"] == 5


def test_rejects_invalid_thresholds() -> None:
    for invalid in (-1, 1.5, True, "3"):
        try:
            remediation.normalize_stall_attempts(invalid)
        except ValueError as error:
            assert str(error) == "stall_attempts must be a non-negative integer"
        else:
            raise AssertionError("invalid stall threshold was accepted")


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
