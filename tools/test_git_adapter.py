"""Spec-derived disposable Git tests for checkpoint and slice integration."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents/skills/autonomous/scripts"))
import git_adapter


def run(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def call(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def commit(root: Path, message: str) -> str:
    call(root, "add", ".")
    call(root, "commit", "-qm", message)
    return run(root, "rev-parse", "HEAD")


def repo() -> tuple[Path, str]:
    root = Path(tempfile.mkdtemp())
    call(root, "init", "-q")
    call(root, "config", "user.email", "test@example.com")
    call(root, "config", "user.name", "Test")
    (root / "shared.txt").write_text("base\n", encoding="utf-8")
    base = commit(root, "base")
    return root, base


def branches(root: Path, base: str) -> tuple[str, str, Path]:
    call(root, "branch", "producer")
    call(root, "branch", "consumer")
    call(root, "switch", "producer")
    (root / "producer.txt").write_text("producer\n", encoding="utf-8")
    producer = commit(root, "producer")
    call(root, "switch", "consumer")
    (root / "consumer.txt").write_text("consumer\n", encoding="utf-8")
    commit(root, "consumer")
    call(root, "switch", "--detach", base)
    lane = root / "consumer-lane"
    call(root, "worktree", "add", "-q", str(lane), "consumer")
    return producer, run(lane, "rev-parse", "HEAD"), lane


def test_exact_checkpoint_rebase_and_ancestor_noop() -> None:
    root, base = repo()
    try:
        producer, pre_head, lane = branches(root, base)
        adapter = git_adapter.GitAdapter(root)
        synced = adapter.sync_checkpoint(lane, producer, declared_paths=["producer.txt"])
        assert synced["status"] == "synced"
        assert synced["pre_head"] == pre_head
        assert synced["post_head"] != pre_head
        assert synced["changed_paths"] == ["producer.txt"]
        assert synced["invalidated_evidence"] == ["gate", "technical_verifier", "deep_review"]
        assert run(lane, "merge-base", "--is-ancestor", producer, "HEAD") == ""

        noop = adapter.sync_checkpoint(lane, producer, declared_paths=["producer.txt", "consumer.txt"])
        assert noop["status"] == "noop"
        assert noop["pre_head"] == noop["post_head"] == run(lane, "rev-parse", "HEAD")
        assert noop["changed_paths"] == []
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", "consumer-lane"], cwd=root, check=False, stdout=subprocess.DEVNULL)
        shutil.rmtree(root, ignore_errors=True)


def test_conflict_aborts_rebase_and_restores_clean_pre_sync_head() -> None:
    root, base = repo()
    try:
        call(root, "branch", "producer")
        call(root, "branch", "consumer")
        call(root, "switch", "producer")
        (root / "shared.txt").write_text("producer\n", encoding="utf-8")
        producer = commit(root, "producer conflict")
        call(root, "switch", "consumer")
        (root / "shared.txt").write_text("consumer\n", encoding="utf-8")
        commit(root, "consumer conflict")
        call(root, "switch", "--detach", base)
        lane = root / "consumer-lane"
        call(root, "worktree", "add", "-q", str(lane), "consumer")
        pre_head = run(lane, "rev-parse", "HEAD")
        result = git_adapter.GitAdapter(root).sync_checkpoint(lane, producer, declared_paths=["shared.txt"])
        assert result["status"] == "serial"
        assert result["serial_recovery"] is True
        assert result["pre_head"] == result["post_head"] == pre_head
        assert run(lane, "status", "--porcelain") == ""
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", "consumer-lane"], cwd=root, check=False, stdout=subprocess.DEVNULL)
        shutil.rmtree(root, ignore_errors=True)


def test_dirty_consumer_is_rejected_before_checkpoint_effect() -> None:
    root, base = repo()
    try:
        producer, pre_head, lane = branches(root, base)
        (lane / "uncommitted.txt").write_text("do not touch\n", encoding="utf-8")
        result = git_adapter.GitAdapter(root).sync_checkpoint(lane, producer, declared_paths=["producer.txt"])
        assert result["status"] == "serial"
        assert result["reason"] == "dirty-worktree"
        assert result["pre_head"] == result["post_head"] == pre_head
        assert (lane / "uncommitted.txt").read_text(encoding="utf-8") == "do not touch\n"
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", "consumer-lane"], cwd=root, check=False, stdout=subprocess.DEVNULL)
        shutil.rmtree(root, ignore_errors=True)


def test_undeclared_change_and_incomparable_checkpoints_are_serial() -> None:
    root, base = repo()
    try:
        producer_a = root / "a.txt"
        call(root, "branch", "producer-a")
        call(root, "switch", "producer-a")
        producer_a.write_text("a\n", encoding="utf-8")
        checkpoint_a = commit(root, "producer a")
        call(root, "switch", "--detach", base)
        call(root, "branch", "producer-b")
        call(root, "switch", "producer-b")
        (root / "b.txt").write_text("b\n", encoding="utf-8")
        checkpoint_b = commit(root, "producer b")
        call(root, "switch", "--detach", base)
        call(root, "branch", "consumer")
        call(root, "switch", "consumer")
        (root / "consumer.txt").write_text("consumer\n", encoding="utf-8")
        commit(root, "consumer")
        call(root, "switch", "--detach", base)
        lane = root / "consumer-lane"
        call(root, "worktree", "add", "-q", str(lane), "consumer")
        adapter = git_adapter.GitAdapter(root)
        multiple = adapter.sync_checkpoint(lane, [checkpoint_a, checkpoint_b], declared_paths=["a.txt", "b.txt"])
        assert multiple["status"] == "serial"
        assert multiple["reason"] == "incomparable-checkpoints"
        assert run(lane, "rev-parse", "HEAD") != base
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", "consumer-lane"], cwd=root, check=False, stdout=subprocess.DEVNULL)
        shutil.rmtree(root, ignore_errors=True)


def test_changed_head_reports_evidence_invalidation_and_undeclared_paths_restore() -> None:
    root, base = repo()
    try:
        producer, pre_head, lane = branches(root, base)
        result = git_adapter.GitAdapter(root).sync_checkpoint(lane, producer, declared_paths=[])
        assert result["status"] == "serial"
        assert result["reason"] == "undeclared-changed-path"
        assert result["pre_head"] == result["post_head"] == pre_head
        assert result["changed_paths"] == ["producer.txt"]
        assert result["invalidated_evidence"] == []
        assert run(lane, "status", "--porcelain") == ""
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", "consumer-lane"], cwd=root, check=False, stdout=subprocess.DEVNULL)
        shutil.rmtree(root, ignore_errors=True)


def test_verified_slice_integration_is_deterministic_and_preserves_commits() -> None:
    root, base = repo()
    try:
        call(root, "branch", "slice-A")
        call(root, "switch", "slice-A")
        (root / "a.txt").write_text("A\n", encoding="utf-8")
        commit_a = commit(root, "slice A")
        call(root, "switch", "--detach", base)
        call(root, "branch", "slice-B")
        call(root, "switch", "slice-B")
        (root / "b.txt").write_text("B\n", encoding="utf-8")
        commit_b = commit(root, "slice B")
        call(root, "switch", "--detach", base)
        result = git_adapter.GitAdapter(root).integrate_slices(
            root, [{"slice": "B", "commit": commit_b}, {"slice": "A", "commit": commit_a}]
        )
        assert result["status"] == "merged"
        assert result["merged"] == [commit_a, commit_b]
        assert result["changed_paths"] == ["a.txt", "b.txt"]
        assert run(root, "merge-base", "--is-ancestor", commit_a, "HEAD") == ""
        assert run(root, "merge-base", "--is-ancestor", commit_b, "HEAD") == ""
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_integration_conflict_aborts_without_touching_pre_operation_head() -> None:
    root, base = repo()
    try:
        call(root, "branch", "slice-A")
        call(root, "switch", "slice-A")
        (root / "shared.txt").write_text("A\n", encoding="utf-8")
        commit_a = commit(root, "slice A conflict")
        call(root, "switch", "--detach", base)
        call(root, "branch", "slice-B")
        call(root, "switch", "slice-B")
        (root / "shared.txt").write_text("B\n", encoding="utf-8")
        commit_b = commit(root, "slice B conflict")
        call(root, "switch", "--detach", base)
        pre_head = run(root, "rev-parse", "HEAD")
        result = git_adapter.GitAdapter(root).integrate_slices(
            root, [{"slice": "B", "commit": commit_b}, {"slice": "A", "commit": commit_a}]
        )
        assert result["status"] == "serial"
        assert result["reason"] == "merge-conflict"
        assert result["pre_head"] == result["post_head"] == pre_head
        assert run(root, "status", "--porcelain") == ""
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
