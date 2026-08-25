"""Spec-derived tests for the parallel slice executor coordinator."""

from __future__ import annotations

import json
import io
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents/skills/autonomous/scripts"))
import parallel_execute
import orca_adapter


def fake_git_worktree(destination: Path, source_head: str) -> dict[str, str]:
    return {
        "worktree_id": str(destination),
        "worktree_path": str(destination),
        "branch": "(detached)",
        "pre_head": source_head,
    }


_RealCoordinator = parallel_execute.Coordinator


class TestCoordinator(_RealCoordinator):
    def __init__(self, *args: object, **kwargs: object) -> None:
        original_factory = kwargs.get("adapter_factory")
        if callable(original_factory):
            def remember_adapter() -> object:
                adapter = original_factory()
                self._active_adapter = adapter
                return adapter

            kwargs["adapter_factory"] = remember_adapter
        kwargs.setdefault("worktree_creator", self._test_worktree_creator)
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]

    def _test_worktree_creator(self, destination: Path, source_head: str) -> dict[str, str]:
        adapter = getattr(self, "_active_adapter", None)
        observe = getattr(adapter, "observe_worktree", None)
        if callable(observe):
            return observe(destination, source_head)
        effect = getattr(adapter, "worktree_effect", None)
        if callable(effect):
            return effect(destination, source_head)
        return fake_git_worktree(destination, source_head)


parallel_execute.Coordinator = TestCoordinator  # type: ignore[assignment]


def make_repo(*, mode: str = "safe", feature: str = "fixture") -> Path:
    root = Path(tempfile.mkdtemp())
    feature_dir = root / ".specs" / "features" / feature
    feature_dir.mkdir(parents=True)
    (feature_dir / "tasks.md").write_text(
        "### T1: first\n**Status:** pending\n**Slice:** A\n**Where:** src/a.py\n**Depends on:** None\n\n"
        "### T2: second\n**Status:** pending\n**Slice:** B\n**Where:** src/b.py\n**Depends on:** None\n",
        encoding="utf-8",
    )
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
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return root


def test_state_rejects_out_of_order_and_duplicate_lane_transition() -> None:
    state = parallel_execute.new_runtime_state("repo", "fixture", "safe", "head")
    state["lanes"]["slice-A"] = {"slice": "A", "task": "T1", "state": "ready"}
    parallel_execute.transition_lane(state, "slice-A", "running", expected="ready")
    assert state["lanes"]["slice-A"]["state"] == "running"
    try:
        parallel_execute.transition_lane(state, "slice-A", "running", expected="ready")
    except parallel_execute.StateError as exc:
        assert "out-of-order" in str(exc)
    else:
        raise AssertionError("duplicate transition must be rejected")


def test_state_validation_rejects_foreign_and_malformed_state() -> None:
    state = parallel_execute.new_runtime_state("repo", "fixture", "safe", "head")
    for foreign in (
        {**state, "repository_id": "other"},
        {**state, "feature": "other"},
        {**state, "lanes": []},
        {**state, "version": 2},
    ):
        try:
            parallel_execute.validate_runtime_state(foreign, "repo", "fixture")
        except parallel_execute.StateError as exc:
            assert str(exc)
        else:
            raise AssertionError("invalid state must be rejected")


def test_runtime_state_path_is_git_common_state_not_versioned_feature_state() -> None:
    root = make_repo()
    try:
        path = parallel_execute.runtime_state_path(root, "fixture")
        common_value = subprocess.check_output(
            ["git", "rev-parse", "--git-common-dir"], cwd=root, text=True
        ).strip()
        common = (root / common_value if not Path(common_value).is_absolute() else Path(common_value)).resolve()
        assert common in path.parents
        assert ".specs" not in path.parts
    finally:
        shutil.rmtree(root)


def test_atomic_state_replacement_preserves_previous_on_pre_rename_failure() -> None:
    directory = Path(tempfile.mkdtemp())
    path = directory / "state.json"
    try:
        parallel_execute.atomic_write_json(path, {"version": 1, "status": "complete"})
        try:
            parallel_execute.atomic_write_json(
                path, {"version": 1, "status": "torn"}, before_replace=lambda: (_ for _ in ()).throw(RuntimeError("boom"))
            )
        except RuntimeError as exc:
            assert str(exc) == "boom"
        else:
            raise AssertionError("injected replacement failure must propagate")
        assert json.loads(path.read_text(encoding="utf-8")) == {"version": 1, "status": "complete"}
    finally:
        shutil.rmtree(directory)


def test_safe_argv_uses_no_shell_and_bounded_timeout() -> None:
    calls: list[dict[str, object]] = []

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append({"argv": argv, **kwargs})
        return subprocess.CompletedProcess(argv, 0, "ok", "")

    original = parallel_execute.subprocess.run
    parallel_execute.subprocess.run = fake_run  # type: ignore[assignment]
    try:
        result = parallel_execute.run_argv([sys.executable, "-c", "print('ok')", "$(touch pwned)"], timeout=3)
    finally:
        parallel_execute.subprocess.run = original  # type: ignore[assignment]
    assert result.returncode == 0
    assert calls[0]["shell"] is False
    assert calls[0]["timeout"] == 3
    assert calls[0]["argv"][-1] == "$(touch pwned)"


def test_bounded_path_rejects_escape_and_unsafe_symlink_before_write() -> None:
    root = Path(tempfile.mkdtemp())
    outside = Path(tempfile.mkdtemp())
    try:
        (root / "safe").mkdir()
        (root / "safe" / "link").symlink_to(outside, target_is_directory=True)
        for candidate in (root.parent / "outside", root / ".." / "escape", root / "safe" / "link" / "file"):
            try:
                parallel_execute.bounded_path(root, candidate)
            except parallel_execute.PathBoundaryError as exc:
                assert str(exc)
            else:
                raise AssertionError("unsafe path must be rejected")
    finally:
        shutil.rmtree(root)
        shutil.rmtree(outside)


def test_disabled_coordinator_returns_serial_without_constructing_adapter() -> None:
    root = make_repo(mode="disabled")
    try:
        constructed = False

        def factory() -> object:
            nonlocal constructed
            constructed = True
            return object()

        result = parallel_execute.Coordinator(root, "fixture", adapter_factory=factory).start()
        assert result["fallback"] is True
        assert result["reason"] == "disabled-mode"
        assert result["lanes"][0]["id"] == "serial"
        assert constructed is False
    finally:
        shutil.rmtree(root)


class RecordingAdapter:
    def __init__(self) -> None:
        self.effects: list[tuple[str, str]] = []

    def worktree_effect(self, destination: Path, source_head: str) -> dict[str, str]:
        self.effects.append(("worktree", str(destination)))
        return {
            "worktree_id": "wt-A",
            "worktree_path": str(destination),
            "branch": "slice/A",
            "pre_head": source_head,
        }

    def start_worker(self, lane: dict[str, object], receipt: dict[str, object], *, idempotency_key: str) -> dict[str, str]:
        self.effects.append(("worker", idempotency_key))
        return {
            "feature": "fixture",
            "slice": str(lane["slice"]),
            "worktree_id": str(receipt["worktree_id"]),
            "worktree_path": str(receipt["worktree_path"]),
            "branch": str(receipt["branch"]),
            "pre_head": str(receipt["pre_head"]),
            "run_id": "run-A",
            "orchestration_task_id": "task-A",
            "task": str(lane["task"]),
            "dispatch_id": "dispatch-A",
            "terminal_handle": "terminal-A",
            "idempotency_key": idempotency_key,
        }


def lane_plan(*, resources: list[str]) -> dict[str, object]:
    return {
        "fallback": False,
        "lanes": [
            {
                "id": "slice-A",
                "slice": "A",
                "task": "T1",
                "status": "ready",
                "sync_after": [],
                "resources": resources,
            }
        ],
    }


def test_restart_reconciles_accepted_effects_without_duplicate_keys_or_workers() -> None:
    root = make_repo()
    try:
        adapters: list[RecordingAdapter] = []

        def factory() -> RecordingAdapter:
            adapter = RecordingAdapter()
            adapters.append(adapter)
            return adapter

        first = parallel_execute.Coordinator(root, "fixture", adapter_factory=factory)
        first._plan = lambda: lane_plan(resources=[])  # type: ignore[method-assign]
        first_result = first.start()
        second = parallel_execute.Coordinator(root, "fixture", adapter_factory=factory)
        second._plan = lambda: lane_plan(resources=[])  # type: ignore[method-assign]
        second_result = second.start(resume=True)
        assert len(adapters[0].effects) == 2
        assert adapters[1].effects == []
        assert len(first_result["state"]["actions"]) == 2  # type: ignore[index]
        assert second_result["state"]["actions"] == first_result["state"]["actions"]  # type: ignore[index]
    finally:
        shutil.rmtree(root)


def test_worker_start_partial_orca_effect_is_durable_and_retry_reconciles_without_duplicate_run_task() -> None:
    root = make_repo()
    try:
        class PartialFailureAdapter(RecordingAdapter):
            def __init__(self) -> None:
                super().__init__()
                self.failed = True
                self.reconciled = False
                self.reconcile_attempts = 0

            def start_worker(self, lane: dict[str, object], receipt: dict[str, object], *, idempotency_key: str) -> dict[str, str]:
                if self.failed:
                    self.failed = False
                    raise orca_adapter.AdapterError("Orca command failed: selector_not_found", details={"code": "selector_not_found", "stage": "worker-start", "run_id": "run-A", "task_id": "task-A"})
                return super().start_worker(lane, receipt, idempotency_key=idempotency_key)

            def reconcile_action(self, action: dict[str, object]) -> dict[str, str] | None:
                assert action["partial_effect"]["run_id"] == "run-A"  # type: ignore[index]
                assert action["partial_effect"]["task_id"] == "task-A"  # type: ignore[index]
                self.reconcile_attempts += 1
                if self.reconcile_attempts == 1:
                    raise orca_adapter.AdapterError("retry still pending", details={"code": "retryable"})
                self.reconciled = True
                return self.start_worker(action["worker_plan"], action["worktree_receipt"], idempotency_key=str(action["key"]))  # type: ignore[arg-type,index]

        adapter = PartialFailureAdapter()
        first = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: adapter)
        first._plan = lambda: lane_plan(resources=[])  # type: ignore[method-assign]
        failed = first.start()
        assert failed["fallback"] is True
        assert failed["reason"] == "worker-failed", failed
        assert failed["actions"] and failed["actions"][0]["action"] == "worker"
        action = failed["state"]["actions"][failed["actions"][0]["key"]]  # type: ignore[index]
        assert action["status"] == "pending"
        assert action["partial_effect"]["code"] == "selector_not_found"
        second = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: adapter)
        second._plan = lambda: lane_plan(resources=[])  # type: ignore[method-assign]
        retried = second.start(resume=True)
        assert retried["fallback"] is True
        partial = retried["state"]["actions"][failed["actions"][0]["key"]]["partial_effect"]  # type: ignore[index]
        assert partial["code"] == "retryable"
        assert partial["run_id"] == "run-A" and partial["task_id"] == "task-A"
        third = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: adapter)
        third._plan = lambda: lane_plan(resources=[])  # type: ignore[method-assign]
        completed = third.start(resume=True)
        assert completed["fallback"] is False
        assert adapter.reconciled is True
    finally:
        shutil.rmtree(root)


class RecordingProvider:
    def __init__(self, *, lease_id: str = "lease-A") -> None:
        self.lease_id = lease_id
        self.acquires = 0
        self.releases = 0
        self.requests: list[dict[str, object]] = []

    def acquire(self, request: dict[str, object], live_lease_ids: set[str]) -> dict[str, object]:
        self.acquires += 1
        self.requests.append(dict(request))
        assert request["resources"] == ["port"]
        assert request["idempotency_key"] not in live_lease_ids
        return {
            "lease_id": self.lease_id,
            "idempotency_key": request["idempotency_key"],
            "resources": ["port"],
            "prepared_worktree": True,
            "environment_keys": ["PORT"],
            "environment": {"PORT": "<redacted>"},
            "released": False,
        }

    def release(self, request: dict[str, object], lease_id: str) -> dict[str, object]:
        self.releases += 1
        self.requests.append(dict(request))
        assert lease_id == self.lease_id
        return {"lease_id": lease_id, "released": True}


def test_none_resources_bypass_provider_and_resource_lane_requires_correlated_lease() -> None:
    root = make_repo()
    try:
        adapter = RecordingAdapter()
        provider_calls = 0

        def provider_factory(_: Path) -> RecordingProvider:
            nonlocal provider_calls
            provider_calls += 1
            return RecordingProvider()

        coordinator = parallel_execute.Coordinator(
            root, "fixture", adapter_factory=lambda: adapter, provider_factory=provider_factory
        )
        coordinator._plan = lambda: lane_plan(resources=[])  # type: ignore[method-assign]
        result = coordinator.start()
        assert result["fallback"] is False
        assert provider_calls == 0
        assert [effect[0] for effect in adapter.effects] == ["worktree", "worker"]

        resource_root = make_repo()
        provider_executable = resource_root / "provider"
        provider_executable.write_text("#!/bin/sh\n", encoding="utf-8")
        provider_executable.chmod(0o755)
        workflow = json.loads((resource_root / ".specs/features/fixture/workflow.json").read_text(encoding="utf-8"))
        workflow["parallelization"]["resource_provider"] = "provider"
        (resource_root / ".specs/features/fixture/workflow.json").write_text(json.dumps(workflow), encoding="utf-8")
        resource_provider = RecordingProvider()
        resource_coordinator = parallel_execute.Coordinator(
            resource_root,
            "fixture",
            adapter_factory=lambda: RecordingAdapter(),
            provider_factory=lambda _: resource_provider,
        )
        resource_coordinator._plan = lambda: lane_plan(resources=["port"])  # type: ignore[method-assign]
        resource_result = resource_coordinator.start()
        assert resource_result["fallback"] is False
        assert resource_provider.acquires == 1
        assert set(resource_provider.requests[0]) == {
            "repository", "feature", "slice", "task", "worktree", "idempotency_key", "resources"
        }
        assert resource_provider.requests[0]["repository"] == str(resource_root.resolve())
        assert resource_provider.requests[0]["feature"] == "fixture"
        assert resource_provider.requests[0]["slice"] == "A"
        assert resource_provider.requests[0]["task"] == "T1"
        assert resource_provider.requests[0]["worktree"] == resource_result["state"]["lanes"]["slice-A"]["worktree_path"]  # type: ignore[index]
        assert isinstance(resource_provider.requests[0]["idempotency_key"], str)
        lane = resource_result["state"]["lanes"]["slice-A"]  # type: ignore[index]
        assert lane["lease"]["prepared_worktree"] is True  # type: ignore[index]
        assert lane["lease"]["environment"]["PORT"] == "<redacted>"  # type: ignore[index]
    finally:
        shutil.rmtree(root)
        if "resource_root" in locals():
            shutil.rmtree(resource_root)


def test_partial_worker_retry_reacquires_fresh_resource_lease_before_reconcile() -> None:
    root = make_repo()
    resource_provider = RecordingProvider(lease_id="unused")
    resource_provider.lease_ids = ["lease-A", "lease-B"]  # type: ignore[attr-defined]
    original_acquire = resource_provider.acquire

    def fresh_acquire(request: dict[str, object], live_lease_ids: set[str]) -> dict[str, object]:
        result = original_acquire(request, live_lease_ids)
        result["lease_id"] = resource_provider.lease_ids[resource_provider.acquires - 1]  # type: ignore[attr-defined]
        return result

    resource_provider.acquire = fresh_acquire  # type: ignore[method-assign]
    def fresh_release(request: dict[str, object], lease_id: str) -> dict[str, object]:
        resource_provider.releases += 1
        return {"lease_id": lease_id, "released": True}
    resource_provider.release = fresh_release  # type: ignore[method-assign]
    workflow = json.loads((root / ".specs/features/fixture/workflow.json").read_text(encoding="utf-8"))
    workflow["parallelization"]["resource_provider"] = "provider"
    (root / ".specs/features/fixture/workflow.json").write_text(json.dumps(workflow), encoding="utf-8")
    (root / "provider").write_text("#!/bin/sh\n", encoding="utf-8")
    (root / "provider").chmod(0o755)

    class FailOnce(RecordingAdapter):
        def __init__(self) -> None:
            super().__init__()
            self.failed = False
            self.reconciles = 0

        def start_worker(self, lane: dict[str, object], receipt: dict[str, object], *, idempotency_key: str) -> dict[str, str]:
            if not self.failed:
                self.failed = True
                raise orca_adapter.AdapterError("worker failed", details={"run_id": "run-A", "task_id": "task-A"})
            result = super().start_worker(lane, receipt, idempotency_key=idempotency_key)
            result["status"] = "complete"
            return result

        def reconcile_action(self, action: dict[str, object]) -> dict[str, str] | None:
            self.reconciles += 1
            return self.start_worker(action["worker_plan"], action["worktree_receipt"], idempotency_key=str(action["key"]))  # type: ignore[arg-type,index]

    adapter = FailOnce()
    try:
        first = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: adapter, provider_factory=lambda _: resource_provider)
        first._plan = lambda: lane_plan(resources=["port"])  # type: ignore[method-assign]
        failed = first.start()
        assert failed["reason"] == "worker-failed", failed
        first_lease = failed["state"]["lanes"]["slice-A"]["lease"]  # type: ignore[index]
        assert first_lease["released"] is True  # type: ignore[index]
        second = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: adapter, provider_factory=lambda _: resource_provider)
        second._plan = lambda: lane_plan(resources=["port"])  # type: ignore[method-assign]
        retried = second.start(resume=True)
        assert retried["fallback"] is False, retried
        assert resource_provider.acquires == 2
        assert resource_provider.releases == 2, retried
        assert resource_provider.requests[0]["idempotency_key"] != resource_provider.requests[1]["idempotency_key"]
        assert adapter.reconciles == 1
        assert retried["state"]["lanes"]["slice-A"]["lease"]["lease_id"] == "lease-B"  # type: ignore[index]
    finally:
        shutil.rmtree(root)


def test_restart_reconciles_existing_pending_retry_acquire_without_duplicate_provider_effect() -> None:
    root = make_repo()
    workflow = json.loads((root / ".specs/features/fixture/workflow.json").read_text(encoding="utf-8"))
    workflow["parallelization"]["resource_provider"] = "provider"
    (root / ".specs/features/fixture/workflow.json").write_text(json.dumps(workflow), encoding="utf-8")
    (root / "provider").write_text("#!/bin/sh\n", encoding="utf-8")
    (root / "provider").chmod(0o755)

    class ReconcilingProvider:
        def __init__(self) -> None:
            self.acquires = 0
            self.reconciles = 0
            self.releases = 0

        def acquire(self, request: dict[str, object], live_lease_ids: set[str]) -> dict[str, object]:
            self.acquires += 1
            return {"lease_id": "lease-A", "idempotency_key": request["idempotency_key"], "resources": ["port"], "prepared_worktree": True, "environment_keys": ["PORT"], "environment": {"PORT": "<redacted>"}, "released": False}

        def reconcile_action(self, action: dict[str, object]) -> dict[str, object]:
            self.reconciles += 1
            return {"lease_id": "lease-B", "idempotency_key": action["key"], "resources": ["port"], "prepared_worktree": True, "environment_keys": ["PORT"], "environment": {"PORT": "<redacted>"}, "released": False}

        def release(self, request: dict[str, object], lease_id: str) -> dict[str, object]:
            self.releases += 1
            return {"lease_id": lease_id, "released": True}

    class FailingAdapter(RecordingAdapter):
        def __init__(self) -> None:
            super().__init__()
            self.failed = True

        def start_worker(self, lane: dict[str, object], receipt: dict[str, object], *, idempotency_key: str) -> dict[str, str]:
            if self.failed:
                self.failed = False
                raise orca_adapter.AdapterError("worker failed", details={"run_id": "run-A", "task_id": "task-A"})
            result = super().start_worker(lane, receipt, idempotency_key=idempotency_key)
            result["status"] = "complete"
            return result

        def reconcile_action(self, action: dict[str, object]) -> dict[str, str] | None:
            return self.start_worker(action["worker_plan"], action["worktree_receipt"], idempotency_key=str(action["key"]))  # type: ignore[arg-type,index]

    provider = ReconcilingProvider()
    adapter = FailingAdapter()
    try:
        first = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: adapter, provider_factory=lambda _: provider)
        first._plan = lambda: lane_plan(resources=["port"])  # type: ignore[method-assign]
        failed = first.start()
        assert failed["reason"] == "worker-failed"
        state_path = parallel_execute.runtime_state_path(root, "fixture")
        state = json.loads(state_path.read_text(encoding="utf-8"))
        retry_key = parallel_execute.idempotency_key("fixture", "A", "T1", "acquire-retry-1", state["source_git_head"])
        state["lanes"]["slice-A"]["resource_retry_attempt"] = 1
        state["lanes"]["slice-A"]["retry_acquire_key"] = retry_key
        state["actions"][retry_key] = {"key": retry_key, "action": "acquire", "status": "pending", "lane": "slice-A"}
        parallel_execute.atomic_write_json(state_path, state)
        resumed = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: adapter, provider_factory=lambda _: provider)
        resumed._plan = lambda: lane_plan(resources=["port"])  # type: ignore[method-assign]
        result = resumed.start(resume=True)
        assert result["fallback"] is False
        assert provider.acquires == 1 and provider.reconciles == 1
        assert result["state"]["actions"][retry_key]["status"] == "accepted"  # type: ignore[index]
    finally:
        shutil.rmtree(root)


def test_resource_cleanup_is_owned_and_idempotent() -> None:
    root = make_repo()
    try:
        provider_executable = root / "provider"
        provider_executable.write_text("#!/bin/sh\n", encoding="utf-8")
        provider_executable.chmod(0o755)
        workflow = json.loads((root / ".specs/features/fixture/workflow.json").read_text(encoding="utf-8"))
        workflow["parallelization"]["resource_provider"] = "provider"
        (root / ".specs/features/fixture/workflow.json").write_text(json.dumps(workflow), encoding="utf-8")
        provider = RecordingProvider()
        coordinator = parallel_execute.Coordinator(
            root, "fixture", adapter_factory=lambda: RecordingAdapter(), provider_factory=lambda _: provider
        )
        coordinator._plan = lambda: lane_plan(resources=["port"])  # type: ignore[method-assign]
        coordinator.start()
        state = json.loads(coordinator.state_path.read_text(encoding="utf-8"))
        state["lanes"]["slice-B"] = {
            "slice": "B",
            "task": "T2",
            "state": "running",
            "resources": ["port"],
            "lease": dict(state["lanes"]["slice-A"]["lease"]),
        }
        parallel_execute.atomic_write_json(coordinator.state_path, state)
        try:
            coordinator.release_lane("slice-A")
        except parallel_execute.ExecutorError as exc:
            assert "duplicate live lease" in str(exc)
        else:
            raise AssertionError("foreign lease cleanup must be rejected")
        state["lanes"].pop("slice-B")
        parallel_execute.atomic_write_json(coordinator.state_path, state)
        first = coordinator.release_lane("slice-A")
        second = coordinator.release_lane("slice-A")
        assert first["released"] is True
        assert second["idempotent"] is True
        assert provider.releases == 1
    finally:
        shutil.rmtree(root)


def test_resource_provider_rejects_malformed_duplicate_and_foreign_receipts() -> None:
    root = Path(tempfile.mkdtemp())
    try:
        provider_path = root / "provider"
        provider_path.write_text("#!/bin/sh\n", encoding="utf-8")
        provider_path.chmod(0o755)
        request = {"idempotency_key": "key-A", "resources": ["port"]}
        for payload in (
            {"lease_id": "lease-A", "resources": ["database"], "prepared_worktree": True, "environment": {}, "idempotency_key": "key-A"},
            {"lease_id": "lease-A", "resources": ["port"], "prepared_worktree": False, "environment": {}, "idempotency_key": "key-A"},
            {"lease_id": "lease-A", "resources": ["port"], "prepared_worktree": True, "environment": {}, "idempotency_key": "other"},
        ):
            class Completed:
                stdout = json.dumps(payload)

            provider = parallel_execute.ResourceProvider(
                root, provider_path, runner=lambda *args, **kwargs: Completed()
            )
            try:
                provider.acquire(request, set())
            except parallel_execute.ExecutorError as exc:
                assert "receipt" in str(exc)
            else:
                raise AssertionError("invalid provider receipt must be rejected")
        class CompletedMalformed:
            stdout = "not-json"

        provider = parallel_execute.ResourceProvider(
            root, provider_path, runner=lambda *args, **kwargs: CompletedMalformed()
        )
        try:
            provider.acquire(request, {"lease-A"})
        except parallel_execute.ExecutorError as exc:
            assert "malformed" in str(exc)
        else:
            raise AssertionError("malformed provider output must be rejected")
        class CompletedValid:
            stdout = json.dumps(
                {
                    "lease_id": "lease-A",
                    "resources": ["port"],
                    "prepared_worktree": True,
                    "environment": {"PORT": "secret"},
                    "idempotency_key": "key-A",
                }
            )

        provider = parallel_execute.ResourceProvider(
            root, provider_path, runner=lambda *args, **kwargs: CompletedValid()
        )
        try:
            provider.acquire(request, {"lease-A"})
        except parallel_execute.ExecutorError as exc:
            assert "receipt" in str(exc)
        else:
            raise AssertionError("live lease reuse must be rejected")
        calls: list[tuple[list[str], dict[str, object]]] = []

        def recording_runner(argv: list[str], **kwargs: object) -> object:
            calls.append((argv, kwargs))
            return CompletedValid()

        provider = parallel_execute.ResourceProvider(root, provider_path, runner=recording_runner)
        full_request = {
            "repository": str(root),
            "feature": "fixture",
            "slice": "A",
            "task": "T1",
            "worktree": str(root),
            "idempotency_key": "key-A",
            "resources": ["port"],
        }
        receipt = provider.acquire(full_request, set())
        assert receipt["lease_id"] == "lease-A"
        assert calls[0][0] == [str(provider.executable)]
        sent = json.loads(str(calls[0][1]["input"]))
        assert sent == {**full_request, "operation": "acquire"}
    finally:
        shutil.rmtree(root)


class TerminalAdapter(RecordingAdapter):
    def __init__(self, status: str = "accepted") -> None:
        super().__init__()
        self.status = status

    def start_worker(self, lane: dict[str, object], receipt: dict[str, object], *, idempotency_key: str) -> dict[str, str]:
        return {**super().start_worker(lane, receipt, idempotency_key=idempotency_key), "status": self.status}


class FailingProvider(RecordingProvider):
    def __init__(self, failure: str, *, fail_release: bool = False) -> None:
        super().__init__()
        self.failure = failure
        self.fail_release = fail_release

    def acquire(self, request: dict[str, object], live_lease_ids: set[str]) -> dict[str, object]:
        if self.failure:
            raise parallel_execute.ExecutorError(self.failure)
        return super().acquire(request, live_lease_ids)

    def release(self, request: dict[str, object], lease_id: str) -> dict[str, object]:
        self.releases += 1
        if self.fail_release:
            raise parallel_execute.ExecutorError("cleanup timeout")
        return super().release(request, lease_id)


def configure_provider(root: Path) -> None:
    provider_executable = root / "provider"
    provider_executable.write_text("#!/bin/sh\n", encoding="utf-8")
    provider_executable.chmod(0o755)
    workflow_path = root / ".specs/features/fixture/workflow.json"
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    workflow["parallelization"]["resource_provider"] = "provider"
    workflow_path.write_text(json.dumps(workflow), encoding="utf-8")


def test_resource_provider_failures_refuse_worker_and_report_serial_recovery() -> None:
    cases = [
        ("missing", None, "missing-resource-provider"),
        ("timeout", FailingProvider("provider timeout"), "resource-acquire-failed"),
        ("malformed", FailingProvider("malformed provider receipt"), "resource-acquire-failed"),
        ("duplicate", FailingProvider("duplicate live lease"), "resource-acquire-failed"),
    ]
    for _, provider, expected_reason in cases:
        root = make_repo()
        try:
            adapter = RecordingAdapter()
            if provider is not None:
                configure_provider(root)
            coordinator = parallel_execute.Coordinator(
                root, "fixture", adapter_factory=lambda: adapter, provider_factory=lambda _: provider  # type: ignore[arg-type]
            )
            coordinator._plan = lambda: lane_plan(resources=["port"])  # type: ignore[method-assign]
            result = coordinator.start()
            assert result["fallback"] is True
            assert result["reason"] == expected_reason
            assert [effect[0] for effect in adapter.effects].count("worker") == 0
        finally:
            shutil.rmtree(root)


def test_terminal_worker_states_release_accepted_lease_exactly_once() -> None:
    for status in ("accepted", "halted", "abandoned"):
        root = make_repo()
        try:
            configure_provider(root)
            provider = RecordingProvider()
            coordinator = parallel_execute.Coordinator(
                root, "fixture", adapter_factory=lambda: TerminalAdapter(status), provider_factory=lambda _: provider
            )
            coordinator._plan = lambda: lane_plan(resources=["port"])  # type: ignore[method-assign]
            result = coordinator.start()
            assert result["fallback"] is False
            assert provider.releases == 1
            lane = result["state"]["lanes"]["slice-A"]  # type: ignore[index]
            assert lane["lease"]["released"] is True  # type: ignore[index]
        finally:
            shutil.rmtree(root)


def test_cleanup_failure_is_serial_recovery_with_failed_cleanup_receipt() -> None:
    root = make_repo()
    try:
        configure_provider(root)
        provider = FailingProvider("", fail_release=True)
        coordinator = parallel_execute.Coordinator(
            root, "fixture", adapter_factory=lambda: TerminalAdapter("accepted"), provider_factory=lambda _: provider
        )
        coordinator._plan = lambda: lane_plan(resources=["port"])  # type: ignore[method-assign]
        result = coordinator.start()
        assert result["fallback"] is True
        assert result["reason"] == "cleanup-failed"
        assert provider.releases == 1
        state = json.loads(coordinator.state_path.read_text(encoding="utf-8"))
        assert any(action["action"] == "release" and action["status"] == "failed" for action in state["actions"].values())
    finally:
        shutil.rmtree(root)


def test_executor_cli_start_resume_status_emit_one_json_object_and_status_has_no_effect() -> None:
    root = make_repo(mode="disabled")
    try:
        script = Path(__file__).resolve().parent.parent / ".agents/skills/autonomous/scripts/parallel_execute.py"
        command = [sys.executable, str(script), "status", "--root", str(root), "--feature", "fixture"]
        status = subprocess.run(command, text=True, capture_output=True, check=True)
        assert len(status.stdout.splitlines()) == 1
        assert json.loads(status.stdout)["state"] is None
        assert json.loads(status.stdout)["command"] == "status"
        assert list((root / ".git").glob("parallel-slice-executor/*")) == []
        start = subprocess.run(
            [sys.executable, str(script), "start", "--root", str(root), "--feature", "fixture"],
            text=True,
            capture_output=True,
            check=True,
        )
        assert json.loads(start.stdout)["reason"] == "disabled-mode"
        assert json.loads(start.stdout)["command"] == "start"
        assert start.stderr == ""
        resume = subprocess.run(
            [sys.executable, str(script), "resume", "--root", str(root), "--feature", "fixture", "--wait-seconds", "1"],
            text=True,
            capture_output=True,
            check=True,
        )
        resumed = json.loads(resume.stdout)
        assert resumed["command"] == "resume"
        assert resumed["reason"] == "disabled-mode"
        assert resumed["fallback"] is True
    finally:
        shutil.rmtree(root)


def test_executor_cli_selects_orca_adapter_and_threads_non_default_wait_budget() -> None:
    root = make_repo()
    try:
        first = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter())
        first._plan = lambda: lane_plan(resources=[])  # type: ignore[method-assign]
        first.start()

        class TimeoutAdapter(RecordingAdapter):
            def __init__(self) -> None:
                super().__init__()
                self.waits: list[float] = []

            def wait_events(self, receipt: dict[str, object], *, timeout: float = 30) -> dict[str, object]:
                self.waits.append(timeout)
                return {"event": "timeout", "unchanged": True}

        adapter = TimeoutAdapter()
        selected: list[tuple[str, Path, str]] = []
        original_factory = parallel_execute._adapter_factory
        original_plan = parallel_execute.Coordinator._plan
        parallel_execute._adapter_factory = lambda name, root, feature: (selected.append((name, root, feature)) or (lambda: adapter))  # type: ignore[assignment]
        parallel_execute.Coordinator._plan = lambda self: lane_plan(resources=[])  # type: ignore[method-assign]
        stdout = io.StringIO()
        try:
            with redirect_stdout(stdout):
                exit_code = parallel_execute.main(["resume", "--root", str(root), "--feature", "fixture", "--adapter", "orca", "--wait-seconds", "7"])
        finally:
            parallel_execute._adapter_factory = original_factory  # type: ignore[assignment]
            parallel_execute.Coordinator._plan = original_plan  # type: ignore[method-assign]
        result = json.loads(stdout.getvalue())
        assert exit_code == 0
        assert selected[0][0] == "orca"
        assert selected[0][1].resolve() == root.resolve()
        assert selected[0][2] == "fixture"
        assert adapter.waits == [7.0]
        assert result["state"]["lanes"]["slice-A"]["state"] == "running"
        try:
            with redirect_stderr(io.StringIO()):
                parallel_execute.main(["resume", "--root", str(root), "--feature", "fixture", "--wait-seconds", "0"])
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError("out-of-range wait budget must be rejected")
    finally:
        shutil.rmtree(root)


def test_auto_adapter_requires_orca_runtime_and_contract_capability() -> None:
    import orca_adapter

    original_which = parallel_execute.shutil.which
    original_capability = getattr(orca_adapter, "CAPABILITY", None)
    try:
        parallel_execute.shutil.which = lambda _: None  # type: ignore[assignment]
        assert parallel_execute._adapter_factory("auto", Path("."), "fixture") is None
        parallel_execute.shutil.which = lambda _: "/usr/local/bin/orca"  # type: ignore[assignment]
        orca_adapter.CAPABILITY = "unsupported"  # type: ignore[attr-defined]
        assert parallel_execute._adapter_factory("auto", Path("."), "fixture") is None
        orca_adapter.CAPABILITY = "orchestration.contract.v1"  # type: ignore[attr-defined]
        assert parallel_execute._adapter_factory("auto", Path("."), "fixture") is not None
    finally:
        parallel_execute.shutil.which = original_which  # type: ignore[assignment]
        if original_capability is None:
            delattr(orca_adapter, "CAPABILITY")
        else:
            orca_adapter.CAPABILITY = original_capability


def test_auto_adapter_missing_capability_returns_serial_without_worktree_effect() -> None:
    root = make_repo()
    original_which = parallel_execute.shutil.which
    original_plan = parallel_execute.Coordinator._plan
    try:
        parallel_execute.shutil.which = lambda _: None  # type: ignore[assignment]
        parallel_execute.Coordinator._plan = lambda self: lane_plan(resources=[])  # type: ignore[method-assign]
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = parallel_execute.main(["start", "--root", str(root), "--feature", "fixture", "--adapter", "auto"])
        result = json.loads(stdout.getvalue())
        assert exit_code == 0
        assert result["fallback"] is True
        assert result["reason"] == "unsupported-adapter"
        assert not list(root.parent.glob(f".{root.name}-parallel-slices"))
    finally:
        parallel_execute.shutil.which = original_which  # type: ignore[assignment]
        parallel_execute.Coordinator._plan = original_plan  # type: ignore[method-assign]
        shutil.rmtree(root)


def test_executor_cli_safe_resume_reconciles_pending_worker_through_injected_adapter() -> None:
    root = make_repo()
    try:
        probe = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter())
        snapshot = probe._workflow()
        source_head = snapshot["git_head"]
        probe._prepare_repository()
        worker_key = parallel_execute.idempotency_key("fixture", "A", "T1", "worker", source_head)
        worktree_key = parallel_execute.idempotency_key("fixture", "A", "T1", "worktree", source_head)
        destination = parallel_execute.derive_worktree_destination(root, "fixture", "A", "T1")
        state = parallel_execute.new_runtime_state(str(root.resolve()), "fixture", "safe", source_head)
        state["lanes"]["slice-A"] = {
            "slice": "A",
            "task": "T1",
            "state": "running",
            "resources": [],
            "worktree_id": "wt-A",
            "worktree_path": str(destination),
            "branch": "slice/A",
            "pre_head": source_head,
        }
        state["actions"][worktree_key] = {
            "key": worktree_key,
            "action": "worktree",
            "status": "accepted",
            "lane": "slice-A",
            "external_id": "wt-A",
            "receipt": {
                "worktree_id": "wt-A",
                "worktree_path": str(destination),
                "branch": "slice/A",
                "pre_head": source_head,
            },
        }
        state["actions"][worker_key] = {
            "key": worker_key,
            "action": "worker",
            "status": "pending",
            "lane": "slice-A",
        }
        parallel_execute.atomic_write_json(probe.state_path, state)  # type: ignore[arg-type]

        class ResumeRecordingAdapter(RecordingAdapter):
            def __init__(self) -> None:
                super().__init__()
                self.reconciled: list[str] = []

            def reconcile_action(self, action: dict[str, object]) -> dict[str, str]:
                self.reconciled.append(str(action["action"]))
                return {
                    "feature": "fixture", "slice": "A",
                    "worktree_id": "wt-A", "worktree_path": str(destination), "branch": "slice/A", "pre_head": source_head,
                    "run_id": "run-A", "orchestration_task_id": "task-A", "task": "T1",
                    "dispatch_id": "dispatch-resumed", "terminal_handle": "terminal-A", "idempotency_key": str(action["key"]),
                    "status": "running",
                }

        adapter = ResumeRecordingAdapter()
        original_plan = parallel_execute.Coordinator._plan
        parallel_execute.Coordinator._plan = lambda self: lane_plan(resources=[])  # type: ignore[method-assign]
        stdout = io.StringIO()
        stderr = io.StringIO()
        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = parallel_execute.main(
                    ["resume", "--root", str(root), "--feature", "fixture"],
                    adapter_factory=lambda: adapter,
                )
        finally:
            parallel_execute.Coordinator._plan = original_plan  # type: ignore[method-assign]
        assert exit_code == 0
        assert stderr.getvalue() == ""
        lines = stdout.getvalue().splitlines()
        assert len(lines) == 1
        result = json.loads(lines[0])
        assert result["command"] == "resume"
        assert result["fallback"] is False
        assert result["state"]["lanes"]["slice-A"]["state"] == "running"
        assert result["state"]["actions"][worker_key]["status"] == "accepted"
        assert result["state"]["actions"][worker_key]["external_id"] == "dispatch-resumed"
        assert result["state"]["actions"][worker_key]["receipt"]["dispatch_id"] == "dispatch-resumed"
        assert adapter.reconciled == ["worker"]
        assert adapter.effects == []
    finally:
        shutil.rmtree(root)


def test_executor_resume_consumes_run_delivery_reads_accepts_then_releases_worker() -> None:
    root = make_repo()
    try:
        probe = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter())
        snapshot = probe._workflow()
        source_head = snapshot["git_head"]
        probe._prepare_repository()
        worker_key = parallel_execute.idempotency_key("fixture", "A", "T1", "worker", source_head)
        worktree_key = parallel_execute.idempotency_key("fixture", "A", "T1", "worktree", source_head)
        destination = parallel_execute.derive_worktree_destination(root, "fixture", "A", "T1")
        state = parallel_execute.new_runtime_state(str(root.resolve()), "fixture", "safe", source_head)
        state["lanes"]["slice-A"] = {
            "slice": "A", "task": "T1", "state": "running", "resources": [],
            "worktree_id": "wt-A", "worktree_path": str(destination), "branch": "slice/A", "pre_head": source_head,
            "run_id": "run-A", "orchestration_task_id": "task-A", "dispatch_id": "dispatch-A", "terminal_handle": "terminal-A",
        }
        state["actions"][worktree_key] = {
            "key": worktree_key, "action": "worktree", "status": "accepted", "lane": "slice-A",
            "external_id": "wt-A", "receipt": {"worktree_id": "wt-A", "worktree_path": str(destination), "branch": "slice/A", "pre_head": source_head},
        }
        state["actions"][worker_key] = {
            "key": worker_key, "action": "worker", "status": "accepted", "lane": "slice-A", "external_id": "dispatch-A",
            "receipt": {"run_id": "run-A", "orchestration_task_id": "task-A", "dispatch_id": "dispatch-A", "terminal_handle": "terminal-A", "worktree_id": "wt-A", "worktree_path": str(destination), "branch": "slice/A", "pre_head": source_head, "feature": "fixture", "slice": "A", "task": "T1", "idempotency_key": worker_key, "status": "running"},
        }
        parallel_execute.atomic_write_json(probe.state_path, state)  # type: ignore[arg-type]

        class LiveResumeAdapter(RecordingAdapter):
            def __init__(self, state_path: Path | None = None) -> None:
                super().__init__()
                self.calls: list[str] = []
                self.state_path = state_path

            def wait_events(self, receipt: dict[str, object], *, timeout: float = 30) -> dict[str, object]:
                self.calls.append("check")
                return {"event": "worker_done", "delivery_id": "delivery-A", "run_id": "run-A", "payload": {"taskId": "task-A", "dispatchId": "dispatch-A", "outcome": "succeeded"}}

            def read_worker(self, receipt: dict[str, object]) -> dict[str, object]:
                self.calls.append("read")
                return {"dispatch_id": "dispatch-A", "source": "terminal", "source_identity": "terminal-A", "provider": "codex", "transcript": "<redacted>", "cursor": "cursor-A", "status": "succeeded"}

            def accept_worker_done(self, receipt: dict[str, object], delivery: dict[str, object], output: dict[str, object]) -> dict[str, object]:
                self.calls.append("accept")
                return {**dict(receipt), "status": "accepted", "accepted": True}

            def ack_delivery(self, receipt: dict[str, object], delivery: dict[str, object]) -> dict[str, object]:
                if self.state_path is not None:
                    persisted = json.loads(self.state_path.read_text(encoding="utf-8"))
                    assert any(action["action"] == "worker_ack" and action["status"] == "pending" for action in persisted["actions"].values())
                self.calls.append("ack")
                return {"acknowledged": True, "delivery_id": "delivery-A"}

            def release(self, receipt: dict[str, object], result: dict[str, object] | None = None) -> dict[str, object]:
                if self.state_path is not None:
                    persisted = json.loads(self.state_path.read_text(encoding="utf-8"))
                    assert any(action["action"] == "worker_release" and action["status"] == "pending" for action in persisted["actions"].values())
                self.calls.append("release")
                return {"released": True, "dispatch_id": "dispatch-A"}

        adapter = LiveResumeAdapter(probe.state_path)
        class ResumeGit:
            def head(self, worktree: str, **_: object) -> str:
                assert worktree == str(destination)
                return source_head

        original_plan = parallel_execute.Coordinator._plan
        parallel_execute.Coordinator._plan = lambda self: lane_plan(resources=[])  # type: ignore[method-assign]
        stdout = io.StringIO()
        stderr = io.StringIO()
        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = parallel_execute.main(
                    ["resume", "--root", str(root), "--feature", "fixture"],
                    adapter_factory=lambda: adapter,
                    git_adapter_factory=lambda: ResumeGit(),
                )
        finally:
            parallel_execute.Coordinator._plan = original_plan  # type: ignore[method-assign]
        assert exit_code == 0
        assert stderr.getvalue() == ""
        result = json.loads(stdout.getvalue())
        assert result["fallback"] is False
        assert result["state"]["lanes"]["slice-A"]["state"] == "complete"
        assert result["state"]["lanes"]["slice-A"]["current_head"] == source_head
        assert adapter.calls == ["check", "read", "accept", "ack", "release"]
        worker_state = result["state"]["actions"][worker_key]
        assert worker_state["delivery"]["delivery_id"] == "delivery-A"
        assert worker_state["completion"]["delivery_id"] == "delivery-A"

        class RestartAdapter(LiveResumeAdapter):
            def wait_events(self, receipt: dict[str, object], *, timeout: float = 30) -> dict[str, object]:
                raise AssertionError("completed worker must not reread delivery after restart")

        restarted = RestartAdapter()
        out = io.StringIO()
        old_plan = parallel_execute.Coordinator._plan
        parallel_execute.Coordinator._plan = lambda self: lane_plan(resources=[])  # type: ignore[method-assign]
        try:
            with redirect_stdout(out):
                parallel_execute.main(["resume", "--root", str(root), "--feature", "fixture"], adapter_factory=lambda: restarted)
        finally:
            parallel_execute.Coordinator._plan = old_plan  # type: ignore[method-assign]
        restart_result = json.loads(out.getvalue())
        assert restart_result["state"]["lanes"]["slice-A"]["state"] == "complete"
        assert restarted.calls == []

        persisted = json.loads(probe.state_path.read_text(encoding="utf-8"))
        persisted["lanes"]["slice-A"]["state"] = "running"
        parallel_execute.atomic_write_json(probe.state_path, persisted)
        resumed_running = RestartAdapter()
        out = io.StringIO()
        old_plan = parallel_execute.Coordinator._plan
        parallel_execute.Coordinator._plan = lambda self: lane_plan(resources=[])  # type: ignore[method-assign]
        try:
            with redirect_stdout(out):
                parallel_execute.main(["resume", "--root", str(root), "--feature", "fixture"], adapter_factory=lambda: resumed_running)
        finally:
            parallel_execute.Coordinator._plan = old_plan  # type: ignore[method-assign]
        exact_shape_result = json.loads(out.getvalue())
        assert exact_shape_result["state"]["lanes"]["slice-A"]["state"] == "complete"
        assert resumed_running.calls == []
    finally:
        shutil.rmtree(root)


def test_executor_resume_delivery_outcomes_are_timeout_waiting_or_serial_without_release() -> None:
    original_plan = parallel_execute.Coordinator._plan
    parallel_execute.Coordinator._plan = lambda self: lane_plan(resources=[])  # type: ignore[method-assign]
    try:
        for expected_event, expected_state, expected_fallback in (
            ("timeout", "running", False),
            ("waiting", "waiting", False),
            ("escalation", "serial", True),
            ("invalid", "serial", True),
            ("missing", "serial", True),
            ("duplicate", "serial", True),
        ):
            root = make_repo()
            try:
                first = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter())
                first.start()

                class OutcomeAdapter(RecordingAdapter):
                    def __init__(self) -> None:
                        super().__init__()
                        self.calls: list[str] = []

                    def wait_events(self, receipt: dict[str, object], *, timeout: float = 30) -> dict[str, object]:
                        self.calls.append("wait")
                        if expected_event == "timeout":
                            return {"event": "timeout", "unchanged": True}
                        if expected_event == "waiting":
                            return {"event": "waiting", "status": "clean", "dependency": "producer-A", "payload": {"environment": {"TOKEN": "<redacted>"}}}
                        if expected_event in {"invalid", "missing", "duplicate"}:
                            raise parallel_execute.ExecutorError(expected_event + " delivery")
                        return {"event": "escalation"}

                    def end_waiter(self, receipt: dict[str, object], waiter: dict[str, object]) -> dict[str, object]:
                        self.calls.append("end_waiter")
                        return {"ended": True, "terminal_handle": "terminal-A"}

                    def release(self, receipt: dict[str, object], result: dict[str, object] | None = None) -> dict[str, object]:
                        self.calls.append("release")
                        return {"released": True, "dispatch_id": "dispatch-A"}

                adapter = OutcomeAdapter()
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    exit_code = parallel_execute.main(["resume", "--root", str(root), "--feature", "fixture"], adapter_factory=lambda: adapter)
                result = json.loads(stdout.getvalue())
                assert exit_code == 0
                assert result["fallback"] is expected_fallback
                if expected_fallback:
                    assert result["reason"].startswith("worker:")
                    assert result["state"]["lanes"]["slice-A"]["state"] == expected_state
                else:
                    assert result["state"]["lanes"]["slice-A"]["state"] == expected_state
                    if expected_event == "waiting":
                        serialized = json.dumps(result["state"]["lanes"]["slice-A"]["waiter"])
                        assert "<redacted>" in serialized
                        assert "secret" not in serialized
                assert adapter.calls == (["wait", "end_waiter"] if expected_event == "waiting" else ["wait"])
            finally:
                shutil.rmtree(root)
    finally:
        parallel_execute.Coordinator._plan = original_plan  # type: ignore[method-assign]


def test_executor_waiter_persists_end_before_restart_follow_up_on_same_terminal() -> None:
    root = make_repo()
    original_plan = parallel_execute.Coordinator._plan
    parallel_execute.Coordinator._plan = lambda self: lane_plan(resources=[])  # type: ignore[method-assign]
    try:
        first = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter())
        first.start()

        class WaiterAdapter(RecordingAdapter):
            def __init__(self, phase: str) -> None:
                super().__init__()
                self.phase = phase
                self.calls: list[tuple[str, str]] = []

            def wait_events(self, receipt: dict[str, object], *, timeout: float = 30) -> dict[str, object]:
                self.calls.append(("wait", str(receipt["terminal_handle"])))
                if self.phase == "waiting":
                    return {"event": "waiting", "status": "clean", "dependency": "producer-A", "payload": {"environment": {"TOKEN": "<redacted>"}}}
                return {"event": "dependency", "status": "complete", "dependency": "producer-A"}

            def end_waiter(self, receipt: dict[str, object], waiter: dict[str, object]) -> dict[str, object]:
                self.calls.append(("end_waiter", str(receipt["terminal_handle"])))
                return {"ended": True, "terminal_handle": str(receipt["terminal_handle"])}

            def follow_up(self, receipt: dict[str, object], waiter: dict[str, object], dependency: dict[str, object], *, idempotency_key: str | None = None) -> dict[str, object]:
                self.calls.append(("follow_up", str(receipt["terminal_handle"])))
                return {
                    "feature": "fixture", "slice": "A",
                    "worktree_id": receipt["worktree_id"], "worktree_path": receipt["worktree_path"], "branch": receipt["branch"], "pre_head": receipt["pre_head"],
                    "run_id": receipt["run_id"], "orchestration_task_id": receipt["orchestration_task_id"], "task": receipt["task"],
                    "dispatch_id": "dispatch-follow-up", "terminal_handle": receipt["terminal_handle"], "idempotency_key": idempotency_key, "status": "running",
                }

        waiting_adapter = WaiterAdapter("waiting")
        out = io.StringIO()
        with redirect_stdout(out):
            parallel_execute.main(["resume", "--root", str(root), "--feature", "fixture"], adapter_factory=lambda: waiting_adapter)
        waiting_result = json.loads(out.getvalue())
        assert waiting_result["state"]["lanes"]["slice-A"]["state"] == "waiting"
        assert waiting_result["state"]["lanes"]["slice-A"]["waiter"]["ended"] is True
        assert waiting_adapter.calls == [("wait", "terminal-A"), ("end_waiter", "terminal-A")]

        follow_adapter = WaiterAdapter("dependency")
        out = io.StringIO()
        with redirect_stdout(out):
            parallel_execute.main(["resume", "--root", str(root), "--feature", "fixture"], adapter_factory=lambda: follow_adapter)
        follow_result = json.loads(out.getvalue())
        assert follow_result["state"]["lanes"]["slice-A"]["state"] == "running"
        assert follow_adapter.calls == [("wait", "terminal-A"), ("follow_up", "terminal-A")]
        assert "secret" not in json.dumps(waiting_result["state"])
    finally:
        parallel_execute.Coordinator._plan = original_plan  # type: ignore[method-assign]
        shutil.rmtree(root)


def test_waiting_dependency_checkpoint_blocks_then_follows_up_once_after_correlated_gate() -> None:
    root = make_repo()
    original_plan = parallel_execute.Coordinator._plan
    try:
        first = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter())
        first._plan = lambda: lane_plan(resources=[])  # type: ignore[method-assign]
        first.start()
        state = json.loads(first.state_path.read_text(encoding="utf-8"))
        lane = state["lanes"]["slice-A"]
        lane["state"] = "waiting"
        lane["waiter"] = {"event": "waiting", "status": "clean", "dependency": "producer-A", "ended": True}
        state["lanes"]["producer"] = {
            "slice": "P", "task": "T0", "state": "complete", "resources": [], "current_head": state["source_git_head"]
        }
        parallel_execute.atomic_write_json(first.state_path, state)
        plan = {
            "fallback": False,
            "lanes": [{"id": "slice-A", "slice": "A", "task": "T1", "status": "follow_up", "sync_after": ["T0"], "declared_paths": ["producer.txt"], "resources": []}],
        }

        class WaitingCheckpointAdapter(RecordingAdapter):
            def __init__(self, state_path: Path) -> None:
                super().__init__()
                self.state_path = state_path
                self.calls: list[tuple[str, str]] = []

            def sync_checkpoint(self, consumer: Path, producer: str, *, declared_paths: list[str] | None = None, expected_receipt: dict[str, object] | None = None) -> dict[str, object]:
                assert declared_paths == ["producer.txt"]
                current = json.loads(self.state_path.read_text(encoding="utf-8"))["source_git_head"]
                return {
                    "status": "synced", "changed": True, "producer_commit": producer, "pre_head": current, "post_head": "waiting-checkpoint-head",
                    "changed_paths": ["producer.txt"], "invalidated_evidence": ["gate", "technical_verifier", "deep_review"],
                }

            def wait_events(self, receipt: dict[str, object], *, timeout: float = 30) -> dict[str, object]:
                self.calls.append(("wait", str(receipt["terminal_handle"])))
                return {"event": "dependency", "status": "complete", "dependency": "producer-A"}

            def follow_up(self, receipt: dict[str, object], waiter: dict[str, object], dependency: dict[str, object], *, idempotency_key: str | None = None) -> dict[str, object]:
                self.calls.append(("follow_up", str(receipt["terminal_handle"])))
                return {
                    "feature": "fixture", "slice": "A", "worktree_id": receipt["worktree_id"],
                    "worktree_path": receipt["worktree_path"], "branch": receipt["branch"], "pre_head": receipt["pre_head"],
                    "run_id": receipt["run_id"], "orchestration_task_id": receipt["orchestration_task_id"], "task": receipt["task"],
                    "dispatch_id": "dispatch-follow-up", "terminal_handle": receipt["terminal_handle"],
                    "idempotency_key": idempotency_key, "status": "running",
                }

        adapter = WaitingCheckpointAdapter(first.state_path)
        blocked = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: adapter, git_adapter_factory=lambda: adapter)
        blocked._plan = lambda: plan  # type: ignore[method-assign]
        blocked_result = blocked.start(resume=True)
        blocked_lane = blocked_result["state"]["lanes"]["slice-A"]
        assert blocked_lane["state"] == "gate_required"
        assert blocked_lane["current_head"] == "waiting-checkpoint-head"
        assert adapter.calls == []

        waiting = parallel_execute.Coordinator(
            root, "fixture", adapter_factory=lambda: adapter,
            git_adapter_factory=lambda: (_ for _ in ()).throw(AssertionError("waiting restart must reuse sync receipt")),
            gate_receipt_factory=lambda _: {"passed": True, "current_head": "waiting-checkpoint-head", "lane": "slice-A", "gate": "gate"},
        )
        waiting._plan = lambda: plan  # type: ignore[method-assign]
        resumed = waiting.start(resume=True)
        assert resumed["state"]["lanes"]["slice-A"]["state"] == "running"
        assert adapter.calls == [("wait", "terminal-A"), ("follow_up", "terminal-A")]

        again = parallel_execute.Coordinator(
            root, "fixture", adapter_factory=lambda: adapter,
            git_adapter_factory=lambda: (_ for _ in ()).throw(AssertionError("restarted follow-up must not resync")),
        )
        again._plan = lambda: plan  # type: ignore[method-assign]
        again.start(resume=True)
        assert adapter.calls == [("wait", "terminal-A"), ("follow_up", "terminal-A"), ("wait", "terminal-A")]
    finally:
        parallel_execute.Coordinator._plan = original_plan  # type: ignore[method-assign]
        shutil.rmtree(root)


def test_disabled_start_short_circuits_planner_git_and_adapter() -> None:
    root = make_repo(mode="disabled")
    original_root = parallel_execute._repository_root
    original_state_path = parallel_execute.runtime_state_path
    try:
        def forbidden(*args: object, **kwargs: object) -> Path:
            raise AssertionError("disabled execution must not resolve Git state")

        parallel_execute._repository_root = forbidden  # type: ignore[assignment]
        parallel_execute.runtime_state_path = forbidden  # type: ignore[assignment]
        coordinator = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: (_ for _ in ()).throw(AssertionError("adapter")))
        coordinator._plan = lambda: (_ for _ in ()).throw(AssertionError("planner"))  # type: ignore[method-assign]
        result = coordinator.start()
        assert result["reason"] == "disabled-mode"
        assert result["lanes"][0]["id"] == "serial"
    finally:
        parallel_execute._repository_root = original_root  # type: ignore[assignment]
        parallel_execute.runtime_state_path = original_state_path  # type: ignore[assignment]
        shutil.rmtree(root)


def test_same_slice_tasks_never_start_two_workers_or_reorder_declared_tasks() -> None:
    root = make_repo()
    try:
        adapter = RecordingAdapter()
        coordinator = parallel_execute.Coordinator(
            root,
            "fixture",
            adapter_factory=lambda: adapter,
        )
        coordinator._plan = lambda: {
            "fallback": False,
            "lanes": [
                {"id": "slice-A-1", "slice": "A", "task": "T1", "status": "ready", "sync_after": [], "resources": []},
                {"id": "slice-A-2", "slice": "A", "task": "T2", "status": "ready", "sync_after": [], "resources": []},
            ],
        }  # type: ignore[method-assign]
        result = coordinator.start()
        assert result["fallback"] is False
        assert result["state"]["lanes"]["slice-A-1"]["state"] == "running"  # type: ignore[index]
        assert "slice-A-2" not in result["state"]["lanes"]  # type: ignore[index]
        assert [effect[0] for effect in adapter.effects] == ["worktree", "worker"]
    finally:
        shutil.rmtree(root)


class CheckpointReceiptAdapter(RecordingAdapter):
    def __init__(self, state_path: Path, *, changed: bool = True) -> None:
        super().__init__()
        self.state_path = state_path
        self.changed = changed
        self.sync_calls = 0

    def sync_checkpoint(self, consumer: Path, producer: str, *, declared_paths: list[str] | None = None, expected_receipt: dict[str, object] | None = None) -> dict[str, object]:
        self.sync_calls += 1
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        assert state["actions"]
        head = state["source_git_head"]
        return {
            "status": "synced" if self.changed else "noop",
            "changed": self.changed,
            "producer_commit": producer,
            "pre_head": head,
            "post_head": "checkpoint-head" if self.changed else head,
            "changed_paths": ["producer.txt"] if self.changed else [],
            "invalidated_evidence": ["gate", "technical_verifier", "deep_review"] if self.changed else [],
        }

    def remove_worktree(self, worktree: str, **_: object) -> dict[str, object]:
        self.effects.append(("worktree_cleanup", worktree))
        return {"removed": True, "worktree_path": worktree}


def test_malformed_checkpoint_receipt_serializes_with_named_receipt_and_cleanup() -> None:
    root = make_repo()
    try:
        probe = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter())
        probe._prepare_repository()
        workflow = json.loads((root / ".specs/features/fixture/workflow.json").read_text(encoding="utf-8"))
        state = parallel_execute.new_runtime_state(str(root.resolve()), "fixture", "full", workflow["git_head"])
        state["lanes"]["producer"] = {"slice": "P", "task": "T0", "state": "complete", "resources": [], "current_head": workflow["git_head"]}
        parallel_execute.atomic_write_json(probe.state_path, state)

        class Malformed(CheckpointReceiptAdapter):
            def sync_checkpoint(self, consumer: Path, producer: str, *, declared_paths: list[str] | None = None, expected_receipt: dict[str, object] | None = None) -> dict[str, object]:
                return {"status": "synced", "pre_head": workflow["git_head"]}

        adapter = Malformed(probe.state_path)
        plan = {"fallback": False, "lanes": [{"id": "slice-A", "slice": "A", "task": "T1", "status": "ready", "sync_after": ["T0"], "declared_paths": ["src/a.py"], "resources": []}]}
        coordinator = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: adapter, git_adapter_factory=lambda: adapter)
        coordinator._plan = lambda: plan  # type: ignore[method-assign]
        result = coordinator.start()
        assert result["fallback"] is True
        assert result["reason"] == "malformed-checkpoint-receipt"
        assert result["state"]["lanes"]["slice-A"]["state"] == "serial"  # type: ignore[index]
        sync_action = next(action for action in result["state"]["actions"].values() if action["action"] == "sync")
        assert sync_action["receipt"]["reason"] == "malformed-checkpoint-receipt"
        assert any(effect[0] == "worktree_cleanup" for effect in adapter.effects)
    finally:
        shutil.rmtree(root)


def test_checkpoint_invalidation_blocks_worker_and_persists_exact_receipt_across_restart() -> None:
    root = make_repo()
    try:
        probe = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter())
        probe._prepare_repository()
        workflow = json.loads((root / ".specs/features/fixture/workflow.json").read_text(encoding="utf-8"))
        state = parallel_execute.new_runtime_state(str(root.resolve()), "fixture", "full", workflow["git_head"])
        state["lanes"]["producer"] = {"slice": "P", "task": "T0", "state": "complete", "resources": [], "current_head": workflow["git_head"]}
        parallel_execute.atomic_write_json(probe.state_path, state)
        adapter = CheckpointReceiptAdapter(probe.state_path)
        plan = {
            "fallback": False,
            "lanes": [{"id": "slice-A", "slice": "A", "task": "T1", "status": "ready", "sync_after": ["T0"], "resources": []}],
        }
        first = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: adapter, git_adapter_factory=lambda: adapter)
        first._plan = lambda: plan  # type: ignore[method-assign]
        result = first.start()
        lane = result["state"]["lanes"]["slice-A"]
        assert result["fallback"] is False
        assert lane["state"] == "gate_required"
        assert lane["current_head"] == "checkpoint-head"
        assert lane["invalidated_evidence"] == ["gate", "technical_verifier", "deep_review"]
        assert not any(effect[0] == "worker" for effect in adapter.effects)
        calls = adapter.sync_calls

        blocked = parallel_execute.Coordinator(
            root,
            "fixture",
            adapter_factory=lambda: adapter,
            git_adapter_factory=lambda: (_ for _ in ()).throw(AssertionError("restart must not resync")),
            gate_receipt_factory=lambda _: {"passed": False, "current_head": "checkpoint-head", "lane": "slice-A", "gate": "gate"},
        )
        blocked._plan = lambda: plan  # type: ignore[method-assign]
        blocked_result = blocked.start(resume=True)
        assert blocked_result["state"]["lanes"]["slice-A"]["state"] == "gate_required"
        assert adapter.sync_calls == calls
        accepted = parallel_execute.Coordinator(
            root,
            "fixture",
            adapter_factory=lambda: adapter,
            git_adapter_factory=lambda: (_ for _ in ()).throw(AssertionError("accepted gate must replay sync receipt")),
            gate_receipt_factory=lambda _: {"passed": True, "current_head": "checkpoint-head", "lane": "slice-A", "gate": "gate"},
        )
        accepted._plan = lambda: plan  # type: ignore[method-assign]
        accepted_result = accepted.start(resume=True)
        assert accepted_result["state"]["lanes"]["slice-A"]["state"] == "running"
        assert adapter.sync_calls == calls
        assert any(effect[0] == "worker" for effect in adapter.effects)
    finally:
        shutil.rmtree(root)


def test_gate_receipt_requires_exact_identity_and_removes_only_gate_invalidation() -> None:
    root = make_repo()
    try:
        probe = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter())
        probe._prepare_repository()
        workflow = json.loads((root / ".specs/features/fixture/workflow.json").read_text(encoding="utf-8"))
        state = parallel_execute.new_runtime_state(str(root.resolve()), "fixture", "full", workflow["git_head"])
        state["lanes"]["slice-A"] = {
            "slice": "A", "task": "T1", "state": "gate_required", "resources": [],
            "current_head": "checkpoint-head", "invalidated_evidence": ["gate", "technical_verifier", "deep_review"],
        }
        parallel_execute.atomic_write_json(probe.state_path, state)
        plan = {"fallback": False, "lanes": [{"id": "slice-A", "slice": "A", "task": "T1", "status": "ready", "sync_after": [], "resources": []}]}
        wrong = parallel_execute.Coordinator(
            root, "fixture", adapter_factory=lambda: RecordingAdapter(),
            gate_receipt_factory=lambda _: {"passed": True, "current_head": "wrong", "lane": "slice-A", "gate": "gate"},
        )
        wrong._plan = lambda: plan  # type: ignore[method-assign]
        wrong_result = wrong.start(resume=True)
        assert wrong_result["state"]["lanes"]["slice-A"]["state"] == "gate_required"
        accepted = parallel_execute.Coordinator(
            root, "fixture", adapter_factory=lambda: RecordingAdapter(),
            gate_receipt_factory=lambda _: {"passed": True, "current_head": "checkpoint-head", "lane": "slice-A", "gate": "gate"},
        )
        accepted._plan = lambda: plan  # type: ignore[method-assign]
        accepted_result = accepted.start(resume=True)
        lane = accepted_result["state"]["lanes"]["slice-A"]
        assert "gate" not in lane["invalidated_evidence"]
        assert lane["invalidated_evidence"] == ["technical_verifier", "deep_review"]
    finally:
        shutil.rmtree(root)


class ReconcilingAdapter(RecordingAdapter):
    def __init__(self, state_path: Path) -> None:
        super().__init__()
        self.state_path = state_path
        self.reconciled: list[str] = []

    def reconcile_action(self, action: dict[str, object]) -> dict[str, str]:
        self.reconciled.append(str(action["action"]))
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        root = self.state_path.parent.parent.parent
        destination = parallel_execute.derive_worktree_destination(root, "fixture", "A", "T1")
        return {"worktree_id": "wt-recovered", "worktree_path": str(destination), "branch": "slice/A", "pre_head": state["source_git_head"]}


def test_pending_crash_receipt_is_reconciled_without_repeating_external_effect() -> None:
    root = make_repo()
    try:
        probe = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter())
        probe._prepare_repository()
        state = parallel_execute.new_runtime_state(str(root.resolve()), "fixture", "safe", json.loads((root / ".specs/features/fixture/workflow.json").read_text())["git_head"])
        state["lanes"]["slice-A"] = {"slice": "A", "task": "T1", "state": "ready", "resources": []}
        key = parallel_execute.idempotency_key("fixture", "A", "T1", "worktree", state["source_git_head"])
        state["actions"][key] = {"key": key, "action": "worktree", "status": "pending", "lane": "slice-A"}
        parallel_execute.atomic_write_json(probe.state_path, state)
        adapter = ReconcilingAdapter(probe.state_path)
        coordinator = parallel_execute.Coordinator(
            root,
            "fixture",
            adapter_factory=lambda: adapter,
        )
        coordinator._plan = lambda: lane_plan(resources=[])  # type: ignore[method-assign]
        result = coordinator.start(resume=True)
        assert result["fallback"] is False
        assert adapter.reconciled == ["worktree"]
        assert [effect[0] for effect in adapter.effects] == ["worker"]
        assert result["state"]["actions"][key]["status"] == "accepted"  # type: ignore[index]
    finally:
        shutil.rmtree(root)


def test_unreconcilable_pending_or_foreign_state_selects_serial_without_adapter_effect() -> None:
    root = make_repo()
    try:
        probe = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter())
        probe._prepare_repository()
        state = parallel_execute.new_runtime_state(str(root.resolve()), "other-feature", "safe", "head")
        parallel_execute.atomic_write_json(probe.state_path, state)
        adapter = RecordingAdapter()
        coordinator = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: adapter)
        coordinator._plan = lambda: lane_plan(resources=[])  # type: ignore[method-assign]
        result = coordinator.start(resume=True)
        assert result["fallback"] is True
        assert result["reason"].startswith("state:")
        assert adapter.effects == []
        valid = parallel_execute.new_runtime_state(
            str(root.resolve()), "fixture", "safe", json.loads((root / ".specs/features/fixture/workflow.json").read_text())["git_head"]
        )
        valid["lanes"]["slice-A"] = {"slice": "A", "task": "T1", "state": "ready", "resources": []}
        key = parallel_execute.idempotency_key("fixture", "A", "T1", "worktree", valid["source_git_head"])
        valid["actions"][key] = {"key": key, "action": "worktree", "status": "pending", "lane": "slice-A"}
        parallel_execute.atomic_write_json(coordinator.state_path, valid)
        pending_adapter = RecordingAdapter()
        pending = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: pending_adapter)
        pending._plan = lambda: lane_plan(resources=[])  # type: ignore[method-assign]
        pending_result = pending.start(resume=True)
        assert pending_result["fallback"] is True
        assert pending_result["reason"] == "unreconciled-pending"
        assert pending_adapter.effects == []
    finally:
        shutil.rmtree(root)


def test_nested_malformed_lease_state_is_rejected_before_adapter_effect() -> None:
    root = make_repo()
    try:
        probe = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter())
        probe._prepare_repository()
        source_head = json.loads((root / ".specs/features/fixture/workflow.json").read_text())["git_head"]
        malformed = parallel_execute.new_runtime_state(str(root.resolve()), "fixture", "safe", source_head)
        malformed["lanes"]["slice-A"] = {
            "slice": "A",
            "task": "T1",
            "state": "ready",
            "resources": ["port"],
            "lease": {
                "lease_id": "lease-A",
                "idempotency_key": "key-A",
                "resources": ["port"],
                "prepared_worktree": True,
                "environment_keys": ["PORT"],
                "environment": {"PORT": "secret"},
                "released": False,
            },
        }
        parallel_execute.atomic_write_json(probe.state_path, malformed)
        adapter = RecordingAdapter()
        coordinator = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: adapter)
        coordinator._plan = lambda: lane_plan(resources=["port"])  # type: ignore[method-assign]
        result = coordinator.start(resume=True)
        assert result["fallback"] is True
        assert result["reason"].startswith("state:")
        assert adapter.effects == []
    finally:
        shutil.rmtree(root)


class ObservingAdapter(RecordingAdapter):
    def __init__(self, state_path: Path) -> None:
        super().__init__()
        self.state_path = state_path
        self.pending_before_effect = False

    def observe_worktree(self, destination: Path, source_head: str) -> dict[str, str]:
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        pending = next(action for action in state["actions"].values() if action["action"] == "worktree")
        self.pending_before_effect = pending["status"] == "pending"
        return fake_git_worktree(destination, source_head)


def test_each_external_action_observes_its_persisted_idempotency_key_before_effect() -> None:
    root = make_repo()
    try:
        state_path = parallel_execute.runtime_state_path(root, "fixture")
        adapter = ObservingAdapter(state_path)
        coordinator = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: adapter)
        coordinator._plan = lambda: lane_plan(resources=[])  # type: ignore[method-assign]
        result = coordinator.start()
        assert result["fallback"] is False
        assert adapter.pending_before_effect is True
    finally:
        shutil.rmtree(root)


def test_invalid_worktree_destination_is_rejected_before_adapter_effect() -> None:
    root = make_repo()
    try:
        adapter = RecordingAdapter()
        coordinator = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: adapter)
        coordinator._plan = lambda: {
            "fallback": False,
            "lanes": [lane_plan(resources=[])["lanes"][0]],
        }  # type: ignore[method-assign]
        coordinator._worktree_destination = lambda lane: root.parent.parent / "escape"  # type: ignore[method-assign]
        result = coordinator.start()
        assert result["fallback"] is True
        assert result["reason"] == "unsafe-worktree-path"
        assert adapter.effects == []
    finally:
        shutil.rmtree(root)


class OrderedAdapter(RecordingAdapter):
    def __init__(self, statuses: list[str]) -> None:
        super().__init__()
        self.statuses = iter(statuses)
        self.created = 0

    def worktree_effect(self, destination: Path, source_head: str) -> dict[str, str]:
        self.created += 1
        self.effects.append(("worktree:T" + str(self.created), str(destination)))
        return {"worktree_id": f"wt-{self.created}", "worktree_path": str(destination), "branch": f"slice/A-{self.created}", "pre_head": source_head}

    def start_worker(self, lane: dict[str, object], receipt: dict[str, object], *, idempotency_key: str) -> dict[str, str]:
        self.effects.append(("worker:" + str(lane["task"]), idempotency_key))
        return {
            "feature": "fixture",
            "slice": str(lane["slice"]),
            "worktree_id": str(receipt["worktree_id"]),
            "worktree_path": str(receipt["worktree_path"]),
            "branch": str(receipt["branch"]),
            "pre_head": str(receipt["pre_head"]),
            "run_id": "run-" + str(lane["task"]),
            "orchestration_task_id": "task-" + str(lane["task"]),
            "task": str(lane["task"]),
            "dispatch_id": f"dispatch-{lane['task']}",
            "terminal_handle": "terminal-" + str(lane["task"]),
            "idempotency_key": idempotency_key,
            "status": next(self.statuses),
        }


def test_same_slice_dispatches_one_active_task_then_preserves_declared_order() -> None:
    root = make_repo()
    try:
        adapter = OrderedAdapter(["running", "accepted"])

        def plan() -> dict[str, object]:
            return {
                "fallback": False,
                "lanes": [
                    {"id": "slice-A-1", "slice": "A", "task": "T1", "status": "ready", "sync_after": [], "resources": []},
                    {"id": "slice-A-2", "slice": "A", "task": "T2", "status": "ready", "sync_after": [], "resources": []},
                ],
            }

        first = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: adapter)
        first._plan = plan  # type: ignore[method-assign]
        first_result = first.start()
        assert first_result["fallback"] is False
        assert first_result["state"]["lanes"]["slice-A-1"]["state"] == "running"  # type: ignore[index]
        assert "slice-A-2" not in first_result["state"]["lanes"]  # type: ignore[index]
        checkpoint = json.loads(first.state_path.read_text(encoding="utf-8"))
        checkpoint["lanes"]["slice-A-1"]["state"] = "complete"
        parallel_execute.atomic_write_json(first.state_path, checkpoint)
        adapter.statuses = iter(["accepted"])
        second = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: adapter)
        second._plan = plan  # type: ignore[method-assign]
        second_result = second.start(resume=True)
        assert second_result["state"]["lanes"]["slice-A-1"]["state"] == "complete"  # type: ignore[index]
        assert second_result["state"]["lanes"]["slice-A-2"]["state"] == "complete"  # type: ignore[index]
        assert [item[0] for item in adapter.effects] == ["worktree:T1", "worker:T1", "worktree:T2", "worker:T2"]
    finally:
        shutil.rmtree(root)


class BoundaryProvider(RecordingProvider):
    def __init__(self, state_path: Path, *, reconciled: dict[str, dict[str, object]] | None = None) -> None:
        super().__init__()
        self.state_path = state_path
        self.events: list[str] = []
        self.reconciled = reconciled

    def _assert_pending(self, key: str, action: str) -> None:
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        assert state["actions"][key]["action"] == action
        assert state["actions"][key]["status"] == "pending"

    def acquire(self, request: dict[str, object], live_lease_ids: set[str]) -> dict[str, object]:
        self._assert_pending(str(request["idempotency_key"]), "acquire")
        self.events.append("acquire-pending")
        return super().acquire(request, live_lease_ids)

    def release(self, request: dict[str, object], lease_id: str) -> dict[str, object]:
        self._assert_pending(str(request["idempotency_key"]), "release")
        self.events.append("release-pending")
        return super().release(request, lease_id)

    def reconcile_action(self, action: dict[str, object]) -> dict[str, object] | None:
        if self.reconciled is not None and str(action["action"]) in self.reconciled:
            self.events.append("reconcile-" + str(action["action"]))
            payload = dict(self.reconciled[str(action["action"])])
            if action["action"] == "acquire":
                payload["idempotency_key"] = action["key"]
            return payload
        return None


class BoundaryAdapter(RecordingAdapter):
    def __init__(self, state_path: Path, events: list[str], *, terminal: bool = True) -> None:
        super().__init__()
        self.state_path = state_path
        self.events = events
        self.terminal = terminal

    def observe_worktree(self, destination: Path, source_head: str) -> dict[str, str]:
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        pending = next(action for action in state["actions"].values() if action["action"] == "worktree")
        assert pending["status"] == "pending"
        self.events.append("worktree-pending")
        return fake_git_worktree(destination, source_head)

    def start_worker(self, lane: dict[str, object], receipt: dict[str, object], *, idempotency_key: str) -> dict[str, str]:
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        assert state["actions"][idempotency_key]["status"] == "pending"
        self.events.append("worker-pending")
        return {
            "feature": "fixture",
            "slice": str(lane["slice"]),
            "worktree_id": str(receipt["worktree_id"]),
            "worktree_path": str(receipt["worktree_path"]),
            "branch": str(receipt["branch"]),
            "pre_head": str(receipt["pre_head"]),
            "run_id": "run-A",
            "orchestration_task_id": "task-A",
            "task": str(lane["task"]),
            "dispatch_id": "dispatch-A",
            "terminal_handle": "terminal-A",
            "idempotency_key": idempotency_key,
            "status": "accepted" if self.terminal else "running",
        }

    def reconcile_action(self, action: dict[str, object]) -> dict[str, object] | None:
        if action["action"] == "worker":
            self.events.append("reconcile-worker")
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
            lane = state["lanes"][str(action["lane"])]
            return {
                "feature": "fixture", "slice": lane["slice"],
                "worktree_id": lane["worktree_id"], "worktree_path": lane["worktree_path"], "branch": lane["branch"], "pre_head": lane["pre_head"],
                "run_id": "run-A", "orchestration_task_id": "task-A", "task": lane["task"],
                "dispatch_id": "dispatch-A", "terminal_handle": "terminal-A", "idempotency_key": action["key"], "status": "running",
            }
        return None


def test_every_acquire_worker_and_release_effect_observes_persisted_pending_intent() -> None:
    root = make_repo()
    try:
        configure_provider(root)
        state_path = parallel_execute.runtime_state_path(root, "fixture")
        events: list[str] = []
        provider = BoundaryProvider(state_path)
        provider.events = events
        adapter = BoundaryAdapter(state_path, events)
        coordinator = parallel_execute.Coordinator(
            root, "fixture", adapter_factory=lambda: adapter, provider_factory=lambda _: provider
        )
        coordinator._plan = lambda: lane_plan(resources=["port"])  # type: ignore[method-assign]
        result = coordinator.start()
        assert result["fallback"] is False
        assert events == ["worktree-pending", "acquire-pending", "worker-pending", "release-pending"]
    finally:
        shutil.rmtree(root)


def test_pending_acquire_worker_and_release_reconcile_without_repeating_effects() -> None:
    root = make_repo()
    try:
        configure_provider(root)
        probe = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter())
        probe._prepare_repository()
        source_head = json.loads((root / ".specs/features/fixture/workflow.json").read_text())["git_head"]
        state = parallel_execute.new_runtime_state(str(root.resolve()), "fixture", "safe", source_head)
        worktree = str(parallel_execute.derive_worktree_destination(root, "fixture", "A", "T1"))
        acquire_key = parallel_execute.idempotency_key("fixture", "A", "T1", "acquire", source_head)
        state["lanes"]["slice-A"] = {
            "slice": "A", "task": "T1", "state": "running", "resources": ["port"],
            "worktree_id": "wt-A", "worktree_path": worktree, "branch": "slice/A", "pre_head": source_head,
            "lease": {"lease_id": "lease-A", "idempotency_key": acquire_key, "resources": ["port"], "prepared_worktree": True, "environment_keys": [], "environment": {}, "released": False},
        }
        for action, status in (("worktree", "accepted"), ("acquire", "pending"), ("worker", "pending"), ("release", "pending")):
            key = parallel_execute.idempotency_key("fixture", "A", "T1", action, source_head)
            state["actions"][key] = {"key": key, "action": action, "status": status, "lane": "slice-A"}
            if action == "worktree":
                state["actions"][key].update({"external_id": "wt-A", "receipt": {"worktree_id": "wt-A", "worktree_path": worktree, "branch": "slice/A", "pre_head": source_head}})
        parallel_execute.atomic_write_json(probe.state_path, state)
        provider = BoundaryProvider(
            probe.state_path,
            reconciled={
                "acquire": {"lease_id": "lease-A", "resources": ["port"], "prepared_worktree": True, "environment": {}},
                "release": {"lease_id": "lease-A", "released": True},
            },
        )
        adapter = BoundaryAdapter(probe.state_path, provider.events, terminal=False)
        coordinator = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: adapter, provider_factory=lambda _: provider)
        coordinator._plan = lambda: lane_plan(resources=["port"])  # type: ignore[method-assign]
        result = coordinator.start(resume=True)
        assert result["fallback"] is False
        assert provider.acquires == 0
        assert provider.releases == 0
        assert "reconcile-acquire" in provider.events
        assert "reconcile-release" in provider.events
        assert "reconcile-worker" in provider.events
        recovered_lease = result["state"]["lanes"]["slice-A"]["lease"]  # type: ignore[index]
        assert recovered_lease["idempotency_key"] == acquire_key  # type: ignore[index]
        assert recovered_lease["resources"] == ["port"]  # type: ignore[index]
        assert recovered_lease["prepared_worktree"] is True  # type: ignore[index]
        assert recovered_lease["environment"] == {}  # type: ignore[index]
        assert adapter.effects == []
    finally:
        shutil.rmtree(root)


class WorkerOnlyAdapter:
    def __init__(self, seen: list[str]) -> None:
        self.seen = seen

    def start_worker(self, lane: dict[str, object], receipt: dict[str, object], *, idempotency_key: str) -> dict[str, str]:
        self.seen.append(str(receipt["worktree_path"]))
        return {"dispatch_id": "dispatch-existing", "status": "running"}


def test_worker_only_adapter_receives_precreated_validated_git_worktree() -> None:
    root = make_repo()
    try:
        seen: list[str] = []
        created: list[tuple[Path, str]] = []
        original_creator = parallel_execute.create_git_worktree

        def fake_creator(repo: Path, destination: Path, source_head: str) -> dict[str, str]:
            created.append((destination, source_head))
            return {
                "worktree_id": "git-wt-A",
                "worktree_path": str(destination),
                "branch": "(detached)",
                "pre_head": source_head,
            }

        parallel_execute.create_git_worktree = fake_creator  # type: ignore[assignment]
        adapter = WorkerOnlyAdapter(seen)
        coordinator = parallel_execute.Coordinator(
            root,
            "fixture",
            adapter_factory=lambda: adapter,
            worktree_creator=lambda destination, source_head: parallel_execute.create_git_worktree(root, destination, source_head),
        )
        coordinator._plan = lambda: lane_plan(resources=[])  # type: ignore[method-assign]
        result = coordinator.start()
        assert result["fallback"] is True
        assert result["reason"] == "worker-failed"
        assert len(created) == 1
        assert seen == [str(created[0][0])]
        assert created[0][0].parent.parent.parent == root.resolve().parent
    finally:
        parallel_execute.create_git_worktree = original_creator  # type: ignore[assignment]
        shutil.rmtree(root)


def test_real_git_worktree_creation_and_cleanup_use_unpatched_argv_path() -> None:
    root = make_repo()
    destination = parallel_execute.derive_worktree_destination(root, "fixture", "A", "T1")
    try:
        source_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        receipt = parallel_execute.create_git_worktree(root, destination, source_head)
        assert destination.is_dir()
        assert receipt["worktree_path"] == str(destination)
        assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=destination, text=True).strip() == source_head
        removed = subprocess.run(["git", "worktree", "remove", "--force", str(destination)], cwd=root, check=True, capture_output=True, text=True)
        assert removed.returncode == 0
        subprocess.run(["git", "worktree", "prune"], cwd=root, check=True, capture_output=True, text=True)
        assert not destination.exists()
    finally:
        if destination.exists():
            subprocess.run(["git", "worktree", "remove", "--force", str(destination)], cwd=root, check=False, capture_output=True, text=True)


def test_integration_requires_fresh_external_technical_verifier_and_frozen_root_head() -> None:
    for verifier in (None, {"current_head": "stale"}, {"current_head": "head-A", "author": "worker-A"}, {"malformed": True}):
        root = make_repo(mode="full")
        try:
            probe = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter())
            probe._prepare_repository()
            source_head = json.loads((root / ".specs/features/fixture/workflow.json").read_text(encoding="utf-8"))["git_head"]
            lane = {
                "slice": "A", "task": "T1", "state": "complete", "resources": [], "current_head": "head-A",
                "worktree_id": "wt-A", "worktree_path": str(root / "A-worktree"), "branch": "(detached)", "pre_head": source_head,
            }
            state = parallel_execute.new_runtime_state(str(root.resolve()), "fixture", "full", source_head)
            state["lanes"]["slice-A"] = lane
            worker_key = parallel_execute.idempotency_key("fixture", "A", "T1", "worker", source_head)
            state["actions"][worker_key] = {
                "key": worker_key, "action": "worker", "status": "accepted", "lane": "slice-A", "external_id": "dispatch-A",
                "receipt": {"dispatch_id": "dispatch-A"}, "completion": {"delivery_id": "delivery-A", "outcome": "succeeded"},
                "delivery": {"event": "worker_done", "payload": {"outcome": "succeeded"}},
            }
            parallel_execute.atomic_write_json(probe.state_path, state)
            plan = {"fallback": False, "lanes": [{"id": "slice-A", "slice": "A", "task": "T1", "status": "ready", "sync_after": [], "declared_paths": ["src/a.py"], "resources": []}]}

            class GuardGit:
                def __init__(self, moved: bool = False) -> None:
                    self.calls = 0
                    self.moved = moved

                def head(self, _: Path) -> str:
                    return "moved-head" if self.moved else source_head

                def integrate_slices(self, *_: object) -> dict[str, object]:
                    self.calls += 1
                    raise AssertionError("integration must not run without a fresh verifier")

            git = GuardGit()
            coordinator = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter(), git_adapter_factory=lambda: git)
            coordinator._plan = lambda: plan  # type: ignore[method-assign]
            receipts = None
            if verifier is not None and verifier.get("malformed"):
                receipts = [{"receipt_id": "verifier-A"}]
            elif verifier is not None:
                receipts = [{
                    "receipt_id": "verifier-A", "feature": "fixture", "slice": "A", "task": "T1",
                    "worktree_id": "wt-A", "worktree_path": str(root / "A-worktree"), "current_head": verifier["current_head"],
                    "author": verifier.get("author", "verifier-A"), "implementer": "worker-A", "verdict": "passed",
                }]
            result = coordinator.start(technical_verifier_receipts=receipts)
            assert result["fallback"] is True
            assert result["reason"] == "integration-unverified"
            assert git.calls == 0
        finally:
            shutil.rmtree(root)

    root = make_repo(mode="full")
    try:
        probe = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter())
        probe._prepare_repository()
        source_head = json.loads((root / ".specs/features/fixture/workflow.json").read_text(encoding="utf-8"))["git_head"]
        state = parallel_execute.new_runtime_state(str(root.resolve()), "fixture", "full", source_head)
        state["lanes"]["slice-A"] = {"slice": "A", "task": "T1", "state": "complete", "resources": [], "current_head": "head-A", "worktree_id": "wt-A", "worktree_path": str(root / "A-worktree"), "branch": "(detached)", "pre_head": source_head}
        worker_key = parallel_execute.idempotency_key("fixture", "A", "T1", "worker", source_head)
        state["actions"][worker_key] = {"key": worker_key, "action": "worker", "status": "accepted", "lane": "slice-A", "external_id": "dispatch-A", "receipt": {"dispatch_id": "dispatch-A"}, "completion": {"delivery_id": "delivery-A", "outcome": "succeeded"}, "delivery": {"event": "worker_done", "payload": {"outcome": "succeeded"}}}
        parallel_execute.atomic_write_json(probe.state_path, state)
        plan = {"fallback": False, "lanes": [{"id": "slice-A", "slice": "A", "task": "T1", "status": "ready", "sync_after": [], "declared_paths": ["src/a.py"], "resources": []}]}
        receipt = {"receipt_id": "verifier-A", "feature": "fixture", "slice": "A", "task": "T1", "worktree_id": "wt-A", "worktree_path": str(root / "A-worktree"), "current_head": "head-A", "author": "verifier-A", "implementer": "worker-A", "verdict": "passed"}

        class MovedGit:
            def head(self, _: Path) -> str:
                return "moved-head"

            def integrate_slices(self, *_: object) -> dict[str, object]:
                raise AssertionError("moved feature root must not merge")

        coordinator = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter(), git_adapter_factory=lambda: MovedGit())
        coordinator._plan = lambda: plan  # type: ignore[method-assign]
        result = coordinator.start(technical_verifier_receipts=[receipt])
        assert result["fallback"] is True
        assert result["reason"] == "feature-head-moved"
        assert result["state"]["integration_recovery"]["reason"] == "feature-head-moved"  # type: ignore[index]
    finally:
        shutil.rmtree(root)


def test_full_coordinator_integrates_only_all_verified_complete_lanes_once() -> None:
    root = make_repo(mode="full")
    try:
        probe = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter())
        probe._prepare_repository()
        source_head = json.loads((root / ".specs/features/fixture/workflow.json").read_text(encoding="utf-8"))["git_head"]
        state = parallel_execute.new_runtime_state(str(root.resolve()), "fixture", "full", source_head)
        verifier_receipts: list[dict[str, str]] = []
        for lane_id, slice_id, task_id, current_head in (
            ("slice-A", "A", "T1", "head-A"),
            ("slice-B", "B", "T2", "head-B"),
        ):
            worktree_path = str(root / f"{slice_id}-worktree")
            state["lanes"][lane_id] = {
                "slice": slice_id, "task": task_id, "state": "complete", "resources": [],
                "current_head": current_head, "worktree_id": f"wt-{slice_id}", "worktree_path": worktree_path,
                "branch": "(detached)", "pre_head": source_head,
            }
            worker_key = parallel_execute.idempotency_key("fixture", slice_id, task_id, "worker", source_head)
            state["actions"][worker_key] = {
                "key": worker_key, "action": "worker", "status": "accepted", "lane": lane_id,
                "external_id": f"dispatch-{slice_id}",
                "receipt": {"dispatch_id": f"dispatch-{slice_id}"},
                "completion": {"delivery_id": f"delivery-{slice_id}", "outcome": "succeeded"},
                "delivery": {"event": "worker_done", "payload": {"outcome": "succeeded"}},
            }
            verifier_receipts.append({
                "receipt_id": f"verifier-{slice_id}", "feature": "fixture", "slice": slice_id, "task": task_id,
                "worktree_id": f"wt-{slice_id}", "worktree_path": worktree_path, "current_head": current_head,
                "author": f"verifier-{slice_id}", "implementer": f"worker-{slice_id}", "verdict": "passed",
            })
        parallel_execute.atomic_write_json(probe.state_path, state)
        plan = {
            "fallback": False,
            "lanes": [
                {"id": "slice-A", "slice": "A", "task": "T1", "status": "ready", "sync_after": [], "declared_paths": ["src/a.py"], "resources": []},
                {"id": "slice-B", "slice": "B", "task": "T2", "status": "ready", "sync_after": [], "declared_paths": ["src/b.py"], "resources": []},
            ],
        }

        class IntegrationGit:
            def __init__(self) -> None:
                self.calls: list[list[dict[str, str]]] = []

            def integrate_slices(self, feature_worktree: Path, entries: list[dict[str, str]]) -> dict[str, object]:
                self.calls.append(entries)
                return {"status": "merged", "pre_head": source_head, "post_head": "merged-head", "merged": ["head-A", "head-B"], "invalidated_evidence": ["gate", "technical_verifier", "deep_review"]}

            def head(self, feature_worktree: Path) -> str:
                assert feature_worktree == root.resolve()
                return source_head

        git = IntegrationGit()
        first = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter(), git_adapter_factory=lambda: git)
        first._plan = lambda: plan  # type: ignore[method-assign]
        result = first.start(technical_verifier_receipts=verifier_receipts)
        assert result["fallback"] is False
        assert result["state"]["integration_receipt"]["post_head"] == "merged-head"  # type: ignore[index]
        assert result["state"]["post_integration_gate"]["status"] == "required"  # type: ignore[index]
        assert git.calls == [[{"slice": "A", "commit": "head-A"}, {"slice": "B", "commit": "head-B"}]]

        class NoReplayGit:
            def integrate_slices(self, *_: object) -> dict[str, object]:
                raise AssertionError("accepted integration must not repeat")

        restarted = parallel_execute.Coordinator(root, "fixture", adapter_factory=lambda: RecordingAdapter(), git_adapter_factory=lambda: NoReplayGit())
        restarted._plan = lambda: plan  # type: ignore[method-assign]
        resumed = restarted.start()
        assert resumed["state"]["integration_receipt"]["post_head"] == "merged-head"  # type: ignore[index]
    finally:
        shutil.rmtree(root)


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
