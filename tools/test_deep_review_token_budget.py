"""Contract tests for the deep-review token ledger and public runner."""

from __future__ import annotations

import json
import sqlite3
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / ".agents/skills/deep-review/scripts"
sys.path.insert(0, str(SCRIPTS))

from token_budget import (  # noqa: E402
    DEFAULT_BUDGET_TOKENS,
    TokenBudgetError,
    checkpoint_ledger,
    delta_usage,
    read_ledger,
    start_ledger,
    write_unmetered_fallback,
)


PREFIX = "/reviewer/deep-review"


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


class TokenBudgetTests(unittest.TestCase):
    def test_snapshot_delta_uses_post_snapshot_and_does_not_double_count(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            db = root / "codex.sqlite"
            state = root / "ledger.json"
            create_db(db, 100)
            started = start_ledger(state, db, PREFIX, selected_files=1, jobs=1)
            update_db(db, 160)
            checked = checkpoint_ledger(state, "job-1")
            self.assertEqual(started["budget_tokens"], DEFAULT_BUDGET_TOKENS)
            self.assertEqual(checked["usage"]["total_tokens"], 60)
            self.assertNotIn("secret prompt", state.read_text(encoding="utf-8"))
            self.assertEqual(delta_usage(started["baseline_by_thread"], {"thread-1": {"total_tokens": 160, "input_tokens": None, "cached_input_tokens": None, "output_tokens": None, "reasoning_output_tokens": None}})["total_tokens"], 60)
            resumed = start_ledger(state, db, PREFIX, selected_files=1, jobs=1)
            self.assertEqual(resumed["usage"]["total_tokens"], 60)
            update_db(db, 180)
            self.assertEqual(checkpoint_ledger(state, "job-2")["usage"]["total_tokens"], 80)

    def test_checkpoint_crossing_budget_is_persisted(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            db = root / "codex.sqlite"
            state = root / "ledger.json"
            create_db(db)
            start_ledger(state, db, PREFIX, budget=100, jobs=2)
            update_db(db, 100)
            checked = checkpoint_ledger(state, "job-1")
            self.assertEqual(checked["status"], "budget_exhausted")
            self.assertEqual(read_ledger(state)["checkpoints"][0]["job"], "job-1")

    def test_lower_counter_and_invalid_ledger_fail_closed_without_rewrite(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            db = root / "codex.sqlite"
            state = root / "ledger.json"
            create_db(db, 100)
            start_ledger(state, db, PREFIX, jobs=1)
            update_db(db, 120)
            checkpoint_ledger(state, "job-1")
            update_db(db, 110)
            before = state.read_text(encoding="utf-8")
            with self.assertRaises(TokenBudgetError):
                checkpoint_ledger(state, "job-2")
            self.assertEqual(state.read_text(encoding="utf-8"), before)
            malformed = json.loads(before)
            malformed["scope"]["prompt"] = "secret"
            state.write_text(json.dumps(malformed), encoding="utf-8")
            with self.assertRaises(TokenBudgetError):
                read_ledger(state)

    def test_fallback_is_explicitly_unmetered_and_content_safe(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            state = Path(raw) / "fallback.json"
            write_unmetered_fallback(state)
            payload = state.read_text(encoding="utf-8")
            self.assertEqual(json.loads(payload)["status"], "unmetered")
            self.assertNotIn("prompt", payload)
            self.assertNotIn("response", payload)

    def test_public_runner_preserves_first_output_and_skips_second_at_budget(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            db = root / "codex.sqlite"
            create_db(db)
            out = Path.cwd() / ".deep-review" / "token-budget-test"
            jobs = root / "jobs.json"
            ledger = root / "ledger.json"
            helper = root / "job.py"
            calls = root / "calls.txt"
            helper.write_text(
                "import json, sqlite3, sys\n"
                "prompt, output, db, label, calls = sys.argv[1:]\n"
                "with open(calls, 'a', encoding='utf-8') as f: f.write(label + '\\n')\n"
                "with open(output, 'w', encoding='utf-8') as f: json.dump({'defects': [], 'advisories': [], 'suppressions': [], 'coverage': {'hunks': [], 'rules': []}}, f)\n"
                "conn = sqlite3.connect(db); conn.execute('update threads set tokens_used = 100'); conn.commit(); conn.close()\n",
                encoding="utf-8",
            )
            jobs.write_text(json.dumps({"jobs": [
                {"label": "job-1", "kind": "sweep", "lane": "tests", "prompt": str(root / "p1"), "output": ".deep-review/token-budget-test/job-1.json", "required_hunks": [], "rule_ids": []},
                {"label": "job-2", "kind": "sweep", "lane": "tests", "prompt": str(root / "p2"), "output": ".deep-review/token-budget-test/job-2.json", "required_hunks": [], "rule_ids": []},
            ]}), encoding="utf-8")
            try:
                command = [
                    sys.executable, str(SCRIPTS / "run_jobs.py"), "--out", str(out), "--jobs-file", str(jobs),
                    "--command", f"{sys.executable} {helper} {{prompt}} {{output}} {db} {{label}} {calls}",
                    "--metered", "--token-db", str(db), "--token-ledger", str(ledger), "--budget", "100", "--no-freeze-check",
                ]
                result = subprocess.run(command, cwd=Path.cwd(), capture_output=True, text=True)
                self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                self.assertEqual(calls.read_text(encoding="utf-8").splitlines(), ["job-1"])
                self.assertTrue((Path.cwd() / ".deep-review/token-budget-test/job-1.json").is_file())
                self.assertFalse((Path.cwd() / ".deep-review/token-budget-test/job-2.json").exists())
                persisted = json.loads(ledger.read_text(encoding="utf-8"))
                self.assertEqual(persisted["status"], "budget_exhausted")
                self.assertEqual([row["job"] for row in persisted["checkpoints"]], ["job-1"])

                fallback_out = Path.cwd() / ".deep-review" / "token-budget-fallback-test"
                fallback_jobs = root / "fallback-jobs.json"
                fallback_calls = root / "fallback-calls.txt"
                fallback_jobs.write_text(
                    json.dumps({"jobs": [
                        {"label": "job-1", "kind": "sweep", "lane": "tests", "prompt": str(root / "p1"), "output": ".deep-review/token-budget-fallback-test/job-1.json", "required_hunks": [], "rule_ids": []},
                        {"label": "job-2", "kind": "sweep", "lane": "tests", "prompt": str(root / "p2"), "output": ".deep-review/token-budget-fallback-test/job-2.json", "required_hunks": [], "rule_ids": []},
                    ]}), encoding="utf-8")
                fallback = subprocess.run(
                    [sys.executable, str(SCRIPTS / "run_jobs.py"), "--out", str(fallback_out), "--jobs-file", str(fallback_jobs), "--workers", "4", "--command", f"{sys.executable} {helper} {{prompt}} {{output}} {db} {{label}} {fallback_calls}", "--no-freeze-check"],
                    cwd=Path.cwd(), capture_output=True, text=True,
                )
                self.assertEqual(fallback.returncode, 0, fallback.stdout + fallback.stderr)
                self.assertEqual(fallback_calls.read_text(encoding="utf-8").splitlines(), ["job-1", "job-2"])
                self.assertEqual(json.loads((fallback_out / "runs/token-ledger.json").read_text(encoding="utf-8"))["status"], "unmetered")

                blocked_out = Path.cwd() / ".deep-review" / "token-budget-invalid-test"
                blocked_jobs = root / "blocked-jobs.json"
                blocked_calls = root / "blocked-calls.txt"
                blocked_jobs.write_text(
                    json.dumps({"jobs": [{"label": "job-1", "kind": "sweep", "lane": "tests", "prompt": str(root / "p1"), "output": ".deep-review/token-budget-invalid-test/job-1.json", "required_hunks": [], "rule_ids": []}]}),
                    encoding="utf-8",
                )
                invalid = subprocess.run(
                    [sys.executable, str(SCRIPTS / "run_jobs.py"), "--out", str(blocked_out), "--jobs-file", str(blocked_jobs), "--command", f"{sys.executable} {helper} {{prompt}} {{output}} {db} {{label}} {blocked_calls}", "--metered", "--token-db", str(root / "missing.sqlite"), "--no-freeze-check"],
                    cwd=Path.cwd(), capture_output=True, text=True,
                )
                self.assertEqual(invalid.returncode, 2)
                self.assertFalse(blocked_calls.exists())
                self.assertNotIn("sqlite", invalid.stdout.lower() + invalid.stderr.lower())
            finally:
                shutil.rmtree(out, ignore_errors=True)
                shutil.rmtree(Path.cwd() / ".deep-review/token-budget-fallback-test", ignore_errors=True)
                shutil.rmtree(Path.cwd() / ".deep-review/token-budget-invalid-test", ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
