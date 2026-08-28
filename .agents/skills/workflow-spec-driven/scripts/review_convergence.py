#!/usr/bin/env python3
"""Persist blocker fingerprints and their failed-verifier convergence counts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def fingerprint(requirement: str, root_cause: str, failure_path: str) -> str:
    material = "\0".join(_normalize(value) for value in (requirement, root_cause, failure_path))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def state_path(root: Path, feature: str) -> Path:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", feature):
        raise ValueError("invalid feature")
    resolved_root = Path(root).resolve()
    feature_dir = (resolved_root / ".specs" / "features" / feature).resolve()
    try:
        feature_dir.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("feature path escapes root") from exc
    return feature_dir / "review-fingerprints.json"


def _load(path: Path, feature: str) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "feature": feature, "fingerprints": {}}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("version") != 1 or payload.get("feature") != feature or not isinstance(payload.get("fingerprints"), dict):
        raise ValueError("invalid convergence state")
    return payload


def _save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def record_result(
    root: Path,
    feature: str,
    requirement: str,
    root_cause: str,
    failure_path: str,
    *,
    verifier_failed: bool,
    gate_passed: bool,
    previous_fingerprint: str | None = None,
) -> dict[str, Any]:
    path = state_path(root, feature)
    state = _load(path, feature)
    key = previous_fingerprint or fingerprint(requirement, root_cause, failure_path)
    current = state["fingerprints"].get(key)
    if previous_fingerprint is not None and current is None:
        raise ValueError("unknown previous fingerprint")
    if current is not None and _normalize(str(current.get("requirement", ""))) != _normalize(requirement):
        raise ValueError("previous fingerprint requirement mismatch")
    if current is None:
        current = {
            "fingerprint": key,
            "requirement": _normalize(requirement),
            "root_cause": _normalize(root_cause),
            "failure_path": _normalize(failure_path),
            "failed_remediations": 0,
            "status": "open",
        }
    elif previous_fingerprint is not None:
        current.update({"requirement": _normalize(requirement), "root_cause": _normalize(root_cause), "failure_path": _normalize(failure_path)})
    if verifier_failed:
        if current["status"] != "halted":
            current["failed_remediations"] += 1
            current["status"] = "open"
            if current["failed_remediations"] >= 3:
                current["status"] = "halted"
    elif gate_passed and previous_fingerprint is not None and current["status"] == "open":
        current["status"] = "closed"
    state["fingerprints"][key] = current
    _save(path, state)
    return dict(current)


def record_failure(
    root: Path,
    feature: str,
    requirement: str,
    root_cause: str,
    failure_path: str,
    *,
    gate_passed: bool = False,
    previous_fingerprint: str | None = None,
) -> dict[str, Any]:
    return record_result(
        root,
        feature,
        requirement,
        root_cause,
        failure_path,
        verifier_failed=True,
        gate_passed=gate_passed,
        previous_fingerprint=previous_fingerprint,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--feature", required=True)
    parser.add_argument("--requirement", required=True)
    parser.add_argument("--root-cause", required=True)
    parser.add_argument("--failure-path", required=True)
    parser.add_argument("--previous-fingerprint")
    parser.add_argument("--verifier-failed", action="store_true")
    parser.add_argument("--gate-passed", action="store_true")
    args = parser.parse_args(argv)
    result = record_result(
        args.root,
        args.feature,
        args.requirement,
        args.root_cause,
        args.failure_path,
        verifier_failed=args.verifier_failed,
        gate_passed=args.gate_passed,
        previous_fingerprint=args.previous_fingerprint,
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
