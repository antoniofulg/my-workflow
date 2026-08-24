# Parallel Slice Executor Validation

**Verdict**: FAIL
**Date:** 2026-08-24
**Phase:** Technical Verification
**Scope:** Slice A only, tasks T1/T2
**Spec:** `.specs/features/parallel-slice-executor/spec.md`
**Diff range:** `d73071c..28b8522`
**Incremental remediation:** `f8871f2..28b8522`
**Verifier:** independent Verifier, author != verifier

This report does not close the feature and does not cover Slices B-D or QA.

## Task Disposition

| Task | Recorded status | Technical disposition |
| --- | --- | --- |
| T1 | complete | FAIL: disabled-mode and state recovery improved, but EXE-02 remains hollow and SEC-004 still validates an adapter-returned worktree only after the external effect. |
| T2 | complete | FAIL: worktree pre-effect persistence/reconciliation is now discriminated, but worker persistence and pending resource reconciliation are not. Two targeted mutants survived. |

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | `file:line` + assertion evidence | Result |
| --- | --- | --- | --- |
| EXE-01 | Disabled returns serial and calls no worktree, worker, event, Git, or resource adapter. | `tools/test_parallel_executor.py:553-567` forbids planner/Git/adapter calls and asserts `reason == "disabled-mode"`; production returns before repository/planner preparation at `.agents/skills/autonomous/scripts/parallel_execute.py:515-525`. | PASS |
| EXE-02 | A valid safe/full plan exposes at most one active worker per slice and preserves declared task order. | `tools/test_parallel_executor.py:574-589` supplies two ordered tasks in one slice but asserts serial fallback and zero effects. It does not assert one active task or subsequent ordered progress, so UT-001 does not assert its contracted result from `.specs/features/parallel-slice-executor/tests.md:7`. | GAP |
| EXE-03 | Before every external action, persist a key derived from feature, slice, task, action, and source checkpoint. | Worktree persistence is observed at `tools/test_parallel_executor.py:659-680`, backed by `.agents/skills/autonomous/scripts/parallel_execute.py:581-590`. The same test does not observe worker/acquire/release effects; mutation M2 removed the worker pre-effect save at production line 639 and all 21 tests passed. | FAIL |
| EXE-04 | Restart reconciles persisted receipts and never recreates an accepted worktree, worker, or lease. | Accepted worktree/worker replay is covered at `tools/test_parallel_executor.py:205-224`; pending worktree recovery is covered at `:594-622`. No pending acquire/worker/release crash case exists; mutation M3 disabled pending-acquire reconciliation at production lines 625-630 and all 21 tests passed. | FAIL |
| EXE-05 | Malformed, foreign, or unreconcilable state selects serial recovery, names the reason, and causes no adapter effect. | Direct malformed/foreign validation is asserted at `tools/test_parallel_executor.py:62-75`; coordinator foreign and unreconcilable pending outcomes assert fallback, reason, and zero effects at `:627-654`. | PASS |
| EXE-18 | `Resources: none` permits worktree concurrency without acquiring a runtime lease. | `tools/test_parallel_executor.py:257-275` asserts `fallback is False`, zero provider construction, then worktree and worker effects. | PASS |
| EXE-19 | Before worker start, resource lanes call an argv-only provider request containing repository, feature, slice, task, worktree, and key. | `tools/test_parallel_executor.py:290-302` asserts every coordinator request field; `:409-427` asserts exact provider argv/input. No assertion observes acquire before worker start, so the ordering clause remains evidence-zero. | GAP |
| EXE-20 | Accept only a correlated receipt with unique live lease ID, declared resources, prepared worktree, and redacted environment keys. | `tools/test_parallel_executor.py:351-406` rejects resource/key/preparation mismatches, malformed JSON, and live-lease reuse; `:423-427` accepts exact correlated input; `:303-305` asserts preparation and redaction. | PASS |
| EXE-21 | Missing/unsupported/timed-out/malformed/duplicate/cleanup-failed providers refuse dispatch and report serial fallback. | `tools/test_parallel_executor.py:469-489` asserts fallback reason and zero worker effects for missing, timeout, malformed, and duplicate failures; `:513-527` asserts cleanup-failed fallback and retained failed cleanup receipt. | PASS |
| EXE-22 | Accepted, halted, or abandoned workers release their lease exactly once and retain cleanup evidence. | `tools/test_parallel_executor.py:494-508` asserts one release and persisted `released is True` for all three terminal outcomes; `:310-346` asserts owned idempotent retry. | PASS |

**Acceptance status:** 6 PASS, 2 GAP, 2 FAIL across the ten Slice A EXE requirements.

## Security Requirements

| Requirement | Surface | Evidence | Result |
| --- | --- | --- | --- |
| SEC-001 | S1 | `tools/test_parallel_executor.py:62-75,627-654` asserts invalid identity/schema rejection plus coordinator fallback with zero adapter effects. | PASS |
| SEC-002 | S1 | `tools/test_parallel_executor.py:78-105` asserts Git-common placement, exclusion from `.specs`, and preservation of prior JSON after an injected pre-rename failure. | PASS |
| SEC-003 | S6 | `tools/test_parallel_executor.py:110-126` asserts literal argv, `shell is False`, and timeout `3`. | PASS |
| SEC-004 | S6 | Declared unsafe paths are rejected before adapter construction at `tools/test_parallel_executor.py:685-697`. However normal adapter worktree creation occurs at `.agents/skills/autonomous/scripts/parallel_execute.py:590` and its returned path is bounded only at `:593-594`; the T1 control requires destination validation before the first write/process. | FAIL |
| SEC-007 | S11 | `tools/test_parallel_executor.py:469-489` asserts resource-bearing workers never start after missing or rejected acquisition; successful preparation is asserted at `:303-305`. | PASS |
| SEC-008 | S11 | `tools/test_parallel_executor.py:310-346` asserts foreign cleanup rejection and one destructive release across owned retry. | PASS |

- **Security guidance applied:** `docs/guidelines/SECURITY.md` residual review.
- **Threat model:** `.specs/features/parallel-slice-executor/threat-model.md:1-29`, now present and scoped to Slice A/S11.
- **Open Critical:** 0.
- **Open High:** 0.
- **Security verdict:** FAIL due to SEC-004 effect-boundary ordering.

## Prior Gap Reconciliation

| Prior gap | Current disposition |
| --- | --- |
| Disabled mode touched planner/Git before returning. | CLOSED by `tools/test_parallel_executor.py:553-567` and production `:515-525`. |
| Worktree idempotency key was not observed before its effect. | CLOSED for worktree: sensor M1 is now killed. Still open for other external actions under EXE-03. |
| Pending restart raised instead of reconciling. | CLOSED for pending worktree at `tools/test_parallel_executor.py:605-622`. Still open for acquire/worker/release under EXE-04. |
| Resource failures and terminal lease release lacked outcome tests. | CLOSED by `tools/test_parallel_executor.py:469-527`. |
| Full provider request and live-lease uniqueness were not asserted. | CLOSED by `tools/test_parallel_executor.py:294-302,351-427`. |
| Scoped S11 threat model was absent. | CLOSED by `.specs/features/parallel-slice-executor/threat-model.md:1-29`. |
| Same-slice task order was not proven. | OPEN: the new test serializes both tasks instead of proving one active task and ordered progress. |
| Worktree destination was not checked before its external effect. | OPEN: returned path validation still follows `create_worktree`. |

## Gate Evidence

- **Quick command:** `python3 tools/test_parallel_executor.py`
- **Quick result:** exit 0, `21 passed, 0 failed`; 0 skipped, 0 warnings.
- **Before feature:** owning suite absent at `d73071c`; **after remediation:** 21 tests; delta +21.
- **Spec validator:** `python3 /Users/antoniofulg/Projects/my-workflow/.agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-executor/spec.md` -> exit 0, 0 errors, 0 warnings.
- **Tasks validator:** `python3 /Users/antoniofulg/Projects/my-workflow/.agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-executor/tasks.md` -> exit 0, 0 errors, 0 warnings.
- **Commit validators:** `check_commit.py` over all three slice commit messages -> 3/3 exit 0.
- **Compile:** `python3 -m py_compile .agents/skills/autonomous/scripts/parallel_execute.py tools/test_parallel_executor.py` -> exit 0.
- **Full diff check:** `git diff --check d73071c..28b8522` -> exit 0, no output.
- **Incremental diff check:** `git diff --check f8871f2..28b8522` -> exit 0, no output.

Passing gates do not override surviving mutants or the SEC-004 ordering deviation.

## Discrimination Sensor

Baseline real-tree porcelain was empty. Each mutation ran in its own detached temporary worktree at `28b8522`; all were removed. Final real-tree porcelain matched the empty baseline.

| Mutation | Target | Fault | Directed result | Outcome |
| --- | --- | --- | --- | --- |
| M1 | `.agents/skills/autonomous/scripts/parallel_execute.py:582` | Removed persisted pending receipt before `create_worktree`. | exit 1 at `tools/test_parallel_executor.py:679` | KILLED |
| M2 | `.agents/skills/autonomous/scripts/parallel_execute.py:639` | Removed persisted pending receipt before `start_worker`. | exit 0, `21 passed, 0 failed` | SURVIVED -> EXE-03 fix task |
| M3 | `.agents/skills/autonomous/scripts/parallel_execute.py:625` | Disabled reconciliation of a persisted pending `acquire`, causing the external acquire to repeat. | exit 0, `21 passed, 0 failed` | SURVIVED -> EXE-04 fix task |

**Sensor:** 3 injected, 1 killed, 2 survived. FAIL.

## Code Quality and Contract Integrity

| Check | Result |
| --- | --- |
| Minimum/surgical implementation | PASS for the two Slice A runtime/test files. |
| No unrelated product-code changes | PASS. |
| Assigned cases map to T1/T2 | PASS at `.specs/features/parallel-slice-executor/tests.md:53-56`. |
| Cases assert contracted outcomes | FAIL under `docs/guidelines/TEST-CONTRACT.md:53-55`: UT-001 does not prove ordered activation; EXE-03/04/19 lack boundary-order assertions. |
| Security residual review | FAIL only for concrete SEC-004 ordering path; 0 Critical and 0 High findings. |
| Public QA dispatch | Not applicable to this technical Slice A verification; QA was not run. |

## Ranked Gaps / Fix Tasks

1. **Major — EXE-03:** extend the owning integration test to observe persisted pending receipts before worker, acquire, and release effects. M2 proves worker durability can regress undetected.
2. **Major — EXE-04:** add crash-window reconciliation tests for pending acquire, worker, and release receipts, asserting no repeated external effect. M3 proves pending acquisition can duplicate undetected.
3. **Major — SEC-004:** validate the concrete worktree destination before `create_worktree` can write/start a process, or make the adapter receive only a prevalidated bounded destination; assert an unsafe adapter path causes zero effects.
4. **Major — EXE-02/EXE-19:** replace hollow zero-effect/order coverage with one-active-task plus later ordered progress, and assert provider acquisition precedes worker dispatch.

## Summary

**Overall:** FAIL. Remediation closes disabled-mode, worktree crash recovery, resource failure/cleanup, provider receipt, and threat-model gaps. Two discrimination mutants survive and SEC-004 remains a concrete pre-effect ordering deviation. Slice A stays technically unverified; feature completion and QA remain untouched.
