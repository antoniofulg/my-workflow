# Parallel Slice Executor Validation

**Verdict**: FAIL
**Date:** 2026-08-24
**Phase:** Technical Verification
**Scope:** Slice A only, tasks T1/T2 after T2R2
**Spec:** `.specs/features/parallel-slice-executor/spec.md`
**Diff range:** `d73071c..10d9ef5`
**Incremental remediation:** `28b8522..10d9ef5`
**Verifier:** independent Verifier, author != verifier

This is the third and final Technical Verification round for Slice A. It does not close the feature,
does not cover Slices B-D, and does not dispatch QA.

## Verdict and Cap Disposition

Quick and structural gates pass, and all three required mutants are killed. Slice A still fails:

1. the pending-worker crash window remains evidence-zero;
2. pending acquire reconciliation bypasses the correlated/redacted lease validation required by
   EXE-20 and can persist malformed runtime state; and
3. the legacy adapter worktree-creator path contradicts the core-owned checkout boundary frozen by
   AD-011 and T2R2.

The Technical Verifier cap is exhausted under `docs/guidelines/REVIEW-ROUNDS.md:17-24,145-146`.
These residual blockers are escalated; no fourth fix/re-verify round is authorized by this report.

## Task and Contract Disposition

| Owner | Case | Disposition | Evidence |
| --- | --- | --- | --- |
| T1 | UT-001 | PASS | Disabled no-effect assertions at `tools/test_parallel_executor.py:147-161,560-574`; one-active and ordered progress at `:737-766`. |
| T1 | UT-003 | FAIL | `tools/test_parallel_executor.py:62-75` covers only top-level foreign/schema variants. Nested lease/action receipt shape and duplicate live lease IDs are not validated by `.agents/skills/autonomous/scripts/parallel_execute.py:94-130`. |
| T1 | SEC-001 | FAIL | Same root cause as UT-003: malformed nested runtime receipts can pass `_load_state` and reach effects. |
| T1 | SEC-002 | PASS | Git-common placement and prior-state preservation at `tools/test_parallel_executor.py:78-105`. |
| T1 | SEC-003 | PASS | Exact argv, `shell is False`, and timeout at `tools/test_parallel_executor.py:110-126`. |
| T1 | SEC-004 | PASS | Unsafe destination returns before adapter effects at `tools/test_parallel_executor.py:702-715`; sensor M3 kills bypassing the preflight. |
| T2 | UT-002 | FAIL | Accepted replay is covered at `tools/test_parallel_executor.py:212-231`; pending worktree at `:613-630`; acquire/release at `:840-874`. The fixture labels worker `accepted`, not `pending`, at `:854`, so no assertion proves pending-worker reconciliation without a repeated start. |
| T2 | UT-007 | PASS | `Resources: none` bypass and correlated fresh lease at `tools/test_parallel_executor.py:264-312`; acquire-before-worker ordering at `:820-835`. |
| T2 | UT-008 | PASS | Provider failures at `tools/test_parallel_executor.py:476-496`; owned cleanup/retry at `:317-353`; terminal cleanup at `:501-534`. |
| T2 | IT-001 | GAP | `tools/test_parallel_executor.py:539-555` executes disabled `status` and `start` only. It does not invoke the CLI `resume` command promised by `.specs/features/parallel-slice-executor/tests.md:22`. Programmatic resume is covered elsewhere, so CLI resume remains evidence-zero. |
| T2 | SEC-007 | PASS | Resource failures assert zero worker effects at `tools/test_parallel_executor.py:476-496`; fresh acquire precedes worker at `:820-835`. |
| T2 | SEC-008 | PASS | Foreign cleanup rejection and exact-once owned retry at `tools/test_parallel_executor.py:317-353`. |

**Assigned-case status:** 8 PASS, 1 GAP, 3 FAIL across the 12 T1/T2 cases.

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | `file:line` + assertion evidence | Result |
| --- | --- | --- | --- |
| EXE-01 | Disabled returns serial and calls no worktree, worker, event, Git, or resource adapter. | `tools/test_parallel_executor.py:560-574` forbids Git/planner/adapter work and asserts `reason == "disabled-mode"`; production returns at `.agents/skills/autonomous/scripts/parallel_execute.py:562-571`. | PASS |
| EXE-02 | At most one active worker per slice; declared task order is preserved. | `tools/test_parallel_executor.py:753-766` asserts only T1 runs first, then T2 becomes complete after T1's checkpoint, with exact effect order `worktree:T1, worker:T1, worktree:T2, worker:T2`. | PASS |
| EXE-03 | Every external effect observes a persisted key derived from feature, slice, task, action, and source checkpoint. | `tools/test_parallel_executor.py:778-835` reads persisted pending worktree/acquire/worker/release actions before each effect; sensor M1 kills removal of the worker pre-effect save. Key material is implemented at `.agents/skills/autonomous/scripts/parallel_execute.py:468-477`. | PASS |
| EXE-04 | Restart reconciles receipts without recreating an accepted worktree, worker, or lease. | Accepted replay: `tools/test_parallel_executor.py:212-231`; pending worktree: `:613-630`; pending acquire/release: `:840-874`. However `:854` sets worker status to `accepted`, so pending-worker recovery is not exercised. | FAIL |
| EXE-05 | Malformed, foreign, or unreconcilable state serializes with a decisive reason and no adapter effect. | Foreign and unreconcilable top-level paths pass at `tools/test_parallel_executor.py:635-662`. Nested lease/action schemas and duplicate lease IDs are omitted from `.agents/skills/autonomous/scripts/parallel_execute.py:94-130`, so malformed persisted resource state can pass validation. | FAIL |
| EXE-18 | `Resources: none` permits worktree concurrency without a lease. | `tools/test_parallel_executor.py:279-282` asserts successful dispatch, zero provider construction, then worktree and worker effects. | PASS |
| EXE-19 | Resource acquire uses the complete argv-only request before worker start. | Request fields are asserted at `tools/test_parallel_executor.py:301-309,421-434`; exact order is asserted at `:834-835` as worktree, acquire, worker, release. | PASS |
| EXE-20 | Only a unique, correlated, prepared lease with declared resources and redacted environment is accepted. | Fresh provider output is rejected/accepted precisely at `tools/test_parallel_executor.py:358-434`. Pending reconciliation returns an opaque mapping at `.agents/skills/autonomous/scripts/parallel_execute.py:479-484` and stores it directly at `:690-697`; the passing fixture at `tools/test_parallel_executor.py:860-874` omits the idempotency key and normalized redaction fields. | FAIL |
| EXE-21 | Missing/unsupported/timed-out/malformed/duplicate/cleanup-failed providers refuse worker dispatch and report serial fallback. | `tools/test_parallel_executor.py:476-496` asserts fallback reason and zero workers; `:520-534` asserts cleanup-failed fallback and retained failed receipt. | PASS |
| EXE-22 | Accepted, halted, or abandoned workers release an owned lease exactly once and retain cleanup evidence. | `tools/test_parallel_executor.py:501-515` asserts one release and `released is True`; `:317-353` asserts foreign rejection and idempotent owned retry. | PASS |

**Acceptance status:** 7 PASS, 3 FAIL across the ten Slice A EXE requirements.

## Security Requirements

| Requirement | Surface | Evidence | Result |
| --- | --- | --- | --- |
| SEC-001 | S1 | Top-level rejection passes at `tools/test_parallel_executor.py:62-75,635-662`; nested lease/action validation is absent at `.agents/skills/autonomous/scripts/parallel_execute.py:94-130`. | FAIL |
| SEC-002 | S1 | `tools/test_parallel_executor.py:78-105` proves Git-common storage and atomic prior-state survival. | PASS |
| SEC-003 | S6 | `tools/test_parallel_executor.py:110-126,421-434` proves argv-only subprocess input, `shell=False`, and bounded timeout. | PASS |
| SEC-004 | S6 | Destination preflight at `.agents/skills/autonomous/scripts/parallel_execute.py:589-598`; zero-effect unsafe-path assertion at `tools/test_parallel_executor.py:702-715`; sensor M3 killed. | PASS |
| SEC-007 | S11 | `tools/test_parallel_executor.py:476-496,820-835` proves no resource worker before accepted acquisition. | PASS |
| SEC-008 | S11 | `tools/test_parallel_executor.py:317-353` proves foreign cleanup rejection and exact-once owned retry. | PASS |

- **Security guidance:** `docs/guidelines/SECURITY.md:131-145` residual review.
- **Threat model:** `.specs/features/parallel-slice-executor/threat-model.md:1-29`.
- **Open Critical:** 0.
- **Open High:** 0.
- **Security verdict:** FAIL because SEC-001 remains incomplete.

## Prior Gap Reconciliation

| Prior gap | Final disposition |
| --- | --- |
| Disabled mode touched planner/Git before returning. | CLOSED by `tools/test_parallel_executor.py:560-574`. |
| Same-slice order was not proven. | CLOSED by `tools/test_parallel_executor.py:737-766`. |
| Worktree/worker/acquire/release pending intent was not observed before effects. | CLOSED by `tools/test_parallel_executor.py:778-835`; sensor M1 killed. |
| Pending acquire reconciliation could repeat the external effect. | CLOSED by `tools/test_parallel_executor.py:840-873`; sensor M2 killed. |
| Pending worker reconciliation was unproved. | OPEN: `tools/test_parallel_executor.py:854` marks worker `accepted`, and `:872-874` asserts only acquire/release reconciliation plus no fresh adapter effects. |
| Acquire-before-worker ordering was unproved. | CLOSED by exact event ordering at `tools/test_parallel_executor.py:834-835`. |
| Unsafe destination could reach an adapter before validation. | CLOSED by `tools/test_parallel_executor.py:702-715`; sensor M3 killed. |
| Core must create the checkout before adapter worker attachment under AD-011. | OPEN: `.agents/skills/autonomous/scripts/parallel_execute.py:489-503` retains a legacy adapter `prepare_worktree/create_worktree` branch. `tools/test_parallel_executor.py:888-912` proves only the alternate worker-only path and never forbids adapter-owned creation. |
| Resource failure/cleanup, request correlation, live-lease reuse, and S11 threat model gaps. | CLOSED for fresh effects by `tools/test_parallel_executor.py:317-434,476-534` and `.specs/features/parallel-slice-executor/threat-model.md:1-29`; pending acquire receipt validation remains open under EXE-20. |

## Gate Evidence

- **Quick command:** `python3 tools/test_parallel_executor.py`
- **Quick result:** exit 0, `25 passed, 0 failed`; 0 skipped; 0 warnings.
- **Before feature:** owning suite absent at `d73071c`; **after T2R2:** 25 tests; delta +25.
- **Strict spec:** `python3 /Users/antoniofulg/Projects/my-workflow/.agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-executor/spec.md` -> exit 0, 0 errors, 0 warnings.
- **Strict tasks:** `python3 /Users/antoniofulg/Projects/my-workflow/.agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-executor/tasks.md` -> exit 0, 0 errors, 0 warnings.
- **AD index:** `python3 tools/ad-index.py --check` -> exit 0, `AD-INDEX.md up to date`.
- **Full diff:** `git diff --check d73071c..10d9ef5` -> exit 0, no output.
- **Incremental diff:** `git diff --check 28b8522..10d9ef5` -> exit 0, no output.
- **Compile:** `python3 -m py_compile .agents/skills/autonomous/scripts/parallel_execute.py tools/test_parallel_executor.py` -> exit 0.

Passing gates do not override evidence-zero criteria or contract deviations.

## Discrimination Sensor

Real-tree porcelain was empty before the sensor. Each mutation ran in its own detached temporary
worktree at `10d9ef5`; all scratches were removed. Final real-tree porcelain matched the empty
baseline before this report edit.

| Mutation | Target | Fault | Directed result | Outcome |
| --- | --- | --- | --- | --- |
| M1 | `.agents/skills/autonomous/scripts/parallel_execute.py:703-705` | Removed `_save(state)` before `start_worker`. | exit 1 at `tools/test_parallel_executor.py:834` | KILLED |
| M2 | `.agents/skills/autonomous/scripts/parallel_execute.py:690-695` | Disabled pending-acquire reconciliation, forcing a duplicate acquire. | exit 1 at `tools/test_parallel_executor.py:870` | KILLED |
| M3 | `.agents/skills/autonomous/scripts/parallel_execute.py:594-598` | Bypassed the second bounded destination preflight. | exit 1 at `tools/test_parallel_executor.py:714` | KILLED |

**Sensor:** 3 injected, 3 killed, 0 survived. PASS.

## Code Quality and Contract Integrity

| Check | Result |
| --- | --- |
| Minimum/surgical implementation | PASS for the Slice A runtime and owning suite. |
| No unrelated product-code mutation in T2R2 | PASS. |
| Every assigned test maps to T1/T2 | PASS per `.specs/features/parallel-slice-executor/tests.md:53-56`. |
| Cases assert contracted outcomes | FAIL under `docs/guidelines/TEST-CONTRACT.md:47-55`: UT-002 pending worker, IT-001 CLI resume, and nested malformed-state outcomes are hollow/evidence-zero. |
| AD-011 / DX parity | FAIL: legacy adapter worktree creation remains at `.agents/skills/autonomous/scripts/parallel_execute.py:489-503`, despite `.specs/STATE.md` AD-011 and `.specs/features/parallel-slice-executor/dx.md:34-40` assigning creation to the core. |
| Security residual review | FAIL for SEC-001; 0 Critical and 0 High findings. |
| Public QA dispatch | Not applicable to this technical-only packet; QA was not run. |

## Ranked Residual Blockers / Fix Tasks

1. **Major - EXE-04 / UT-002:** add a true pending-worker crash fixture, reconcile through the
   adapter, and assert `start_worker` is not repeated. Current test uses `worker = accepted`.
2. **Major - EXE-20 / EXE-05 / SEC-001:** route fresh and reconciled acquire receipts through one
   strict validator; require current key/lane/resources, unique lease ID, prepared worktree, and
   redacted environment; validate the persisted nested lease/action schema before any effect.
3. **Major - AD-011 / T2R2:** remove the legacy adapter-owned worktree creation path. Core must always
   invoke its fixed-argv Git creator, then pass only the existing validated checkout to
   `start_worker`; update doubles to observe the core seam.
4. **Major - IT-001:** exercise the public CLI `resume` command and assert one JSON object, persisted
   state agreement, and no repeated effects.

## Summary

**Overall:** FAIL, post-cap escalation. T2R2 closes the prior ordering, pending-intent,
pending-acquire, and destination-preflight gaps, and all required mutants die. Pending-worker
reconciliation remains unproved; reconciled leases bypass the required strict receipt validation;
and the legacy worktree creator contradicts AD-011. Slice A remains technically unverified. Feature
completion and QA remain untouched.
