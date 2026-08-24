#!/usr/bin/env python3
"""Project versioned slice tasks into a deterministic dispatch plan."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MODES = {"disabled", "safe", "full"}
STATUS_VALUES = {"pending", "in_progress", "waiting", "complete"}
TASK_HEADING = re.compile(r"^###\s+(T\d+)\s*:")
FIELD = re.compile(r"^\*\*([^*]+):\*\*\s*(.*?)\s*$")


@dataclass(frozen=True)
class Task:
    id: str
    order: int
    status: str
    slice_id: str | None
    where: str | None
    depends_on: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return self.status == "complete"


def _snapshot(root: Path, feature: str) -> dict[str, Any]:
    path = root / ".specs" / "features" / feature / "workflow.json"
    try:
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        if (
            not isinstance(snapshot, dict)
            or type(snapshot.get("version")) is not int
            or snapshot["version"] != 1
            or snapshot.get("feature") != feature
        ):
            raise ValueError("invalid workflow snapshot")
        mode = snapshot["parallelization"]["mode"]
        source_git_head = snapshot["git_head"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid workflow snapshot") from exc
    if not isinstance(mode, str) or mode not in MODES:
        raise ValueError("invalid workflow snapshot")
    if not isinstance(source_git_head, str) or not source_git_head:
        raise ValueError("invalid workflow snapshot")
    return {"mode": mode, "source_git_head": source_git_head}


def _dependencies(value: str | None) -> tuple[str, ...]:
    if not value or value.strip().lower() == "none":
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _ambiguous_where(value: str | None) -> bool:
    if not value:
        return True
    return "," in value or ";" in value or " and " in value.lower()


def _parse_tasks(path: Path) -> tuple[list[Task], list[str]]:
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
        slice_id = fields.get("slice") or None
        where = fields.get("where") or None
        if status not in STATUS_VALUES:
            reasons.append(f"invalid-status:{task_id}")
        if slice_id is None:
            reasons.append(f"missing-slice:{task_id}")
        if _ambiguous_where(where):
            reasons.append(f"ambiguous-where:{task_id}")
        tasks.append(
            Task(
                id=task_id,
                order=order,
                status=status,
                slice_id=slice_id,
                where=where,
                depends_on=_dependencies(fields.get("depends on")),
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
            if left.where == right.where:
                reasons.append(f"write-conflict:{left.id}:{right.id}:{left.where}")
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
            "sync_after": [],
        }
    ]


def _base_plan(feature: str, mode: str, source_git_head: str) -> dict[str, Any]:
    return {
        "version": 1,
        "feature": feature,
        "mode": mode,
        "source_git_head": source_git_head,
        "fallback": False,
        "lanes": [],
        "blocked": [],
        "reasons": [],
    }


def plan(
    *, root: Path,
    feature: str,
    verified_slices: set[str] | None = None,
) -> dict[str, Any]:
    """Return a read-only point-in-time plan for one feature."""
    root = root.resolve()
    snapshot = _snapshot(root, feature)
    mode = snapshot["mode"]
    plan_output = _base_plan(feature, mode, snapshot["source_git_head"])
    tasks_path = root / ".specs" / "features" / feature / "tasks.md"
    try:
        tasks, reasons = _parse_tasks(tasks_path)
    except OSError as exc:
        raise ValueError("tasks file is missing or unreadable") from exc

    by_id = {task.id: task for task in tasks}
    for task in tasks:
        for dependency in task.depends_on:
            if dependency not in by_id:
                reasons.append(f"unknown-dependency:{task.id}->{dependency}")
    reasons.extend(_cycle_reasons(tasks, by_id))

    candidates: list[Task] = []
    blocked: dict[str, list[str]] = {}
    seen_slices: set[str | None] = set()
    for task in tasks:
        if task.complete:
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
                if mode == "safe" and dependency.slice_id not in verified:
                    task_reasons.append(f"awaiting-verified-slice:{dependency.slice_id}")
                elif mode == "full":
                    sync_after.append(dependency.id)
        if task_reasons:
            blocked[task.id] = list(dict.fromkeys(task_reasons))
            continue
        ready_tasks.append(task)
        ready.append(
            {
                "id": "serial" if mode == "disabled" else f"slice-{task.slice_id}",
                "slice": task.slice_id,
                "task": task.id,
                "status": "follow_up" if task.status == "waiting" else "ready",
                "sync_after": sync_after,
            }
        )

    conflict_reasons = _write_conflicts(ready_tasks)
    if conflict_reasons:
        for lane in ready[1:]:
            blocked[lane["task"]] = ["serial-fallback"]
        plan_output["fallback"] = True
        plan_output["reasons"] = conflict_reasons
        if ready:
            serial_lane = dict(ready[0])
            serial_lane["id"] = "serial"
            plan_output["lanes"] = [serial_lane]
        else:
            plan_output["lanes"] = []
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

    plan_output["lanes"] = ready
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
