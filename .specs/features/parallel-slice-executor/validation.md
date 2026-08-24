# Parallel Slice Executor Validation

**Verdict**: FAIL
**Date:** 2026-08-24
**Phase:** Technical Verification
**Scope:** Slice A only, tasks T1/T2 after final remediation
**Spec:** `.specs/features/parallel-slice-executor/spec.md`
**Diff range:** `d73071c..9f525b4`
**Incremental remediation:** `10d9ef5..9f525b4`
**Verifier:** independent Verifier, author != verifier

This verdict covers only Slice A. It does not close the feature, verify Slices B-D, or perform QA.

## Verdict and Post-Cap Disposition

The final remediation closes pending-worker recovery, strict normalization of reconciled acquire
receipts, nested runtime-state validation, and the core-owned worktree boundary. Quick and
structural gates pass. Slice A still fails because IT-001 does not prove that the public CLI
`resume` command reconciles persisted state through an adapter. A behavior-level mutant that
removes adapter construction only for CLI `resume` survives the complete executor suite.

This is the residual blocker after the final fix round. No product or test fix was made here.

## Task and Contract Disposition

| Owner | Case | Disposition | Evidence |
| --- | --- | --- | --- |
| T1 | UT-001 | PASS | Legal/out-of-order transition assertions at `tools/test_parallel_executor.py:88-98`; disabled no-effect at `:186-198,608-627`; one-active/order at `:818-847`. |
| T1 | UT-003 | PASS | Foreign/top-level malformed rejection at `tools/test_parallel_executor.py:101-114`; foreign/unreconciled persisted state at `:691-718`; nested malformed lease rejection before adapter effects at `:723-752`. |
| T1 | SEC-001 | PASS | Nested lease/action validation at `.agents/skills/autonomous/scripts/parallel_execute.py:94-174`; malformed nested lease yields serial recovery and zero effects at `tools/test_parallel_executor.py:723-752`. |
| T1 | SEC-002 | PASS | Git-common placement and atomic prior-state preservation at `tools/test_parallel_executor.py:117-146`. |
| T1 | SEC-003 | PASS | Exact argv, `shell is False`, and bounded timeout at `tools/test_parallel_executor.py:149-165`. |
| T1 | SEC-004 | PASS | Path/symlink rejection at `tools/test_parallel_executor.py:168-180`; unsafe destination returns before adapter effects at `:784-797`. |
| T2 | UT-002 | PASS | Accepted replay at `tools/test_parallel_executor.py:244-263`; pending worktree at `:665-686`; pending acquire, worker, and release recovery with zero repeated effects at `:931-974`. |
| T2 | UT-007 | PASS | `Resources: none` bypass and correlated prepared lease at `tools/test_parallel_executor.py:297-346`; recovered acquire receipt normalization at `:940-973`. |
| T2 | UT-008 | PASS | Provider rejection paths at `tools/test_parallel_executor.py:394-470,512-570`; owned cleanup and exact-once retry at `:353-389,537-570`. |
| T2 | IT-001 | FAIL | `tools/test_parallel_executor.py:575-603` invokes all three public verbs and proves one-object/verb output, but runs only `disabled` mode. It does not establish persisted state, load a recording adapter, or assert reconciliation/no repeated effect. Sensor M3 survives. |
| T2 | SEC-007 | PASS | Resource failure paths assert serial recovery and zero worker dispatch at `tools/test_parallel_executor.py:512-534`; accepted acquire precedes worker at `:911-926`. |
| T2 | SEC-008 | PASS | Duplicate/foreign lease rejection and idempotent owned cleanup at `tools/test_parallel_executor.py:353-389`; pending release recovery avoids a second provider effect at `:931-974`. |

**Assigned-case status:** 11 PASS, 1 FAIL across the 12 T1/T2 cases.

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | `file:line` + assertion evidence | Result |
| --- | --- | --- | --- |
| EXE-01 | Disabled returns serial without worktree, worker, event, Git, or resource effects. | `tools/test_parallel_executor.py:608-627` installs forbidden Git/planner/adapter seams and asserts `reason == "disabled-mode"`; production short-circuit is `.agents/skills/autonomous/scripts/parallel_execute.py:606-615`. | PASS |
| EXE-02 | At most one active worker per slice and declared task order is preserved. | `tools/test_parallel_executor.py:818-847` asserts T2 is absent while T1 runs, then exact `worktree:T1, worker:T1, worktree:T2, worker:T2` order. | PASS |
| EXE-03 | Every external effect observes a persisted idempotency key derived from feature, slice, task, action, and source checkpoint. | Key material at `.agents/skills/autonomous/scripts/parallel_execute.py:522-531`; pending worktree/acquire/worker/release observations at `tools/test_parallel_executor.py:770-779,911-926`. | PASS |
| EXE-04 | Restart reconciles persisted receipts without recreating accepted or pending worktree, worker, or lease effects. | Accepted replay at `tools/test_parallel_executor.py:244-263`; pending worktree at `:665-686`; pending acquire/worker/release reconciliation and zero repeated effects at `:931-974`; sensor M1 killed. | PASS |
| EXE-05 | Malformed, foreign, or unreconcilable state serializes with a decisive reason and no adapter effect. | Runtime validation at `.agents/skills/autonomous/scripts/parallel_execute.py:71-174`; foreign/unreconciled paths at `tools/test_parallel_executor.py:691-718`; unredacted nested lease at `:723-752`. | PASS |
| EXE-18 | `Resources: none` permits worktree concurrency without acquisition. | `tools/test_parallel_executor.py:297-315` asserts successful dispatch, zero provider construction, and only worktree/worker effects. | PASS |
| EXE-19 | Resource acquisition receives the complete argv-only request before worker start. | Request fields at `tools/test_parallel_executor.py:335-343,457-470`; exact worktree/acquire/worker/release order at `:911-926`. | PASS |
| EXE-20 | Only a unique, correlated, prepared, resource-matching, redacted lease is accepted. | Validator at `.agents/skills/autonomous/scripts/parallel_execute.py:325-357`; fresh rejection/acceptance at `tools/test_parallel_executor.py:394-470`; recovered receipt normalized at production `:738-747` and asserted at tests `:940-973`; sensor M2 killed. | PASS |
| EXE-21 | Missing, timed-out, malformed, duplicate, or cleanup-failed providers refuse parallel dispatch. | `tools/test_parallel_executor.py:512-570` asserts serial reasons, zero worker effects, and retained failed cleanup receipt. | PASS |
| EXE-22 | Accepted, halted, or abandoned workers release owned leases exactly once and retain cleanup evidence. | `tools/test_parallel_executor.py:353-389,537-570,931-974` asserts exact-once release, retry behavior, terminal cleanup, and recovered release without another provider call. | PASS |

**Acceptance status:** 10 PASS, 0 FAIL across the ten Slice A EXE requirements. IT-001 remains a
separate assigned integration-contract failure under `docs/guidelines/TEST-CONTRACT.md:47-55`.

## Security Requirements

| Requirement | Evidence | Result |
| --- | --- | --- |
| SEC-001 | `.agents/skills/autonomous/scripts/parallel_execute.py:71-174`; `tools/test_parallel_executor.py:101-114,691-752`. | PASS |
| SEC-002 | `tools/test_parallel_executor.py:117-146`. | PASS |
| SEC-003 | `tools/test_parallel_executor.py:149-165,457-470`. | PASS |
| SEC-004 | `tools/test_parallel_executor.py:168-180,784-797`. | PASS |
| SEC-007 | `tools/test_parallel_executor.py:512-534,911-926`. | PASS |
| SEC-008 | `tools/test_parallel_executor.py:353-389,931-974`. | PASS |

**Security status:** 6 PASS, 0 FAIL for Slice A.

## Prior Gap Reconciliation

| Prior gap | Final disposition |
| --- | --- |
| Pending worker recovery was evidence-zero. | CLOSED: fixture stores worker `pending`; adapter returns a reconciled worker; assertions require `reconcile-worker` and zero fresh effects at `tools/test_parallel_executor.py:946-974`. Sensor M1 killed forced replacement dispatch. |
| Reconciled acquire receipts bypassed strict normalization. | CLOSED: both fresh and recovered receipts call `normalize_lease_receipt` at `.agents/skills/autonomous/scripts/parallel_execute.py:738-745`; normalized key/resources/prepared/environment fields are asserted at `tools/test_parallel_executor.py:969-973`. Sensor M2 killed bypassing normalization. |
| Nested malformed runtime state could reach effects. | CLOSED: lease/action validation exists at `.agents/skills/autonomous/scripts/parallel_execute.py:94-174`; unredacted nested state serializes before adapter work at `tools/test_parallel_executor.py:723-752`. |
| Adapter-owned worktree creation remained possible. | CLOSED: `rg -n 'adapter\.create_worktree' .agents/skills/autonomous/scripts/parallel_execute.py tools/test_parallel_executor.py` exits 1 with no match; no adapter creator path remains. Only core `create_git_worktree`/`worktree_creator` remain at production `:423-429,543-547`. Worker-only adapter receives an already-created checkout at `tools/test_parallel_executor.py:979-1017`. |
| Public CLI resume was not exercised. | PARTIAL: the verb is now invoked and labeled at `tools/test_parallel_executor.py:594-603`, but only in disabled mode. Persisted-state adapter reconciliation remains evidence-zero; sensor M3 survives. |

## Gate Evidence

- **Executor gate:** `python3 tools/test_parallel_executor.py` -> exit 0, `26 passed, 0 failed`; 0 skipped.
- **Before feature:** owning suite absent at `d73071c`; **after final remediation:** 26 tests; delta +26.
- **Strict spec:** `python3 /Users/antoniofulg/Projects/my-workflow/.agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-executor/spec.md` -> exit 0, 0 errors, 0 warnings.
- **Strict tasks:** `python3 /Users/antoniofulg/Projects/my-workflow/.agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-executor/tasks.md` -> exit 0, 0 errors, 0 warnings.
- **AD index:** `python3 tools/ad-index.py --check` -> exit 0, `AD-INDEX.md up to date`.
- **Full diff:** `git diff --check d73071c..9f525b4` -> exit 0, no output.
- **Incremental diff:** `git diff --check 10d9ef5..9f525b4` -> exit 0, no output.
- **Compile:** `python3 -m py_compile .agents/skills/autonomous/scripts/parallel_execute.py tools/test_parallel_executor.py` -> exit 0.

Passing gates do not override the surviving behavior mutant or hollow IT-001 case.

## Discrimination Sensor

Baseline real-tree porcelain was empty. Each mutation ran in its own detached temporary worktree at
`9f525b4`; all scratches were removed. Real-tree porcelain returned to the baseline before this
report edit.

| Mutation | Target | Behavior fault | Directed result | Outcome |
| --- | --- | --- | --- | --- |
| M1 | `.agents/skills/autonomous/scripts/parallel_execute.py:757-762` | Disabled pending-worker reconciliation, forcing replacement `start_worker`. | exit 1 at `tools/test_parallel_executor.py:968`, missing `reconcile-worker`. | KILLED |
| M2 | `.agents/skills/autonomous/scripts/parallel_execute.py:738-745` | Stored recovered acquire mapping without `normalize_lease_receipt`. | exit 1 in runtime validation: `invalid lease environment keys: slice-A`. | KILLED |
| M3 | `.agents/skills/autonomous/scripts/parallel_execute.py:829-837` | Disabled adapter construction only for public CLI `resume`. | exit 0, `26 passed, 0 failed`. | SURVIVED -> fix task |

**Sensor:** 3 injected, 2 killed, 1 survived. FAIL.

## Code Quality and Contract Integrity

| Check | Result |
| --- | --- |
| Minimum/surgical Slice A implementation | PASS. |
| No scope creep in final remediation | PASS. |
| Core exclusively owns Git worktree creation | PASS; no `adapter.create_worktree` or `adapter.prepare_worktree` path remains. |
| Every assigned case asserts its contracted outcome | FAIL: IT-001 does not assert public CLI persisted-state reconciliation, contrary to `.specs/features/parallel-slice-executor/tests.md:18-20` and `docs/guidelines/TEST-CONTRACT.md:47-55`. |
| Spec-anchored EXE and security outcomes | PASS: 10/10 EXE and 6/6 security requirements have direct evidence. |

## Ranked Residual Blocker / Fix Task

1. **Major - IT-001 / T2:** run public CLI `resume` in `safe` mode against persisted pending state
   and a recording adapter seam; assert one JSON object names `resume`, the pending receipt is
   reconciled, and no replacement worktree/worker/lease effect occurs. The M3 adapter-removal mutant
   must fail this test. This is the only residual Slice A blocker after the final fix round.

## Summary

**Overall:** FAIL, post-cap residual. T1/T2 implementation requirements now have direct evidence,
pending worker and recovered lease mutants die, nested state is fail-closed, and adapter-owned
worktree creation is absent. IT-001 remains hollow for the public CLI's persisted-state resume path,
and its behavior mutant survives. Slice A remains technically unverified. Feature completion and QA
remain untouched.
