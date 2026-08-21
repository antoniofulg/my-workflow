#!/usr/bin/env python3
"""Deep-review job runner/validator (mutating helper; writes only under --out).

One resumable engine for every job kind (defect cohort, polish, sweep). Two modes:

  --validate-only            Report each job as VALID / PENDING / INVALID and
                             refresh the status file. This is how Workflow- and
                             Agent-driven rounds resume: dispatch only what is
                             not VALID, then re-run this mode until exit 0.
  --command '<template>'     Execute pending jobs via a subprocess per job
                             ({prompt} required; {output} and {label} optional
                             placeholders), bounded workers, output validation,
                             retries, and provider-block detection.

Valid outputs are always preserved — re-running never repeats finished work.
The source freeze is checked before and after execution (--no-freeze-check to
skip). Exit codes: 0 all jobs valid, 1 failures/pending remain, 2 blocked by a
provider limit or invalid metering state, 3 either source drift or a metered
budget stop. A budget stop persists `budget_exhausted` in the token ledger and
preserves the round; it is not a source-drift restart signal.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import threading
from pathlib import Path

sys.dont_write_bytecode = True  # keep the tracked skill tree free of __pycache__

from _common import check_freeze, load_jobs, read_json, repo_root, validate_job_output, write_json
from token_budget import (
    DEFAULT_BUDGET_TOKENS,
    TokenBudgetError,
    checkpoint_ledger,
    finalize_ledger,
    start_ledger,
    validate_ledger_telemetry,
    write_unmetered_fallback,
)

PRINT_LOCK = threading.Lock()
STOP_EVENT = threading.Event()
STOP_REASON: dict[str, str] = {}


def say(message: str) -> None:
    with PRINT_LOCK:
        print(message, flush=True)


def job_state(repo: Path, out: Path, job: dict) -> tuple[str, str]:
    if not (repo / job["output"]).is_file():
        return "pending", "missing output"
    try:
        validate_job_output(repo, out, job)
    except ValueError as error:
        return "invalid", str(error)
    return "valid", ""


def render_command(template: str, job: dict, repo: Path) -> list[str]:
    tokens = shlex.split(template)
    substituted = [
        token.replace("{prompt}", job["prompt"])
        .replace("{output}", job["output"])
        .replace("{label}", job["label"])
        for token in tokens
    ]
    return substituted


def run_one(repo: Path, out: Path, job: dict, args) -> dict:
    label = job["label"]
    output = repo / job["output"]
    state, _ = job_state(repo, out, job)
    if state == "valid":
        say(f"SKIP {label} existing-valid-output")
        return {"label": label, "status": "pass", "attempt": 0, "preserved": True}

    runs_dir = out / "runs"
    last_error, exit_code = "not run", None
    for attempt in range(1, args.attempts + 1):
        if STOP_EVENT.is_set():
            return {"label": label, "status": "blocked", "attempt": attempt - 1,
                    "error": STOP_REASON.get("reason", "run stopped")}
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            output.unlink()
        stdout_path = runs_dir / f"{label}.attempt-{attempt}.events.jsonl"
        stderr_path = runs_dir / f"{label}.attempt-{attempt}.err"
        command = render_command(args.command, job, repo)
        with stdout_path.open("w", encoding="utf-8") as out_file, stderr_path.open(
            "w", encoding="utf-8"
        ) as err_file:
            try:
                completed = subprocess.run(
                    command, cwd=repo, stdout=out_file, stderr=err_file,
                    check=False, timeout=args.timeout_min * 60,
                )
                exit_code = completed.returncode
            except subprocess.TimeoutExpired:
                exit_code = None
                last_error = f"runner timeout after {args.timeout_min}m"
                say(f"RETRY {label} attempt={attempt} reason={last_error}")
                continue
        streams = (
            stdout_path.read_text(encoding="utf-8", errors="replace")
            + stderr_path.read_text(encoding="utf-8", errors="replace")
        )
        blocked_on = next((pattern for pattern in args.block_on if pattern in streams), None)
        if blocked_on:
            STOP_EVENT.set()
            STOP_REASON.setdefault("reason", blocked_on)
            STOP_REASON.setdefault("label", label)
            say(f"BLOCKED {label} pattern={blocked_on}")
            return {"label": label, "status": "blocked", "attempt": attempt,
                    "exit_code": exit_code, "error": blocked_on}
        if exit_code != 0:
            last_error = f"command exit {exit_code}"
        else:
            state, reason = job_state(repo, out, job)
            if state == "valid":
                say(f"PASS {label} attempt={attempt}")
                return {"label": label, "status": "pass", "attempt": attempt, "exit_code": 0}
            last_error = reason or "output invalid"
        say(f"RETRY {label} attempt={attempt} reason={last_error}")
    return {"label": label, "status": "fail", "attempt": args.attempts,
            "exit_code": exit_code, "error": last_error}


def stage_report(repo: Path, out: Path, jobs: list[dict]) -> tuple[int, list[dict]]:
    pending = []
    for job in jobs:
        state, reason = job_state(repo, out, job)
        if state != "valid":
            pending.append({"label": job["label"], "state": state, "reason": reason})
    return len(jobs) - len(pending), pending


def token_ledger_path(args, out: Path) -> Path:
    return Path(args.token_ledger).resolve() if args.token_ledger else out / "runs" / "token-ledger.json"


def token_metering(args, out: Path, jobs: list[dict]) -> tuple[str, Path | None, dict | None]:
    """Start strict metering when requested; otherwise record an honest fallback."""
    ledger_path = token_ledger_path(args, out)
    strict = args.metered or args.token_db is not None or args.token_ledger is not None
    if not strict:
        write_unmetered_fallback(ledger_path)
        return "unmetered", None, None
    try:
        ledger = start_ledger(
            ledger_path,
            args.token_db or default_token_db(),
            args.reviewer_prefix,
            args.budget_tokens,
            repository=str(repo_root()),
            round=args.round,
            base=args.base,
            head=args.head,
            selected_files=args.selected_files or len(jobs),
            carried_files=args.carried_files,
            jobs=len(jobs),
            model=args.model,
            reasoning=args.reasoning,
        )
    except TokenBudgetError as error:
        raise error
    return "metered", ledger_path, ledger


def default_token_db() -> str:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    return str(codex_home / "state_5.sqlite")


def run_metered_jobs(repo: Path, out: Path, jobs: list[dict], args, ledger_path: Path, ledger: dict) -> tuple[list[dict], bool, str | None]:
    """Run exactly one job, checkpoint it, then decide whether another may start."""
    results: list[dict] = []
    budget_exhausted = ledger["status"] == "budget_exhausted"
    error: str | None = None
    checkpointed = {row["job"] for row in ledger["checkpoints"]}
    if budget_exhausted:
        return results, True, None
    for job in jobs:
        try:
            ledger = validate_ledger_telemetry(ledger_path)
        except TokenBudgetError as failure:
            error = str(failure)
            break
        if ledger["status"] == "budget_exhausted":
            budget_exhausted = True
            break
        result = run_one(repo, out, job, args)
        results.append(result)
        if result["status"] != "pass":
            if result["status"] == "blocked":
                break
            continue
        if job["label"] not in checkpointed:
            try:
                ledger = checkpoint_ledger(ledger_path, job["label"])
            except TokenBudgetError as failure:
                error = str(failure)
                break
            checkpointed.add(job["label"])
            result["token_usage"] = ledger["usage"]["total_tokens"]
        if ledger["status"] == "budget_exhausted":
            budget_exhausted = True
            break
    if error is None and not budget_exhausted and not any(item["status"] == "fail" for item in results):
        try:
            ledger = finalize_ledger(ledger_path)
            budget_exhausted = ledger["status"] == "budget_exhausted"
        except TokenBudgetError as failure:
            error = str(failure)
    return results, budget_exhausted, error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True)
    parser.add_argument("--jobs-file", help="default: <out>/jobs.json")
    parser.add_argument("--only", nargs="*", help="exact job labels to consider")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--command", help="subprocess template; {prompt} required, {output}/{label} optional")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--timeout-min", type=int, default=35)
    parser.add_argument("--block-on", action="append", default=None,
                        help="abort-the-run substring (repeatable); default: usageLimitExceeded")
    parser.add_argument("--status-file", help="default: <out>/runs/<jobs-stem>-status.json")
    parser.add_argument("--no-freeze-check", action="store_true")
    parser.add_argument("--metered", action="store_true", help="require compatible Codex telemetry and enforce the token budget")
    parser.add_argument("--token-db", help="Codex state SQLite path")
    parser.add_argument("--token-ledger", "--ledger", help="content-safe token ledger path")
    parser.add_argument("--reviewer-prefix", default="/reviewer/deep-review")
    parser.add_argument("--budget-tokens", "--token-budget", "--budget", dest="budget_tokens", type=int, default=DEFAULT_BUDGET_TOKENS)
    parser.add_argument("--round", type=int, default=0)
    parser.add_argument("--base", default="unknown")
    parser.add_argument("--head", default="unknown")
    parser.add_argument("--selected-files", type=int)
    parser.add_argument("--carried-files", type=int, default=0)
    parser.add_argument("--model", default="unknown")
    parser.add_argument("--reasoning", default="unknown")
    args = parser.parse_args()
    if bool(args.validate_only) == bool(args.command):
        parser.error("pass exactly one of --validate-only or --command")
    if not 1 <= args.workers <= 6:
        parser.error("--workers must be between 1 and 6")
    if not 1 <= args.attempts <= 3:
        parser.error("--attempts must be between 1 and 3")
    if args.command and "{prompt}" not in args.command:
        parser.error("--command must contain the {prompt} placeholder")
    args.block_on = args.block_on or ["usageLimitExceeded"]
    STOP_EVENT.clear()
    STOP_REASON.clear()

    repo = repo_root()
    out = Path(args.out).resolve()
    jobs_path = Path(args.jobs_file).resolve() if args.jobs_file else out / "jobs.json"
    try:
        jobs = load_jobs(jobs_path)
    except RuntimeError as error:
        sys.stderr.write(f"{error}\n")
        return 1
    if args.only:
        unknown = set(args.only) - {job["label"] for job in jobs}
        if unknown:
            parser.error(f"unknown jobs: {sorted(unknown)}")
        jobs = [job for job in jobs if job["label"] in args.only]

    status_path = (
        Path(args.status_file).resolve() if args.status_file
        else out / "runs" / f"{jobs_path.stem}-status.json"
    )

    if args.validate_only:
        rows = []
        for job in jobs:
            state, reason = job_state(repo, out, job)
            row = {"label": job["label"], "status": state, "reason": reason or None}
            if state != "valid":  # pending rows carry the dispatch contract for the engines
                row["prompt"], row["output"] = job["prompt"], job["output"]
            rows.append(row)
            say(f"{state.upper()} {job['label']}" + (f" — {reason}" if reason else ""))
        write_json(status_path, {"mode": "validate", "jobs": rows})
        pending = [row for row in rows if row["status"] != "valid"]
        say(f"SUMMARY valid={len(rows) - len(pending)} pending={len(pending)} of {len(rows)}")
        return 0 if not pending else 1

    drift: list[str] = []
    if not args.no_freeze_check:
        try:
            drift = check_freeze(repo, out, "before run")
        except RuntimeError as error:
            sys.stderr.write(f"{error}\n")
            return 1
        if drift:
            sys.stderr.write(drift[0] + "\n")
            return 3

    (out / "runs").mkdir(parents=True, exist_ok=True)
    try:
        metering, ledger_path, ledger = token_metering(args, out, jobs)
    except TokenBudgetError as error:
        say(f"METERED unavailable: {error}")
        write_json(out / "runs" / "token-budget-status.json", {"status": "blocked", "metering": "metered", "error": str(error)})
        return 2

    budget_exhausted = False
    token_error: str | None = None
    if metering == "metered":
        args.workers = 1
        say("METERED sequential workers=1")
        results, budget_exhausted, token_error = run_metered_jobs(repo, out, jobs, args, ledger_path, ledger)
    else:
        args.workers = 1
        say("UNMETERED sequential workers=1")
        results = [run_one(repo, out, job, args) for job in jobs]
        for result in results:
            if result["status"] == "fail":
                say(f"FAIL {result['label']}: {result['error']}")

    valid_count, pending = stage_report(repo, out, jobs)
    failed = [item for item in results if item["status"] == "fail"]
    blocked = [item for item in results if item["status"] == "blocked"]
    write_json(status_path, {
        "mode": "run", "metering": metering,
        "token_ledger": str(ledger_path) if ledger_path else None,
        "jobs": results,
        "summary": {"pass": len(results) - len(failed) - len(blocked),
                    "fail": len(failed), "blocked": len(blocked),
                    "stage_valid": valid_count, "stage_total": len(jobs)},
    })
    if token_error:
        write_json(out / "runs" / "token-budget-status.json", {"status": "blocked", "metering": "metered", "error": token_error})
    if blocked:
        write_json(out / "run-blocker.json", {
            "status": "blocked",
            "pattern": STOP_REASON.get("reason"),
            "first_label": STOP_REASON.get("label"),
            "jobs_file": str(jobs_path),
            "valid_outputs": valid_count,
            "total_jobs": len(jobs),
            "pending": [row["label"] for row in pending],
        })
    say(f"SUMMARY pass={len(results) - len(failed) - len(blocked)} fail={len(failed)} "
        f"blocked={len(blocked)}; stage {valid_count}/{len(jobs)} outputs valid")

    if not args.no_freeze_check:
        try:
            drift = check_freeze(repo, out, "after run")
        except RuntimeError as error:
            sys.stderr.write(f"{error}\n")
            return 1
        if drift:
            sys.stderr.write(drift[0] + "\n")
            return 3
    if token_error:
        say(f"METERED blocked: {token_error}")
        return 2
    if budget_exhausted:
        say("METERED budget exhausted; remaining jobs were not started")
        return 3
    if blocked:
        say(f"resume: rerun this command after the limit clears — see {out / 'run-blocker.json'}")
        return 2
    return 1 if failed or pending else 0


if __name__ == "__main__":
    sys.exit(main())
