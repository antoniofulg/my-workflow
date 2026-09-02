"""Spec-derived tests for the provider-neutral Orca worker adapter."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Mapping

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents/skills/autonomous/scripts"))
import orca_adapter


KEY = "k" * 64
HEAD = "a" * 40


class Completed:
    def __init__(self, payload: object) -> None:
        self.stdout = json.dumps(payload)


class RecordingCLI:
    def __init__(self, responses: list[object]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[list[str], dict[str, object]]] = []

    def __call__(self, argv: list[str], **kwargs: object) -> Completed:
        self.calls.append((list(argv), dict(kwargs)))
        if not self.responses:
            raise AssertionError(f"unexpected Orca call: {argv}")
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return Completed(response)


def fixture() -> tuple[Path, dict[str, object], dict[str, str]]:
    root = Path(tempfile.mkdtemp())
    worktree = root / "existing-worktree"
    worktree.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    (root / "seed").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "seed"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
    lane = {"id": "slice-A", "slice": "A", "task": "T1", "feature": "fixture"}
    worktree_receipt = {
        "worktree_id": "wt-A",
        "worktree_path": str(worktree),
        "branch": "(detached)",
        "pre_head": HEAD,
    }
    return root, lane, worktree_receipt


def worker_payload(worktree: dict[str, str], *, status: str = "running") -> dict[str, object]:
    return {
        "run_id": "run-A",
        "task_id": "task-A",
        "dispatch_id": "dispatch-A",
        "terminal_handle": "terminal-A",
        "worktree_id": worktree["worktree_id"],
        "worktree_path": worktree["worktree_path"],
        "branch": worktree["branch"],
        "pre_head": worktree["pre_head"],
        "feature": "fixture",
        "slice": "A",
        "task": "T1",
        "idempotency_key": KEY,
        "status": status,
    }


def adapter(root: Path, cli: RecordingCLI, **kwargs: object) -> orca_adapter.OrcaAdapter:
    return orca_adapter.OrcaAdapter(root, "fixture", runner=cli, **kwargs)


def start_responses(worktree: dict[str, str]) -> list[object]:
    return [
        {"runs": []},
        {"id": "request-run-create", "result": {"run": {"id": "run-A", "objective": "parallel-slice:fixture:" + KEY}}},
        {"tasks": []},
        {"id": "request-task-create", "result": {"task": {"id": "task-A", "run_id": "run-A", "spec": "parallel-slice:fixture:A:T1:" + KEY}}},
        {"worktree_path": worktree["worktree_path"]},
        worker_payload(worktree),
    ]


def live_delivery(*, outcome: str = "succeeded") -> dict[str, object]:
    return {
        "id": "delivery-A",
        "run_id": "run-A",
        "type": "worker_done",
        "from_handle": "terminal-A",
        "payload": json.dumps(
            {"taskId": "task-A", "dispatchId": "dispatch-A", "outcome": outcome, "filesModified": []}
        ),
        "created_at": "2026-08-24T00:00:00Z",
    }


def live_worker_output() -> dict[str, object]:
    return {
        "dispatchId": "dispatch-A",
        "source": "terminal",
        "sourceIdentity": "terminal-A",
        "provider": "codex",
        "transcript": "secret worker transcript",
        "cursor": "cursor-A",
        "status": "succeeded",
    }


class CanaryDouble(orca_adapter.OrcaAdapter):
    def __init__(self, root: Path, *, failure: str | None = None) -> None:
        self.failure = failure
        super().__init__(
            root,
            "fixture",
            runner=RecordingCLI([{"exists": failure == "absence", "worktree_path": str(root / "canary-worktree")}]),
            worktree_creator=lambda destination, source: {
                "worktree_id": "wt-canary", "worktree_path": str(root / "canary-worktree"),
                "branch": "(detached)", "pre_head": HEAD,
            },
            worktree_remover=self._remove,
        )
        self._canary_worker = {
            "worktree_id": "wt-canary", "worktree_path": str(root / "canary-worktree"),
            "branch": "(detached)", "pre_head": HEAD, "feature": "fixture", "slice": "canary",
            "task": "lifecycle", "run_id": "run-canary", "task_id": "task-canary",
            "orchestration_task_id": "task-canary", "dispatch_id": "dispatch-canary",
            "terminal_handle": "terminal-canary", "idempotency_key": "canary-key", "status": "running",
        }

    def probe(self) -> dict[str, object]:
        return {
            "version": 1, "feature": "fixture", "adapter": "orca", "status": "candidate",
            "runtime": {
                "app_version": "1.4.189", "capabilities": [orca_adapter.CAPABILITY],
                "executable_identity": {"path": "orca", "size": 1, "mtime_ns": 1},
            },
            "proof": {"cleanup": "not-run"},
        }

    def _canary_source_head(self) -> str:
        return HEAD

    def start_worker(self, lane: object, worktree: object, *, idempotency_key: str) -> dict[str, object]:
        if self.failure == "start":
            raise orca_adapter.AdapterError(
                "worker start failed", details={
                    "run_id": "run-canary", "task_id": "task-canary", "dispatch_id": "dispatch-canary",
                    "terminal_handle": "terminal-canary",
                },
            )
        self._canary_worker["idempotency_key"] = idempotency_key
        return dict(self._canary_worker)

    def wait_events(self, receipt: object, *, timeout: float = 30) -> dict[str, object]:
        if self.failure == "completion":
            raise orca_adapter.AdapterError("worker completion failed")
        return {
            "event": "worker_done", "status": "accepted", "delivery_id": "delivery-canary",
            "task_id": "task-canary", "dispatch_id": "dispatch-canary",
        }

    def read_worker(self, receipt: object) -> dict[str, object]:
        if self.failure == "read":
            raise orca_adapter.AdapterError("worker read failed")
        return {"dispatch_id": "dispatch-canary", "transcript": "<redacted>"}

    def accept_worker_done(self, receipt: object, delivery: object, output: object) -> dict[str, object]:
        return {"accepted": True}

    def ack_delivery(self, receipt: object, delivery: object) -> dict[str, object]:
        if self.failure == "ack":
            raise orca_adapter.AdapterError("worker ack failed")
        return {"acknowledged": True}

    def release(self, receipt: object, result: object = None) -> dict[str, object]:
        if self.failure == "release":
            raise orca_adapter.AdapterError("worker release failed")
        return {"released": True}

    def _call(self, *arguments: str, timeout: float | None = None) -> dict[str, object]:
        if arguments[0] == "worker-show":
            return {"status": "released", "dispatch_id": "dispatch-canary", "terminal": {"handle": "terminal-canary", "status": "exited", "connected": False, "writable": False}}
        return {"exists": self.failure == "absence", "worktree_path": str(self._canary_worker["worktree_path"])}

    def _remove(self, receipt: Mapping[str, object]) -> dict[str, object]:
        if self.failure == "removal":
            raise orca_adapter.AdapterError("worktree removal failed")
        return {"removed": True, "worktree_path": receipt["worktree_path"]}


def test_start_attaches_existing_worktree_and_correlates_every_receipt_field() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI(start_responses(worktree))
        receipt = adapter(root, cli).start_worker(lane, worktree, idempotency_key=KEY)
        commands = [call[0][2] for call in cli.calls]
        assert commands == ["run-list", "run-create", "task-list", "task-create", "show", "worker-start"]
        assert all("create" not in call[0][2:] or "worktree" not in call[0] for call in cli.calls)
        worker_call = cli.calls[-1][0]
        assert "--worktree" in worker_call
        assert "path:" + str(Path(worktree["worktree_path"]).resolve()) in worker_call
        assert worker_call[worker_call.index("--timeout-ms") + 1] == str(orca_adapter.WORKER_START_TIMEOUT_MS)
        assert receipt["run_id"] == "run-A"
        assert receipt["orchestration_task_id"] == "task-A"
        assert receipt["dispatch_id"] == "dispatch-A"
        assert receipt["terminal_handle"] == "terminal-A"
        assert receipt["worktree_path"] == worktree["worktree_path"]
        assert receipt["pre_head"] == HEAD
        assert receipt["idempotency_key"] == KEY
        assert receipt["status"] == "running"
    finally:
        shutil.rmtree(root)


def test_probe_rejects_installed_known_bad_version_without_lifecycle_effect() -> None:
    root, _, _ = fixture()
    try:
        cli = RecordingCLI([{"ready": True, "appVersion": "1.4.188", "capabilities": [orca_adapter.CAPABILITY]}])
        result = adapter(root, cli).probe()
        assert result["status"] == "unsupported"
        assert result["reason"] == "known-incompatible-version:1.4.188"
        assert [call[0] for call in cli.calls] == [["orca", "status", "--json"]]
    finally:
        shutil.rmtree(root)


def test_probe_rejects_not_ready_missing_version_and_missing_contract() -> None:
    cases = (
        ({"ready": False, "appVersion": "1.4.189", "capabilities": [orca_adapter.CAPABILITY]}, "runtime-not-ready"),
        ({"ready": False, "status": "running", "appVersion": "1.4.189", "capabilities": [orca_adapter.CAPABILITY]}, "runtime-not-ready"),
        ({"ready": True, "capabilities": [orca_adapter.CAPABILITY]}, "missing-app-version"),
        ({"ready": True, "version": 1, "capabilities": [orca_adapter.CAPABILITY]}, "missing-app-version"),
        ({"ready": True, "appVersion": "1.4.189", "capabilities": []}, "missing-capability:" + orca_adapter.CAPABILITY),
    )
    for payload, reason in cases:
        root, _, _ = fixture()
        try:
            result = adapter(root, RecordingCLI([payload])).probe()
            assert result["status"] == "unsupported"
            assert result["reason"] == reason
            if "appVersion" in payload:
                assert result["envelope"]["app_version"] == payload["appVersion"]
                assert result["envelope"]["protocol_version"] == payload.get("version")
        finally:
            shutil.rmtree(root)


def test_canary_failure_at_each_stage_never_caches_pass_and_reports_owned_ids() -> None:
    for failure, expected_stage in (
        ("start", "worker-start"), ("completion", "worker-done"), ("read", "worker-read"),
        ("ack", "worker-ack"), ("release", "worker-release"), ("removal", "worktree-remove"),
        ("absence", "absence"),
    ):
        root, _, _ = fixture()
        try:
            worker = CanaryDouble(root, failure=failure)
            try:
                worker.canary()
            except orca_adapter.AdapterError as exc:
                assert exc.details["stage"] == expected_stage
                assert exc.details["dispatch_id"] == "dispatch-canary"
                assert exc.details["terminal_handle"] == "terminal-canary"
            else:
                raise AssertionError(f"canary failure {failure} must be reported")
            assert not worker._cache_path().exists()
        finally:
            shutil.rmtree(root)


def test_probe_reuses_only_matching_repository_runtime_cache() -> None:
    root, _, _ = fixture()
    try:
        cli = RecordingCLI([
            {"ready": True, "appVersion": "1.4.189", "capabilities": [orca_adapter.CAPABILITY]},
            {"ready": True, "appVersion": "1.4.189", "capabilities": [orca_adapter.CAPABILITY]},
        ])
        worker = adapter(root, cli)
        identity = worker.identity()
        orca_adapter.core.atomic_write_json(
            worker._cache_path(),
            {
                "version": 1, "feature": "fixture", "repository": str(worker.root), "adapter": "orca",
                "runtime": identity, "proof": {"cleanup": "clean"}, "status": "compatible",
            },
        )
        result = worker.probe()
        assert result["status"] == "compatible"
        assert result["proof"]["cleanup"] == "clean"
        assert result["proof"]["source"] == "canary"
        assert result["proof"]["cached"] is True
        assert result["missing_capabilities"] == []
        assert result["reason"] is None
        changed = adapter(
            root,
            RecordingCLI([{"ready": True, "appVersion": "1.4.190", "capabilities": [orca_adapter.CAPABILITY]}]),
        ).probe()
        assert changed["status"] == "candidate"
        assert changed["reason"] == "canary-required"
    finally:
        shutil.rmtree(root)


def test_cache_identity_changes_require_a_new_canary_for_repository_capabilities_and_executable() -> None:
    for change in ("repository", "capabilities", "path", "size", "mtime_ns"):
        root, _, _ = fixture()
        try:
            initial = adapter(
                root,
                RecordingCLI([{"ready": True, "appVersion": "1.4.189", "capabilities": [orca_adapter.CAPABILITY]}]),
            )
            identity = initial.identity()
            runtime = dict(identity)
            if change == "repository":
                repository = str(initial.root) + "/foreign"
            else:
                repository = str(initial.root)
                runtime["capabilities"] = [orca_adapter.CAPABILITY, "new.capability"] if change == "capabilities" else runtime["capabilities"]
                executable = dict(runtime["executable_identity"])
                if change == "path":
                    executable["path"] = "/different/orca"
                elif change == "size":
                    executable["size"] = int(executable.get("size", 0)) + 1
                elif change == "mtime_ns":
                    executable["mtime_ns"] = int(executable.get("mtime_ns", 0)) + 1
                runtime["executable_identity"] = executable
            orca_adapter.core.atomic_write_json(initial._cache_path(), {
                "version": 1, "feature": "fixture", "repository": repository, "adapter": "orca",
                "runtime": identity, "proof": {"cleanup": "clean"}, "status": "compatible",
            })
            changed = adapter(
                root,
                RecordingCLI([{"ready": True, "appVersion": "1.4.189", "capabilities": [orca_adapter.CAPABILITY]}]),
            )
            if change == "capabilities":
                changed._runtime_identity = lambda status: runtime  # type: ignore[method-assign]
            elif change != "repository":
                changed._executable_identity = lambda: runtime["executable_identity"]  # type: ignore[method-assign]
            result = changed.probe()
            assert result["status"] == "candidate"
            assert result["reason"] == "canary-required"
        finally:
            shutil.rmtree(root)


def test_matching_cache_returns_compatible_without_running_canary() -> None:
    root, _, _ = fixture()
    try:
        class NoCanary(orca_adapter.OrcaAdapter):
            def canary(self) -> dict[str, object]:
                raise AssertionError("matching cache must not run canary")

        worker = NoCanary(
            root,
            "fixture",
            runner=RecordingCLI([
                {"ready": True, "appVersion": "1.4.189", "capabilities": [orca_adapter.CAPABILITY]},
                {"ready": True, "appVersion": "1.4.189", "capabilities": [orca_adapter.CAPABILITY]},
            ]),
        )
        identity = worker.identity()
        orca_adapter.core.atomic_write_json(worker._cache_path(), {
            "version": 1, "feature": "fixture", "repository": str(worker.root), "adapter": "orca",
            "runtime": identity, "proof": {"cleanup": "clean"}, "status": "compatible",
        })
        result = worker.probe()
        assert result["status"] == "compatible"
        assert result["proof"]["cleanup"] == "clean"
        assert len(worker.runner.calls) == 2  # type: ignore[attr-defined]
    finally:
        shutil.rmtree(root)


def test_canary_requires_clean_removal_before_writing_compatibility_cache() -> None:
    root, _, _ = fixture()
    worktree = root / "canary-worktree"
    worktree.mkdir()
    receipt = {"worktree_id": "wt-canary", "worktree_path": str(worktree), "branch": "(detached)", "pre_head": HEAD}
    creator_calls: list[tuple[Path, str]] = []
    worker_starts: list[str] = []
    worker_done_events: list[dict[str, object]] = []
    try:
        class Candidate(orca_adapter.OrcaAdapter):
            def probe(self) -> dict[str, object]:
                return {
                    "version": 1, "feature": "fixture", "adapter": "orca", "status": "candidate",
                    "runtime": {"app_version": "1.4.189", "capabilities": [orca_adapter.CAPABILITY], "executable_identity": {}},
                    "proof": {"cleanup": "not-run"},
                }

            def _canary_source_head(self) -> str:
                return HEAD

            def start_worker(self, lane: object, worktree: object, *, idempotency_key: str) -> dict[str, object]:
                worker_starts.append("worker-start")
                return {**receipt, "feature": "fixture", "slice": "canary", "task": "lifecycle", "run_id": "run-canary", "task_id": "task-canary", "orchestration_task_id": "task-canary", "dispatch_id": "dispatch-canary", "terminal_handle": "terminal-canary", "idempotency_key": idempotency_key, "status": "running"}

            def wait_events(self, receipt: object, *, timeout: float = 30) -> dict[str, object]:
                event = {"event": "worker_done", "status": "accepted", "delivery_id": "delivery-canary", "task_id": "task-canary", "dispatch_id": "dispatch-canary"}
                worker_done_events.append(event)
                return event

            def read_worker(self, receipt: object) -> dict[str, object]:
                return {"dispatch_id": "dispatch-canary", "transcript": "<redacted>"}

            def accept_worker_done(self, receipt: object, delivery: object, output: object) -> dict[str, object]:
                return {"accepted": True}

            def ack_delivery(self, receipt: object, delivery: object) -> dict[str, object]:
                return {"acknowledged": True}

            def release(self, receipt: object, result: object = None) -> dict[str, object]:
                return {"released": True}

            def _call(self, *arguments: str, timeout: float | None = None) -> dict[str, object]:
                if arguments[0] == "worker-show":
                    return {"status": "released", "dispatch_id": "dispatch-canary", "terminal": {"handle": "terminal-canary", "status": "exited", "connected": False, "writable": False}}
                return {"exists": False, "worktree_path": str(worktree)}

        cli = RecordingCLI([{"exists": False, "worktree_path": str(worktree)}])
        def create_worktree(destination: Path, source: str) -> dict[str, str]:
            creator_calls.append((destination, source))
            return receipt

        def remove_worktree(value: Mapping[str, object]) -> dict[str, object]:
            shutil.rmtree(worktree)
            return {"removed": True, "worktree_path": str(worktree)}

        candidate = Candidate(
            root, "fixture", runner=cli,
            worktree_creator=create_worktree,
            worktree_remover=remove_worktree,
        )
        result = candidate.canary()
        assert result["status"] == "compatible"
        assert result["proof"]["cleanup"] == "clean"
        assert result["proof"]["source"] == "canary"
        assert result["proof"]["cached"] is False
        assert result["missing_capabilities"] == []
        assert result["reason"] is None
        assert len(creator_calls) == 1
        assert worker_starts == ["worker-start"]
        assert worker_done_events == [{
            "event": "worker_done", "status": "accepted", "delivery_id": "delivery-canary",
            "task_id": "task-canary", "dispatch_id": "dispatch-canary",
        }]
        assert json.loads(candidate._cache_path().read_text(encoding="utf-8"))["status"] == "compatible"
    finally:
        shutil.rmtree(root)


def test_not_found_absence_requires_the_exact_local_path_to_be_gone() -> None:
    class NotFoundRunner:
        def __call__(self, argv: list[str], **kwargs: object) -> object:
            raise subprocess.CalledProcessError(
                1, argv, output=json.dumps({"error": {"code": "selector_not_found"}})
            )

    root, _, _ = fixture()
    try:
        gone = root / "gone-worktree"
        worker = adapter(root, NotFoundRunner())
        worker._canary_absence(gone)
        retained = root / "retained-worktree"
        retained.mkdir()
        try:
            worker._canary_absence(retained)
        except orca_adapter.AdapterError as exc:
            assert exc.details["stage"] == "absence"
            assert exc.details["worktree_path"] == str(retained)
        else:
            raise AssertionError("not_found must not hide a retained local checkout")
    finally:
        shutil.rmtree(root)


def test_r11_generic_operation_ids_are_ignored_for_scoped_run_and_task_identity() -> None:
    root, lane, worktree = fixture()
    run_id = "run_658585e3a862"
    task_id = "task_78fcfca161b8"
    objective = "parallel-slice:fixture:" + KEY
    spec = "parallel-slice:fixture:A:T1:" + KEY
    try:
        cli = RecordingCLI([
            {"runs": []},
            {"id": "bbcfd-request", "requestId": "request-A", "mutation": {"requestId": "request-A"}, "result": {"run": {"id": run_id, "objective": objective}}},
            {"tasks": []},
            {"id": "operation-task", "requestId": "request-B", "result": {"task": {"id": task_id, "run_id": run_id, "spec": spec}}},
            {"worktree_path": worktree["worktree_path"]},
            {**worker_payload(worktree), "run_id": run_id, "task_id": task_id, "orchestration_task_id": task_id},
        ])
        receipt = adapter(root, cli).start_worker(lane, worktree, idempotency_key=KEY)
        assert receipt["run_id"] == run_id and receipt["task_id"] == task_id
        worker_call = cli.calls[-1][0]
        assert worker_call[worker_call.index("--task") + 1] == task_id
        assert worker_call[worker_call.index("--task") + 1] != "operation-task"
    finally:
        shutil.rmtree(root)


def test_r11_generic_or_missing_scoped_ids_halt_before_downstream_effects() -> None:
    root, lane, worktree = fixture()
    objective = "parallel-slice:fixture:" + KEY
    spec = "parallel-slice:fixture:A:T1:" + KEY
    try:
        generic_run = RecordingCLI([{"runs": []}, {"id": "request-only", "requestId": "request-A"}])
        try:
            adapter(root, generic_run).start_worker(lane, worktree, idempotency_key=KEY)
        except orca_adapter.AdapterError:
            pass
        else:
            raise AssertionError("generic run operation id must not become Run identity")
        assert [call[0][2] for call in generic_run.calls] == ["run-list", "run-create"]

        generic_task = RecordingCLI([
            {"runs": []}, {"result": {"run": {"id": "run-A", "objective": objective}}},
            {"tasks": []}, {"id": "request-only", "requestId": "request-B"},
        ])
        try:
            adapter(root, generic_task).start_worker(lane, worktree, idempotency_key=KEY)
        except orca_adapter.AdapterError:
            pass
        else:
            raise AssertionError("generic task operation id must not become Task identity")
        assert [call[0][2] for call in generic_task.calls] == ["run-list", "run-create", "task-list", "task-create"]
    finally:
        shutil.rmtree(root)


def test_r11_scoped_run_and_task_conflicts_halt_before_worker_effect() -> None:
    root, lane, worktree = fixture()
    objective = "parallel-slice:fixture:" + KEY
    spec = "parallel-slice:fixture:A:T1:" + KEY
    try:
        conflict_run = RecordingCLI([{"runs": []}, {"result": {"run": {"id": "run-B", "objective": objective}}, "run_id": "run-A"}])
        try:
            adapter(root, conflict_run).start_worker(lane, worktree, idempotency_key=KEY)
        except orca_adapter.AdapterError as exc:
            assert exc.details["code"] == "correlation_conflict"
        else:
            raise AssertionError("conflicting scoped Run identities must halt")
        assert [call[0][2] for call in conflict_run.calls] == ["run-list", "run-create"]

        conflict_task = RecordingCLI([
            {"runs": []}, {"result": {"run": {"id": "run-A", "objective": objective}}}, {"tasks": []},
            {"result": {"task": {"id": "task-B", "run_id": "run-A", "spec": spec}}, "task_id": "task-A"},
        ])
        try:
            adapter(root, conflict_task).start_worker(lane, worktree, idempotency_key=KEY)
        except orca_adapter.AdapterError as exc:
            assert exc.details["code"] == "correlation_conflict"
        else:
            raise AssertionError("conflicting scoped Task identities must halt")
        assert [call[0][2] for call in conflict_task.calls] == ["run-list", "run-create", "task-list", "task-create"]
    finally:
        shutil.rmtree(root)


def test_structured_worker_start_failure_preserves_partial_effect_and_reuses_run_task_on_retry() -> None:
    root, lane, worktree = fixture()
    try:
        failure = subprocess.CalledProcessError(
            1, ["orca", "orchestration", "worker-start"],
            output=json.dumps({"ok": False, "error": {"code": "agent_prompt_stalled", "stage": "worker-start", "run_id": "run-A", "task_id": "task-A", "dispatch_id": "dispatch-A", "terminal_handle": "terminal-A", "residualResources": {"token": "secret"}}}),
            stderr="",
        )
        cli = RecordingCLI(start_responses(worktree)[:4] + [{"worktree_path": worktree["worktree_path"]}, failure])
        worker = adapter(root, cli)
        try:
            worker.start_worker(lane, worktree, idempotency_key=KEY)
        except orca_adapter.AdapterError as exc:
            assert "agent_prompt_stalled" in str(exc)
            assert exc.details["run_id"] == "run-A"
            assert exc.details["task_id"] == "task-A"
            assert exc.details["dispatch_id"] == "dispatch-A"
            assert exc.details["terminal_handle"] == "terminal-A"
            assert exc.details["residualResources"]["token"] == "<redacted>"
        else:
            raise AssertionError("structured worker failure must be reported")

        retry_cli = RecordingCLI([
            {"dispatch_id": "dispatch-A", "status": "failed", "terminal_handle": "terminal-A"},
            {"released": True, "dispatch_id": "dispatch-A"},
            {"worktree_path": worktree["worktree_path"]},
            worker_payload(worktree),
        ])
        retry = adapter(root, retry_cli)
        action = {
            "action": "worker", "key": KEY,
            "partial_effect": {"run_id": "run-A", "task_id": "task-A", "dispatch_id": "dispatch-A", "terminal_handle": "terminal-A"},
            "worker_plan": lane,
            "worktree_receipt": worktree,
        }
        receipt = retry.reconcile_action(action)
        assert receipt is not None and receipt["run_id"] == "run-A" and receipt["orchestration_task_id"] == "task-A"
        assert [call[0][2] for call in retry_cli.calls] == ["worker-show", "worker-release", "show", "worker-start"]
        assert retry_cli.calls[3][0][retry_cli.calls[3][0].index("--task") + 1] == "task-A"
        assert retry_cli.calls[3][0][retry_cli.calls[3][0].index("--retry-of") + 1] == "dispatch-A"
        assert retry.reconcile_action(action) == receipt
        assert len(retry_cli.calls) == 4
    finally:
        shutil.rmtree(root)


def test_nested_dispatch_envelopes_preserve_ctx_identity_through_failure_show_release_and_retry() -> None:
    root, lane, worktree = fixture()
    dispatch_id = "ctx_5f619d0f6298"
    try:
        failure = subprocess.CalledProcessError(
            1, ["orca", "orchestration", "worker-start"],
            output=json.dumps({"ok": False, "error": {"code": "agent_prompt_stalled", "run_id": "run-A", "task_id": "task-A", "terminal_handle": "terminal-A", "dispatch": {"id": dispatch_id}}}),
        )
        cli = RecordingCLI(start_responses(worktree)[:4] + [{"worktree_path": worktree["worktree_path"]}, failure])
        try:
            adapter(root, cli).start_worker(lane, worktree, idempotency_key=KEY)
        except orca_adapter.AdapterError as exc:
            assert exc.details["dispatch_id"] == dispatch_id
        else:
            raise AssertionError("nested stalled dispatch must remain a partial effect")

        retry_cli = RecordingCLI([
            {"result": {"dispatch": {"id": dispatch_id, "status": "failed"}, "worker": {"agent_terminal_handle": "terminal-A"}, "terminal": {"handle": "terminal-A"}, "terminalResource": {"terminalHandle": "terminal-A"}}},
            {"result": {"dispatch": {"id": dispatch_id, "released": True}}},
            {"worktree_path": worktree["worktree_path"]},
            worker_payload(worktree),
        ])
        action = {
            "action": "worker", "key": KEY,
            "partial_effect": {
                "run_id": "run-A", "task_id": "task-A", "dispatch_id": dispatch_id, "terminal_handle": "terminal-A",
                "result": {
                    "dispatchId": dispatch_id, "state": "failed",
                    "lastError": {"code": "agent_prompt_stalled"}, "mutation": {"requestId": "req-A"},
                },
            },
            "worker_plan": lane, "worktree_receipt": worktree,
        }
        worker = adapter(root, retry_cli)
        receipt = worker.reconcile_action(action)
        assert receipt is not None
        assert action["partial_effect"]["run_id"] == "run-A"
        assert action["partial_effect"]["request_id"] == "req-A"
        assert action["partial_effect"]["state"] == "failed"
        assert action["partial_effect"]["result"]["mutation"]["requestId"] == "req-A"  # type: ignore[index]
        worker_start = retry_cli.calls[-1][0]
        assert worker_start[worker_start.index("--retry-of") + 1] == dispatch_id
        assert worker.reconcile_action(action) == receipt
        assert len(retry_cli.calls) == 4
    finally:
        shutil.rmtree(root)


def test_dispatch_identity_rejects_shell_forms_without_overwriting_explicit_id() -> None:
    try:
        orca_adapter._payload({"dispatch_id": "ctx_explicit", "dispatch": {"id": "ctx_other"}})
    except orca_adapter.AdapterError as exc:
        assert exc.details["code"] == "correlation_conflict"
    else:
        raise AssertionError("conflicting canonical dispatch identities must halt")
    for value in ("ctx bad", "ctx;rm", "ctx`id`", "ctx\nother", "ctx'quote'"):
        try:
            orca_adapter._payload({"result": {"dispatch": {"id": value}}})
        except orca_adapter.AdapterError:
            continue
        raise AssertionError(f"malicious dispatch identity must be rejected: {value!r}")


def test_canonical_projection_merges_nested_effects_without_replacing_outer_envelope() -> None:
    dispatch_id = "ctx_5f619d0f6298"
    terminal = "term_2dcb9465-d91c-4260-baa3-b92859412439"
    nested_effect = {
        "dispatch": {"id": dispatch_id},
        "state": "failed",
        "lastError": {"code": "agent_prompt_stalled"},
        "mutation": {"requestId": "req-A"},
    }
    cases = (
        {
            "run_id": "run-A", "task_id": "task-A", "dispatch_id": dispatch_id,
            "terminal_handle": terminal, "result": nested_effect,
        },
        {
            "result": {
                "run": {"id": "run-A"}, "task": {"id": "task-A"},
                "dispatch": {"id": dispatch_id}, "terminal": {"handle": terminal},
                "mutation": {"requestId": "req-A"}, "state": "failed",
            },
        },
        {
            "runId": "run-A", "run_id": "run-A", "taskId": "task-A",
            "dispatchId": dispatch_id, "terminal_handle": terminal,
            "request_id": "req-A", "mutation": {"requestId": "req-A"},
        },
    )
    for envelope in cases:
        projected = orca_adapter._payload(envelope)
        assert projected["run_id"] == "run-A"
        assert projected["task_id"] == "task-A"
        assert projected["dispatch_id"] == dispatch_id
        assert projected["terminal_handle"] == terminal
        assert projected["request_id"] == "req-A"
    projected = orca_adapter._payload(cases[0])
    assert projected["result"] == nested_effect
    assert projected["state"] == "failed"
    assert projected["lastError"] == {"code": "agent_prompt_stalled"}


def test_canonical_projection_rejects_conflicting_identity_and_request_keys() -> None:
    conflicts = (
        ({"run_id": "run-A", "result": {"runId": "run-B"}}, "run_id"),
        ({"task_id": "task-A", "result": {"taskId": "task-B"}}, "task_id"),
        ({"dispatch_id": "ctx-A", "result": {"dispatch": {"id": "ctx-B"}}}, "dispatch_id"),
        ({"terminal_handle": "term-A", "result": {"terminal": {"handle": "term-B"}}}, "terminal_handle"),
        ({"request_id": "req-A", "mutation": {"requestId": "req-B"}}, "request_id"),
        ({"idempotency_key": "key-A", "release": {"idempotencyKey": "key-B"}}, "idempotency_key"),
        ({"retry_request": "retry-A", "result": {"retryRequest": "retry-B"}}, "retry_request"),
    )
    for envelope, field in conflicts:
        try:
            orca_adapter._payload(envelope)
        except orca_adapter.AdapterError as exc:
            assert exc.details["code"] == "correlation_conflict"
            assert exc.details["field"] == field
        else:
            raise AssertionError(f"conflicting {field} must halt before use")


def test_failure_projection_preserves_nested_error_effect_and_missing_run_task_has_zero_effects() -> None:
    failure = subprocess.CalledProcessError(
        1,
        ["orca", "worker-start"],
        output=json.dumps({
            "ok": False,
            "error": {
                "code": "agent_prompt_stalled",
                "result": {
                    "runId": "run-A", "taskId": "task-A",
                    "dispatch": {"id": "ctx_5f619d0f6298"},
                    "terminal": {"handle": "term-A"},
                    "state": "failed", "lastError": {"code": "stalled"},
                    "mutation": {"requestId": "req-A"},
                },
            },
        }),
    )
    details = orca_adapter._failure_details(failure)
    assert details["run_id"] == "run-A"
    assert details["task_id"] == "task-A"
    assert details["dispatch_id"] == "ctx_5f619d0f6298"
    assert details["terminal_handle"] == "term-A"
    assert details["request_id"] == "req-A"
    assert details["state"] == "failed"
    assert details["lastError"] == {"code": "stalled"}
    assert "result" in details

    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI([])
        try:
            adapter(root, cli).reconcile_action({
                "action": "worker", "key": KEY,
                "partial_effect": {"result": {"dispatch": {"id": "ctx_5f619d0f6298"}}},
                "worker_plan": lane, "worktree_receipt": worktree,
            })
        except orca_adapter.AdapterError:
            pass
        else:
            raise AssertionError("missing run/task must halt before recovery")
        assert cli.calls == []
    finally:
        shutil.rmtree(root)


def test_worktree_discovery_retries_selector_visibility_before_one_worker_start() -> None:
    root, lane, worktree = fixture()
    try:
        not_found = subprocess.CalledProcessError(
            1, ["orca", "worktree", "show"],
            output=json.dumps({"ok": False, "error": {"code": "selector_not_found", "stage": "worktree-show"}}),
        )
        cli = RecordingCLI(start_responses(worktree)[:4] + [not_found, {"worktree_path": worktree["worktree_path"]}, worker_payload(worktree)])
        receipt = adapter(root, cli, sleep=lambda _: None).start_worker(lane, worktree, idempotency_key=KEY)
        assert receipt["dispatch_id"] == "dispatch-A"
        assert [call[0][2] for call in cli.calls].count("show") == 2
        assert [call[0][2] for call in cli.calls].count("worker-start") == 1
    finally:
        shutil.rmtree(root)


def test_worktree_discovery_timeout_preserves_run_task_and_never_starts_worker() -> None:
    root, lane, worktree = fixture()
    try:
        not_found = subprocess.CalledProcessError(
            1, ["orca", "worktree", "show"],
            output=json.dumps({"ok": False, "error": {"code": "selector_not_found", "stage": "worktree-show"}}),
        )
        cli = RecordingCLI(start_responses(worktree)[:4] + [not_found] * 8)
        now = [0.0]
        sleeps: list[float] = []

        def clock() -> float:
            return now[0]

        def sleep(delay: float) -> None:
            sleeps.append(delay)
            now[0] += delay

        try:
            adapter(root, cli, clock=clock, sleep=sleep, discovery_timeout=1.0).start_worker(lane, worktree, idempotency_key=KEY)
        except orca_adapter.AdapterError as exc:
            assert exc.details["run_id"] == "run-A"
            assert exc.details["task_id"] == "task-A"
            assert exc.details["stage"] == "worktree-discovery"
            assert exc.details["attempts"] == 5
            assert exc.details["elapsed_ms"] == 1000
            assert exc.details["selector"].startswith("path:")
            assert sum(sleeps) <= 1.0
        else:
            raise AssertionError("bounded discovery timeout must fail safely")
        assert not any(call[0][2] == "worker-start" for call in cli.calls)
    finally:
        shutil.rmtree(root)


def test_worktree_discovery_mismatch_malformed_and_permission_fail_immediately() -> None:
    for discovery_response in (
        {"worktree_path": "/tmp/foreign-worktree"},
        {},
        subprocess.CalledProcessError(
            1, ["orca", "worktree", "show"],
            output=json.dumps({"ok": False, "error": {"code": "permission_denied"}}),
        ),
    ):
        root, lane, worktree = fixture()
        try:
            cli = RecordingCLI(start_responses(worktree)[:4] + [discovery_response])
            sleeps: list[float] = []
            try:
                adapter(root, cli, sleep=sleeps.append).start_worker(lane, worktree, idempotency_key=KEY)
            except orca_adapter.AdapterError:
                pass
            else:
                raise AssertionError("non-selector discovery failure must halt immediately")
            assert [call[0][2] for call in cli.calls].count("show") == 1
            assert not sleeps
            assert not any(call[0][2] == "worker-start" for call in cli.calls)
        finally:
            shutil.rmtree(root)


def test_r13_nested_worktree_receipt_projects_exact_path_and_id_before_worker_start() -> None:
    root, lane, worktree = fixture()
    expected = worktree["worktree_path"]
    try:
        responses = (
            {"id": "request-worktree", "result": {"worktree": {"id": "wt-real", "path": expected, "branch": "", "head": ""}}},
            {"id": "request-worktree", "result": {"worktree": {"worktreeId": "wt-real", "worktreePath": expected, "branch": ""}}},
            {"id": "request-worktree", "result": {"worktree": {"id": "wt-real", "git": {"path": expected}, "branch": ""}}},
        )
        for discovery in responses:
            cli = RecordingCLI(start_responses(worktree)[:4] + [discovery, worker_payload(worktree)])
            receipt = adapter(root, cli, sleep=lambda _: None).start_worker(lane, worktree, idempotency_key=KEY)
            assert receipt["dispatch_id"] == "dispatch-A"
            assert [call[0][2] for call in cli.calls].count("show") == 1
            assert [call[0][2] for call in cli.calls].count("worker-start") == 1
    finally:
        shutil.rmtree(root)


def test_r13_worktree_receipt_missing_divergent_or_conflicting_path_and_id_halts() -> None:
    root, lane, worktree = fixture()
    expected = worktree["worktree_path"]
    foreign = str(root / "foreign-worktree")
    try:
        responses = (
            {"id": "request-worktree", "result": {"worktree": {"id": "wt-real"}}},
            {"id": "request-worktree", "result": {"worktree": {"id": "wt-real", "path": foreign}}},
            {"worktree_path": expected, "result": {"worktree": {"path": foreign, "id": "wt-real"}}},
            {"worktree_id": "wt-A", "result": {"worktree": {"path": expected, "id": "wt-B"}}},
        )
        for discovery in responses:
            cli = RecordingCLI(start_responses(worktree)[:4] + [discovery])
            try:
                adapter(root, cli, sleep=lambda _: None).start_worker(lane, worktree, idempotency_key=KEY)
            except orca_adapter.AdapterError as exc:
                if discovery is responses[0]:
                    assert exc.details["code"] == "malformed_worktree_receipt"
                elif discovery is responses[1]:
                    assert "uncorrelated" in str(exc)
                else:
                    assert exc.details["code"] == "correlation_conflict"
            else:
                raise AssertionError("invalid contextual worktree receipt must halt")
            assert [call[0][2] for call in cli.calls].count("show") == 1
            assert not any(call[0][2] == "worker-start" for call in cli.calls)
    finally:
        shutil.rmtree(root)


def test_unknown_stalled_dispatch_fails_safely_without_release_or_retry() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI([{"dispatch_id": "dispatch-A", "status": "unknown", "terminal_handle": "terminal-A"}])
        try:
            adapter(root, cli).reconcile_action({
                "action": "worker", "key": KEY,
                "partial_effect": {"run_id": "run-A", "task_id": "task-A", "dispatch_id": "dispatch-A", "terminal_handle": "terminal-A"},
                "worker_plan": lane, "worktree_receipt": worktree,
            })
        except orca_adapter.AdapterError as exc:
            assert exc.details["code"] == "worker_outcome_unknown"
        else:
            raise AssertionError("live stalled dispatch must not be retried")
        assert [call[0][2] for call in cli.calls] == ["worker-show"]
    finally:
        shutil.rmtree(root)


def test_r15_failed_owned_live_terminal_stops_once_then_releases_and_retries() -> None:
    root, lane, worktree = fixture()
    dispatch_id = "ctx_d9be12345678"
    terminal = "term_d33912345678"
    resource = "wtr_r15owned"
    try:
        def show(status: str, connected: bool, writable: bool) -> dict[str, object]:
            return {"result": {"dispatch": {"id": dispatch_id, "status": status}, "terminal": {"handle": terminal, "status": "running" if connected else "exited", "connected": connected, "writable": writable}, "terminalResource": {"id": resource, "ownershipState": "owned", "owner": {"dispatchId": dispatch_id}, "origin": {"dispatchId": dispatch_id}, "releaseState": "not_requested"}}}

        stop = {"result": {"stopped": True, "dispatch": {"id": dispatch_id, "status": "stopped"}}}
        worker = {**worker_payload(worktree), "dispatch_id": dispatch_id, "terminal_handle": terminal}
        cli = RecordingCLI([show("failed", True, True), stop, show("stopped", False, False), {"released": True, "dispatch_id": dispatch_id}, {"worktree_path": worktree["worktree_path"]}, worker])
        action = {"action": "worker", "key": KEY, "partial_effect": {"run_id": "run-A", "task_id": "task-A", "dispatch_id": dispatch_id, "terminal_handle": terminal}, "worker_plan": lane, "worktree_receipt": worktree}
        adapter_instance = adapter(root, cli)
        receipt = adapter_instance.reconcile_action(action)
        assert receipt is not None and receipt["dispatch_id"] == dispatch_id
        stop_receipt = action["partial_effect"]["recovery_stop"]  # type: ignore[index]
        assert stop_receipt["stopped"] is True and stop_receipt["retry_request"] == KEY + ":recovery-stop"
        assert [call[0][2] for call in cli.calls] == ["worker-show", "worker-stop", "worker-show", "worker-release", "show", "worker-start"]
        stop_call = cli.calls[1][0]
        assert stop_call[stop_call.index("--dispatch") + 1] == dispatch_id
        assert stop_call[stop_call.index("--retry-request") + 1] == KEY + ":recovery-stop"
        retry_call = cli.calls[-1][0]
        assert retry_call[retry_call.index("--retry-of") + 1] == dispatch_id
        assert adapter_instance.reconcile_action(action) == receipt
        assert len(cli.calls) == 6
        cli.responses.append({"deliveries": [{"id": "late-r15", "run_id": "run-A", "type": "worker_done", "from_handle": terminal, "payload": json.dumps({"taskId": "task-A", "dispatchId": dispatch_id, "outcome": "succeeded"})}]})
        try:
            adapter_instance.wait_events(receipt)
        except orca_adapter.AdapterError as exc:
            assert "stale" in str(exc)
        else:
            raise AssertionError("stopped/released dispatch must reject late delivery")
        replay_cli = RecordingCLI([show("stopped", False, False), {"worktree_path": worktree["worktree_path"]}, worker])
        replay_adapter = adapter(root, replay_cli)
        replay_receipt = replay_adapter.reconcile_action(action)
        assert replay_receipt is not None and replay_receipt["dispatch_id"] == dispatch_id
        assert [call[0][2] for call in replay_cli.calls] == ["worker-show", "show", "worker-start"]
        replay_cli.responses.append({"deliveries": [{"id": "late-r15-replay", "run_id": "run-A", "type": "worker_done", "from_handle": terminal, "payload": json.dumps({"taskId": "task-A", "dispatchId": dispatch_id, "outcome": "succeeded"})}]})
        try:
            replay_adapter.wait_events(replay_receipt)
        except orca_adapter.AdapterError as exc:
            assert "stale" in str(exc)
        else:
            raise AssertionError("fresh adapter must restore revoked dispatch before delivery checks")
    finally:
        shutil.rmtree(root)


def test_r16_camel_terminal_resource_owner_origin_and_terminal_aliases_drive_stop() -> None:
    root, lane, worktree = fixture()
    dispatch_id = "ctx_d9be8d183c51"
    terminal = "term_d339f23b-d3dd-4990-bdfa-c1c447420bc5"
    try:
        def show(status: str, connected: bool, writable: bool) -> dict[str, object]:
            return {"result": {"dispatch": {"id": dispatch_id, "status": status}, "terminalResource": {"resourceId": "wtr_3de59cfde75f", "terminalHandle": terminal, "status": "live" if connected else "exited", "connected": connected, "writable": writable, "ownershipState": "owned", "ownerDispatchId": dispatch_id, "originDispatchId": dispatch_id, "worktreeId": worktree["worktree_id"], "releaseState": "not_requested", "retainedReason": None, "releaseRequestedAt": None, "releaseCompletedAt": None, "releaseError": None}}}

        cli = RecordingCLI([show("failed", True, True), {"result": {"stopped": True, "dispatch": {"id": dispatch_id, "status": "stopped"}}}, show("stopped", False, False), {"released": True, "dispatch_id": dispatch_id}, {"worktree_path": worktree["worktree_path"]}, {**worker_payload(worktree), "dispatch_id": dispatch_id, "terminal_handle": terminal}])
        action = {"action": "worker", "key": KEY, "partial_effect": {"run_id": "run-A", "task_id": "task-A", "dispatch_id": dispatch_id, "terminal_handle": terminal}, "worker_plan": lane, "worktree_receipt": worktree}
        receipt = adapter(root, cli).reconcile_action(action)
        assert receipt is not None
        assert [call[0][2] for call in cli.calls] == ["worker-show", "worker-stop", "worker-show", "worker-release", "show", "worker-start"]
        assert action["partial_effect"]["owner_dispatch_id"] == dispatch_id  # type: ignore[index]
        assert action["partial_effect"]["origin_dispatch_id"] == dispatch_id  # type: ignore[index]
        assert action["partial_effect"]["resource_id"] == "wtr_3de59cfde75f"  # type: ignore[index]
    finally:
        shutil.rmtree(root)


def test_r16_terminal_resource_aliases_equal_or_conflicting_and_missing_owner() -> None:
    dispatch_id = "ctx_d9be8d183c51"
    equal = {"result": {"terminalResource": {"ownerDispatchId": dispatch_id, "owner_dispatch_id": dispatch_id, "originDispatchId": dispatch_id, "origin_dispatch_id": dispatch_id, "terminalHandle": "term-A", "terminal_handle": "term-A"}}}
    projected = orca_adapter._payload(equal)
    assert projected["owner_dispatch_id"] == dispatch_id and projected["origin_dispatch_id"] == dispatch_id
    for resource in (
        {"ownerDispatchId": dispatch_id, "owner_dispatch_id": "ctx-foreign"},
        {"originDispatchId": dispatch_id, "origin_dispatch_id": "ctx-foreign"},
    ):
        try:
            orca_adapter._payload({"result": {"terminalResource": resource}})
        except orca_adapter.AdapterError as exc:
            assert exc.details["code"] == "correlation_conflict"
        else:
            raise AssertionError("conflicting terminal resource aliases must halt")
    root, lane, worktree = fixture()
    try:
        response = {"result": {"dispatch": {"id": dispatch_id, "status": "failed"}, "terminalResource": {"resourceId": "wtr-r16", "terminalHandle": "term-A", "status": "live", "connected": True, "writable": True, "ownershipState": "owned"}}}
        cli = RecordingCLI([response])
        action = {"action": "worker", "key": KEY, "partial_effect": {"run_id": "run-A", "task_id": "task-A", "dispatch_id": dispatch_id, "terminal_handle": "term-A"}, "worker_plan": lane, "worktree_receipt": worktree}
        try:
            adapter(root, cli).reconcile_action(action)
        except orca_adapter.AdapterError as exc:
            assert exc.details["code"] == "recovery_stop_unproven"
        else:
            raise AssertionError("missing owner/origin must block stop")
        assert [call[0][2] for call in cli.calls] == ["worker-show"]
    finally:
        shutil.rmtree(root)


def test_r15_live_takeover_or_unsupervised_terminal_blocks_stop_and_release() -> None:
    dispatch_id = "ctx_d9be12345678"
    terminal = "term_d33912345678"
    for ownership, owner, origin in (("user_takeover", "user", "user"), ("owned", "ctx_foreign", dispatch_id)):
        root, lane, worktree = fixture()
        try:
            response = {"result": {"dispatch": {"id": dispatch_id, "status": "failed"}, "terminal": {"handle": terminal, "status": "running", "connected": True, "writable": True}, "terminalResource": {"id": "wtr-r15", "ownershipState": ownership, "owner": {"dispatchId": owner}, "origin": {"dispatchId": origin}}}}
            cli = RecordingCLI([response])
            action = {"action": "worker", "key": KEY, "partial_effect": {"run_id": "run-A", "task_id": "task-A", "dispatch_id": dispatch_id, "terminal_handle": terminal}, "worker_plan": lane, "worktree_receipt": worktree}
            try:
                adapter(root, cli).reconcile_action(action)
            except orca_adapter.AdapterError as exc:
                assert exc.details["code"] in {"recovery_stop_unproven", "correlation_conflict"}
            else:
                raise AssertionError("takeover or foreign-owned live terminal must block")
            assert [call[0][2] for call in cli.calls] == ["worker-show"]
        finally:
            shutil.rmtree(root)


def test_retained_release_evidence_blocks_live_recovery_before_stop() -> None:
    dispatch_id = "ctx_d9be12345678"
    terminal = "term_d33912345678"
    for persisted, resource_state in ((True, "not_requested"), (False, "retained")):
        root, lane, worktree = fixture()
        try:
            response = {"result": {"dispatch": {"id": dispatch_id, "status": "failed"}, "terminal": {"handle": terminal, "status": "running", "connected": True, "writable": True}, "terminalResource": {"id": "wtr-r15", "ownershipState": "owned", "owner": {"dispatchId": dispatch_id}, "origin": {"dispatchId": dispatch_id}, "releaseState": resource_state, "retainedReason": "identity_unproven"}}}
            cli = RecordingCLI([response])
            partial = {"run_id": "run-A", "task_id": "task-A", "dispatch_id": dispatch_id, "terminal_handle": terminal}
            if persisted:
                partial.update({"releaseState": "retained", "retainedReason": "identity_unproven", "lastError": "tab_not_found"})
            action = {"action": "worker", "key": KEY, "partial_effect": partial, "worker_plan": lane, "worktree_receipt": worktree}
            try:
                adapter(root, cli).reconcile_action(action)
            except orca_adapter.AdapterError as exc:
                assert exc.details["code"] == "release_identity_unproven"
                assert exc.details["releaseState"] == "retained"
                assert exc.details["retainedReason"] == "identity_unproven"
            else:
                raise AssertionError("retained release evidence must block before stop")
            assert [call[0][2] for call in cli.calls] == ["worker-show"]
        finally:
            shutil.rmtree(root)


def test_r15_post_stop_running_terminal_blocks_before_release_or_retry() -> None:
    root, lane, worktree = fixture()
    dispatch_id = "ctx_d9be12345678"
    terminal = "term_d33912345678"
    try:
        show_live = {"result": {"dispatch": {"id": dispatch_id, "status": "failed"}, "terminal": {"handle": terminal, "status": "running", "connected": True, "writable": True}, "terminalResource": {"id": "wtr-r15", "ownershipState": "owned", "owner": {"dispatchId": dispatch_id}, "origin": {"dispatchId": dispatch_id}}}}
        stop = {"result": {"stopped": True, "dispatch": {"id": dispatch_id, "status": "stopped"}}}
        post_running = {"result": {"dispatch": {"id": dispatch_id, "status": "stopped"}, "terminal": {"handle": terminal, "status": "running", "connected": False, "writable": False}, "terminalResource": {"id": "wtr-r15", "ownershipState": "owned", "owner": {"dispatchId": dispatch_id}, "origin": {"dispatchId": dispatch_id}}}}
        cli = RecordingCLI([show_live, stop, post_running])
        action = {"action": "worker", "key": KEY, "partial_effect": {"run_id": "run-A", "task_id": "task-A", "dispatch_id": dispatch_id, "terminal_handle": terminal}, "worker_plan": lane, "worktree_receipt": worktree}
        try:
            adapter(root, cli).reconcile_action(action)
        except orca_adapter.AdapterError as exc:
            assert exc.details["code"] == "recovery_stop_unproven"
        else:
            raise AssertionError("post-stop running terminal must block")
        assert [call[0][2] for call in cli.calls] == ["worker-show", "worker-stop", "worker-show"]
    finally:
        shutil.rmtree(root)


def test_r15_pending_stop_receipt_reuses_exact_request_on_restart() -> None:
    root, lane, worktree = fixture()
    dispatch_id = "ctx_d9be12345678"
    terminal = "term_d33912345678"
    request = KEY + ":recovery-stop"
    try:
        def show(status: str, connected: bool, writable: bool) -> dict[str, object]:
            return {"result": {"dispatch": {"id": dispatch_id, "status": status}, "terminal": {"handle": terminal, "status": "running" if connected else "exited", "connected": connected, "writable": writable}, "terminalResource": {"id": "wtr-r15", "ownershipState": "owned", "owner": {"dispatchId": dispatch_id}, "origin": {"dispatchId": dispatch_id}}}}

        cli = RecordingCLI([show("failed", True, True), {"result": {"stopped": True, "dispatch": {"id": dispatch_id, "status": "stopped"}}}, show("stopped", False, False), {"released": True, "dispatch_id": dispatch_id}, {"worktree_path": worktree["worktree_path"]}, {**worker_payload(worktree), "dispatch_id": dispatch_id, "terminal_handle": terminal}])
        action = {"action": "worker", "key": KEY, "partial_effect": {"run_id": "run-A", "task_id": "task-A", "dispatch_id": dispatch_id, "terminal_handle": terminal, "recovery_stop": {"status": "pending", "dispatch_id": dispatch_id, "retry_request": request}}, "worker_plan": lane, "worktree_receipt": worktree}
        receipt = adapter(root, cli).reconcile_action(action)
        assert receipt is not None
        stop_call = cli.calls[1][0]
        assert stop_call[stop_call.index("--retry-request") + 1] == request
        assert [call[0][2] for call in cli.calls].count("worker-stop") == 1
    finally:
        shutil.rmtree(root)


def test_r15_stop_failure_blocks_without_release_or_retry() -> None:
    root, lane, worktree = fixture()
    dispatch_id = "ctx_d9be12345678"
    terminal = "term_d33912345678"
    try:
        show = {"result": {"dispatch": {"id": dispatch_id, "status": "failed"}, "terminal": {"handle": terminal, "status": "running", "connected": True, "writable": True}, "terminalResource": {"id": "wtr-r15", "ownershipState": "owned", "owner": {"dispatchId": dispatch_id}, "origin": {"dispatchId": dispatch_id}}}}
        failed_stop = {"result": {"stopped": False, "dispatch": {"id": dispatch_id, "status": "failed"}, "error": "stop_failed"}}
        cli = RecordingCLI([show, failed_stop])
        action = {"action": "worker", "key": KEY, "partial_effect": {"run_id": "run-A", "task_id": "task-A", "dispatch_id": dispatch_id, "terminal_handle": terminal}, "worker_plan": lane, "worktree_receipt": worktree}
        try:
            adapter(root, cli).reconcile_action(action)
        except orca_adapter.AdapterError as exc:
            assert exc.details["code"] == "recovery_stop_failed"
        else:
            raise AssertionError("failed stop must block recovery")
        assert [call[0][2] for call in cli.calls] == ["worker-show", "worker-stop"]
    finally:
        shutil.rmtree(root)


def test_running_stalled_dispatch_fails_safely_without_release_or_retry() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI([{"dispatch_id": "dispatch-A", "status": "running", "terminal_handle": "terminal-A"}])
        try:
            adapter(root, cli).reconcile_action({
                "action": "worker", "key": KEY,
                "partial_effect": {"run_id": "run-A", "task_id": "task-A", "dispatch_id": "dispatch-A", "terminal_handle": "terminal-A"},
                "worker_plan": lane, "worktree_receipt": worktree,
            })
        except orca_adapter.AdapterError as exc:
            assert exc.details["code"] == "worker_still_live"
        else:
            raise AssertionError("running stalled dispatch must not be retried")
        commands = [call[0][2] for call in cli.calls]
        assert commands == ["worker-show"]
        assert "worker-release" not in commands and "worker-start" not in commands
    finally:
        shutil.rmtree(root)


def test_persisted_release_receipt_allows_retry_when_dispatch_status_is_released() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI([
            {"dispatch_id": "dispatch-A", "status": "released", "terminal_handle": "terminal-A"},
            {"worktree_path": worktree["worktree_path"]},
            worker_payload(worktree),
        ])
        worker = adapter(root, cli)
        action = {
            "action": "worker", "key": KEY,
            "partial_effect": {
                "run_id": "run-A", "task_id": "task-A", "dispatch_id": "dispatch-A", "terminal_handle": "terminal-A",
                "recovery_release": {"released": True, "dispatch_id": "dispatch-A", "idempotency_key": KEY + ":recovery-release"},
            },
            "worker_plan": lane, "worktree_receipt": worktree,
        }
        receipt = worker.reconcile_action(action)
        assert receipt is not None and receipt["run_id"] == "run-A"
        assert [call[0][2] for call in cli.calls] == ["worker-show", "show", "worker-start"]
    finally:
        shutil.rmtree(root)


def test_nested_worker_show_missing_dispatch_id_halts_before_release_or_retry() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI([{"result": {"dispatch": {"status": "failed"}}}])
        try:
            adapter(root, cli).reconcile_action({
                "action": "worker", "key": KEY,
                "partial_effect": {"run_id": "run-A", "task_id": "task-A", "dispatch_id": "ctx_5f619d0f6298", "terminal_handle": "terminal-A"},
                "worker_plan": lane, "worktree_receipt": worktree,
            })
        except orca_adapter.AdapterError as exc:
            assert exc.details["code"] == "uncorrelated_dispatch"
        else:
            raise AssertionError("missing worker-show dispatch identity must halt recovery")
        assert [call[0][2] for call in cli.calls] == ["worker-show"]
    finally:
        shutil.rmtree(root)


def test_restart_normalizes_nested_persisted_partial_effect_and_retries_exact_ctx_task() -> None:
    root, lane, worktree = fixture()
    dispatch_id = "ctx_5f619d0f6298"
    try:
        cli = RecordingCLI([
            {"result": {"dispatch": {"id": dispatch_id, "status": "failed"}, "worker": {"agent_terminal_handle": "terminal-A"}, "terminal": {"handle": "terminal-A"}, "terminalResource": {"terminalHandle": "terminal-A"}}},
            {"result": {"dispatch": {"id": dispatch_id, "released": True}}},
            {"worktree_path": worktree["worktree_path"]},
            worker_payload(worktree),
        ])
        action = {
            "action": "worker", "key": KEY,
            "partial_effect": {"result": {"runId": "run-A", "taskId": "task-A", "dispatchId": dispatch_id, "terminalHandle": "terminal-A"}},
            "worker_plan": lane, "worktree_receipt": worktree,
        }
        receipt = adapter(root, cli).reconcile_action(action)
        assert receipt is not None and receipt["run_id"] == "run-A" and receipt["task_id"] == "task-A"
        assert [call[0][2] for call in cli.calls] == ["worker-show", "worker-release", "show", "worker-start"]
        worker_start = cli.calls[-1][0]
        assert worker_start[worker_start.index("--retry-of") + 1] == dispatch_id
        assert action["partial_effect"]["dispatch_id"] == dispatch_id  # type: ignore[index]
        assert action["partial_effect"]["terminal_handle"] == "terminal-A"  # type: ignore[index]
    finally:
        shutil.rmtree(root)


def test_restart_persists_authoritative_terminal_before_release_and_replays_idempotently() -> None:
    root, lane, worktree = fixture()
    dispatch_id = "ctx_5f619d0f6298"
    terminal = "term_2dcb9465-d91c-4260-baa3-b92859412439"
    try:
        worker = {**worker_payload(worktree), "dispatch_id": dispatch_id, "terminal_handle": terminal}
        action = {
            "action": "worker", "key": KEY,
            "partial_effect": {"result": {"runId": "run-A", "taskId": "task-A", "dispatchId": dispatch_id}},
            "worker_plan": lane, "worktree_receipt": worktree,
        }
        assert "terminal_handle" not in json.dumps(action["partial_effect"])

        class ObservingCLI(RecordingCLI):
            def __call__(self, argv: list[str], **kwargs: object) -> Completed:
                if len(argv) > 2 and argv[2] == "worker-release":
                    assert action["partial_effect"]["terminal_handle"] == terminal  # type: ignore[index]
                return super().__call__(argv, **kwargs)

        cli = ObservingCLI([
            {"result": {"dispatch": {"id": dispatch_id, "status": "failed"}, "worker": {"agent_terminal_handle": terminal}}},
            {"result": {"dispatch": {"id": dispatch_id, "released": True}}},
            {"worktree_path": worktree["worktree_path"]},
            worker,
        ])
        adapter_instance = adapter(root, cli)
        receipt = adapter_instance.reconcile_action(action)
        assert receipt is not None and receipt["run_id"] == "run-A" and receipt["task_id"] == "task-A"
        assert action["partial_effect"]["terminal_handle"] == terminal  # type: ignore[index]
        assert [call[0][2] for call in cli.calls] == ["worker-show", "worker-release", "show", "worker-start"]
        retry_args = cli.calls[-1][0]
        assert retry_args[retry_args.index("--retry-of") + 1] == dispatch_id
        assert retry_args[retry_args.index("--task") + 1] == "task-A"
        assert adapter_instance.reconcile_action(action) == receipt
        assert len(cli.calls) == 4
    finally:
        shutil.rmtree(root)


def test_tab_not_found_release_reconciles_exited_terminal_and_retries_once() -> None:
    root, lane, worktree = fixture()
    dispatch_id = "ctx_5f619d0f6298"
    terminal = "term_2dcb9465-d91c-4260-baa3-b92859412439"
    def show(*, status: str, connected: bool, writable: bool, handle: str = terminal) -> dict[str, object]:
        return {"result": {"dispatch": {"id": dispatch_id, "status": status}, "terminal": {"handle": handle, "status": "exited", "connected": connected, "writable": writable}}}
    tab_error = subprocess.CalledProcessError(
        1, ["orca", "orchestration", "worker-release"],
        output=json.dumps({"ok": False, "error": {"code": "tab_not_found", "dispatch": {"id": dispatch_id}, "terminal": {"handle": terminal}}}),
    )
    try:
        worker = {**worker_payload(worktree), "dispatch_id": dispatch_id, "terminal_handle": terminal}
        evidence = {
            "state": "failed",
            "lastError": "tab_not_found",
            "releaseState": "completed",
            "releaseError": "tab_not_found",
            "released": True,
            "reconciled": True,
            "terminal_status": "exited",
            "connected": False,
            "writable": False,
            "reason": "tab_not_found",
            "release_error": "tab_not_found",
            "mutation": {
                "requestId": KEY + ":recovery-release",
                "processAction": {"action": "worker-release", "dispatch_id": dispatch_id},
                "archive": {"kind": "recovery-release", "dispatch_id": dispatch_id},
            },
            "release": {"state": "completed", "requested": True, "completed": True},
        }
        action = {
            "action": "worker", "key": KEY,
            "partial_effect": {
                "run_id": "run-A", "task_id": "task-A", "dispatch_id": dispatch_id, "terminal_handle": terminal,
                "result": {"dispatchId": dispatch_id, **evidence},
            },
            "worker_plan": lane, "worktree_receipt": worktree,
        }

        def assert_evidence() -> None:
            partial = action["partial_effect"]
            for field in (
                "state", "lastError", "releaseState", "releaseError", "released", "reconciled",
                "terminal_status", "connected", "writable", "reason", "release_error",
            ):
                assert partial[field] == evidence[field]
            assert partial["run_id"] == "run-A"
            assert partial["task_id"] == "task-A"
            assert partial["dispatch_id"] == dispatch_id
            assert partial["terminal_handle"] == terminal
            assert partial["request_id"] == KEY + ":recovery-release"
            assert partial["result"]["mutation"] == evidence["mutation"]  # type: ignore[index]
            assert partial["result"]["release"] == evidence["release"]  # type: ignore[index]

        class ObservingCLI(RecordingCLI):
            def __call__(self, argv: list[str], **kwargs: object) -> Completed:
                if len(argv) > 2 and argv[2] == "worker-release":
                    assert_evidence()
                return super().__call__(argv, **kwargs)

        cli = ObservingCLI([show(status="failed", connected=False, writable=False), tab_error, show(status="failed", connected=False, writable=False), {"worktree_path": worktree["worktree_path"]}, worker])
        adapter_instance = adapter(root, cli)
        receipt = adapter_instance.reconcile_action(action)
        assert_evidence()
        release = action["partial_effect"]["recovery_release"]  # type: ignore[index]
        assert release == {
            "released": True,
            "reconciled": True,
            "idempotency_key": KEY + ":recovery-release",
            "reason": "tab_not_found",
            "error": "tab_not_found",
            "release_error": "tab_not_found",
            "dispatch_id": dispatch_id,
            "terminal_handle": terminal,
            "terminal_status": "exited",
            "connected": False,
            "writable": False,
        }
        assert receipt is not None and receipt["run_id"] == "run-A" and receipt["task_id"] == "task-A"
        assert [call[0][2] for call in cli.calls] == ["worker-show", "worker-release", "worker-show", "show", "worker-start"]
        assert cli.calls[-1][0][cli.calls[-1][0].index("--retry-of") + 1] == dispatch_id
        cli.responses.append({"deliveries": [{
            "id": "late-delivery", "run_id": "run-A", "type": "worker_done", "from_handle": terminal,
            "payload": json.dumps({"taskId": "task-A", "dispatchId": dispatch_id, "outcome": "succeeded"}),
        }]})
        try:
            adapter_instance.wait_events(receipt)
        except orca_adapter.AdapterError as exc:
            assert "stale" in str(exc)
        else:
            raise AssertionError("reconciled release must revoke late delivery")
        assert adapter_instance.reconcile_action(action) == receipt
        assert_evidence()
        assert len(cli.calls) == 6
    finally:
        shutil.rmtree(root)


def test_tab_not_found_postcheck_live_unknown_or_mismatched_blocks_retry() -> None:
    cases = (
        {"status": "failed", "connected": True, "writable": True},
        {"status": "failed", "connected": False, "writable": True},
        {"status": "failed", "connected": False, "writable": False, "handle": "term-other"},
        {"status": "unknown", "connected": False, "writable": False},
        {"status": "failed", "connected": False, "writable": False, "post_dispatch": None},
        {"status": "failed", "connected": False, "writable": False, "post_dispatch": "ctx_foreign"},
    )
    for post in cases:
        root, lane, worktree = fixture()
        dispatch_id = "ctx_5f619d0f6298"
        terminal = "term_2dcb9465-d91c-4260-baa3-b92859412439"
        try:
            def show(status, connected, writable, handle=terminal, post_dispatch=dispatch_id):
                dispatch = {"status": status}
                if post_dispatch is not None:
                    dispatch["id"] = post_dispatch
                return {"result": {"dispatch": dispatch, "terminalHandle": handle, "terminal": {"handle": handle, "status": "exited", "connected": connected, "writable": writable}}}

            tab_error = subprocess.CalledProcessError(1, ["orca", "worker-release"], output=json.dumps({"ok": False, "error": {"code": "tab_not_found", "dispatch": {"id": dispatch_id}}}))
            cli = RecordingCLI([show("failed", False, False), tab_error, show(post["status"], post["connected"], post["writable"], post.get("handle", terminal), post.get("post_dispatch", dispatch_id))])
            action = {"action": "worker", "key": KEY, "partial_effect": {"run_id": "run-A", "task_id": "task-A", "dispatch_id": dispatch_id, "terminal_handle": terminal}, "worker_plan": lane, "worktree_receipt": worktree}
            worker = adapter(root, cli)
            try:
                worker.reconcile_action(action)
            except orca_adapter.AdapterError as exc:
                assert exc.details["code"] == "release_unknown"
            else:
                raise AssertionError("ambiguous tab_not_found post-check must block retry")
            assert [call[0][2] for call in cli.calls] == ["worker-show", "worker-release", "worker-show"]
            assert "recovery_release" not in action["partial_effect"]
            assert dispatch_id not in worker._revoked_dispatches
        finally:
            shutil.rmtree(root)


def test_malformed_nested_persisted_dispatch_id_halts_before_worker_show_mutation() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI([])
        try:
            adapter(root, cli).reconcile_action({
                "action": "worker", "key": KEY,
                "partial_effect": {"result": {"runId": "run-A", "taskId": "task-A", "dispatch": {"id": "ctx bad", "status": "failed"}, "terminalHandle": "terminal-A"}},
                "worker_plan": lane, "worktree_receipt": worktree,
            })
        except orca_adapter.AdapterError:
            pass
        else:
            raise AssertionError("malformed persisted dispatch identity must halt")
        assert cli.calls == []
    finally:
        shutil.rmtree(root)


def test_worker_show_missing_malformed_or_conflicting_terminal_halts_before_release_or_retry() -> None:
    cases = (
        ({"result": {"dispatch": {"id": "ctx_5f619d0f6298", "status": "failed"}}}, None),
        ({"result": {"dispatch": {"id": "ctx_5f619d0f6298", "status": "failed"}, "terminal": {"handle": "term bad"}}}, None),
        ({"result": {"dispatch": {"id": "ctx_5f619d0f6298", "status": "failed"}, "terminal": {"handle": "term_new"}}}, "term_old"),
    )
    for show_response, persisted_terminal in cases:
        root, lane, worktree = fixture()
        try:
            cli = RecordingCLI([show_response])
            partial = {"run_id": "run-A", "task_id": "task-A", "dispatch_id": "ctx_5f619d0f6298"}
            if persisted_terminal is not None:
                partial["terminal_handle"] = persisted_terminal
            try:
                adapter(root, cli).reconcile_action({
                    "action": "worker", "key": KEY,
                    "partial_effect": partial, "worker_plan": lane, "worktree_receipt": worktree,
                })
            except orca_adapter.AdapterError as exc:
                assert exc.details["code"] == "uncorrelated_terminal"
            else:
                raise AssertionError("invalid worker-show terminal must halt recovery")
            assert [call[0][2] for call in cli.calls] == ["worker-show"]
        finally:
            shutil.rmtree(root)


def test_delivery_from_revoked_dispatch_is_rejected_as_stale() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI([{"released": True, "dispatch_id": "dispatch-A"}, {"deliveries": [live_delivery()]}])
        worker = adapter(root, cli)
        receipt = {**worker_payload(worktree), "orchestration_task_id": "task-A"}
        release = worker.release(receipt, {"accepted": True})
        assert release["released"] is True
        try:
            worker.wait_events(receipt)
        except orca_adapter.AdapterError as exc:
            assert "stale" in str(exc)
        else:
            raise AssertionError("revoked dispatch delivery must be rejected")
    finally:
        shutil.rmtree(root)


def test_retained_release_preserves_identity_unproven_evidence_and_replays_without_effect() -> None:
    root, lane, worktree = fixture()
    dispatch_id = "ctx_5f619d0f6298"
    terminal = "term_2dcb9465-d91c-4260-baa3-b92859412439"
    try:
        response = {"result": {
            "code": "identity_unproven", "state": "retained", "releaseState": "retained",
            "ownershipState": "owned", "retainedReason": "identity_unproven",
            "releaseError": "identity_unproven", "releaseRequestedAt": "2026-08-25T05:00:00Z",
            "releaseCompletedAt": None, "released": False, "requestId": KEY + ":recovery-release",
            "dispatch": {"id": dispatch_id, "status": "failed"},
            "terminal": {"handle": terminal}, "resource": {"id": "resource-A"},
        }}
        cli = RecordingCLI([response])
        worker = adapter(root, cli)
        receipt = {**worker_payload(worktree), "dispatch_id": dispatch_id, "terminal_handle": terminal}
        try:
            worker.release(receipt, {"accepted": True})
        except orca_adapter.AdapterError as exc:
            assert exc.details["code"] == "release_identity_unproven"
            assert exc.details["provider_code"] == "identity_unproven"
            for field, expected in {
                "state": "retained", "releaseState": "retained", "ownershipState": "owned",
                "retainedReason": "identity_unproven", "releaseError": "identity_unproven",
                "releaseRequestedAt": "2026-08-25T05:00:00Z", "releaseCompletedAt": None,
                "request_id": KEY + ":recovery-release", "dispatch_id": dispatch_id,
                "terminal_handle": terminal, "resource_id": "resource-A",
            }.items():
                assert exc.details[field] == expected
            assert exc.details["result"]["dispatch"]["id"] == dispatch_id  # type: ignore[index]
        else:
            raise AssertionError("retained identity-unproven release must remain blocked")
        assert [call[0][2] for call in cli.calls] == ["worker-release"]
        try:
            worker.release(receipt, {"accepted": True})
        except orca_adapter.AdapterError as exc:
            assert exc.details["code"] == "release_identity_unproven"
            assert exc.details["idempotent"] is True
        else:
            raise AssertionError("replayed retained release must remain blocked")
        assert len(cli.calls) == 1
        assert dispatch_id not in worker._revoked_dispatches
    finally:
        shutil.rmtree(root)


def test_r10_real_retained_failure_promotes_nested_aliases_and_replays_stably() -> None:
    root, lane, worktree = fixture()
    dispatch_id = "ctx_5f619d0f6298"
    terminal = "term_2dcb9465-d91c-4260-baa3-b92859412439"
    request_id = "req-r10"
    try:
        failure = subprocess.CalledProcessError(
            1,
            ["orca", "orchestration", "worker-release"],
            output=json.dumps({
                "_meta": {"runtimeId": "runtime-A"}, "ok": True,
                "code": "release_not_accepted", "dispatch_id": dispatch_id,
                "idempotency_key": KEY + ":recovery-release", "lastError": "tab_not_found",
                "message": "selector_not_found", "reason": "identity_unproven", "request_id": request_id,
                "result": {
                    "archive": {"source": "transcript", "status": "captured"},
                    "dispatchId": dispatch_id,
                    "mutation": {"replayed": False, "requestId": request_id},
                    "processAction": "none", "reason": "identity_unproven", "state": "retained",
                    "retained_reason": "identity_unproven", "release_state": "retained",
                    "ownership_state": "owned", "release_error": "tab_not_found",
                },
                "state": "retained", "status": "retained", "run_id": "run-A", "task_id": "task-A",
                "terminal_handle": terminal,
            }),
        )
        cli = RecordingCLI([failure])
        worker = adapter(root, cli)
        receipt = {**worker_payload(worktree), "dispatch_id": dispatch_id, "terminal_handle": terminal}
        try:
            worker.release(receipt, {"accepted": True})
        except orca_adapter.AdapterError as exc:
            assert exc.details["code"] == "release_identity_unproven"
            assert exc.details["provider_code"] == "release_not_accepted"
            for field, expected in {
                "state": "retained", "status": "retained", "releaseState": "retained",
                "retainedReason": "identity_unproven", "ownershipState": "owned",
                "releaseError": "tab_not_found", "reason": "identity_unproven",
                "lastError": "tab_not_found", "message": "selector_not_found",
                "request_id": request_id, "dispatch_id": dispatch_id, "terminal_handle": terminal,
            }.items():
                assert exc.details[field] == expected
            assert exc.details["result"]["mutation"] == {"replayed": False, "requestId": request_id}  # type: ignore[index]
            assert exc.details["result"]["archive"] == {"source": "transcript", "status": "captured"}  # type: ignore[index]
            assert exc.details["result"]["processAction"] == "none"  # type: ignore[index]
        else:
            raise AssertionError("R10 retained release must be a stable structured failure")
        try:
            worker.release(receipt, {"accepted": True})
        except orca_adapter.AdapterError as exc:
            assert exc.details["code"] == "release_identity_unproven"
            assert exc.details["idempotent"] is True
            assert exc.details["request_id"] == request_id
        else:
            raise AssertionError("R10 replay must remain blocked")
        assert len(cli.calls) == 1
        assert dispatch_id not in worker._revoked_dispatches
    finally:
        shutil.rmtree(root)


def test_release_state_completed_is_explicitly_correlated_and_idempotent() -> None:
    root, lane, worktree = fixture()
    dispatch_id = "ctx_5f619d0f6298"
    terminal = "term_2dcb9465-d91c-4260-baa3-b92859412439"
    try:
        cli = RecordingCLI([{"result": {"releaseState": "completed", "ownershipState": "owned", "dispatch": {"id": dispatch_id}, "terminal": {"handle": terminal}, "resource": {"id": "resource-A"}}}])
        worker = adapter(root, cli)
        receipt = {**worker_payload(worktree), "dispatch_id": dispatch_id, "terminal_handle": terminal}
        released = worker.release(receipt, {"accepted": True})
        assert released["released"] is True and released["dispatch_id"] == dispatch_id
        assert worker.release(receipt, {"accepted": True})["idempotent"] is True
        assert len(cli.calls) == 1
    finally:
        shutil.rmtree(root)


def test_release_identity_missing_or_foreign_blocks_without_revocation() -> None:
    dispatch_id = "ctx_5f619d0f6298"
    for response in (
        {"result": {"releaseState": "retained", "ownershipState": "owned", "dispatch": {"status": "failed"}}},
        {"result": {"releaseState": "retained", "ownershipState": "owned", "dispatch": {"id": "ctx_foreign"}}},
    ):
        root, lane, worktree = fixture()
        try:
            cli = RecordingCLI([response])
            worker = adapter(root, cli)
            receipt = {**worker_payload(worktree), "dispatch_id": dispatch_id}
            try:
                worker.release(receipt, {"accepted": True})
            except orca_adapter.AdapterError as exc:
                assert exc.details.get("code") == "uncorrelated_release"
            else:
                raise AssertionError("missing or foreign release identity must block")
            assert len(cli.calls) == 1
            assert dispatch_id not in worker._revoked_dispatches
        finally:
            shutil.rmtree(root)


def test_retained_reconcile_persists_structured_failure_without_retry_effect() -> None:
    root, lane, worktree = fixture()
    dispatch_id = "ctx_5f619d0f6298"
    terminal = "term_2dcb9465-d91c-4260-baa3-b92859412439"
    try:
        cli = RecordingCLI([
            {"result": {"dispatch": {"id": dispatch_id, "status": "failed"}, "terminal": {"handle": terminal, "status": "exited", "connected": False, "writable": False}}},
            {"result": {"code": "identity_unproven", "state": "retained", "releaseState": "retained", "ownershipState": "owned", "retainedReason": "identity_unproven", "releaseError": "identity_unproven", "dispatch": {"id": dispatch_id}, "terminal": {"handle": terminal}}},
        ])
        action = {"action": "worker", "key": KEY, "partial_effect": {"run_id": "run-A", "task_id": "task-A", "dispatch_id": dispatch_id, "terminal_handle": terminal}, "worker_plan": lane, "worktree_receipt": worktree}
        first_worker = adapter(root, cli)
        try:
            first_worker.reconcile_action(action)
        except orca_adapter.AdapterError as exc:
            assert exc.details["code"] == "release_identity_unproven"
            persisted = {
                **action,
                "partial_effect": {**action["partial_effect"], **dict(exc.details)},
            }
        else:
            raise AssertionError("retained release must not retry")
        assert [call[0][2] for call in cli.calls] == ["worker-show", "worker-release"]
        assert not any(call[0][2] in {"show", "worker-start"} for call in cli.calls)
        replay_cli = RecordingCLI([{"result": {"dispatch": {"id": dispatch_id, "status": "failed"}, "terminal": {"handle": terminal}}}])
        try:
            adapter(root, replay_cli).reconcile_action(persisted)
        except orca_adapter.AdapterError as exc:
            assert exc.details["code"] == "release_identity_unproven"
            assert exc.details["idempotent"] is True
            assert exc.details["idempotency_key"] == KEY + ":recovery-release"
        else:
            raise AssertionError("persisted retained failure must remain blocked on restart")
        assert [call[0][2] for call in replay_cli.calls] == ["worker-show"]
    finally:
        shutil.rmtree(root)


def test_start_reuses_run_task_and_worker_by_idempotency_without_duplicate_effect() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI(start_responses(worktree))
        worker = adapter(root, cli)
        first = worker.start_worker(lane, worktree, idempotency_key=KEY)
        second = worker.start_worker(lane, worktree, idempotency_key=KEY)
        assert second == first
        assert len(cli.calls) == 6
        duplicate = dict(worktree, worktree_id="wt-duplicate")
        try:
            worker.start_worker(lane, duplicate, idempotency_key=KEY)
        except orca_adapter.AdapterError as exc:
            assert "idempotency" in str(exc)
        else:
            raise AssertionError("duplicate worktree receipt must halt")
    finally:
        shutil.rmtree(root)


def test_worker_done_is_read_before_release_and_transcript_is_redacted() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI(start_responses(worktree) + [{"deliveries": [live_delivery()]}, live_worker_output(), {"released": True, "dispatch_id": "dispatch-A"}])
        worker = adapter(root, cli)
        receipt = worker.start_worker(lane, worktree, idempotency_key=KEY)
        delivery = worker.wait_events(receipt)
        result = worker.read_worker(receipt)
        accepted = worker.accept_worker_done(receipt, delivery, result)
        released = worker.release(receipt, accepted)
        assert result["dispatch_id"] == "dispatch-A"
        assert result["transcript"] == "<redacted>"
        assert "secret worker transcript" not in json.dumps(result)
        assert released["released"] is True
        assert [call[0][2] for call in cli.calls[-3:]] == ["check", "worker-read", "worker-release"]
    finally:
        shutil.rmtree(root)


def test_clean_waiter_ends_turn_and_follow_up_reuses_terminal_after_dependency_event() -> None:
    root, lane, worktree = fixture()
    try:
        waiter = {
            "id": "delivery-wait", "run_id": "run-A", "type": "question", "from_handle": "terminal-A",
            "payload": json.dumps({"taskId": "task-A", "dispatchId": "dispatch-A", "outcome": "waiting", "status": "waiting", "dependency": "producer-A"}),
        }
        cli = RecordingCLI(
            start_responses(worktree)
            + [{"deliveries": [waiter]}, worker_payload(worktree)]
        )
        worker = adapter(root, cli)
        receipt = worker.start_worker(lane, worktree, idempotency_key=KEY)
        observed = worker.wait_events(receipt, timeout=5)
        worker.end_waiter(receipt, observed)
        dependency = {"event": "dependency", "dependency": "producer-A", **worker_payload(worktree), "status": "complete"}
        follow_up = worker.follow_up(receipt, observed, dependency)
        assert observed["event"] == "waiting"
        assert follow_up["terminal_handle"] == "terminal-A"
        follow_call = cli.calls[-1][0]
        assert follow_call[2] == "worker-start"
        assert follow_call[follow_call.index("--terminal") + 1] == "terminal-A"
        restarted = adapter(root, RecordingCLI([worker_payload(worktree)]))
        persisted_waiter = {**observed, "ended": True}
        restarted_follow_up = restarted.follow_up(receipt, persisted_waiter, dependency)
        assert restarted_follow_up["terminal_handle"] == "terminal-A"
    finally:
        shutil.rmtree(root)


def test_wait_timeout_is_blocking_and_leaves_no_follow_up_effect() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI(start_responses(worktree) + [{"events": [], "timeout": True}])
        worker = adapter(root, cli)
        receipt = worker.start_worker(lane, worktree, idempotency_key=KEY)
        result = worker.wait_events(receipt, timeout=1)
        assert result == {"event": "timeout", "unchanged": True}
        assert [call[0][2] for call in cli.calls[-1:]] == ["check"]
        assert not any(call[0][2] in {"send", "worker-start", "worker-release"} for call in cli.calls[-1:])
    finally:
        shutil.rmtree(root)


def test_live_delivery_is_run_scoped_and_worker_read_is_a_separate_schema() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI(start_responses(worktree) + [{"deliveries": [live_delivery()]}, live_worker_output(), {"released": True, "dispatch_id": "dispatch-A"}])
        worker = adapter(root, cli)
        receipt = worker.start_worker(lane, worktree, idempotency_key=KEY)
        delivery = worker.wait_events(receipt, timeout=5)
        output = worker.read_worker(receipt)
        accepted = worker.accept_worker_done(receipt, delivery, output)
        worker.release(receipt, accepted)
        assert delivery["delivery_id"] == "delivery-A"
        assert delivery["payload"]["taskId"] == "task-A"
        assert output["source_identity"] == "terminal-A"
        assert output["transcript"] == "<redacted>"
        assert [call[0][2] for call in cli.calls[-3:]] == ["check", "worker-read", "worker-release"]
        check_call = cli.calls[-3][0]
        assert check_call[check_call.index("--run") + 1] == "run-A"
        assert "--terminal" not in check_call
    finally:
        shutil.rmtree(root)


def test_invalid_worker_result_cannot_release_or_persist_transcript() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI(start_responses(worktree))
        worker = adapter(root, cli)
        receipt = worker.start_worker(lane, worktree, idempotency_key=KEY)
        try:
            worker.release(receipt, {"accepted": False, "transcript": "secret"})
        except orca_adapter.AdapterError as exc:
            assert "accepted" in str(exc)
        else:
            raise AssertionError("invalid result must halt before release")
        assert not any(call[0][2] == "worker-release" for call in cli.calls)
        assert "secret" not in json.dumps(receipt)
    finally:
        shutil.rmtree(root)


def test_nested_delivery_credentials_are_redacted_before_adapter_returns_payload() -> None:
    root, lane, worktree = fixture()
    try:
        delivery = live_delivery()
        delivery["payload"] = json.dumps({
            "taskId": "task-A", "dispatchId": "dispatch-A", "outcome": "waiting", "status": "waiting",
            "dependency": "password=dependency-secret", "environment": {"TOKEN": "secret-token"},
            "nested": {"credentials": {"password": "secret-password", "access_token": "access-secret", "refresh_token": "refresh-secret", "api_key": "api-secret", "client_secret": "client-secret", "cookie": "cookie-secret"}},
        })
        delivery["type"] = "question"
        cli = RecordingCLI(start_responses(worktree) + [{"deliveries": [delivery]}])
        worker = adapter(root, cli)
        receipt = worker.start_worker(lane, worktree, idempotency_key=KEY)
        observed = worker.wait_events(receipt)
        serialized = json.dumps(observed)
        assert observed["payload"]["environment"]["TOKEN"] == "<redacted>"
        assert observed["dependency"] == "password=<redacted>"
        assert observed["payload"]["nested"]["credentials"]["password"] == "<redacted>"
        assert observed["payload"]["nested"]["credentials"]["access_token"] == "<redacted>"
        assert observed["payload"]["nested"]["credentials"]["refresh_token"] == "<redacted>"
        assert observed["payload"]["nested"]["credentials"]["api_key"] == "<redacted>"
        assert observed["payload"]["nested"]["credentials"]["client_secret"] == "<redacted>"
        assert observed["payload"]["nested"]["credentials"]["cookie"] == "<redacted>"
        assert "secret-token" not in serialized
        assert "secret-password" not in serialized
        assert "access-secret" not in serialized
        assert "refresh-secret" not in serialized
        assert "api-secret" not in serialized
        assert "client-secret" not in serialized
        assert "cookie-secret" not in serialized
    finally:
        shutil.rmtree(root)


def test_structured_failure_redacts_credentials_inside_freeform_nested_strings() -> None:
    failure = subprocess.CalledProcessError(
        17,
        ["orca", "worker-start"],
        output=json.dumps({
            "error": {
                "code": "selector_not_found",
                "stage": "worker-start",
                "message": "code=selector_not_found password=secret token=tok api-key=api client-secret=client cookie=cookie access_token=access authorization=auth secret='quoted-secret' credential=\"quoted-credential\" Authorization: Bearer bearer-secret",
                "nested": [{"message": "Authorization Bearer list-secret token='list-token'"}],
            }
        }),
    )
    details = orca_adapter._failure_details(failure)
    serialized = json.dumps(details)
    assert details["code"] == "selector_not_found"
    assert details["stage"] == "worker-start"
    assert "password=secret" not in serialized
    assert "token=tok" not in serialized
    for redacted in (
        "password=<redacted>", "token=<redacted>", "api-key=<redacted>",
        "client-secret=<redacted>", "cookie=<redacted>", "access_token=<redacted>",
        "authorization=<redacted>", "secret='<redacted>'", "credential=\"<redacted>\"",
    ):
        assert redacted in details["message"]
    for secret in (
        "password=secret", "list-secret", "list-token", "bearer-secret", "api-key=api",
        "client-secret=client", "cookie=cookie", "access_token=access", "authorization=auth",
        "quoted-secret", "quoted-credential",
    ):
        assert secret not in serialized


def test_duplicate_delivery_is_rejected_before_follow_up_or_release() -> None:
    root, lane, worktree = fixture()
    try:
        delivery = {"deliveries": [live_delivery()]}
        cli = RecordingCLI(start_responses(worktree) + [delivery, delivery])
        worker = adapter(root, cli)
        receipt = worker.start_worker(lane, worktree, idempotency_key=KEY)
        worker.wait_events(receipt)
        try:
            worker.wait_events(receipt)
        except orca_adapter.AdapterError as exc:
            assert "duplicate" in str(exc)
        else:
            raise AssertionError("duplicate delivery must halt")
        assert not any(call[0][2] in {"worker-release", "worker-start"} for call in cli.calls[6:])
    finally:
        shutil.rmtree(root)


def test_delivery_ack_is_run_scoped_and_available_before_release() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI(start_responses(worktree) + [{"deliveries": [live_delivery()]}, {"acknowledged": True, "delivery_id": "delivery-A"}])
        worker = adapter(root, cli)
        receipt = worker.start_worker(lane, worktree, idempotency_key=KEY)
        delivery = worker.wait_events(receipt)
        ack = worker.ack_delivery(receipt, delivery)
        assert ack == {"acknowledged": True, "delivery_id": "delivery-A"}
        ack_call = cli.calls[-1][0]
        assert ack_call[2] == "check"
        assert ack_call[ack_call.index("--run") + 1] == "run-A"
        assert ack_call[ack_call.index("--ack") + 1] == "delivery-A"
    finally:
        shutil.rmtree(root)


def test_delivery_ack_requires_explicit_positive_correlated_receipt() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI(start_responses(worktree) + [{"deliveries": [live_delivery()]}, {}])
        worker = adapter(root, cli)
        receipt = worker.start_worker(lane, worktree, idempotency_key=KEY)
        delivery = worker.wait_events(receipt)
        try:
            worker.ack_delivery(receipt, delivery)
        except orca_adapter.AdapterError as exc:
            assert "acknowledgement" in str(exc)
        else:
            raise AssertionError("missing positive acknowledgement must halt")
    finally:
        shutil.rmtree(root)


def test_worker_release_requires_explicit_dispatch_ownership() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI(start_responses(worktree) + [{"released": True}])
        worker = adapter(root, cli)
        receipt = worker.start_worker(lane, worktree, idempotency_key=KEY)
        try:
            worker.release(receipt, {"accepted": True})
        except orca_adapter.AdapterError as exc:
            assert "release" in str(exc)
        else:
            raise AssertionError("release without dispatch correlation must halt")
    finally:
        shutil.rmtree(root)


def test_worker_read_rejects_foreign_source_identity() -> None:
    root, lane, worktree = fixture()
    try:
        output = live_worker_output()
        output["sourceIdentity"] = "terminal-foreign"
        cli = RecordingCLI(start_responses(worktree) + [output])
        worker = adapter(root, cli)
        receipt = worker.start_worker(lane, worktree, idempotency_key=KEY)
        try:
            worker.read_worker(receipt)
        except orca_adapter.AdapterError as exc:
            assert "source" in str(exc)
        else:
            raise AssertionError("foreign worker-read source must halt")
    finally:
        shutil.rmtree(root)


def test_duplicate_matching_runs_tasks_and_unknown_worker_fields_halt() -> None:
    root, lane, worktree = fixture()
    try:
        objective = "parallel-slice:fixture:" + KEY
        duplicate_runs = [{"run": {"id": "run-A"}, "objective": objective}, {"run": {"id": "run-B"}, "objective": objective}]
        cli = RecordingCLI([{"runs": duplicate_runs}])
        try:
            adapter(root, cli).start_worker(lane, worktree, idempotency_key=KEY)
        except orca_adapter.AdapterError as exc:
            assert "multiple" in str(exc)
        else:
            raise AssertionError("duplicate matching runs must halt")

        duplicate_tasks = [{"task": {"id": "task-A"}, "run_id": "run-A", "spec": "parallel-slice:fixture:A:T1:" + KEY}, {"task": {"id": "task-B"}, "run_id": "run-A", "spec": "parallel-slice:fixture:A:T1:" + KEY}]
        cli = RecordingCLI([
            {"runs": []}, {"run": {"id": "run-A"}, "objective": objective}, {"tasks": duplicate_tasks},
        ])
        try:
            adapter(root, cli).start_worker(lane, worktree, idempotency_key=KEY)
        except orca_adapter.AdapterError as exc:
            assert "multiple" in str(exc)
        else:
            raise AssertionError("duplicate matching tasks must halt")

        response = worker_payload(worktree)
        response["unknown"] = "value"
        cli = RecordingCLI(start_responses(worktree)[:4] + [{"worktree_path": worktree["worktree_path"]}, response])
        try:
            adapter(root, cli).start_worker(lane, worktree, idempotency_key=KEY)
        except orca_adapter.AdapterError as exc:
            assert "unknown" in str(exc)
        else:
            raise AssertionError("unknown worker field must halt")
    finally:
        shutil.rmtree(root)


def test_incomplete_start_receipt_uses_authoritative_worker_show() -> None:
    root, lane, worktree = fixture()
    try:
        start = {"run_id": "run-A", "task_id": "task-A", "dispatch_id": "dispatch-A"}
        cli = RecordingCLI(start_responses(worktree)[:4] + [{"worktree_path": worktree["worktree_path"]}, start, worker_payload(worktree)])
        receipt = adapter(root, cli).start_worker(lane, worktree, idempotency_key=KEY)
        assert [call[0][2] for call in cli.calls] == ["run-list", "run-create", "task-list", "task-create", "show", "worker-start", "worker-show"]
        assert receipt["dispatch_id"] == "dispatch-A"
    finally:
        shutil.rmtree(root)


def test_supported_nested_worker_envelope_is_removed_before_strict_validation() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI(start_responses(worktree)[:4] + [{"worktree_path": worktree["worktree_path"]}, {"worker": worker_payload(worktree)}])
        receipt = adapter(root, cli).start_worker(lane, worktree, idempotency_key=KEY)
        assert receipt["dispatch_id"] == "dispatch-A"
        assert "worker" not in receipt
    finally:
        shutil.rmtree(root)


def test_delivery_projection_drops_top_level_free_text_and_credentials() -> None:
    root, lane, worktree = fixture()
    try:
        delivery = live_delivery()
        delivery.update({"subject": "top-secret", "body": "free secret", "environment": {"api_key": "credential"}})
        cli = RecordingCLI(start_responses(worktree) + [{"deliveries": [delivery]}])
        worker = adapter(root, cli)
        receipt = worker.start_worker(lane, worktree, idempotency_key=KEY)
        observed = worker.wait_events(receipt)
        serialized = json.dumps(observed)
        assert "top-secret" not in serialized
        assert "free secret" not in serialized
        assert "credential" not in serialized
        assert set(observed) <= {"event", "status", "delivery_id", "run_id", "from_handle", "payload", "task_id", "dispatch_id", "dependency"}
    finally:
        shutil.rmtree(root)


def test_each_mandatory_worker_field_missing_from_authoritative_receipt_halts_without_cleanup() -> None:
    root, lane, worktree = fixture()
    try:
        fields = (
            "worktree_id", "worktree_path", "branch", "pre_head", "run_id",
            "task_id", "dispatch_id", "terminal_handle", "feature", "slice", "task", "idempotency_key",
        )
        for field in fields:
            response = worker_payload(worktree)
            response.pop(field, None)
            cli = RecordingCLI(start_responses(worktree)[:4] + [{"worktree_path": worktree["worktree_path"]}, response, response])
            worker = adapter(root, cli)
            try:
                worker.start_worker(lane, worktree, idempotency_key=KEY)
            except orca_adapter.AdapterError as exc:
                assert "Orca" in str(exc)
            else:
                raise AssertionError(f"missing {field} must halt")
            assert not any(call[0][2] in {"worker-release", "worker-start"} for call in cli.calls[6:])
    finally:
        shutil.rmtree(root)


def test_mismatch_dirty_duplicate_escalation_and_failure_halt_before_replacement() -> None:
    root, lane, worktree = fixture()
    try:
        cases = [
            {**live_delivery(), "payload": json.dumps({"taskId": "other-task", "dispatchId": "dispatch-A", "outcome": "succeeded"})},
            {**live_delivery(), "payload": json.dumps({"taskId": "task-A", "dispatchId": "dispatch-A", "outcome": "succeeded", "status": "dirty"})},
            {**live_delivery(), "payload": json.dumps({"taskId": "task-A", "dispatchId": "dispatch-other", "outcome": "succeeded"})},
            {**live_delivery(), "type": "escalation"},
            {**live_delivery(outcome="failed")},
        ]
        for event in cases:
            cli = RecordingCLI(start_responses(worktree) + [{"deliveries": [event]}])
            worker = adapter(root, cli)
            receipt = worker.start_worker(lane, worktree, idempotency_key=KEY)
            try:
                worker.wait_events(receipt)
            except orca_adapter.AdapterError as exc:
                assert "Orca" in str(exc)
            else:
                raise AssertionError("invalid worker receipt must halt")
            assert not any(call[0][2] == "worker-start" for call in cli.calls[6:])
    finally:
        shutil.rmtree(root)


def test_shell_is_disabled_and_secret_values_never_appear_in_error_or_state() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI(start_responses(worktree))
        receipt = adapter(root, cli).start_worker(lane, worktree, idempotency_key=KEY)
        assert all(call[1].get("shell") is False for call in cli.calls)
        assert "TOKEN" not in json.dumps(receipt)
        assert "secret" not in json.dumps(receipt)
        assert all(call[0][0] == "orca" for call in cli.calls)
    finally:
        shutil.rmtree(root)


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
