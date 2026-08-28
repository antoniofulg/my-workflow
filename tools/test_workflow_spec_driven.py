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


def run_builder(root: Path, body: dict[str, object], role: bytes = b"") -> tuple[subprocess.CompletedProcess[str], Path, Path]:
    input_path = root / "request.json"
    output_path = root / "packet.md"
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


class WorkflowSpecDrivenTests(unittest.TestCase):
    def test_ut002_allowlist_rejects_transcript_before_materialization(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result, output, telemetry = run_builder(
                Path(directory), request(transcript="whole conversation")
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())
            self.assertEqual(json.loads(telemetry.read_text())["error"], "unknown_field")

    def test_ut003_exact_role_and_slice_budget_failures_are_effect_free(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result, output, telemetry = run_builder(root, request(), role=b"x" * 3_073)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())
            role_report = json.loads(telemetry.read_text())
            self.assertEqual(role_report["role_bytes"], 3_073)
            self.assertEqual(role_report["error"], "role_budget_exceeded")

            oversized = request(memory="x" * 11_000)
            result, output, telemetry = run_builder(root, oversized)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())
            slice_report = json.loads(telemetry.read_text())
            self.assertGreaterEqual(slice_report["slice_bytes"], 10_241)
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


if __name__ == "__main__":
    unittest.main()
