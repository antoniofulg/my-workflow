#!/usr/bin/env python3
"""RST-02: tools/review-metrics.py reports the reviewed fraction from git history.

Every case builds a throwaway repository with real merge commits carrying real
trailers, because the tool's contract is with git's own trailer formatting.

  python3 tools/test_review_metrics.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent / "review-metrics.py"
SIGNAL = "Review-Signal:"
ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
}


class Repo:
    """A real git repository in a temporary directory."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.git("init", "-q", "-b", "main")

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", "-c", "commit.gpgsign=false", *args],
            cwd=self.path,
            env=ENV,
            check=True,
            capture_output=True,
            text=True,
        ).stdout

    def root(self) -> None:
        self.git("commit", "-q", "--allow-empty", "-m", "chore(repo): root")

    def deliver(self, name: str, trailer: str | None = None) -> None:
        """A merge commit standing in for a delivered pull request."""
        self.git("checkout", "-q", "-b", name)
        self.git("commit", "-q", "--allow-empty", "-m", f"feat({name}): work")
        self.git("checkout", "-q", "main")
        message = f"Merge branch '{name}'"
        if trailer is not None:
            message += f"\n\n{SIGNAL} {trailer}"
        self.git("merge", "--no-ff", "-q", "-m", message, name)

    def run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(TOOL), *args, "--json"],
            cwd=self.path,
            env=ENV,
            capture_output=True,
            text=True,
        )

    def metrics(self, *args: str) -> dict:
        result = self.run(*args)
        assert result.returncode == 0, result.stderr
        return json.loads(result.stdout)


class ReviewMetricsTests(unittest.TestCase):
    MEDIUM = "tier=medium slices=3 verified=3 sensor=2/2 rounds=1 findings=4 fixed=3 dismissed=1"
    SMALL = "tier=small slices=2 verified=1 sensor=1/3 rounds=2 findings=2 fixed=1 dismissed=1"

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Repo(Path(self.temporary.name))

    def test_signalled_and_unsigned_deliveries_are_both_counted(self) -> None:
        self.repo.root()
        self.repo.deliver("signed", self.MEDIUM)
        self.repo.deliver("bare")
        report = self.repo.metrics()
        self.assertEqual(report["deliveries"], 2)
        self.assertEqual(report["signalled"], 1)
        self.assertEqual(report["unsigned"], 1)

    def test_the_reviewed_fraction_is_verified_over_total_slices(self) -> None:
        self.repo.root()
        self.repo.deliver("one", self.MEDIUM)
        self.repo.deliver("two", self.SMALL)
        report = self.repo.metrics()
        self.assertEqual((report["verified"], report["slices"]), (4, 5))
        self.assertAlmostEqual(report["reviewed_fraction"], 4 / 5)

    def test_a_direct_tier_counts_as_reviewed_by_design(self) -> None:
        self.repo.root()
        self.repo.deliver("correction", "tier=direct")
        self.repo.deliver("batched", "tier=batch")
        report = self.repo.metrics()
        self.assertEqual(report["reviewed_by_design"], 2)
        self.assertEqual(report["unsigned"], 0)
        self.assertEqual(report["tiers"], {"batch": 1, "direct": 1})

    def test_a_tier_without_slices_does_not_divide_by_zero(self) -> None:
        self.repo.root()
        self.repo.deliver("correction", "tier=direct")
        report = self.repo.metrics()
        self.assertEqual(report["slices"], 0)
        self.assertIsNone(report["reviewed_fraction"])

    def test_a_range_without_a_trailer_reports_zeros_and_exits_zero(self) -> None:
        self.repo.root()
        self.repo.deliver("bare")
        report = self.repo.metrics()
        self.assertEqual(report["signalled"], 0)
        self.assertEqual(report["unsigned"], 1)
        self.assertIsNone(report["reviewed_fraction"])

    def test_an_empty_history_exits_zero(self) -> None:
        report = self.repo.metrics()
        self.assertEqual(report["deliveries"], 0)
        self.assertEqual(report["unsigned"], 0)
        self.assertIsNone(report["reviewed_fraction"])

    def test_an_unreadable_rev_range_fails_instead_of_reporting_zeros(self) -> None:
        self.repo.root()
        result = self.repo.run("no-such-ref..HEAD")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("no-such-ref", result.stderr)

    def test_whitespace_runs_between_fields_parse(self) -> None:
        self.repo.root()
        self.repo.deliver("spaced", self.MEDIUM.replace(" slices=3 ", "  slices=3\t"))
        report = self.repo.metrics()
        self.assertEqual(report["signalled"], 1)
        self.assertEqual((report["verified"], report["slices"]), (3, 3))

    def test_aggregates_sum_across_deliveries(self) -> None:
        self.repo.root()
        self.repo.deliver("one", self.MEDIUM)
        self.repo.deliver("two", self.SMALL)
        self.repo.deliver("three", "tier=direct")
        self.repo.deliver("four")
        report = self.repo.metrics()
        self.assertEqual(report["findings"], 6)
        self.assertEqual(report["fixed"], 4)
        self.assertEqual(report["dismissed"], 2)
        self.assertEqual(report["surviving_mutants"], 2)
        self.assertEqual(report["tiers"], {"direct": 1, "medium": 1, "small": 1})

    def test_a_rev_range_limits_what_is_read(self) -> None:
        self.repo.root()
        self.repo.deliver("early", self.MEDIUM)
        boundary = self.repo.git("rev-parse", "HEAD").strip()
        self.repo.deliver("late", self.SMALL)
        report = self.repo.metrics(f"{boundary}..HEAD")
        self.assertEqual(report["signalled"], 1)
        self.assertEqual((report["verified"], report["slices"]), (1, 2))


if __name__ == "__main__":
    unittest.main()
