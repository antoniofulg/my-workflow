#!/usr/bin/env python3
"""Create and validate the disposable, real-interface E2E-001 pilot fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


FEATURE = "parallel-pilot"
MARKER = ".parallel-slice-qa-fixture"
OWNERSHIP = ".parallel-slice-qa-ownership.json"
PREFIX = "parallel-slice-pilot-"
ROOT = Path(__file__).resolve().parent.parent
OWNED_WORKTREES = ("parallel-pilot/A-T1", "parallel-pilot/B-T2")
EXPECTED_LANES = ("slice-A", "slice-B")
LIFECYCLE_VERSION = 1


def git(root: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def _owner() -> tuple[Path, Path, str]:
    owner = Path(git(ROOT, "rev-parse", "--show-toplevel")).resolve()
    common_value = git(owner, "rev-parse", "--git-common-dir")
    common = (owner / common_value if not Path(common_value).is_absolute() else Path(common_value)).resolve()
    return owner, common, git(owner, "rev-parse", "HEAD")


def _gitdir(worktree: Path) -> str:
    value = git(worktree, "rev-parse", "--git-dir")
    return str((worktree / value if not Path(value).is_absolute() else Path(value)).resolve())


def _worktree_root(root: Path, common_dir: Path | None = None) -> Path:
    if common_dir is None:
        value = git(root, "rev-parse", "--git-common-dir")
        common_dir = (root / value if not Path(value).is_absolute() else Path(value)).resolve()
    return common_dir.parent.parent / f".{root.name}-parallel-slices"


def setup() -> dict[str, str]:
    root = Path(tempfile.mkdtemp(prefix="parallel-slice-pilot-")).resolve()
    shutil.rmtree(root)
    owner, common, owner_head = _owner()
    try:
        git(owner, "worktree", "add", "--detach", str(root), owner_head)
        feature_dir = root / ".specs" / "features" / FEATURE
        feature_dir.mkdir(parents=True)
        (feature_dir / "tasks.md").write_text(
            "## Vertical Slice Closure\n\n| Slice | Observable outcome | Independent gate | Merge if later slices are cancelled? | Why |\n| --- | --- | --- | --- | --- |\n| A | Capability A. | `gate-a` | yes | Independent value. |\n| B | Capability B. | `gate-b` | yes | Independent value. |\n\n## Task Breakdown\n\n"
            "### T1: pilot A\n**Status:** pending\n**Slice:** A\n**Where:** src/a.py\n**Depends on:** None\n**Resources:** none\n\n"
            "### T2: pilot B\n**Status:** pending\n**Slice:** B\n**Where:** src/b.py\n**Depends on:** None\n**Resources:** none\n",
            encoding="utf-8",
        )
        agents = root / ".codex" / "agents"
        agents.mkdir(parents=True)
        for name, model, effort in (
            ("implementer", "gpt-5.6-luna", "high"),
            ("verifier", "gpt-5.6-sol", "medium"),
            ("explorer", "gpt-5.6-luna", "medium"),
            ("deep-reviewer", "gpt-5.6-luna", "high"),
        ):
            (agents / f"{name}.toml").write_text(
                f'name = "{name}"\nmodel = "{model}"\nmodel_reasoning_effort = "{effort}"\n'
                'developer_instructions = "QA fixture"\n',
                encoding="utf-8",
            )
        git(root, "add", "-f", str(feature_dir / "tasks.md"), str(agents))
        git(root, "commit", "-qm", "qa fixture plan")
        head = git(root, "rev-parse", "HEAD")
        (feature_dir / "workflow.json").write_text(
            json.dumps(
                {
                    "version": 3,
                    "feature": FEATURE,
                    "git_head": head,
                    "profile": None,
                    "overrides": {},
                    "deep_review": {"cadence": "grouped.3", "groups": [[1, 2]]},
                    "parallelization": {
                        "mode": "assisted",
                        "max_workers": "auto",
                        "automatic_baseline": 2,
                        "automatic_ceiling": 4,
                        "resource_provider": None,
                    },
                    "roles": {
                        "implementer": {
                            "provider": "codex", "agent_file": ".codex/agents/implementer.toml",
                            "model": "gpt-5.6-luna", "effort": "high",
                        },
                        "verifier": {
                            "provider": "codex", "agent_file": ".codex/agents/verifier.toml",
                            "model": "gpt-5.6-sol", "effort": "medium",
                        },
                        "explorer": {
                            "provider": "codex", "agent_file": ".codex/agents/explorer.toml",
                            "model": "gpt-5.6-luna", "effort": "medium",
                        },
                        "deep_reviewer": {
                            "provider": "codex", "agent_file": ".codex/agents/deep-reviewer.toml",
                            "model": "gpt-5.6-luna", "effort": "high",
                        },
                    },
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (root / MARKER).write_text("disposable QA fixture\n", encoding="utf-8")
        (root / OWNERSHIP).write_text(
            json.dumps(
                {
                    "root": str(root), "feature": FEATURE, "source_git_head": head,
                    "owner_root": str(owner), "owner_common_dir": str(common),
                    "source_worktree": str(root), "source_worktree_id": _gitdir(root),
                    "worktrees": list(OWNED_WORKTREES),
                },
                sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )
        return {"root": str(root), "feature": FEATURE, "status": "created"}
    except Exception:
        subprocess.run(["git", "worktree", "remove", "--force", str(root)], cwd=owner, check=False, capture_output=True)
        shutil.rmtree(root, ignore_errors=True)
        raise


def _validate_root(value: str) -> Path:
    root = Path(value).resolve()
    temporary_root = Path(tempfile.gettempdir()).resolve()
    if temporary_root not in root.parents or not root.name.startswith(PREFIX):
        raise ValueError("pilot root is outside the disposable fixture boundary")
    if not root.is_dir() or not (root / MARKER).is_file() or not (root / OWNERSHIP).is_file() or not (root / ".specs/features" / FEATURE / "workflow.json").is_file():
        raise ValueError("not a parallel pilot fixture")
    ownership = json.loads((root / OWNERSHIP).read_text(encoding="utf-8"))
    owner, common, _ = _owner()
    if (
        ownership.get("root") != str(root)
        or ownership.get("feature") != FEATURE
        or ownership.get("worktrees") != list(OWNED_WORKTREES)
        or ownership.get("owner_root") != str(owner)
        or ownership.get("owner_common_dir") != str(common)
        or ownership.get("source_worktree") != str(root)
        or not isinstance(ownership.get("source_worktree_id"), str)
    ):
        raise ValueError("pilot ownership attestation is invalid")
    return root


def _validate_fixture(value: str) -> tuple[Path, dict[str, object], dict[str, object], str]:
    root = _validate_root(value)
    ownership = json.loads((root / OWNERSHIP).read_text(encoding="utf-8"))
    snapshot_path = root / ".specs/features" / FEATURE / "workflow.json"
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    repository_head = git(root, "rev-parse", "HEAD")
    if snapshot.get("feature") != FEATURE or snapshot.get("git_head") != repository_head:
        raise ValueError("pilot frozen workflow source HEAD does not match repository HEAD")
    if ownership.get("source_git_head") != repository_head:
        raise ValueError("pilot ownership source HEAD does not match repository HEAD")
    if _gitdir(root) != ownership.get("source_worktree_id"):
        raise ValueError("pilot source worktree identity does not match ownership attestation")
    return root, ownership, snapshot, repository_head


def _residual_paths(worktree_root: Path) -> list[str]:
    if not worktree_root.exists():
        return []
    paths: list[str] = []
    for current, directories, files in os.walk(worktree_root, followlinks=False):
        current_path = Path(current)
        paths.extend(str(current_path / name) for name in sorted(directories + files))
    return sorted(paths)


def lifecycle_complete(status: dict[str, object]) -> bool:
    state = status.get("state")
    if not isinstance(state, dict) or set(state.get("lanes", {})) != set(EXPECTED_LANES):
        return False
    lanes = state["lanes"]
    actions = state.get("actions")
    if not isinstance(lanes, dict) or not isinstance(actions, dict):
        return False
    for lane_id in EXPECTED_LANES:
        lane = lanes.get(lane_id)
        if not isinstance(lane, dict) or lane.get("state") != "complete":
            return False
        if lane.get("lifecycle_events") != ["worker_done", "worker_read", "worker_ack", "worker_release"]:
            return False
        lane_actions = [action for action in actions.values() if isinstance(action, dict) and action.get("lane") == lane_id]
        worker = next((action for action in lane_actions if action.get("action") == "worker"), None)
        ack = next((action for action in lane_actions if action.get("action") == "worker_ack"), None)
        release = next((action for action in lane_actions if action.get("action") == "worker_release"), None)
        if not all(isinstance(action, dict) and action.get("status") in {"accepted", "released"} for action in (worker, ack, release)):
            return False
        completion = worker.get("completion")
        delivery = worker.get("delivery")
        ack_receipt = ack.get("receipt")
        release_receipt = release.get("receipt")
        if not isinstance(completion, dict) or not isinstance(delivery, dict) or delivery.get("event") != "worker_done":
            return False
        if not isinstance(ack_receipt, dict) or ack_receipt.get("acknowledged") is not True or ack_receipt.get("delivery_id") != completion.get("delivery_id"):
            return False
        if not isinstance(release_receipt, dict) or release_receipt.get("released") is not True or release_receipt.get("dispatch_id") != lane.get("dispatch_id"):
            return False
    return True


def _validate_tombstone(root: Path, record: dict[str, object]) -> Path:
    owner, common, _ = _owner()
    if (
        record.get("root") != str(root)
        or record.get("feature") != FEATURE
        or record.get("owner_root") != str(owner)
        or record.get("owner_common_dir") != str(common)
        or record.get("source_worktree") != str(root)
        or not isinstance(record.get("source_worktree_id"), str)
        or record.get("lifecycle_version") != LIFECYCLE_VERSION
        or not isinstance(record.get("lifecycle_digest"), str)
        or not isinstance(record.get("lane_worktree_ids"), dict)
        or set(record.get("lane_worktree_ids", {})) != set(EXPECTED_LANES)
    ):
        raise ValueError("pilot cleanup attestation is invalid")
    if record.get("worktrees") != list(OWNED_WORKTREES):
        raise ValueError("pilot cleanup attestation is invalid")
    if record.get("status") not in ("authorized", "diagnostic-authorized", "cleaned", "cleaned-with-residual", "diagnostic-aborted", "diagnostic-aborted-with-residual"):
        raise ValueError("pilot cleanup attestation is invalid")
    source_git_head = record.get("source_git_head")
    workflow_git_head = record.get("workflow_git_head")
    if not isinstance(source_git_head, str) or source_git_head != workflow_git_head or len(source_git_head) != 40:
        raise ValueError("pilot cleanup attestation source HEAD is invalid")
    worktree_root = _worktree_root(root, Path(str(record["owner_common_dir"])))
    residual_paths = record.get("residual_paths", [])
    if not isinstance(residual_paths, list) or any(not isinstance(path, str) for path in residual_paths):
        raise ValueError("pilot cleanup attestation residuals are invalid")
    for value in residual_paths:
        path = Path(value)
        try:
            path.resolve().relative_to(worktree_root.resolve())
        except ValueError as exc:
            raise ValueError("pilot cleanup attestation residual escapes worktree boundary") from exc
    return worktree_root


def _executor_status(root: Path) -> dict[str, object]:
    # The disposable checkout is created at the frozen source head. Resolve the
    # coordinator from this source tree so an in-flight schema hard cut is
    # exercised by the same reader that owns the fixture contract.
    executor = ROOT / ".agents/skills/autonomous/scripts/parallel_execute.py"
    result = subprocess.run(
        [sys.executable, str(executor), "status", "--root", str(root), "--feature", FEATURE],
        text=True, capture_output=True, check=False,
    )
    if result.returncode != 0:
        raise ValueError("pilot executor status is unavailable")
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise ValueError("pilot executor status is malformed")
    return payload


def _state_digest(status: dict[str, object]) -> str:
    return hashlib.sha256(json.dumps(status.get("state"), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _authorization_record(
    root: Path, ownership: dict[str, object], snapshot: dict[str, object], status: dict[str, object],
    lane_ids: dict[str, str], *, diagnostic: bool = False,
) -> dict[str, object]:
    return {
        "feature": FEATURE,
        "root": str(root),
        "owner_root": str(ownership["owner_root"]),
        "owner_common_dir": str(ownership["owner_common_dir"]),
        "source_worktree": str(root),
        "source_worktree_id": ownership["source_worktree_id"],
        "source_git_head": ownership["source_git_head"],
        "workflow_git_head": snapshot["git_head"],
        "worktrees": list(OWNED_WORKTREES),
        "lane_worktree_ids": lane_ids,
        "lifecycle_version": LIFECYCLE_VERSION,
        "lifecycle_digest": _state_digest(status),
        "status": "diagnostic-authorized" if diagnostic else "authorized",
        "residual_paths": [],
    }


def authorize_lifecycle(root_value: str) -> dict[str, object]:
    root, ownership, snapshot, _ = _validate_fixture(root_value)
    status = _executor_status(root)
    if not lifecycle_complete(status):
        return {"authorized": False, "reason": "lifecycle-incomplete", "root": root_value}
    lane_ids = _lane_worktree_ids(status, _worktree_root(root))
    attestation = root.parent / f".{root.name}.parallel-pilot-cleaned"
    record = _authorization_record(root, ownership, snapshot, status, lane_ids)
    _write_tombstone(attestation, record)
    return {"authorized": True, "lifecycle_version": LIFECYCLE_VERSION, "lifecycle_digest": record["lifecycle_digest"], "root": root_value}


def _reject_symlink_components(root: Path, candidate: Path) -> None:
    anchor = root.absolute()
    if anchor.is_symlink():
        raise ValueError("pilot lane path contains a symlink")
    path = candidate.absolute()
    try:
        relative = path.relative_to(anchor)
    except ValueError as exc:
        raise ValueError("pilot lane path escapes worktree boundary") from exc
    current = anchor
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise ValueError("pilot lane path contains a symlink")


def _registered_worktree_paths(owner: Path) -> set[Path]:
    output = git(owner, "worktree", "list", "--porcelain")
    paths: set[Path] = set()
    for line in output.splitlines():
        if line.startswith("worktree "):
            paths.add(Path(line.removeprefix("worktree ")).absolute())
    return paths


def _attested_worktree_is_gone(owner: Path, path: Path, worktree_id: str) -> bool:
    if path.exists():
        return False
    if path.absolute() in _registered_worktree_paths(owner):
        return False
    return not Path(worktree_id).exists()


def _lane_worktree_ids(
    status: dict[str, object], worktree_root: Path, *, attested: dict[str, str] | None = None,
    owner: Path | None = None, allow_removed: bool = False,
) -> dict[str, str]:
    state = status.get("state")
    lanes = state.get("lanes") if isinstance(state, dict) else None
    if not isinstance(lanes, dict) or set(lanes) != set(EXPECTED_LANES):
        raise ValueError("pilot lifecycle lanes are incomplete")
    result: dict[str, str] = {}
    for lane_id in EXPECTED_LANES:
        lane = lanes.get(lane_id)
        expected_path = worktree_root / OWNED_WORKTREES[EXPECTED_LANES.index(lane_id)]
        if not isinstance(lane, dict) or lane.get("worktree_path") != str(expected_path) or not isinstance(lane.get("worktree_id"), str):
            raise ValueError("pilot lane worktree ownership is incomplete")
        lane_id_value = lane["worktree_id"]
        if attested is not None and attested.get(lane_id) != lane_id_value:
            raise ValueError("pilot lane worktree identity changed")
        _reject_symlink_components(worktree_root, expected_path)
        if expected_path.is_dir() and _gitdir(expected_path) == lane_id_value:
            result[lane_id] = lane_id_value
            continue
        if allow_removed and owner is not None and _attested_worktree_is_gone(owner, expected_path, lane_id_value):
            result[lane_id] = lane_id_value
            continue
        raise ValueError("pilot lane worktree identity is stale")
    return result


def _owned_identities_are_gone(owner: Path, root: Path, worktree_root: Path, lane_ids: dict[str, str], source_id: str) -> bool:
    for lane_id in EXPECTED_LANES:
        path = worktree_root / OWNED_WORKTREES[EXPECTED_LANES.index(lane_id)]
        _reject_symlink_components(worktree_root, path)
        if not _attested_worktree_is_gone(owner, path, lane_ids[lane_id]):
            return False
    if root.exists() or root.absolute() in _registered_worktree_paths(owner) or Path(source_id).exists():
        return False
    return True


def _remove_owned_worktrees(owner: Path, worktree_root: Path, expected_ids: dict[str, str] | None = None) -> list[str]:
    residual: list[str] = []
    for relative in OWNED_WORKTREES:
        worktree = worktree_root / relative
        _reject_symlink_components(worktree_root, worktree)
        if not worktree.exists():
            continue
        if expected_ids is not None:
            lane_id = EXPECTED_LANES[OWNED_WORKTREES.index(relative)]
            if _gitdir(worktree) != expected_ids.get(lane_id):
                raise ValueError("pilot lane worktree identity is stale")
        result = subprocess.run(["git", "worktree", "remove", "--force", str(worktree)], cwd=owner, check=False, capture_output=True)
        if result.returncode != 0 or worktree.exists():
            residual.append(str(worktree))
    return residual


def _prune_empty_worktree_dirs(worktree_root: Path) -> None:
    for entry in (worktree_root / FEATURE, worktree_root):
        if entry.is_dir():
            try:
                entry.rmdir()
            except OSError:
                pass


def _write_tombstone(path: Path, record: dict[str, object]) -> None:
    path.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")


def _accepted_worker_effect(status: dict[str, object]) -> bool:
    state = status.get("state")
    actions = state.get("actions") if isinstance(state, dict) else None
    if not isinstance(actions, dict):
        return False
    for action in actions.values():
        if not isinstance(action, dict) or action.get("action") != "worker":
            continue
        if action.get("status") in {"accepted", "released"}:
            return True
        partial = action.get("partial_effect")
        if isinstance(partial, dict) and any(partial.get(key) for key in ("run_id", "task_id", "dispatch_id")):
            return True
    return False


def dry_run(root_value: str) -> dict[str, object]:
    root, _, snapshot, repository_head = _validate_fixture(root_value)
    planner = ROOT / ".agents/skills/workflow-config/scripts/parallel_plan.py"
    result = subprocess.run(
        ["python3", str(planner), "--root", str(root), "--feature", FEATURE],
        text=True,
        capture_output=True,
        check=True,
    )
    plan = json.loads(result.stdout)
    lanes = plan.get("lanes")
    if plan.get("mode") != "assisted" or plan.get("fallback") is not False or not isinstance(lanes, list) or len(lanes) != 2:
        raise ValueError("pilot fixture must expose exactly two assisted lanes")
    if any(lane.get("status") != "ready" or lane.get("resources") != [] for lane in lanes):
        raise ValueError("pilot fixture lanes must be ready and resource-free")
    return {
        "validated": True,
        "root": str(root),
        "feature": FEATURE,
        "mode": "assisted",
        "source_git_head": snapshot["git_head"],
        "repository_head": repository_head,
        "lanes": lanes,
    }


def cleanup(root_value: str, *, abort_incomplete: bool = False) -> dict[str, object]:
    root = Path(root_value).resolve()
    attestation = root.parent / f".{root.name}.parallel-pilot-cleaned"
    if not root.exists():
        if not attestation.is_file():
            raise ValueError("pilot root is not an attested disposable fixture")
        record = json.loads(attestation.read_text(encoding="utf-8"))
        worktree_root = _validate_tombstone(root, record)
        if record["status"] in {"authorized", "diagnostic-authorized"}:
            owner = Path(str(record["owner_root"])).resolve()
            lane_ids = record.get("lane_worktree_ids")
            if not isinstance(lane_ids, dict) or not all(isinstance(lane_ids.get(lane), str) for lane in EXPECTED_LANES):
                raise ValueError("pilot cleanup authorization is invalid")
            if not _owned_identities_are_gone(owner, root, worktree_root, lane_ids, str(record["source_worktree_id"])):
                raise ValueError("pilot cleanup authorization has unreconciled owned identities")
            _prune_empty_worktree_dirs(worktree_root)
        residual = _residual_paths(worktree_root)
        if residual:
            if record["status"] == "cleaned":
                record["status"] = "cleaned-with-residual"
            record["residual_paths"] = residual
            _write_tombstone(attestation, record)
            return {"cleaned": False, "aborted": record["status"].startswith("diagnostic"), "diagnostic_cleanup": record["status"].startswith("diagnostic"), "idempotent": True, "residual_paths": residual, "root": root_value}
        if record["status"].startswith("diagnostic"):
            return {"cleaned": False, "aborted": True, "diagnostic_cleanup": True, "idempotent": True, "residual_paths": [], "root": root_value}
        record["status"] = "cleaned"
        record["residual_paths"] = []
        _write_tombstone(attestation, record)
        return {"cleaned": True, "idempotent": True, "residual_paths": [], "root": root_value}
    root, ownership, snapshot, _ = _validate_fixture(root_value)
    owner = Path(str(ownership["owner_root"])).resolve()
    worktree_root = _worktree_root(root)
    prior_authorization: dict[str, object] | None = None
    if attestation.is_file():
        prior_authorization = json.loads(attestation.read_text(encoding="utf-8"))
        _validate_tombstone(root, prior_authorization)
        if prior_authorization.get("status") not in {"authorized", "diagnostic-authorized"}:
            raise ValueError("pilot cleanup authorization is stale")
    elif not abort_incomplete:
        return {"cleaned": False, "aborted": False, "diagnostic_cleanup": False, "reason": "cleanup-authorization-missing", "root": root_value}
    status = _executor_status(root)
    lifecycle = lifecycle_complete(status)
    if not lifecycle and not abort_incomplete:
        return {"cleaned": False, "aborted": False, "diagnostic_cleanup": False, "reason": "lifecycle-incomplete", "root": root_value}
    if abort_incomplete and _accepted_worker_effect(status):
        return {"cleaned": False, "aborted": False, "diagnostic_cleanup": True, "reason": "worker-may-be-live", "instruction": "release accepted workers before diagnostic abort", "root": root_value}
    if lifecycle:
        attested_ids = prior_authorization.get("lane_worktree_ids") if isinstance(prior_authorization, dict) else None
        lane_ids = _lane_worktree_ids(
            status, worktree_root,
            attested=attested_ids if isinstance(attested_ids, dict) else None,
            owner=owner,
            allow_removed=prior_authorization is not None and not abort_incomplete,
        )
    else:
        lane_ids = {lane_id: "unverified" for lane_id in EXPECTED_LANES}
    if not abort_incomplete and (prior_authorization is None or prior_authorization.get("lifecycle_digest") != _state_digest(status)):
        raise ValueError("pilot cleanup authorization digest is stale")
    residual: list[str] = []
    record = (
        dict(prior_authorization)
        if prior_authorization is not None and not abort_incomplete
        else _authorization_record(root, ownership, snapshot, status, lane_ids, diagnostic=abort_incomplete)
    )
    record["residual_paths"] = residual
    if abort_incomplete:
        _write_tombstone(attestation, record)
    residual = _remove_owned_worktrees(owner, worktree_root, lane_ids if lifecycle and not abort_incomplete else None)
    _prune_empty_worktree_dirs(worktree_root)
    residual.extend(_residual_paths(worktree_root))
    source_result = subprocess.run(["git", "worktree", "remove", "--force", str(root)], cwd=owner, check=False, capture_output=True)
    if source_result.returncode != 0 or root.exists():
        return {"cleaned": False, "aborted": abort_incomplete, "diagnostic_cleanup": abort_incomplete, "reason": "source-worktree-removal-failed", "residual_paths": residual, "root": root_value}
    record["status"] = ("diagnostic-aborted-with-residual" if abort_incomplete and residual else "diagnostic-aborted" if abort_incomplete else "cleaned-with-residual" if residual else "cleaned")
    record["residual_paths"] = residual
    _write_tombstone(attestation, record)
    return {"cleaned": not residual and not abort_incomplete, "aborted": abort_incomplete, "diagnostic_cleanup": abort_incomplete, "idempotent": False, "residual_paths": residual, "root": root_value}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("setup", "dry-run", "cleanup", "lifecycle-check"))
    parser.add_argument("--root")
    parser.add_argument("--abort-incomplete", action="store_true")
    args = parser.parse_args()
    if args.command == "lifecycle-check":
        if args.root:
            result = authorize_lifecycle(args.root)
            print(json.dumps(result, sort_keys=True))
            return 0 if result["authorized"] else 1
        result = {"complete": lifecycle_complete(json.load(sys.stdin))}
        print(json.dumps(result, sort_keys=True))
        return 0 if result["complete"] else 1
    if args.command == "setup":
        result = setup()
    elif args.root:
        result = dry_run(args.root) if args.command == "dry-run" else cleanup(args.root, abort_incomplete=args.abort_incomplete)
    else:
        parser.error("--root is required for dry-run and cleanup")
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("cleaned", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
