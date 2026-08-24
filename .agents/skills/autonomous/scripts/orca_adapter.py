"""Narrow, receipt-validating adapter for Orca's orchestration CLI."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Callable, Mapping

import parallel_execute as core


class AdapterError(core.ExecutorError):
    """Orca returned an unsupported, foreign, or failed lifecycle receipt."""


_SENSITIVE_KEYS = {"environment", "env", "credentials", "secrets", "token", "password", "authorization", "transcript", "body"}


def _redact_payload(value: Any, *, container: bool = False) -> Any:
    if isinstance(value, Mapping):
        if container:
            return {str(key): _redact_payload(item, container=True) for key, item in value.items()}
        result: dict[str, Any] = {}
        for key, item in value.items():
            if str(key).lower() in _SENSITIVE_KEYS:
                result[str(key)] = _redact_payload(item, container=True) if isinstance(item, (Mapping, list)) else "<redacted>"
            else:
                result[str(key)] = _redact_payload(item)
        return result
    if isinstance(value, list):
        return [_redact_payload(item, container=container) for item in value]
    return "<redacted>" if container else value


def _default_runner(argv: list[str], **kwargs: object) -> Any:
    # core.run_argv owns shell=False; the explicit kwarg is kept at the adapter seam so tests
    # can discriminate accidental shell execution without changing the shared helper.
    kwargs.pop("shell", None)
    return core.run_argv(argv, **kwargs)


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise AdapterError(f"invalid Orca {label}")
    return value


def _payload(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AdapterError("malformed Orca response")
    if value.get("ok") is False:
        raise AdapterError("Orca command failed")
    result = value.get("result")
    if isinstance(result, dict):
        value = result
    for nested in ("run", "task", "worker", "dispatch", "worktree"):
        if isinstance(value.get(nested), dict):
            value = {**value, **value[nested]}
    for field, aliases in {
        "run_id": ("run_id", "runId"),
        "task_id": ("task_id", "taskId"),
        "dispatch_id": ("dispatch_id", "dispatchId"),
        "terminal_handle": ("terminal_handle", "terminalHandle", "agentTerminalHandle"),
        "worktree_id": ("worktree_id", "worktreeId"),
        "worktree_path": ("worktree_path", "worktreePath"),
        "pre_head": ("pre_head", "preHead", "sourceHead"),
    }.items():
        if field not in value:
            for alias in aliases:
                if alias in value:
                    value[field] = value[alias]
                    break
    return value


class OrcaAdapter:
    """Attach workers to an already-created checkout and validate every receipt."""

    def __init__(
        self,
        root: Path,
        feature: str,
        *,
        runner: Callable[..., Any] = _default_runner,
        executable: str = "orca",
        timeout: float = 30,
    ) -> None:
        self.root = Path(root).resolve()
        self.feature = _text(feature, "feature")
        self.runner = runner
        self.executable = _text(executable, "executable")
        if timeout <= 0:
            raise AdapterError("Orca timeout must be positive")
        self.timeout = timeout
        self._workers: dict[str, dict[str, Any]] = {}
        self._ended_waiters: set[str] = set()
        self._released: dict[str, dict[str, Any]] = {}
        self._deliveries: set[str] = set()

    def _call(self, *arguments: str, timeout: float | None = None) -> dict[str, Any]:
        argv = [self.executable, "orchestration", *arguments, "--json"]
        try:
            completed = self.runner(
                argv,
                cwd=self.root,
                timeout=self.timeout if timeout is None else timeout,
                check=True,
                shell=False,
            )
        except (OSError, subprocess.SubprocessError, core.ExecutorError, TypeError) as exc:
            raise AdapterError("Orca command failed") from exc
        try:
            return _payload(json.loads(completed.stdout))
        except (AttributeError, TypeError, json.JSONDecodeError) as exc:
            raise AdapterError("malformed Orca response") from exc

    def _worktree(self, lane: Mapping[str, Any], receipt: Mapping[str, Any]) -> dict[str, str]:
        lane_id = _text(lane.get("id"), "lane id")
        for key in ("slice", "task"):
            _text(lane.get(key), f"lane {key}")
        result = {key: _text(receipt.get(key), f"worktree {key}") for key in (
            "worktree_id", "worktree_path", "branch", "pre_head"
        )}
        path = Path(result["worktree_path"])
        if not path.is_absolute() or not path.exists() or not path.is_dir():
            raise AdapterError(f"invalid existing worktree: {lane_id}")
        try:
            path.resolve(strict=True)
        except OSError as exc:
            raise AdapterError("invalid existing worktree") from exc
        return result

    def _find_run(self, objective: str) -> str | None:
        response = self._call("run-list")
        runs = response.get("runs", [])
        if not isinstance(runs, list):
            raise AdapterError("malformed Orca run list")
        for run in runs:
            if isinstance(run, Mapping) and run.get("objective") == objective:
                return _text(run.get("id") or run.get("run_id") or run.get("runId"), "run id")
        return None

    def _ensure_run(self, key: str) -> str:
        objective = f"parallel-slice:{self.feature}:{key}"
        run_id = self._find_run(objective)
        if run_id is not None:
            return run_id
        response = self._call("run-create", "--objective", objective)
        if response.get("objective") not in (None, objective):
            raise AdapterError("uncorrelated Orca run receipt")
        return _text(response.get("id") or response.get("run_id") or response.get("runId"), "run id")

    def _find_task(self, run_id: str, spec: str) -> str | None:
        response = self._call("task-list", "--run", run_id)
        tasks = response.get("tasks", [])
        if not isinstance(tasks, list):
            raise AdapterError("malformed Orca task list")
        for task in tasks:
            if isinstance(task, Mapping) and task.get("spec") == spec:
                task_run = task.get("run_id") or task.get("runId")
                if task_run is not None and task_run != run_id:
                    raise AdapterError("uncorrelated Orca task receipt")
                return _text(task.get("id") or task.get("task_id") or task.get("taskId"), "task id")
        return None

    def _ensure_task(self, run_id: str, lane: Mapping[str, Any], key: str) -> str:
        slice_id = _text(lane.get("slice"), "lane slice")
        task_name = _text(lane.get("task"), "lane task")
        spec = f"parallel-slice:{self.feature}:{slice_id}:{task_name}:{key}"
        task_id = self._find_task(run_id, spec)
        if task_id is not None:
            return task_id
        response = self._call("task-create", "--run", run_id, "--spec", spec)
        response_run = response.get("run_id") or response.get("runId")
        if response_run not in (None, run_id):
            raise AdapterError("uncorrelated Orca task receipt")
        return _text(response.get("id") or response.get("task_id") or response.get("taskId"), "task id")

    def _validate_worker(
        self,
        payload: Mapping[str, Any],
        lane: Mapping[str, Any],
        worktree: Mapping[str, str],
        key: str,
        *,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        data = dict(payload)
        expected = {
            "feature": self.feature,
            "slice": _text(lane.get("slice"), "lane slice"),
            "task": _text(lane.get("task"), "lane task"),
            "worktree_id": worktree["worktree_id"],
            "worktree_path": worktree["worktree_path"],
            "branch": worktree["branch"],
            "pre_head": worktree["pre_head"],
            "idempotency_key": key,
        }
        for field, expected_value in expected.items():
            if field not in data:
                raise AdapterError(f"missing Orca worker receipt: {field}")
            if data[field] != expected_value:
                raise AdapterError(f"uncorrelated Orca worker receipt: {field}")
            data[field] = expected_value
        run_id = _text(data.get("run_id"), "run id")
        actual_task = _text(data.get("task_id") or data.get("orchestration_task_id"), "task id")
        if task_id is not None and actual_task != task_id:
            raise AdapterError("uncorrelated Orca task receipt")
        data["run_id"] = run_id
        data["task_id"] = actual_task
        data["orchestration_task_id"] = actual_task
        data["dispatch_id"] = _text(data.get("dispatch_id"), "dispatch id")
        data["terminal_handle"] = _text(data.get("terminal_handle"), "terminal handle")
        return data

    @staticmethod
    def _complete_worker(payload: Mapping[str, Any]) -> bool:
        return all(
            field in payload
            for field in (
                "run_id", "task_id", "dispatch_id", "terminal_handle", "feature", "slice", "task",
                "worktree_id", "worktree_path", "branch", "pre_head", "idempotency_key",
            )
        )

    def _authoritative_worker(
        self,
        response: Mapping[str, Any],
        lane: Mapping[str, Any],
        worktree: Mapping[str, str],
        key: str,
        *,
        task_id: str,
    ) -> dict[str, Any]:
        data = dict(response)
        if not self._complete_worker(data):
            dispatch_id = _text(data.get("dispatch_id"), "dispatch id")
            authoritative = self._call("worker-show", "--dispatch", dispatch_id)
            data = {**data, **authoritative}
        return self._validate_worker(data, lane, worktree, key, task_id=task_id)

    def start_worker(
        self, lane: Mapping[str, Any], receipt: Mapping[str, Any], *, idempotency_key: str
    ) -> dict[str, Any]:
        key = _text(idempotency_key, "idempotency key")
        worktree = self._worktree(lane, receipt)
        cached = self._workers.get(key)
        if cached is not None:
            if any(cached[field] != worktree[field] for field in ("worktree_id", "worktree_path", "pre_head")):
                raise AdapterError("idempotency key changed worktree")
            return dict(cached)
        run_id = self._ensure_run(key)
        task_id = self._ensure_task(run_id, lane, key)
        response = self._call(
            "worker-start",
            "--task",
            task_id,
            "--worktree",
            "path:" + worktree["worktree_path"],
            "--agent",
            "codex",
        )
        worker = self._authoritative_worker(response, lane, worktree, key, task_id=task_id)
        if worker["run_id"] != run_id:
            raise AdapterError("uncorrelated Orca run receipt")
        worker["status"] = "running"
        self._workers[key] = dict(worker)
        return dict(worker)

    def _delivery(self, delivery: Mapping[str, Any], receipt: Mapping[str, Any]) -> dict[str, Any]:
        delivery_id = _text(delivery.get("id"), "delivery id")
        if delivery_id in self._deliveries:
            raise AdapterError("duplicate Orca delivery")
        run_id = _text(delivery.get("run_id"), "delivery run id")
        if run_id != receipt.get("run_id"):
            raise AdapterError("uncorrelated Orca delivery: run_id")
        event_type = _text(delivery.get("type"), "delivery type")
        if event_type not in {"worker_done", "escalation", "question"}:
            raise AdapterError("unsupported Orca delivery")
        if delivery.get("from_handle") != receipt.get("terminal_handle"):
            raise AdapterError("uncorrelated Orca delivery: from_handle")
        raw_payload = delivery.get("payload")
        if isinstance(raw_payload, str):
            try:
                payload = json.loads(raw_payload)
            except json.JSONDecodeError as exc:
                raise AdapterError("malformed Orca delivery payload") from exc
        else:
            payload = raw_payload
        if not isinstance(payload, dict):
            raise AdapterError("malformed Orca delivery payload")
        task_id = payload.get("taskId") or payload.get("task_id")
        dispatch_id = payload.get("dispatchId") or payload.get("dispatch_id")
        if task_id != receipt.get("orchestration_task_id"):
            raise AdapterError("uncorrelated Orca delivery: taskId")
        if dispatch_id != receipt.get("dispatch_id"):
            raise AdapterError("uncorrelated Orca delivery: dispatchId")
        outcome = payload.get("outcome")
        if payload.get("status") in {"dirty", "failed", "escalated"} or outcome == "failed":
            raise AdapterError("Orca worker delivery halted")
        if event_type == "worker_done":
            if outcome != "succeeded":
                raise AdapterError("Orca worker outcome was not accepted")
            event = "worker_done"
            status = "accepted"
        elif event_type == "escalation":
            raise AdapterError("Orca worker escalated")
        elif payload.get("status") == "waiting" and payload.get("dependency"):
            event = "waiting"
            status = "clean"
        elif payload.get("event") == "dependency" and payload.get("status") == "complete":
            event = "dependency"
            status = "complete"
        else:
            event = "question"
            status = "question"
        safe_payload = _redact_payload(payload)
        self._deliveries.add(delivery_id)
        return {
            "event": event,
            "status": status,
            "delivery_id": delivery_id,
            "run_id": run_id,
            "from_handle": delivery["from_handle"],
            "payload": safe_payload,
            "task_id": task_id,
            "dispatch_id": dispatch_id,
            **({"dependency": payload["dependency"]} if "dependency" in payload else {}),
        }

    def read_worker(self, receipt: Mapping[str, Any]) -> dict[str, Any]:
        dispatch_id = _text(receipt.get("dispatch_id"), "dispatch id")
        response = self._call("worker-read", "--dispatch", dispatch_id, "--limit", "50")
        actual_dispatch = response.get("dispatch_id") or response.get("dispatchId")
        if actual_dispatch != dispatch_id:
            raise AdapterError("uncorrelated worker-read dispatch")
        aliases = {
            "source": ("source",),
            "source_identity": ("source_identity", "sourceIdentity"),
            "provider": ("provider",),
            "cursor": ("cursor",),
            "status": ("status",),
        }
        for field, names in aliases.items():
            if not any(name in response for name in names):
                raise AdapterError(f"missing worker-read field: {field}")
        transcript = response.get("transcript")
        if transcript is None:
            raise AdapterError("missing worker-read transcript")
        status = response.get("status")
        if status not in {"succeeded", "accepted", "complete", "completed"}:
            raise AdapterError("worker-read did not prove completion")
        return {
            "dispatch_id": dispatch_id,
            "source": response.get("source"),
            "source_identity": response.get("source_identity") or response.get("sourceIdentity"),
            "provider": response.get("provider"),
            "transcript": "<redacted>",
            "cursor": response.get("cursor"),
            "status": status,
            "transcript_redacted": True,
        }

    def accept_worker_done(
        self,
        receipt: Mapping[str, Any],
        delivery: Mapping[str, Any],
        output: Mapping[str, Any],
    ) -> dict[str, Any]:
        if delivery.get("event") != "worker_done" or delivery.get("status") != "accepted":
            raise AdapterError("worker delivery was not accepted")
        if output.get("dispatch_id") != receipt.get("dispatch_id") or output.get("transcript") != "<redacted>":
            raise AdapterError("worker output is uncorrelated or unredacted")
        return {
            **dict(receipt),
            "status": "accepted",
            "accepted": True,
            "delivery_id": delivery["delivery_id"],
            "output": dict(output),
        }

    def wait_events(self, receipt: Mapping[str, Any], *, timeout: float = 30) -> dict[str, Any]:
        if timeout <= 0:
            raise AdapterError("Orca wait timeout must be positive")
        run_id = _text(receipt.get("run_id"), "run id")
        response = self._call(
            "check",
            "--run",
            run_id,
            "--wait",
            "--types",
            "worker_done,question,escalation",
            "--timeout-ms",
            str(int(timeout * 1000)),
            timeout=timeout + 1,
        )
        deliveries = response.get("deliveries")
        if deliveries == [] or response.get("timeout") is True or response.get("count") == 0:
            return {"event": "timeout", "unchanged": True}
        if isinstance(deliveries, list) and len(deliveries) == 1:
            return self._delivery(deliveries[0], receipt)
        delivery = response.get("delivery")
        if isinstance(delivery, Mapping):
            return self._delivery(delivery, receipt)
        raise AdapterError("missing Orca delivery")

    def _release(self, receipt: Mapping[str, Any]) -> dict[str, Any]:
        key = _text(receipt.get("idempotency_key"), "idempotency key")
        if key in self._released:
            return {**self._released[key], "idempotent": True}
        dispatch_id = _text(receipt.get("dispatch_id"), "dispatch id")
        response = self._call("worker-release", "--dispatch", dispatch_id)
        if response.get("released") is not True:
            raise AdapterError("Orca worker release was not accepted")
        if response.get("dispatch_id") not in (None, dispatch_id):
            raise AdapterError("uncorrelated Orca release receipt")
        result = {"released": True, "dispatch_id": dispatch_id}
        self._released[key] = result
        return dict(result)

    def release(self, receipt: Mapping[str, Any], result: Mapping[str, Any] | None = None) -> dict[str, Any]:
        if result is None or result.get("accepted") is not True:
            raise AdapterError("worker must be accepted before release")
        return self._release(receipt)

    def end_waiter(self, receipt: Mapping[str, Any], waiter: Mapping[str, Any]) -> dict[str, Any]:
        event = waiter
        if event.get("event") != "waiting" or event.get("status") != "clean":
            raise AdapterError("worker waiter is not clean")
        dependency = _text(event.get("dependency"), "dependency")
        self._ended_waiters.add(_text(receipt.get("dispatch_id"), "dispatch id") + ":" + dependency)
        return {"ended": True, "terminal_handle": _text(receipt.get("terminal_handle"), "terminal handle")}

    def follow_up(
        self,
        receipt: Mapping[str, Any],
        waiter: Mapping[str, Any],
        dependency: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        waiter_event = waiter
        if waiter_event.get("event") != "waiting" or waiter_event.get("status") != "clean":
            raise AdapterError("worker waiter is not clean")
        dependency_name = _text(waiter_event.get("dependency"), "dependency")
        if dependency.get("event") != "dependency" or dependency.get("status") != "complete":
            raise AdapterError("dependency event is unavailable")
        if dependency.get("dependency") != dependency_name:
            raise AdapterError("uncorrelated dependency event")
        dispatch_id = _text(receipt.get("dispatch_id"), "dispatch id")
        if waiter_event.get("ended") is not True and dispatch_id + ":" + dependency_name not in self._ended_waiters:
            raise AdapterError("worker turn is still active")
        next_task = _text(dependency.get("next_task_id") or receipt.get("orchestration_task_id"), "task id")
        response = self._call("worker-start", "--task", next_task, "--terminal", _text(receipt.get("terminal_handle"), "terminal handle"))
        lane = {"feature": self.feature, "slice": receipt["slice"], "task": receipt["task"]}
        worktree = {key: receipt[key] for key in ("worktree_id", "worktree_path", "branch", "pre_head")}
        key = _text(idempotency_key or receipt.get("idempotency_key"), "idempotency key")
        return self._authoritative_worker(response, lane, worktree, key, task_id=next_task)


Adapter = OrcaAdapter
