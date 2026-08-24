#!/usr/bin/env python3
"""Create and validate the disposable, real-interface E2E-001 pilot fixture."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


FEATURE = "parallel-pilot"
MARKER = ".parallel-slice-qa-fixture"
OWNERSHIP = ".parallel-slice-qa-ownership.json"
PREFIX = "parallel-slice-pilot-"
ROOT = Path(__file__).resolve().parent.parent
OWNED_WORKTREES = ("parallel-pilot/A-T1", "parallel-pilot/B-T2")


def git(root: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def setup() -> dict[str, str]:
    root = Path(tempfile.mkdtemp(prefix="parallel-slice-pilot-")).resolve()
    try:
        git(root, "init", "-q")
        git(root, "config", "user.email", "qa@example.com")
        git(root, "config", "user.name", "Parallel QA")
        (root / "seed.txt").write_text("seed\n", encoding="utf-8")
        git(root, "add", "seed.txt")
        git(root, "commit", "-qm", "qa fixture seed")
        head = git(root, "rev-parse", "HEAD")
        feature_dir = root / ".specs" / "features" / FEATURE
        feature_dir.mkdir(parents=True)
        (feature_dir / "tasks.md").write_text(
            "### T1: pilot A\n**Status:** pending\n**Slice:** A\n**Where:** src/a.py\n**Depends on:** None\n**Resources:** none\n\n"
            "### T2: pilot B\n**Status:** pending\n**Slice:** B\n**Where:** src/b.py\n**Depends on:** None\n**Resources:** none\n",
            encoding="utf-8",
        )
        (feature_dir / "workflow.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "feature": FEATURE,
                    "git_head": head,
                    "parallelization": {"mode": "safe", "resource_provider": None},
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        (root / MARKER).write_text("disposable QA fixture\n", encoding="utf-8")
        (root / OWNERSHIP).write_text(
            json.dumps({"root": str(root), "feature": FEATURE, "source_git_head": head, "worktrees": list(OWNED_WORKTREES)}, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return {"root": str(root), "feature": FEATURE, "status": "created"}
    except Exception:
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
    if ownership.get("root") != str(root) or ownership.get("feature") != FEATURE or ownership.get("worktrees") != list(OWNED_WORKTREES):
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
    return root, ownership, snapshot, repository_head


def _residual_paths(worktree_root: Path) -> list[str]:
    if not worktree_root.exists():
        return []
    paths: list[str] = []
    for current, directories, files in os.walk(worktree_root, followlinks=False):
        current_path = Path(current)
        paths.extend(str(current_path / name) for name in sorted(directories + files))
    return sorted(paths)


def _validate_tombstone(root: Path, record: dict[str, object]) -> Path:
    if record.get("root") != str(root) or record.get("feature") != FEATURE:
        raise ValueError("pilot cleanup attestation is invalid")
    if record.get("worktrees") != list(OWNED_WORKTREES):
        raise ValueError("pilot cleanup attestation is invalid")
    if record.get("status") not in ("cleaned", "cleaned-with-residual"):
        raise ValueError("pilot cleanup attestation is invalid")
    source_git_head = record.get("source_git_head")
    workflow_git_head = record.get("workflow_git_head")
    if not isinstance(source_git_head, str) or source_git_head != workflow_git_head or len(source_git_head) != 40:
        raise ValueError("pilot cleanup attestation source HEAD is invalid")
    worktree_root = root.parent / f".{root.name}-parallel-slices"
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
    if plan.get("mode") != "safe" or plan.get("fallback") is not False or not isinstance(lanes, list) or len(lanes) != 2:
        raise ValueError("pilot fixture must expose exactly two safe lanes")
    if any(lane.get("status") != "ready" or lane.get("resources") != [] for lane in lanes):
        raise ValueError("pilot fixture lanes must be ready and resource-free")
    return {
        "validated": True,
        "root": str(root),
        "feature": FEATURE,
        "mode": "safe",
        "source_git_head": snapshot["git_head"],
        "repository_head": repository_head,
        "lanes": lanes,
    }


def cleanup(root_value: str) -> dict[str, object]:
    root = Path(root_value).resolve()
    attestation = root.parent / f".{root.name}.parallel-pilot-cleaned"
    if not root.exists():
        if not attestation.is_file():
            raise ValueError("pilot root is not an attested disposable fixture")
        record = json.loads(attestation.read_text(encoding="utf-8"))
        worktree_root = _validate_tombstone(root, record)
        residual = _residual_paths(worktree_root)
        if residual:
            record["status"] = "cleaned-with-residual"
            record["residual_paths"] = residual
            attestation.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
            return {"cleaned": False, "idempotent": True, "residual_paths": residual, "root": root_value}
        record["status"] = "cleaned"
        record["residual_paths"] = []
        attestation.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
        return {"cleaned": True, "idempotent": True, "residual_paths": [], "root": root_value}
    root, ownership, snapshot, _ = _validate_fixture(root_value)
    worktree_root = root.parent / f".{root.name}-parallel-slices"
    residual: list[str] = []
    for relative in OWNED_WORKTREES:
        worktree = worktree_root / relative
        if not worktree.exists():
            continue
        if not worktree.is_dir() or not (worktree / ".git").exists():
            residual.append(str(worktree))
            continue
        result = subprocess.run(["git", "worktree", "remove", "--force", str(worktree)], cwd=root, check=False, capture_output=True)
        if result.returncode != 0 or worktree.exists():
            continue
    if worktree_root.exists():
        for entry in (worktree_root / FEATURE, worktree_root):
            if entry.is_dir():
                try:
                    entry.rmdir()
                except OSError:
                    pass
    residual = _residual_paths(worktree_root)
    record = {
        "feature": FEATURE,
        "root": str(root),
        "source_git_head": ownership["source_git_head"],
        "workflow_git_head": snapshot["git_head"],
        "worktrees": list(OWNED_WORKTREES),
        "status": "cleaned-with-residual" if residual else "cleaned",
        "residual_paths": residual,
    }
    attestation.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
    shutil.rmtree(root)
    return {"cleaned": not residual, "idempotent": False, "residual_paths": residual, "root": root_value}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("setup", "dry-run", "cleanup"))
    parser.add_argument("--root")
    args = parser.parse_args()
    if args.command == "setup":
        result = setup()
    elif args.root:
        result = dry_run(args.root) if args.command == "dry-run" else cleanup(args.root)
    else:
        parser.error("--root is required for dry-run and cleanup")
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("cleaned", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
