"""Regression tests for the vendored TLC spec and task validators."""

from __future__ import annotations

import sys
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / ".agents/skills/tlc-spec-driven/scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_spec  # noqa: E402
import validate_tasks  # noqa: E402
import validate_state  # noqa: E402


FIXTURES = Path(__file__).resolve().parent / "fixtures/tlc-validator"


def lines(name: str) -> list[str]:
    return (FIXTURES / name).read_text(encoding="utf-8").splitlines()


class TLCValidatorTests(unittest.TestCase):
    def _temporary_tasks(self, content: str) -> Path:
        directory = Path(tempfile.mkdtemp())
        path = directory / "tasks.md"
        path.write_text(content, encoding="utf-8")
        self.addCleanup(lambda: shutil.rmtree(directory))
        return path

    def test_explicit_fail_verdict_wins_over_legacy_result_pass(self) -> None:
        self.assertEqual(
            validate_state._verdict("**Verdict**: FAIL\n**Result**: PASS"),
            "fail",
        )


    def test_explicit_pass_verdict_wins_over_legacy_result_fail(self) -> None:
        self.assertEqual(
            validate_state._verdict("**Verdict**: PASS\n**Result**: FAIL"),
            "pass",
        )


    def test_legacy_result_pass_remains_supported(self) -> None:
        self.assertEqual(validate_state._verdict("**Result**: PASS"), "pass")


    def test_legacy_result_summary_pass_remains_supported(self) -> None:
        self.assertEqual(
            validate_state._verdict("**Result**: 1/1 killed — PASS."),
            "pass",
        )


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

    def test_validates_the_praxis_contract_as_one_slice(self) -> None:
        path = FIXTURES / "merge-alone-one-slice.md"
        contract = validate_tasks.validated_slice_contract(str(path))
        self.assertEqual(contract["slice_ids"], ["A"])
        self.assertEqual(len(contract["task_slices"]), 5)
        self.assertEqual(set(contract["task_slices"].values()), {"A"})
        self.assertEqual(contract["closures"]["A"]["merge_alone"], True)
        self.assertEqual(validate_tasks.check(str(path))[0], [])

    def test_validates_independent_slices_without_counting_remediation(self) -> None:
        contract = validate_tasks.validated_slice_contract(str(FIXTURES / "merge-alone-two-slices.md"))
        self.assertEqual(contract["slice_ids"], ["A", "B"])
        self.assertEqual(contract["task_slices"], {"T1": "A", "T2": "A", "T3": "B", "T4": "B"})

    def test_rejects_empty_closure_fields(self) -> None:
        source = (FIXTURES / "merge-alone-one-slice.md").read_text(encoding="utf-8")
        row = "| A | The complete migration is usable. | `python3 -m unittest` | yes | It is the requested deliverable. |"
        for replacement, expected in (
            ("| A |  | `python3 -m unittest` | yes | It is the requested deliverable. |", "observable outcome"),
            ("| A | The complete migration is usable. |  | yes | It is the requested deliverable. |", "independent gate"),
            ("| A | The complete migration is usable. | `python3 -m unittest` | yes |  |", "reason"),
        ):
            path = self._temporary_tasks(source.replace(row, replacement))
            with self.assertRaisesRegex(ValueError, expected):
                validate_tasks.validated_slice_contract(str(path))

    def test_requires_exact_lowercase_merge_alone_yes(self) -> None:
        source = (FIXTURES / "merge-alone-one-slice.md").read_text(encoding="utf-8")
        row = "| A | The complete migration is usable. | `python3 -m unittest` | yes | It is the requested deliverable. |"
        for value in ("no", "", "Yes", "true"):
            replacement = f"| A | The complete migration is usable. | `python3 -m unittest` | {value} | It is the requested deliverable. |"
            path = self._temporary_tasks(source.replace(row, replacement))
            with self.assertRaisesRegex(ValueError, "exact lowercase yes"):
                validate_tasks.validated_slice_contract(str(path))

    def test_rejects_inconsistent_primary_task_membership(self) -> None:
        source = (FIXTURES / "merge-alone-one-slice.md").read_text(encoding="utf-8")
        task_prefix = "**Slice:** A\n**Depends on:** None\n**Where:** `src/discovery.py`"
        cases = (
            (source.replace(task_prefix, "**Where:** `src/discovery.py`"), "T1"),
            (source.replace(task_prefix, "**Slice:** A\n**Slice:** B\n**Where:** `src/discovery.py`"), "exactly one Slice"),
            (source.replace(task_prefix, "**Slice:** Z\n**Where:** `src/discovery.py`"), "without a closure row"),
        )
        for content, expected in cases:
            path = self._temporary_tasks(content)
            with self.assertRaisesRegex(ValueError, expected):
                validate_tasks.validated_slice_contract(str(path))

    def test_rejects_duplicate_and_orphan_closure_rows(self) -> None:
        source = (FIXTURES / "merge-alone-one-slice.md").read_text(encoding="utf-8")
        row = "| A | The complete migration is usable. | `python3 -m unittest` | yes | It is the requested deliverable. |"
        duplicate = self._temporary_tasks(source.replace(row, row + "\n" + row))
        with self.assertRaisesRegex(ValueError, "repeats slice 'A'"):
            validate_tasks.validated_slice_contract(str(duplicate))
        orphan = self._temporary_tasks(source.replace(row, "| B | The complete migration is usable. | `python3 -m unittest` | yes | It is the requested deliverable. |"))
        with self.assertRaisesRegex(ValueError, "closure row has no primary task"):
            validate_tasks.validated_slice_contract(str(orphan))

    def test_slice_contract_json_is_deterministic_and_ordered(self) -> None:
        script = Path(__file__).resolve().parent.parent / ".agents/skills/tlc-spec-driven/scripts/validate_tasks.py"
        path = FIXTURES / "merge-alone-two-slices.md"
        command = [sys.executable, str(script), str(path), "--slice-contract-json"]
        first = subprocess.run(command, text=True, capture_output=True, check=True)
        second = subprocess.run(command, text=True, capture_output=True, check=True)
        self.assertEqual(first.stdout.encode(), second.stdout.encode())
        payload = json.loads(first.stdout)
        self.assertEqual(list(payload["task_slices"]), ["T1", "T2", "T3", "T4"])
        self.assertEqual(payload["slice_ids"], ["A", "B"])


if __name__ == "__main__":
    unittest.main()
