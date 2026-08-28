"""Contract checks for the adopted workflow-owned slice packet builder."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / ".agents/skills/workflow-spec-driven/scripts/slice_packet.py"


def request(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": 1,
        "feature": "feature-a",
        "slice": "S3",
        "tasks": ["T7"],
        "acceptance_criteria": ["HSE-03"],
        "test_ids": ["UT-002"],
        "gate": "python3 tools/test_workflow_spec_driven.py",
        "design_excerpt": "bounded packet design",
        "memory": "checkpoint memory",
    }
    value.update(overrides)
    return value


def run_builder(
    root: Path,
    body: dict[str, object],
    role: bytes = b"",
    output_path: Path | None = None,
) -> tuple[subprocess.CompletedProcess[str], Path, Path]:
    input_path = root / "request.json"
    output_path = output_path or root / "packet.md"
    telemetry_path = root / "telemetry.json"
    input_path.write_text(json.dumps(body), encoding="utf-8")
    role_path = root / "role.md"
    role_path.write_bytes(role)
    command = [
        sys.executable,
        str(BUILDER),
        "build",
        "--input",
        str(input_path),
        "--output",
        str(output_path),
        "--telemetry",
        str(telemetry_path),
        "--role-input",
        str(role_path),
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    return result, output_path, telemetry_path


def memory_length_for_slice_size(target: int) -> int:
    """Find an exact serialized size through the public CLI, not implementation internals."""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        low, high = 0, target
        while low <= high:
            length = (low + high) // 2
            result, output, telemetry = run_builder(root, request(memory="x" * length))
            report = json.loads(telemetry.read_text(encoding="utf-8"))
            output.unlink(missing_ok=True)
            if report["slice_bytes"] == target:
                return length
            if report["slice_bytes"] < target:
                low = length + 1
            else:
                high = length - 1
        raise AssertionError(f"could not produce an exact {target}-byte slice packet")


class WorkflowSpecDrivenTests(unittest.TestCase):
    def test_ut002_allowlist_rejects_transcript_before_materialization(self) -> None:
        unknown_fields = ("transcript", "full_state", "unrelated_slice")
        for field in unknown_fields:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                result, output, telemetry = run_builder(
                    Path(directory), request(**{field: "unrelated context"})
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())
                self.assertEqual(json.loads(telemetry.read_text())["error"], "unknown_field")

        with tempfile.TemporaryDirectory() as directory:
            result, output, _telemetry = run_builder(Path(directory), request())
            self.assertEqual(result.returncode, 0)
            packet = output.read_text(encoding="utf-8")
            for section in (
                "# Slice packet",
                "Feature: `feature-a`",
                "Slice: `S3`",
                "## Tasks\n- `T7`",
                "## Acceptance criteria\n- `HSE-03`",
                "## Tests\n- `UT-002`",
                "## Gate\n\n```text\npython3 tools/test_workflow_spec_driven.py\n```",
                "## Design excerpt\n\nbounded packet design",
                "## Slice memory\n\ncheckpoint memory",
            ):
                self.assertIn(section, packet)

    def test_ut003_exact_role_and_slice_budget_failures_are_effect_free(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result, output, telemetry = run_builder(root, request(), role=b"x" * 3_072)
            self.assertEqual(result.returncode, 0)
            self.assertTrue(output.exists())
            accepted_role = json.loads(telemetry.read_text())
            self.assertEqual(accepted_role["role_bytes"], 3_072)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result, output, telemetry = run_builder(root, request(), role=b"x" * 3_073)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())
            role_report = json.loads(telemetry.read_text())
            self.assertEqual(role_report["role_bytes"], 3_073)
            self.assertEqual(role_report["error"], "role_budget_exceeded")

        exact = memory_length_for_slice_size(10_240)
        with tempfile.TemporaryDirectory() as directory:
            result, output, telemetry = run_builder(Path(directory), request(memory="x" * exact))
            self.assertEqual(result.returncode, 0)
            self.assertTrue(output.exists())
            accepted_slice = json.loads(telemetry.read_text())
            self.assertEqual(accepted_slice["slice_bytes"], 10_240)

        exact_oversized = memory_length_for_slice_size(10_241)
        with tempfile.TemporaryDirectory() as directory:
            result, output, telemetry = run_builder(
                Path(directory), request(memory="x" * exact_oversized)
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())
            slice_report = json.loads(telemetry.read_text())
            self.assertEqual(slice_report["slice_bytes"], 10_241)
            self.assertEqual(slice_report["error"], "slice_budget_exceeded")

    def test_ut004_telemetry_reports_counts_without_packet_body(self) -> None:
        marker = "unique-packet-body-marker"
        with tempfile.TemporaryDirectory() as directory:
            result, output, telemetry = run_builder(
                Path(directory), request(memory=marker, design_excerpt="design")
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn(marker, output.read_text(encoding="utf-8"))
            telemetry_text = telemetry.read_text(encoding="utf-8")
            self.assertNotIn(marker, telemetry_text)
            report = json.loads(telemetry_text)
            self.assertTrue(report["within_budget"])
            self.assertEqual(report["slice_budget_bytes"], 10_240)
            self.assertEqual(report["role_budget_bytes"], 3_072)
            self.assertGreater(report["slice_bytes"], 0)
            self.assertEqual(report["components"], {"role": 0, "slice": report["slice_bytes"]})
            self.assertEqual(report["total_bytes"], report["slice_bytes"])
            self.assertNotIn("memory", report)
            self.assertNotIn("design_excerpt", report)

    def test_sec011_sensitive_unknown_input_never_enters_diagnostics(self) -> None:
        marker = "secret-marker-SEC-011"
        with tempfile.TemporaryDirectory() as directory:
            result, _output, telemetry = run_builder(
                Path(directory), request(unrelated_payload=marker)
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn(marker, result.stdout)
            self.assertNotIn(marker, result.stderr)
            self.assertNotIn(marker, telemetry.read_text(encoding="utf-8"))

            result, _output, telemetry = run_builder(
                Path(directory), request(), output_path=Path.home()
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout), {"error": "io_error", "ok": False})
            self.assertNotIn(str(Path.home()), result.stdout)
            self.assertNotIn(str(Path.home()), result.stderr)
            self.assertNotIn(str(Path.home()), telemetry.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
