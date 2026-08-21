"""Contract tests for observational deep-review metrics and the public runner."""

from __future__ import annotations

import json
import os
import sqlite3
import stat
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / ".agents/skills/deep-review/scripts"
sys.path.insert(0, str(SCRIPTS))

from token_metrics import (  # noqa: E402
    TokenMetricsError,
    checkpoint_metrics,
    finalize_metrics,
    read_metrics,
    read_telemetry,
    start_metrics,
)
import token_metrics  # noqa: E402
import run_jobs  # noqa: E402

PREFIX = "/reviewer/deep-review"
REPO = Path.cwd()


def create_db(path: Path, total: int = 0, agent_path: str = PREFIX) -> None:
    db = sqlite3.connect(path)
    db.execute("create table threads (id text, rollout_path text, tokens_used integer, agent_path text, first_user_message text)")
    db.execute("insert into threads values (?, ?, ?, ?, ?)", ("thread-1", "", total, agent_path, "secret prompt"))
    db.commit()
    db.close()


def update_db(path: Path, total: int) -> None:
    db = sqlite3.connect(path)
    db.execute("update threads set tokens_used = ?", (total,))
    db.commit()
    db.close()


def valid_output(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"defects": [], "advisories": [], "suppressions": [], "coverage": {"hunks": [], "rules": []}}), encoding="utf-8")


def write_jobs(path: Path, output_dir: str, count: int = 2) -> None:
    path.write_text(json.dumps({"jobs": [
        {"label": f"job-{index}", "kind": "sweep", "lane": "tests", "prompt": str(path.parent / f"p{index}"), "output": f"{output_dir}/job-{index}.json", "required_hunks": [], "rule_ids": []}
        for index in range(1, count + 1)
    ]}), encoding="utf-8")


def helper_script(path: Path, *, overlap: bool = False) -> None:
    if overlap:
        path.write_text(
            "import json, os, sys, time\n"
            "prompt, output, label, calls, active, overlap = sys.argv[1:]\n"
            "if os.path.exists(active): open(overlap, 'w', encoding='utf-8').close()\n"
            "open(active, 'w', encoding='utf-8').close()\n"
            "with open(calls, 'a', encoding='utf-8') as stream: stream.write(label + '\\n')\n"
            "time.sleep(0.12)\n"
            "json.dump({'defects': [], 'advisories': [], 'suppressions': [], 'coverage': {'hunks': [], 'rules': []}}, open(output, 'w', encoding='utf-8'))\n"
            "try: os.unlink(active)\n"
            "except FileNotFoundError: pass\n",
            encoding="utf-8",
        )

    else:
        path.write_text(
            "import json, sys\n"
            "prompt, output, label, calls = sys.argv[1:]\n"
            "with open(calls, 'a', encoding='utf-8') as stream: stream.write(label + '\\n')\n"
            "json.dump({'defects': [], 'advisories': [], 'suppressions': [], 'coverage': {'hunks': [], 'rules': []}}, open(output, 'w', encoding='utf-8'))\n",
            encoding="utf-8",
        )


def retry_helper_script(path: Path) -> None:
    path.write_text(
        "import json, os, pathlib, sys, time\n"
        "prompt, output, label, calls, state_dir, active, overlap = sys.argv[1:]\n"
        "state = pathlib.Path(state_dir) / label\n"
        "attempt = int(state.read_text()) + 1 if state.exists() else 1\n"
        "state.parent.mkdir(parents=True, exist_ok=True)\n"
        "state.write_text(str(attempt))\n"
        "if os.path.exists(active): open(overlap, 'w', encoding='utf-8').close()\n"
        "open(active, 'w', encoding='utf-8').close()\n"
        "with open(calls, 'a', encoding='utf-8') as stream: stream.write(f'{label}:{attempt}\\n')\n"
        "time.sleep(0.05)\n"
        "if attempt == 1:\n"
        "    os.unlink(active)\n"
        "    raise SystemExit(1)\n"
        "json.dump({'defects': [], 'advisories': [], 'suppressions': [], 'coverage': {'hunks': [], 'rules': []}}, open(output, 'w', encoding='utf-8'))\n"
        "os.unlink(active)\n",
        encoding="utf-8",
    )
def runner(out: Path, jobs: Path, helper: Path, calls: Path, *, db: Path | None = None, ledger: Path | None = None, workers: int = 2, extra: list[str] | None = None, helper_suffix: list[Path] | None = None) -> list[str]:
    command = [sys.executable, str(SCRIPTS / "run_jobs.py"), "--out", str(out), "--jobs-file", str(jobs), "--workers", str(workers), "--no-freeze-check"]
    if helper:
        suffix = " ".join(str(value) for value in (helper_suffix or []))
        command += ["--command", f"{sys.executable} {helper} {{prompt}} {{output}} {{label}} {calls} {suffix}".strip()]
    if db is not None:
        command += ["--metrics", "--metrics-db", str(db), "--metrics-reviewer-prefix", PREFIX]
    if ledger is not None:
        command += ["--metrics-ledger", str(ledger)]
    return command + (extra or [])


class TokenMetricsTests(unittest.TestCase):
    def test_drm01_compatible_totals_and_cumulative_delta(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            db, ledger = root / "codex.sqlite", root / "metrics.json"
            create_db(db, 100)
            started = start_metrics(ledger, db, PREFIX, repository="repo", selected_files=1, jobs=1)
            update_db(db, 160)
            checkpoint = checkpoint_metrics(ledger, 1)
            self.assertEqual(checkpoint["usage"]["total_tokens"], 60)
            self.assertEqual(checkpoint["checkpoints"][0]["completed_jobs"], 1)
            update_db(db, 180)
            finished = finalize_metrics(ledger)
            self.assertEqual(finished["status"], "complete")
            self.assertEqual(finished["usage"]["total_tokens"], 80)
            self.assertEqual(start_metrics(ledger, db, PREFIX, repository="repo", selected_files=1, jobs=1)["status"], "complete")
            self.assertEqual(started["baseline_by_thread"]["thread-1"]["total_tokens"], 100)

    def test_drm02_runner_serializes_reviewers_and_metrics_checkpoints(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            db, out, jobs = root / "codex.sqlite", REPO / ".deep-review/metrics-concurrency", root / "jobs.json"
            calls, active, overlap, ledger = root / "calls", root / "active", root / "overlap", root / "metrics.json"
            create_db(db)
            write_jobs(jobs, ".deep-review/metrics-concurrency")
            helper = root / "job.py"
            helper_script(helper, overlap=True)
            try:
                result = subprocess.run(runner(out, jobs, helper, calls, db=db, ledger=ledger, helper_suffix=[active, overlap]), cwd=REPO, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertFalse(overlap.exists())
                self.assertEqual(sorted(calls.read_text(encoding="utf-8").splitlines()), ["job-1", "job-2"])
                metrics = read_metrics(ledger)
                self.assertEqual(metrics["status"], "complete")
                self.assertEqual([row["completed_jobs"] for row in metrics["checkpoints"]], [1, 2])
                self.assertTrue(all("job" not in row for row in metrics["checkpoints"]))
            finally:
                shutil.rmtree(out, ignore_errors=True)

    def test_drm03_invalid_missing_and_regressing_metrics_do_not_change_review_exit(self) -> None:
        scenarios = ("invalid", "missing", "regressing", "deleted", "ledger-invalid")
        for scenario in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                db, out, jobs = root / "codex.sqlite", REPO / f".deep-review/metrics-{scenario}", root / "jobs.json"
                calls, ledger = root / "calls", root / "metrics.json"
                create_db(db, 100 if scenario == "regressing" else 0)
                write_jobs(jobs, f".deep-review/metrics-{scenario}")
                helper = root / "job.py"
                helper_script(helper)
                if scenario == "invalid":
                    connection = sqlite3.connect(db)
                    connection.execute("update threads set tokens_used = 'bad'")
                    connection.commit()
                    connection.close()
                if scenario == "regressing":
                    start_metrics(ledger, db, PREFIX, repository=str(REPO), selected_files=2, jobs=2)
                    update_db(db, 90)
                if scenario == "deleted":
                    start_metrics(ledger, db, PREFIX, repository=str(REPO), selected_files=2, jobs=2)
                    connection = sqlite3.connect(db)
                    connection.execute("delete from threads where id = 'thread-1'")
                    connection.commit()
                    connection.close()
                if scenario == "ledger-invalid":
                    ledger.mkdir()
                shutil.rmtree(out, ignore_errors=True)
                result = subprocess.run(runner(out, jobs, helper, calls, db=None if scenario == "missing" else db, ledger=ledger), cwd=REPO, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(sorted(calls.read_text(encoding="utf-8").splitlines()), ["job-1", "job-2"])
                if scenario == "ledger-invalid":
                    status = json.loads((out / "runs/jobs-status.json").read_text(encoding="utf-8"))["metrics"]
                    self.assertEqual(status, "unavailable")
                else:
                    self.assertEqual(read_metrics(ledger)["status"], "unavailable")
                shutil.rmtree(out, ignore_errors=True)

    def test_drm03_checkpoint_observation_failure_is_nonblocking(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            db, out, jobs = root / "codex.sqlite", REPO / ".deep-review/metrics-checkpoint-failure", root / "jobs.json"
            calls, ledger = root / "calls", root / "jobs.json.metrics.json"
            create_db(db)
            write_jobs(jobs, ".deep-review/metrics-checkpoint-failure")
            helper = root / "job.py"
            helper_script(helper)
            command = runner(out, jobs, helper, calls, db=db, ledger=ledger, workers=1)
            old_argv = sys.argv
            try:
                sys.argv = [command[1], *command[2:]]
                with patch.object(run_jobs, "checkpoint_metrics", side_effect=OSError("checkpoint unavailable")):
                    result = run_jobs.main()
                self.assertEqual(result, 0)
                self.assertEqual(calls.read_text(encoding="utf-8").splitlines(), ["job-1", "job-2"])
                status = json.loads((out / "runs/jobs-status.json").read_text(encoding="utf-8"))
                self.assertEqual(status["metrics"], "unavailable")
            finally:
                sys.argv = old_argv
                shutil.rmtree(out, ignore_errors=True)

    def test_drm03_finalize_observation_failure_is_nonblocking(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            db, out, jobs = root / "codex.sqlite", REPO / ".deep-review/metrics-finalize-failure", root / "jobs.json"
            calls, ledger = root / "calls", root / "metrics.json"
            create_db(db)
            write_jobs(jobs, ".deep-review/metrics-finalize-failure")
            helper = root / "job.py"
            helper_script(helper)
            command = runner(out, jobs, helper, calls, db=db, ledger=ledger, workers=1)
            old_argv = sys.argv
            try:
                sys.argv = [command[1], *command[2:]]
                with patch.object(run_jobs, "finalize_metrics", side_effect=OSError("finalize unavailable")):
                    result = run_jobs.main()
                self.assertEqual(result, 0)
                self.assertEqual(calls.read_text(encoding="utf-8").splitlines(), ["job-1", "job-2"])
                status = json.loads((out / "runs/jobs-status.json").read_text(encoding="utf-8"))
                self.assertEqual(status["metrics"], "unavailable")
            finally:
                sys.argv = old_argv
                shutil.rmtree(out, ignore_errors=True)

    def test_drm04_configured_retries_run_serially(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            out, jobs = REPO / ".deep-review/metrics-retries", root / "jobs.json"
            calls, state_dir = root / "calls", root / "attempts"
            active, overlap = root / "active", root / "overlap"
            write_jobs(jobs, ".deep-review/metrics-retries")
            helper = root / "job.py"
            retry_helper_script(helper)
            try:
                result = subprocess.run(
                    runner(out, jobs, helper, calls, workers=2, extra=["--attempts", "2"], helper_suffix=[state_dir, active, overlap]),
                    cwd=REPO, capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertFalse(overlap.exists())
                self.assertEqual(calls.read_text(encoding="utf-8").splitlines(), ["job-1:1", "job-1:2", "job-2:1", "job-2:2"])
                status = json.loads((out / "runs/jobs-status.json").read_text(encoding="utf-8"))
                self.assertEqual([row["attempt"] for row in status["jobs"]], [2, 2])
            finally:
                shutil.rmtree(out, ignore_errors=True)

    def test_drm04_completed_metrics_are_idempotent_and_outputs_resume(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            db, out, jobs = root / "codex.sqlite", REPO / ".deep-review/metrics-idempotent", root / "jobs.json"
            calls, ledger = root / "calls", root / "metrics.json"
            create_db(db)
            write_jobs(jobs, ".deep-review/metrics-idempotent", count=1)
            helper = root / "job.py"
            helper_script(helper)
            try:
                command = runner(out, jobs, helper, calls, db=db, ledger=ledger, workers=1)
                first = subprocess.run(command, cwd=REPO, capture_output=True, text=True)
                second = subprocess.run(command, cwd=REPO, capture_output=True, text=True)
                self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
                self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
                self.assertEqual(calls.read_text(encoding="utf-8").splitlines(), ["job-1"])
                self.assertEqual(read_metrics(ledger)["status"], "complete")
            finally:
                shutil.rmtree(out, ignore_errors=True)

    def test_drm05_content_safe_exact_shape_and_atomic_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            db, ledger = root / "codex.sqlite", root / "metrics.json"
            create_db(db)
            start_metrics(ledger, db, PREFIX, repository="repo", selected_files=1, jobs=1)
            self.assertEqual(stat.S_IMODE(ledger.stat().st_mode), 0o600)
            valid = json.loads(ledger.read_text(encoding="utf-8"))
            for field in ("prompt", "response", "source"):
                malformed = json.loads(json.dumps(valid))
                malformed["usage"] = {"total_tokens": 0, "input_tokens": None, "cached_input_tokens": None, "output_tokens": None, "reasoning_output_tokens": None, field: "secret"}
                ledger.write_text(json.dumps(malformed), encoding="utf-8")
                with self.subTest(field=field), self.assertRaises(TokenMetricsError):
                    read_metrics(ledger)

    def test_drm05_ledger_replace_is_atomic_and_failure_safe(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            db, ledger = root / "codex.sqlite", root / "metrics.json"
            create_db(db)
            start_metrics(ledger, db, PREFIX, repository="repo", selected_files=1, jobs=1)
            before = ledger.read_bytes()
            update_db(db, 10)
            replaced: list[tuple[Path, Path]] = []
            original_replace = token_metrics.os.replace

            def observe_replace(source: str | os.PathLike[str], target: str | os.PathLike[str]) -> None:
                source_path, target_path = Path(source), Path(target)
                self.assertNotEqual(source_path, target_path)
                self.assertEqual(target_path, ledger)
                self.assertEqual(stat.S_IMODE(source_path.stat().st_mode), 0o600)
                replaced.append((source_path, target_path))
                original_replace(source, target)

            with patch.object(token_metrics.os, "replace", observe_replace):
                checkpoint_metrics(ledger, 1)
            self.assertEqual(len(replaced), 1)
            self.assertNotEqual(ledger.read_bytes(), before)

            stable = ledger.read_bytes()

            def fail_replace(source: str | os.PathLike[str], target: str | os.PathLike[str]) -> None:
                raise OSError("simulated replace failure")

            update_db(db, 20)
            with patch.object(token_metrics.os, "replace", fail_replace), self.assertRaises(OSError):
                checkpoint_metrics(ledger, 2)
            self.assertEqual(ledger.read_bytes(), stable)
            self.assertEqual(list(root.glob(f".{ledger.name}.*.tmp")), [])

    def test_drm06_shared_docs_are_provider_neutral(self) -> None:
        skill = (REPO / ".agents/skills/deep-review/SKILL.md").read_text(encoding="utf-8")
        orchestration = (REPO / ".agents/skills/deep-review/references/orchestration.md").read_text(encoding="utf-8")
        policy_lines = [line.lower() for line in (skill + orchestration).splitlines() if "metric" in line.lower() or "token" in line.lower()]
        for line in policy_lines:
            for marker in ("budget", "cap", "stop", "skip", "prevent", "limit", "enforce"):
                self.assertNotIn(marker, line)
        runtime = (REPO / ".agents/skills/deep-review/references/subagent-runtimes.md").read_text(encoding="utf-8").lower()
        runtime_metric_lines = [line for line in runtime.splitlines() if "metric" in line or "token" in line]
        for line in runtime_metric_lines:
            for marker in ("budget", "cap", "stop before", "skip", "prevent", "enforce"):
                self.assertNotIn(marker, line)
        self.assertNotIn("Codex", orchestration)
        self.assertIn("Graft", orchestration)
        self.assertIn("fallback", orchestration.lower())
        self.assertNotIn("parallel(", orchestration)
        native = orchestration.split("**Named native dispatch", 1)[1].split("Metrics are optional", 1)[0].lower()
        self.assertIn("one at a time", native)
        self.assertNotRegex(native, r"parallel|concurr|fan[- ]out|promise\.all")
        graft = " ".join(orchestration.split("When the pinned Graft CLI", 1)[1].split("**Workflow fallback", 1)[0].lower().split())
        self.assertIn("optional", graft)
        self.assertIn("plain repository inspection", graft)
        self.assertIn("does not block review", graft)
        self.assertNotRegex(graft, r"\bmandatory\b|\brequired\b")
        manifest = json.loads((REPO / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["devDependencies"]["@nanonets/graft"], "0.10.1")
        self.assertEqual(manifest["scripts"]["review:graft:build"], "graft build")
        self.assertEqual(manifest["scripts"]["review:graft:version"], "graft --version")

    def test_drm01_native_hooks_are_cumulative_with_serial_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            db, ledger = root / "codex.sqlite", root / "metrics.json"
            create_db(db)
            start_metrics(ledger, db, PREFIX, repository="repo", selected_files=2, jobs=2)
            active = 0
            overlap = False
            completed = 0

            def native_job() -> None:
                nonlocal active, overlap, completed
                active += 1
                overlap = overlap or active > 1
                completed += 1
                update_db(db, completed * 10)
                active -= 1

            for index in range(1, 3):
                native_job()
                checkpoint_metrics(ledger, index)
            finished = finalize_metrics(ledger)
            self.assertFalse(overlap)
            self.assertEqual([row["completed_jobs"] for row in finished["checkpoints"]], [1, 2])
            self.assertEqual(finished["usage"]["total_tokens"], 20)
            self.assertEqual(finished["status"], "complete")

    def test_drm07_explicit_reviewer_path_and_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root, db = Path(raw), Path(raw) / "codex.sqlite"
            create_db(db, 10, PREFIX + "-sibling")
            connection = sqlite3.connect(db)
            connection.execute("insert into threads values (?, ?, ?, ?, ?)", ("child", "", 20, PREFIX + "/child", "secret"))
            connection.commit()
            connection.close()
            snapshot = read_telemetry(db, PREFIX)
            self.assertEqual(snapshot["child"]["total_tokens"], 20)
            self.assertNotIn("thread-1", snapshot)

    def test_drm08_unsupported_host_is_honestly_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            out, jobs, calls = REPO / ".deep-review/metrics-unsupported", root / "jobs.json", root / "calls"
            write_jobs(jobs, ".deep-review/metrics-unsupported", count=1)
            helper = root / "job.py"
            helper_script(helper)
            try:
                result = subprocess.run(runner(out, jobs, helper, calls, workers=1), cwd=REPO, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                artifact = json.loads((out / "runs/review-metrics.json").read_text(encoding="utf-8"))
                self.assertEqual(artifact["status"], "unavailable")
                self.assertNotIn("total_tokens", artifact)
            finally:
                shutil.rmtree(out, ignore_errors=True)

    def test_provider_block_still_writes_blocker_and_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            out, jobs, calls = REPO / ".deep-review/provider-block-test", root / "jobs.json", root / "calls"
            write_jobs(jobs, ".deep-review/provider-block-test", count=1)
            helper = root / "blocked.py"
            helper.write_text("print('usageLimitExceeded')\n", encoding="utf-8")
            shutil.rmtree(out, ignore_errors=True)
            try:
                result = subprocess.run(runner(out, jobs, helper, calls, workers=1), cwd=REPO, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                blocker = json.loads((out / "run-blocker.json").read_text(encoding="utf-8"))
                self.assertEqual(blocker["status"], "blocked")
                self.assertEqual(blocker["pattern"], "usageLimitExceeded")
            finally:
                shutil.rmtree(out, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
