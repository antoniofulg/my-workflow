"""Narrow, receipt-validating adapter for Orca's orchestration CLI."""

from __future__ import annotations

import json
import hashlib
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Callable, Mapping

import parallel_execute as core


CAPABILITY = "orchestration.contract.v1"
WORKTREE_DISCOVERY_TIMEOUT_SECONDS = 30.0
WORKTREE_DISCOVERY_INITIAL_BACKOFF_SECONDS = 0.1
WORKTREE_DISCOVERY_MAX_BACKOFF_SECONDS = 1.0
WORKER_START_TIMEOUT_MS = 120_000
KNOWN_INCOMPATIBLE_VERSIONS = {"1.4.188"}


class AdapterError(core.ExecutorError):
    """Orca returned an unsupported, foreign, or failed lifecycle receipt."""

    def __init__(self, message: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details = dict(details or {})


_SENSITIVE_KEYS = {"environment", "env", "credentials", "secrets", "token", "password", "authorization", "transcript", "body"}

_CREDENTIAL_TEXT = re.compile(
    r'''(?ix)(?P<prefix>\b(?:password|token|access[_-]?token|api[_-]?key|client[_-]?secret|cookie|secret|credential)\b\s*[:=]\s*)
        (?:(?P<quote>["'])(?P<quoted>.*?)(?P=quote)|(?P<bare>[^\s,;}'"]+))'''
)
_AUTH_TEXT = re.compile(
    r'''(?ix)(?P<prefix>\bauthorization\b\s*[:=]\s*)(?!bearer\b)
        (?:(?P<quote>["'])(?P<quoted>.*?)(?P=quote)|(?P<bare>[^\s,;}'"]+))'''
)
_BEARER_TEXT = re.compile(
    r'''(?ix)(?P<prefix>\b(?:authorization\s*[:=]\s*)?bearer\s+)
        (?:(?P<quote>["'])(?P<quoted>.*?)(?P=quote)|(?P<bare>[^\s,;}'"]+))'''
)


def _is_sensitive_key(key: str) -> bool:
    normalized = key.strip().lower().replace("-", "_")
    if normalized in _SENSITIVE_KEYS or normalized in {"access_token", "refresh_token", "api_key", "client_secret", "cookie"}:
        return True
    return normalized.endswith(("_token", "_secret", "_key", "_cookie", "_password", "_credential"))


def _redact_text(value: str) -> str:
    """Remove credential-shaped values while retaining diagnostic code and stage text."""
    def replace(match: re.Match[str]) -> str:
        quote = match.group("quote")
        return match.group("prefix") + (f"{quote}<redacted>{quote}" if quote else "<redacted>")

    value = _BEARER_TEXT.sub(replace, value)
    value = _AUTH_TEXT.sub(replace, value)
    return _CREDENTIAL_TEXT.sub(replace, value)


def _redact_payload(value: Any, *, container: bool = False) -> Any:
    if isinstance(value, Mapping):
        if container:
            return {str(key): _redact_payload(item, container=True) for key, item in value.items()}
        result: dict[str, Any] = {}
        for key, item in value.items():
            if _is_sensitive_key(str(key)):
                result[str(key)] = _redact_payload(item, container=True) if isinstance(item, (Mapping, list)) else "<redacted>"
            else:
                result[str(key)] = _redact_payload(item)
        return result
    if isinstance(value, list):
        return [_redact_payload(item, container=container) for item in value]
    if isinstance(value, str):
        return "<redacted>" if container else _redact_text(value)
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


_DISPATCH_FORBIDDEN = set(";|&$<>\"'`()\\")


def _opaque_token(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 256:
        raise AdapterError(f"invalid Orca {label}")
    if any(ord(char) < 32 or ord(char) == 127 or char.isspace() or char in _DISPATCH_FORBIDDEN for char in value):
        raise AdapterError(f"invalid Orca {label}")
    return value


def _nested_dispatch_id(value: Mapping[str, Any]) -> Any:
    if "dispatch_id" in value:
        return value["dispatch_id"]
    if "dispatchId" in value:
        return value["dispatchId"]
    nested = value.get("dispatch")
    if isinstance(nested, Mapping):
        if "dispatch_id" in nested:
            return nested["dispatch_id"]
        if "dispatchId" in nested:
            return nested["dispatchId"]
        if "id" in nested:
            return nested["id"]
    result = value.get("result")
    if isinstance(result, Mapping):
        return _nested_dispatch_id(result)
    return None


def _nested_terminal_handle(value: Mapping[str, Any]) -> Any:
    for field in ("terminal_handle", "terminalHandle", "agentTerminalHandle", "agent_terminal_handle"):
        if field in value:
            return value[field]
    for key in ("worker", "terminal", "terminalResource", "terminal_resource", "dispatch", "result"):
        nested = value.get(key)
        if isinstance(nested, Mapping):
            if key in {"terminal", "terminalResource", "terminal_resource"} and "handle" in nested:
                return nested["handle"]
            handle = _nested_terminal_handle(nested)
            if handle is not None:
                return handle
    return None


def _nested_terminal_state(value: Mapping[str, Any]) -> Mapping[str, Any] | None:
    for key in ("terminal", "terminalResource", "terminal_resource"):
        nested = value.get(key)
        if isinstance(nested, Mapping):
            return nested
    for key in ("worker", "dispatch", "result"):
        nested = value.get(key)
        if isinstance(nested, Mapping):
            state = _nested_terminal_state(nested)
            if state is not None:
                return state
    return None


def _nested_resource(value: Mapping[str, Any]) -> Mapping[str, Any] | None:
    for key in ("terminalResource", "terminal_resource", "resource"):
        nested = value.get(key)
        if isinstance(nested, Mapping):
            return nested
    for key in ("worker", "dispatch", "terminal", "result"):
        nested = value.get(key)
        if isinstance(nested, Mapping):
            resource = _nested_resource(nested)
            if resource is not None:
                return resource
    return None


def _resource_dispatch_identity(resource: Mapping[str, Any], field: str) -> Any:
    parts = field.split("_")
    camel = parts[0] + "".join(part.capitalize() for part in parts[1:])
    aliases = (field, camel)
    values: list[Any] = []
    for alias in aliases:
        if alias not in resource:
            continue
        value = resource[alias]
        if isinstance(value, Mapping):
            value = _nested_dispatch_id(value) or value.get("dispatch_id") or value.get("dispatchId") or value.get("id")
        if value not in (None, "") and value not in values:
            values.append(value)
    if len(values) > 1:
        raise AdapterError("conflicting Orca resource identity", details={"code": "correlation_conflict", "field": field})
    return values[0] if values else None


_IDENTITY_ALIASES = {
    "run_id": ("run_id", "runId"),
    "task_id": ("task_id", "taskId"),
    "dispatch_id": ("dispatch_id", "dispatchId"),
    "terminal_handle": ("terminal_handle", "terminalHandle", "agentTerminalHandle", "agent_terminal_handle"),
    "resource_id": ("resource_id", "resourceId", "terminal_resource_id", "terminalResourceId"),
    "worktree_id": ("worktree_id", "worktreeId"),
    "request_id": ("request_id", "requestId"),
    "idempotency_key": ("idempotency_key", "idempotencyKey"),
    "retry_request": ("retry_request", "retryRequest", "retry_request_id", "retryRequestId", "retry_of", "retryOf"),
}
_IDENTITY_LABELS = {
    "run_id": "run id",
    "task_id": "task id",
    "dispatch_id": "dispatch id",
    "terminal_handle": "terminal handle",
    "resource_id": "resource id",
    "worktree_id": "worktree id",
    "request_id": "request id",
    "idempotency_key": "idempotency key",
    "retry_request": "retry request",
}
_CONTAINER_IDENTITY = {
    "run": ("run_id", "run id"),
    "task": ("task_id", "task id"),
    "dispatch": ("dispatch_id", "dispatch id"),
    "resource": ("resource_id", "resource id"),
    "terminalResource": ("resource_id", "resource id"),
    "worktree": ("worktree_id", "worktree id"),
}
_STATE_ALIASES = {
    "status": ("status", "state"),
    "state": ("state", "status"),
    "lastError": ("lastError", "last_error"),
    "releaseState": ("releaseState", "release_state"),
    "releaseError": ("releaseError", "release_error"),
    "released": ("released",),
    "reconciled": ("reconciled",),
    "terminal_status": ("terminal_status", "terminalStatus"),
    "connected": ("connected",),
    "writable": ("writable",),
    "reason": ("reason",),
    "release_error": ("release_error",),
    "error": ("error",),
    "code": ("code",),
    "ownershipState": ("ownershipState", "ownership_state"),
    "retainedReason": ("retainedReason", "retained_reason"),
    "releaseRequestedAt": ("releaseRequestedAt", "release_requested_at"),
    "releaseCompletedAt": ("releaseCompletedAt", "release_completed_at"),
}
_PASSTHROUGH_ALIASES = {
    "objective": ("objective",),
    "spec": ("spec",),
    "feature": ("feature",),
    "slice": ("slice",),
    "task": ("task",),
    "worktree_path": ("worktree_path", "worktreePath"),
    "branch": ("branch",),
    "pre_head": ("pre_head", "preHead", "sourceHead"),
    "orchestration_task_id": ("orchestration_task_id", "orchestrationTaskId"),
}


def _canonical_candidates(value: Mapping[str, Any]) -> dict[str, list[Any]]:
    candidates = {field: [] for field in _IDENTITY_ALIASES}
    states = {field: [] for field in _STATE_ALIASES}
    passthrough = {field: [] for field in _PASSTHROUGH_ALIASES}

    def visit(node: Mapping[str, Any], container: str | None = None, parent: str | None = None) -> None:
        for key, item in node.items():
            name = str(key)
            if name in {alias for aliases in _IDENTITY_ALIASES.values() for alias in aliases}:
                for field, aliases in _IDENTITY_ALIASES.items():
                    if name in aliases:
                        candidates[field].append(item)
                        break
            for field, aliases in _STATE_ALIASES.items():
                if name in aliases:
                    states[field].append(item)
            for field, aliases in _PASSTHROUGH_ALIASES.items():
                if name in aliases and not (field == "task" and isinstance(item, Mapping)):
                    passthrough[field].append(item)
            if container in _CONTAINER_IDENTITY and name == "id":
                candidates[_CONTAINER_IDENTITY[container][0]].append(item)
            if container == "worktree" and name in {"path", "worktree_path", "worktreePath"}:
                passthrough["worktree_path"].append(item)
            if container == "git" and parent == "worktree" and name in {"path", "worktree_path", "worktreePath"}:
                passthrough["worktree_path"].append(item)
            if container in {"terminal", "terminalResource", "terminal_resource"} and name == "handle":
                candidates["terminal_handle"].append(item)
            if isinstance(item, Mapping) and name in _CONTAINER_IDENTITY:
                if "id" in item:
                    candidates[_CONTAINER_IDENTITY[name][0]].append(item["id"])
                if name == "worktree":
                    for alias in ("path", "worktree_path", "worktreePath"):
                        if alias in item:
                            passthrough["worktree_path"].append(item[alias])
                            break
                    git = item.get("git")
                    if isinstance(git, Mapping):
                        for alias in ("path", "worktree_path", "worktreePath"):
                            if alias in git:
                                passthrough["worktree_path"].append(git[alias])
                                break
            if isinstance(item, Mapping):
                visit(item, name, container)

    visit(value)
    return {**candidates, **states, **passthrough}


def _canonical_projection(value: Mapping[str, Any]) -> dict[str, Any]:
    """Project nested Orca envelopes without discarding their outer evidence."""
    projected = dict(value)
    candidates = _canonical_candidates(value)
    for field, values in ((field, candidates[field]) for field in _IDENTITY_ALIASES):
        present = [candidate for candidate in values if candidate not in (None, "", "<redacted>")]
        normalized: list[str] = []
        for candidate in present:
            try:
                normalized_value = _opaque_token(candidate, _IDENTITY_LABELS[field])
            except AdapterError as exc:
                code = "uncorrelated_terminal" if field == "terminal_handle" else "invalid_identity"
                raise AdapterError(
                    str(exc), details={"code": code, "field": field}
                ) from exc
            if normalized_value not in normalized:
                normalized.append(normalized_value)
        if len(normalized) > 1:
            raise AdapterError(
                f"conflicting Orca {field}",
                details={"code": "correlation_conflict", "field": field},
            )
        if field not in projected and normalized:
            projected[field] = normalized[0]
        elif field in projected and projected[field] == "<redacted>":
            projected.pop(field)
        elif field in projected and projected[field] not in (None, ""):
            projected[field] = _opaque_token(projected[field], _IDENTITY_LABELS[field])

    for field, values in ((field, candidates[field]) for field in _STATE_ALIASES):
        if field not in projected:
            for candidate in values:
                projected[field] = candidate
                break
    if "releaseState" not in projected:
        state = projected.get("status") or projected.get("state")
        if state in {"retained", "released", "completed"}:
            projected["releaseState"] = state
    if "retainedReason" not in projected and projected.get("reason") == "identity_unproven":
        projected["retainedReason"] = "identity_unproven"
    if "releaseError" not in projected and "lastError" in projected:
        projected["releaseError"] = projected["lastError"]
    worktree_paths = [candidate for candidate in candidates["worktree_path"] if candidate not in (None, "")]
    if projected.get("worktree_path") not in (None, ""):
        worktree_paths.append(projected["worktree_path"])
    if len({str(candidate) for candidate in worktree_paths}) > 1:
        raise AdapterError(
            "conflicting Orca worktree path",
            details={"code": "correlation_conflict", "field": "worktree_path"},
        )
    resource = _nested_resource(value)
    if resource is not None:
        for field in ("owner_dispatch_id", "origin_dispatch_id"):
            identity = _resource_dispatch_identity(resource, field)
            if identity is None:
                continue
            normalized = _opaque_token(identity, field.replace("_", " "))
            if field in projected and projected[field] not in (None, normalized):
                raise AdapterError(
                    f"conflicting Orca resource {field}",
                    details={"code": "correlation_conflict", "field": field},
                )
            projected[field] = normalized
    for field in _PASSTHROUGH_ALIASES:
        if field not in projected:
            for candidate in candidates[field]:
                if candidate not in (None, ""):
                    projected[field] = candidate
                    break
    return projected


def _is_identity_unproven_release(value: Mapping[str, Any]) -> bool:
    state = value.get("releaseState") or value.get("release_state") or value.get("status") or value.get("state")
    reason = value.get("retainedReason") or value.get("retained_reason") or value.get("reason")
    return state == "retained" and reason == "identity_unproven"


def _scoped_identifier(value: Mapping[str, Any], field: str, container: str) -> Any:
    aliases = (field, field.replace("_", ""), field.replace("_", "Id"))
    for alias in aliases:
        if alias in value:
            return value[alias]
    nested = value.get(container)
    if isinstance(nested, Mapping):
        for alias in aliases:
            if alias in nested:
                return nested[alias]
        return nested.get("id")
    return None


def _scoped_field(value: Mapping[str, Any], field: str, container: str) -> Any:
    if field in value:
        return value[field]
    nested = value.get(container)
    return nested.get(field) if isinstance(nested, Mapping) else None


def _payload(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AdapterError("malformed Orca response")
    if value.get("ok") is False:
        raise AdapterError("Orca command failed")
    return _canonical_projection(value)


def _bounded(value: Any, depth: int = 0) -> Any:
    if depth > 3:
        return "<truncated>"
    if isinstance(value, Mapping):
        return {str(key): _bounded(item, depth + 1) for key, item in list(value.items())[:32]}
    if isinstance(value, list):
        return [_bounded(item, depth + 1) for item in value[:32]]
    if isinstance(value, str):
        return value[:256]
    return value


def _failure_details(exc: subprocess.CalledProcessError) -> dict[str, Any]:
    raw = exc.stdout or exc.stderr or ""
    try:
        payload = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return {"returncode": exc.returncode}
    if not isinstance(payload, Mapping):
        return {"returncode": exc.returncode}
    error = payload.get("error") if isinstance(payload.get("error"), Mapping) else payload
    details = _redact_payload(_bounded(error))
    if not isinstance(details, dict):
        details = {"message": details}
    details = _canonical_projection(details)
    details["returncode"] = exc.returncode
    return details


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
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        discovery_timeout: float = WORKTREE_DISCOVERY_TIMEOUT_SECONDS,
        worktree_creator: Callable[[Path, str], Mapping[str, Any]] | None = None,
        worktree_remover: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.feature = _text(feature, "feature")
        self.runner = runner
        self.executable = _text(executable, "executable")
        if timeout <= 0:
            raise AdapterError("Orca timeout must be positive")
        if discovery_timeout <= 0:
            raise AdapterError("Orca worktree discovery timeout must be positive")
        self.timeout = timeout
        self._clock = clock
        self._sleep = sleep
        self._discovery_timeout = discovery_timeout
        self._workers: dict[str, dict[str, Any]] = {}
        self._ended_waiters: set[str] = set()
        self._released: dict[str, dict[str, Any]] = {}
        self._release_failures: dict[str, dict[str, Any]] = {}
        self._stopped: dict[str, dict[str, Any]] = {}
        self._stop_failures: dict[str, dict[str, Any]] = {}
        self._revoked_dispatches: set[str] = set()
        self._deliveries: set[str] = set()
        self._worktree_creator = worktree_creator
        self._worktree_remover = worktree_remover

    def _cache_path(self) -> Path:
        try:
            return core.runtime_state_path(self.root, self.feature).with_name(
                core.runtime_state_path(self.root, self.feature).stem + "-orca-compatibility.json"
            )
        except (core.ExecutorError, OSError, subprocess.SubprocessError):
            return self.root / ".parallel-slice-executor" / f"{self.feature}-orca-compatibility.json"

    def _executable_identity(self) -> dict[str, Any]:
        resolved = Path(shutil.which(self.executable) or self.executable).resolve()
        identity: dict[str, Any] = {"path": str(resolved)}
        try:
            stat = resolved.stat()
        except OSError:
            return identity
        identity.update({"size": stat.st_size, "mtime_ns": stat.st_mtime_ns})
        return identity

    @staticmethod
    def _status_value(value: Mapping[str, Any], names: set[str]) -> Any:
        pending: list[Any] = [value]
        while pending:
            current = pending.pop(0)
            if not isinstance(current, Mapping):
                continue
            for key, item in current.items():
                if str(key) in names:
                    return item
                if isinstance(item, Mapping):
                    pending.append(item)
                elif isinstance(item, list):
                    pending.extend(item)
        return None

    def _status_call(self) -> dict[str, Any]:
        try:
            completed = self.runner(
                [self.executable, "status", "--json"], cwd=self.root, timeout=self.timeout,
                check=True, shell=False,
            )
        except (subprocess.CalledProcessError, OSError, subprocess.SubprocessError, core.ExecutorError, TypeError) as exc:
            raise AdapterError("Orca status probe failed", details={"code": "status-unreachable"}) from exc
        try:
            payload = json.loads(completed.stdout)
        except (AttributeError, TypeError, json.JSONDecodeError) as exc:
            raise AdapterError("malformed Orca status response", details={"code": "malformed-status"}) from exc
        if not isinstance(payload, Mapping):
            raise AdapterError("malformed Orca status response", details={"code": "malformed-status"})
        return _payload(payload)

    def _runtime_identity(self, status: Mapping[str, Any]) -> dict[str, Any]:
        app_version = self._status_value(status, {"appVersion", "app_version", "version"})
        capabilities = self._status_value(status, {"capabilities", "capabilitySet", "capability_set"})
        if isinstance(capabilities, Mapping):
            capabilities = [key for key, enabled in capabilities.items() if enabled is True]
        if not isinstance(capabilities, list):
            capabilities = []
        capabilities = sorted({str(item) for item in capabilities if isinstance(item, str) and item})
        return {
            "app_version": app_version if isinstance(app_version, str) else "",
            "capabilities": capabilities,
            "executable_identity": self._executable_identity(),
        }

    def _load_cached(self, identity: Mapping[str, Any]) -> dict[str, Any] | None:
        try:
            value = json.loads(self._cache_path().read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            return None
        if not isinstance(value, Mapping) or value.get("status") != "compatible":
            return None
        if value.get("repository") != str(self.root) or value.get("runtime") != dict(identity):
            return None
        proof = value.get("proof")
        if not isinstance(proof, Mapping) or proof.get("cleanup") != "clean":
            return None
        return dict(value)

    def identity(self) -> dict[str, Any]:
        status = self._status_call()
        return self._runtime_identity(status)

    def probe(self) -> dict[str, Any]:
        """Return a read-only compatibility decision; never start a canary implicitly."""
        status = self._status_call()
        runtime = self._runtime_identity(status)
        version = runtime["app_version"]
        ready = self._status_value(status, {"ready", "reachable", "connected"})
        status_name = self._status_value(status, {"status", "state"})
        result: dict[str, Any] = {
            "version": 1, "feature": self.feature, "adapter": "orca", "runtime": runtime,
            "proof": {"source": "lifecycle-canary", "cleanup": "not-run"},
        }
        if ready is not True and status_name not in {"ready", "connected", "running"}:
            return {**result, "status": "unsupported", "reason": "runtime-not-ready"}
        if not version:
            return {**result, "status": "unsupported", "reason": "missing-app-version"}
        if CAPABILITY not in runtime["capabilities"]:
            return {**result, "status": "unsupported", "reason": "missing-capability:" + CAPABILITY}
        if version in KNOWN_INCOMPATIBLE_VERSIONS:
            return {**result, "status": "unsupported", "reason": "known-incompatible-version:" + version}
        cached = self._load_cached(runtime)
        if cached is not None:
            return cached
        return {**result, "status": "candidate", "reason": "canary-required"}

    def _canary_source_head(self) -> str:
        try:
            return core.run_argv(["git", "rev-parse", "HEAD"], cwd=self.root, timeout=self.timeout).stdout.strip()
        except (OSError, subprocess.SubprocessError, core.ExecutorError) as exc:
            raise AdapterError("Orca canary could not resolve source head", details={"stage": "worktree-create"}) from exc

    def _canary_absence(self, path: Path) -> None:
        try:
            response = self._json_call([self.executable, "worktree", "show", "--worktree", "path:" + str(path), "--json"])
        except AdapterError as exc:
            code = str(exc.details.get("code", ""))
            if code in {"not_found", "worktree_not_found", "selector_not_found"}:
                return
            raise AdapterError("Orca canary could not prove checkout absence", details={"stage": "absence", **dict(exc.details)}) from exc
        if response.get("exists") is False or response.get("status") in {"removed", "not_found"}:
            return
        raise AdapterError("Orca canary checkout remains discoverable", details={"stage": "absence", "worktree_path": str(path)})

    def canary(self) -> dict[str, Any]:
        """Exercise the full worker lifecycle once, then persist only a clean proof."""
        decision = self.probe()
        if decision.get("status") == "unsupported":
            raise AdapterError(str(decision.get("reason", "Orca runtime is unsupported")), details={"stage": "preflight"})
        if decision.get("status") == "compatible":
            return decision
        runtime = decision.get("runtime")
        if not isinstance(runtime, Mapping):
            raise AdapterError("Orca canary lacks runtime identity", details={"stage": "preflight"})
        source_head = self._canary_source_head()
        destination = self.root.parent / ("." + self.root.name + "-orca-canary-" + self.feature)
        lane = {"id": "orca-canary", "feature": self.feature, "slice": "canary", "task": "lifecycle"}
        key = hashlib.sha256((self.feature + "\0" + source_head).encode("utf-8")).hexdigest()
        worktree: Mapping[str, Any] | None = None
        worker: Mapping[str, Any] | None = None
        accepted: Mapping[str, Any] | None = None
        released = False
        removed = False
        stage = "worktree-create"
        details: dict[str, Any] = {}
        try:
            creator = self._worktree_creator
            worktree = creator(destination, source_head) if creator is not None else core.create_git_worktree(self.root, destination, source_head)
            if not isinstance(worktree, Mapping):
                raise AdapterError("Orca canary worktree receipt is malformed")
            stage = "worker-start"
            worker = self.start_worker(lane, worktree, idempotency_key=key)
            stage = "worker-done"
            event = self.wait_events(worker, timeout=min(self.timeout, 30))
            if event.get("event") != "worker_done" or event.get("status") != "accepted":
                raise AdapterError("Orca canary worker did not complete", details={"event": dict(event)})
            stage = "worker-read"
            output = self.read_worker(worker)
            accepted = self.accept_worker_done(worker, event, output)
            stage = "worker-ack"
            self.ack_delivery(worker, event)
            stage = "worker-release"
            self.release(worker, accepted)
            released = True
            stage = "release-proof"
            status = self._call("worker-show", "--dispatch", _opaque_token(worker.get("dispatch_id"), "dispatch id"))
            if status.get("status") not in {"released", "completed", "complete", "exited"}:
                raise AdapterError("Orca canary release was not settled", details={"stage": stage, "dispatch_id": worker.get("dispatch_id")})
            stage = "worktree-remove"
            remover = self._worktree_remover
            removal = remover(worktree) if remover is not None else __import__("git_adapter").GitAdapter(self.root).remove_worktree(
                worktree["worktree_path"], expected_receipt=worktree, expected_head=source_head
            )
            if not isinstance(removal, Mapping) or removal.get("removed") is not True:
                raise AdapterError("Orca canary checkout removal was not proven")
            removed = True
            stage = "absence"
            self._canary_absence(Path(str(worktree["worktree_path"])))
            proof = {"source": "lifecycle-canary", "checked_at": time.time(), "cleanup": "clean"}
            receipt = {
                "version": 1, "feature": self.feature, "repository": str(self.root), "adapter": "orca",
                "runtime": dict(runtime), "proof": proof, "status": "compatible",
            }
            core.atomic_write_json(self._cache_path(), receipt)
            return receipt
        except Exception as exc:
            error_details = getattr(exc, "details", None)
            if isinstance(error_details, Mapping):
                details.update(error_details)
            details.setdefault("stage", stage)
            for field in ("run_id", "task_id", "dispatch_id", "terminal_handle"):
                if worker is not None and isinstance(worker.get(field), str):
                    details[field] = worker[field]
            if worktree is not None and isinstance(worktree.get("worktree_path"), str):
                details["worktree_path"] = worktree["worktree_path"]
            raise AdapterError("Orca canary failed at " + str(details.get("stage", stage)), details=_redact_payload(details)) from exc
        finally:
            if worker is not None and accepted is not None and not released:
                try:
                    self.release(worker, accepted)
                    released = True
                except Exception:
                    details.setdefault("cleanup", "worker-retained")
            if worktree is not None and released and not removed:
                try:
                    remover = self._worktree_remover
                    if remover is not None:
                        remover(worktree)
                    else:
                        __import__("git_adapter").GitAdapter(self.root).remove_worktree(
                            worktree["worktree_path"], expected_receipt=worktree, expected_head=source_head
                        )
                    removed = True
                except Exception:
                    details.setdefault("cleanup", "worktree-retained")

    def _json_call(self, argv: list[str], *, timeout: float | None = None) -> dict[str, Any]:
        try:
            completed = self.runner(
                argv,
                cwd=self.root,
                timeout=self.timeout if timeout is None else timeout,
                check=True,
                shell=False,
            )
        except subprocess.CalledProcessError as exc:
            details = _failure_details(exc)
            if "worker-release" in argv and _is_identity_unproven_release(details):
                provider_code = details.get("code")
                details = {**details, "code": "release_identity_unproven", "provider_code": provider_code}
                raise AdapterError("Orca worker release blocked: release_identity_unproven", details=details) from exc
            code = details.get("code", "command_failed")
            raise AdapterError(f"Orca command failed: {code}", details=details) from exc
        except (OSError, subprocess.SubprocessError, core.ExecutorError, TypeError) as exc:
            raise AdapterError("Orca command failed") from exc
        try:
            return _payload(json.loads(completed.stdout))
        except (AttributeError, TypeError, json.JSONDecodeError) as exc:
            raise AdapterError("malformed Orca response") from exc

    def _call(self, *arguments: str, timeout: float | None = None) -> dict[str, Any]:
        return self._json_call([self.executable, "orchestration", *arguments, "--json"], timeout=timeout)

    def _reconcile_tab_not_found_release(
        self, dispatch_id: str, terminal_handle: str, request_key: str, error: AdapterError
    ) -> dict[str, Any]:
        post = self._call("worker-show", "--dispatch", dispatch_id)
        actual_dispatch = post.get("dispatch_id") or post.get("dispatchId")
        try:
            actual_dispatch = _opaque_token(actual_dispatch, "dispatch id")
        except AdapterError:
            actual_dispatch = None
        post_terminal = _nested_terminal_handle(post)
        try:
            post_terminal = _opaque_token(post_terminal, "terminal handle")
        except AdapterError:
            post_terminal = None
        terminal_state = _nested_terminal_state(post)
        post_status = post.get("status") or post.get("state")
        if (
            actual_dispatch != dispatch_id
            or post_terminal != terminal_handle
            or post_status not in {"failed", "stopped", "abandoned", "released"}
            or not isinstance(terminal_state, Mapping)
            or terminal_state.get("status") != "exited"
            or terminal_state.get("connected") is not False
            or terminal_state.get("writable") is not False
        ):
            raise AdapterError(
                "Orca dispatch release remains unknown",
                details={"code": "release_unknown", "dispatch_id": dispatch_id, "terminal_handle": terminal_handle},
            ) from error
        self._revoked_dispatches.add(dispatch_id)
        return {
            "released": True,
            "reconciled": True,
            "idempotency_key": request_key,
            "reason": "tab_not_found",
            "error": "tab_not_found",
            "release_error": "tab_not_found",
            "dispatch_id": dispatch_id,
            "terminal_handle": terminal_handle,
            "terminal_status": "exited",
            "connected": False,
            "writable": False,
        }

    def _discover_worktree(self, path: str) -> str:
        expected = Path(path).resolve()
        last_error: AdapterError | None = None
        selector = "path:" + path
        started = self._clock()
        deadline = started + self._discovery_timeout
        attempts = 0
        backoff = WORKTREE_DISCOVERY_INITIAL_BACKOFF_SECONDS
        while True:
            attempts += 1
            try:
                response = self._json_call(
                    [self.executable, "worktree", "show", "--worktree", selector, "--json"]
                )
                candidate = response.get("worktree_path") or response.get("worktreePath")
                if candidate is None:
                    raise AdapterError(
                        "malformed Orca worktree discovery",
                        details={"code": "malformed_worktree_receipt", "stage": "worktree-discovery", "selector": selector},
                    )
                candidate_value = _text(candidate, "worktree path")
                if not Path(candidate_value).is_absolute():
                    raise AdapterError(
                        "malformed Orca worktree discovery",
                        details={"code": "malformed_worktree_receipt", "stage": "worktree-discovery", "selector": selector},
                    )
                candidate_path = Path(candidate_value).resolve()
                if candidate_path != expected:
                    raise AdapterError("uncorrelated Orca worktree discovery")
                return str(candidate_path)
            except AdapterError as exc:
                if exc.details.get("code") != "selector_not_found":
                    raise
                last_error = exc
            now = self._clock()
            remaining = deadline - now
            if remaining <= 0:
                break
            delay = min(backoff, remaining)
            self._sleep(delay)
            backoff = min(backoff * 2, WORKTREE_DISCOVERY_MAX_BACKOFF_SECONDS)
        elapsed_ms = max(0, int((self._clock() - started) * 1000))
        details = dict(last_error.details) if last_error is not None else {"code": "selector_not_found"}
        details.update({"stage": "worktree-discovery", "attempts": attempts, "elapsed_ms": elapsed_ms, "selector": selector})
        raise AdapterError("Orca worktree discovery timed out", details=details)

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
        matches: list[str] = []
        for run in runs:
            if isinstance(run, Mapping) and _scoped_field(run, "objective", "run") == objective:
                run_id = _scoped_identifier(run, "run_id", "run")
                matches.append(_opaque_token(run_id, "run id"))
        if len(matches) > 1:
            raise AdapterError("multiple matching Orca runs")
        return matches[0] if matches else None

    def _ensure_run(self, key: str) -> str:
        objective = f"parallel-slice:{self.feature}:{key}"
        run_id = self._find_run(objective)
        if run_id is not None:
            return run_id
        response = self._call("run-create", "--objective", objective)
        response_objective = _scoped_field(response, "objective", "run")
        if response_objective != objective:
            raise AdapterError("uncorrelated Orca run receipt")
        return _opaque_token(_scoped_identifier(response, "run_id", "run"), "run id")

    def _find_task(self, run_id: str, spec: str) -> str | None:
        response = self._call("task-list", "--run", run_id)
        tasks = response.get("tasks", [])
        if not isinstance(tasks, list):
            raise AdapterError("malformed Orca task list")
        matches: list[str] = []
        for task in tasks:
            if isinstance(task, Mapping) and _scoped_field(task, "spec", "task") == spec:
                task_run = _scoped_identifier(task, "run_id", "run")
                if task_run is not None and task_run != run_id:
                    raise AdapterError("uncorrelated Orca task receipt")
                matches.append(_opaque_token(_scoped_identifier(task, "task_id", "task"), "task id"))
        if len(matches) > 1:
            raise AdapterError("multiple matching Orca tasks")
        return matches[0] if matches else None

    def _ensure_task(self, run_id: str, lane: Mapping[str, Any], key: str) -> str:
        slice_id = _text(lane.get("slice"), "lane slice")
        task_name = _text(lane.get("task"), "lane task")
        spec = f"parallel-slice:{self.feature}:{slice_id}:{task_name}:{key}"
        task_id = self._find_task(run_id, spec)
        if task_id is not None:
            return task_id
        response = self._call("task-create", "--run", run_id, "--spec", spec)
        response_run = _scoped_identifier(response, "run_id", "run")
        if response_run not in (None, run_id):
            raise AdapterError("uncorrelated Orca task receipt")
        response_spec = _scoped_field(response, "spec", "task")
        if response_spec != spec:
            raise AdapterError("uncorrelated Orca task receipt")
        return _opaque_token(_scoped_identifier(response, "task_id", "task"), "task id")

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
        allowed = {
            "feature", "slice", "task", "worktree_id", "worktree_path", "branch", "pre_head", "idempotency_key",
            "run_id", "runId", "task_id", "taskId", "orchestration_task_id", "dispatch_id", "dispatchId",
            "terminal_handle", "terminalHandle", "agentTerminalHandle", "status",
            "ok", "result", "error", "run", "task", "worker", "dispatch", "terminal", "terminalResource",
            "terminal_resource", "mutation", "release", "state", "lastError", "last_error", "releaseState",
            "release_state", "releaseError", "release_error", "request_id", "requestId", "idempotencyKey",
            "retryRequest", "retry_request", "retryRequestId", "retry_request_id", "retryOf", "retry_of", "resource_id",
            "resourceId", "ownershipState", "ownership_state", "retainedReason", "retained_reason",
            "releaseRequestedAt", "release_requested_at", "releaseCompletedAt", "release_completed_at", "code",
        }
        unknown = set(data) - allowed
        if unknown:
            raise AdapterError("unknown Orca worker receipt field")
        pending = [data.get("worker")]
        result = data.get("result")
        if isinstance(result, Mapping):
            pending.append(result.get("worker"))
        while pending:
            nested_worker = pending.pop()
            if not isinstance(nested_worker, Mapping):
                continue
            if set(nested_worker) - allowed:
                raise AdapterError("unknown Orca worker receipt field")
            nested_result = nested_worker.get("result")
            if isinstance(nested_result, Mapping):
                pending.append(nested_result.get("worker"))
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
        data["dispatch_id"] = _opaque_token(data.get("dispatch_id"), "dispatch id")
        data["terminal_handle"] = _text(data.get("terminal_handle"), "terminal handle")
        return {
            **{field: data[field] for field in expected},
            "run_id": data["run_id"],
            "task_id": actual_task,
            "orchestration_task_id": actual_task,
            "dispatch_id": data["dispatch_id"],
            "terminal_handle": data["terminal_handle"],
            **({"status": data["status"]} if "status" in data else {}),
        }

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
            dispatch_id = _opaque_token(data.get("dispatch_id"), "dispatch id")
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
        try:
            worker_path = self._discover_worktree(worktree["worktree_path"])
            response = self._call(
                "worker-start", "--task", task_id, "--worktree", "path:" + worker_path, "--agent", "codex",
                "--timeout-ms", str(WORKER_START_TIMEOUT_MS),
            )
        except AdapterError as exc:
            raise AdapterError(str(exc), details={**exc.details, "run_id": run_id, "task_id": task_id}) from exc
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
        dispatch_id = _opaque_token(payload.get("dispatchId") or payload.get("dispatch_id"), "dispatch id")
        if task_id != receipt.get("orchestration_task_id"):
            raise AdapterError("uncorrelated Orca delivery: taskId")
        if dispatch_id != receipt.get("dispatch_id"):
            raise AdapterError("uncorrelated Orca delivery: dispatchId")
        if dispatch_id in self._revoked_dispatches:
            raise AdapterError("stale Orca delivery from revoked dispatch")
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
            **({"dependency": safe_payload["dependency"]} if "dependency" in safe_payload else {}),
        }

    def read_worker(self, receipt: Mapping[str, Any]) -> dict[str, Any]:
        dispatch_id = _opaque_token(receipt.get("dispatch_id"), "dispatch id")
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
        source_identity = response.get("source_identity") or response.get("sourceIdentity")
        if source_identity != receipt.get("terminal_handle"):
            raise AdapterError("uncorrelated worker-read source")
        return {
            "dispatch_id": dispatch_id,
            "source": response.get("source"),
            "source_identity": source_identity,
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

    def ack_delivery(self, receipt: Mapping[str, Any], delivery: Mapping[str, Any]) -> dict[str, Any]:
        delivery_id = _text(delivery.get("delivery_id"), "delivery id")
        run_id = _text(receipt.get("run_id"), "run id")
        response = self._call("check", "--run", run_id, "--ack", delivery_id)
        if response.get("acknowledged") is not True:
            raise AdapterError("Orca delivery acknowledgement failed")
        if response.get("delivery_id") != delivery_id:
            raise AdapterError("uncorrelated Orca acknowledgement")
        return {"acknowledged": True, "delivery_id": delivery_id}

    def reconcile_action(self, action: Mapping[str, Any]) -> Mapping[str, Any] | None:
        if action.get("action") == "worker":
            partial = action.get("partial_effect")
            plan = action.get("worker_plan")
            receipt = action.get("worktree_receipt")
            if not isinstance(partial, Mapping) or not isinstance(plan, Mapping) or not isinstance(receipt, Mapping):
                return None
            action_key = _text(action.get("key"), "idempotency key")
            cached = self._workers.get(action_key)
            if cached is not None:
                return dict(cached)
            normalized_partial = _payload(dict(partial))
            if isinstance(partial, dict):
                for field in (
                    "run_id", "task_id", "dispatch_id", "terminal_handle", "request_id", "idempotency_key",
                    "retry_request", "state", "lastError", "releaseState", "releaseError", "released",
                    "reconciled", "terminal_status", "connected", "writable", "reason", "release_error",
                    "resource_id", "worktree_id", "owner_dispatch_id", "origin_dispatch_id", "ownershipState",
                    "retainedReason", "releaseRequestedAt", "releaseCompletedAt",
                ):
                    if field in normalized_partial:
                        partial[field] = normalized_partial[field]
            run_id = _text(normalized_partial.get("run_id"), "run id")
            task_id = _text(normalized_partial.get("task_id"), "task id")
            persisted_terminal = normalized_partial.get("terminal_handle")
            if persisted_terminal is not None:
                persisted_terminal = _opaque_token(persisted_terminal, "terminal handle")
            dispatch_id = _opaque_token(normalized_partial.get("dispatch_id"), "dispatch id")
            status_response = self._call("worker-show", "--dispatch", dispatch_id)
            actual_dispatch = status_response.get("dispatch_id") or status_response.get("dispatchId")
            try:
                normalized_actual = _opaque_token(actual_dispatch, "dispatch id")
            except AdapterError:
                normalized_actual = None
            if normalized_actual != dispatch_id:
                raise AdapterError(
                    "uncorrelated Orca dispatch status",
                    details={"code": "uncorrelated_dispatch", "dispatch_id": dispatch_id, "actual_dispatch": normalized_actual},
                )
            authoritative_terminal = _nested_terminal_handle(status_response)
            try:
                authoritative_terminal = _opaque_token(authoritative_terminal, "terminal handle")
            except AdapterError:
                raise AdapterError(
                    "uncorrelated Orca terminal status",
                    details={"code": "uncorrelated_terminal", "dispatch_id": dispatch_id},
                )
            if persisted_terminal is not None and persisted_terminal != authoritative_terminal:
                raise AdapterError(
                    "uncorrelated Orca terminal status",
                    details={"code": "uncorrelated_terminal", "dispatch_id": dispatch_id},
                )
            if isinstance(partial, dict):
                partial["terminal_handle"] = authoritative_terminal
            status = status_response.get("status") or status_response.get("state")
            if isinstance(partial, dict):
                for field in (
                    "resource_id", "worktree_id", "owner_dispatch_id", "origin_dispatch_id", "ownershipState",
                    "releaseState", "retainedReason", "releaseRequestedAt", "releaseCompletedAt", "releaseError",
                ):
                    if field in status_response:
                        partial[field] = status_response[field]
                provider_resource = _nested_resource(status_response)
                if provider_resource is not None:
                    partial["terminalResource"] = dict(provider_resource)
            release = partial.get("recovery_release")
            expected_release_key = action_key + ":recovery-release"
            release_accepted = (
                isinstance(release, Mapping)
                and release.get("released") is True
                and release.get("dispatch_id") == dispatch_id
                and release.get("idempotency_key") == expected_release_key
            )
            if release_accepted and release.get("reconciled") is True:
                release_accepted = all(
                    release.get(field) == expected
                    for field, expected in {
                        "terminal_handle": authoritative_terminal,
                        "terminal_status": "exited",
                        "connected": False,
                        "writable": False,
                        "reason": "tab_not_found",
                        "error": "tab_not_found",
                    }.items()
                )
            if release_accepted:
                self._revoked_dispatches.add(dispatch_id)
            if status == "released" and not release_accepted:
                raise AdapterError(
                    "Orca released dispatch lacks its recovery receipt",
                    details={"code": "worker_outcome_unknown", "dispatch_id": dispatch_id, "status": status},
                )
            if status not in {"failed", "stopped", "abandoned", "revoked", "exited", "released"}:
                code = "worker_outcome_unknown" if status in {None, "unknown", "outcome_unknown"} else "worker_still_live"
                raise AdapterError("Orca worker dispatch is not reclaimable", details={"code": code, "dispatch_id": dispatch_id, "status": status or "unknown"})
            persisted_reason = normalized_partial.get("retainedReason") or normalized_partial.get("reason")
            persisted_release_state = normalized_partial.get("releaseState") or normalized_partial.get("release_state")
            provider_resource = _nested_resource(status_response)
            provider_release_state = None if provider_resource is None else provider_resource.get("releaseState") or provider_resource.get("release_state")
            provider_reason = None if provider_resource is None else provider_resource.get("retainedReason") or provider_resource.get("retained_reason") or provider_resource.get("reason")
            retained_state = persisted_release_state == "retained" or provider_release_state == "retained"
            retained_reason = persisted_reason or provider_reason
            if not release_accepted and (
                normalized_partial.get("code") == "release_identity_unproven"
                or retained_state
                or retained_reason in {"identity_unproven", "user_takeover"}
            ):
                code = "release_identity_unproven" if retained_reason == "identity_unproven" else "recovery_stop_unproven"
                details = {
                    **dict(normalized_partial), "code": code, "dispatch_id": dispatch_id,
                    "releaseState": persisted_release_state or provider_release_state,
                    "retainedReason": retained_reason,
                    "idempotent": True,
                }
                if provider_resource is not None:
                    details["terminalResource"] = dict(provider_resource)
                raise AdapterError("Orca retained terminal resource blocks recovery", details=details)
            stop_request = action_key + ":recovery-stop"
            if status in {"failed", "stopped", "revoked"} and self._requires_recovery_stop(status_response, dispatch_id, authoritative_terminal):
                stop = partial.get("recovery_stop")
                if isinstance(stop, Mapping):
                    if stop.get("dispatch_id") != dispatch_id or stop.get("retry_request") != stop_request:
                        raise AdapterError(
                            "uncorrelated persisted recovery stop",
                            details={"code": "recovery_stop_unproven", "dispatch_id": dispatch_id, "retry_request": stop_request},
                        )
                    if stop.get("status") == "pending":
                        stop = self._stop_worker(dispatch_id, stop_request)
                        if isinstance(partial, dict):
                            partial["recovery_stop"] = dict(stop)
                    elif stop.get("stopped") is not True:
                        raise AdapterError(
                            "uncorrelated persisted recovery stop",
                            details={"code": "recovery_stop_unproven", "dispatch_id": dispatch_id, "retry_request": stop_request},
                        )
                else:
                    if isinstance(partial, dict):
                        partial["recovery_stop"] = {"status": "pending", "dispatch_id": dispatch_id, "retry_request": stop_request}
                    stop = self._stop_worker(dispatch_id, stop_request)
                    if isinstance(partial, dict):
                        partial["recovery_stop"] = dict(stop)
                stopped_response = self._call("worker-show", "--dispatch", dispatch_id)
                stopped_dispatch = stopped_response.get("dispatch_id") or stopped_response.get("dispatchId")
                stopped_terminal = _nested_terminal_handle(stopped_response)
                stopped_state = _nested_terminal_state(stopped_response)
                stopped_status = stopped_response.get("status") or stopped_response.get("state")
                if (
                    stopped_dispatch != dispatch_id
                    or stopped_terminal != authoritative_terminal
                    or stopped_status not in {"stopped", "exited", "released"}
                    or not isinstance(stopped_state, Mapping)
                    or stopped_state.get("status") != "exited"
                    or stopped_state.get("connected") is not False
                    or stopped_state.get("writable") is not False
                ):
                    raise AdapterError(
                        "Orca recovery stop did not fence the worker",
                        details={"code": "recovery_stop_unproven", "dispatch_id": dispatch_id, "terminal_handle": authoritative_terminal},
                    )
                status_response = stopped_response
                status = stopped_status
            if not release_accepted:
                try:
                    release = self._release({"idempotency_key": _text(action.get("key"), "idempotency key") + ":recovery-release", "dispatch_id": dispatch_id})
                except AdapterError as exc:
                    if exc.details.get("code") != "tab_not_found":
                        raise
                    release = self._reconcile_tab_not_found_release(dispatch_id, authoritative_terminal, expected_release_key, exc)
                partial["recovery_release"] = dict(release)
            worker_path = self._discover_worktree(_text(receipt.get("worktree_path"), "worktree path"))
            response = self._call(
                "worker-start", "--task", task_id, "--retry-of", dispatch_id,
                "--worktree", "path:" + worker_path, "--agent", "codex",
                "--timeout-ms", str(WORKER_START_TIMEOUT_MS),
            )
            worker = self._authoritative_worker(response, plan, receipt, action_key, task_id=task_id)
            if worker.get("run_id") != run_id:
                raise AdapterError("uncorrelated Orca run receipt")
            worker["status"] = "running"
            self._workers[action_key] = dict(worker)
            return worker
        if action.get("action") == "worker_ack":
            delivery_id = _text(action.get("delivery_id"), "delivery id")
            run_id = _text(action.get("run_id"), "run id")
            return self.ack_delivery({"run_id": run_id}, {"delivery_id": delivery_id})
        if action.get("action") != "worker_release":
            return None
        dispatch_id = _opaque_token(action.get("dispatch_id"), "dispatch id")
        status = self._call("worker-show", "--dispatch", dispatch_id).get("status")
        if status in {"released", "complete", "completed"}:
            return {"released": True, "dispatch_id": dispatch_id}
        return self._release({"idempotency_key": _text(action.get("key"), "idempotency key"), "dispatch_id": dispatch_id})

    def _release(self, receipt: Mapping[str, Any]) -> dict[str, Any]:
        key = _text(receipt.get("idempotency_key"), "idempotency key")
        if key in self._released:
            return {**self._released[key], "idempotency_key": key, "idempotent": True}
        prior_failure = self._release_failures.get(key)
        if prior_failure is not None:
            raise AdapterError(
                str(prior_failure["message"]),
                details={**dict(prior_failure["details"]), "idempotent": True},
            )
        dispatch_id = _opaque_token(receipt.get("dispatch_id"), "dispatch id")
        try:
            response = self._call("worker-release", "--dispatch", dispatch_id)
        except AdapterError as exc:
            if exc.details.get("code") != "release_identity_unproven":
                raise
            details = {**dict(exc.details), "dispatch_id": dispatch_id, "idempotency_key": key}
            failure = {"message": "Orca worker release blocked: release_identity_unproven", "details": details}
            self._release_failures[key] = failure
            raise AdapterError(str(failure["message"]), details=details) from exc
        actual_dispatch = response.get("dispatch_id") or response.get("dispatchId")
        if actual_dispatch != dispatch_id:
            raise AdapterError(
                "uncorrelated Orca release receipt",
                details={"code": "uncorrelated_release", "dispatch_id": dispatch_id, "actual_dispatch": actual_dispatch},
            )
        release_state = str(response.get("releaseState") or response.get("release_state") or "").lower()
        explicit_released = response.get("released")
        accepted = explicit_released is True or (release_state in {"released", "completed"} and explicit_released is not False)
        if not accepted:
            code = str(response.get("code") or response.get("retainedReason") or "release_not_accepted")
            if _is_identity_unproven_release(response) or code == "identity_unproven":
                code = "release_identity_unproven"
            details = {
                **dict(response),
                "code": code,
                "provider_code": response.get("code"),
                "dispatch_id": dispatch_id,
                "idempotency_key": key,
            }
            failure = {"message": f"Orca worker release blocked: {code}", "details": details}
            self._release_failures[key] = failure
            raise AdapterError(str(failure["message"]), details=details)
        result = {**dict(response), "released": True, "dispatch_id": dispatch_id, "idempotency_key": key}
        self._released[key] = result
        self._revoked_dispatches.add(dispatch_id)
        return dict(result)

    def _stop_worker(self, dispatch_id: str, retry_request: str) -> dict[str, Any]:
        if retry_request in self._stopped:
            return {**self._stopped[retry_request], "idempotent": True}
        prior_failure = self._stop_failures.get(retry_request)
        if prior_failure is not None:
            raise AdapterError(str(prior_failure["message"]), details={**dict(prior_failure["details"]), "idempotent": True})
        response = self._call("worker-stop", "--dispatch", dispatch_id, "--retry-request", retry_request)
        actual_dispatch = response.get("dispatch_id") or response.get("dispatchId")
        if actual_dispatch != dispatch_id:
            raise AdapterError(
                "uncorrelated Orca stop receipt",
                details={"code": "recovery_stop_uncorrelated", "dispatch_id": dispatch_id, "actual_dispatch": actual_dispatch},
            )
        status = response.get("status") or response.get("state")
        if response.get("stopped") is not True and status not in {"stopped", "exited"}:
            details = {**dict(response), "code": "recovery_stop_failed", "dispatch_id": dispatch_id, "retry_request": retry_request}
            failure = {"message": "Orca worker stop was not accepted", "details": details}
            self._stop_failures[retry_request] = failure
            raise AdapterError(str(failure["message"]), details=details)
        result = {**dict(response), "stopped": True, "dispatch_id": dispatch_id, "retry_request": retry_request}
        self._stopped[retry_request] = result
        return dict(result)

    def _requires_recovery_stop(self, response: Mapping[str, Any], dispatch_id: str, terminal_handle: str) -> bool:
        terminal_state = _nested_terminal_state(response)
        live = isinstance(terminal_state, Mapping) and terminal_state.get("connected") is True and terminal_state.get("writable") is True
        if not live:
            return False
        resource = _nested_resource(response)
        ownership = None if resource is None else resource.get("ownershipState") or resource.get("ownership_state")
        owner = None if resource is None else (_resource_dispatch_identity(resource, "owner_dispatch_id") or _resource_dispatch_identity(resource, "owner"))
        origin = None if resource is None else (_resource_dispatch_identity(resource, "origin_dispatch_id") or _resource_dispatch_identity(resource, "origin"))
        if ownership != "owned" or owner != dispatch_id or origin != dispatch_id:
            raise AdapterError(
                "Orca live failed worker is not safely owned for recovery stop",
                details={
                    "code": "recovery_stop_unproven", "dispatch_id": dispatch_id, "terminal_handle": terminal_handle,
                    "ownershipState": ownership, "owner_dispatch_id": owner, "origin_dispatch_id": origin,
                },
            )
        return True

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
        response = self._call(
            "worker-start", "--task", next_task, "--terminal", _text(receipt.get("terminal_handle"), "terminal handle"),
            "--timeout-ms", str(WORKER_START_TIMEOUT_MS),
        )
        lane = {"feature": self.feature, "slice": receipt["slice"], "task": receipt["task"]}
        worktree = {key: receipt[key] for key in ("worktree_id", "worktree_path", "branch", "pre_head")}
        key = _text(idempotency_key or receipt.get("idempotency_key"), "idempotency key")
        return self._authoritative_worker(response, lane, worktree, key, task_id=next_task)


Adapter = OrcaAdapter
