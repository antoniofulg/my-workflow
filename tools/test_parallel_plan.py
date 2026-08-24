"""Contract tests for the deterministic parallel slice planner."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents/skills/workflow-config/scripts"))
import parallel_plan


ROOT = Path(__file__).resolve().parent.parent


def make_repo(tasks: str, mode: str = "safe", feature: str = "fixture") -> Path:
    root = Path(tempfile.mkdtemp())
    feature_dir = root / ".specs/features" / feature
    feature_dir.mkdir(parents=True)
    (feature_dir / "tasks.md").write_text(tasks, encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    (root / "seed").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    (feature_dir / "workflow.json").write_text(
        json.dumps(
            {
                "feature": feature,
                "git_head": head,
                "parallelization": {"mode": mode},
                "version": 1,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return root


def task(
    task_id: str,
    slice_id: str | None,
    status: str = "pending",
    depends_on: str = "None",
    where: str | None = None,
    resources: str | None = "none",
) -> str:
    slice_field = f"**Slice:** {slice_id}\n" if slice_id is not None else ""
    where = where or f"src/{task_id.lower()}.py"
    return (
        f"### {task_id}: {task_id}\n"
        f"**Status:** {status}\n"
        f"{slice_field}"
        f"**Where:** {where}\n"
        f"**Depends on:** {depends_on}\n"
        + (f"**Resources:** {resources}\n" if resources is not None else "")
        + "\n"
    )


def first_task(plan: dict[str, object], task_id: str) -> dict[str, object]:
    return next(item for item in plan["lanes"] if item["task"] == task_id)  # type: ignore[index]


def blocked_task(plan: dict[str, object], task_id: str) -> dict[str, object]:
    return next(item for item in plan["blocked"] if item["task"] == task_id)  # type: ignore[index]


def test_slice_order_exposes_only_first_incomplete_task() -> None:
    root = make_repo(task("T1", "A") + task("T2", "A") + task("T3", "B"))
    try:
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert [item["task"] for item in plan["lanes"]] == ["T1", "T3"]
        assert blocked_task(plan, "T2")["reasons"] == ["slice-order:T1"]
    finally:
        shutil.rmtree(root)


def test_disabled_mode_returns_one_serial_lane_in_declared_order() -> None:
    root = make_repo(task("T1", "A") + task("T2", "B"), mode="disabled")
    try:
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert plan["fallback"] is False
        assert plan["lanes"] == [
            {"id": "serial", "slice": "A", "task": "T1", "status": "ready", "sync_after": [], "resources": []}
        ]
        assert blocked_task(plan, "T2")["reasons"] == ["disabled-mode"]
    finally:
        shutil.rmtree(root)


def test_safe_mode_requires_verified_cross_slice_producers() -> None:
    root = make_repo(
        task("T1", "A", status="complete")
        + task("T2", "B", depends_on="T1")
        + task("T3", "C")
    )
    try:
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert [item["task"] for item in plan["lanes"]] == ["T3"]
        assert blocked_task(plan, "T2")["reasons"] == ["awaiting-verified-slice:A"]

        verified = parallel_plan.plan(root=root, feature="fixture", verified_slices={"A"})
        assert [item["task"] for item in verified["lanes"]] == ["T2", "T3"]
    finally:
        shutil.rmtree(root)


def test_full_mode_records_completed_cross_slice_dependency_checkpoint() -> None:
    root = make_repo(
        task("T1", "A", status="complete") + task("T2", "B", depends_on="T1"), mode="full"
    )
    try:
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert first_task(plan, "T2")["sync_after"] == ["T1"]
        assert first_task(plan, "T2")["status"] == "ready"
    finally:
        shutil.rmtree(root)


def test_graph_failures_fall_back_with_decisive_reasons() -> None:
    cases = (
        (
            task("T1", "A", depends_on="T2") + task("T2", "B", depends_on="T1"),
            "dependency-cycle:",
        ),
        (task("T1", "A", depends_on="T99"), "unknown-dependency:T1->T99"),
        (task("T1", None), "missing-slice:T1"),
        (task("T1", "A", where="src/a.py, src/b.py"), "ambiguous-where:T1"),
    )
    for tasks, reason in cases:
        root = make_repo(tasks)
        try:
            plan = parallel_plan.plan(root=root, feature="fixture")
            assert plan["fallback"] is True
            assert any(reason in item for item in plan["reasons"])
            assert plan["lanes"][0]["id"] == "serial"
        finally:
            shutil.rmtree(root)


def test_write_collision_falls_back_and_names_both_tasks() -> None:
    root = make_repo(task("T1", "A", where="src/shared.py") + task("T2", "B", where="src/shared.py"))
    try:
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert plan["fallback"] is True
        assert "write-conflict:T1:T2:src/shared.py" in plan["reasons"]
    finally:
        shutil.rmtree(root)


def test_dependency_blocking_precedes_write_conflict_evaluation() -> None:
    root = make_repo(
        task("T1", "A", where="src/shared.py")
        + task("T2", "B", depends_on="T3", where="src/shared.py")
        + task("T3", "C")
    )
    try:
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert plan["fallback"] is False
        assert [item["task"] for item in plan["lanes"]] == ["T1", "T3"]
        assert blocked_task(plan, "T2")["reasons"] == ["dependency-incomplete:T3"]
    finally:
        shutil.rmtree(root)


def test_fallback_reasons_are_complete_and_ordered() -> None:
    root = make_repo(
        task("T1", None, depends_on="T99")
        + task("T2", "B", depends_on="T3")
        + task("T3", "C", depends_on="T2")
        + task("T4", "D", where="src/d.py, src/e.py")
    )
    try:
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert plan["fallback"] is True
        assert plan["reasons"] == [
            "missing-slice:T1",
            "ambiguous-where:T4",
            "unknown-dependency:T1->T99",
            "dependency-cycle:T2->T3->T2",
        ]
    finally:
        shutil.rmtree(root)


def test_in_progress_is_blocked_and_waiting_follows_up_after_dependencies() -> None:
    root = make_repo(
        task("T1", "A", status="in_progress") + task("T2", "B"), mode="safe"
    )
    try:
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert [item["task"] for item in plan["lanes"]] == ["T2"]
        assert blocked_task(plan, "T1")["reasons"] == ["in-progress:T1"]
    finally:
        shutil.rmtree(root)

    root = make_repo(
        task("T1", "A", status="waiting", depends_on="T2") + task("T2", "B"), mode="full"
    )
    try:
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert [item["task"] for item in plan["lanes"]] == ["T2"]
        assert blocked_task(plan, "T1")["reasons"] == ["waiting-on-dependency:T2"]
    finally:
        shutil.rmtree(root)

    root = make_repo(
        task("T1", "A", status="waiting", depends_on="T2")
        + task("T2", "B", status="complete"),
        mode="full",
    )
    try:
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert plan["lanes"] == [
            {
                "id": "slice-A",
                "slice": "A",
                "task": "T1",
                "status": "follow_up",
                "sync_after": ["T2"],
                "resources": [],
            }
        ]
    finally:
        shutil.rmtree(root)


def test_same_state_and_head_emit_byte_identical_json() -> None:
    root = make_repo(task("T1", "A") + task("T2", "B"))
    try:
        resolver = ROOT / ".agents/skills/workflow-config/scripts/parallel_plan.py"
        command = [sys.executable, str(resolver), "--root", str(root), "--feature", "fixture"]
        first = subprocess.run(command, text=True, capture_output=True, check=True)
        second = subprocess.run(command, text=True, capture_output=True, check=True)
        assert first.stdout.encode() == second.stdout.encode()
    finally:
        shutil.rmtree(root)


def test_missing_tasks_file_exits_nonzero_without_a_successful_plan() -> None:
    root = make_repo(task("T1", "A"))
    try:
        (root / ".specs/features/fixture/tasks.md").unlink()
        resolver = ROOT / ".agents/skills/workflow-config/scripts/parallel_plan.py"
        result = subprocess.run(
            [sys.executable, str(resolver), "--root", str(root), "--feature", "fixture"],
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 1
        assert result.stdout == ""
        assert "tasks file is missing or unreadable" in result.stderr
    finally:
        shutil.rmtree(root)


def test_snapshot_identity_and_version_are_validated_before_mode_and_head() -> None:
    root = make_repo(task("T1", "A"))
    path = root / ".specs/features/fixture/workflow.json"
    try:
        for snapshot in (
            {
                "feature": "other-feature",
                "git_head": "head",
                "parallelization": {"mode": "safe"},
                "version": 1,
            },
            {
                "feature": "fixture",
                "git_head": "head",
                "parallelization": {"mode": "safe"},
                "version": 2,
            },
        ):
            path.write_text(json.dumps(snapshot), encoding="utf-8")
            try:
                parallel_plan.plan(root=root, feature="fixture")
            except ValueError as exc:
                assert str(exc) == "invalid workflow snapshot"
            else:
                raise AssertionError("expected invalid workflow snapshot")
    finally:
        shutil.rmtree(root)


def test_malformed_snapshot_modes_exit_with_invalid_snapshot_error() -> None:
    root = make_repo(task("T1", "A"))
    path = root / ".specs/features/fixture/workflow.json"
    resolver = ROOT / ".agents/skills/workflow-config/scripts/parallel_plan.py"
    try:
        for mode in ({}, []):
            snapshot = {
                "feature": "fixture",
                "git_head": "head",
                "parallelization": {"mode": mode},
                "version": 1,
            }
            path.write_text(json.dumps(snapshot), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(resolver), "--root", str(root), "--feature", "fixture"],
                text=True,
                capture_output=True,
                check=False,
            )
            assert result.returncode == 1
            assert result.stdout == ""
            assert result.stderr == "parallel plan: invalid workflow snapshot\n"
    finally:
        shutil.rmtree(root)


def test_cli_emits_the_point_in_time_plan() -> None:
    root = make_repo(
        task("T1", "A", status="complete") + task("T2", "B", depends_on="T1"), mode="full"
    )
    try:
        resolver = ROOT / ".agents/skills/workflow-config/scripts/parallel_plan.py"
        result = subprocess.run(
            [sys.executable, str(resolver), "--root", str(root), "--feature", "fixture"],
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(result.stdout)
        head = json.loads(
            (root / ".specs/features/fixture/workflow.json").read_text(encoding="utf-8")
        )["git_head"]
        assert payload == {
            "blocked": [],
            "fallback": False,
            "feature": "fixture",
            "lanes": [
                {
                    "id": "slice-B",
                    "slice": "B",
                    "status": "ready",
                    "sync_after": ["T1"],
                    "resources": [],
                    "task": "T2",
                }
            ],
            "mode": "full",
            "reasons": [],
            "source_git_head": head,
            "version": 1,
        }
    finally:
        shutil.rmtree(root)


def test_resources_normalize_to_sorted_stable_lane_arrays() -> None:
    root = make_repo(task("T1", "A", resources="Port, Runtime") + task("T2", "B", resources="none"))
    try:
        first = parallel_plan.plan(root=root, feature="fixture")
        second = parallel_plan.plan(root=root, feature="fixture")
        assert first["lanes"][0]["resources"] == ["port", "runtime"]
        assert first["lanes"][1]["resources"] == []
        assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    finally:
        shutil.rmtree(root)


def test_invalid_resource_metadata_selects_serial_fallback_before_execution() -> None:
    cases = (
        (None, "missing-resources:T1"),
        ("", "invalid-resources:T1"),
        ("none, runtime", "mixed-none-resources:T1"),
        ("runtime, runtime", "duplicate-resources:T1:runtime"),
        ("runtime,,port", "invalid-resources:T1"),
        ("runtime and port", "invalid-resources:T1"),
        ("runtime/port", "invalid-resources:T1"),
    )
    for resources, expected in cases:
        root = make_repo(task("T1", "A", resources=resources))
        try:
            plan = parallel_plan.plan(root=root, feature="fixture")
            assert plan["fallback"] is True
            assert plan["reasons"] == [expected]
            assert plan["lanes"][0]["id"] == "serial"
            assert plan["lanes"][0]["resources"] == []
        finally:
            shutil.rmtree(root)


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
