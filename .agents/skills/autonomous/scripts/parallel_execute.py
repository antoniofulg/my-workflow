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
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


MODES = {"disabled", "safe", "full"}
LANE_STATES = {"ready", "needs_resources", "running", "waiting", "needs_sync", "invalidated", "gate_required", "complete", "failed", "serial"}
TRANSITIONS: dict[str, set[str]] = {
    "ready": {"needs_resources", "running", "invalidated", "serial", "failed"},
    "needs_resources": {"running", "invalidated", "serial", "failed"},
    "running": {"waiting", "needs_sync", "invalidated", "complete", "failed", "serial"},
    "waiting": {"needs_sync", "running", "invalidated", "failed", "serial"},
    "needs_sync": {"running", "serial", "failed"},
    "invalidated": {"gate_required", "serial", "failed"},
    "gate_required": {"ready", "running", "waiting", "serial", "failed"},
    "complete": set(),
    "failed": set(),
    "serial": {"ready"},
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


def _validate_technical_verifier_receipt(
    receipt: Mapping[str, Any], lane: Mapping[str, Any], *, feature: str, current_head: str
) -> None:
    required = (
        "receipt_id", "feature", "slice", "task", "worktree_id", "worktree_path",
        "current_head", "author", "implementer", "verdict",
    )
    if any(not isinstance(receipt.get(field), str) or not receipt[field] for field in required):
        raise StateError("malformed technical verifier receipt")
    if (
        receipt["feature"] != feature
        or receipt["slice"] != lane.get("slice")
        or receipt["task"] != lane.get("task")
        or receipt["worktree_id"] != lane.get("worktree_id")
        or receipt["worktree_path"] != lane.get("worktree_path")
        or receipt["current_head"] != current_head
        or receipt["verdict"] != "passed"
        or receipt["author"] == receipt["implementer"]
    ):
        raise StateError("uncorrelated technical verifier receipt")


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
    post_gate = state.get("post_integration_gate")
    if post_gate is not None:
        if (
            not isinstance(post_gate, Mapping)
            or post_gate.get("status") != "required"
            or not isinstance(post_gate.get("current_head"), str)
            or post_gate.get("invalidated_evidence") != ["gate", "technical_verifier", "deep_review"]
        ):
            raise StateError("invalid post-integration gate state")

    active_slices: set[str] = set()
    seen_external: set[str] = set()
    seen_lease_ids: set[str] = set()
    seen_action_external_ids: dict[str, str] = {}
    for lane_id, lane in lanes.items():
        if not isinstance(lane_id, str) or not _ID.fullmatch(lane_id) or not isinstance(lane, Mapping):
            raise StateError("invalid lane receipt")
        slice_id = _require_text(lane.get("slice"), "lane slice")
        task_id = _require_text(lane.get("task"), "lane task")
        state_name = lane.get("state")
        if state_name not in LANE_STATES:
            raise StateError(f"invalid lane state: {lane_id}")
        if state_name in {"needs_resources", "running", "waiting", "needs_sync", "invalidated", "gate_required"}:
            if slice_id in active_slices:
                raise StateError(f"duplicate active lane slice: {slice_id}")
            active_slices.add(slice_id)
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
        lease = lane.get("lease")
        if lease is not None:
            if not isinstance(lease, Mapping):
                raise StateError(f"invalid lease receipt: {lane_id}")
            lease_id = _require_text(lease.get("lease_id"), "lease id")
            _require_text(lease.get("idempotency_key"), "lease idempotency key")
            lease_resources = lease.get("resources")
            if lease_resources != resources or lease.get("prepared_worktree") is not True:
                raise StateError(f"invalid lease receipt: {lane_id}")
            if not isinstance(lease_resources, list) or any(not isinstance(item, str) or not item for item in lease_resources):
                raise StateError(f"invalid lease resources: {lane_id}")
            if not isinstance(lease.get("environment_keys"), list) or any(not isinstance(item, str) for item in lease["environment_keys"]):
                raise StateError(f"invalid lease environment keys: {lane_id}")
            environment = lease.get("environment")
            if not isinstance(environment, Mapping) or any(value != "<redacted>" for value in environment.values()):
                raise StateError(f"unredacted lease environment: {lane_id}")
            if type(lease.get("released")) is not bool:
                raise StateError(f"invalid lease release state: {lane_id}")
            if lease_id in seen_lease_ids:
                raise StateError(f"duplicate live lease: {lease_id}")
            seen_lease_ids.add(lease_id)
    for key, action in actions.items():
        if not isinstance(key, str) or not _ID.fullmatch(key) or not isinstance(action, Mapping):
            raise StateError("invalid action receipt")
        if action.get("key") != key or action.get("action") not in {
            "worktree", "worktree_cleanup", "worker", "follow_up", "acquire", "release", "worker_ack", "worker_release", "sync", "gate", "integrate", "technical_verifier"
        }:
            raise StateError("invalid action receipt")
        if action.get("status") not in {"pending", "accepted", "released", "failed"}:
            raise StateError("invalid action status")
        action_lane_id = _require_text(action.get("lane"), "action lane")
        if action_lane_id not in lanes:
            raise StateError("action references unknown lane")
        if action.get("status") in {"accepted", "released"}:
            external_id = _require_text(action.get("external_id"), "action external id")
            previous_action = seen_action_external_ids.get(external_id)
            if previous_action is not None and {previous_action, action["action"]} != {"acquire", "release"}:
                raise StateError("duplicate external receipt")
            seen_action_external_ids[external_id] = str(action["action"])
            receipt = action.get("receipt")
            if not isinstance(receipt, Mapping):
                raise StateError("missing action receipt")
            lane = lanes[action_lane_id]
            if action["action"] == "acquire":
                normalize_lease_receipt(
                    receipt,
                    {"resources": lane.get("resources", []), "idempotency_key": key},
                    set(),
                )
            elif action["action"] == "release":
                if receipt.get("lease_id") != external_id or receipt.get("released") is not True:
                    raise StateError("invalid release receipt")
            elif action["action"] == "integrate":
                if (
                    receipt.get("status") != "merged"
                    or not isinstance(receipt.get("post_head"), str)
                    or receipt.get("invalidated_evidence") != ["gate", "technical_verifier", "deep_review"]
                ):
                    raise StateError("invalid integration receipt")
            elif action["action"] == "technical_verifier":
                lane_head = lane.get("current_head")
                if not isinstance(lane_head, str):
                    raise StateError("technical verifier lacks current lane head")
                _validate_technical_verifier_receipt(
                    receipt, lane, feature=actual_feature, current_head=lane_head
                )
        elif action.get("receipt") is not None:
            raise StateError("pending action contains receipt")


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
    except ValueError:
        # macOS commonly exposes /var as a symlink to /private/var; validate the
        # resolved destination below while still checking lexical components
        # whenever the candidate is visibly inside the declared root.
        pass
    else:
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


def derive_worktree_destination(root: Path, feature: str, slice_id: str, task: str) -> Path:
    """Return a deterministic, validated sibling destination for a Git worktree."""
    if not all(_ID.fullmatch(value) for value in (feature, slice_id, task)):
        raise PathBoundaryError("invalid worktree identity")
    common = _git_common_dir(Path(root).resolve())
    anchor = common.parent.parent
    destination = anchor / f".{Path(root).resolve().name}-parallel-slices" / feature / f"{slice_id}-{task}"
    return bounded_path(anchor, destination)


def create_git_worktree(root: Path, destination: Path, source_head: str) -> dict[str, str]:
    """Create the already-validated checkout that an adapter will attach a worker to."""
    bounded_path(destination.parent.parent.parent, destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    run_argv(
        ["git", "worktree", "add", "--detach", str(destination), source_head],
        cwd=root,
        timeout=60,
    )
    gitdir_value = run_argv(["git", "rev-parse", "--git-dir"], cwd=destination).stdout.strip()
    gitdir = (destination / gitdir_value if not Path(gitdir_value).is_absolute() else Path(gitdir_value)).resolve()
    return {
        "worktree_id": str(gitdir),
        "gitdir": str(gitdir),
        "worktree_path": str(destination),
        "branch": "(detached)",
        "pre_head": source_head,
    }


def idempotency_key(feature: str, slice_id: str, task: str, action: str, source_checkpoint: str) -> str:
    material = "\0".join((feature, slice_id, task, action, source_checkpoint)).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def normalize_lease_receipt(
    payload: Mapping[str, Any], request: Mapping[str, Any], live_lease_ids: set[str]
) -> dict[str, Any]:
    lease_id = payload.get("lease_id")
    environment = payload.get("environment")
    if (
        not isinstance(lease_id, str)
        or not lease_id
        or lease_id in live_lease_ids
        or payload.get("resources") != request.get("resources")
        or payload.get("prepared_worktree") is not True
        or not isinstance(environment, Mapping)
        or payload.get("idempotency_key") != request.get("idempotency_key")
    ):
        raise ExecutorError("resource receipt is uncorrelated or already live")
    return {
        "lease_id": lease_id,
        "idempotency_key": request["idempotency_key"],
        "resources": list(request["resources"]),
        "prepared_worktree": True,
        "environment_keys": sorted(str(key) for key in environment),
        "environment": {str(key): "<redacted>" for key in sorted(environment)},
        "released": False,
    }


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


def _compatibility_is_usable(result: Mapping[str, Any]) -> bool:
    """Only an explicit, clean compatibility result may authorize host effects."""
    proof = result.get("proof")
    return result.get("status") == "compatible" and isinstance(proof, Mapping) and proof.get("cleanup") == "clean"


def _adapter_fallback(
    feature: str,
    mode: str,
    result: Mapping[str, Any],
    lanes: list[dict[str, Any]],
) -> dict[str, Any]:
    adapter = result.get("adapter", "unknown")
    reason = result.get("reason")
    if not isinstance(reason, str) or not reason:
        missing = result.get("missing_capabilities")
        reason = "missing-capabilities:" + ",".join(str(item) for item in missing) if isinstance(missing, list) and missing else "incompatible"
    return _serial_result(feature, mode, f"{adapter}:{reason}", lanes)


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
        return normalize_lease_receipt(payload, request, live_lease_ids)

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
        git_adapter_factory: Callable[[], Any] | None = None,
        gate_receipt_factory: Callable[[Mapping[str, Any]], Mapping[str, Any] | None] | None = None,
        provider_factory: Callable[[Path], ResourceProvider] | None = None,
        worktree_creator: Callable[[Path, str], Mapping[str, Any]] | None = None,
    ):
        self.root = Path(root).resolve()
        self.feature = feature
        self.adapter_factory = adapter_factory
        self.git_adapter_factory = git_adapter_factory
        self.gate_receipt_factory = gate_receipt_factory
        self.provider_factory = provider_factory
        self.worktree_creator = worktree_creator
        self.state_path: Path | None = None

    def _prepare_repository(self) -> None:
        if self.state_path is None:
            self.root = _repository_root(self.root)
            self.state_path = runtime_state_path(self.root, self.feature)

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
        if self.state_path is None:
            raise StateError("runtime state path is unavailable")
        try:
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
            validate_runtime_state(state, str(self.root), self.feature)
            return state
        except FileNotFoundError:
            return None
        except (OSError, json.JSONDecodeError, StateError) as exc:
            raise StateError(str(exc)) from exc

    def _save(self, state: dict[str, Any]) -> None:
        if self.state_path is None:
            raise StateError("runtime state path is unavailable")
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
        if workflow["parallelization"]["mode"] == "disabled":
            return {"version": 1, "feature": self.feature, "mode": "disabled", "state": None, "actions": []}
        self._prepare_repository()
        try:
            state = self._load_state(workflow)
        except StateError as exc:
            return _serial_result(self.feature, workflow["parallelization"]["mode"], f"state:{exc}")
        if state is None:
            return {"version": 1, "feature": self.feature, "mode": workflow["parallelization"]["mode"], "state": None, "actions": []}
        return {"version": 1, "feature": self.feature, "mode": state["mode"], "state": state, "actions": []}

    def preflight(self, *, adapter: str, canary: bool = False) -> dict[str, Any]:
        """Inspect one host adapter before any scheduler or checkout effect."""
        workflow = self._workflow()
        mode = workflow["parallelization"]["mode"]
        if mode == "disabled":
            return {
                "version": 1,
                "feature": self.feature,
                "mode": mode,
                "adapter": adapter,
                "status": "disabled",
                "reason": "disabled-mode",
                "proof": {"cleanup": "not-run"},
            }
        if self.adapter_factory is None:
            return {
                "version": 1,
                "feature": self.feature,
                "mode": mode,
                "adapter": adapter,
                "status": "unsupported",
                "reason": "adapter-unavailable",
                "proof": {"cleanup": "not-run"},
            }
        try:
            instance = self.adapter_factory()
            probe = getattr(instance, "probe", None)
            if not callable(probe):
                return {
                    "version": 1,
                    "feature": self.feature,
                    "mode": mode,
                    "adapter": adapter,
                    "status": "unsupported",
                    "reason": "compatibility-probe-unavailable",
                    "proof": {"cleanup": "not-run"},
                }
            result = probe()
            if not isinstance(result, Mapping):
                raise ExecutorError("malformed compatibility result")
            if canary and result.get("status") == "candidate":
                run_canary = getattr(instance, "canary", None)
                if not callable(run_canary):
                    return {**dict(result), "status": "unsupported", "reason": "canary-unavailable"}
                try:
                    run_canary()
                except Exception as exc:
                    details = getattr(exc, "details", None)
                    failure = {"status": "unsupported", "reason": str(exc)}
                    if isinstance(details, Mapping):
                        failure["failure"] = dict(details)
                    return {**dict(result), **failure}
                result = probe()
            return dict(result)
        except Exception as exc:
            return {
                "version": 1,
                "feature": self.feature,
                "mode": mode,
                "adapter": adapter,
                "status": "unsupported",
                "reason": str(exc),
                "proof": {"cleanup": "not-run"},
            }

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

    def _git_adapter(self) -> Any:
        if self.git_adapter_factory is not None:
            return self.git_adapter_factory()
        scripts = Path(__file__).resolve().parent
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        import git_adapter

        return git_adapter.GitAdapter(self.root)

    def _checkpoint_lanes(self, state: Mapping[str, Any], plan_lane: Mapping[str, Any]) -> list[Mapping[str, Any]]:
        dependencies = plan_lane.get("sync_after", [])
        if not isinstance(dependencies, list):
            raise ExecutorError("malformed checkpoint dependencies")
        lanes = state.get("lanes", {})
        result: list[Mapping[str, Any]] = []
        for dependency in dependencies:
            matches = [lane for lane in lanes.values() if isinstance(lane, Mapping) and lane.get("task") == dependency]
            if len(matches) != 1 or not isinstance(matches[0].get("current_head"), str):
                raise ExecutorError("missing exact producer checkpoint receipt")
            result.append(matches[0])
        return result

    def _consume_gate(self, state: dict[str, Any], lane_id: str, lane: dict[str, Any]) -> bool:
        if lane.get("state") not in {"invalidated", "gate_required"}:
            return True
        if lane.get("state") == "invalidated":
            transition_lane(state, lane_id, "gate_required", expected="invalidated")
        key, action, created = self._record_action(state, lane_id, lane, "gate")
        self._save(state)
        if action.get("status") in {"accepted", "released"}:
            return True
        if self.gate_receipt_factory is None:
            lane["gate_error"] = "gate receipt unavailable"
            self._save(state)
            return False
        receipt = self.gate_receipt_factory({"lane": lane_id, "current_head": lane.get("current_head"), "gate": "gate"})
        valid = (
            isinstance(receipt, Mapping)
            and receipt.get("passed") is True
            and receipt.get("current_head") == lane.get("current_head")
            and receipt.get("lane") == lane_id
            and receipt.get("gate") == "gate"
        )
        if not valid:
            lane["gate_error"] = "invalid gate receipt"
            self._save(state)
            return False
        self._accept(action, external_id="gate:" + str(lane.get("current_head")), receipt=dict(receipt))
        invalidated = lane.get("invalidated_evidence", [])
        if not isinstance(invalidated, list):
            raise StateError("invalidated evidence is malformed")
        lane["invalidated_evidence"] = [item for item in invalidated if item != "gate"]
        lane.pop("gate_error", None)
        if lane["state"] == "gate_required":
            resume_state = lane.get("checkpoint_previous_state", "ready")
            if resume_state not in {"ready", "running", "waiting"}:
                resume_state = "ready"
            transition_lane(state, lane_id, resume_state, expected="gate_required")
        self._save(state)
        return True

    def _sync_lane(self, state: dict[str, Any], lane_id: str, plan_lane: Mapping[str, Any], lane: dict[str, Any]) -> str:
        dependencies = plan_lane.get("sync_after", [])
        if not dependencies:
            return "ready"
        producers = self._checkpoint_lanes(state, plan_lane)
        checkpoints = [str(producer["current_head"]) for producer in producers]
        key, action, created = self._record_action(state, lane_id, lane, "sync")
        replayed = action.get("status") in {"accepted", "released"}
        if replayed and action.get("producer_commits") != checkpoints:
            raise ExecutorError("checkpoint receipt does not match declared producers")
        if not replayed:
            action["producer_commits"] = checkpoints
            action["pre_head"] = lane.get("current_head") or lane.get("pre_head")
        self._save(state)
        if action.get("status") in {"accepted", "released"}:
            receipt = action.get("receipt")
        else:
            adapter = self._git_adapter()
            declared = plan_lane.get("declared_paths")
            receipt = adapter.sync_checkpoint(
                lane["worktree_path"], checkpoints[0] if len(checkpoints) == 1 else checkpoints,
                declared_paths=declared if isinstance(declared, list) else None,
                expected_receipt=dict(lane),
            )
            if not isinstance(receipt, Mapping):
                raise ExecutorError("malformed checkpoint receipt")
        if not isinstance(receipt, Mapping):
            receipt = {"status": "serial", "reason": "malformed-checkpoint-receipt"}
        status = receipt.get("status")
        if status == "serial":
            reason = receipt.get("reason") if isinstance(receipt.get("reason"), str) else "checkpoint-failed"
            serial_receipt = {
                "status": "serial",
                "serial_recovery": True,
                "reason": reason,
                "pre_head": action.get("pre_head") or lane.get("current_head") or "unknown",
                "post_head": action.get("pre_head") or lane.get("current_head") or "unknown",
            }
            if action.get("status") == "pending":
                self._accept(action, external_id="serial:" + reason, receipt=serial_receipt)
            action["producer_commits"] = checkpoints
            if lane["state"] in {"ready", "running", "waiting"}:
                transition_lane(state, lane_id, "serial", expected=lane["state"])
            lane["fallback_reason"] = reason
            self._save(state)
            return "serial"
        if status not in {"noop", "synced"}:
            serial = {"status": "serial", "reason": "malformed-checkpoint-receipt"}
            self._accept(action, external_id="serial:malformed-checkpoint-receipt", receipt=serial)
            transition_lane(state, lane_id, "serial", expected=lane["state"])
            lane["fallback_reason"] = "malformed-checkpoint-receipt"
            self._save(state)
            return "serial"
        pre_head = receipt.get("pre_head")
        post_head = receipt.get("post_head")
        if not isinstance(pre_head, str) or not pre_head or not isinstance(post_head, str) or not post_head:
            serial = {"status": "serial", "reason": "malformed-checkpoint-receipt"}
            self._accept(action, external_id="serial:malformed-checkpoint-receipt", receipt=serial)
            transition_lane(state, lane_id, "serial", expected=lane["state"])
            lane["fallback_reason"] = "malformed-checkpoint-receipt"
            self._save(state)
            return "serial"
        if not replayed and pre_head != action.get("pre_head"):
            serial = {"status": "serial", "reason": "uncorrelated-checkpoint-receipt", "pre_head": pre_head, "post_head": post_head}
            self._accept(action, external_id="serial:uncorrelated-checkpoint-receipt", receipt=serial)
            transition_lane(state, lane_id, "serial", expected=lane["state"])
            lane["fallback_reason"] = "uncorrelated-checkpoint-receipt"
            self._save(state)
            return "serial"
        if status == "noop" and pre_head != post_head:
            serial = {"status": "serial", "reason": "invalid-checkpoint-head", "pre_head": pre_head, "post_head": post_head}
            self._accept(action, external_id="serial:invalid-checkpoint-head", receipt=serial)
            transition_lane(state, lane_id, "serial", expected=lane["state"])
            lane["fallback_reason"] = "invalid-checkpoint-head"
            self._save(state)
            return "serial"
        if status == "synced" and receipt.get("producer_commit") not in checkpoints:
            serial = {"status": "serial", "reason": "uncorrelated-checkpoint-receipt", "pre_head": pre_head, "post_head": post_head}
            self._accept(action, external_id="serial:uncorrelated-checkpoint-receipt", receipt=serial)
            transition_lane(state, lane_id, "serial", expected=lane["state"])
            lane["fallback_reason"] = "uncorrelated-checkpoint-receipt"
            self._save(state)
            return "serial"
        if action.get("status") == "pending":
            self._accept(action, external_id=post_head, receipt=dict(receipt))
            action["producer_commits"] = checkpoints
            self._save(state)
        lane["current_head"] = post_head
        lane["checkpoint_receipt"] = dict(receipt)
        changed = receipt.get("changed") if isinstance(receipt.get("changed"), bool) else pre_head != post_head
        if changed:
            if replayed:
                self._save(state)
                return "ready"
            evidence = receipt.get("invalidated_evidence")
            if evidence != ["gate", "technical_verifier", "deep_review"]:
                raise ExecutorError("checkpoint receipt omitted evidence invalidation")
            lane["invalidated_evidence"] = list(evidence)
            lane["checkpoint_previous_state"] = lane["state"]
            if lane["state"] in {"ready", "running", "waiting"}:
                transition_lane(state, lane_id, "invalidated", expected=lane["state"])
                transition_lane(state, lane_id, "gate_required", expected="invalidated")
            self._save(state)
            return "blocked"
        self._save(state)
        return "ready"

    def _record_action(
        self, state: dict[str, Any], lane_id: str, lane: Mapping[str, Any], action: str
    ) -> tuple[str, dict[str, Any], bool]:
        key = idempotency_key(self.feature, str(lane["slice"]), str(lane["task"]), action, state["source_git_head"])
        receipt = state["actions"].get(key)
        created = receipt is None
        if receipt is None:
            receipt = {"key": key, "action": action, "status": "pending", "lane": lane_id}
            state["actions"][key] = receipt
        return key, receipt, created

    def _reconcile_pending(self, adapter: Any, action: Mapping[str, Any]) -> Mapping[str, Any] | None:
        reconcile = getattr(adapter, "reconcile_action", None)
        if not callable(reconcile):
            return None
        receipt = reconcile(dict(action))
        return receipt if isinstance(receipt, Mapping) else None

    def _worktree_destination(self, lane: Mapping[str, Any]) -> Path:
        return derive_worktree_destination(self.root, self.feature, str(lane["slice"]), str(lane["task"]))

    def _cleanup_rejected_worktree(self, state: dict[str, Any], lane_id: str, lane: dict[str, Any]) -> None:
        worktree_path = lane.get("worktree_path")
        if not isinstance(worktree_path, str) or not worktree_path:
            return
        key, action, created = self._record_action(state, lane_id, lane, "worktree_cleanup")
        self._save(state)
        if action.get("status") in {"accepted", "released"}:
            return
        adapter = self._git_adapter()
        remover = getattr(adapter, "remove_worktree", None)
        if not callable(remover):
            raise ExecutorError("worktree cleanup unavailable")
        expected_head = lane.get("current_head") or lane.get("pre_head")
        receipt = remover(
            worktree_path,
            expected_receipt=dict(lane),
            expected_head=expected_head if isinstance(expected_head, str) else None,
        )
        if not isinstance(receipt, Mapping) or receipt.get("removed") is not True or receipt.get("worktree_path") != worktree_path:
            raise ExecutorError("uncorrelated worktree cleanup receipt")
        self._accept(action, external_id="worktree-cleanup:" + worktree_path, receipt=dict(receipt))
        lane["worktree_cleanup"] = dict(receipt)
        self._save(state)

    def _record_producer_head(self, state: dict[str, Any], lane_id: str, lane: dict[str, Any]) -> str:
        worktree_path = lane.get("worktree_path")
        if not isinstance(worktree_path, str) or not worktree_path:
            raise ExecutorError("missing owned worktree for producer checkpoint")
        expected_head = lane.get("current_head") or lane.get("pre_head")
        current_head = self._git_adapter().head(
            worktree_path,
            expected_receipt=dict(lane),
            expected_head=expected_head if isinstance(expected_head, str) and lane.get("current_head") else None,
        )
        if not isinstance(current_head, str) or not current_head:
            raise ExecutorError("missing producer worktree HEAD")
        lane["current_head"] = current_head
        self._save(state)
        return current_head

    def _consume_technical_verifier_receipts(
        self, state: dict[str, Any], receipts: Sequence[Mapping[str, Any]] | None
    ) -> None:
        if receipts is None:
            return
        for receipt in receipts:
            if not isinstance(receipt, Mapping):
                continue
            lane_id = next(
                (
                    candidate_id
                    for candidate_id, candidate in state["lanes"].items()
                    if isinstance(candidate, Mapping)
                    and candidate.get("slice") == receipt.get("slice")
                    and candidate.get("task") == receipt.get("task")
                ),
                None,
            )
            if lane_id is None:
                continue
            lane = state["lanes"][lane_id]
            key, action, _ = self._record_action(state, lane_id, lane, "technical_verifier")
            try:
                current_head = lane.get("current_head")
                if not isinstance(current_head, str):
                    raise StateError("technical verifier lacks current lane head")
                _validate_technical_verifier_receipt(
                    receipt, lane, feature=self.feature, current_head=current_head
                )
            except StateError as exc:
                action["status"] = "failed"
                action.pop("receipt", None)
                action["error"] = str(exc)
                self._save(state)
                continue
            self._accept(action, external_id=str(receipt["receipt_id"]), receipt=dict(receipt))
            action["idempotency_key"] = key
            self._save(state)

    def _integrate_verified_slices(self, state: dict[str, Any], plan: Mapping[str, Any]) -> str:
        if state.get("mode") != "full":
            return "not-applicable"
        plan_lanes = [lane for lane in plan.get("lanes", []) if isinstance(lane, Mapping) and lane.get("id") != "serial"]
        if not plan_lanes:
            return "not-applicable"
        entries: list[dict[str, Any]] = []
        for plan_lane in plan_lanes:
            lane_id = str(plan_lane.get("id", ""))
            lane = state.get("lanes", {}).get(lane_id)
            if not isinstance(lane, Mapping) or lane.get("state") != "complete":
                return "incomplete"
            current_head = lane.get("current_head")
            if not isinstance(current_head, str) or not current_head:
                return "unverified"
            worker_key = idempotency_key(self.feature, str(plan_lane["slice"]), str(plan_lane["task"]), "worker", state["source_git_head"])
            worker_action = state["actions"].get(worker_key)
            completion = worker_action.get("completion") if isinstance(worker_action, Mapping) else None
            delivery = worker_action.get("delivery") if isinstance(worker_action, Mapping) else None
            payload = delivery.get("payload") if isinstance(delivery, Mapping) else None
            outcome = completion.get("outcome") if isinstance(completion, Mapping) else None
            if outcome is None and isinstance(payload, Mapping):
                outcome = payload.get("outcome")
            if outcome not in {"succeeded", "passed", "complete"}:
                return "unverified"
            verifier_key = idempotency_key(
                self.feature, str(plan_lane["slice"]), str(plan_lane["task"]), "technical_verifier", state["source_git_head"]
            )
            verifier_action = state["actions"].get(verifier_key)
            if not isinstance(verifier_action, Mapping) or verifier_action.get("status") not in {"accepted", "released"}:
                return "unverified"
            verifier_receipt = verifier_action.get("receipt")
            if not isinstance(verifier_receipt, Mapping):
                return "unverified"
            try:
                _validate_technical_verifier_receipt(
                    verifier_receipt, lane, feature=self.feature, current_head=current_head
                )
            except StateError:
                return "unverified"
            entries.append({"slice": str(plan_lane["slice"]), "commit": current_head})
        lane_id = str(plan_lanes[0]["id"])
        lane = state["lanes"][lane_id]
        _, action, created = self._record_action(state, lane_id, lane, "integrate")
        self._save(state)
        if action.get("status") in {"accepted", "released"}:
            return "merged"
        git = self._git_adapter()
        if not created:
            receipt = self._reconcile_pending(git, action)
            if receipt is None:
                lane["fallback_reason"] = "unreconciled-pending:integrate"
                self._save(state)
                return "serial"
        else:
            root_head = git.head(self.root)
            if root_head != state["source_git_head"]:
                lane["fallback_reason"] = "feature-head-moved"
                state["integration_recovery"] = {
                    "status": "serial",
                    "reason": "feature-head-moved",
                    "expected_head": state["source_git_head"],
                    "actual_head": root_head,
                }
                self._save(state)
                return "serial"
            receipt = git.integrate_slices(self.root, entries)
        if not isinstance(receipt, Mapping) or receipt.get("status") != "merged":
            lane["fallback_reason"] = "integration-failed"
            self._save(state)
            return "serial"
        merged = receipt.get("merged")
        expected_commits = [entry["commit"] for entry in sorted(entries, key=lambda item: (item["slice"], item["commit"]))]
        if merged != expected_commits or not isinstance(receipt.get("post_head"), str) or not isinstance(receipt.get("pre_head"), str):
            lane["fallback_reason"] = "uncorrelated-integration-receipt"
            self._save(state)
            return "serial"
        self._accept(action, external_id=receipt["post_head"], receipt=dict(receipt))
        state["integration_receipt"] = dict(receipt)
        state["post_integration_gate"] = {
            "status": "required",
            "current_head": receipt["post_head"],
            "invalidated_evidence": ["gate", "technical_verifier", "deep_review"],
        }
        self._save(state)
        return "merged"

    def _create_worktree(self, destination: Path) -> Mapping[str, Any]:
        if self.worktree_creator is not None:
            receipt = self.worktree_creator(destination, self._source_head)
            return receipt if isinstance(receipt, Mapping) else {}
        return create_git_worktree(self.root, destination, self._source_head)

    def _accept(self, action_receipt: dict[str, Any], **fields: Any) -> None:
        action_receipt.update(fields)
        action_receipt["status"] = "accepted"

    def _resume_worker_event(
        self,
        snapshot: Mapping[str, Any],
        state: dict[str, Any],
        lane_id: str,
        plan_lane: Mapping[str, Any],
        lane: dict[str, Any],
        adapter: Any,
        provider: ResourceProvider | None,
        wait_seconds: float = 30,
    ) -> str:
        """Consume one Run delivery; return continue, handled, or serial."""
        try:
            worker_key = idempotency_key(self.feature, str(plan_lane["slice"]), str(plan_lane["task"]), "worker", state["source_git_head"])
            worker_action = state["actions"].get(worker_key)
            if not isinstance(worker_action, dict):
                raise ExecutorError("missing worker action receipt")
            completion = worker_action.get("completion")
            persisted_delivery = worker_action.get("delivery")
            delivery = (
                dict(persisted_delivery)
                if isinstance(persisted_delivery, Mapping)
                else adapter.wait_events(dict(lane), timeout=wait_seconds)
            )
            if delivery.get("event") == "timeout":
                return "handled"
            if delivery.get("event") in {"waiting", "question"}:
                ended = adapter.end_waiter(dict(lane), dict(delivery))
                if not isinstance(ended, Mapping) or ended.get("ended") is not True:
                    raise ExecutorError("worker waiter was not ended")
                lane["waiter"] = {**dict(delivery), "ended": True}
                if lane["state"] == "running":
                    transition_lane(state, lane_id, "waiting", expected="running")
                self._save(state)
                return "handled"
            if delivery.get("event") == "dependency" and lane["state"] == "waiting":
                waiter = lane.get("waiter")
                if not isinstance(waiter, Mapping):
                    raise ExecutorError("missing waiter receipt")
                follow_key, follow_action, follow_created = self._record_action(state, lane_id, lane, "follow_up")
                self._save(state)
                if follow_action["status"] == "pending":
                    if not follow_created:
                        follow_receipt = self._reconcile_pending(adapter, follow_action)
                        if follow_receipt is None:
                            raise ExecutorError("unreconciled pending action: follow_up")
                    else:
                        follow_receipt = adapter.follow_up(dict(lane), waiter, dict(delivery), idempotency_key=follow_key)
                    if not isinstance(follow_receipt, Mapping):
                        raise ExecutorError("malformed follow-up receipt")
                    self._validate_worker_receipt(follow_receipt, lane, plan_lane, follow_key, state["source_git_head"])
                    follow_receipt = self._project_worker_receipt(follow_receipt)
                    self._accept(follow_action, external_id=follow_receipt.get("dispatch_id"), receipt=dict(follow_receipt))
                    for key in ("run_id", "orchestration_task_id", "dispatch_id", "terminal_handle"):
                        if key in follow_receipt:
                            lane[key] = follow_receipt[key]
                    transition_lane(state, lane_id, "running", expected="waiting")
                    self._save(state)
                return "handled"
            if delivery.get("event") != "worker_done":
                raise ExecutorError("unhandled worker delivery")
            if not isinstance(completion, Mapping):
                worker_action["delivery"] = dict(delivery)
                self._save(state)
                output = adapter.read_worker(dict(lane))
                accepted = adapter.accept_worker_done(dict(lane), dict(delivery), dict(output))
                accepted = {**dict(accepted), "delivery_id": delivery["delivery_id"]}
                worker_action["completion"] = dict(accepted)
                lane["lifecycle_events"] = ["worker_done", "worker_read"]
                self._save(state)
            else:
                accepted = dict(completion)
            if not isinstance(lane.get("current_head"), str):
                lane["current_head"] = self._record_producer_head(state, lane_id, lane)
                accepted["current_head"] = lane["current_head"]
                worker_action["completion"] = dict(accepted)
                self._save(state)
            ack_key, ack_action, ack_created = self._record_action(state, lane_id, lane, "worker_ack")
            ack_action["delivery_id"] = delivery["delivery_id"]
            ack_action["run_id"] = lane["run_id"]
            self._save(state)
            if ack_action["status"] == "pending":
                ack = adapter.ack_delivery(dict(lane), dict(delivery)) if ack_created else self._reconcile_pending(adapter, ack_action)
                if not isinstance(ack, Mapping) or ack.get("acknowledged") is not True:
                    raise ExecutorError("delivery was not acknowledged")
                if ack.get("delivery_id") != delivery["delivery_id"]:
                    raise ExecutorError("delivery acknowledgement is uncorrelated")
                self._accept(ack_action, external_id="ack:" + str(delivery["delivery_id"]), receipt=dict(ack))
                worker_action["delivery_ack"] = dict(ack)
                lane["lifecycle_events"] = ["worker_done", "worker_read", "worker_ack"]
                self._save(state)
            release_key, release_action, release_created = self._record_action(state, lane_id, lane, "worker_release")
            release_action["dispatch_id"] = lane["dispatch_id"]
            self._save(state)
            if release_action["status"] == "pending":
                if not release_created:
                    release_receipt = self._reconcile_pending(adapter, release_action)
                    if release_receipt is None:
                        raise ExecutorError("unreconciled pending action: release")
                else:
                    release_receipt = adapter.release(dict(lane), dict(accepted))
                if (
                    not isinstance(release_receipt, Mapping)
                    or release_receipt.get("released") is not True
                    or release_receipt.get("dispatch_id") != lane["dispatch_id"]
                ):
                    raise ExecutorError("worker release receipt was not accepted")
                self._accept(release_action, external_id="release:" + str(lane["dispatch_id"]), receipt=dict(release_receipt))
                lane["lifecycle_events"] = ["worker_done", "worker_read", "worker_ack", "worker_release"]
                self._save(state)
            if lane.get("lease") is not None:
                self._release_lease_state(snapshot, state, lane_id, provider)
            if lane["state"] == "running":
                transition_lane(state, lane_id, "complete", expected="running")
            self._save(state)
            return "handled"
        except Exception as exc:
            lane["fallback_reason"] = "worker:" + str(exc)
            if lane["state"] in {"running", "waiting"}:
                transition_lane(state, lane_id, "serial", expected=lane["state"])
            self._save(state)
            return "serial"

    def _validate_worker_receipt(
        self,
        receipt: Mapping[str, Any],
        lane: Mapping[str, Any],
        plan_lane: Mapping[str, Any],
        key: str,
        source_head: str,
    ) -> None:
        required = (
            "feature", "slice", "worktree_id", "worktree_path", "branch", "pre_head", "run_id",
            "orchestration_task_id", "task", "dispatch_id", "terminal_handle", "idempotency_key",
        )
        if any(not isinstance(receipt.get(field), str) or not receipt[field] for field in required):
            raise ExecutorError("incomplete worker receipt")
        for field in ("worktree_id", "worktree_path", "branch", "pre_head"):
            if receipt[field] != lane.get(field):
                raise ExecutorError(f"uncorrelated worker receipt: {field}")
        if receipt["pre_head"] != source_head:
            raise ExecutorError("worker source head changed")
        if receipt["feature"] != self.feature or receipt["slice"] != str(plan_lane["slice"]):
            raise ExecutorError("uncorrelated worker receipt: feature/slice")
        if receipt["idempotency_key"] != key:
            raise ExecutorError("uncorrelated worker receipt: idempotency_key")
        if receipt["task"] != str(plan_lane["task"]):
            raise ExecutorError("uncorrelated worker receipt: task")

    @staticmethod
    def _project_worker_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
        fields = (
            "feature", "slice", "task", "worktree_id", "worktree_path", "branch", "pre_head", "run_id",
            "orchestration_task_id", "dispatch_id", "terminal_handle", "idempotency_key", "status",
        )
        return {field: receipt[field] for field in fields if field in receipt}

    def _validate_worktree_receipt(self, receipt: Mapping[str, Any], destination: Path, source_head: str) -> None:
        required = ("worktree_id", "worktree_path", "branch", "pre_head")
        if any(not isinstance(receipt.get(field), str) or not receipt[field] for field in required):
            raise ExecutorError("incomplete worktree receipt")
        if Path(str(receipt["worktree_path"])).resolve() != Path(destination).resolve():
            raise ExecutorError("uncorrelated worktree receipt: path")
        if receipt["pre_head"] != source_head:
            raise ExecutorError("uncorrelated worktree receipt: source head")

    def _release_lease_state(
        self, snapshot: Mapping[str, Any], state: dict[str, Any], lane_id: str, provider: ResourceProvider | None
    ) -> dict[str, Any]:
        lane = state["lanes"][lane_id]
        lease = lane.get("lease")
        if not isinstance(lease, dict) or not isinstance(lease.get("lease_id"), str):
            return {"released": False, "reason": "no-lease"}
        lease_id = lease["lease_id"]
        for other_lane_id, other_lane in state["lanes"].items():
            other_lease = other_lane.get("lease")
            if other_lane_id != lane_id and isinstance(other_lease, Mapping) and other_lease.get("lease_id") == lease_id:
                raise ExecutorError("foreign lease cleanup")
        if lease.get("released") is True:
            return {"released": True, "lease_id": lease_id, "idempotent": True}
        if provider is None:
            provider = self._provider(snapshot)
        if provider is None:
            raise ExecutorError("missing resource provider")
        key, action, created = self._record_action(state, lane_id, lane, "release")
        prior_receipt = action.get("receipt") if isinstance(action, Mapping) else None
        if (
            action.get("status") in {"accepted", "released"}
            and isinstance(prior_receipt, Mapping)
            and prior_receipt.get("lease_id") != lease_id
        ):
            key = idempotency_key(
                self.feature, str(lane["slice"]), str(lane["task"]), f"release-retry-{lease_id}", snapshot["git_head"]
            )
            action = state["actions"].get(key)
            created = action is None
            if action is None:
                action = {"key": key, "action": "release", "status": "pending", "lane": lane_id}
                state["actions"][key] = action
        self._save(state)
        if action["status"] in {"accepted", "released"}:
            lease["released"] = True
            self._save(state)
            return {"released": True, "lease_id": lease_id, "idempotent": True}
        request = {
            "repository": str(self.root),
            "feature": self.feature,
            "slice": lane["slice"],
            "task": lane["task"],
            "worktree": lane.get("worktree_path", ""),
            "idempotency_key": key,
            "resources": lane.get("resources", []),
        }
        try:
            if not created:
                receipt = self._reconcile_pending(provider, action)
                if receipt is None:
                    raise ExecutorError("unreconciled pending action: release")
            else:
                receipt = provider.release(request, lease_id)
            if receipt.get("lease_id") != lease_id or receipt.get("released") is not True:
                raise ExecutorError("resource release receipt is uncorrelated")
        except ExecutorError as exc:
            action["status"] = "failed"
            lane["fallback_reason"] = "cleanup-failed"
            self._save(state)
            raise ExecutorError("resource cleanup failed") from exc
        lease["released"] = True
        self._accept(action, external_id=receipt["lease_id"], receipt=dict(receipt))
        action["status"] = "released"
        self._save(state)
        return {"released": True, "lease_id": lease_id, "idempotent": False}

    def start(
        self,
        *,
        resume: bool = False,
        wait_seconds: float = 30,
        technical_verifier_receipts: Sequence[Mapping[str, Any]] | None = None,
    ) -> dict[str, Any]:
        snapshot = self._workflow()
        mode = snapshot["parallelization"]["mode"]
        if mode == "disabled":
            return _serial_result(
                self.feature,
                mode,
                "disabled-mode",
                [{"id": "serial", "slice": None, "task": None, "status": "ready", "sync_after": []}],
            )
        self._prepare_repository()
        plan = self._plan()
        lanes = list(plan.get("lanes", []))
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
        self._source_head = snapshot["git_head"]
        seen_slices: set[str] = set()
        provider: ResourceProvider | None = None
        destinations: dict[str, Path] = {}
        for plan_lane in lanes:
            slice_id = plan_lane.get("slice")
            if isinstance(slice_id, str):
                seen_slices.add(slice_id)
            lane_id = str(plan_lane.get("id", ""))
            try:
                destination = self._worktree_destination(plan_lane)
                destinations[lane_id] = bounded_path(_git_common_dir(self.root).parent.parent, destination)
            except (ExecutorError, PathBoundaryError):
                return _serial_result(self.feature, mode, "unsafe-worktree-path", lanes)
            resources = self._lane_resources(plan_lane)
            if resources is None:
                return _serial_result(self.feature, mode, "missing-resource-metadata", lanes)
            if resources and provider is None:
                try:
                    provider = self._provider(snapshot)
                except (ExecutorError, PathBoundaryError):
                    return _serial_result(self.feature, mode, "missing-resource-provider", lanes)
        if any(self._lane_resources(plan_lane) for plan_lane in lanes) and provider is None:
            return _serial_result(self.feature, mode, "missing-resource-provider", lanes)
        if self.adapter_factory is None:
            return _serial_result(self.feature, mode, "unsupported-adapter", lanes)
        try:
            adapter = self.adapter_factory()
            probe = getattr(adapter, "probe", None)
            if callable(probe):
                compatibility = probe()
                if not isinstance(compatibility, Mapping) or not _compatibility_is_usable(compatibility):
                    if isinstance(compatibility, Mapping):
                        return _adapter_fallback(self.feature, mode, compatibility, lanes)
                    return _serial_result(self.feature, mode, "adapter:malformed-compatibility", lanes)
        except Exception as exc:
            return _serial_result(self.feature, mode, "adapter:" + str(exc), lanes)
        actions: list[dict[str, Any]] = []
        slice_lane_ids: dict[str, list[str]] = {}
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
            prior_lane_ids = slice_lane_ids.setdefault(slice_id, [])
            if prior_lane_ids:
                prior_lane = state["lanes"].get(prior_lane_ids[-1])
                if prior_lane is None or prior_lane.get("state") not in {"complete", "failed", "serial"}:
                    prior_lane_ids.append(lane_id)
                    continue
            prior_lane_ids.append(lane_id)
            if existing is None:
                state["lanes"][lane_id] = {"slice": slice_id, "task": task_id, "state": "ready", "resources": resources}
                existing = state["lanes"][lane_id]
            elif existing.get("slice") != slice_id or existing.get("task") != task_id:
                return _serial_result(self.feature, mode, "mismatched-lane-receipt", lanes)
            if existing.get("state") in {"invalidated", "gate_required"} and not self._consume_gate(state, lane_id, existing):
                self._save(state)
                result = {"version": 1, "feature": self.feature, "mode": mode, "fallback": False, "state": state, "actions": []}
                return result
            release_key = idempotency_key(self.feature, slice_id, task_id, "release", state["source_git_head"])
            if release_key in state["actions"] and state["actions"][release_key].get("status") == "pending":
                try:
                    self._release_lease_state(snapshot, state, lane_id, provider)
                except ExecutorError:
                    existing["fallback_reason"] = "cleanup-failed"
                    if existing["state"] in {"ready", "running"}:
                        transition_lane(state, lane_id, "serial", expected=existing["state"])
                    self._save(state)
                    return _serial_result(self.feature, mode, "cleanup-failed", lanes)
            worker_key = idempotency_key(self.feature, slice_id, task_id, "worker", state["source_git_head"])
            pending_worker_retry = (
                resume
                and existing["state"] == "serial"
                and isinstance(state["actions"].get(worker_key), Mapping)
                and state["actions"][worker_key].get("status") == "pending"
                and isinstance(state["actions"][worker_key].get("partial_effect"), Mapping)
            )
            if pending_worker_retry:
                transition_lane(state, lane_id, "ready", expected="serial")
                if resources:
                    retry_acquire_created = False
                    retry_key = existing.get("retry_acquire_key")
                    retry_action = state["actions"].get(retry_key) if isinstance(retry_key, str) else None
                    if not isinstance(retry_action, Mapping) or retry_action.get("status") in {"accepted", "released"}:
                        attempt = int(existing.get("resource_retry_attempt", 0)) + 1
                        retry_key = idempotency_key(
                            self.feature, slice_id, task_id, f"acquire-retry-{attempt}", state["source_git_head"]
                        )
                        retry_action = {
                            "key": retry_key, "action": "acquire", "status": "pending", "lane": lane_id,
                        }
                        state["actions"][retry_key] = retry_action
                        existing["resource_retry_attempt"] = attempt
                        existing["retry_acquire_key"] = retry_key
                        retry_acquire_created = True
                        self._save(state)
            else:
                retry_acquire_created = False
            if existing["state"] in {"complete", "failed", "serial"}:
                continue
            worktree_key, worktree_action, worktree_created = self._record_action(state, lane_id, existing, "worktree")
            self._save(state)
            if worktree_action["status"] == "pending":
                try:
                    if not worktree_created:
                        receipt = self._reconcile_pending(adapter, worktree_action)
                        if receipt is None:
                            raise ExecutorError("unreconciled pending action: worktree")
                    else:
                        receipt = self._create_worktree(destinations[lane_id])
                    if not isinstance(receipt, Mapping):
                        raise ExecutorError("malformed worktree receipt")
                    self._validate_worktree_receipt(receipt, destinations[lane_id], state["source_git_head"])
                    bounded_path(_git_common_dir(self.root).parent.parent, receipt["worktree_path"])
                    self._accept(worktree_action, external_id=receipt.get("worktree_id"), receipt=dict(receipt))
                    existing.update({key: receipt[key] for key in ("worktree_id", "gitdir", "worktree_path", "branch", "pre_head") if key in receipt})
                except Exception as exc:
                    existing["fallback_reason"] = "worktree:" + str(exc)
                    if existing["state"] in {"ready", "running"}:
                        transition_lane(state, lane_id, "serial", expected=existing["state"])
                    self._save(state)
                    return _serial_result(self.feature, mode, "unreconciled-pending" if not worktree_created else "worktree-failed", lanes)
            if plan_lane.get("sync_after"):
                try:
                    sync_status = self._sync_lane(state, lane_id, plan_lane, existing)
                except Exception as exc:
                    existing["fallback_reason"] = "checkpoint:" + str(exc)
                    if existing["state"] in {"ready", "running", "waiting"}:
                        transition_lane(state, lane_id, "serial", expected=existing["state"])
                    self._save(state)
                    try:
                        self._cleanup_rejected_worktree(state, lane_id, existing)
                    except ExecutorError:
                        existing["fallback_reason"] = "cleanup-failed"
                        self._save(state)
                        return _serial_result(self.feature, mode, "cleanup-failed", lanes)
                    result = _serial_result(self.feature, mode, "checkpoint-failed", lanes)
                    result["state"] = state
                    return result
                if sync_status == "serial":
                    try:
                        self._cleanup_rejected_worktree(state, lane_id, existing)
                    except ExecutorError:
                        existing["fallback_reason"] = "cleanup-failed"
                        self._save(state)
                        return _serial_result(self.feature, mode, "cleanup-failed", lanes)
                    result = _serial_result(self.feature, mode, existing.get("fallback_reason", "checkpoint-failed"), lanes)
                    result["state"] = state
                    return result
                if sync_status == "blocked":
                    return {"version": 1, "feature": self.feature, "mode": mode, "fallback": False, "state": state, "actions": []}
            if resume and existing.get("state") in {"running", "waiting"}:
                worker_key = idempotency_key(self.feature, slice_id, task_id, "worker", state["source_git_head"])
                worker_action = state["actions"].get(worker_key)
                if isinstance(worker_action, Mapping) and worker_action.get("status") in {"accepted", "released"}:
                    if not callable(getattr(adapter, "wait_events", None)):
                        continue
                    if self._resume_worker_event(snapshot, state, lane_id, plan_lane, existing, adapter, provider, wait_seconds) == "serial":
                        result = _serial_result(self.feature, mode, existing.get("fallback_reason", "worker-failed"), lanes)
                        result["state"] = state
                        return result
                    continue
            if resources:
                if provider is None:
                    existing["fallback_reason"] = "missing-resource-provider"
                    transition_lane(state, lane_id, "serial")
                    self._save(state)
                    return _serial_result(self.feature, mode, "missing-resource-provider", lanes)
                retry_key = existing.get("retry_acquire_key") if pending_worker_retry else None
                retry_action = state["actions"].get(retry_key) if isinstance(retry_key, str) else None
                if isinstance(retry_key, str) and isinstance(retry_action, dict):
                    acquire_key, acquire_action, acquire_created = retry_key, retry_action, retry_acquire_created
                else:
                    acquire_key, acquire_action, acquire_created = self._record_action(state, lane_id, existing, "acquire")
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
                        live = {
                            other_lane.get("lease", {}).get("lease_id")
                            for other_lane_id, other_lane in state["lanes"].items()
                            if other_lane_id != lane_id and isinstance(other_lane.get("lease"), Mapping)
                        }
                        if not acquire_created:
                            recovered = self._reconcile_pending(provider, acquire_action)
                            if recovered is None:
                                raise ExecutorError("unreconciled pending action: acquire")
                            lease = normalize_lease_receipt(recovered, request, {item for item in live if isinstance(item, str)})
                        else:
                            acquired = provider.acquire(request, {item for item in live if isinstance(item, str)})
                            lease = normalize_lease_receipt(acquired, request, {item for item in live if isinstance(item, str)})
                        existing["lease"] = lease
                        self._accept(acquire_action, external_id=lease["lease_id"], receipt=lease)
                    except ExecutorError as exc:
                        existing["fallback_reason"] = str(exc)
                        transition_lane(state, lane_id, "serial")
                        self._save(state)
                        return _serial_result(self.feature, mode, "resource-acquire-failed", lanes)
            worker_key, worker_action, worker_created = self._record_action(state, lane_id, existing, "worker")
            worker_action["worker_plan"] = dict(plan_lane)
            worker_action["worktree_receipt"] = {
                key: existing[key]
                for key in ("worktree_id", "gitdir", "worktree_path", "branch", "pre_head")
                if key in existing
            }
            self._save(state)
            if worker_action["status"] == "pending":
                try:
                    if not worker_created:
                        receipt = self._reconcile_pending(adapter, worker_action)
                        if receipt is None:
                            raise ExecutorError("unreconciled pending action: worker")
                    else:
                        receipt = adapter.start_worker(dict(plan_lane), dict(existing), idempotency_key=worker_key)
                    if not isinstance(receipt, Mapping):
                        raise ExecutorError("malformed worker receipt")
                    self._validate_worker_receipt(receipt, existing, plan_lane, worker_key, state["source_git_head"])
                    receipt = self._project_worker_receipt(receipt)
                    self._accept(worker_action, external_id=receipt.get("dispatch_id"), receipt=dict(receipt))
                    for key in ("run_id", "orchestration_task_id", "dispatch_id", "terminal_handle"):
                        if key in receipt:
                            existing[key] = receipt[key]
                    if existing["state"] == "ready":
                        transition_lane(state, lane_id, "running", expected="ready")
                    actions.append({"action": "worker", "lane": lane_id, "key": worker_key})
                except Exception as exc:
                    details = getattr(exc, "details", None)
                    if isinstance(details, Mapping):
                        previous = worker_action.get("partial_effect")
                        merged = dict(previous) if isinstance(previous, Mapping) else {}
                        for key, value in details.items():
                            if key in {"run_id", "task_id", "orchestration_task_id", "dispatch_id"}:
                                if isinstance(value, str) and value:
                                    merged[key] = value
                            else:
                                merged[key] = value
                        worker_action["partial_effect"] = merged
                    worker_action["error"] = str(exc)
                    existing["fallback_reason"] = "worker:" + str(exc)
                    transition_lane(state, lane_id, "serial")
                    self._save(state)
                    if existing.get("lease") is not None:
                        try:
                            self._release_lease_state(snapshot, state, lane_id, provider)
                        except ExecutorError:
                            return _serial_result(self.feature, mode, "cleanup-failed", lanes)
                    result = _serial_result(self.feature, mode, "worker-failed", lanes)
                    result["state"] = state
                    result["actions"] = [{"action": "worker", "lane": lane_id, "key": worker_key}]
                    if isinstance(worker_action.get("partial_effect"), Mapping):
                        result["partial_effects"] = dict(worker_action["partial_effect"])
                    return result
                self._save(state)
                terminal = receipt.get("terminal") is True or receipt.get("status") in {
                    "accepted", "complete", "halted", "abandoned", "failed"
                }
                if terminal and existing.get("lease") is not None:
                    try:
                        self._release_lease_state(snapshot, state, lane_id, provider)
                    except ExecutorError:
                        return _serial_result(self.feature, mode, "cleanup-failed", lanes)
                if terminal and existing["state"] == "running":
                    if mode == "full" and not isinstance(existing.get("current_head"), str):
                        try:
                            self._record_producer_head(state, lane_id, existing)
                        except ExecutorError as exc:
                            existing["fallback_reason"] = "producer-head:" + str(exc)
                            transition_lane(state, lane_id, "serial", expected="running")
                            self._save(state)
                            return _serial_result(self.feature, mode, "producer-head-failed", lanes)
                    transition_lane(state, lane_id, "complete", expected="running")
        self._consume_technical_verifier_receipts(state, technical_verifier_receipts)
        integration_status = self._integrate_verified_slices(state, plan)
        if integration_status == "serial":
            result = _serial_result(self.feature, mode, state.get("integration_recovery", {}).get("reason", "integration-failed"), lanes)
            result["state"] = state
            return result
        if integration_status == "unverified":
            return _serial_result(self.feature, mode, "integration-unverified", lanes)
        self._save(state)
        return {"version": 1, "feature": self.feature, "mode": mode, "fallback": False, "state": state, "actions": actions}

    def release_lane(self, lane_id: str) -> dict[str, Any]:
        snapshot = self._workflow()
        self._prepare_repository()
        state = self._load_state(snapshot)
        if state is None or lane_id not in state["lanes"]:
            raise ExecutorError("unknown lane")
        return self._release_lease_state(snapshot, state, lane_id, None)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("start", "resume", "status", "preflight"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--feature", required=True)
    parser.add_argument("--adapter", choices=("auto", "orca", "maestri"), default="auto")
    parser.add_argument("--canary", action="store_true")
    parser.add_argument("--wait-seconds", type=_wait_seconds, default=30.0)
    parser.add_argument("--technical-verifier-receipt", action="append", type=Path, default=[])
    return parser


def _wait_seconds(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("wait-seconds must be a number") from exc
    if not 1 <= parsed <= 3600:
        raise argparse.ArgumentTypeError("wait-seconds must be between 1 and 3600")
    return parsed


def _adapter_factory(name: str, root: Path, feature: str) -> Callable[[], Any] | None:
    maestri_selected = name == "maestri" or (name == "auto" and bool(os.environ.get("MAESTRI_SOCKET")))
    if maestri_selected:
        if shutil.which("maestri") is None:
            return None
        try:
            import maestri_adapter  # type: ignore[import-not-found]
        except ImportError:
            return None
        factory = getattr(maestri_adapter, "Adapter", None) or getattr(maestri_adapter, "MaestriAdapter", None)
        if factory is None:
            return None
        return lambda: factory(root=root, feature=feature)
    if name not in {"auto", "orca"}:
        return None
    if shutil.which("orca") is None:
        return None
    try:
        import orca_adapter  # type: ignore[import-not-found]
    except ImportError:
        return None
    if getattr(orca_adapter, "CAPABILITY", None) != "orchestration.contract.v1":
        return None
    factory = getattr(orca_adapter, "Adapter", None) or getattr(orca_adapter, "OrcaAdapter", None)
    if factory is None:
        return None
    return lambda: factory(root=root, feature=feature)


def main(
    argv: list[str] | None = None,
    *,
    adapter_factory: Callable[[], Any] | None = None,
    git_adapter_factory: Callable[[], Any] | None = None,
) -> int:
    args = _parser().parse_args(argv)
    try:
        selected_adapter_factory = adapter_factory
        if selected_adapter_factory is None and args.command != "status":
            selected_adapter_factory = _adapter_factory(args.adapter, args.root, args.feature)
        coordinator = Coordinator(
            args.root,
            args.feature,
            adapter_factory=None if args.command == "status" else selected_adapter_factory,
            git_adapter_factory=git_adapter_factory,
        )
        if args.command == "status":
            result = coordinator.status()
        elif args.command == "preflight":
            result = coordinator.preflight(adapter=args.adapter, canary=args.canary)
        else:
            receipts: list[Mapping[str, Any]] = []
            for receipt_path in args.technical_verifier_receipt:
                payload = json.loads(receipt_path.read_text(encoding="utf-8"))
                if not isinstance(payload, Mapping):
                    raise ExecutorError("technical verifier receipt must be an object")
                receipts.append(payload)
            result = coordinator.start(
                resume=args.command == "resume",
                wait_seconds=args.wait_seconds,
                technical_verifier_receipts=receipts,
            )
        result = {**result, "command": args.command}
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ExecutorError, OSError, subprocess.SubprocessError) as exc:
        print(f"parallel executor: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
