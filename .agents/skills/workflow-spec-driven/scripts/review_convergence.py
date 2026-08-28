#!/usr/bin/env python3
"""Persist immutable blocker fingerprints and append-only audit generations."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

MAX_FAILURES = 3
GENERATION_STATUSES = {"open", "halted", "closed"}


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


def _halt_event(generation: int, failures: int) -> dict[str, Any]:
    return {"generation": generation, "failed_remediations": failures, "status": "halted"}


def _generation(number: int, failures: int, status: str, **extra: Any) -> dict[str, Any]:
    value: dict[str, Any] = {"generation": number, "failed_remediations": failures, "status": status}
    value.update(extra)
    if status == "halted":
        value.setdefault("halt_event", _halt_event(number, failures))
    return value


def _legacy_generation(entry: dict[str, Any]) -> dict[str, Any]:
    failures = entry.get("failed_remediations")
    status = entry.get("status")
    if not isinstance(failures, int) or failures < 0 or status not in GENERATION_STATUSES:
        raise ValueError("invalid convergence entry")
    if status == "halted" and failures < MAX_FAILURES:
        raise ValueError("halted convergence entry has too few failures")
    return _generation(1, failures, status)


def _valid_authorization(reference: str) -> bool:
    return bool(
        reference and reference == reference.strip() and reference.startswith(".specs/")
        and "#" in reference and ".." not in reference and "\\" not in reference
        and not Path(reference).is_absolute()
    )


def _validate_generation(generation: Any, expected_number: int) -> dict[str, Any]:
    if not isinstance(generation, dict) or generation.get("generation") != expected_number:
        raise ValueError("non-contiguous audit generations")
    failures = generation.get("failed_remediations")
    status = generation.get("status")
    if not isinstance(failures, int) or failures < 0 or status not in GENERATION_STATUSES:
        raise ValueError("invalid audit generation")
    if status == "halted":
        event = generation.get("halt_event")
        if not isinstance(event, dict) or event != _halt_event(expected_number, failures):
            raise ValueError("invalid halt event")
    elif "halt_event" in generation:
        raise ValueError("halt event on non-halted generation")
    if "authorization_ref" in generation and (
        not isinstance(generation["authorization_ref"], str)
        or not _valid_authorization(generation["authorization_ref"])
    ):
        raise ValueError("invalid authorization reference")
    return generation


def _normalize_entry(key: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("fingerprint") != key:
        raise ValueError("invalid convergence entry")
    required = ("requirement", "root_cause", "failure_path")
    if any(not isinstance(value.get(field), str) or not value[field].strip() for field in required):
        raise ValueError("invalid convergence entry")
    normalized = dict(value)
    for field in required:
        normalized[field] = _normalize(normalized[field])
    generations = normalized.get("generations")
    if generations is None:
        generations = [_legacy_generation(normalized)]
    elif not isinstance(generations, list) or not generations:
        raise ValueError("invalid audit generations")
    generations = [_validate_generation(item, index) for index, item in enumerate(generations, 1)]
    current_generation = normalized.get("current_generation", len(generations))
    if current_generation != len(generations):
        raise ValueError("invalid current generation")
    cumulative = sum(item["failed_remediations"] for item in generations)
    if normalized.get("failed_remediations") != cumulative:
        raise ValueError("inconsistent cumulative failures")
    if normalized.get("status") != generations[-1]["status"]:
        raise ValueError("inconsistent convergence status")
    if any(item["status"] == "closed" for item in generations[:-1]):
        raise ValueError("closed audit generation cannot be resumed")
    normalized.update({"current_generation": current_generation, "generations": generations})
    return normalized


def _load(path: Path, feature: str) -> dict[str, Any]:
    if not path.exists():
        return {"version": 2, "feature": feature, "fingerprints": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("invalid convergence state") from exc
    if payload.get("version") not in {1, 2} or payload.get("feature") != feature or not isinstance(payload.get("fingerprints"), dict):
        raise ValueError("invalid convergence state")
    return {
        "version": 2,
        "feature": feature,
        "fingerprints": {key: _normalize_entry(key, value) for key, value in payload["fingerprints"].items()},
    }


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


def _entry_key(state: dict[str, Any], requirement: str, root_cause: str, failure_path: str, previous_fingerprint: str | None) -> str:
    key = previous_fingerprint or fingerprint(requirement, root_cause, failure_path)
    current = state["fingerprints"].get(key)
    if previous_fingerprint is not None and current is None:
        raise ValueError("unknown previous fingerprint")
    if current is not None and _normalize(str(current.get("requirement", ""))) != _normalize(requirement):
        raise ValueError("previous fingerprint requirement mismatch")
    if previous_fingerprint is None and any(
        item.get("status") == "halted" and item.get("requirement") == _normalize(requirement)
        for item in state["fingerprints"].values()
    ):
        raise ValueError("halted fingerprint requires authorized resume")
    return key


def record_result(
    root: Path, feature: str, requirement: str, root_cause: str, failure_path: str, *,
    verifier_failed: bool, gate_passed: bool, previous_fingerprint: str | None = None,
    independent: bool = False, evidence_ref: str | None = None,
) -> dict[str, Any]:
    path = state_path(root, feature)
    state = _load(path, feature)
    key = _entry_key(state, requirement, root_cause, failure_path, previous_fingerprint)
    current = state["fingerprints"].get(key)
    if current is None:
        current = {
            "fingerprint": key, "requirement": _normalize(requirement),
            "root_cause": _normalize(root_cause), "failure_path": _normalize(failure_path),
            "failed_remediations": 0, "status": "open", "current_generation": 1,
            "generations": [_generation(1, 0, "open")],
        }
    else:
        current = deepcopy(current)
        if previous_fingerprint is not None and current["status"] == "halted":
            if _normalize(root_cause) != current["root_cause"] or _normalize(failure_path) != current["failure_path"]:
                raise ValueError("halted fingerprint identity cannot be reworded")
        elif previous_fingerprint is not None:
            current.update({"requirement": _normalize(requirement), "root_cause": _normalize(root_cause), "failure_path": _normalize(failure_path)})
    generation = current["generations"][-1]
    if verifier_failed:
        if current["status"] == "halted":
            raise ValueError("halted fingerprint requires authorized resume")
        generation["failed_remediations"] += 1
        generation["status"] = "halted" if generation["failed_remediations"] >= MAX_FAILURES else "open"
        if generation["status"] == "halted":
            generation["halt_event"] = _halt_event(generation["generation"], generation["failed_remediations"])
    elif gate_passed and previous_fingerprint is not None and current["status"] == "open":
        qualifies = independent and bool(evidence_ref) and _valid_authorization(evidence_ref)
        if current["current_generation"] == 1 or qualifies:
            if current["current_generation"] > 1:
                generation["evidence_ref"] = evidence_ref
            generation["status"] = "closed"
            generation.pop("halt_event", None)
    current["failed_remediations"] = sum(item["failed_remediations"] for item in current["generations"])
    current["status"] = current["generations"][-1]["status"]
    state["fingerprints"][key] = current
    _save(path, state)
    return deepcopy(current)


def record_failure(root: Path, feature: str, requirement: str, root_cause: str, failure_path: str, *, gate_passed: bool = False, previous_fingerprint: str | None = None) -> dict[str, Any]:
    return record_result(root, feature, requirement, root_cause, failure_path, verifier_failed=True, gate_passed=gate_passed, previous_fingerprint=previous_fingerprint)


def resume(root: Path, feature: str, resume_fingerprint: str, authorization_ref: str) -> dict[str, Any]:
    """Append an authorized generation without mutating the halted history."""
    path = state_path(root, feature)
    state = _load(path, feature)
    if not re.fullmatch(r"[0-9a-f]{64}", resume_fingerprint):
        raise ValueError("invalid resume fingerprint")
    if not _valid_authorization(authorization_ref):
        raise ValueError("invalid authorization reference")
    current = state["fingerprints"].get(resume_fingerprint)
    if current is None:
        raise ValueError("unknown resume fingerprint")
    if current["status"] != "halted" or current["generations"][-1]["status"] != "halted":
        raise ValueError("resume requires halted fingerprint")
    updated = deepcopy(current)
    generation = _generation(current["current_generation"] + 1, 0, "open", authorization_ref=authorization_ref)
    updated["generations"].append(generation)
    updated["current_generation"] = generation["generation"]
    updated["status"] = "open"
    updated["failed_remediations"] = sum(item["failed_remediations"] for item in updated["generations"])
    state["fingerprints"][resume_fingerprint] = updated
    _save(path, state)
    return deepcopy(updated)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--feature", required=True)
    parser.add_argument("--requirement")
    parser.add_argument("--root-cause")
    parser.add_argument("--failure-path")
    parser.add_argument("--previous-fingerprint")
    parser.add_argument("--resume-fingerprint")
    parser.add_argument("--authorization-ref")
    parser.add_argument("--verifier-failed", action="store_true")
    parser.add_argument("--gate-passed", action="store_true")
    parser.add_argument("--independent", action="store_true")
    parser.add_argument("--evidence-ref")
    args = parser.parse_args(argv)
    if args.resume_fingerprint is not None:
        if args.authorization_ref is None:
            raise SystemExit("--authorization-ref is required with --resume-fingerprint")
        result = resume(args.root, args.feature, args.resume_fingerprint, args.authorization_ref)
    else:
        if any(value is None for value in (args.requirement, args.root_cause, args.failure_path)):
            raise SystemExit("--requirement, --root-cause, and --failure-path are required")
        result = record_result(args.root, args.feature, args.requirement, args.root_cause, args.failure_path, verifier_failed=args.verifier_failed, gate_passed=args.gate_passed, previous_fingerprint=args.previous_fingerprint, independent=args.independent, evidence_ref=args.evidence_ref)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
