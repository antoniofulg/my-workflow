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


def test_structured_worker_start_failure_preserves_partial_effect_and_reuses_run_task_on_retry() -> None:
    root, lane, worktree = fixture()
    try:
        failure = subprocess.CalledProcessError(
            1, ["orca", "orchestration", "worker-start"],
            output=json.dumps({"ok": False, "error": {"code": "selector_not_found", "stage": "worker-start", "run_id": "run-A", "task_id": "task-A", "residualResources": {"token": "secret"}}}),
            stderr="",
        )
        cli = RecordingCLI(start_responses(worktree)[:4] + [{"worktree_path": worktree["worktree_path"]}, failure])
        worker = adapter(root, cli)
        try:
            worker.start_worker(lane, worktree, idempotency_key=KEY)
        except orca_adapter.AdapterError as exc:
            assert "selector_not_found" in str(exc)
            assert exc.details["run_id"] == "run-A"
            assert exc.details["task_id"] == "task-A"
            assert exc.details["residualResources"]["token"] == "<redacted>"
        else:
            raise AssertionError("structured worker failure must be reported")

        retry_cli = RecordingCLI([{"worktree_path": worktree["worktree_path"]}, worker_payload(worktree)])
        retry = adapter(root, retry_cli)
        receipt = retry.reconcile_action({
            "action": "worker", "key": KEY,
            "partial_effect": {"run_id": "run-A", "task_id": "task-A"},
            "worker_plan": lane,
            "worktree_receipt": worktree,
        })
        assert receipt is not None and receipt["run_id"] == "run-A" and receipt["orchestration_task_id"] == "task-A"
        assert retry_cli.calls[1][0][2] == "worker-start"
        assert retry_cli.calls[1][0][retry_cli.calls[1][0].index("--task") + 1] == "task-A"
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
        receipt = adapter(root, cli).start_worker(lane, worktree, idempotency_key=KEY)
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
        cli = RecordingCLI(start_responses(worktree)[:4] + [not_found, not_found, not_found])
        try:
            adapter(root, cli).start_worker(lane, worktree, idempotency_key=KEY)
        except orca_adapter.AdapterError as exc:
            assert exc.details["run_id"] == "run-A"
            assert exc.details["task_id"] == "task-A"
            assert exc.details["stage"] == "worktree-discovery"
            assert exc.details["attempts"] == 3
        else:
            raise AssertionError("bounded discovery timeout must fail safely")
        assert not any(call[0][2] == "worker-start" for call in cli.calls)
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
        duplicate_runs = [{"id": "run-A", "objective": objective}, {"id": "run-B", "objective": objective}]
        cli = RecordingCLI([{"runs": duplicate_runs}])
        try:
            adapter(root, cli).start_worker(lane, worktree, idempotency_key=KEY)
        except orca_adapter.AdapterError as exc:
            assert "multiple" in str(exc)
        else:
            raise AssertionError("duplicate matching runs must halt")

        duplicate_tasks = [{"id": "task-A", "run_id": "run-A", "spec": "parallel-slice:fixture:A:T1:" + KEY}, {"id": "task-B", "run_id": "run-A", "spec": "parallel-slice:fixture:A:T1:" + KEY}]
        cli = RecordingCLI([
            {"runs": []}, {"id": "run-A", "objective": objective}, {"tasks": duplicate_tasks},
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
