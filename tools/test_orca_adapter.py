"""Spec-derived tests for the provider-neutral Orca worker adapter."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

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


def adapter(root: Path, cli: RecordingCLI) -> orca_adapter.OrcaAdapter:
    return orca_adapter.OrcaAdapter(root, "fixture", runner=cli)


def start_responses(worktree: dict[str, str]) -> list[object]:
    return [
        {"runs": []},
        {"id": "run-A", "objective": "parallel-slice:fixture:" + KEY},
        {"tasks": []},
        {"id": "task-A", "run_id": "run-A", "spec": "parallel-slice:fixture:A:T1:" + KEY},
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


def test_start_attaches_existing_worktree_and_correlates_every_receipt_field() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI(start_responses(worktree))
        receipt = adapter(root, cli).start_worker(lane, worktree, idempotency_key=KEY)
        commands = [call[0][2] for call in cli.calls]
        assert commands == ["run-list", "run-create", "task-list", "task-create", "worker-start"]
        assert all("create" not in call[0][2:] or "worktree" not in call[0] for call in cli.calls)
        worker_call = cli.calls[-1][0]
        assert "--worktree" in worker_call
        assert "path:" + worktree["worktree_path"] in worker_call
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


def test_start_reuses_run_task_and_worker_by_idempotency_without_duplicate_effect() -> None:
    root, lane, worktree = fixture()
    try:
        cli = RecordingCLI(start_responses(worktree))
        worker = adapter(root, cli)
        first = worker.start_worker(lane, worktree, idempotency_key=KEY)
        second = worker.start_worker(lane, worktree, idempotency_key=KEY)
        assert second == first
        assert len(cli.calls) == 5
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
            + [{"deliveries": [waiter]}, {"started": True, **worker_payload(worktree)}]
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


def test_incomplete_start_receipt_uses_authoritative_worker_show() -> None:
    root, lane, worktree = fixture()
    try:
        start = {"run_id": "run-A", "task_id": "task-A", "dispatch_id": "dispatch-A"}
        cli = RecordingCLI(start_responses(worktree)[:4] + [start, worker_payload(worktree)])
        receipt = adapter(root, cli).start_worker(lane, worktree, idempotency_key=KEY)
        assert [call[0][2] for call in cli.calls] == ["run-list", "run-create", "task-list", "task-create", "worker-start", "worker-show"]
        assert receipt["dispatch_id"] == "dispatch-A"
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
            assert not any(call[0][2] == "worker-start" for call in cli.calls[5:])
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
