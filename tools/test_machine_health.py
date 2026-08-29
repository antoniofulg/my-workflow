"""Spec-derived checks for normalized host admission evidence."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents/skills/autonomous/scripts"))
import machine_health


def healthy(observed: float = 10.0) -> dict[str, object]:
    return {
        "schema_version": 1,
        "observed_at_monotonic": observed,
        "cpu": "healthy",
        "memory": "healthy",
        "disk": "healthy",
        "heavy_gates_active": 0,
    }


def test_healthy_windows_scale_one_lane_and_never_override_caps() -> None:
    evidence = healthy()
    assert machine_health.should_admit_lane(2, "auto", evidence, now_monotonic=10) is True
    assert machine_health.should_admit_lane(3, "auto", evidence, now_monotonic=10) is True
    assert machine_health.should_admit_lane(4, "auto", evidence, now_monotonic=10) is False
    assert machine_health.should_admit_lane(2, 3, evidence, now_monotonic=10) is True
    assert machine_health.should_admit_lane(3, 3, evidence, now_monotonic=10) is False
    assert machine_health.should_admit_lane(1, 1, evidence, now_monotonic=10) is False


def test_missing_malformed_stale_or_pressured_evidence_denies_lane_above_baseline() -> None:
    cases: list[dict[str, object] | None] = [
        None,
        {**healthy(), "schema_version": 99},
        {**healthy(0), "observed_at_monotonic": 0},
        {**healthy(), "cpu": "pressured"},
        {**healthy(), "memory": "pressured"},
        {**healthy(), "disk": "pressured"},
    ]
    for evidence in cases:
        assert machine_health.should_admit_lane(2, "auto", evidence, now_monotonic=40) is False
    assert machine_health.should_admit_lane(2, "auto", healthy(), now_monotonic=10) is True


def test_non_finite_timestamps_and_non_integer_gate_counts_fail_closed() -> None:
    for evidence in (
        {**healthy(), "observed_at_monotonic": float("nan")},
        {**healthy(), "observed_at_monotonic": float("inf")},
        {**healthy(), "heavy_gates_active": 0.0},
        {**healthy(), "heavy_gates_active": True},
    ):
        assert machine_health.should_admit_lane(2, "auto", evidence, now_monotonic=10) is False


def test_health_reader_failure_denies_growth_without_exception() -> None:
    assert machine_health.should_admit_lane(2, "auto", None, now_monotonic=10) is False


def test_health_output_is_normalized() -> None:
    evidence = machine_health.collect_health(
        ".",
        now_monotonic=10,
        cpu_reader=lambda: "healthy",
        memory_reader=lambda: "healthy",
        disk_reader=lambda _: "healthy",
        heavy_gates_active=2,
    )
    assert set(evidence) == {
        "schema_version", "observed_at_monotonic", "cpu", "memory", "disk",
        "heavy_gates_active", "admit_one",
    }
    assert evidence["observed_at_monotonic"] == 10.0
    assert evidence["heavy_gates_active"] == 2
    assert evidence["admit_one"] is True
    assert all(isinstance(evidence[key], (int, float, bool, str)) for key in evidence)


def test_health_diagnostics_never_echo_host_markers() -> None:
    marker = "/Users/secret-user/packet-marker-command-env"
    evidence = machine_health.collect_health(
        marker,
        now_monotonic=10,
        cpu_reader=lambda: "healthy",
        memory_reader=lambda: "healthy",
        disk_reader=lambda _: "healthy",
    )
    assert marker not in json.dumps(evidence, sort_keys=True)
    assert all(marker not in str(value) for value in evidence.values())


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
