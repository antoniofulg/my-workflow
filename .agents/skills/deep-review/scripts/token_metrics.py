#!/usr/bin/env python3
"""Content-safe observational token metrics for compatible providers."""

from __future__ import annotations

import json
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

USAGE_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
)


class TokenMetricsError(Exception):
    """Safe error used internally when a measurement cannot be trusted."""


def _empty_usage() -> dict[str, int | None]:
    return {"total_tokens": 0, **{field: None for field in USAGE_FIELDS}}


def _safe_count(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def _usage(value: object) -> bool:
    expected = {"total_tokens", *USAGE_FIELDS}
    return (
        isinstance(value, dict)
        and set(value) == expected
        and _safe_count(value["total_tokens"]) is not None
        and all(value[field] is None or _safe_count(value[field]) is not None for field in USAGE_FIELDS)
    )


def _timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _rollout_usage(path: object) -> dict[str, int | None]:
    if not isinstance(path, str) or not path or not Path(path).is_file():
        return {field: None for field in USAGE_FIELDS}
    latest: object = None
    try:
        with Path(path).open(encoding="utf-8", errors="replace") as stream:
            for line in stream:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                payload = event.get("payload") if isinstance(event, dict) else None
                if not isinstance(payload, dict) or payload.get("type") != "token_count":
                    continue
                info = payload.get("info")
                if not isinstance(info, dict):
                    latest = None
                    continue
                candidate = info.get("total_token_usage", info.get("last_token_usage"))
                latest = candidate if isinstance(candidate, dict) else None
    except OSError:
        return {field: None for field in USAGE_FIELDS}
    if not isinstance(latest, dict):
        return {field: None for field in USAGE_FIELDS}
    return {field: _safe_count(latest.get(field)) for field in USAGE_FIELDS}


def read_telemetry(db_path: str | Path, reviewer_prefix: str) -> dict[str, dict[str, int | None]]:
    """Read only allowlisted counters for the explicitly configured path."""
    path = Path(db_path).expanduser()
    prefix = reviewer_prefix.rstrip("/") if isinstance(reviewer_prefix, str) else ""
    if not prefix or not path.is_file():
        raise TokenMetricsError("telemetry")
    db: sqlite3.Connection | None = None
    try:
        db = sqlite3.connect(path.as_posix())
        db.execute("PRAGMA query_only = ON")
        columns = {row[1] for row in db.execute("PRAGMA table_info(threads)")}
        if not {"id", "rollout_path", "tokens_used", "agent_path"}.issubset(columns):
            raise TokenMetricsError("telemetry")
        result: dict[str, dict[str, int | None]] = {}
        for thread_id, rollout_path, tokens_used, agent_path in db.execute(
            "SELECT id, rollout_path, tokens_used, agent_path FROM threads"
        ):
            if not isinstance(thread_id, str):
                raise TokenMetricsError("telemetry")
            if not isinstance(agent_path, str) or not (agent_path == prefix or agent_path.startswith(prefix + "/")):
                continue
            total = _safe_count(tokens_used)
            if total is None:
                raise TokenMetricsError("telemetry")
            result[thread_id] = {"total_tokens": total, **_rollout_usage(rollout_path)}
        return result
    except TokenMetricsError:
        raise
    except (OSError, sqlite3.Error):
        raise TokenMetricsError("telemetry") from None
    finally:
        if db is not None:
            db.close()


def delta_usage(baseline: dict[str, dict[str, int | None]], snapshot: dict[str, dict[str, int | None]]) -> dict[str, int | None]:
    if not set(baseline).issubset(snapshot):
        raise TokenMetricsError("telemetry")
    rows = []
    for thread_id, current in snapshot.items():
        previous = baseline.get(thread_id, _empty_usage())
        total = int(current["total_tokens"]) - int(previous["total_tokens"])
        if total < 0:
            raise TokenMetricsError("telemetry")
        detail: dict[str, int | None] = {"total_tokens": total}
        for field in USAGE_FIELDS:
            current_value, baseline_value = current[field], previous[field]
            if current_value is None:
                detail[field] = None
            elif baseline_value is None:
                detail[field] = current_value
            else:
                detail[field] = current_value - baseline_value
                if detail[field] < 0:
                    raise TokenMetricsError("telemetry")
        rows.append(detail)
    result: dict[str, int | None] = {"total_tokens": sum(int(row["total_tokens"]) for row in rows)}
    for field in USAGE_FIELDS:
        result[field] = None if any(row[field] is None for row in rows) else sum(int(row[field]) for row in rows)
    return result


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{secrets.token_hex(4)}.tmp")
    try:
        temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _scope(options: dict) -> dict:
    return {
        "repository": str(options.get("repository", "unknown")),
        "round": int(options.get("round", 0)),
        "base": str(options.get("base", "unknown")),
        "head": str(options.get("head", "unknown")),
        "selected_files": int(options.get("selected_files", 0)),
        "carried_files": int(options.get("carried_files", 0)),
        "jobs": int(options.get("jobs", 0)),
        "model": str(options.get("model", "unknown")),
        "reasoning_effort": str(options.get("reasoning", "unknown")),
        "reviewer_prefix": str(options.get("reviewer_prefix", "")),
    }


def _unavailable(path: Path, reason: str, scope: dict | None = None, db_path: str | Path | None = None) -> dict:
    payload = {
        "schema_version": 1,
        "kind": "review_token_metrics",
        "started_at": _now(),
        "finalized_at": _now(),
        "runtime_db": str(Path(db_path).expanduser().resolve()) if db_path else "",
        "scope": scope or _scope({}),
        "status": "unavailable",
        "reason": reason,
    }
    _write_json(path, payload)
    return payload


def _valid_metrics(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    if value.get("status") == "unavailable":
        return set(value) == {"schema_version", "kind", "started_at", "finalized_at", "runtime_db", "scope", "status", "reason"} and value["kind"] == "review_token_metrics" and _timestamp(value["started_at"]) and _timestamp(value["finalized_at"]) and isinstance(value["reason"], str)
    expected = {"schema_version", "kind", "started_at", "finalized_at", "runtime_db", "scope", "baseline_by_thread", "reviewer_thread_count", "checkpoints", "usage", "status"}
    if set(value) != expected or value["schema_version"] != 1 or value["kind"] != "review_token_metrics" or not _timestamp(value["started_at"]):
        return False
    if value["finalized_at"] is not None and not _timestamp(value["finalized_at"]):
        return False
    scope = value["scope"]
    required_scope = {"repository", "round", "base", "head", "selected_files", "carried_files", "jobs", "model", "reasoning_effort", "reviewer_prefix"}
    if not isinstance(scope, dict) or set(scope) != required_scope or not isinstance(scope["reviewer_prefix"], str):
        return False
    if not all(isinstance(scope[key], str) and bool(scope[key]) for key in ("repository", "base", "head", "model", "reasoning_effort")):
        return False
    if not all(isinstance(scope[key], int) and scope[key] >= 0 for key in ("round", "selected_files", "carried_files", "jobs")):
        return False
    return (
        isinstance(value["runtime_db"], str)
        and isinstance(value["baseline_by_thread"], dict)
        and all(_usage(row) for row in value["baseline_by_thread"].values())
        and isinstance(value["reviewer_thread_count"], int)
        and isinstance(value["checkpoints"], list)
        and all(isinstance(row, dict) and set(row) == {"recorded_at", "completed_jobs", "usage"} and _timestamp(row["recorded_at"]) and isinstance(row["completed_jobs"], int) and row["completed_jobs"] >= 0 and _usage(row["usage"]) for row in value["checkpoints"])
        and _usage(value["usage"])
        and value["status"] in {"running", "complete"}
        and (value["status"] == "running" or value["finalized_at"] is not None)
    )


def read_metrics(path: str | Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise TokenMetricsError("ledger") from None
    if not _valid_metrics(value):
        raise TokenMetricsError("ledger")
    return value


def start_metrics(path: str | Path, db_path: str | Path | None, reviewer_prefix: str | None, **options) -> dict:
    state_path = Path(path).expanduser()
    scope = _scope({**options, "reviewer_prefix": reviewer_prefix or ""})
    if state_path.exists():
        try:
            metrics = read_metrics(state_path)
        except TokenMetricsError:
            return _unavailable(state_path, "persisted metrics unavailable", scope, db_path)
        if metrics["status"] == "unavailable":
            return metrics
        if metrics["scope"] != scope or metrics["runtime_db"] != str(Path(db_path).expanduser().resolve() if db_path else ""):
            return _unavailable(state_path, "metrics scope unavailable", scope, db_path)
        if metrics["status"] == "complete":
            return metrics
        return validate_metrics(state_path)
    if not db_path or not reviewer_prefix:
        return _unavailable(state_path, "compatible telemetry unavailable", scope, db_path)
    try:
        snapshot = read_telemetry(db_path, reviewer_prefix)
    except TokenMetricsError:
        return _unavailable(state_path, "compatible telemetry unavailable", scope, db_path)
    metrics = {
        "schema_version": 1,
        "kind": "review_token_metrics",
        "started_at": _now(),
        "finalized_at": None,
        "runtime_db": str(Path(db_path).expanduser().resolve()),
        "scope": scope,
        "baseline_by_thread": snapshot,
        "reviewer_thread_count": len(snapshot),
        "checkpoints": [],
        "usage": _empty_usage(),
        "status": "running",
    }
    _write_json(state_path, metrics)
    return metrics


def _measure(path: Path, metrics: dict) -> dict:
    if metrics["status"] != "running":
        return metrics
    try:
        snapshot = read_telemetry(metrics["runtime_db"], metrics["scope"]["reviewer_prefix"])
        usage = delta_usage(metrics["baseline_by_thread"], snapshot)
        if usage["total_tokens"] < metrics["usage"]["total_tokens"]:
            raise TokenMetricsError("telemetry")
    except TokenMetricsError:
        return _unavailable(path, "runtime telemetry unavailable", metrics["scope"], metrics["runtime_db"])
    return {**metrics, "reviewer_thread_count": len(snapshot), "usage": usage}


def validate_metrics(path: str | Path) -> dict:
    state_path = Path(path)
    metrics = read_metrics(state_path)
    measured = _measure(state_path, metrics)
    if measured is not metrics:
        _write_json(state_path, measured)
    return measured


def checkpoint_metrics(path: str | Path, completed_jobs: int) -> dict:
    state_path = Path(path)
    metrics = read_metrics(state_path)
    measured = _measure(state_path, metrics)
    if measured["status"] == "unavailable":
        return measured
    checkpoint = {"recorded_at": _now(), "completed_jobs": max(0, int(completed_jobs)), "usage": measured["usage"]}
    next_metrics = {**measured, "checkpoints": [*measured["checkpoints"], checkpoint]}
    _write_json(state_path, next_metrics)
    return next_metrics


def finalize_metrics(path: str | Path) -> dict:
    state_path = Path(path)
    metrics = read_metrics(state_path)
    if metrics["status"] in {"complete", "unavailable"}:
        return metrics
    measured = _measure(state_path, metrics)
    if measured["status"] == "unavailable":
        return measured
    finalized = {**measured, "finalized_at": _now(), "status": "complete"}
    _write_json(state_path, finalized)
    return finalized


def write_unavailable_metrics(path: str | Path, reason: str = "compatible telemetry unavailable") -> None:
    _unavailable(Path(path), reason)
