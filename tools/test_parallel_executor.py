"""Spec-derived tests for the parallel slice executor coordinator."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents/skills/autonomous/scripts"))
import parallel_execute


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

    def create_worktree(self, lane: dict[str, object], *, idempotency_key: str) -> dict[str, str]:
        self.effects.append(("worktree", idempotency_key))
        return {
            "worktree_id": "wt-A",
            "worktree_path": "/tmp/parallel-executor-wt-A",
            "branch": "slice/A",
            "pre_head": "head",
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

    def acquire(self, request: dict[str, object], live_lease_ids: set[str]) -> dict[str, object]:
        self.acquires += 1
        assert request["resources"] == ["port"]
        assert request["idempotency_key"] not in live_lease_ids
        return {
            "lease_id": self.lease_id,
            "resources": ["port"],
            "prepared_worktree": True,
            "environment_keys": ["PORT"],
            "environment": {"PORT": "<redacted>"},
            "released": False,
        }

    def release(self, request: dict[str, object], lease_id: str) -> dict[str, object]:
        self.releases += 1
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

        provider_executable = root / "provider"
        provider_executable.write_text("#!/bin/sh\n", encoding="utf-8")
        provider_executable.chmod(0o755)
        workflow = json.loads((root / ".specs/features/fixture/workflow.json").read_text(encoding="utf-8"))
        workflow["parallelization"]["resource_provider"] = "provider"
        (root / ".specs/features/fixture/workflow.json").write_text(json.dumps(workflow), encoding="utf-8")
        resource_provider = RecordingProvider()
        resource_coordinator = parallel_execute.Coordinator(
            root,
            "fixture",
            adapter_factory=lambda: RecordingAdapter(),
            provider_factory=lambda _: resource_provider,
        )
        resource_coordinator._plan = lambda: lane_plan(resources=["port"])  # type: ignore[method-assign]
        resource_result = resource_coordinator.start()
        assert resource_result["fallback"] is False
        assert resource_provider.acquires == 1
        lane = resource_result["state"]["lanes"]["slice-A"]  # type: ignore[index]
        assert lane["lease"]["prepared_worktree"] is True  # type: ignore[index]
        assert lane["lease"]["environment"]["PORT"] == "<redacted>"  # type: ignore[index]
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
            assert "foreign" in str(exc)
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
        assert list((root / ".git").glob("parallel-slice-executor/*")) == []
        start = subprocess.run(
            [sys.executable, str(script), "start", "--root", str(root), "--feature", "fixture"],
            text=True,
            capture_output=True,
            check=True,
        )
        assert json.loads(start.stdout)["reason"] == "disabled-mode"
        assert start.stderr == ""
    finally:
        shutil.rmtree(root)


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
