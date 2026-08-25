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
    write_unavailable_metrics,
)
import token_metrics  # noqa: E402
import run_jobs  # noqa: E402
import build_jobs  # noqa: E402
from graft_context import graft_binary, prepare_graft_context  # noqa: E402
import graft_context  # noqa: E402

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


def write_jobs(path: Path, output_dir: str, count: int = 2) -> None:
    path.write_text(json.dumps({"jobs": [
        {"label": f"job-{index}", "kind": "sweep", "lane": "tests", "prompt": str(path.parent / f"p{index}"), "output": f"{output_dir}/job-{index}.json", "required_hunks": [], "rule_ids": []}
        for index in range(1, count + 1)
    ]}), encoding="utf-8")


def write_manifest(out: Path, concurrency: int = 3) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.json").write_text(json.dumps({"concurrency": concurrency}), encoding="utf-8")


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
        "    try: os.unlink(active)\n"
        "    except FileNotFoundError: pass\n"
        "    raise SystemExit(1)\n"
        "json.dump({'defects': [], 'advisories': [], 'suppressions': [], 'coverage': {'hunks': [], 'rules': []}}, open(output, 'w', encoding='utf-8'))\n"
        "try: os.unlink(active)\n"
        "except FileNotFoundError: pass\n",
        encoding="utf-8",
    )
def runner(out: Path, jobs: Path, helper: Path, calls: Path, *, db: Path | None = None, ledger: Path | None = None, extra: list[str] | None = None, helper_suffix: list[Path] | None = None) -> list[str]:
    command = [sys.executable, str(SCRIPTS / "run_jobs.py"), "--out", str(out), "--jobs-file", str(jobs), "--no-freeze-check"]
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
            self.assertEqual(finished["final_snapshot_by_thread"]["thread-1"]["total_tokens"], 180)
            self.assertEqual(finished["final_usage"]["total_tokens"], 180)
            self.assertEqual(
                finished["final_usage"]["total_tokens"] - started["baseline_by_thread"]["thread-1"]["total_tokens"],
                finished["usage"]["total_tokens"],
            )
            self.assertEqual(start_metrics(ledger, db, PREFIX, repository="repo", selected_files=1, jobs=1)["status"], "complete")
            self.assertEqual(started["baseline_by_thread"]["thread-1"]["total_tokens"], 100)
            mutations = (
                ("alter-final-usage", lambda value: value["final_usage"].update({"total_tokens": 181})),
                ("alter-final-snapshot", lambda value: value["final_snapshot_by_thread"]["thread-1"].update({"total_tokens": 181})),
                ("drop-final-usage", lambda value: value.pop("final_usage")),
            )
            for name, mutate in mutations:
                malformed = json.loads(json.dumps(finished))
                mutate(malformed)
                ledger.write_text(json.dumps(malformed), encoding="utf-8")
                with self.subTest(name=name), self.assertRaises(TokenMetricsError):
                    read_metrics(ledger)

    def test_drm02_runner_overlaps_reviewers_at_default_and_explicit_max(self) -> None:
        for concurrency, count in ((3, 3), (6, 6)):
            with self.subTest(concurrency=concurrency), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                db, out, jobs = root / "codex.sqlite", REPO / f".deep-review/metrics-concurrency-{concurrency}", root / "jobs.json"
                calls, active, overlap, ledger = root / "calls", root / "active", root / "overlap", root / "metrics.json"
                create_db(db)
                write_manifest(out, concurrency)
                write_jobs(jobs, f".deep-review/metrics-concurrency-{concurrency}", count=count)
                helper = root / "job.py"
                helper_script(helper, overlap=True)
                try:
                    result = subprocess.run(
                        runner(out, jobs, helper, calls, db=db, ledger=ledger, helper_suffix=[active, overlap]),
                        cwd=REPO, capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertTrue(overlap.exists())
                    status = json.loads((out / "runs/jobs-status.json").read_text(encoding="utf-8"))
                    self.assertEqual([row["label"] for row in status["jobs"]], [f"job-{i}" for i in range(1, count + 1)])
                    metrics = read_metrics(ledger)
                    self.assertEqual(metrics["status"], "complete")
                    self.assertEqual([row["completed_jobs"] for row in metrics["checkpoints"]], list(range(1, count + 1)))
                    self.assertTrue(all("job" not in row for row in metrics["checkpoints"]))
                finally:
                    shutil.rmtree(out, ignore_errors=True)

    def test_drm02_runner_serializes_metrics_checkpoints_in_main_thread(self) -> None:
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
                self.assertCountEqual(calls.read_text(encoding="utf-8").splitlines(), ["job-1", "job-2"])
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
            command = runner(out, jobs, helper, calls, db=db, ledger=ledger)
            old_argv = sys.argv
            try:
                sys.argv = [command[1], *command[2:]]
                with patch.object(run_jobs, "checkpoint_metrics", side_effect=OSError("checkpoint unavailable")):
                    result = run_jobs.main()
                self.assertEqual(result, 0)
                self.assertCountEqual(calls.read_text(encoding="utf-8").splitlines(), ["job-1", "job-2"])
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
            command = runner(out, jobs, helper, calls, db=db, ledger=ledger)
            old_argv = sys.argv
            try:
                sys.argv = [command[1], *command[2:]]
                with patch.object(run_jobs, "finalize_metrics", side_effect=OSError("finalize unavailable")):
                    result = run_jobs.main()
                self.assertEqual(result, 0)
                self.assertCountEqual(calls.read_text(encoding="utf-8").splitlines(), ["job-1", "job-2"])
                status = json.loads((out / "runs/jobs-status.json").read_text(encoding="utf-8"))
                self.assertEqual(status["metrics"], "unavailable")
            finally:
                sys.argv = old_argv
                shutil.rmtree(out, ignore_errors=True)

    def test_drm04_configured_retries_stay_within_worker_slots(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            db, out, jobs = root / "codex.sqlite", REPO / ".deep-review/metrics-retries", root / "jobs.json"
            calls, state_dir, ledger = root / "calls", root / "attempts", root / "metrics.json"
            active, overlap = root / "active", root / "overlap"
            create_db(db)
            write_jobs(jobs, ".deep-review/metrics-retries")
            helper = root / "job.py"
            retry_helper_script(helper)
            try:
                result = subprocess.run(
                    runner(out, jobs, helper, calls, db=db, ledger=ledger, extra=["--attempts", "2"], helper_suffix=[state_dir, active, overlap]),
                    cwd=REPO, capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue(overlap.exists())
                self.assertCountEqual(calls.read_text(encoding="utf-8").splitlines(), ["job-1:1", "job-1:2", "job-2:1", "job-2:2"])
                status = json.loads((out / "runs/jobs-status.json").read_text(encoding="utf-8"))
                self.assertEqual([row["attempt"] for row in status["jobs"]], [2, 2])
                metrics = read_metrics(ledger)
                self.assertEqual(metrics["status"], "complete")
                self.assertEqual(metrics["usage"]["total_tokens"], 0)
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
                command = runner(out, jobs, helper, calls, db=db, ledger=ledger)
                first = subprocess.run(command, cwd=REPO, capture_output=True, text=True)
                second = subprocess.run(command, cwd=REPO, capture_output=True, text=True)
                self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
                self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
                self.assertEqual(calls.read_text(encoding="utf-8").splitlines(), ["job-1"])
                self.assertEqual(read_metrics(ledger)["status"], "complete")
            finally:
                shutil.rmtree(out, ignore_errors=True)

    def test_drm04_selective_resume_finalizes_full_scope_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            db, out, jobs = root / "codex.sqlite", REPO / ".deep-review/metrics-selective-resume", root / "jobs.json"
            calls, ledger = root / "calls", root / "metrics.json"
            create_db(db)
            write_jobs(jobs, ".deep-review/metrics-selective-resume")
            helper = root / "job.py"
            helper_script(helper)
            try:
                start_metrics(ledger, db, PREFIX, repository=str(REPO), selected_files=2, jobs=2)
                update_db(db, 10)
                first = subprocess.run(
                    runner(out, jobs, helper, calls, db=db, ledger=ledger, extra=["--only", "job-1"]),
                    cwd=REPO, capture_output=True, text=True,
                )
                self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
                partial = read_metrics(ledger)
                self.assertEqual(partial["status"], "running")
                self.assertEqual([row["completed_jobs"] for row in partial["checkpoints"]], [1])

                update_db(db, 30)
                second = subprocess.run(
                    runner(out, jobs, helper, calls, db=db, ledger=ledger, extra=["--only", "job-2"]),
                    cwd=REPO, capture_output=True, text=True,
                )
                self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
                finished = read_metrics(ledger)
                self.assertEqual(finished["status"], "complete")
                self.assertEqual(finished["usage"]["total_tokens"], 30)
                self.assertEqual([row["completed_jobs"] for row in finished["checkpoints"]], [1, 2])
                self.assertEqual(calls.read_text(encoding="utf-8").splitlines(), ["job-1", "job-2"])
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

    def test_drm05_unavailable_ledger_keeps_exact_content_safe_shape(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root, ledger = Path(raw), Path(raw) / "metrics.json"
            write_unavailable_metrics(ledger)
            valid = json.loads(ledger.read_text(encoding="utf-8"))
            mutations = {
                "scope-extra": lambda value: value["scope"].update({"prompt": "secret"}),
                "schema-version": lambda value: value.update({"schema_version": 2}),
                "runtime-db-shape": lambda value: value.update({"runtime_db": {"source": "secret"}}),
                "top-level-extra": lambda value: value.update({"response": "secret"}),
            }
            for name, mutate in mutations.items():
                malformed = json.loads(json.dumps(valid))
                mutate(malformed)
                ledger.write_text(json.dumps(malformed), encoding="utf-8")
                with self.subTest(name=name), self.assertRaises(TokenMetricsError):
                    read_metrics(ledger)

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
        self.assertIn("manifest concurrency", native)
        self.assertIn("active attempts", native)
        self.assertNotIn("one at a time", native)
        self.assertRegex(native, r"concurr|refill|worker slot")
        graft = " ".join(orchestration.split("Before prompts are materialized", 1)[1].split("**Workflow fallback", 1)[0].lower().split())
        self.assertIn("optional", graft)
        self.assertIn("plain repository inspection", graft)
        self.assertIn("does not block review", graft)
        self.assertNotRegex(graft, r"\bmandatory\b|\brequired\b")
        manifest = json.loads((REPO / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["devDependencies"]["@nanonets/graft"], "0.10.1")
        self.assertEqual(manifest["scripts"]["review:graft:build"], "graft build")
        self.assertEqual(manifest["scripts"]["review:graft:version"], "graft --version")

    def test_drm06_build_jobs_wires_graft_context_and_dot_fallback(self) -> None:
        (REPO / ".deep-review").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=REPO / ".deep-review") as raw:
            out = Path(raw)
            manifest = {
                "target": "fixture",
                "base": "base",
                "diff_command": "git diff base..HEAD -- <file>",
                "files": [{
                    "path": "tools/test_deep_review_token_metrics.py", "status": "M",
                    "adds": 1, "dels": 0, "disposition": "selected",
                    "hunks": [{"start": 1, "lines": 1, "side": "new"}],
                }],
            }
            (out / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (out / "knowledge.json").write_text(json.dumps({"selected_paths": [manifest["files"][0]["path"]], "sources": []}), encoding="utf-8")
            (out / "rules.json").write_text(json.dumps({"sources": [], "rules": []}), encoding="utf-8")
            (out / "context-pack.md").write_text("# Context\n", encoding="utf-8")
            (out / "plan.json").write_text(json.dumps({
                "cohorts": [{"id": "c01", "name": "fixture", "risk": "normal", "files": [manifest["files"][0]["path"]]}],
                "sweeps": [],
            }), encoding="utf-8")
            old_argv = sys.argv
            try:
                sys.argv = ["build_jobs.py", "--out", str(out)]
                self.assertEqual(build_jobs.main(), 0)
            finally:
                sys.argv = old_argv
            prompt = (out / "prompts/cohort-c01.md").read_text(encoding="utf-8")
            self.assertIn("GRAFT CONTEXT", prompt)
            graft_path = out / "graft-context.md"
            self.assertIn("graft-context.md", prompt)
            if graft_binary(REPO):
                self.assertIn("Repository map", graft_path.read_text(encoding="utf-8"))

            dot_context = prepare_graft_context(REPO, out / "dot", [".agents/skills/deep-review/SKILL.md"])
            self.assertEqual(dot_context["status"], "ready-with-fallback" if graft_binary(REPO) else "fallback")
            self.assertIn("plain repository inspection", (out / "dot/graft-context.md").read_text(encoding="utf-8"))

            failing = out / "failing-graft"
            failing.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
            failing.chmod(0o700)
            with patch.object(graft_context, "graft_binary", return_value=str(failing)):
                failed_context = prepare_graft_context(REPO, out / "failed", ["tools/test_deep_review_token_metrics.py"])
            self.assertEqual(failed_context["status"], "fallback")
            self.assertIn("plain repository inspection", (out / "failed/graft-context.md").read_text(encoding="utf-8"))

    def test_drm06_graft_never_uses_global_path_binary(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake_repo, fake_bin, marker = root / "repo", root / "bin", root / "invoked"
            fake_repo.mkdir()
            fake_bin.mkdir()
            attacker = fake_bin / "graft"
            attacker.write_text(f"#!/bin/sh\ntouch {marker}\n", encoding="utf-8")
            attacker.chmod(0o700)
            with patch.dict(os.environ, {"PATH": str(fake_bin)}):
                self.assertIsNone(graft_binary(fake_repo))
                context = prepare_graft_context(fake_repo, root / "out", ["src/app.py"])
            self.assertEqual(context["status"], "fallback")
            self.assertFalse(marker.exists())

    def test_drm06_graft_later_failures_are_nonblocking(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for name, failure, expected in (("map", "map", "Graft map failed"), ("symbols", "ask", "symbol lookup failed"), ("callers", "callers", "blast-radius lookup failed")):
                script = root / f"graft-{name}.py"
                log = root / f"{name}.log"
                script.write_text(
                    "#!/usr/bin/env python3\n"
                    "import json, pathlib, sys\n"
                    f"pathlib.Path({str(log)!r}).open('a').write(sys.argv[1] + '\\n')\n"
                    f"if sys.argv[1] == {failure!r}: sys.exit(1)\n"
                    "if sys.argv[1] == 'ask': print(json.dumps({'hits': [{'kind': 'symbol', 'title': 'main · function'}]}))\n"
                    "else: print('{}')\n",
                    encoding="utf-8",
                )
                script.chmod(0o700)
                with patch.object(graft_context, "graft_binary", return_value=str(script)):
                    context = prepare_graft_context(REPO, root / name, ["tools/test_deep_review_token_metrics.py"])
                self.assertIn(context["status"], {"fallback", "ready-with-fallback"})
                self.assertIn(expected, (root / name / "graft-context.md").read_text(encoding="utf-8"))
                self.assertIn("build", log.read_text(encoding="utf-8"))

    def test_drm01_metrics_hooks_are_cumulative_without_job_attribution(self) -> None:
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
                result = subprocess.run(runner(out, jobs, helper, calls), cwd=REPO, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                artifact = json.loads((out / "runs/review-metrics.json").read_text(encoding="utf-8"))
                self.assertEqual(artifact["status"], "unavailable")
                self.assertNotIn("total_tokens", artifact)
            finally:
                shutil.rmtree(out, ignore_errors=True)

    def test_provider_block_with_metrics_still_writes_blocker_and_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            db, out, jobs = root / "codex.sqlite", REPO / ".deep-review/provider-block-test", root / "jobs.json"
            calls, ledger = root / "calls", root / "metrics.json"
            create_db(db)
            write_jobs(jobs, ".deep-review/provider-block-test", count=1)
            helper = root / "blocked.py"
            helper.write_text("print('usageLimitExceeded')\n", encoding="utf-8")
            shutil.rmtree(out, ignore_errors=True)
            try:
                result = subprocess.run(runner(out, jobs, helper, calls, db=db, ledger=ledger), cwd=REPO, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                blocker = json.loads((out / "run-blocker.json").read_text(encoding="utf-8"))
                self.assertEqual(blocker["status"], "blocked")
                self.assertEqual(blocker["pattern"], "usageLimitExceeded")
                metrics = read_metrics(ledger)
                self.assertEqual(metrics["status"], "running")
            finally:
                shutil.rmtree(out, ignore_errors=True)

    def test_provider_block_finishes_active_jobs_and_resume_skips_valid_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            out, jobs = REPO / ".deep-review/provider-block-concurrent", root / "jobs.json"
            calls, marker = root / "calls", root / "block-once"
            write_manifest(out, 2)
            write_jobs(jobs, ".deep-review/provider-block-concurrent", count=4)
            helper = root / "block-once.py"
            helper.write_text(
                "import json, pathlib, sys, time\n"
                "prompt, output, label, calls, marker = sys.argv[1:]\n"
                "with open(calls, 'a', encoding='utf-8') as stream: stream.write(label + '\\n')\n"
                "if label == 'job-1' and not pathlib.Path(marker).exists():\n"
                "    pathlib.Path(marker).touch()\n"
                "    print('usageLimitExceeded')\n"
                "    raise SystemExit(1)\n"
                "time.sleep(0.08)\n"
                "json.dump({'defects': [], 'advisories': [], 'suppressions': [], 'coverage': {'hunks': [], 'rules': []}}, open(output, 'w', encoding='utf-8'))\n",
                encoding="utf-8",
            )
            try:
                first = subprocess.run(
                    runner(out, jobs, helper, calls, extra=["--attempts", "1"], helper_suffix=[marker]),
                    cwd=REPO, capture_output=True, text=True,
                )
                self.assertEqual(first.returncode, 2, first.stdout + first.stderr)
                self.assertCountEqual(calls.read_text(encoding="utf-8").splitlines(), ["job-1", "job-2"])
                blocker = json.loads((out / "run-blocker.json").read_text(encoding="utf-8"))
                self.assertEqual(blocker["pending"], ["job-1", "job-3", "job-4"])
                status = json.loads((out / "runs/jobs-status.json").read_text(encoding="utf-8"))
                self.assertEqual([row["label"] for row in status["jobs"]], ["job-1", "job-2", "job-3", "job-4"])

                second = subprocess.run(
                    runner(out, jobs, helper, calls, extra=["--attempts", "1"], helper_suffix=[marker]),
                    cwd=REPO, capture_output=True, text=True,
                )
                self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
                self.assertCountEqual(calls.read_text(encoding="utf-8").splitlines(), ["job-1", "job-2", "job-1", "job-3", "job-4"])
            finally:
                shutil.rmtree(out, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
