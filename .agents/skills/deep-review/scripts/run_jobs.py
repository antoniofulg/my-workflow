#!/usr/bin/env python3
"""Deep-review job runner/validator (mutating helper; writes only under --out).

  --validate-only            Report each job as VALID / PENDING / INVALID.
  --command '<template>'     Execute pending jobs with bounded concurrency and retries,
                             output validation, and provider-block detection.

Valid outputs are preserved and resumed. Optional metrics observe the run without
changing dispatch, output ordering, retries, or exit behavior. Exit codes are 0 for
valid outputs, 1 for failures/pending outputs, 2 for provider blocks, and 3 for
source drift.
"""

from __future__ import annotations

import argparse
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import json
import shlex
import subprocess
import sys
import threading
from pathlib import Path

sys.dont_write_bytecode = True

from _common import check_freeze, load_jobs, repo_root, validate_job_output, write_json
from token_metrics import (
    checkpoint_metrics,
    finalize_metrics,
    start_metrics,
    write_unavailable_metrics,
)

PRINT_LOCK = threading.Lock()
STOP_EVENT = threading.Event()
STOP_REASON: dict[str, str] = {}
STOP_LOCK = threading.Lock()


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


def manifest_concurrency(out: Path) -> int:
    """Read the frozen scheduler bound; old fixtures without it use the default."""
    manifest_path = out / "manifest.json"
    if not manifest_path.is_file():
        return 3
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"cannot read manifest concurrency: {error}") from error
    value = manifest.get("concurrency", 3)
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 6:
        raise RuntimeError("manifest concurrency must be an integer from 1 through 6")
    return value


def record_block(label: str, reason: str) -> None:
    with STOP_LOCK:
        STOP_EVENT.set()
        STOP_REASON.setdefault("reason", reason)
        STOP_REASON.setdefault("label", label)


def render_command(template: str, job: dict) -> list[str]:
    return [
        token.replace("{prompt}", job["prompt"])
        .replace("{output}", job["output"])
        .replace("{label}", job["label"])
        for token in shlex.split(template)
    ]


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
        with stdout_path.open("w", encoding="utf-8") as out_file, stderr_path.open("w", encoding="utf-8") as err_file:
            try:
                completed = subprocess.run(
                    render_command(args.command, job), cwd=repo, stdout=out_file, stderr=err_file,
                    check=False, timeout=args.timeout_min * 60,
                )
                exit_code = completed.returncode
            except subprocess.TimeoutExpired:
                exit_code = None
                last_error = f"runner timeout after {args.timeout_min}m"
                say(f"RETRY {label} attempt={attempt} reason={last_error}")
                continue
        streams = stdout_path.read_text(encoding="utf-8", errors="replace") + stderr_path.read_text(encoding="utf-8", errors="replace")
        blocked_on = next((pattern for pattern in args.block_on if pattern in streams), None)
        if blocked_on:
            record_block(label, blocked_on)
            say(f"BLOCKED {label} pattern={blocked_on}")
            return {"label": label, "status": "blocked", "attempt": attempt, "exit_code": exit_code, "error": blocked_on}
        if exit_code != 0:
            last_error = f"command exit {exit_code}"
        else:
            state, reason = job_state(repo, out, job)
            if state == "valid":
                say(f"PASS {label} attempt={attempt}")
                return {"label": label, "status": "pass", "attempt": attempt, "exit_code": 0}
            last_error = reason or "output invalid"
        say(f"RETRY {label} attempt={attempt} reason={last_error}")
    return {"label": label, "status": "fail", "attempt": args.attempts, "exit_code": exit_code, "error": last_error}


def stage_report(repo: Path, out: Path, jobs: list[dict]) -> tuple[int, list[dict]]:
    pending = []
    for job in jobs:
        state, reason = job_state(repo, out, job)
        if state != "valid":
            pending.append({"label": job["label"], "state": state, "reason": reason})
    return len(jobs) - len(pending), pending


def metrics_path(args, out: Path) -> Path:
    return Path(args.metrics_ledger).resolve() if args.metrics_ledger else out / "runs" / "review-metrics.json"


def mark_metrics_unavailable(path: Path, reason: str) -> None:
    try:
        write_unavailable_metrics(path, reason)
    except Exception:
        pass


def start_observation(args, out: Path, scope_jobs: list[dict]) -> tuple[str, Path, dict]:
    try:
        path = metrics_path(args, out)
        configured = bool(args.metrics or args.metrics_db or args.metrics_ledger or args.metrics_reviewer_prefix)
        if not configured:
            mark_metrics_unavailable(path, "compatible telemetry unavailable")
            return "unavailable", path, {"status": "unavailable"}
        metrics = start_metrics(
            path,
            args.metrics_db,
            args.metrics_reviewer_prefix,
            repository=str(repo_root()), round=args.round, base=args.base, head=args.head,
            selected_files=args.selected_files or len(scope_jobs), carried_files=args.carried_files,
            jobs=len(scope_jobs), model=args.model, reasoning=args.reasoning,
        )
        return metrics["status"], path, metrics
    except Exception:
        fallback = out / "runs" / "review-metrics.json"
        mark_metrics_unavailable(fallback, "metrics unavailable")
        return "unavailable", fallback, {"status": "unavailable"}


def checkpoint_observation(path: Path, completed_jobs: int) -> str:
    try:
        return checkpoint_metrics(path, completed_jobs)["status"]
    except Exception:
        mark_metrics_unavailable(path, "metrics unavailable")
        return "unavailable"


def finalize_observation(path: Path) -> str:
    try:
        return finalize_metrics(path)["status"]
    except Exception:
        mark_metrics_unavailable(path, "metrics unavailable")
        return "unavailable"


def run_pending_jobs(repo: Path, out: Path, jobs: list[dict], args, concurrency: int, on_complete=None) -> dict[str, dict]:
    """Run pending jobs in a bounded pool; all result ordering is restored by the caller."""
    pending = [job for job in jobs if job_state(repo, out, job)[0] != "valid"]
    results: dict[str, dict] = {}
    if not pending:
        return results

    active: dict[object, dict] = {}
    next_index = 0
    blocked = False
    with ThreadPoolExecutor(max_workers=min(concurrency, len(pending))) as executor:
        while next_index < len(pending) and len(active) < concurrency:
            job = pending[next_index]
            next_index += 1
            active[executor.submit(run_one, repo, out, job, args)] = job

        while active:
            done, _ = wait(tuple(active), return_when=FIRST_COMPLETED)
            for future in done:
                job = active.pop(future)
                try:
                    result = future.result()
                except Exception as error:  # keep sibling jobs independent
                    result = {
                        "label": job["label"], "status": "fail", "attempt": 0,
                        "error": f"runner exception: {error}",
                    }
                results[job["label"]] = result
                if on_complete is not None:
                    on_complete(result)
                if result["status"] == "fail":
                    say(f"FAIL {job['label']}: {result.get('error', 'job failed')}")
                blocked = blocked or result["status"] == "blocked" or STOP_EVENT.is_set()

            if not blocked:
                while next_index < len(pending) and len(active) < concurrency:
                    job = pending[next_index]
                    next_index += 1
                    active[executor.submit(run_one, repo, out, job, args)] = job

    if blocked:
        reason = STOP_REASON.get("reason", "provider block")
        for job in pending[next_index:]:
            results[job["label"]] = {
                "label": job["label"], "status": "blocked", "attempt": 0, "error": reason,
            }
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True)
    parser.add_argument("--jobs-file", help="default: <out>/jobs.json")
    parser.add_argument("--only", nargs="*", help="exact job labels to consider")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--command", help="subprocess template; {prompt} required, {output}/{label} optional")
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--timeout-min", type=int, default=35)
    parser.add_argument("--block-on", action="append", default=None, help="provider-block substring (repeatable)")
    parser.add_argument("--status-file", help="default: <out>/runs/<jobs-stem>-status.json")
    parser.add_argument("--no-freeze-check", action="store_true")
    parser.add_argument("--metrics", action="store_true", help="observe compatible provider token metrics")
    parser.add_argument("--metrics-db", help="provider telemetry database supplied by an adapter")
    parser.add_argument("--metrics-ledger", help="content-safe observational metrics path")
    parser.add_argument("--metrics-reviewer-prefix", help="explicit provider reviewer path for telemetry")
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
        scope_jobs = load_jobs(jobs_path)
    except RuntimeError as error:
        sys.stderr.write(f"{error}\n")
        return 1
    try:
        concurrency = manifest_concurrency(out)
    except RuntimeError as error:
        sys.stderr.write(f"{error}\n")
        return 1
    if args.only:
        unknown = set(args.only) - {job["label"] for job in scope_jobs}
        if unknown:
            parser.error(f"unknown jobs: {sorted(unknown)}")
        jobs = [job for job in scope_jobs if job["label"] in args.only]
    else:
        jobs = scope_jobs

    status_path = Path(args.status_file).resolve() if args.status_file else out / "runs" / f"{jobs_path.stem}-status.json"
    if args.validate_only:
        if not args.no_freeze_check:
            try:
                drift = check_freeze(repo, out, "validate")
            except RuntimeError as error:
                sys.stderr.write(f"{error}\n")
                return 1
            if drift:
                sys.stderr.write(drift[0] + "\n")
                return 3
        rows = []
        for job in jobs:
            state, reason = job_state(repo, out, job)
            row = {"label": job["label"], "status": state, "reason": reason or None}
            if state != "valid":
                row["prompt"], row["output"] = job["prompt"], job["output"]
            rows.append(row)
            say(f"{state.upper()} {job['label']}" + (f" — {reason}" if reason else ""))
        write_json(status_path, {"mode": "validate", "jobs": rows})
        pending = [row for row in rows if row["status"] != "valid"]
        say(f"SUMMARY valid={len(rows) - len(pending)} pending={len(pending)} of {len(rows)}")
        return 0 if not pending else 1

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
    metrics_status, metrics_file, _ = start_observation(args, out, scope_jobs)
    initial_results = {
        job["label"]: {"label": job["label"], "status": "pass", "attempt": 0, "preserved": True}
        for job in jobs if job_state(repo, out, job)[0] == "valid"
    }
    completed_jobs = sum(job_state(repo, out, scope_job)[0] == "valid" for scope_job in scope_jobs)

    def checkpoint_completed(_result: dict) -> None:
        nonlocal completed_jobs, metrics_status
        completed_jobs = min(len(scope_jobs), completed_jobs + 1)
        if metrics_status == "running":
            metrics_status = checkpoint_observation(metrics_file, completed_jobs)

    pending_results = run_pending_jobs(repo, out, jobs, args, concurrency, checkpoint_completed)
    results_by_label = {**initial_results, **pending_results}
    results = [
        results_by_label.get(job["label"], {
            "label": job["label"], "status": "blocked", "attempt": 0,
            "error": STOP_REASON.get("reason", "run stopped"),
        })
        for job in jobs
    ]
    valid_count, pending = stage_report(repo, out, jobs)
    _, scope_pending = stage_report(repo, out, scope_jobs)
    failed = [item for item in results if item["status"] == "fail"]
    blocked = [item for item in results if item["status"] == "blocked"]
    if metrics_status == "running" and not failed and not scope_pending:
        metrics_status = finalize_observation(metrics_file)
    if blocked:
        try:
            write_json(out / "run-blocker.json", {
                "status": "blocked", "pattern": STOP_REASON.get("reason"),
                "first_label": STOP_REASON.get("label"), "jobs_file": str(jobs_path),
                "valid_outputs": valid_count, "total_jobs": len(jobs),
                "pending": [row["label"] for row in pending],
            })
        except Exception:
            pass
    write_json(status_path, {
        "mode": "run", "metrics": metrics_status, "metrics_ledger": str(metrics_file), "jobs": results,
        "summary": {"pass": len(results) - len(failed) - len(blocked), "fail": len(failed), "blocked": len(blocked), "stage_valid": valid_count, "stage_total": len(jobs)},
    })
    say(f"SUMMARY pass={len(results) - len(failed) - len(blocked)} fail={len(failed)} blocked={len(blocked)}; stage {valid_count}/{len(jobs)} outputs valid")

    if not args.no_freeze_check:
        try:
            drift = check_freeze(repo, out, "after run")
        except RuntimeError as error:
            sys.stderr.write(f"{error}\n")
            return 1
        if drift:
            sys.stderr.write(drift[0] + "\n")
            return 3
    if blocked:
        say(f"resume: rerun this command after the provider block clears — see {out / 'run-blocker.json'}")
        return 2
    return 1 if failed or pending else 0


if __name__ == "__main__":
    sys.exit(main())
