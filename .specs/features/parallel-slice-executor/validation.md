# Parallel Slice Executor Validation

**Verdict**: FAIL
**Date:** 2026-08-24
**Phase:** Technical Verification
**Scope:** Slice A only, tasks T1/T2
**Spec:** `.specs/features/parallel-slice-executor/spec.md`
**Diff range:** `d73071c..f8871f2`
**Verifier:** independent Verifier, author != verifier

This report does not close the feature and does not cover Slices B-D or QA.

## Task Disposition

| Task | Recorded status | Technical disposition |
| --- | --- | --- |
| T1 | complete | FAIL: EXE-01, EXE-02, EXE-05, SEC-001, and SEC-004 are not proven; EXE-01 has a concrete deviation. |
| T2 | complete | FAIL: restart reconciliation, pre-effect persistence, resource failure coverage, and automatic lease release are not proven; one relevant mutant survived. |

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | `file:line` + assertion evidence | Result |
| --- | --- | --- | --- |
| EXE-01 | Disabled returns serial and calls no worktree, worker, event, Git, or resource adapter. | `tools/test_parallel_executor.py:157-161` asserts serial result and no constructed worker adapter. However `.agents/skills/autonomous/scripts/parallel_execute.py:344-348` resolves repository/state through Git before `start`, and `:443-448` plans before the disabled return. A diagnostic spy observed `git rev-parse --show-toplevel` twice and `git rev-parse --git-common-dir` once during construction. | FAIL |
| EXE-02 | At most one active worker receipt per slice; declared task order is preserved. | `tools/test_parallel_executor.py:49-59` asserts only one lane-state transition and rejection of its duplicate. No assertion drives two tasks in one slice or proves worker count/order. | GAP |
| EXE-03 | Before each external action, persist a key derived from feature, slice, task, action, and source checkpoint. | Key composition exists at `.agents/skills/autonomous/scripts/parallel_execute.py:261-263,428-435`; pre-effect save is at `:481-485`. No assertion observes persistence before the effect or proves all five inputs discriminate. Sensor mutation M1 removed `:482`; all 12 tests still passed. | FAIL |
| EXE-04 | Restart reconciles persisted receipts with adapter and never recreates accepted worktree, worker, or lease. | `tools/test_parallel_executor.py:215-224` proves accepted worktree/worker receipts are skipped on a second start. It does not exercise adapter reconciliation, leases, or a crash window. A pending receipt reaches `.agents/skills/autonomous/scripts/parallel_execute.py:434-435` and raises `ExecutorError: unreconciled pending action: worktree` instead of reconciling. | FAIL |
| EXE-05 | Malformed, foreign, or unreconcilable state selects serial recovery with decisive reason and no adapter effect. | `tools/test_parallel_executor.py:62-75` only asserts direct schema rejection. It does not assert coordinator serial recovery, decisive reason, or zero adapter effects; pending state is an uncaught error at `.agents/skills/autonomous/scripts/parallel_execute.py:434-435`. | FAIL |
| EXE-18 | `Resources: none` permits worktree concurrency without runtime lease acquisition. | `tools/test_parallel_executor.py:265-272` asserts `fallback is False`, zero provider construction, and worktree/worker effects. | PASS |
| EXE-19 | Resource lanes call the provider before worker start using argv-only input containing repository, feature, slice, task, worktree, and key. | Request construction exists at `.agents/skills/autonomous/scripts/parallel_execute.py:508-516` and argv-only provider invocation at `:289-293`. `tools/test_parallel_executor.py:235-245` asserts only `resources` and a key condition; it does not assert the other required fields, argv shape, or acquire-before-worker order. | GAP |
| EXE-20 | Accept only a correlated JSON receipt with unique lease ID, declared resources, prepared worktree, and redacted environment keys. | `tools/test_parallel_executor.py:287-293,339-374` asserts acquisition, prepared state, redaction, resource mismatch, unprepared receipt, foreign key, and malformed JSON. No valid receipt with a reused live lease ID is rejected, so uniqueness is evidence-zero. | GAP |
| EXE-21 | Missing/unsupported/timed-out/malformed/duplicate/cleanup-failed provider refuses dispatch and reports serial fallback. | `tools/test_parallel_executor.py:339-374` covers malformed and some uncorrelated acquire receipts only. No assertion covers missing provider, timeout, live-lease reuse, cleanup failure, no worker dispatch, or serial fallback. Cleanup failure raises at `.agents/skills/autonomous/scripts/parallel_execute.py:581-587`, not a serial result. | FAIL |
| EXE-22 | Accepted, halted, or abandoned workers release a lease exactly once and retain cleanup evidence. | `tools/test_parallel_executor.py:298-334` proves an explicit `release_lane` call is owned and idempotent. No assertion or coordinator path releases on worker accepted, halted, or abandoned; `start` returns after worker acceptance at `.agents/skills/autonomous/scripts/parallel_execute.py:527-545`. | FAIL |

**Acceptance status:** 1 PASS, 3 GAP, 6 FAIL across the ten Slice A EXE requirements.

## Security Requirements

| Requirement | Surface | Evidence | Result |
| --- | --- | --- | --- |
| SEC-001 | S1 | `tools/test_parallel_executor.py:62-75` asserts schema rejection, but not rejection before any adapter effect through the coordinator. | GAP |
| SEC-002 | S1 | `tools/test_parallel_executor.py:78-105` asserts Git-common placement, exclusion from `.specs`, and preservation of the prior JSON after an injected pre-rename failure. | PASS |
| SEC-003 | S6 | `tools/test_parallel_executor.py:110-126` asserts `shell is False`, timeout `3`, and literal metacharacter argv. Sensor M2 changing `shell=False` to `shell=True` was killed. | PASS |
| SEC-004 | S6 | `tools/test_parallel_executor.py:129-141` directly tests the path helper. It does not prove repository/worktree destinations are checked before the first write/process. Adapter receipts are copied at `.agents/skills/autonomous/scripts/parallel_execute.py:485-490` without a bounded-path assertion in this slice. | FAIL |
| SEC-007 | S11 | `tools/test_parallel_executor.py:287-293` proves a successful prepared lease, but no test proves a worker never starts for absent, timed-out, malformed, or duplicate leases. Sensor M3 bypassing resource acquisition was killed only by the happy-path acquire count. | GAP |
| SEC-008 | S11 | `tools/test_parallel_executor.py:313-334` asserts foreign duplicate-lease cleanup rejection, one provider release, and idempotent retry. | PASS |

- **Security guidance applied:** `docs/guidelines/SECURITY.md` residual review; no matching dedicated security skill was installed in the packet environment.
- **Threat model:** missing. Slice A implements S11 isolation behavior, which triggers a scoped threat model under `docs/guidelines/SECURITY.md` section 4.
- **Open Critical:** 0.
- **Open High:** 0.
- **Security verdict:** FAIL, due SEC-004 and evidence gaps.

## Edge Cases in Slice A

| Edge case | Evidence | Result |
| --- | --- | --- |
| Duplicate worktree/branch/terminal/dispatch/live lease IDs serialize. | State validation checks several duplicate external IDs, but no assigned test asserts the full duplicate-receipt outcome; branch duplication is explicitly excluded at `.agents/skills/autonomous/scripts/parallel_execute.py:111-115`. | GAP |
| External path escape/symlink fails before first write. | Helper-only assertion at `tools/test_parallel_executor.py:129-141`; no effect-boundary assertion. | FAIL |
| Repeated accepted resource cleanup has no second destructive effect. | `tools/test_parallel_executor.py:330-334` asserts idempotent second result and `provider.releases == 1`. | PASS |
| Credential-shaped provider values remain redacted. | `tools/test_parallel_executor.py:291-293` asserts `<redacted>` for `PORT`; production redaction is at `.agents/skills/autonomous/scripts/parallel_execute.py:317-323`. | PASS |

## Gate Evidence

### Quick gate

- **Command:** `python3 tools/test_parallel_executor.py`
- **Result:** exit 0, `12 passed, 0 failed`; 0 skipped; warnings: none.
- **Before feature:** `tools/test_parallel_executor.py` did not exist at `d73071c`.
- **After feature:** 12 tests.
- **Delta:** +12 tests in the owning suite.

### Structural and diff checks

- **Command:** `python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-executor/tasks.md`
- **Result:** exit 0, `0 error(s), 0 warning(s)`.
- **Command:** `git diff --check d73071c..f8871f2`
- **Result:** exit 0, no output.
- **Command:** `python3 -m py_compile .agents/skills/autonomous/scripts/parallel_execute.py tools/test_parallel_executor.py`
- **Result:** exit 0, no output.
- **Command:** `python3 .agents/skills/tlc-spec-driven/scripts/validate_state.py parallel-slice-executor`
- **Result:** expected exit 1: report verdict is FAIL and ranked gaps must be fixed before feature completion.

Passing gates do not override the spec mismatches and hollow cases above.

## Discrimination Sensor

Baseline real-tree porcelain was empty. Mutations ran in detached temporary worktrees at `f8871f2`; the worktree was removed after each run. Final real-tree porcelain matched the empty baseline.

| Mutation | Target | Fault | Directed test result | Outcome |
| --- | --- | --- | --- | --- |
| M1 | `.agents/skills/autonomous/scripts/parallel_execute.py:482` | Removed state persistence immediately before `create_worktree`. | exit 0, `12 passed, 0 failed` | SURVIVED: EXE-03 pre-effect durability is not discriminated. |
| M2 | `.agents/skills/autonomous/scripts/parallel_execute.py:201` | Changed `shell=False` to `shell=True`. | exit 1 | KILLED by the executor suite. |
| M3 | `.agents/skills/autonomous/scripts/parallel_execute.py:496` | Bypassed resource acquisition for resource-bearing lanes. | exit 1 at `tools/test_parallel_executor.py:290`, expected one acquire. | KILLED. |

**Sensor:** 3 injected, 2 killed, 1 survived. FAIL.

## Code Quality and Contract Integrity

| Check | Result |
| --- | --- |
| Minimum/surgical implementation | PASS for the two runtime/test files in Slice A. |
| No unrelated product-code changes | PASS. Diff contains executor, its owning tests, and feature workflow artifacts. |
| Tests map to assigned contract IDs | PASS by ownership table at `.specs/features/parallel-slice-executor/tests.md:53-56`. |
| Assigned cases assert contracted outcomes | FAIL. EXE-02, EXE-03, EXE-05, EXE-19–22, SEC-001, SEC-004, and SEC-007 have missing or partial assertions. |
| No unclaimed tests | PASS. All 12 functions support assigned ACs/done-when criteria. |
| Public QA dispatch | Not applicable for Slice A. This is an internal coordinator primitive; no QA was run. |

Guidelines applied: `docs/guidelines/TEST-CONTRACT.md`, `GATES.md`, `VERIFICATION-EVIDENCE.md`, `REVIEW-ROUNDS.md`, and `SECURITY.md`.

## Ranked Gaps / Fix Tasks

1. **Major, EXE-03/EXE-04/EXE-05:** implement and test reconciliation of a persisted `pending` action after a crash. The current path raises instead of consulting the adapter or returning named serial recovery. Add a crash-window test that observes persistence before the external effect and proves at-most-once recovery.
2. **Major, EXE-01:** short-circuit disabled mode before planner/Git/effect adapter calls, then assert zero calls across every named adapter category.
3. **Major, EXE-22/EXE-21/SEC-007:** implement and test lease release on worker accepted/halted/abandoned plus missing provider, timeout, duplicate live lease, malformed receipt, and cleanup-failure serial outcomes. Assert no worker starts without an accepted prepared lease.
4. **Major, SEC-004:** bind `bounded_path` to actual repository/worktree effect boundaries and assert escape/symlink inputs fail before write/process start.
5. **Major, EXE-02:** add a two-task same-slice case asserting one active worker and declared task order.
6. **Major, EXE-19/EXE-20:** assert the full provider argv/request contract and valid live-lease duplication rejection.
7. **Process gap:** add the required scoped S11 threat model before Slice A can receive a clean security verdict.

## Summary

**Overall:** FAIL. Slice A is not technically verified. Quick gate passes, but one mutant survives and multiple assigned criteria lack outcome-level evidence or contradict runtime behavior. Feature status remains open; QA was not executed.
