#!/usr/bin/env python3
"""Deterministic, restart-safe coordinator for inter-slice execution.

The module deliberately keeps external effects behind small adapter/provider protocols.  Runtime
state is local machine state under Git's common directory; feature specifications remain versioned
truth and never receive host-specific receipts.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


MODES = {"disabled", "safe", "full"}
LANE_STATES = {"ready", "needs_resources", "running", "waiting", "needs_sync", "complete", "failed", "serial"}
TRANSITIONS: dict[str, set[str]] = {
    "ready": {"needs_resources", "running", "serial", "failed"},
    "needs_resources": {"running", "serial", "failed"},
    "running": {"waiting", "needs_sync", "complete", "failed", "serial"},
    "waiting": {"needs_sync", "running", "failed", "serial"},
    "needs_sync": {"running", "serial", "failed"},
    "complete": set(),
    "failed": set(),
    "serial": set(),
}
_ID = re.compile(r"^[A-Za-z0-9_.:/-]+$")


class ExecutorError(ValueError):
    """Expected, fail-closed executor input or adapter failure."""


class StateError(ExecutorError):
    """Runtime state is malformed, foreign, or violates its transition graph."""


class PathBoundaryError(ExecutorError):
    """A path leaves its declared root or crosses an unsafe symlink."""


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise StateError(f"invalid {label}")
    return value


def new_runtime_state(repository_id: str, feature: str, mode: str, source_git_head: str) -> dict[str, Any]:
    if mode not in MODES:
        raise StateError("invalid mode")
    return {
        "version": 1,
        "repository_id": _require_text(repository_id, "repository identity"),
        "feature": _require_text(feature, "feature"),
        "mode": mode,
        "source_git_head": _require_text(source_git_head, "source git head"),
        "lanes": {},
        "actions": {},
    }


def validate_runtime_state(
    state: Mapping[str, Any], repository_id: str | None = None, feature: str | None = None
) -> None:
    if not isinstance(state, Mapping):
        raise StateError("runtime state must be an object")
    if state.get("version") != 1:
        raise StateError("invalid runtime state version")
    actual_repository = _require_text(state.get("repository_id"), "repository identity")
    actual_feature = _require_text(state.get("feature"), "feature")
    if repository_id is not None and actual_repository != repository_id:
        raise StateError("foreign repository state")
    if feature is not None and actual_feature != feature:
        raise StateError("foreign feature state")
    if state.get("mode") not in MODES:
        raise StateError("invalid runtime state mode")
    _require_text(state.get("source_git_head"), "source git head")
    lanes = state.get("lanes")
    actions = state.get("actions")
    if not isinstance(lanes, Mapping) or not isinstance(actions, Mapping):
        raise StateError("runtime state lanes and actions must be objects")

    seen_slices: set[str] = set()
    seen_external: set[str] = set()
    for lane_id, lane in lanes.items():
        if not isinstance(lane_id, str) or not _ID.fullmatch(lane_id) or not isinstance(lane, Mapping):
            raise StateError("invalid lane receipt")
        slice_id = _require_text(lane.get("slice"), "lane slice")
        task_id = _require_text(lane.get("task"), "lane task")
        state_name = lane.get("state")
        if state_name not in LANE_STATES:
            raise StateError(f"invalid lane state: {lane_id}")
        if slice_id in seen_slices:
            raise StateError(f"duplicate lane slice: {slice_id}")
        seen_slices.add(slice_id)
        for field in ("worktree_id", "branch", "run_id", "dispatch_id", "terminal_handle"):
            value = lane.get(field)
            if value is not None:
                value = _require_text(value, field)
                if field != "branch" and value in seen_external:
                    raise StateError(f"duplicate external receipt: {field}")
                if field != "branch":
                    seen_external.add(value)
        resources = lane.get("resources", [])
        if not isinstance(resources, list) or any(not isinstance(item, str) or not item for item in resources):
            raise StateError(f"invalid resources: {lane_id}")
        if len(set(resources)) != len(resources):
            raise StateError(f"duplicate resources: {lane_id}")
    for key, action in actions.items():
        if not isinstance(key, str) or not _ID.fullmatch(key) or not isinstance(action, Mapping):
            raise StateError("invalid action receipt")
        if action.get("key") != key or action.get("action") not in {
            "worktree", "worker", "follow_up", "acquire", "release"
        }:
            raise StateError("invalid action receipt")
        if action.get("status") not in {"pending", "accepted", "released", "failed"}:
            raise StateError("invalid action status")
        _require_text(action.get("lane"), "action lane")
        if action["lane"] not in lanes:
            raise StateError("action references unknown lane")


def transition_lane(
    state: dict[str, Any], lane_id: str, new_state: str, *, expected: str | None = None
) -> None:
    validate_runtime_state(state)
    lane = state["lanes"].get(lane_id)
    if not isinstance(lane, dict):
        raise StateError(f"unknown lane: {lane_id}")
    current = lane["state"]
    if expected is not None and current != expected:
        raise StateError(f"out-of-order transition: expected {expected}, got {current}")
    if new_state not in TRANSITIONS.get(current, set()):
        raise StateError(f"illegal transition: {current}->{new_state}")
    lane["state"] = new_state


def _reject_symlink_components(root: Path, candidate: Path) -> None:
    current = root
    relative = candidate.relative_to(root)
    for component in relative.parts:
        current = current / component
        if current.is_symlink():
            raise PathBoundaryError("unsafe symlink path")


def bounded_path(root: Path, candidate: Path | str, *, must_exist: bool = False) -> Path:
    root = Path(root).absolute().resolve()
    raw = Path(candidate)
    if any(part == ".." for part in raw.parts):
        raise PathBoundaryError("parent traversal is not allowed")
    target = raw if raw.is_absolute() else root / raw
    target = target.absolute()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise PathBoundaryError("path leaves declared root") from exc
    _reject_symlink_components(root, target)
    resolved = target.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise PathBoundaryError("resolved path leaves declared root") from exc
    if must_exist and not target.exists():
        raise PathBoundaryError("path does not exist")
    return resolved


def run_argv(
    argv: Sequence[str],
    *,
    cwd: Path | str | None = None,
    timeout: float = 30,
    check: bool = True,
    input: str | None = None,
) -> subprocess.CompletedProcess[str]:
    if not argv or any(not isinstance(item, str) for item in argv):
        raise ExecutorError("argv must contain strings")
    if timeout <= 0:
        raise ExecutorError("timeout must be positive")
    return subprocess.run(
        list(argv),
        cwd=str(cwd) if cwd is not None else None,
        input=input,
        capture_output=True,
        text=True,
        shell=False,
        timeout=timeout,
        check=check,
    )


def atomic_write_json(
    path: Path,
    value: Mapping[str, Any],
    *,
    before_replace: Callable[[], None] | None = None,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if before_replace is not None:
            before_replace()
        os.replace(temporary_path, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass


def _repository_root(root: Path) -> Path:
    return Path(run_argv(["git", "rev-parse", "--show-toplevel"], cwd=root).stdout.strip()).resolve()


def _git_common_dir(root: Path) -> Path:
    value = run_argv(["git", "rev-parse", "--git-common-dir"], cwd=root).stdout.strip()
    path = Path(value)
    return (root / path if not path.is_absolute() else path).resolve()


def runtime_state_path(root: Path, feature: str) -> Path:
    root = _repository_root(Path(root).resolve())
    if not _ID.fullmatch(feature):
        raise ExecutorError("invalid feature")
    common = _git_common_dir(root)
    if common.is_symlink():
        raise PathBoundaryError("unsafe git common directory")
    storage = common / "parallel-slice-executor"
    if storage.exists() and storage.is_symlink():
        raise PathBoundaryError("unsafe runtime state directory")
    repository_key = hashlib.sha256(str(root).encode("utf-8")).hexdigest()[:16]
    return storage / f"{repository_key}-{feature}.json"


def idempotency_key(feature: str, slice_id: str, task: str, action: str, source_checkpoint: str) -> str:
    material = "\0".join((feature, slice_id, task, action, source_checkpoint)).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def _serial_result(feature: str, mode: str, reason: str, lanes: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "version": 1,
        "feature": feature,
        "mode": mode,
        "fallback": True,
        "reason": reason,
        "lanes": lanes or [],
        "actions": [],
    }


class ResourceProvider:
    """Validate the consumer executable's correlated JSON lease protocol."""

    def __init__(self, root: Path, executable: Path, *, timeout: float = 30, runner: Callable[..., Any] = run_argv):
        self.root = Path(root).resolve()
        self.executable = bounded_path(self.root, executable, must_exist=True)
        if not self.executable.is_file() or not os.access(self.executable, os.X_OK):
            raise ExecutorError("resource provider is not executable")
        self.timeout = timeout
        self.runner = runner

    def _call(self, request: Mapping[str, Any]) -> dict[str, Any]:
        try:
            completed = self.runner(
                [str(self.executable)], cwd=self.root, timeout=self.timeout, input=json.dumps(request), check=True
            )
        except (OSError, subprocess.SubprocessError, ExecutorError) as exc:
            raise ExecutorError("resource provider failed") from exc
        try:
            payload = json.loads(completed.stdout)
        except (AttributeError, TypeError, json.JSONDecodeError) as exc:
            raise ExecutorError("resource provider returned malformed data") from exc
        if not isinstance(payload, dict):
            raise ExecutorError("resource provider returned malformed data")
        return payload

    def acquire(self, request: Mapping[str, Any], live_lease_ids: set[str]) -> dict[str, Any]:
        payload = self._call({**request, "operation": "acquire"})
        lease_id = payload.get("lease_id")
        if (
            not isinstance(lease_id, str)
            or not lease_id
            or lease_id in live_lease_ids
            or payload.get("resources") != request.get("resources")
            or payload.get("prepared_worktree") is not True
            or not isinstance(payload.get("environment"), dict)
            or payload.get("idempotency_key") != request.get("idempotency_key")
        ):
            raise ExecutorError("resource receipt is uncorrelated or already live")
        return {
            "lease_id": lease_id,
            "resources": list(request["resources"]),
            "prepared_worktree": True,
            "environment_keys": sorted(payload["environment"]),
            "environment": {key: "<redacted>" for key in sorted(payload["environment"])},
            "released": False,
        }

    def release(self, request: Mapping[str, Any], lease_id: str) -> dict[str, Any]:
        payload = self._call({**request, "operation": "release", "lease_id": lease_id})
        if payload.get("lease_id") != lease_id or payload.get("released") is not True:
            raise ExecutorError("resource release receipt is uncorrelated")
        return {"lease_id": lease_id, "released": True}


class Coordinator:
    """Reconcile a frozen plan and local receipts into deterministic adapter effects."""

    def __init__(
        self,
        root: Path,
        feature: str,
        *,
        adapter_factory: Callable[[], Any] | None = None,
        provider_factory: Callable[[Path], ResourceProvider] | None = None,
    ):
        self.root = _repository_root(Path(root).resolve())
        self.feature = feature
        self.adapter_factory = adapter_factory
        self.provider_factory = provider_factory
        self.state_path = runtime_state_path(self.root, feature)

    def _workflow(self) -> dict[str, Any]:
        path = self.root / ".specs" / "features" / self.feature / "workflow.json"
        try:
            snapshot = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(snapshot, dict) or snapshot.get("version") != 1 or snapshot.get("feature") != self.feature:
                raise ValueError
            mode = snapshot["parallelization"]["mode"]
            head = snapshot["git_head"]
            if mode not in MODES or not isinstance(head, str) or not head:
                raise ValueError
            return snapshot
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ExecutorError("invalid workflow snapshot") from exc

    def _plan(self) -> dict[str, Any]:
        scripts = Path(__file__).resolve().parents[2] / "workflow-config" / "scripts"
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        import parallel_plan

        try:
            return parallel_plan.plan(root=self.root, feature=self.feature)
        except ValueError as exc:
            raise ExecutorError(str(exc)) from exc

    def _load_state(self, workflow: Mapping[str, Any]) -> dict[str, Any] | None:
        try:
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
            validate_runtime_state(state, str(self.root), self.feature)
            return state
        except FileNotFoundError:
            return None
        except (OSError, json.JSONDecodeError, StateError) as exc:
            raise StateError(str(exc)) from exc

    def _save(self, state: dict[str, Any]) -> None:
        validate_runtime_state(state, str(self.root), self.feature)
        atomic_write_json(self.state_path, state)

    def transition(self, state: dict[str, Any], event: Mapping[str, Any]) -> list[dict[str, Any]]:
        lane_id = event.get("lane")
        new_state = event.get("state")
        if not isinstance(lane_id, str) or not isinstance(new_state, str):
            raise StateError("transition event is malformed")
        transition_lane(state, lane_id, new_state, expected=event.get("expected"))
        return list(event.get("actions", [])) if isinstance(event.get("actions", []), list) else []

    def status(self) -> dict[str, Any]:
        workflow = self._workflow()
        try:
            state = self._load_state(workflow)
        except StateError as exc:
            return _serial_result(self.feature, workflow["parallelization"]["mode"], f"state:{exc}")
        if state is None:
            return {"version": 1, "feature": self.feature, "mode": workflow["parallelization"]["mode"], "state": None, "actions": []}
        return {"version": 1, "feature": self.feature, "mode": state["mode"], "state": state, "actions": []}

    def _lane_resources(self, lane: Mapping[str, Any]) -> list[str] | None:
        resources = lane.get("resources")
        if resources is None:
            return None
        if not isinstance(resources, list) or any(not isinstance(item, str) or not item for item in resources):
            return None
        if len(set(resources)) != len(resources):
            return None
        return list(resources)

    def _provider(self, snapshot: Mapping[str, Any]) -> ResourceProvider | None:
        configured = snapshot.get("parallelization", {}).get("resource_provider")
        if not configured:
            return None
        if not isinstance(configured, str) or Path(configured).is_absolute():
            raise PathBoundaryError("invalid resource provider path")
        executable = bounded_path(self.root, configured, must_exist=True)
        if self.provider_factory is not None:
            return self.provider_factory(executable)
        return ResourceProvider(self.root, executable)

    def _record_action(self, state: dict[str, Any], lane_id: str, lane: Mapping[str, Any], action: str) -> tuple[str, dict[str, Any]]:
        key = idempotency_key(self.feature, str(lane["slice"]), str(lane["task"]), action, state["source_git_head"])
        receipt = state["actions"].get(key)
        if receipt is None:
            receipt = {"key": key, "action": action, "status": "pending", "lane": lane_id}
            state["actions"][key] = receipt
        elif receipt.get("status") == "pending":
            raise ExecutorError(f"unreconciled pending action: {action}")
        return key, receipt

    def _accept(self, receipt: dict[str, Any], **fields: Any) -> None:
        receipt.update(fields)
        receipt["status"] = "accepted"

    def start(self, *, resume: bool = False) -> dict[str, Any]:
        snapshot = self._workflow()
        mode = snapshot["parallelization"]["mode"]
        plan = self._plan()
        lanes = list(plan.get("lanes", []))
        if mode == "disabled":
            return _serial_result(self.feature, mode, "disabled-mode", lanes)
        if plan.get("fallback"):
            return _serial_result(self.feature, mode, "plan-fallback", lanes)
        try:
            state = self._load_state(snapshot)
        except StateError as exc:
            return _serial_result(self.feature, mode, f"state:{exc}", lanes)
        if state is None:
            state = new_runtime_state(str(self.root), self.feature, mode, snapshot["git_head"])
        if state["source_git_head"] != snapshot["git_head"]:
            return _serial_result(self.feature, mode, "source-head-changed", lanes)
        if self.adapter_factory is None:
            return _serial_result(self.feature, mode, "unsupported-adapter", lanes)
        adapter = self.adapter_factory()
        provider: ResourceProvider | None = None
        actions: list[dict[str, Any]] = []
        for plan_lane in lanes:
            lane_id = str(plan_lane.get("id", ""))
            slice_id = plan_lane.get("slice")
            task_id = plan_lane.get("task")
            if not _ID.fullmatch(lane_id) or not isinstance(slice_id, str) or not isinstance(task_id, str):
                return _serial_result(self.feature, mode, "invalid-plan-lane", lanes)
            resources = self._lane_resources(plan_lane)
            if resources is None:
                return _serial_result(self.feature, mode, "missing-resource-metadata", lanes)
            existing = state["lanes"].get(lane_id)
            if existing is None:
                state["lanes"][lane_id] = {"slice": slice_id, "task": task_id, "state": "ready", "resources": resources}
                existing = state["lanes"][lane_id]
            elif existing.get("slice") != slice_id or existing.get("task") != task_id:
                return _serial_result(self.feature, mode, "mismatched-lane-receipt", lanes)
            if existing["state"] in {"complete", "failed", "serial"}:
                continue
            worktree_key, worktree_action = self._record_action(state, lane_id, existing, "worktree")
            self._save(state)
            if worktree_action["status"] == "pending":
                try:
                    receipt = adapter.create_worktree(dict(plan_lane), idempotency_key=worktree_key)
                    if not isinstance(receipt, Mapping):
                        raise ExecutorError("malformed worktree receipt")
                    self._accept(worktree_action, external_id=receipt.get("worktree_id"), receipt=dict(receipt))
                    existing.update({key: receipt[key] for key in ("worktree_id", "worktree_path", "branch", "pre_head") if key in receipt})
                    transition_lane(state, lane_id, "running", expected="ready")
                except Exception as exc:
                    existing["fallback_reason"] = "worktree:" + str(exc)
                    transition_lane(state, lane_id, "serial", expected="ready")
                    self._save(state)
                    return _serial_result(self.feature, mode, "worktree-failed", lanes)
            if resources:
                if provider is None:
                    try:
                        provider = self._provider(snapshot)
                    except (ExecutorError, PathBoundaryError):
                        existing["fallback_reason"] = "missing-resource-provider"
                        transition_lane(state, lane_id, "serial")
                        self._save(state)
                        return _serial_result(self.feature, mode, "missing-resource-provider", lanes)
                acquire_key, acquire_action = self._record_action(state, lane_id, existing, "acquire")
                self._save(state)
                if acquire_action["status"] == "pending":
                    request = {
                        "repository": str(self.root),
                        "feature": self.feature,
                        "slice": slice_id,
                        "task": task_id,
                        "worktree": existing.get("worktree_path", ""),
                        "idempotency_key": acquire_key,
                        "resources": resources,
                    }
                    try:
                        live = {lane.get("lease", {}).get("lease_id") for lane in state["lanes"].values() if isinstance(lane.get("lease"), Mapping)}
                        lease = provider.acquire(request, {item for item in live if isinstance(item, str)})
                        existing["lease"] = lease
                        self._accept(acquire_action, external_id=lease["lease_id"], receipt=lease)
                    except ExecutorError as exc:
                        existing["fallback_reason"] = str(exc)
                        transition_lane(state, lane_id, "serial")
                        self._save(state)
                        return _serial_result(self.feature, mode, "resource-acquire-failed", lanes)
            worker_key, worker_action = self._record_action(state, lane_id, existing, "worker")
            self._save(state)
            if worker_action["status"] == "pending":
                try:
                    receipt = adapter.start_worker(dict(plan_lane), dict(existing), idempotency_key=worker_key)
                    if not isinstance(receipt, Mapping):
                        raise ExecutorError("malformed worker receipt")
                    self._accept(worker_action, external_id=receipt.get("dispatch_id"), receipt=dict(receipt))
                    for key in ("run_id", "orchestration_task_id", "dispatch_id", "terminal_handle"):
                        if key in receipt:
                            existing[key] = receipt[key]
                    actions.append({"action": "worker", "lane": lane_id, "key": worker_key})
                except Exception as exc:
                    existing["fallback_reason"] = "worker:" + str(exc)
                    transition_lane(state, lane_id, "serial")
                    self._save(state)
                    return _serial_result(self.feature, mode, "worker-failed", lanes)
        self._save(state)
        return {"version": 1, "feature": self.feature, "mode": mode, "fallback": False, "state": state, "actions": actions}

    def release_lane(self, lane_id: str) -> dict[str, Any]:
        snapshot = self._workflow()
        state = self._load_state(snapshot)
        if state is None or lane_id not in state["lanes"]:
            raise ExecutorError("unknown lane")
        lane = state["lanes"][lane_id]
        lease = lane.get("lease")
        if not isinstance(lease, dict) or not isinstance(lease.get("lease_id"), str):
            return {"released": False, "reason": "no-lease"}
        if lease.get("released") is True:
            return {"released": True, "lease_id": lease["lease_id"], "idempotent": True}
        provider = self._provider(snapshot)
        if provider is None:
            raise ExecutorError("missing resource provider")
        key, action = self._record_action(state, lane_id, lane, "release")
        self._save(state)
        if action["status"] == "accepted" or action["status"] == "released":
            lease["released"] = True
            self._save(state)
            return {"released": True, "lease_id": lease["lease_id"], "idempotent": True}
        request = {
            "repository": str(self.root),
            "feature": self.feature,
            "slice": lane["slice"],
            "task": lane["task"],
            "worktree": lane.get("worktree_path", ""),
            "idempotency_key": key,
            "resources": lane.get("resources", []),
        }
        receipt = provider.release(request, lease["lease_id"])
        lease["released"] = True
        self._accept(action, external_id=receipt["lease_id"], receipt=receipt)
        action["status"] = "released"
        self._save(state)
        return {"released": True, "lease_id": lease["lease_id"], "idempotent": False}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("start", "resume", "status"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--feature", required=True)
    parser.add_argument("--adapter", choices=("auto", "orca"), default="auto")
    parser.add_argument("--wait-seconds", type=float, default=30)
    return parser


def _adapter_factory(name: str, root: Path, feature: str) -> Callable[[], Any] | None:
    if name not in {"auto", "orca"}:
        return None
    try:
        import orca_adapter  # type: ignore[import-not-found]
    except ImportError:
        return None
    factory = getattr(orca_adapter, "Adapter", None) or getattr(orca_adapter, "OrcaAdapter", None)
    if factory is None:
        return None
    return lambda: factory(root=root, feature=feature)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        coordinator = Coordinator(
            args.root,
            args.feature,
            adapter_factory=None if args.command == "status" else _adapter_factory(args.adapter, args.root, args.feature),
        )
        if args.command == "status":
            result = coordinator.status()
        else:
            result = coordinator.start(resume=args.command == "resume")
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ExecutorError, OSError, subprocess.SubprocessError) as exc:
        print(f"parallel executor: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
