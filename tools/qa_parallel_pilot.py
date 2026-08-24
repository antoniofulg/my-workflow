#!/usr/bin/env python3
"""Create and validate the disposable, real-interface E2E-001 pilot fixture."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


FEATURE = "parallel-pilot"
MARKER = ".parallel-slice-qa-fixture"
ROOT = Path(__file__).resolve().parent.parent


def git(root: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def setup() -> dict[str, str]:
    root = Path(tempfile.mkdtemp(prefix="parallel-slice-pilot-"))
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
        return {"root": str(root), "feature": FEATURE, "status": "created"}
    except Exception:
        shutil.rmtree(root, ignore_errors=True)
        raise


def _validate_root(value: str) -> Path:
    root = Path(value).resolve()
    if not (root / MARKER).is_file() or not (root / ".specs/features" / FEATURE / "workflow.json").is_file():
        raise ValueError("not a parallel pilot fixture")
    return root


def dry_run(root_value: str) -> dict[str, object]:
    root = _validate_root(root_value)
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
    return {"validated": True, "root": str(root), "feature": FEATURE, "mode": "safe", "lanes": lanes}


def cleanup(root_value: str) -> dict[str, object]:
    root = _validate_root(root_value)
    worktree_root = root.parent / f".{root.name}-parallel-slices"
    if worktree_root.exists():
        for child in sorted(worktree_root.rglob("*"), reverse=True):
            if child.is_dir() and (child / ".git").exists():
                subprocess.run(["git", "worktree", "remove", "--force", str(child)], cwd=root, check=False)
        shutil.rmtree(worktree_root, ignore_errors=True)
    shutil.rmtree(root)
    return {"cleaned": True, "root": root_value}


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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
