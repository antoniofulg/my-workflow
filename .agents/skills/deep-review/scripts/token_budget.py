#!/usr/bin/env python3
"""Content-safe Codex token snapshots and per-round budget checkpoints."""

from __future__ import annotations

import json
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_BUDGET_TOKENS = 15_000_000
USAGE_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
)


class TokenBudgetError(Exception):
    """Safe, user-facing error with no telemetry internals."""

    def __init__(self, kind: str):
        self.kind = kind
        super().__init__("ledger unavailable" if kind == "ledger" else "runtime telemetry unavailable")


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
        for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
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
    """Read only the Codex counters; never select prompt or response columns."""
    path = Path(db_path).expanduser()
    if not reviewer_prefix or not path.is_file():
        raise TokenBudgetError("telemetry")
    db: sqlite3.Connection | None = None
    try:
        db = sqlite3.connect(path.as_posix())
        db.execute("PRAGMA query_only = ON")
        columns = {row[1] for row in db.execute("PRAGMA table_info(threads)")}
        required = {"id", "rollout_path", "tokens_used", "agent_path"}
        if not required.issubset(columns):
            raise TokenBudgetError("telemetry")
        prefix = reviewer_prefix.rstrip("/")
        rows = db.execute("SELECT id, rollout_path, tokens_used, agent_path FROM threads")
        result: dict[str, dict[str, int | None]] = {}
        for thread_id, rollout_path, tokens_used, agent_path in rows:
            if not isinstance(thread_id, str):
                raise TokenBudgetError("telemetry")
            if not isinstance(agent_path, str) or not (agent_path == prefix or agent_path.startswith(prefix + "/")):
                continue
            total = _safe_count(tokens_used)
            if total is None:
                raise TokenBudgetError("telemetry")
            result[thread_id] = {"total_tokens": total, **_rollout_usage(rollout_path)}
        return result
    except TokenBudgetError:
        raise
    except (OSError, sqlite3.Error):
        raise TokenBudgetError("telemetry") from None
    finally:
        if db is not None:
            db.close()


def _delta(current: int, baseline: int) -> int:
    value = current - baseline
    if value < 0:
        raise TokenBudgetError("telemetry")
    return value


def _detail_delta(current: int | None, baseline: int | None) -> int | None:
    if current is None:
        return None
    return _delta(current, baseline) if baseline is not None else current


def delta_usage(baseline: dict[str, dict[str, int | None]], snapshot: dict[str, dict[str, int | None]]) -> dict[str, int | None]:
    if not set(baseline).issubset(snapshot):
        raise TokenBudgetError("telemetry")
    rows: list[dict[str, int | None]] = []
    for thread_id, current in snapshot.items():
        previous = baseline.get(thread_id, _empty_usage())
        rows.append(
            {
                "total_tokens": _delta(int(current["total_tokens"]), int(previous["total_tokens"])),
                **{
                    field: _detail_delta(current[field], previous[field])
                    for field in USAGE_FIELDS
                },
            }
        )
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
        "reviewer_prefix": str(options["reviewer_prefix"]),
    }


def start_ledger(path: str | Path, db_path: str | Path, reviewer_prefix: str, budget: int = DEFAULT_BUDGET_TOKENS, **options) -> dict:
    state_path = Path(path).expanduser()
    if state_path.exists():
        ledger = read_ledger(state_path)
        if ledger["budget_tokens"] != budget or ledger["runtime_db"] != str(Path(db_path).expanduser().resolve()) or ledger["scope"]["reviewer_prefix"] != reviewer_prefix:
            raise TokenBudgetError("ledger")
        for key in ("round", "base", "head", "selected_files", "carried_files", "jobs", "model", "reasoning"):
            if key in options:
                ledger_key = "reasoning_effort" if key == "reasoning" else ("selected_files" if key == "selected_files" else key)
                if ledger["scope"].get(ledger_key) != options[key]:
                    raise TokenBudgetError("ledger")
        if ledger["status"] != "running":
            return ledger
        return validate_ledger_telemetry(state_path)
    if not isinstance(budget, int) or isinstance(budget, bool) or budget <= 0:
        raise TokenBudgetError("ledger")
    snapshot = read_telemetry(db_path, reviewer_prefix)
    ledger = {
        "schema_version": 1,
        "kind": "review_token_ledger",
        "started_at": _now(),
        "runtime_db": str(Path(db_path).expanduser().resolve()),
        "budget_tokens": budget,
        "scope": _scope({**options, "reviewer_prefix": reviewer_prefix}),
        "baseline_by_thread": snapshot,
        "reviewer_thread_count": len(snapshot),
        "checkpoints": [],
        "usage": _empty_usage(),
        "status": "running",
    }
    _write_json(state_path, ledger)
    return ledger


def _valid_ledger(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    expected = {"schema_version", "kind", "started_at", "finalized_at", "runtime_db", "budget_tokens", "scope", "baseline_by_thread", "reviewer_thread_count", "checkpoints", "usage", "status"}
    if set(value) - expected or not {"schema_version", "kind", "started_at", "runtime_db", "budget_tokens", "scope", "baseline_by_thread", "reviewer_thread_count", "checkpoints", "usage", "status"}.issubset(value):
        return False
    if value["schema_version"] != 1 or value["kind"] != "review_token_ledger" or not _timestamp(value["started_at"]):
        return False
    if "finalized_at" in value and value["finalized_at"] is not None and not _timestamp(value["finalized_at"]):
        return False
    if not isinstance(value["runtime_db"], str) or not value["runtime_db"] or not isinstance(value["budget_tokens"], int) or value["budget_tokens"] <= 0:
        return False
    scope = value["scope"]
    required_scope = {"repository", "round", "base", "head", "selected_files", "carried_files", "jobs", "model", "reasoning_effort", "reviewer_prefix"}
    if not isinstance(scope, dict) or set(scope) != required_scope or not all(isinstance(scope[key], str) and bool(scope[key]) for key in ("repository", "base", "head", "model", "reasoning_effort", "reviewer_prefix")) or not all(isinstance(scope[key], int) and scope[key] >= 0 for key in ("round", "selected_files", "carried_files", "jobs")):
        return False
    if not isinstance(value["baseline_by_thread"], dict) or not all(_usage(row) for row in value["baseline_by_thread"].values()):
        return False
    if not isinstance(value["reviewer_thread_count"], int) or value["reviewer_thread_count"] < 0 or not isinstance(value["checkpoints"], list) or not all(_valid_checkpoint(row) for row in value["checkpoints"]):
        return False
    if not _usage(value["usage"]) or value["status"] not in {"running", "complete", "budget_exhausted"}:
        return False
    if value["status"] == "running" and value.get("finalized_at") is not None:
        return False
    if value["status"] == "complete" and value.get("finalized_at") is None:
        return False
    if value["status"] == "budget_exhausted" and value["usage"]["total_tokens"] < value["budget_tokens"]:
        return False
    if value["status"] in {"running", "complete"} and value["usage"]["total_tokens"] >= value["budget_tokens"]:
        return False
    checkpoints = value["checkpoints"]
    if value["status"] != "budget_exhausted" and checkpoints and checkpoints[-1]["usage"] != value["usage"]:
        return False
    if not all(checkpoints[index]["usage"]["total_tokens"] <= checkpoints[index + 1]["usage"]["total_tokens"] for index in range(len(checkpoints) - 1)):
        return False
    return all(
        checkpoint["status"] == "running"
        or (index == len(checkpoints) - 1 and checkpoint["status"] == "budget_exhausted")
        for index, checkpoint in enumerate(checkpoints)
    )


def _valid_checkpoint(value: object) -> bool:
    return isinstance(value, dict) and set(value) == {"job", "recorded_at", "usage", "status"} and isinstance(value["job"], str) and bool(value["job"]) and _timestamp(value["recorded_at"]) and _usage(value["usage"]) and value["status"] in {"running", "budget_exhausted"}


def read_ledger(path: str | Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise TokenBudgetError("ledger") from None
    if not _valid_ledger(value):
        raise TokenBudgetError("ledger")
    return value


def checkpoint_ledger(path: str | Path, job: str) -> dict:
    ledger = read_ledger(path)
    if ledger["status"] != "running" or not job:
        raise TokenBudgetError("ledger")
    snapshot = read_telemetry(ledger["runtime_db"], ledger["scope"]["reviewer_prefix"])
    usage = delta_usage(ledger["baseline_by_thread"], snapshot)
    if usage["total_tokens"] < ledger["usage"]["total_tokens"]:
        raise TokenBudgetError("telemetry")
    status = "budget_exhausted" if usage["total_tokens"] >= ledger["budget_tokens"] else "running"
    next_ledger = {
        **ledger,
        "reviewer_thread_count": len(snapshot),
        "checkpoints": [*ledger["checkpoints"], {"job": job, "recorded_at": _now(), "usage": usage, "status": status}],
        "usage": usage,
        "status": status,
    }
    _write_json(Path(path), next_ledger)
    return next_ledger


def validate_ledger_telemetry(path: str | Path) -> dict:
    """Validate fresh state and persist a cap decision before starting work."""
    ledger = read_ledger(path)
    if ledger["status"] != "running":
        return ledger
    snapshot = read_telemetry(ledger["runtime_db"], ledger["scope"]["reviewer_prefix"])
    usage = delta_usage(ledger["baseline_by_thread"], snapshot)
    if usage["total_tokens"] < ledger["usage"]["total_tokens"]:
        raise TokenBudgetError("telemetry")
    if usage["total_tokens"] >= ledger["budget_tokens"]:
        ledger = {
            **ledger,
            "reviewer_thread_count": len(snapshot),
            "usage": usage,
            "status": "budget_exhausted",
        }
        _write_json(Path(path), ledger)
        return ledger
    return ledger


def finalize_ledger(path: str | Path) -> dict:
    ledger = read_ledger(path)
    if ledger["status"] != "running":
        raise TokenBudgetError("ledger")
    snapshot = read_telemetry(ledger["runtime_db"], ledger["scope"]["reviewer_prefix"])
    usage = delta_usage(ledger["baseline_by_thread"], snapshot)
    if usage["total_tokens"] < ledger["usage"]["total_tokens"]:
        raise TokenBudgetError("telemetry")
    next_ledger = {**ledger, "finalized_at": _now(), "reviewer_thread_count": len(snapshot), "usage": usage, "status": "budget_exhausted" if usage["total_tokens"] >= ledger["budget_tokens"] else "complete"}
    _write_json(Path(path), next_ledger)
    return next_ledger


def write_unmetered_fallback(path: str | Path, reason: str = "compatible telemetry unavailable") -> None:
    _write_json(Path(path), {"schema_version": 1, "kind": "review_token_fallback", "started_at": _now(), "finalized_at": _now(), "status": "unmetered", "reason": reason})
