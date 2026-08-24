"""Fail-closed Git checkpoint and verified-slice integration adapter."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


class GitAdapterError(RuntimeError):
    """A Git operation cannot safely produce a correlated receipt."""


Runner = Callable[..., subprocess.CompletedProcess[str]]
_COMMIT = re.compile(r"^[0-9a-f]{40}$")


def _run(argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, shell=False, capture_output=True, text=True, **kwargs)


class GitAdapter:
    """Operate on one validated worktree at a time, never resolving conflicts automatically."""

    def __init__(self, root: Path | str, *, runner: Runner = _run) -> None:
        self.root = Path(root).resolve()
        self.runner = runner
        self._validate_repo(self.root)

    def _git(self, cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        completed = self.runner(["git", *args], cwd=str(cwd), check=False)
        if check and completed.returncode != 0:
            raise GitAdapterError(completed.stderr.strip() or "git command failed")
        return completed

    def _validate_repo(self, path: Path) -> None:
        if not path.is_dir():
            raise GitAdapterError("repository is not a directory")
        result = self._git(path, "rev-parse", "--show-toplevel")
        actual = Path(result.stdout.strip()).resolve()
        if actual != path:
            raise GitAdapterError("repository root mismatch")

    def _validate_worktree(self, path: Path | str) -> Path:
        target = Path(path).resolve()
        if not target.is_dir():
            raise GitAdapterError("worktree is not a directory")
        self._git(target, "rev-parse", "--is-inside-work-tree")
        return target

    def head(self, worktree: Path | str | None = None) -> str:
        target = self.root if worktree is None else self._validate_worktree(worktree)
        return self._git(target, "rev-parse", "HEAD").stdout.strip()

    def is_clean(self, worktree: Path | str | None = None) -> bool:
        target = self.root if worktree is None else self._validate_worktree(worktree)
        return self._git(target, "status", "--porcelain", "--untracked-files=all").stdout == ""

    def _valid_commit(self, target: Path, value: Any) -> str:
        if not isinstance(value, str) or not _COMMIT.fullmatch(value):
            raise GitAdapterError("invalid checkpoint commit")
        self._git(target, "cat-file", "-e", value + "^{commit}")
        return value

    def _ancestor(self, target: Path, older: str, newer: str) -> bool:
        return self._git(target, "merge-base", "--is-ancestor", older, newer, check=False).returncode == 0

    def _changed_paths(self, target: Path, before: str, after: str) -> list[str]:
        if before == after:
            return []
        output = self._git(target, "diff", "--name-only", before, after).stdout
        return sorted(path for path in output.splitlines() if path)

    def _restore(self, target: Path, before: str) -> None:
        self._git(target, "rebase", "--abort", check=False)
        self._git(target, "merge", "--abort", check=False)
        self._git(target, "reset", "--hard", before)

    @staticmethod
    def _serial(pre_head: str, reason: str, *, changed_paths: list[str] | None = None) -> dict[str, Any]:
        return {
            "status": "serial",
            "serial_recovery": True,
            "reason": reason,
            "pre_head": pre_head,
            "post_head": pre_head,
            "changed_paths": changed_paths or [],
            "invalidated_evidence": [],
        }

    def sync_checkpoint(
        self,
        consumer: Path | str,
        producer_commit: str | Sequence[str],
        *,
        declared_paths: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        target = self._validate_worktree(consumer)
        pre_head = self.head(target)
        if not self.is_clean(target):
            return self._serial(pre_head, "dirty-worktree")
        values = [producer_commit] if isinstance(producer_commit, str) else list(producer_commit)
        try:
            checkpoints = list(dict.fromkeys(self._valid_commit(target, value) for value in values))
        except GitAdapterError:
            return self._serial(pre_head, "invalid-checkpoint")
        if not checkpoints:
            return self._serial(pre_head, "missing-checkpoint")
        incomparable = any(
            not self._ancestor(target, left, right) and not self._ancestor(target, right, left)
            for index, left in enumerate(checkpoints)
            for right in checkpoints[index + 1 :]
        )
        if incomparable:
            return self._serial(pre_head, "incomparable-checkpoints")
        producer = next((candidate for candidate in checkpoints if all(
            self._ancestor(target, other, candidate) for other in checkpoints
        )), checkpoints[-1])
        if self._ancestor(target, producer, pre_head):
            return {
                "status": "noop",
                "serial_recovery": False,
                "pre_head": pre_head,
                "post_head": pre_head,
                "producer_commit": producer,
                "byte_stable": True,
                "changed_paths": [],
                "invalidated_evidence": [],
            }
        rebased = self._git(target, "rebase", producer, check=False)
        if rebased.returncode != 0:
            self._restore(target, pre_head)
            return self._serial(pre_head, "rebase-conflict")
        post_head = self.head(target)
        changed_paths = self._changed_paths(target, pre_head, post_head)
        if (declared_paths is not None and not set(changed_paths).issubset(set(declared_paths))) or not self._ancestor(target, producer, post_head):
            self._restore(target, pre_head)
            return self._serial(pre_head, "undeclared-changed-path", changed_paths=changed_paths)
        if not self.is_clean(target):
            self._restore(target, pre_head)
            return self._serial(pre_head, "dirty-after-rebase", changed_paths=changed_paths)
        return {
            "status": "synced",
            "serial_recovery": False,
            "producer_commit": producer,
            "pre_head": pre_head,
            "post_head": post_head,
            "changed_paths": changed_paths,
            "invalidated_evidence": ["gate", "technical_verifier", "deep_review"],
        }

    def integrate_slices(
        self,
        feature_worktree: Path | str,
        verified_slices: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        target = self._validate_worktree(feature_worktree)
        pre_head = self.head(target)
        if not self.is_clean(target):
            return self._serial(pre_head, "dirty-worktree")
        try:
            entries = sorted(
                ((str(item["slice"]), self._valid_commit(target, item["commit"])) for item in verified_slices),
                key=lambda item: (item[0], item[1]),
            )
        except (KeyError, GitAdapterError, TypeError):
            return self._serial(pre_head, "invalid-verified-slice")
        if len({commit for _, commit in entries}) != len(entries):
            return self._serial(pre_head, "duplicate-verified-slice")
        merged: list[str] = []
        for _, commit in entries:
            result = self._git(target, "merge", "--no-ff", "--no-edit", commit, check=False)
            if result.returncode != 0:
                self._restore(target, pre_head)
                return self._serial(pre_head, "merge-conflict")
            merged.append(commit)
        post_head = self.head(target)
        if not self.is_clean(target):
            self._restore(target, pre_head)
            return self._serial(pre_head, "dirty-after-merge")
        return {
            "status": "merged",
            "serial_recovery": False,
            "pre_head": pre_head,
            "post_head": post_head,
            "merged": merged,
            "changed_paths": self._changed_paths(target, pre_head, post_head),
            "invalidated_evidence": [],
        }

    def integrate_slice(self, feature_worktree: Path | str, verified_slices: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        return self.integrate_slices(feature_worktree, verified_slices)


def sync_checkpoint(root: Path | str, consumer: Path | str, producer_commit: str | Sequence[str], *, declared_paths: Sequence[str] | None = None) -> dict[str, Any]:
    return GitAdapter(root).sync_checkpoint(consumer, producer_commit, declared_paths=declared_paths)


def integrate_slices(root: Path | str, feature_worktree: Path | str, verified_slices: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return GitAdapter(root).integrate_slices(feature_worktree, verified_slices)


if __name__ == "__main__":
    raise SystemExit("git_adapter is a library; use the coordinator or import GitAdapter")
