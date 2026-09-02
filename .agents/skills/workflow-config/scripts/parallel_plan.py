#!/usr/bin/env python3
"""Project versioned slice tasks into a deterministic dispatch plan."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any

import workflow_config

sys.path.insert(
    0, str(Path(__file__).resolve().parents[2] / "workflow-spec-driven" / "scripts")
)
import validate_tasks


MODES = {"assisted", "disabled"}
STATUS_VALUES = {"pending", "in_progress", "waiting", "complete"}
TASK_HEADING = re.compile(r"^###\s+(T\d+)\s*:")
HEADING = re.compile(r"^#{1,6}\s+")
FIELD = re.compile(r"^\*\*([^*]+):\*\*\s*(.*?)\s*$")
RESOURCE_RE = re.compile(r"^[a-z][a-z0-9-]*$")


@dataclass(frozen=True)
class Task:
    id: str
    order: int
    status: str
    slice_id: str | None
    where: str | None
    declared_paths: tuple[str, ...] | None
    depends_on: tuple[str, ...]
    resources: tuple[str, ...] | None

    @property
    def complete(self) -> bool:
        return self.status == "complete"


def _snapshot(root: Path, feature: str) -> dict[str, Any]:
    path = root / ".specs" / "features" / feature / "workflow.json"
    try:
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        try:
            validated = workflow_config.validate_snapshot(root, feature, snapshot)
        except workflow_config.ConfigError as exc:
            message = str(exc)
            if "stale; rerun resolution" in message:
                raise ValueError(message.removeprefix("workflow-config: ")) from exc
            raise ValueError("invalid workflow snapshot") from exc
    except (OSError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid workflow snapshot") from exc
    parallelization = validated["parallelization"]
    mode = parallelization["mode"]
    max_workers = parallelization["max_workers"]
    source_git_head = validated["git_head"]
    return {
        "mode": mode,
        "max_workers": max_workers,
        "automatic_baseline": 2,
        "automatic_ceiling": 4,
        "resource_provider": parallelization["resource_provider"],
        "source_git_head": source_git_head,
    }


def _dependencies(value: str | None) -> tuple[str, ...]:
    if not value or value.strip().lower() == "none":
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _ambiguous_where(value: str | None) -> bool:
    if not value:
        return True
    return "," in value or ";" in value or " and " in value.lower()


def _declared_paths(value: str | None) -> tuple[tuple[str, ...] | None, str | None]:
    if _ambiguous_where(value):
        return None, "ambiguous-where"
    if value is None or not value.strip():
        return None, "missing-where"
    candidate = value.strip()
    if "\\" in candidate or PurePosixPath(candidate).is_absolute() or ".." in PurePosixPath(candidate).parts:
        return None, "invalid-where"
    if candidate in {".", ""} or any(not part for part in PurePosixPath(candidate).parts):
        return None, "invalid-where"
    return (candidate,), None


def _resources(value: str | None) -> tuple[tuple[str, ...] | None, str | None]:
    if value is None:
        return None, "missing-resources"
    if not value.strip():
        return None, "invalid-resources"
    parts = [part.strip().lower() for part in value.split(",")]
    if any(not part for part in parts):
        return None, "invalid-resources"
    if "none" in parts:
        if len(parts) == 1:
            return (), None
        return None, "mixed-none-resources"
    for part in parts:
        if not RESOURCE_RE.fullmatch(part):
            return None, "invalid-resources"
    if len(set(parts)) != len(parts):
        duplicate = next(part for part in parts if parts.count(part) > 1)
        return None, f"duplicate-resources:{duplicate}"
    return tuple(sorted(parts)), None


def _parse_tasks(path: Path) -> tuple[list[Task], list[str]]:
    # Slice membership comes from the validated closure contract, never from this
    # parser, so the planner and the validator cannot disagree about a task's slice.
    task_slices = validate_tasks.validated_slice_contract(str(path))["task_slices"]
    lines = path.read_text(encoding="utf-8").splitlines()
    sections: list[tuple[str, list[str]]] = []
    current_id: str | None = None
    current: list[str] = []
    for line in lines:
        match = TASK_HEADING.match(line)
        if match:
            if current_id is not None:
                sections.append((current_id, current))
            current_id = match.group(1)
            current = []
        elif HEADING.match(line):
            # Any other heading ends the task, so a `T2R1` remediation record donates
            # no Status, Resources, or Depends on to the primary task above it.
            if current_id is not None:
                sections.append((current_id, current))
            current_id = None
            current = []
        elif current_id is not None:
            current.append(line)
    if current_id is not None:
        sections.append((current_id, current))

    tasks: list[Task] = []
    reasons: list[str] = []
    seen: set[str] = set()
    for order, (task_id, section) in enumerate(sections):
        if task_id in seen:
            reasons.append(f"duplicate-task:{task_id}")
            continue
        seen.add(task_id)
        fields: dict[str, str] = {}
        for line in section:
            match = FIELD.match(line.strip())
            if match:
                fields[match.group(1).strip().lower()] = match.group(2).strip()
        status = fields.get("status", "")
        slice_id = task_slices.get(task_id)
        where = fields.get("where") or None
        declared_paths, where_reason = _declared_paths(where)
        if status not in STATUS_VALUES:
            reasons.append(f"invalid-status:{task_id}")
        if where_reason:
            reasons.append(f"{where_reason}:{task_id}")
        resources, resource_reason = _resources(fields.get("resources"))
        if resource_reason:
            if resource_reason.startswith("duplicate-resources:"):
                resource_reason = f"duplicate-resources:{task_id}:{resource_reason.split(':', 1)[1]}"
            else:
                resource_reason = f"{resource_reason}:{task_id}"
            reasons.append(resource_reason)
        tasks.append(
            Task(
                id=task_id,
                order=order,
                status=status,
                slice_id=slice_id,
                where=where,
                declared_paths=declared_paths,
                depends_on=_dependencies(fields.get("depends on")),
                resources=resources,
            )
        )
    if not tasks:
        reasons.append("missing-tasks")
    return tasks, reasons


def _cycle_reasons(tasks: list[Task], by_id: dict[str, Task]) -> list[str]:
    reasons: list[str] = []
    visiting: list[str] = []
    active: set[str] = set()
    done: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in done:
            return
        if task_id in active:
            start = visiting.index(task_id)
            cycle = visiting[start:] + [task_id]
            reasons.append("dependency-cycle:" + "->".join(cycle))
            return
        active.add(task_id)
        visiting.append(task_id)
        for dependency in by_id[task_id].depends_on:
            if dependency in by_id:
                visit(dependency)
        visiting.pop()
        active.remove(task_id)
        done.add(task_id)

    for task in tasks:
        visit(task.id)
    return list(dict.fromkeys(reasons))


def _write_conflicts(candidates: list[Task]) -> list[str]:
    reasons: list[str] = []
    for index, left in enumerate(candidates):
        for right in candidates[index + 1 :]:
            for left_path in left.declared_paths or ():
                for right_path in right.declared_paths or ():
                    left_parts = PurePosixPath(left_path).parts
                    right_parts = PurePosixPath(right_path).parts
                    if left_parts[: len(right_parts)] == right_parts or right_parts[: len(left_parts)] == left_parts:
                        reasons.append(f"write-conflict:{left.id}:{right.id}:{left_path}:{right_path}")
    return reasons


def _resource_conflicts(candidates: list[Task]) -> list[str]:
    reasons: list[str] = []
    for index, left in enumerate(candidates):
        for right in candidates[index + 1 :]:
            for resource in sorted(set(left.resources or ()) & set(right.resources or ())):
                reasons.append(f"resource-conflict:{left.id}:{right.id}:{resource}")
    return reasons


def _serial_lane(task: Task | None) -> list[dict[str, Any]]:
    if task is None or task.status in {"in_progress", "waiting"}:
        return []
    return [
        {
            "id": "serial",
            "slice": task.slice_id,
            "task": task.id,
            "status": "ready",
            "execution": "serial-integration",
            "worktree": False,
            "sync_after": [],
            "declared_paths": list(task.declared_paths or []),
            "resources": list(task.resources or []),
        }
    ]


def _base_plan(
    feature: str,
    mode: str,
    source_git_head: str,
    *,
    max_workers: str | int,
) -> dict[str, Any]:
    return {
        "version": 1,
        "feature": feature,
        "mode": mode,
        "max_workers": max_workers,
        "source_git_head": source_git_head,
        "fallback": False,
        "decision": "blocked",
        "lanes": [],
        "blocked": [],
        "reasons": [],
        "compatibility": {"ready": [], "selected": [], "conflicts": []},
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
    }


def plan(
    *, root: Path,
    feature: str,
    verified_slices: set[str] | None = None,
    completed_tasks: set[str] | None = None,
    selection_cap: int | None = None,
) -> dict[str, Any]:
    """Return a read-only point-in-time plan for one feature."""
    root = root.resolve()
    snapshot = _snapshot(root, feature)
    mode = snapshot["mode"]
    plan_output = _base_plan(
        feature, mode, snapshot["source_git_head"], max_workers=snapshot["max_workers"]
    )
    tasks_path = root / ".specs" / "features" / feature / "tasks.md"
    try:
        tasks, reasons = _parse_tasks(tasks_path)
    except OSError as exc:
        raise ValueError("tasks file is missing or unreadable") from exc
    try:
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=root,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("repository status is unavailable") from exc
    snapshot_relative = f".specs/features/{feature}/workflow.json"
    fixture_metadata = {".parallel-slice-qa-fixture", ".parallel-slice-qa-ownership.json"}
    dirty = [line for line in dirty if line[3:] not in {snapshot_relative, *fixture_metadata}]
    if dirty:
        plan_output["reasons"] = ["dirty-baseline"]
        plan_output["blocked"] = [
            {"task": task.id, "slice": task.slice_id, "reasons": ["dirty-baseline"]}
            for task in tasks
            if not task.complete
        ]
        return plan_output
    by_id = {task.id: task for task in tasks}
    for task in tasks:
        for dependency in task.depends_on:
            if dependency not in by_id:
                reasons.append(f"unknown-dependency:{task.id}->{dependency}")
    reasons.extend(_cycle_reasons(tasks, by_id))

    candidates: list[Task] = []
    blocked: dict[str, list[str]] = {}
    seen_slices: set[str | None] = set()
    completed = completed_tasks or set()
    for task in tasks:
        if task.complete or task.id in completed:
            continue
        if task.slice_id not in seen_slices:
            candidates.append(task)
            seen_slices.add(task.slice_id)
        else:
            first = next(item for item in candidates if item.slice_id == task.slice_id)
            blocked[task.id] = [f"slice-order:{first.id}"]

    reasons = list(dict.fromkeys(reasons))
    if reasons:
        plan_output["fallback"] = True
        plan_output["reasons"] = reasons
        plan_output["decision"] = "serial-integration"
        plan_output["lanes"] = _serial_lane(candidates[0] if candidates else None)
        plan_output["blocked"] = [
            {
                "task": task.id,
                "slice": task.slice_id,
                "reasons": blocked.get(task.id, ["serial-fallback"]),
            }
            for task in tasks
            if task.id in blocked
        ]
        return plan_output

    verified = verified_slices or set()
    if mode == "disabled" and len(candidates) > 1:
        for task in candidates[1:]:
            blocked[task.id] = ["disabled-mode"]
        candidates = candidates[:1]
    ready: list[dict[str, Any]] = []
    ready_tasks: list[Task] = []
    for task in candidates:
        if task.status == "in_progress":
            blocked[task.id] = [f"in-progress:{task.id}"]
            continue
        task_reasons = list(blocked.get(task.id, []))
        sync_after: list[str] = []
        for dependency_id in task.depends_on:
            dependency = by_id[dependency_id]
            if not dependency.complete:
                reason = "waiting-on-dependency" if task.status == "waiting" else "dependency-incomplete"
                task_reasons.append(f"{reason}:{dependency_id}")
            elif dependency.slice_id != task.slice_id:
                if dependency.slice_id not in verified:
                    task_reasons.append(f"awaiting-verified-slice:{dependency.slice_id}")
                else:
                    sync_after.append(dependency.id)
        if task_reasons:
            blocked[task.id] = list(dict.fromkeys(task_reasons))
            continue
        ready_tasks.append(task)
        producer_paths = sorted(
            {
                path
                for dependency_id in sync_after
                for path in (by_id[dependency_id].declared_paths or ())
            }
        )
        ready.append(
            {
                "id": "serial" if mode == "disabled" else f"slice-{task.slice_id}",
                "slice": task.slice_id,
                "task": task.id,
                "status": "follow_up" if task.status == "waiting" else "ready",
                "execution": "serial-integration" if mode == "disabled" else "concurrent-writer",
                "worktree": mode != "disabled",
                "sync_after": sync_after,
                "declared_paths": producer_paths if sync_after else list(task.declared_paths or []),
                "resources": list(task.resources or []),
            }
        )

    plan_output["compatibility"]["ready"] = [task.id for task in ready_tasks]
    selected: list[dict[str, Any]] = []
    selected_tasks: list[Task] = []
    conflict_reasons: list[str] = []
    if mode == "disabled":
        selected = ready[:1]
        selected_tasks = ready_tasks[:1]
        for lane in ready[1:]:
            blocked[lane["task"]] = ["disabled-mode"]
    else:
        configured_cap = snapshot["max_workers"]
        initial_cap = snapshot["automatic_baseline"] if configured_cap == "auto" else min(
            snapshot["automatic_baseline"], configured_cap
        )
        if selection_cap is not None:
            if type(selection_cap) is not int or selection_cap < 1:
                raise ValueError("invalid selection cap")
            configured_limit = snapshot["automatic_ceiling"] if configured_cap == "auto" else configured_cap
            initial_cap = min(configured_limit, selection_cap)
        for lane, task in zip(ready, ready_tasks):
            if len(selected) >= initial_cap:
                blocked[task.id] = [f"writer-cap:{initial_cap}"]
                continue
            candidate = selected_tasks + [task]
            conflicts = _write_conflicts(candidate) + _resource_conflicts(candidate)
            task_conflicts = [
                reason for reason in conflicts
                if reason.split(":")[1] == task.id or reason.split(":")[2] == task.id
            ]
            if task_conflicts:
                blockers = list(dict.fromkeys(task_conflicts))
                blocked[task.id] = blockers
                conflict_reasons.extend(blockers)
                continue
            selected.append(lane)
            selected_tasks.append(task)

    plan_output["compatibility"]["selected"] = [task.id for task in selected_tasks]
    plan_output["compatibility"]["conflicts"] = list(dict.fromkeys(conflict_reasons))
    plan_output["reasons"] = list(dict.fromkeys(conflict_reasons))
    if len(selected) == 1:
        plan_output["decision"] = "serial-integration"
        selected[0]["id"] = "serial"
        selected[0]["execution"] = "serial-integration"
        selected[0]["worktree"] = False
    elif len(selected) > 1:
        plan_output["decision"] = "concurrent-writers"
        plan_output["role_worktrees"]["implementer"] = True
    plan_output["lanes"] = selected
    plan_output["blocked"] = [
        {
            "task": task.id,
            "slice": task.slice_id,
            "reasons": blocked[task.id],
        }
        for task in tasks
        if task.id in blocked
    ]
    return plan_output


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--feature", required=True)
    parser.add_argument("--verified-slice", action="append", default=[])
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        output = plan(
            root=args.root,
            feature=args.feature,
            verified_slices=set(args.verified_slice),
        )
    except (OSError, ValueError) as exc:
        print(f"parallel plan: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
