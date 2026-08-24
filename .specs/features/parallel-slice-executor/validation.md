# Parallel Slice Executor Validation

**Verdict**: FAIL
**Date:** 2026-08-24
**Phase:** Technical Verification
**Scope:** Slice A prior PASS retained; Slice B/T3 technical verification added below
**Spec:** `.specs/features/parallel-slice-executor/spec.md`
**Diff range:** `d73071c..fac5577`
**Incremental remediation:** `2ae0482..fac5577`
**Verifier:** independent Verifier, author != verifier

This report retains the prior Slice A PASS and records a Slice B FAIL. It does not mark the feature
complete, run deep-review, run the Orca pilot, or perform QA Plan/QA Execute.

## Verdict

T1/T2 outcomes and their assigned contract cases are directly asserted. T2R5 closes the prior
IT-001 fingerprint: public `main(["resume", ...])` now receives a safe-mode adapter seam, loads a
persisted pending worker receipt, reconciles it, emits one correlated `resume` JSON result, and
performs no replacement effect. Removing the adapter from that public resume path kills the suite.

T2R4 also matches AD-012: remediation accounting is keyed by requirement, root cause, and concrete
failure path; only the third failed remediation of the same fingerprint halts, while a distinct
blocker starts independently.

## Task and Contract Disposition

| Owner | Case | Evidence | Result |
| --- | --- | --- | --- |
| T1 | UT-001 | `tools/test_parallel_executor.py:90-100` asserts illegal/out-of-order transitions; `:188-202` asserts disabled serial/no adapter construction; `:712-732,901-930` assert one active same-slice task and exact order. | PASS |
| T1 | UT-003 | `tools/test_parallel_executor.py:103-116,774-835` assert foreign, malformed, nested-secret, and unreconciled state serializes before adapter effects. | PASS |
| T1 | SEC-001 | `.agents/skills/autonomous/scripts/parallel_execute.py:71-174` validates nested state/action/lease receipts; `tools/test_parallel_executor.py:806-835` asserts malformed nested state yields fallback and `adapter.effects == []`. | PASS |
| T1 | SEC-002 | `tools/test_parallel_executor.py:119-148` asserts Git-common placement, no versioned receipt, and preservation of prior JSON across injected pre-rename failure. | PASS |
| T1 | SEC-003 | `.agents/skills/autonomous/scripts/parallel_execute.py:227-248`; `tools/test_parallel_executor.py:151-168` asserts exact argv, `shell is False`, and bounded timeout. | PASS |
| T1 | SEC-004 | `tools/test_parallel_executor.py:170-184,867-880` asserts traversal/symlink/escape rejection and zero adapter effects. | PASS |
| T2 | UT-002 | `tools/test_parallel_executor.py:246-265` asserts accepted replay creates no new effects; `:748-769,1014-1057` assert pending worktree/acquire/worker/release reconciliation without repeated effects. | PASS |
| T2 | UT-007 | `tools/test_parallel_executor.py:299-348` asserts `Resources: none` makes zero provider calls and a resource lane starts only with a correlated prepared/redacted lease. | PASS |
| T2 | UT-008 | `tools/test_parallel_executor.py:355-472,514-572` asserts malformed/duplicate/foreign/timeout/cleanup failure outcomes and exact-once owned cleanup. | PASS |
| T2 | IT-001 | `tools/test_parallel_executor.py:577-607` asserts one-object verb output and read-only status; `:610-686` seeds safe persisted pending state, invokes public `main(["resume", ...], adapter_factory=...)`, and asserts accepted correlated receipt, `adapter.reconciled == ["worker"]`, and `adapter.effects == []`. | PASS |
| T2 | SEC-007 | `tools/test_parallel_executor.py:514-534` asserts resource failures return serial recovery with zero worker dispatch; `:994-1009` proves persisted acquire precedes worker. | PASS |
| T2 | SEC-008 | `tools/test_parallel_executor.py:355-391,539-553,1014-1057` asserts foreign release rejection, owned idempotent retry, and no repeated recovered release. | PASS |
| T2R4 | IT-008 | `docs/guidelines/REVIEW-ROUNDS.md:89-91` defines immutable per-fingerprint accounting; `tools/shared/tests/qa-skills.test.ts:237-260` asserts exact components, independent counters, third-failure halt, reopening retention, and canonical pointers. | PASS |

**Assigned-case status:** 13 PASS, 0 FAIL.

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | Assertion evidence | Result |
| --- | --- | --- | --- |
| EXE-01 | Disabled returns serial and performs no worktree, worker, Git, planner, or resource effect. | `tools/test_parallel_executor.py:188-202,691-705` asserts `reason == "disabled-mode"`, serial lane, forbidden seams untouched, and adapter unconstructed. | PASS |
| EXE-02 | At most one active worker per slice; declared task order remains intact. | `tools/test_parallel_executor.py:712-732,901-930` asserts T2 is absent while T1 runs, then exact `worktree:T1, worker:T1, worktree:T2, worker:T2` order. | PASS |
| EXE-03 | Every external action has a persisted key derived from feature, slice, task, action, and source checkpoint before the effect. | Key material is `.agents/skills/autonomous/scripts/parallel_execute.py:333-335`; pending persistence is asserted at `tools/test_parallel_executor.py:853-862,994-1009`. | PASS |
| EXE-04 | Restart reconciles persisted accepted/pending receipts without recreating worktree, worker, or lease effects. | `tools/test_parallel_executor.py:246-265,748-769,1014-1057`; public safe resume at `:610-686`; sensor M1 and M2 killed. | PASS |
| EXE-05 | Malformed, foreign, or unreconcilable state selects named serial recovery before adapter effects. | `tools/test_parallel_executor.py:774-835` asserts `state:`/`unreconciled-pending` reasons and `adapter.effects == []`. | PASS |
| EXE-18 | `Resources: none` permits worktree concurrency without acquisition. | `tools/test_parallel_executor.py:299-317` asserts successful dispatch, zero provider construction, and only worktree/worker effects; sensor M3 killed. | PASS |
| EXE-19 | Resource acquisition receives the complete argv-only correlated request before worker start. | `tools/test_parallel_executor.py:337-345,452-472,994-1009` asserts exact fields/argv/input and effect order. | PASS |
| EXE-20 | Only unique, correlated, prepared, resource-matching, redacted leases are accepted. | Normalizer is `.agents/skills/autonomous/scripts/parallel_execute.py:338-361`; assertions at `tools/test_parallel_executor.py:396-472,1014-1057`. | PASS |
| EXE-21 | Missing, timed-out, malformed, duplicate, or cleanup-failed providers refuse parallel dispatch and report fallback. | `tools/test_parallel_executor.py:514-572` asserts exact fallback reasons, zero worker dispatch, and failed cleanup receipt. | PASS |
| EXE-22 | Accepted, halted, or abandoned workers release owned leases exactly once and retain evidence. | `tools/test_parallel_executor.py:355-391,539-553,1014-1057` asserts one provider release, released state, and idempotent replay. | PASS |
| EXE-23 | A blocking finding is fingerprinted by requirement, root cause, and concrete failure path, with its own failed-remediation count. | `docs/guidelines/REVIEW-ROUNDS.md:89-90`; `tools/shared/tests/qa-skills.test.ts:237-240`. | PASS |
| EXE-24 | A distinct blocker starts independently and does not consume a closed blocker's count. | `docs/guidelines/REVIEW-ROUNDS.md:91`; `tools/shared/tests/qa-skills.test.ts:241-243`. | PASS |
| EXE-25 | Same fingerprint halts only after three failed remediations; wording/reopening preserves identity and count. | `docs/guidelines/REVIEW-ROUNDS.md:89-91`; `tools/shared/tests/qa-skills.test.ts:240-243`. | PASS |

**Acceptance status:** 13 PASS, 0 FAIL for Slice A.

## Security Requirements

| Requirement | Evidence | Result |
| --- | --- | --- |
| SEC-001 | `.agents/skills/autonomous/scripts/parallel_execute.py:71-174`; `tools/test_parallel_executor.py:103-116,774-835`. | PASS |
| SEC-002 | `.agents/skills/autonomous/scripts/parallel_execute.py:251-303`; `tools/test_parallel_executor.py:119-148`. | PASS |
| SEC-003 | `.agents/skills/autonomous/scripts/parallel_execute.py:227-248`; `tools/test_parallel_executor.py:151-168,452-472`. | PASS |
| SEC-004 | `.agents/skills/autonomous/scripts/parallel_execute.py:201-224,306-324`; `tools/test_parallel_executor.py:170-184,867-880`. | PASS |
| SEC-007 | `tools/test_parallel_executor.py:299-348,514-534,994-1009`. | PASS |
| SEC-008 | `tools/test_parallel_executor.py:355-391,539-553,1014-1057`. | PASS |

**Security status:** 6 PASS, 0 FAIL.

## Prior Blocker Reconciliation

| Fingerprint | Count/disposition |
| --- | --- |
| `IT-001/EXE-04 + CLI resume lacks adapter reconciliation + persisted pending safe-mode worker` | CLOSED by T2R5. The new assertion at `tools/test_parallel_executor.py:610-686` proves the public entrypoint path; mandatory sensor M1 kills removing its adapter. No failed post-fix gate occurred in this verification. |
| T2R1-T2R3 distinct blockers | Remain closed by their existing direct assertions; they do not consume the IT-001 fingerprint count under AD-012 and `docs/guidelines/REVIEW-ROUNDS.md:89-91`. |

## Gate Evidence

- **Executor:** `python3 tools/test_parallel_executor.py` -> exit 0, `27 passed, 0 failed`; 0 skipped.
- **IT-008 targeted:** `npm_config_offline=true npx vitest run tools/shared/tests/qa-skills.test.ts` -> exit 0, 1 file and 23 tests passed; 0 failed/skipped.
- **Before feature:** executor suite absent at `d73071c`; **after T2R5:** 27 tests; delta +27.
- **Strict spec:** `python3 /Users/antoniofulg/Projects/my-workflow/.agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-executor/spec.md` -> exit 0, 0 errors, 0 warnings.
- **Strict tasks:** `python3 /Users/antoniofulg/Projects/my-workflow/.agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-executor/tasks.md` -> exit 0, 0 errors, 0 warnings.
- **AD index:** `python3 tools/ad-index.py --check` -> exit 0, `AD-INDEX.md up to date`.
- **Full diff:** `git diff --check d73071c..fac5577` -> exit 0, no output.
- **Incremental diff:** `git diff --check 2ae0482..fac5577` -> exit 0, no output.
- **Compile:** `python3 -m py_compile .agents/skills/autonomous/scripts/parallel_execute.py tools/test_parallel_executor.py` -> exit 0.

## Discrimination Sensor

Baseline real-tree porcelain was empty. Each mutation ran in its own detached temporary worktree at
`fac5577`; all scratches were removed. Real-tree porcelain returned to the same baseline before this
report edit.

| Mutation | Behavior fault | Directed result | Outcome |
| --- | --- | --- | --- |
| M1 | Public CLI `resume` passes no adapter factory to `Coordinator`, bypassing construction/reconciliation. | Executor suite exit 1 at `tools/test_parallel_executor.py:680`, `assert result["fallback"] is False`. | KILLED |
| M2 | Pending worker always calls `start_worker` instead of `reconcile_action`, allowing a duplicate effect. | Executor suite exit 1 at `tools/test_parallel_executor.py:683`, missing reconciled `external_id == "dispatch-resumed"`. | KILLED |
| M3 | `Resources: none` enters the acquisition branch and requires a provider. | Executor suite exit 1 at `tools/test_parallel_executor.py:861`, unexpected fallback. | KILLED |

**Sensor:** lightweight, 3 injected, 3 killed, 0 survived. PASS.

## Code Quality and Contract Integrity

| Check | Result |
| --- | --- |
| Minimum/surgical T2R5 change | PASS: one optional entrypoint adapter seam and one contracted integration case. |
| No scope creep in incremental remediation | PASS: production change is limited to adapter selection/injection for non-status public commands. |
| IT-001 asserts contracted outcome rather than implementation shape | PASS: persisted pending state, correlated receipt, public `resume` JSON, and zero duplicate effects are observable assertions. |
| T1/T2 per-layer coverage and spec outcomes | PASS: 13/13 assigned cases, 13/13 Slice A EXE criteria, and 6/6 Slice A security requirements. |
| Hollow-case rule | PASS under `docs/guidelines/TEST-CONTRACT.md:47-55`; the prior hollow IT-001 path now fails when required reconciliation is removed. |

## Ranked Gaps

None for Slice A technical verification.

## Summary

**Overall:** PASS for Slice A only. T1/T2 and T2R4/T2R5 match their spec-defined outcomes; all
assigned tests and gates pass; all three behavior mutants die. T3-T7, feature completion,
deep-review, QA Plan, and QA Execute remain outside this verdict.

---

## Slice B / T3 Technical Verification

**Verdict:** FAIL
**Date:** 2026-08-24
**Diff range:** `cbf5b62..77736e6`
**Tests in scope:** IT-002–IT-004, SEC-005, SEC-006
**Verifier:** independent Verifier, author != verifier

T3 is not technically verified. Its seven recording-double tests pass, but the public coordinator
does not drive the adapter's event lifecycle, the adapter interprets `worker-read` output as a
completion event contrary to the live Orca contract, and one required read-before-release mutation
survives. The prior Slice A PASS remains unchanged.

### Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | Evidence | Result |
| --- | --- | --- | --- |
| EXE-06 | Validated child Git worktree exists before provider preparation and Orca attaches only to that checkout. | Core derives and creates before worker start at `.agents/skills/autonomous/scripts/parallel_execute.py:638-705,714-762`; adapter command assertion is `tools/test_orca_adapter.py:86-103`. The test constructs a directory before calling the adapter but does not walk the coordinator-to-adapter boundary required by IT-002. | GAP |
| EXE-07 | Exact worktree, branch, run, task, dispatch, terminal, and source HEAD are validated before lane becomes running. | Core transitions the lane to `running` immediately after worktree creation at `.agents/skills/autonomous/scripts/parallel_execute.py:704-707`; worker receipt is not obtained until `:753-768`. Adapter validation at `.agents/skills/autonomous/scripts/orca_adapter.py:167-190` substitutes missing worktree/lane/idempotency fields from local expectations. `tools/test_orca_adapter.py:97-103` asserts a fake already populated with those fields. | FAIL |
| EXE-08 | `worker_done` is read, correlated to the dispatched task, accepted by the coordinator, then released. | Adapter calls `worker-read` at `.agents/skills/autonomous/scripts/orca_adapter.py:246-250`, while live `orca orchestration worker-read --help` defines bounded transcript/terminal output; live completion arrives through the Run delivery returned by `check`. Coordinator has no call to `read_worker` or adapter `release`; its only worker seam is start at `.agents/skills/autonomous/scripts/parallel_execute.py:753-792`. Sensor M1 proves release can precede validation without test failure. | FAIL |
| EXE-09 | Clean waiter ends its turn; only the declared dependency event starts follow-up on the same terminal. | Direct fake test at `tools/test_orca_adapter.py:152-170` kills a changed terminal, but coordinator never calls `end_waiter` or `follow_up`. No public state transition marks the lane waiting. | FAIL |
| EXE-10 | Missing dependency uses Orca blocking wait and emits no model polling instruction; timeout leaves state unchanged. | `tools/test_orca_adapter.py:175-184` asserts a fake timeout and argv shape. Adapter sends `check --terminal <worker-terminal>` at `.agents/skills/autonomous/scripts/orca_adapter.py:252-272`; live contract says coordinator `check` consumes the bound Run's FIFO Delivery. Coordinator never invokes `wait_events`, so no public resume path is covered. | FAIL |
| EXE-11 | Missing, mismatched, dirty, duplicate, escalated, or failed receipts halt the lane, choose serial recovery, and start no replacement. | `tools/test_orca_adapter.py:189-209` only proves direct adapter exceptions for five fake events. Coordinator does not consume those events or map them to lane halt/serial recovery. Missing receipts and duplicate lifecycle deliveries are not asserted at the public boundary. | FAIL |
| SEC-005 | Every Orca response is correlated to current idempotency key and declared lane. | `.agents/skills/autonomous/scripts/orca_adapter.py:177-181` uses `data.get(field, expected_value)`, so missing provider fields are accepted and manufactured. Direct probe returned `missing_fields_accepted=true`. `tools/test_orca_adapter.py:54-68` builds the expected fields into the fake instead of proving rejection when absent. | FAIL |
| SEC-006 | Logs, errors, and state redact environment values and worker transcript bodies. | Top-level keys are removed at `.agents/skills/autonomous/scripts/orca_adapter.py:238-242` and the direct fake asserts absence at `tools/test_orca_adapter.py:128-147`. The live `worker-read` response is transcript/output data rather than this fake event schema, and `tools/test_orca_adapter.py:214-222` supplies no secret to its error/state check. No evidence proves nested live output or errors are redacted before persistence/logging. | GAP |

**Spec-anchored status:** 0 PASS, 6 FAIL, 2 GAP for Slice B.

### Test Contract Disposition

| Case | Contracted outcome | Evidence | Result |
| --- | --- | --- | --- |
| IT-002 | Worktree precedes worker start; receipt contains every correlated ID. | `tools/test_orca_adapter.py:86-103`; early running transition at `.agents/skills/autonomous/scripts/parallel_execute.py:704-707`; missing receipt fields accepted at `.agents/skills/autonomous/scripts/orca_adapter.py:177-181`. | HOLLOW / FAIL |
| IT-003 | Read before release; same-terminal follow-up; timeout unchanged. | `tools/test_orca_adapter.py:128-184`; sensor M1 survived while M2 died. Coordinator never invokes these lifecycle methods. | FAIL |
| IT-004 | Invalid receipt halts lane and no replacement starts. | `tools/test_orca_adapter.py:189-209` asserts adapter exception/no second fake start, but not coordinator lane halt or serial recovery. | HOLLOW / FAIL |
| SEC-005 | Different lane or idempotency key is rejected and lane halted. | Start-response fake always supplies matching lane/key at `tools/test_orca_adapter.py:54-82`; missing fields are accepted at `.agents/skills/autonomous/scripts/orca_adapter.py:177-181`. | HOLLOW / FAIL |
| SEC-006 | Secret values never survive in output/state; only keys/redaction markers remain. | `tools/test_orca_adapter.py:128-147` covers only top-level fake keys; `:214-222` has no secret-bearing response. | GAP |

Hollow-case disposition follows `docs/guidelines/TEST-CONTRACT.md:47-55`: existence of a direct
adapter assertion does not satisfy a coordinator or live-boundary outcome it cannot discriminate.

### Live Orca Contract Check

- `orca status --json` -> runtime ready, app `1.4.188`, capability `orchestration.contract.v1` present.
- `orca skills get orca-cli` and `orca skills get orchestration` -> current version-matched guides loaded.
- `orca orchestration contract --json` -> unsupported (`Unknown command: orchestration contract`); capability and current command help are the available live contract surface.
- `orca orchestration worker-read --help` -> reads bounded worker transcript/terminal output; it is not the `worker_done` delivery reader assumed by `.agents/skills/autonomous/scripts/orca_adapter.py:246-250`.
- Current guide routes `worker_done` through `orca orchestration check --wait ...`, then requires release only after the accepted delivery is processed.

### Gate Evidence

- `python3 tools/test_orca_adapter.py` -> exit 0, `7 passed, 0 failed`; 0 skipped.
- `python3 tools/test_parallel_executor.py` -> exit 0, `27 passed, 0 failed`; 0 skipped.
- Adapter suite at `cbf5b62`: absent; at `77736e6`: 7 tests; delta +7.
- `python3 .../tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-executor/spec.md` -> exit 0, 0 errors, 0 warnings.
- `python3 .../tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-executor/tasks.md` -> exit 0, 0 errors, 0 warnings.
- `git diff --check cbf5b62..77736e6` -> exit 0, no output.
- `python3 -m py_compile .agents/skills/autonomous/scripts/orca_adapter.py tools/test_orca_adapter.py .agents/skills/autonomous/scripts/parallel_execute.py tools/test_parallel_executor.py` -> exit 0.

### Discrimination Sensor

Baseline real-tree porcelain was empty. Each mutation ran in its own detached temporary worktree at
`77736e6`; all scratches were removed. Real-tree porcelain matched the baseline before this report
edit.

| Mutation | Behavior fault | Directed result | Outcome |
| --- | --- | --- | --- |
| M1 | `release` calls `worker-release` before validating the supplied `worker_done` result. | Adapter suite exit 0, `7 passed, 0 failed`. | SURVIVED -> fix task |
| M2 | Follow-up starts on `terminal-other` instead of the receipt terminal. | Adapter suite exit 1 at `tools/test_orca_adapter.py:170`. | KILLED |
| M3 | Event correlation stops checking `task_id`. | Adapter suite exit 1 at `tools/test_orca_adapter.py:208`. | KILLED |

**Sensor:** lightweight, 3 injected, 2 killed, 1 survived. FAIL.

### Ranked Gaps and Fix Tasks

1. **Blocker** — fingerprint `EXE-08/IT-003 + release validates after destructive cleanup + invalid supplied result reaches release`: make acceptance validation precede `worker-release`, then add a negative assertion that an invalid result produces zero release calls. Sensor M1 must die.
2. **Blocker** — fingerprint `EXE-08–EXE-11 + coordinator never drives live Orca deliveries + started lane is never reconciled through check`: integrate blocking Run-delivery consumption, correlation, waiting/follow-up, accepted release, and serial-recovery transitions through the public coordinator/resume path. Prove with IT-003/IT-004 at that boundary.
3. **Major** — fingerprint `EXE-07 + lane transitions running after worktree only + worker receipt validation occurs later`: keep lane non-running until the complete correlated worker receipt is accepted; add an assertion over persisted/public lane state before and after receipt acceptance.
4. **Blocker** — fingerprint `SEC-005/SEC-006 + recording double invents receipt/event fields + live worker output/delivery schema bypasses claimed correlation and redaction`: bind validation to the live `orchestration.contract.v1` receipt and delivery shapes, reject missing correlation fields instead of filling them, and prove credential/transcript redaction with live-shaped nested fixtures.

### Slice B Summary

**Overall:** FAIL. Green gates do not discriminate the contracted public lifecycle. T3 requires an
Implementer fix and a fresh Technical Verifier. Feature completion, deep-review, Orca pilot, QA Plan,
and QA Execute remain out of scope.
