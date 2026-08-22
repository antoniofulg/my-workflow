"""Regression tests for the vendored TLC spec and task validators."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / ".agents/skills/tlc-spec-driven/scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_spec  # noqa: E402
import validate_tasks  # noqa: E402


FIXTURES = Path(__file__).resolve().parent / "fixtures/tlc-validator"


def lines(name: str) -> list[str]:
    return (FIXTURES / name).read_text(encoding="utf-8").splitlines()


class TLCValidatorTests(unittest.TestCase):
    def test_nested_phase_definitions_keep_each_task_in_its_phase(self) -> None:
        self.assertEqual(
            validate_tasks.parse_phase_membership(lines("nested-phase-tasks.md")),
            {"T1": 1, "T2": 2},
        )


    def test_execution_plan_diagrams_map_later_task_definitions_to_their_phase(self) -> None:
        self.assertEqual(
            validate_tasks.parse_phase_membership(lines("diagram-phase-tasks.md")),
            {"T1": 1, "T2": 1, "T3": 2, "T4": 2},
        )
        errors, _warnings = validate_tasks.check(str(FIXTURES / "diagram-phase-tasks.md"))
        self.assertEqual(errors, [])


    def test_forward_phase_dependency_is_still_rejected(self) -> None:
        errors, _warnings = validate_tasks.check(
            str(FIXTURES / "diagram-forward-dependency.md")
        )
        self.assertTrue(any("T2 (phase 1) depends on T3 (phase 2)" in error for error in errors))


    def test_template_acceptance_criteria_suffix_and_blank_line_are_accepted(self) -> None:
        errors, warnings = validate_spec.check(
            str(FIXTURES / "acceptance-criteria-suffix.md")
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])


    def test_acceptance_criteria_without_shall_is_still_rejected(self) -> None:
        errors, _warnings = validate_spec.check(
            str(FIXTURES / "acceptance-criteria-no-shall.md")
        )
        self.assertTrue(any("acceptance criterion has no SHALL" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
