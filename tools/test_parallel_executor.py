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
            "run_id": "run-A",
            "orchestration_task_id": "task-A",
            "dispatch_id": "dispatch-A",
            "terminal_handle": "terminal-A",
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
                return {"dispatch_id": "dispatch-resumed", "status": "running"}

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
            def __init__(self) -> None:
                super().__init__()
                self.calls: list[str] = []

            def wait_events(self, receipt: dict[str, object], *, timeout: float = 30) -> dict[str, object]:
                self.calls.append("check")
                return {"event": "worker_done", "delivery_id": "delivery-A", "run_id": "run-A", "payload": {"taskId": "task-A", "dispatchId": "dispatch-A", "outcome": "succeeded"}}

            def read_worker(self, receipt: dict[str, object]) -> dict[str, object]:
                self.calls.append("read")
                return {"dispatch_id": "dispatch-A", "source": "terminal", "source_identity": "terminal-A", "provider": "codex", "transcript": "<redacted>", "cursor": "cursor-A", "status": "succeeded"}

            def accept_worker_done(self, receipt: dict[str, object], delivery: dict[str, object], output: dict[str, object]) -> dict[str, object]:
                self.calls.append("accept")
                return {**dict(receipt), "status": "accepted", "accepted": True}

            def release(self, receipt: dict[str, object], result: dict[str, object] | None = None) -> dict[str, object]:
                self.calls.append("release")
                return {"released": True, "dispatch_id": "dispatch-A"}

        adapter = LiveResumeAdapter()
        original_plan = parallel_execute.Coordinator._plan
        parallel_execute.Coordinator._plan = lambda self: lane_plan(resources=[])  # type: ignore[method-assign]
        stdout = io.StringIO()
        stderr = io.StringIO()
        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = parallel_execute.main(["resume", "--root", str(root), "--feature", "fixture"], adapter_factory=lambda: adapter)
        finally:
            parallel_execute.Coordinator._plan = original_plan  # type: ignore[method-assign]
        assert exit_code == 0
        assert stderr.getvalue() == ""
        result = json.loads(stdout.getvalue())
        assert result["fallback"] is False
        assert result["state"]["lanes"]["slice-A"]["state"] == "complete"
        assert adapter.calls == ["check", "read", "accept", "release"]
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
                            return {"event": "waiting", "status": "clean", "dependency": "producer-A"}
                        if expected_event == "invalid":
                            raise parallel_execute.ExecutorError("uncorrelated delivery")
                        return {"event": "escalation"}

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
                assert adapter.calls == ["wait"]
            finally:
                shutil.rmtree(root)
    finally:
        parallel_execute.Coordinator._plan = original_plan  # type: ignore[method-assign]


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


class ReconcilingAdapter(RecordingAdapter):
    def __init__(self, state_path: Path) -> None:
        super().__init__()
        self.state_path = state_path
        self.reconciled: list[str] = []

    def reconcile_action(self, action: dict[str, object]) -> dict[str, str]:
        self.reconciled.append(str(action["action"]))
        return {"worktree_id": "wt-recovered", "worktree_path": str(self.state_path.parent), "branch": "slice/A", "pre_head": "head"}


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
        return {"dispatch_id": f"dispatch-{lane['task']}", "status": next(self.statuses)}


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
        return {"dispatch_id": "dispatch-A", "status": "accepted" if self.terminal else "running"}

    def reconcile_action(self, action: dict[str, object]) -> dict[str, object] | None:
        if action["action"] == "worker":
            self.events.append("reconcile-worker")
            return {"dispatch_id": "dispatch-A", "status": "running"}
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
        assert result["fallback"] is False
        assert len(created) == 1
        assert seen == [str(created[0][0])]
        assert created[0][0].parent.parent.parent == root.resolve().parent
    finally:
        parallel_execute.create_git_worktree = original_creator  # type: ignore[assignment]
        shutil.rmtree(root)


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
