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
**Diff range:** `cbf5b62..f0c3e5d` (T3R1 focus: `77736e6..f0c3e5d`)
**Tests in scope:** IT-002–IT-004, SEC-005, SEC-006
**Verifier:** independent Verifier, author != verifier

T3R1 closes release-before-validation and adds the live Run-delivery completion path, but Slice B is
not technically verified. The coordinator still accepts a sparse worker receipt and marks the lane
running, never calls `end_waiter` before dependency follow-up, and persists an unredacted live waiter
payload. One strict-correlation mutant also survives. The prior Slice A PASS remains unchanged.

### Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | Evidence | Result |
| --- | --- | --- | --- |
| EXE-06 | Validated child Git worktree exists before provider preparation and Orca attaches only to that checkout. | Destination preflight is `.agents/skills/autonomous/scripts/parallel_execute.py:698-707`; accepted worktree precedes `start_worker` at `:755-836`. `tools/test_parallel_executor.py:1192-1221` asserts creation before attachment, and `tools/test_orca_adapter.py:111-129` asserts `path:<existing>` with no Orca worktree creation. | PASS |
| EXE-07 | Exact worktree, branch, run, task, dispatch, terminal, and source HEAD are validated before lane becomes running. | Orca validates the complete authoritative receipt at `.agents/skills/autonomous/scripts/orca_adapter.py:161-222,224-250`. The coordinator only checks `Mapping`, accepts it, copies whichever four fields happen to exist, then transitions at `.agents/skills/autonomous/scripts/parallel_execute.py:827-845`. `tools/test_parallel_executor.py:1183-1221` supplies only `dispatch_id/status` and still asserts successful parallel start. | FAIL |
| EXE-08 | `worker_done` is read, correlated to the dispatched task, accepted by the coordinator, then released. | Live Delivery correlation is `.agents/skills/autonomous/scripts/orca_adapter.py:252-310`; read/redaction/accept/release is `:312-405`; coordinator order is `.agents/skills/autonomous/scripts/parallel_execute.py:565,596-600`. `tools/test_parallel_executor.py:691-753` asserts `check, read, accept, release`; sensor M1 kills release-before-validation and M3 kills lifecycle bypass. | PASS |
| EXE-09 | Clean waiter ends its turn; only the declared dependency event starts follow-up on the same terminal. | Coordinator persists `waiting` at `.agents/skills/autonomous/scripts/parallel_execute.py:568-573` and can call `follow_up` at `:574-595`, but never calls `end_waiter`. Orca requires its instance-local `_ended_waiters` marker at `.agents/skills/autonomous/scripts/orca_adapter.py:407-439`. The public test explicitly observes only `wait` for waiting at `tools/test_parallel_executor.py:758-805`; only the direct same-instance adapter test at `tools/test_orca_adapter.py:173-196` reaches follow-up. | FAIL |
| EXE-10 | Missing dependency uses Orca blocking wait and emits no model polling instruction; timeout leaves state unchanged. | `.agents/skills/autonomous/scripts/orca_adapter.py:363-386` issues run-scoped `check --wait`; `tools/test_orca_adapter.py:199-230` asserts blocking argv and no follow-up/release. `tools/test_parallel_executor.py:758-805` asserts timeout keeps the lane running with only one wait call. | PASS |
| EXE-11 | Missing, mismatched, dirty, duplicate, escalated, or failed receipts halt the lane, choose serial recovery, and start no replacement. | Adapter rejection is `.agents/skills/autonomous/scripts/orca_adapter.py:252-299`; coordinator serial recovery is `.agents/skills/autonomous/scripts/parallel_execute.py:611-616`. `tools/test_parallel_executor.py:758-805` proves invalid/escalated public outcomes, while `tools/test_orca_adapter.py:265-285` proves mismatch/dirty/escalation/failure directly. No assertion supplies a duplicate Delivery or missing authoritative field through the public coordinator. | GAP |
| SEC-005 | Every Orca response is correlated to current idempotency key and declared lane. | Strict worker and Delivery checks exist at `.agents/skills/autonomous/scripts/orca_adapter.py:161-195,252-279`. Sensor M2 replaced missing-field rejection with local expected values and all 10 adapter tests still passed, so the contracted missing-field boundary is not discriminated. | GAP |
| SEC-006 | Logs, errors, and state redact environment values and worker transcript bodies. | Worker transcript is redacted at `.agents/skills/autonomous/scripts/orca_adapter.py:312-343`, asserted at `tools/test_orca_adapter.py:154-168,213-227`. `_delivery` returns raw nested `payload` at `.agents/skills/autonomous/scripts/orca_adapter.py:300-310`, and coordinator persists that object for a waiter at `.agents/skills/autonomous/scripts/parallel_execute.py:568-572`. A live-shaped probe returned `secret_survives=true` and `environment_survives=true`. | FAIL |

**Spec-anchored status:** 3 PASS, 3 FAIL, 2 GAP for Slice B.

### Test Contract Disposition

| Case | Contracted outcome | Evidence | Result |
| --- | --- | --- | --- |
| IT-002 | Worktree precedes worker start; receipt contains every correlated ID. | Worktree ordering is proven, but `tools/test_parallel_executor.py:1183-1221` contradicts the receipt half by accepting a sparse worker receipt into running state. | FAIL |
| IT-003 | Read before release; same-terminal follow-up; timeout unchanged. | Completion and timeout are proven at `tools/test_parallel_executor.py:691-805`; public follow-up is not. Coordinator omits `end_waiter` before `.agents/skills/autonomous/scripts/parallel_execute.py:586`. | FAIL |
| IT-004 | Invalid receipt halts lane and no replacement starts. | `tools/test_parallel_executor.py:758-805` proves invalid/escalated serial recovery; `tools/test_orca_adapter.py:265-285` proves four direct invalid classes. Missing and duplicate public cases have no assertion. | GAP |
| SEC-005 | Different lane or idempotency key is rejected and lane halted. | Code is strict, but sensor M2 survived the removal of missing-field rejection. Under `docs/guidelines/TEST-CONTRACT.md:53-55`, the case remains hollow for absent correlation fields. | HOLLOW / GAP |
| SEC-006 | Secret values never survive in output/state; only keys/redaction markers remain. | Transcript assertion passes at `tools/test_orca_adapter.py:154-168`; a live waiter with nested environment secret survives `_delivery` and is persisted by the coordinator. | FAIL |

Hollow-case disposition follows `docs/guidelines/TEST-CONTRACT.md:53-55`: a present test does not
cover a contracted outcome it cannot discriminate. Live schemas used by the implementation and
fixtures are the Run Delivery at `.agents/skills/autonomous/scripts/orca_adapter.py:252-310` /
`tools/test_orca_adapter.py:89-108` and worker output at `.agents/skills/autonomous/scripts/orca_adapter.py:312-343` /
`tools/test_orca_adapter.py:100-108`. No real worker or pilot was created.

### Gate Evidence

- `python3 tools/test_orca_adapter.py` -> exit 0, `10 passed, 0 failed`; 0 skipped.
- `python3 tools/test_parallel_executor.py` -> exit 0, `29 passed, 0 failed`; 0 skipped.
- Adapter suite at `cbf5b62`: absent; at `f0c3e5d`: 10 tests; delta +10.
- `python3 .../tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-executor/spec.md` -> exit 0, 0 errors, 0 warnings.
- `python3 .../tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-executor/tasks.md` -> exit 0, 0 errors, 0 warnings.
- `git diff --check cbf5b62..f0c3e5d` and `git diff --check 77736e6..f0c3e5d` -> exit 0, no output.
- `python3 -m py_compile .agents/skills/autonomous/scripts/orca_adapter.py tools/test_orca_adapter.py .agents/skills/autonomous/scripts/parallel_execute.py tools/test_parallel_executor.py` -> exit 0.

### Discrimination Sensor

Baseline real-tree porcelain was empty. Each mutation ran in its own detached temporary worktree at
`f0c3e5d`; all scratches were removed. Real-tree porcelain matched the baseline before this report
edit.

| Mutation | Behavior fault | Directed result | Outcome |
| --- | --- | --- | --- |
| M1 | `release` performs `worker-release` before checking `accepted`. | Adapter suite exit 1 at `tools/test_orca_adapter.py:242`; unexpected destructive call. | KILLED |
| M2 | Missing worker receipt fields are filled from local expectations instead of rejected. | Adapter suite exit 0, `10 passed, 0 failed`. | SURVIVED -> fix task |
| M3 | Coordinator resume marks a running lane complete without `check/read/accept/release`. | Executor suite exit 1 at `tools/test_parallel_executor.py:753`. | KILLED |

**Sensor:** lightweight, 3 injected, 2 killed, 1 survived. FAIL.

### Prior Fingerprint Re-derivation and AD-012 Counts

`docs/guidelines/REVIEW-ROUNDS.md:89-91` is canonical for AD-012 accounting: identity is requirement +
root cause + failure path, and only failed scoped post-fix verification increments that fingerprint.

| Prior fingerprint | T3R1 disposition | Failed-remediation count |
| --- | --- | --- |
| `EXE-08/IT-003 + release validates after destructive cleanup + invalid supplied result reaches release` | CLOSED; `tools/test_orca_adapter.py:235-247` and sensor M1 reject release before acceptance. | 0 |
| `EXE-08–EXE-11 + coordinator never drives live Orca deliveries + started lane is never reconciled through check` | CLOSED for completion/check by `.agents/skills/autonomous/scripts/parallel_execute.py:553-610` and sensor M3. A distinct EXE-09 waiter fingerprint remains below. | 0 |
| `EXE-07 + lane transitions running after worktree only + worker receipt validation occurs later` | REMAINS: coordinator accepts a sparse receipt at `.agents/skills/autonomous/scripts/parallel_execute.py:837-845`; `tools/test_parallel_executor.py:1183-1221` reaches running without the exact IDs. | 1 |
| `SEC-005/SEC-006 + recording double invents receipt/event fields + live worker output/delivery schema bypasses claimed correlation and redaction` | PARTIAL: live schemas are separated and start correlation is strict, but M2 survives and nested Delivery secrets remain unredacted. | 1 |

Distinct fingerprints first observed in this pass start independently at one: `EXE-09/IT-003 +
coordinator omits end_waiter + dependency follow-up reaches adapter without the ended-turn marker` and
`EXE-11/IT-004 + no missing/duplicate public assertion + those serial-recovery branches are not
discriminated`.

### Ranked Gaps and Fix Tasks

1. **Blocker, count 1** — fingerprint `SEC-006 + raw nested Delivery payload is returned + waiting coordinator persists environment secret`: redact credential-shaped values before `_delivery` returns and assert the public persisted state contains keys/markers only.
2. **Blocker, count 1** — fingerprint `EXE-09/IT-003 + coordinator omits end_waiter + dependency follow-up reaches adapter without ended-turn marker`: drive end-waiter and dependency follow-up through public resume, including restart-safe state, then assert same terminal and no premature follow-up.
3. **Major, count 1** — fingerprint `EXE-07 + coordinator accepts incomplete worker receipt + lane becomes running without exact IDs`: validate the full worker receipt at the coordinator boundary and make the sparse `WorkerOnlyAdapter` path serialize.
4. **Major, count 1** — fingerprint `SEC-005 + missing-field rejection has no negative assertion + local-value substitution survives`: add live-shaped absent-field cases at the canonical adapter suite; sensor M2 must die.
5. **Major, count 1** — fingerprint `EXE-11/IT-004 + missing/duplicate public outcomes are unasserted + serial recovery is not discriminated`: exercise missing and duplicate Deliveries through coordinator resume and assert serial lane/no replacement.

### Slice B Summary

**Overall:** FAIL. T3R1 closes two prior blocker paths, but one sensor survives and four public/security
outcomes remain failed or hollow. Route the ranked gaps to an Implementer, then use a fresh Technical
Verifier. This verdict does not complete the feature and does not authorize deep-review, a real Orca
pilot, QA Plan, or QA Execute.
