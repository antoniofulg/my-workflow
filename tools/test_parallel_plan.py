"""Contract tests for the deterministic parallel slice planner."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents/skills/workflow-config/scripts"))
import parallel_plan

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / ".agents/skills/workflow-spec-driven/scripts"))
import validate_tasks  # noqa: E402
import test_workflow_config as workflow_fixtures  # noqa: E402


def closure_for(tasks: str) -> str:
    """Build the closure contract every `**Slice:**` value in `tasks` needs to validate."""
    slice_ids = list(dict.fromkeys(re.findall(r"^\*\*Slice:\*\* (\S+)$", tasks, re.MULTILINE)))
    rows = "".join(
        f"| {slice_id} | Capability {slice_id}. | `gate-{slice_id.lower()}` | yes | Independent value. |\n"
        for slice_id in slice_ids
    )
    return (
        "## Vertical Slice Closure\n\n"
        "| Slice | Observable outcome | Independent gate | Merge if later slices are cancelled? | Why |\n"
        "| --- | --- | --- | --- | --- |\n"
        f"{rows}\n"
        "## Task Breakdown\n\n"
    )


def make_repo(
    tasks: str,
    mode: str = "assisted",
    feature: str = "fixture",
    max_workers: str | int = "auto",
) -> Path:
    root = Path(tempfile.mkdtemp())
    feature_dir = root / ".specs/features" / feature
    feature_dir.mkdir(parents=True)
    (feature_dir / "tasks.md").write_text(closure_for(tasks) + tasks, encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    (root / "seed").write_text("seed\n", encoding="utf-8")
    agents = root / ".codex" / "agents"
    agents.mkdir(parents=True)
    for name in ("implementer", "verifier", "explorer", "deep-reviewer", "designer"):
        (agents / f"{name}.toml").write_text(
            'model = "gpt-test"\nmodel_reasoning_effort = "medium"\ndeveloper_instructions = ""\n',
            encoding="utf-8",
        )
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    (feature_dir / "workflow.json").write_text(
        json.dumps(
            {
                "feature": feature,
                "git_head": head,
                "profile": None,
                "overrides": {},
                "deep_review": {"cadence": "feature", "groups": [[1]]},
                "parallelization": {
                    "mode": mode,
                    "max_workers": max_workers,
                    "automatic_baseline": 2,
                    "automatic_ceiling": 4,
                    "resource_provider": None,
                },
                "roles": {
                    role: {
                        "provider": "codex",
                        "agent_file": f".codex/agents/{'deep-reviewer' if role == 'deep_reviewer' else role}.toml",
                        "model": "gpt-test",
                        "effort": "medium",
                    }
                    for role in ("implementer", "verifier", "explorer", "deep_reviewer", "designer")
                },
                "version": 3,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", ".specs/features"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "freeze workflow"], cwd=root, check=True)
    return root


CLOSURE = (
    "## Vertical Slice Closure\n\n"
    "| Slice | Observable outcome | Independent gate | Merge if later slices are cancelled? | Why |\n"
    "| --- | --- | --- | --- | --- |\n"
    "| A | First capability. | `gate-a` | yes | Independent value. |\n"
    "| B | Second capability. | `gate-b` | yes | Independent value. |\n\n"
    "## Task Breakdown\n\n"
)


def make_resolver_repo(tasks: str, feature: str = "fixture") -> Path:
    """Build a repository whose snapshot the resolver derived from the closure contract."""
    root = workflow_fixtures.make_root()
    workflow_fixtures.write_config(root)
    workflow_fixtures.write_packets(root)
    workflow_fixtures.write_tasks(root, tasks, feature)
    workflow_fixtures.workflow_config.sync_agents(root)
    workflow_fixtures.git_root(root)
    workflow_fixtures.workflow_config.resolve(root=root, feature=feature, native_provider="codex")
    return root


# A review remediation record: no primary task, and a slice field the validator ignores.
REMEDIATION = "### T2R1: review remediation\n**Slice:** B\n\n"


# MAS-IT-008: the planner reports exactly the validator's primary-task membership.
def test_resolved_snapshot_preserves_validator_slice_membership() -> None:
    tasks = (
        CLOSURE
        + task("T1", "A")
        + task("T2", "A")
        + REMEDIATION
        + task("T3", "B")
        + task("T4", "B")
    )
    root = make_resolver_repo(tasks)
    try:
        snapshot = json.loads(
            (root / ".specs/features/fixture/workflow.json").read_text(encoding="utf-8")
        )
        assert snapshot["deep_review"]["groups"] == [[1, 2]]
        contract = validate_tasks.validated_slice_contract(
            str(root / ".specs/features/fixture/tasks.md")
        )
        plan = parallel_plan.plan(root=root, feature="fixture")
        planned = {item["task"]: item["slice"] for item in [*plan["lanes"], *plan["blocked"]]}
        assert planned == contract["task_slices"]
        assert plan["source_git_head"] == snapshot["git_head"]
    finally:
        shutil.rmtree(root)


# MAS-IT-011: every heading shape the validator accepts is planned with its membership.
def test_planner_finds_every_task_heading_the_validator_accepts() -> None:
    tasks = task("T1", "A") + task("T2", "A") + task("T3", "B") + task("T4", "B")
    tasks = (
        tasks.replace("### T1: T1", "## T1: T1", 1)
        .replace("### T2: T2", "#### T2: T2", 1)
        .replace("### T3: T3", "### t3: T3", 1)
    )
    root = make_repo(tasks)
    try:
        contract = validate_tasks.validated_slice_contract(
            str(root / ".specs/features/fixture/tasks.md")
        )
        assert set(contract["task_slices"]) == {"T1", "T2", "T3", "T4"}
        plan = parallel_plan.plan(root=root, feature="fixture")
        planned = {item["task"]: item["slice"] for item in [*plan["lanes"], *plan["blocked"]]}
        assert planned == contract["task_slices"]
    finally:
        shutil.rmtree(root)


# MAS-IT-012: a task listed under a phase and defined later is one task to both readers.
def test_planner_reads_a_phase_listing_and_its_definition_as_one_task() -> None:
    tasks = (
        "### Phase 1: Foundation\n\n#### T1: T1\n\n#### T2: T2\n\n"
        + task("T1", "A")
        + task("T2", "B")
    )
    root = make_repo(tasks)
    try:
        contract = validate_tasks.validated_slice_contract(
            str(root / ".specs/features/fixture/tasks.md")
        )
        plan = parallel_plan.plan(root=root, feature="fixture")
        planned = {item["task"]: item["slice"] for item in [*plan["lanes"], *plan["blocked"]]}
        assert plan["fallback"] is False
        assert plan["reasons"] == []
        assert planned == contract["task_slices"]
    finally:
        shutil.rmtree(root)


# MAS-IT-008: a contract the validator rejects fails the plan closed, with its message.
def test_plan_fails_closed_when_the_validator_rejects_the_contract() -> None:
    valid = CLOSURE + task("T1", "A") + task("T2", "B")
    cases = (
        (valid.replace("**Slice:** B", "**slice:** B", 1), "T2: Slice field must use exactly"),
        (
            valid.replace("| B | Second capability. | `gate-b` | yes | Independent value. |\n", "", 1),
            "B: primary tasks use a slice without a closure row",
        ),
    )
    for tasks, expected in cases:
        root = make_repo(tasks)
        try:
            (root / ".specs/features/fixture/tasks.md").write_text(tasks, encoding="utf-8")
            try:
                parallel_plan.plan(root=root, feature="fixture")
            except ValueError as exc:
                assert expected in str(exc)
            else:
                raise AssertionError(f"expected the validator to reject: {expected}")
        finally:
            shutil.rmtree(root)


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


# MAS-IT-010: a remediation record donates no field to the primary task above it.
def test_planner_ignores_remediation_record_fields() -> None:
    # T2 opens slice B, so it plans as a ready lane whose entry carries `status`,
    # `resources` and `sync_after` - the fields the record would leak into.
    tasks = task("T1", "A") + task("T2", "B") + task("T3", "B") + task("T4", "A")
    record = (
        "### T2R1: review remediation\n"
        "**Status:** complete\n"
        "**Resources:** db\n"
        "**Depends on:** T3\n\n"
    )
    with_record = tasks.replace(task("T3", "B"), record + task("T3", "B"), 1)
    plain_root = make_repo(tasks)
    record_root = make_repo(with_record)
    try:
        plain = parallel_plan.plan(root=plain_root, feature="fixture")
        recorded = parallel_plan.plan(root=record_root, feature="fixture")
        assert first_task(plain, "T2")["resources"] == []
        assert first_task(recorded, "T2") == first_task(plain, "T2")
        assert entry_for(recorded, "T2") == entry_for(plain, "T2")
        assert recorded["fallback"] == plain["fallback"]
        assert recorded["reasons"] == plain["reasons"]
    finally:
        shutil.rmtree(plain_root)
        shutil.rmtree(record_root)


def entry_for(plan: dict[str, object], task_id: str) -> dict[str, object]:
    return next(
        item
        for item in [*plan["lanes"], *plan["blocked"]]  # type: ignore[misc]
        if item["task"] == task_id  # type: ignore[index]
    )


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
            {"id": "serial", "slice": "A", "task": "T1", "status": "ready",
             "execution": "serial-integration", "worktree": False,
             "sync_after": [], "declared_paths": ["src/t1.py"], "resources": []}
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
        task("T1", "A", status="complete") + task("T2", "B", depends_on="T1"), mode="assisted"
    )
    try:
        plan = parallel_plan.plan(root=root, feature="fixture", verified_slices={"A"})
        lane = first_task(plan, "T2")
        assert lane["sync_after"] == ["T1"]
        assert lane["status"] == "ready"
        assert lane["declared_paths"] == ["src/t1.py"]
    finally:
        shutil.rmtree(root)


def test_full_mode_declares_sorted_union_of_producer_paths_for_checkpoint() -> None:
    root = make_repo(
        task("T1", "A", status="complete", where="src/z.py")
        + task("T2", "B", status="complete", where="src/a.py")
        + task("T3", "C", depends_on="T1, T2", where="src/consumer.py"),
        mode="assisted",
    )
    try:
        lane = first_task(
            parallel_plan.plan(root=root, feature="fixture", verified_slices={"A", "B"}), "T3"
        )
        assert lane["sync_after"] == ["T1", "T2"]
        assert lane["declared_paths"] == ["src/a.py", "src/z.py"]
    finally:
        shutil.rmtree(root)


def test_graph_failures_fall_back_with_decisive_reasons() -> None:
    cases = (
        (
            task("T1", "A", depends_on="T2") + task("T2", "B", depends_on="T1"),
            "dependency-cycle:",
        ),
        (task("T1", "A", depends_on="T99"), "unknown-dependency:T1->T99"),
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


def test_write_collision_serializes_with_exact_paths() -> None:
    root = make_repo(task("T1", "A", where="src/shared.py") + task("T2", "B", where="src/shared.py"))
    try:
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert plan["fallback"] is False
        assert plan["decision"] == "serial-integration"
        assert plan["lanes"][0]["task"] == "T1"
        assert blocked_task(plan, "T2")["reasons"] == [
            "write-conflict:T1:T2:src/shared.py:src/shared.py"
        ]
    finally:
        shutil.rmtree(root)


def test_one_ready_assisted_slice_is_explicit_serial_integration_without_worktree() -> None:
    root = make_repo(task("T1", "A"))
    try:
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert plan["decision"] == "serial-integration"
        assert plan["compatibility"]["selected"] == ["T1"]
        assert plan["lanes"] == [{
            "id": "serial", "slice": "A", "task": "T1", "status": "ready",
            "execution": "serial-integration", "worktree": False, "sync_after": [],
            "declared_paths": ["src/t1.py"], "resources": [],
        }]
        assert plan["role_worktrees"]["implementer"] is False
    finally:
        shutil.rmtree(root)


def test_concurrent_writer_selection_is_capped_and_not_parity_bound() -> None:
    root = make_repo(task("T1", "A") + task("T2", "B") + task("T3", "C") + task("T4", "D"))
    try:
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert plan["decision"] == "concurrent-writers"
        assert plan["compatibility"]["selected"] == ["T1", "T2"]
        assert [lane["task"] for lane in plan["lanes"]] == ["T1", "T2"]
        assert all(lane["worktree"] is True for lane in plan["lanes"])
        assert plan["role_worktrees"] == {
            "planner": False,
            "coordinator": False,
            "implementer": True,
            "explorer": False,
            "verifier": False,
            "deep_reviewer": False,
            "qa_plan": False,
            "qa_execute": False,
        }
        assert blocked_task(plan, "T3")["reasons"] == ["writer-cap:2"]
        assert blocked_task(plan, "T4")["reasons"] == ["writer-cap:2"]
    finally:
        shutil.rmtree(root)


def test_initial_admission_uses_baseline_before_explicit_ceiling() -> None:
    tasks = task("T1", "A") + task("T2", "B") + task("T3", "C") + task("T4", "D")
    for cap in ("auto", 1, 2, 3, 4):
        root = make_repo(tasks, max_workers=cap)
        try:
            plan = parallel_plan.plan(root=root, feature="fixture")
            expected_count = 1 if cap == 1 else 2
            assert len(plan["lanes"]) == expected_count
            assert plan["compatibility"]["selected"] == [f"T{number}" for number in range(1, expected_count + 1)]
            assert plan["max_workers"] == cap

            snapshot = json.loads(
                (root / ".specs/features/fixture/workflow.json").read_text(encoding="utf-8")
            )
            assert snapshot["parallelization"]["automatic_baseline"] == 2
            assert snapshot["parallelization"]["automatic_ceiling"] == 4
            expected_reason = f"writer-cap:{expected_count}"
            assert blocked_task(plan, "T3")["reasons"] == [expected_reason]
            assert blocked_task(plan, "T4")["reasons"] == [expected_reason]
        finally:
            shutil.rmtree(root)


def test_explicit_cap_above_automatic_ceiling_expands_selection() -> None:
    root = make_repo(
        task("T1", "A") + task("T2", "B") + task("T3", "C") + task("T4", "D") + task("T5", "E"),
        max_workers=5,
    )
    try:
        plan = parallel_plan.plan(root=root, feature="fixture", selection_cap=5)
        assert [item["task"] for item in plan["lanes"]] == ["T1", "T2", "T3", "T4", "T5"]
        assert plan["compatibility"]["selected"] == ["T1", "T2", "T3", "T4", "T5"]
    finally:
        shutil.rmtree(root)


def test_resource_collision_blocks_only_the_conflicting_ready_writer() -> None:
    root = make_repo(task("T1", "A", resources="port") + task("T2", "B", resources="port") + task("T3", "C"))
    try:
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert plan["decision"] == "concurrent-writers"
        assert [lane["task"] for lane in plan["lanes"]] == ["T1", "T3"]
        assert blocked_task(plan, "T2")["reasons"] == ["resource-conflict:T1:T2:port"]
    finally:
        shutil.rmtree(root)


def test_dirty_integration_baseline_has_zero_writer_effect_intents() -> None:
    root = make_repo(task("T1", "A") + task("T2", "B"))
    try:
        (root / "dirty.txt").write_text("uncommitted\n", encoding="utf-8")
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert plan["decision"] == "blocked"
        assert plan["lanes"] == []
        assert plan["reasons"] == ["dirty-baseline"]
        assert all(item["reasons"] == ["dirty-baseline"] for item in plan["blocked"])
    finally:
        shutil.rmtree(root)


def test_fully_dependency_blocked_dag_selects_no_lane_and_names_blockers() -> None:
    root = make_repo(
        task("T1", "A", depends_on="T2")
        + task("T2", "B", status="in_progress")
    )
    try:
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert plan["lanes"] == []
        assert plan["compatibility"]["ready"] == []
        assert blocked_task(plan, "T1")["reasons"] == ["dependency-incomplete:T2"]
        assert blocked_task(plan, "T2")["reasons"] == ["in-progress:T2"]
    finally:
        shutil.rmtree(root)


def test_invalid_where_metadata_serializes_before_executor_effect() -> None:
    cases = ("../escape.py", "/absolute.py", "src/a.py,src/b.py", "src/../a.py")
    missing = "### T1: T1\n**Status:** pending\n**Slice:** A\n**Depends on:** None\n**Resources:** none\n"
    for where in (None, *cases):
        tasks = missing if where is None else task("T1", "A", where=where)
        root = make_repo(tasks)
        try:
            plan = parallel_plan.plan(root=root, feature="fixture")
            assert plan["fallback"] is True
            assert any("where" in reason for reason in plan["reasons"])
            assert plan["lanes"][0]["id"] == "serial"
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
        task("T1", "A", status="bogus", depends_on="T99")
        + task("T2", "B", depends_on="T3")
        + task("T3", "C", depends_on="T2")
        + task("T4", "D", where="src/d.py, src/e.py")
    )
    try:
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert plan["fallback"] is True
        assert plan["reasons"] == [
            "invalid-status:T1",
            "ambiguous-where:T4",
            "unknown-dependency:T1->T99",
            "dependency-cycle:T2->T3->T2",
        ]
    finally:
        shutil.rmtree(root)


def test_in_progress_is_blocked_and_waiting_follows_up_after_dependencies() -> None:
    root = make_repo(
        task("T1", "A", status="in_progress") + task("T2", "B"), mode="assisted"
    )
    try:
        plan = parallel_plan.plan(root=root, feature="fixture")
        assert [item["task"] for item in plan["lanes"]] == ["T2"]
        assert blocked_task(plan, "T1")["reasons"] == ["in-progress:T1"]
    finally:
        shutil.rmtree(root)

    root = make_repo(
        task("T1", "A", status="waiting", depends_on="T2") + task("T2", "B"), mode="assisted"
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
        mode="assisted",
    )
    try:
        plan = parallel_plan.plan(root=root, feature="fixture", verified_slices={"B"})
        assert plan["lanes"] == [
            {
                "id": "serial",
                "slice": "A",
                "task": "T1",
                "status": "follow_up",
                "execution": "serial-integration",
                "worktree": False,
                "sync_after": ["T2"],
                "declared_paths": ["src/t2.py"],
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
            [sys.executable, str(resolver), "--root", str(root), "--feature", "fixture",
             "--verified-slice", "A"],
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
                "parallelization": {"mode": "assisted", "max_workers": "auto", "automatic_baseline": 2, "automatic_ceiling": 4, "resource_provider": None},
                "version": 3,
            },
            {
                "feature": "fixture",
                "git_head": "head",
                "parallelization": {"mode": "assisted", "max_workers": "auto", "automatic_baseline": 2, "automatic_ceiling": 4, "resource_provider": None},
                "version": 1,
            },
            {
                "feature": "fixture",
                "git_head": "head",
                "parallelization": {"mode": "assisted", "max_workers": "auto", "automatic_baseline": 2, "automatic_ceiling": 4, "resource_provider": None},
                "version": 2,
            },
        ):
            path.write_text(json.dumps(snapshot), encoding="utf-8")
            try:
                parallel_plan.plan(root=root, feature="fixture")
            except ValueError as exc:
                expected = (
                    "workflow snapshot version is stale; rerun resolution with --refresh"
                    if snapshot["version"] in (1, 2)
                    else "invalid workflow snapshot"
                )
                assert str(exc) == expected
                if snapshot["version"] in (1, 2):
                    resolver = ROOT / ".agents/skills/workflow-config/scripts/parallel_plan.py"
                    result = subprocess.run(
                        [sys.executable, str(resolver), "--root", str(root), "--feature", "fixture"],
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    assert result.returncode == 1
                    assert result.stdout == ""
                    assert result.stderr == (
                        "parallel plan: workflow snapshot version is stale; "
                        "rerun resolution with --refresh\n"
                    )
            else:
                raise AssertionError("expected invalid workflow snapshot")
    finally:
        shutil.rmtree(root)


def test_complete_snapshot_schema_is_required_before_planning() -> None:
    root = make_repo(task("T1", "A"))
    path = root / ".specs/features/fixture/workflow.json"
    original = json.loads(path.read_text(encoding="utf-8"))
    try:
        for mutate in (
            lambda snapshot: snapshot.pop("roles"),
            lambda snapshot: snapshot["parallelization"].update(resource_provider="/outside/provider"),
        ):
            snapshot = json.loads(json.dumps(original))
            mutate(snapshot)
            path.write_text(json.dumps(snapshot), encoding="utf-8")
            try:
                parallel_plan.plan(root=root, feature="fixture")
            except ValueError as exc:
                assert str(exc) == "invalid workflow snapshot"
            else:
                raise AssertionError("incomplete snapshot must fail before planning")
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
                "version": 3,
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
        task("T1", "A", status="complete") + task("T2", "B", depends_on="T1"), mode="assisted"
    )
    try:
        resolver = ROOT / ".agents/skills/workflow-config/scripts/parallel_plan.py"
        result = subprocess.run(
            [sys.executable, str(resolver), "--root", str(root), "--feature", "fixture",
             "--verified-slice", "A"],
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
            "compatibility": {"conflicts": [], "ready": ["T2"], "selected": ["T2"]},
            "decision": "serial-integration",
            "fallback": False,
            "feature": "fixture",
            "lanes": [
                {
                    "id": "serial",
                    "slice": "B",
                    "status": "ready",
                    "execution": "serial-integration",
                    "worktree": False,
                    "sync_after": ["T1"],
                    "declared_paths": ["src/t1.py"],
                    "resources": [],
                    "task": "T2",
                }
            ],
            "mode": "assisted",
            "max_workers": "auto",
            "reasons": [],
            "source_git_head": head,
            "role_worktrees": {
                "planner": False,
                "coordinator": False,
                "implementer": False,
                "explorer": False,
                "verifier": False,
                "deep_reviewer": False,
                "qa_plan": False,
                "qa_execute": False,
            },
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
