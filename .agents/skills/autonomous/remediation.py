#!/usr/bin/env python3
"""Pure remediation-stall normalization and transition helper.

The executable JSON protocol reads one object from stdin and writes the next
state to stdout. No repository, process, or remote authority is involved.
"""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Iterable, Mapping
from typing import Any

DEFAULT_STALL_ATTEMPTS = 3
_LOCATION = re.compile(r"(?P<path>(?:[A-Za-z]:[\\/]|/)?[^()\s]+?\.(?:test|spec)\.[^()\s:]+):\d+(?::\d+)?")
_TIMING = re.compile(r"\s*\(?\d+(?:\.\d+)?\s*(?:ms|s)\)?", re.IGNORECASE)
_WHITESPACE = re.compile(r"\s+")


def normalize_stall_attempts(value: Any) -> int:
    """Return the strict bound: absent is 3, zero is unbounded."""
    if value is None:
        return DEFAULT_STALL_ATTEMPTS
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("stall_attempts must be a non-negative integer")
    return value


def _normalize_test_name(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("failing test names must be strings")
    text = _TIMING.sub("", value.strip())

    def strip_location(match: re.Match[str]) -> str:
        path = match.group("path").replace("\\", "/").rsplit("/", 1)[-1]
        return path

    text = _LOCATION.sub(strip_location, text)
    return _WHITESPACE.sub(" ", text).strip()


def normalize_failing_tests(names: Iterable[Any]) -> list[str]:
    """Trim, de-time, de-path, deduplicate, and sort test identifiers."""
    if isinstance(names, (str, bytes)):
        raise ValueError("failing tests must be an array")
    values = {_normalize_test_name(name) for name in names}
    values.discard("")
    return sorted(values, key=lambda value: (value.casefold(), value))


def _normalize_fixes(fixes: Iterable[Any]) -> list[str]:
    if isinstance(fixes, (str, bytes)):
        raise ValueError("fixes_tried must be an array")
    result: list[str] = []
    seen: set[str] = set()
    for fix in fixes:
        if not isinstance(fix, str):
            raise ValueError("fixes_tried must contain strings")
        value = _WHITESPACE.sub(" ", fix.strip())
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _previous_tests(previous: Mapping[str, Any]) -> tuple[bool, list[str]]:
    if "failing_tests" not in previous:
        return False, []
    return True, normalize_failing_tests(previous.get("failing_tests", []))


def transition_remediation(
    previous: Mapping[str, Any] | None,
    failing_tests: Iterable[Any],
    *,
    stall_attempts: Any = None,
    gate_available: bool = True,
    fixes_tried: Iterable[Any] = (),
) -> dict[str, Any]:
    """Advance one post-cap remediation attempt without side effects."""
    previous_state: Mapping[str, Any] = previous or {}
    threshold = normalize_stall_attempts(stall_attempts)
    current = normalize_failing_tests(failing_tests)
    fixes = _normalize_fixes(previous_state.get("fixes_tried", []))
    for fix in _normalize_fixes(fixes_tried):
        if fix not in fixes:
            fixes.append(fix)
    attempt_count = int(previous_state.get("attempt_count", 0)) + 1
    prior_stalls = int(previous_state.get("consecutive_stalls", 0))
    had_baseline, prior_tests = _previous_tests(previous_state)
    minimum_count = int(previous_state.get("minimum_failing_count", len(prior_tests)))

    state: dict[str, Any] = {
        "stall_attempts": threshold,
        "failing_tests": current,
        "failing_signature": " | ".join(current),
        "attempt_count": attempt_count,
        "consecutive_stalls": prior_stalls,
        "minimum_failing_count": minimum_count,
        "fixes_tried": fixes,
        "halted": False,
    }

    if not gate_available:
        state.update({"status": "halted", "reason": "scoped_gate_unavailable", "halted": True})
        state["report"] = {
            "reason": state["reason"],
            "failing_signature": state["failing_signature"],
            "attempt_count": state["attempt_count"],
            "fixes_tried": state["fixes_tried"],
        }
        return state

    if not had_baseline or len(current) < minimum_count:
        state.update({
            "status": "progress",
            "reason": "smaller_failing_set" if had_baseline else "initial_failure_set",
            "consecutive_stalls": 0,
            "minimum_failing_count": len(current),
        })
        return state

    stalls = prior_stalls + 1
    state.update({"status": "stalled", "reason": "failing_set_not_smaller", "consecutive_stalls": stalls})
    if threshold and stalls >= threshold:
        state.update({"status": "halted", "reason": "stall_threshold_reached", "halted": True})
        state["report"] = {
            "reason": state["reason"],
            "failing_signature": state["failing_signature"],
            "attempt_count": state["attempt_count"],
            "fixes_tried": state["fixes_tried"],
        }
    return state


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        result = transition_remediation(
            payload.get("previous"),
            payload.get("failing_tests", []),
            stall_attempts=payload.get("stall_attempts"),
            gate_available=payload.get("gate_available", True),
            fixes_tried=payload.get("fixes_tried", []),
        )
    except (TypeError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
