"""Regression tests for the workflow spec and task validators."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / ".agents/skills/workflow-spec-driven/scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_spec  # noqa: E402
import validate_tasks  # noqa: E402
import validate_state  # noqa: E402


FIXTURES = Path(__file__).resolve().parent / "fixtures/tlc-validator"
ROW = "| A | The complete migration is usable. | `python3 -m unittest` | yes | It is the requested deliverable. |"


def lines(name: str) -> list[str]:
    return (FIXTURES / name).read_text(encoding="utf-8").splitlines()


class WorkflowValidatorTests(unittest.TestCase):
    def _temporary_tasks(self, content: str) -> Path:
        directory = Path(tempfile.mkdtemp())
        path = directory / "tasks.md"
        path.write_text(content, encoding="utf-8")
        self.addCleanup(lambda: shutil.rmtree(directory))
        return path

    def _one_slice_source(self) -> str:
        return (FIXTURES / "merge-alone-one-slice.md").read_text(encoding="utf-8")

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
        path = FIXTURES / "nested-phase-tasks.md"
        self.assertEqual(
            validate_tasks.parse_phase_membership(lines(path.name)),
            {"T1": 1, "T2": 2},
        )
        self.assertEqual(
            validate_tasks.validated_slice_contract(str(path))["task_slices"],
            {"T1": "A", "T2": "A"},
        )
        self.assertEqual(validate_tasks.check(str(path))[0], [])


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

    # MAS-UT-001: the Praxis migration is one slice across three technical cohorts.
    def test_praxis_migration_is_one_slice(self) -> None:
        path = FIXTURES / "merge-alone-one-slice.md"
        source = self._one_slice_source()
        cohorts = [ln for ln in source.splitlines() if ln.startswith("### Phase ")]
        primary = [ln for ln in source.splitlines() if validate_tasks.TASK_RE.match(ln)]
        self.assertEqual(len(cohorts), 3)
        self.assertEqual(len(primary), 5)
        contract = validate_tasks.validated_slice_contract(str(path))
        self.assertEqual(contract["slice_ids"], ["A"])
        self.assertEqual(len(contract["task_slices"]), 5)
        self.assertEqual(set(contract["task_slices"].values()), {"A"})
        self.assertTrue(contract["closures"]["A"]["merge_alone"])
        self.assertEqual(validate_tasks.check(str(path))[0], [])

    # MAS-UT-002: independently mergeable capabilities stay two slices.
    def test_independent_capabilities_are_two_slices(self) -> None:
        path = FIXTURES / "merge-alone-two-slices.md"
        contract = validate_tasks.validated_slice_contract(str(path))
        self.assertEqual(contract["slice_ids"], ["A", "B"])
        self.assertEqual(
            contract["task_slices"],
            {"T1": "A", "T2": "A", "T3": "B", "T4": "B"},
        )
        self.assertEqual(validate_tasks.check(str(path))[0], [])

    # MAS-UT-003: an incomplete closure row names the slice and the missing field.
    def test_rejects_incomplete_closure_fields(self) -> None:
        source = self._one_slice_source()
        row = ROW
        for replacement, expected in (
            (
                "| A |  | `python3 -m unittest` | yes | It is the requested deliverable. |",
                "slice 'A' has an empty observable outcome",
            ),
            (
                "| A | The complete migration is usable. |  | yes | It is the requested deliverable. |",
                "slice 'A' has an empty independent gate",
            ),
            (
                "| A | The complete migration is usable. | ` ` | yes | It is the requested deliverable. |",
                "slice 'A' has an empty independent gate",
            ),
            (
                "| A | The complete migration is usable. | `python3 -m unittest` | yes |  |",
                "slice 'A' has an empty reason",
            ),
        ):
            with self.subTest(expected=expected):
                path = self._temporary_tasks(source.replace(row, replacement))
                with self.assertRaisesRegex(ValueError, expected):
                    validate_tasks.validated_slice_contract(str(path))

    # MAS-UT-004: merge-alone accepts only exact lowercase `yes`.
    def test_requires_exact_lowercase_merge_alone_yes(self) -> None:
        source = self._one_slice_source()
        for value in ("no", "", "Yes", "true"):
            with self.subTest(value=value):
                replacement = (
                    "| A | The complete migration is usable. | `python3 -m unittest` | "
                    f"{value} | It is the requested deliverable. |"
                )
                path = self._temporary_tasks(source.replace(ROW, replacement))
                with self.assertRaisesRegex(ValueError, "slice 'A'.*exact lowercase yes"):
                    validate_tasks.validated_slice_contract(str(path))

    # MAS-UT-005: inconsistent primary-task membership names the task.
    def test_rejects_inconsistent_primary_task_membership(self) -> None:
        source = self._one_slice_source()
        prefix = "**Slice:** A\n**Depends on:** None\n**Where:** `src/discovery.py`"
        for content, expected in (
            (
                source.replace(prefix, "**Where:** `src/discovery.py`", 1),
                "T1: exactly one non-empty Slice field is required",
            ),
            (
                source.replace(prefix, "Slice: A\n**Where:** `src/discovery.py`", 1),
                r"T1: Slice field must use exactly `\*\*Slice:\*\*`",
            ),
            (
                source.replace(
                    prefix, "**Slice:** A\n**Slice:** B\n**Where:** `src/discovery.py`", 1
                ),
                "T1: exactly one Slice field is required",
            ),
            (
                source.replace(prefix, "**Slice:** Z\n**Where:** `src/discovery.py`", 1),
                "Z: primary tasks use a slice without a closure row",
            ),
        ):
            with self.subTest(expected=expected):
                path = self._temporary_tasks(content)
                with self.assertRaisesRegex(ValueError, expected):
                    validate_tasks.validated_slice_contract(str(path))

    # MAS-UT-006: duplicate and orphan closure rows name the invalid slice.
    def test_rejects_duplicate_and_orphan_closure_rows(self) -> None:
        source = self._one_slice_source()
        duplicate = self._temporary_tasks(source.replace(ROW, ROW + "\n" + ROW))
        with self.assertRaisesRegex(ValueError, "repeats slice 'A'"):
            validate_tasks.validated_slice_contract(str(duplicate))
        orphan = self._temporary_tasks(source.replace(ROW, ROW.replace("| A |", "| B |", 1)))
        with self.assertRaisesRegex(ValueError, "B: closure row has no primary task"):
            validate_tasks.validated_slice_contract(str(orphan))

    # MAS-UT-007: review remediation records never join the primary contract.
    def test_remediation_records_do_not_inflate_the_contract(self) -> None:
        path = FIXTURES / "merge-alone-two-slices.md"
        source = path.read_text(encoding="utf-8")
        self.assertIn("### T2R1:", source)
        self.assertIn("### TDR1:", source)
        self.assertIn("**Slice:** B", source.split("### TDR1:")[1])
        contract = validate_tasks.validated_slice_contract(str(path))
        self.assertNotIn("T2R1", contract["task_slices"])
        self.assertNotIn("TDR1", contract["task_slices"])
        self.assertEqual(len(contract["slice_ids"]), 2)

    # MAS-UT-008: --slice-contract-json is deterministic and in document order.
    def test_slice_contract_json_is_deterministic_and_ordered(self) -> None:
        command = [
            sys.executable,
            str(SCRIPTS / "validate_tasks.py"),
            str(FIXTURES / "merge-alone-two-slices.md"),
            "--slice-contract-json",
        ]
        first = subprocess.run(command, text=True, capture_output=True, check=True)
        second = subprocess.run(command, text=True, capture_output=True, check=True)
        self.assertEqual(first.stdout.encode(), second.stdout.encode())
        payload = json.loads(first.stdout)
        self.assertEqual(list(payload["task_slices"]), ["T1", "T2", "T3", "T4"])
        self.assertEqual(payload["slice_ids"], ["A", "B"])


if __name__ == "__main__":
    unittest.main()
