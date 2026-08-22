"""Regression tests for deep-review manifest symlink handling.

Run: python3 tools/test_deep_review_symlink_manifest.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / ".agents/skills/deep-review/scripts"
sys.path.insert(0, str(SCRIPTS))

from _common import freeze_snapshot  # noqa: E402

BUILD_MANIFEST = SCRIPTS / "build_manifest.py"


def git(root: Path, *args: str) -> None:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    if result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)


def repo() -> Path:
    root = Path(tempfile.mkdtemp())
    git(root, "init", "-q")
    git(root, "config", "user.email", "test@example.com")
    git(root, "config", "user.name", "deep-review tests")
    (root / ".gitkeep").write_text("repo\n", encoding="utf-8")
    git(root, "add", ".gitkeep")
    git(root, "commit", "-qm", "init")
    return root


def build(root: Path) -> dict:
    out = root / ".deep-review" / "out"
    result = subprocess.run(
        [
            sys.executable,
            str(BUILD_MANIFEST),
            "--out",
            str(out),
            "--base",
            "HEAD",
            "--worktree",
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return json.loads((out / "manifest.json").read_text(encoding="utf-8"))


def record(manifest: dict, path: str) -> dict:
    return next(row for row in manifest["files"] if row["path"] == path)


class SymlinkManifestTests(unittest.TestCase):
    def test_untracked_symlink_directory_matches_adopted_deep_review(self) -> None:
        root = repo()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        target = root / ".agents" / "skills" / "deep-review"
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text("skill\n", encoding="utf-8")
        link = root / ".claude" / "skills" / "deep-review"
        link.parent.mkdir(parents=True)
        os.symlink("../../.agents/skills/deep-review", link)

        row = record(build(root), ".claude/skills/deep-review")
        self.assertEqual(row["kind"], "symlink")
        self.assertEqual(row["target"], "../../.agents/skills/deep-review")
        self.assertEqual((row["adds"], row["dels"]), (1, 0))
        self.assertEqual(row["hunks"], [{"start": 1, "lines": 1, "side": "new"}])

    def test_untracked_symlinks_never_read_targets(self) -> None:
        cases = {
            "file": ("target-file", "one\ntwo\n"),
            "broken": ("missing-target", None),
        }
        for name, (target_name, content) in cases.items():
            with self.subTest(name=name):
                root = repo()
                self.addCleanup(shutil.rmtree, root, ignore_errors=True)
                if content is not None:
                    (root / target_name).write_text(content, encoding="utf-8")
                link = root / f"{name}-link"
                os.symlink(target_name, link)
                row = record(build(root), link.name)
                self.assertEqual(row["kind"], "symlink")
                self.assertEqual(row["target"], target_name)
                self.assertEqual((row["adds"], row["dels"]), (1, 0))
                self.assertEqual(row["hunks"], [{"start": 1, "lines": 1, "side": "new"}])

    def test_untracked_symlink_to_outside_file_never_reads_outside(self) -> None:
        root = repo()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        with tempfile.TemporaryDirectory() as outside_raw:
            outside = Path(outside_raw) / "outside.txt"
            outside.write_text("outside one\noutside two\n", encoding="utf-8")
            link = root / "outside-link"
            os.symlink(str(outside), link)

            row = record(build(root), link.name)
            self.assertEqual(row["kind"], "symlink")
            self.assertEqual(row["target"], str(outside))
            self.assertEqual((row["adds"], row["dels"]), (1, 0))
            self.assertEqual(row["hunks"], [{"start": 1, "lines": 1, "side": "new"}])

    def test_tracked_symlink_keeps_git_diff_stats(self) -> None:
        root = repo()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        (root / "target-a").write_text("a\n", encoding="utf-8")
        (root / "target-b").write_text("b\n", encoding="utf-8")
        link = root / "tracked-link"
        os.symlink("target-a", link)
        git(root, "add", "target-a", "target-b", "tracked-link")
        git(root, "commit", "-qm", "add tracked symlink")
        link.unlink()
        os.symlink("target-b", link)

        row = record(build(root), link.name)
        self.assertEqual(row["status"], "M")
        self.assertEqual(row["kind"], "symlink")
        self.assertEqual(row["target"], "target-b")
        self.assertEqual((row["adds"], row["dels"]), (1, 1))
        self.assertEqual(row["hunks"], [{"start": 1, "lines": 1, "side": "new"}])

    def test_source_freeze_uses_symlink_path_and_target_only(self) -> None:
        root = repo()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        with tempfile.TemporaryDirectory() as outside_raw:
            outside = Path(outside_raw)
            first = outside / "first.txt"
            second = outside / "second.txt"
            first.write_text("before\n", encoding="utf-8")
            second.write_text("same target content\n", encoding="utf-8")
            link = root / "outside-link"
            os.symlink(str(first), link)
            out = root / ".deep-review" / "out"
            manifest = build(root)
            expected = manifest["worktree_snapshot"]

            first.write_text("after\n", encoding="utf-8")
            self.assertEqual(freeze_snapshot(root, out), expected)

            link.unlink()
            os.symlink(str(second), link)
            self.assertNotEqual(freeze_snapshot(root, out), expected)


if __name__ == "__main__":
    unittest.main()
