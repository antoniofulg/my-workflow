"""Canonical contract tests for the bundled Deep Review gates.

Run: python3 tools/test_deep_review_contract.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

SCRIPTS = Path(__file__).resolve().parents[1] / ".agents/skills/deep-review/scripts"
BUILD_MANIFEST = SCRIPTS / "build_manifest.py"
RUN_JOBS = SCRIPTS / "run_jobs.py"
RENDER_REVIEW = SCRIPTS / "render_review.py"
PUBLISH_RECIPE = (
    Path(__file__).resolve().parents[1]
    / ".agents/skills/deep-review/references/publish-github.md"
)
sys.path.insert(0, str(SCRIPTS))

from _common import freeze_snapshot  # noqa: E402
from merge_findings import coverage_ledger  # noqa: E402


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    if result.returncode:
        raise AssertionError(result.stderr or result.stdout)
    return result.stdout.strip()


def run_script(script: Path, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args], cwd=root, capture_output=True, text=True
    )


def publish_walkthrough_recipe() -> str:
    document = PUBLISH_RECIPE.read_text(encoding="utf-8")
    section = document[document.index("## 1. Upsert the walkthrough comment") :]
    start = section.index("```bash") + len("```bash\n")
    end = section.index("```", start)
    return section[start:end]


def init_repo(raw: str) -> Path:
    root = Path(raw)
    git(root, "init", "-q")
    git(root, "config", "user.email", "test@example.com")
    git(root, "config", "user.name", "deep-review tests")
    (root / "source.txt").write_text("a\n", encoding="utf-8")
    git(root, "add", "source.txt")
    git(root, "commit", "-qm", "initial")
    return root


def valid_payload() -> dict:
    return {
        "defects": [],
        "advisories": [],
        "suppressions": [],
        "coverage": {"hunks": [], "rules": []},
    }


def write_job_round(root: Path, *, payload: dict | None = None) -> Path:
    out = root / ".deep-review" / "out"
    out.mkdir(parents=True)
    head = git(root, "rev-parse", "HEAD")
    (out / "manifest.json").write_text(
        json.dumps(
            {
                "target": "test",
                "mode": "full",
                "round": 1,
                "base": head,
                "effective_base": head,
                "head": head,
                "diff_command": "git diff HEAD..HEAD -- <file>",
                "worktree_snapshot": freeze_snapshot(root, out),
                "files": [],
            }
        ),
        encoding="utf-8",
    )
    prompt = out / "prompt.md"
    prompt.write_text("review\n", encoding="utf-8")
    output = out / "agents" / "job.json"
    output.parent.mkdir()
    if payload is not None:
        output.write_text(json.dumps(payload), encoding="utf-8")
    (out / "jobs.json").write_text(
        json.dumps(
            {
                "jobs": [
                    {
                        "label": "sweep-tests",
                        "kind": "sweep",
                        "lane": "sweep",
                        "coverage_check": "sweep:tests",
                        "prompt": str(prompt.relative_to(root)),
                        "output": str(output.relative_to(root)),
                        "required_hunks": [],
                        "rule_ids": [],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return out


def render_fixture(root: Path, findings: list[dict]) -> Path:
    out = root / ".deep-review" / "render"
    out.mkdir(parents=True)
    head = git(root, "rev-parse", "HEAD")
    (out / "manifest.json").write_text(
        json.dumps(
            {
                "target": "test",
                "round": 1,
                "base": head,
                "head": head,
                "worktree_snapshot": freeze_snapshot(root, out),
                "files": [],
            }
        ),
        encoding="utf-8",
    )
    (out / "rules.json").write_text(json.dumps({"rules": []}), encoding="utf-8")
    (out / "context-pack.md").write_text("# Context\n", encoding="utf-8")
    (out / "walkthrough.md").write_text(
        "<!-- deep-review:walkthrough -->\n"
        "## Walkthrough\n\n"
        "## Changes\n\n"
        "## Estimated code review effort\n\n"
        "## Review details\n",
        encoding="utf-8",
    )
    (out / "findings.json").write_text(
        json.dumps(
            {
                "findings": findings,
                "advisories": [],
                "summary": {"merged_raw": 0},
                "review_stats": {"coverage": {"selected_hunk_lines": 0}},
                "reconciliation": {"resolved": [], "still_open_unreviewed": []},
            }
        ),
        encoding="utf-8",
    )
    return out


def finding(severity: str) -> dict:
    return {
        "fingerprint": f"fp-{severity}",
        "result_kind": "defect",
        "round_status": "new",
        "file": "source.txt",
        "line": 1,
        "end_line": None,
        "in_diff": False,
        "hunk": None,
        "category": "potential-issue",
        "severity": severity,
        "quick_win": False,
        "title": f"{severity} finding",
        "body": "The contract is violated.",
        "rule_ids": [],
        "evidence": ["Premise: contract fails → Path: source.txt:1 → Verdict: blocked."],
    }


class DeepReviewContractTests(unittest.TestCase):
    def test_walkthrough_publish_is_one_idempotent_upsert(self) -> None:
        recipe = publish_walkthrough_recipe()
        self.assertIn("--jq '[.[] | select(.body | contains(\"<!-- deep-review:walkthrough -->\"))][0].id // empty'", recipe)
        self.assertIn('if [ -n "$CID" ]; then', recipe)
        self.assertNotIn("/comments/null", recipe)

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            out = root / "out dir"
            out.mkdir()
            walkthrough = out / "walkthrough.md"
            walkthrough.write_text("walkthrough\n", encoding="utf-8")
            log = root / "gh.log"
            fake_gh = root / "gh"
            fake_gh.write_text(
                "#!/bin/sh\n"
                "printf 'CALL\\n' >> \"$GH_LOG\"\n"
                "for arg do printf '<%s>\\n' \"$arg\" >> \"$GH_LOG\"; done\n"
                "if [ \"$GH_MODE\" = existing ] && [ \"$2\" = \"repos/$R/issues/$N/comments\" ]; then\n"
                "  printf '42\\n'\n"
                "fi\n",
                encoding="utf-8",
            )
            fake_gh.chmod(0o700)

            def run_publish(mode: str) -> list[list[str]]:
                env = os.environ.copy()
                env.update(
                    {
                        "GH_LOG": str(log),
                        "GH_MODE": mode,
                        "PATH": f"{root}:{env['PATH']}",
                        "R": "owner/repo",
                        "N": "17",
                        "OUT": str(out),
                    }
                )
                log.write_text("", encoding="utf-8")
                result = subprocess.run(
                    ["sh", "-eu", "-c", recipe],
                    cwd=root,
                    env=env,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                calls: list[list[str]] = []
                current: list[str] = []
                for line in log.read_text(encoding="utf-8").splitlines():
                    if line == "CALL":
                        if current:
                            calls.append(current)
                        current = []
                    else:
                        current.append(line[1:-1])
                if current:
                    calls.append(current)
                return calls

            list_call = ["api", "repos/owner/repo/issues/17/comments", "--paginate", "--jq", "[.[] | select(.body | contains(\"<!-- deep-review:walkthrough -->\"))][0].id // empty"]
            body_arg = f"body=@{walkthrough}"
            self.assertEqual(
                run_publish("empty"),
                [list_call, ["api", "repos/owner/repo/issues/17/comments", "-F", body_arg]],
            )
            self.assertEqual(
                run_publish("existing"),
                [list_call, ["api", "repos/owner/repo/issues/comments/42", "-X", "PATCH", "-F", body_arg]],
            )

    def test_incremental_manifest_uses_effective_base_for_hunks_and_command(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            init_repo(raw)
            base = git(root, "rev-parse", "HEAD")
            (root / "source.txt").write_text("a\nb\n", encoding="utf-8")
            git(root, "add", "source.txt")
            git(root, "commit", "-qm", "first change")
            first = git(root, "rev-parse", "HEAD")
            out = root / ".deep-review" / "out"
            first_run = run_script(BUILD_MANIFEST, root, "--out", str(out), "--base", base, "--head", first)
            self.assertEqual(first_run.returncode, 0, first_run.stdout + first_run.stderr)
            (root / "source.txt").write_text("a\nb\nc\n", encoding="utf-8")
            git(root, "add", "source.txt")
            git(root, "commit", "-qm", "second change")
            second = git(root, "rev-parse", "HEAD")
            (out / "state.json").write_text(
                json.dumps({"rounds": [{"n": 1, "head": first}]}), encoding="utf-8"
            )

            second_run = run_script(BUILD_MANIFEST, root, "--out", str(out), "--base", base)
            self.assertEqual(second_run.returncode, 0, second_run.stdout + second_run.stderr)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            row = next(item for item in manifest["files"] if item["path"] == "source.txt")
            self.assertEqual(manifest["mode"], "incremental")
            self.assertEqual(manifest["effective_base"], first)
            self.assertEqual(row["hunks"], [{"start": 3, "lines": 1, "side": "new"}])
            self.assertEqual(manifest["diff_command"], f"git diff {first[:12]}..{second[:12]} -- <file>")

    def test_manifest_concurrency_uses_cli_config_default_and_rejects_invalid_values(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            init_repo(raw)
            out = root / ".deep-review" / "default"
            result = run_script(BUILD_MANIFEST, root, "--out", str(out), "--base", "HEAD", "--head", "HEAD")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads((out / "manifest.json").read_text())["concurrency"], 3)

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            init_repo(raw)
            (root / ".deep-review.yaml").write_text("concurrency: 5\n", encoding="utf-8")
            out = root / ".deep-review" / "config"
            result = run_script(BUILD_MANIFEST, root, "--out", str(out), "--base", "HEAD", "--head", "HEAD")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads((out / "manifest.json").read_text())["concurrency"], 5)
            override = root / ".deep-review" / "override"
            result = run_script(BUILD_MANIFEST, root, "--out", str(override), "--base", "HEAD", "--head", "HEAD", "--concurrency", "2")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads((override / "manifest.json").read_text())["concurrency"], 2)

        for raw_value in ("true", "false", "0", "7", '"3"', "1.5"):
            with self.subTest(raw_value=raw_value), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                init_repo(raw)
                (root / ".deep-review.yaml").write_text(f"concurrency: {raw_value}\n", encoding="utf-8")
                result = run_script(BUILD_MANIFEST, root, "--out", str(root / ".deep-review/out"), "--base", "HEAD", "--head", "HEAD")
                self.assertNotEqual(result.returncode, 0)

    def test_runner_rejects_removed_workers_option(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            init_repo(raw)
            out = write_job_round(root, payload=valid_payload())
            result = run_script(RUN_JOBS, root, "--out", str(out), "--workers", "2", "--validate-only")
            self.assertNotEqual(result.returncode, 0)

    def test_manifest_handles_untracked_regular_files_and_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            init_repo(raw)
            (root / "regular.txt").write_text("one\ntwo\n", encoding="utf-8")
            os.symlink("regular.txt", root / "link.txt")
            result = run_script(
                BUILD_MANIFEST,
                root,
                "--out",
                str(root / ".deep-review" / "out"),
                "--base",
                "HEAD",
                "--worktree",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest = json.loads(
                (root / ".deep-review/out/manifest.json").read_text(encoding="utf-8")
            )
            regular = next(item for item in manifest["files"] if item["path"] == "regular.txt")
            link = next(item for item in manifest["files"] if item["path"] == "link.txt")
            self.assertEqual((regular["adds"], regular["dels"]), (2, 0))
            self.assertEqual(regular["hunks"], [{"start": 1, "lines": 2, "side": "new"}])
            self.assertEqual((link["kind"], link["target"]), ("symlink", "regular.txt"))
            self.assertEqual(link["hunks"], [{"start": 1, "lines": 1, "side": "new"}])

    def test_critical_and_major_findings_cannot_render_ship(self) -> None:
        for severity in ("critical", "major"):
            with self.subTest(severity=severity), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                init_repo(raw)
                out = render_fixture(root, [finding(severity)])
                result = run_script(RENDER_REVIEW, root, "--out", str(out), "--no-freeze-check")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                review = (out / "review.md").read_text(encoding="utf-8")
                self.assertIn("**Verdict: FIX_BEFORE_SHIP**", review)
                self.assertNotIn("**Verdict: SHIP**", review)

    def test_incomplete_defect_or_polish_hunk_coverage_is_rejected(self) -> None:
        manifest = {
            "files": [
                {
                    "path": "source.txt",
                    "disposition": "selected",
                    "hunks": [{"start": 1, "lines": 2, "side": "new"}],
                }
            ]
        }
        for missing_lane in ("defect", "polish"):
            present_lane = "polish" if missing_lane == "defect" else "defect"
            collected = {
                "hunk_coverage": [
                    {"lane": present_lane, "file": "source.txt", "hunk": "new:1-2"}
                ],
                "rule_coverage": [],
            }
            with self.subTest(missing_lane=missing_lane), self.assertRaisesRegex(
                RuntimeError, f"{missing_lane} coverage incomplete"
            ):
                coverage_ledger(manifest, collected)

    def test_validate_only_rejects_source_drift_before_accepting_valid_output(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            init_repo(raw)
            out = write_job_round(root, payload=valid_payload())
            (root / "source.txt").write_text("drifted\n", encoding="utf-8")
            result = run_script(RUN_JOBS, root, "--out", str(out), "--validate-only")
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn("source drifted", result.stderr)

    def test_render_rejects_source_drift(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            init_repo(raw)
            out = render_fixture(root, [])
            (root / "source.txt").write_text("drifted\n", encoding="utf-8")
            result = run_script(RENDER_REVIEW, root, "--out", str(out))
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("source drifted", result.stderr)

    def test_invalid_and_blocked_jobs_never_validate(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            init_repo(raw)
            out = write_job_round(root, payload={})
            invalid = run_script(RUN_JOBS, root, "--out", str(out), "--validate-only")
            self.assertEqual(invalid.returncode, 1, invalid.stdout + invalid.stderr)
            status = json.loads((out / "runs/jobs-status.json").read_text(encoding="utf-8"))
            self.assertEqual(status["jobs"][0]["status"], "invalid")

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            init_repo(raw)
            out = write_job_round(root)
            blocker = out / "blocker.py"
            blocker.write_text("print('usageLimitExceeded')\n", encoding="utf-8")
            blocked = run_script(
                RUN_JOBS,
                root,
                "--out",
                str(out),
                "--command",
                f"{sys.executable} {blocker} {{prompt}} {{output}} {{label}}",
            )
            self.assertEqual(blocked.returncode, 2, blocked.stdout + blocked.stderr)
            self.assertEqual(
                json.loads((out / "run-blocker.json").read_text(encoding="utf-8"))["status"],
                "blocked",
            )
            validation = run_script(RUN_JOBS, root, "--out", str(out), "--validate-only")
            self.assertEqual(validation.returncode, 1, validation.stdout + validation.stderr)


if __name__ == "__main__":
    unittest.main()
