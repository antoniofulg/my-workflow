#!/usr/bin/env python3
"""Small, redacted host-health evidence provider for assisted lane admission."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Callable, Mapping


SCHEMA_VERSION = 1
DEFAULT_MAX_AGE_SECONDS = 30.0
STATUSES = {"healthy", "pressured", "unknown"}


def _status(value: Any) -> str:
    return value if isinstance(value, str) and value in STATUSES else "unknown"


def _invalid() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "observed_at_monotonic": 0.0,
        "cpu": "unknown",
        "memory": "unknown",
        "disk": "unknown",
        "heavy_gates_active": 0,
        "admit_one": False,
    }


def normalize_health(
    evidence: Mapping[str, Any] | None,
    *,
    now_monotonic: float | None = None,
    max_age_seconds: float = DEFAULT_MAX_AGE_SECONDS,
) -> dict[str, Any]:
    """Return only bounded enums/counts from host evidence.

    Invalid, missing, future, and stale observations are deliberately converted to a
    non-admitting normalized record.  No input value is copied into the result.
    """
    result = _invalid()
    if not isinstance(evidence, Mapping):
        return result
    observed = evidence.get("observed_at_monotonic")
    now = time.monotonic() if now_monotonic is None else now_monotonic
    if (
        type(observed) is not float and type(observed) is not int
        or type(now) not in (int, float)
        or type(max_age_seconds) not in (int, float)
        or max_age_seconds <= 0
        or observed < 0
        or not math.isfinite(float(observed))
        or not math.isfinite(float(now))
        or not math.isfinite(float(max_age_seconds))
        or now < observed
        or now - observed > max_age_seconds
        or evidence.get("schema_version") != SCHEMA_VERSION
        or any(key not in evidence for key in ("cpu", "memory", "disk", "heavy_gates_active"))
    ):
        return result
    cpu, memory, disk = (_status(evidence.get(key)) for key in ("cpu", "memory", "disk"))
    heavy = evidence.get("heavy_gates_active")
    if type(heavy) is not int or heavy < 0 or any(value == "unknown" for value in (cpu, memory, disk)):
        return result
    result.update(
        observed_at_monotonic=float(observed),
        cpu=cpu,
        memory=memory,
        disk=disk,
        heavy_gates_active=heavy,
    )
    result["admit_one"] = all(value == "healthy" for value in (cpu, memory, disk))
    return result


def should_admit_lane(
    active_writers: int,
    configured_cap: str | int,
    evidence: Mapping[str, Any] | None,
    *,
    automatic_ceiling: int = 4,
    now_monotonic: float | None = None,
) -> bool:
    """Decide whether exactly one more writer may be admitted.

    The cap is an input, never raised by this helper.  Health is required only above
    the safe two-writer baseline; callers still choose the initial two lanes.
    """
    if type(active_writers) is not int or active_writers < 0:
        return False
    cap = automatic_ceiling if configured_cap == "auto" else configured_cap
    if type(cap) is not int or cap < 1 or active_writers >= cap:
        return False
    if active_writers < 2:
        return True
    normalized = normalize_health(evidence, now_monotonic=now_monotonic)
    return normalized["admit_one"] is True


def _platform_cpu() -> str:
    try:
        load = os.getloadavg()[0]
        cores = os.cpu_count() or 1
        return "healthy" if load <= cores * 1.5 else "pressured"
    except (AttributeError, OSError, TypeError, IndexError):
        return "unknown"


def _platform_memory() -> str:
    # POSIX sysconf is stdlib-only and intentionally emits no sizes or paths.
    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        total = os.sysconf("SC_PHYS_PAGES")
        available = os.sysconf("SC_AVPHYS_PAGES")
        if not all(type(value) is int and value > 0 for value in (page_size, total)):
            return "unknown"
        if type(available) is not int or available < 0:
            return "unknown"
        return "healthy" if available / total >= 0.10 else "pressured"
    except (AttributeError, OSError, TypeError, ValueError):
        return "unknown"


def _platform_disk(root: Path) -> str:
    try:
        usage = shutil.disk_usage(root)
        return "healthy" if usage.total > 0 and usage.free / usage.total >= 0.10 else "pressured"
    except (OSError, ValueError):
        return "unknown"


def collect_health(
    root: Path | str = ".",
    *,
    now_monotonic: float | None = None,
    cpu_reader: Callable[[], str] = _platform_cpu,
    memory_reader: Callable[[], str] = _platform_memory,
    disk_reader: Callable[[Path], str] = _platform_disk,
    heavy_gates_active: int = 0,
) -> dict[str, Any]:
    """Collect platform signals through bounded readers and normalize their result."""
    now = time.monotonic() if now_monotonic is None else now_monotonic
    try:
        raw = {
            "schema_version": SCHEMA_VERSION,
            "observed_at_monotonic": now,
            "cpu": cpu_reader(),
            "memory": memory_reader(),
            "disk": disk_reader(Path(root)),
            "heavy_gates_active": heavy_gates_active,
        }
    except Exception:
        return _invalid()
    return normalize_health(raw, now_monotonic=now)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--active-writers", type=int, default=2)
    parser.add_argument("--max-workers", default="auto")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        evidence = collect_health(args.root)
        result = {**evidence, "admit_next": should_admit_lane(args.active_writers, args.max_workers, evidence)}
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ValueError) as exc:
        print(f"machine health: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
