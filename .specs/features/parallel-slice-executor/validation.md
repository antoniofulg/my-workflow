# Parallel Slice Executor Validation

**Verdict**: PASS
**Date:** 2026-08-24
**Phase:** Technical Verification
**Scope:** Slice A prior PASS retained; Slice B/T3 PASS retained; Slice C/T4R2 independently re-verified
**Spec:** `.specs/features/parallel-slice-executor/spec.md`
**Diff range:** `b797777..c33425e`
**Incremental remediation:** `4c0a7fc..c33425e`
**Verifier:** independent Verifier, author != verifier

This report retains the prior Slice A PASS and records a Slice B PASS. It does not mark the feature
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

**Verdict:** PASS
**Date:** 2026-08-24
**Diff range:** `cbf5b62..591e68e` (T3R2 focus: `f0c3e5d..591e68e`)
**Tests in scope:** IT-002–IT-004, SEC-005, SEC-006
**Verifier:** independent Verifier, author != verifier

T3R2 closes all five Slice B fingerprints. Exact worker receipts are checked before `running`, clean
waiters end and persist before restart-safe same-terminal follow-up, nested Delivery secrets are
redacted, and missing/duplicate receipts select serial recovery. The prior Slice A PASS remains
unchanged.

### Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | Evidence | Result |
| --- | --- | --- | --- |
| EXE-06 | Validated child Git worktree exists before provider preparation and Orca attaches only to that checkout. | Destination preflight is `.agents/skills/autonomous/scripts/parallel_execute.py:725-745`; accepted worktree is persisted before worker start at `:782-808,854-866`. `tools/test_orca_adapter.py:111-129` asserts `path:<existing>` plus all receipt IDs; `tools/test_parallel_executor.py:1298-1328` proves a precreated worktree is observed even when a sparse worker receipt is rejected. | PASS |
| EXE-07 | Exact worktree, branch, run, task, dispatch, terminal, and source HEAD are validated before lane becomes running. | Adapter validation is `.agents/skills/autonomous/scripts/orca_adapter.py:180-215`; coordinator validation precedes acceptance/transition at `.agents/skills/autonomous/scripts/parallel_execute.py:621-643,854-873`. `tools/test_orca_adapter.py:311-329` rejects every missing authoritative field; `tools/test_parallel_executor.py:1298-1328` rejects a sparse receipt. | PASS |
| EXE-08 | `worker_done` is read, correlated to the dispatched task, accepted by the coordinator, then released. | Delivery correlation is `.agents/skills/autonomous/scripts/orca_adapter.py:271-330`; read/accept/release is `:332-425`; coordinator order is `.agents/skills/autonomous/scripts/parallel_execute.py:599-612`. `tools/test_parallel_executor.py:702-764` asserts exact `check, read, accept, release`; `tools/test_orca_adapter.py:154-168` asserts the adapter order. | PASS |
| EXE-09 | Clean waiter ends its turn; only the declared dependency event starts follow-up on the same terminal. | Coordinator calls `end_waiter`, persists `ended`, then handles dependency follow-up at `.agents/skills/autonomous/scripts/parallel_execute.py:565-598`; adapter enforces ended state and same terminal at `.agents/skills/autonomous/scripts/orca_adapter.py:427-459`. `tools/test_parallel_executor.py:833-881` asserts end-before-restart-follow-up and terminal identity. Sensor M3 kills omission of `end_waiter`. | PASS |
| EXE-10 | Missing dependency uses Orca blocking wait and emits no model polling instruction; timeout leaves state unchanged. | `.agents/skills/autonomous/scripts/orca_adapter.py:383-406` issues run-scoped `check --wait`; `tools/test_orca_adapter.py:203-212` asserts timeout and no send/start/release, while `tools/test_parallel_executor.py:769-826` asserts running state remains unchanged. | PASS |
| EXE-11 | Missing, mismatched, dirty, duplicate, escalated, or failed receipts halt the lane, choose serial recovery, and start no replacement. | Adapter rejection is `.agents/skills/autonomous/scripts/orca_adapter.py:271-301`; coordinator serial recovery is `.agents/skills/autonomous/scripts/parallel_execute.py:614-619,874-883`. `tools/test_orca_adapter.py:280-294,311-354` asserts duplicate, missing, mismatch, dirty, escalation, and failure; `tools/test_parallel_executor.py:769-826` asserts public missing/duplicate outcomes become serial with no release/replacement. | PASS |
| SEC-005 | Every Orca response is correlated to current idempotency key and declared lane. | Strict adapter correlation is `.agents/skills/autonomous/scripts/orca_adapter.py:180-215,271-298`; coordinator independently validates the full receipt at `.agents/skills/autonomous/scripts/parallel_execute.py:621-643`. `tools/test_orca_adapter.py:311-329` asserts each missing field halts; sensor M1 kills local-value substitution. | PASS |
| SEC-006 | Logs, errors, and state redact environment values and worker transcript bodies. | Recursive redaction is `.agents/skills/autonomous/scripts/orca_adapter.py:17-33,318-329`; transcript redaction is `:332-363`. `tools/test_orca_adapter.py:257-275` asserts nested token/password removal; `tools/test_parallel_executor.py:822-825,881` asserts persisted waiter/state contains no secret. Sensor M2 kills raw payload persistence. | PASS |

**Spec-anchored status:** 8 PASS, 0 FAIL, 0 GAP for Slice B.

### Test Contract Disposition

| Case | Contracted outcome | Evidence | Result |
| --- | --- | --- | --- |
| IT-002 | Worktree precedes worker start; receipt contains every correlated ID. | `tools/test_orca_adapter.py:111-129` asserts existing-worktree attachment and exact IDs; `tools/test_parallel_executor.py:1298-1328` asserts sparse receipt rejection before `running`. | PASS |
| IT-003 | Read before release; same-terminal follow-up; timeout unchanged. | `tools/test_parallel_executor.py:702-764` asserts completion order, `:769-826` asserts timeout/waiter outcomes, and `:833-881` asserts persisted end before restart follow-up on the same terminal. | PASS |
| IT-004 | Invalid receipt halts lane and no replacement starts. | `tools/test_orca_adapter.py:280-294,311-354` covers duplicate, missing, mismatched, dirty, escalated, and failed receipts; `tools/test_parallel_executor.py:769-826` proves public serial recovery for missing/duplicate delivery. | PASS |
| SEC-005 | Different lane, idempotency key, or absent authoritative field is rejected and lane halted. | `tools/test_orca_adapter.py:311-329,334-354` asserts missing/mismatched correlation; `tools/test_parallel_executor.py:1298-1328` asserts the coordinator rejects sparse receipts. Sensor M1 dies. | PASS |
| SEC-006 | Secret values never survive in output/state; only keys/redaction markers remain. | `tools/test_orca_adapter.py:154-168,257-275` asserts transcript and nested Delivery redaction; `tools/test_parallel_executor.py:822-825,881` asserts persisted state excludes the secret. Sensor M2 dies. | PASS |

All five cases assert their contracted outcomes at the owning adapter and public coordinator layers.
No hollow-case consultation was needed for T3R2. No real worker or Orca pilot was created.

### Gate Evidence

- `python3 tools/test_orca_adapter.py` -> exit 0, `13 passed, 0 failed`; 0 skipped.
- `python3 tools/test_parallel_executor.py` -> exit 0, `30 passed, 0 failed`; 0 skipped.
- Adapter suite at `cbf5b62`: absent; at `591e68e`: 13 tests; delta +13. Executor suite: 30 tests at `591e68e`.
- `python3 .../tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-executor/spec.md --strict` -> exit 0, 0 errors, 0 warnings.
- `python3 .../tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-executor/tasks.md --strict` -> exit 0, 0 errors, 0 warnings.
- `python3 tools/ad-index.py --check` -> exit 0, `AD-INDEX.md up to date`.
- `git diff --check cbf5b62..591e68e` and `git diff --check f0c3e5d..591e68e` -> exit 0, no output.
- `python3 -m py_compile .agents/skills/autonomous/scripts/orca_adapter.py tools/test_orca_adapter.py .agents/skills/autonomous/scripts/parallel_execute.py tools/test_parallel_executor.py` -> exit 0.
- `python3 .../tlc-spec-driven/scripts/validate_state.py parallel-slice-executor` -> exit 1 because the report-level feature verdict remains `FAIL`; expected, since Slice B PASS does not close T4-T7, pilot, deep-review, or QA.

### Discrimination Sensor

Baseline real-tree porcelain was empty. Each mutation ran in its own detached temporary worktree at
`591e68e`; all scratches were removed. Real-tree porcelain matched the baseline before this report
edit.

| Mutation | Behavior fault | Directed result | Outcome |
| --- | --- | --- | --- |
| M1 | Missing worker receipt fields are filled from local expectations instead of rejected. | Adapter suite exit 1 at `tools/test_orca_adapter.py:328`: `missing worktree_id must halt`. | KILLED |
| M2 | Nested Delivery payload bypasses `_redact_payload` and returns raw secrets. | Adapter suite exit 1 at `tools/test_orca_adapter.py:272`: expected `TOKEN == "<redacted>"`. | KILLED |
| M3 | Coordinator marks waiter ended without calling `end_waiter`. | Executor suite exit 1 at `tools/test_parallel_executor.py:826`: expected `wait, end_waiter` order. | KILLED |

**Sensor:** lightweight, 3 injected, 3 killed, 0 survived. PASS.

### Prior Fingerprint Re-derivation and AD-012 Counts

AD-012 identity remains requirement + root cause + concrete failure path. A passing scoped
re-verification adds zero failed-remediation increments; historical counts remain durable.

| Fingerprint | T3R2 disposition | Prior count | T3R2 increment | Resulting count |
| --- | --- | ---: | ---: | ---: |
| `SEC-006 + raw nested Delivery payload is returned + waiting coordinator persists environment secret` | CLOSED by recursive redaction at `.agents/skills/autonomous/scripts/orca_adapter.py:17-33,318-329`, assertions at `tools/test_orca_adapter.py:257-275` / `tools/test_parallel_executor.py:822-825,881`, and killed M2. | 1 | 0 | 1 |
| `EXE-09/IT-003 + coordinator omits end_waiter + dependency follow-up reaches adapter without ended-turn marker` | CLOSED by `.agents/skills/autonomous/scripts/parallel_execute.py:565-598`, restart assertion at `tools/test_parallel_executor.py:833-881`, and killed M3. | 1 | 0 | 1 |
| `EXE-07 + coordinator accepts incomplete worker receipt + lane becomes running without exact IDs` | CLOSED by coordinator validation at `.agents/skills/autonomous/scripts/parallel_execute.py:621-643,854-873` and sparse-receipt rejection at `tools/test_parallel_executor.py:1298-1328`. | 1 | 0 | 1 |
| `SEC-005 + missing-field rejection has no negative assertion + local-value substitution survives` | CLOSED by all-field negative cases at `tools/test_orca_adapter.py:311-329` and killed M1. | 1 | 0 | 1 |
| `EXE-11/IT-004 + missing/duplicate public outcomes are unasserted + serial recovery is not discriminated` | CLOSED by direct duplicate/missing assertions at `tools/test_orca_adapter.py:280-329` and public serial outcomes at `tools/test_parallel_executor.py:769-826`. | 1 | 0 | 1 |

Earlier T3 fingerprints already closed in T3R1 remain closed with their recorded count 0; T3R2
does not reopen or increment them.

### Ranked Gaps

None for Slice B technical verification.

### Slice B Summary

**Overall:** PASS for Slice B only. EXE-06–EXE-11, IT-002–IT-004, SEC-005, and SEC-006 match their
spec-defined outcomes; 43 scoped tests pass and all three behavior mutants die. This verdict does
not complete the feature and does not authorize deep-review, a real Orca pilot, QA Plan, or QA
Execute.

## Grouped deep-review invalidation

The grouped A-B deep-review result invalidates earlier PASS claims for unknown receipt fields,
credential suffix redaction, durable delivery/release replay, CLI wait controls, and convergence
state. TDR1 closes only those A-B findings. C/D implementation findings remain Planned and are not
implemented by this batch.

## TDR2 final grouped-review remediation

TDR2 closes the remaining A-B verification defects: supported nested worker envelopes are
projected before strict validation, complete Run Deliveries are projected to correlated identifiers
and recursively redacted payloads, acknowledgement and release receipts are durable and
correlated across restart, convergence paths/aliases are bounded and existing-only, and the
declared Python gate discovers every `tools/test_*.py`. C/D implementation findings remain Planned;
there is no review round 3 or real Orca pilot in this remediation.

### Group A-B post-fix closure

- **Reviewed head:** `4d328cd` (round 2), final remediation head `cbced4e`.
- **Post-fix command:** `npm run test:all`.
- **Result:** exit 0; 109 Vitest tests and all 10 discovered Python suites passed.
- **Directed counts:** Orca adapter 20, executor 32, convergence 6; final-round negative reproductions passed.
- **Disposition:** grouped deep-review A-B closed by the required post-round-2 remediation and green gate; no round 3 was opened.
- **Feature status:** incomplete. T4-T7, grouped review C-D, real Orca pilot, final QA, and final full gate remain.

## Slice C / T4R1 Technical Re-verification

**Slice verdict:** FAIL. T4R1 implements changed-checkpoint invalidation and exact gate-receipt
checks for a newly starting lane, but the canonical executor suite does not discriminate the required
waiting-lane path. A mutant that leaves a changed-checkpoint waiter in `waiting` and returns it to
event handling without a fresh gate survives all 34 executor tests. EXE-15 and UT-006 remain open.

### Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | Evidence | Result |
| --- | --- | --- | --- |
| EXE-12 | A clean consumer rebases onto the exact recorded producer commit before dependent work. | `.agents/skills/autonomous/scripts/git_adapter.py:99-137`; `tools/test_git_adapter.py:54-65,101-110` asserts exact sync and dirty rejection. | PASS |
| EXE-13 | An already-ancestor producer makes checkpoint sync a byte-stable no-op. | `.agents/skills/autonomous/scripts/git_adapter.py:120-130`; `tools/test_git_adapter.py:67-70` asserts exact no-op receipt. | PASS |
| EXE-14 | Rebase conflict or undeclared path aborts, restores the clean pre-sync HEAD, and returns serial recovery. | `.agents/skills/autonomous/scripts/git_adapter.py:131-142`; `tools/test_git_adapter.py:76-95,147-157` asserts restored HEAD, clean status, and exact serial reasons. | PASS |
| EXE-15 | A changed checkpoint HEAD invalidates gate, Technical Verifier, and deep-review receipts and requires the affected gate before worker start or follow-up. | Production flow exists at `.agents/skills/autonomous/scripts/parallel_execute.py:538-647,963-1024`; `tools/test_parallel_executor.py:1053-1135` asserts new-lane blocking, restart reuse, rejected failed/wrong-HEAD gate receipts, accepted exact gate, and retained Verifier/deep-review invalidations. No assertion starts from a waiting lane with a dependency delivery. Sensor M2 survives after routing that changed-checkpoint waiter directly back to event handling. | FAIL |
| EXE-16 | Technically verified slice commits merge into the feature branch in deterministic slice order without rewriting them. | `.agents/skills/autonomous/scripts/git_adapter.py:153-190`; `tools/test_git_adapter.py:163-183` asserts A/B order and preserved commit ancestry. | PASS |
| EXE-17 | Integration conflict aborts, restores the clean pre-operation HEAD, and delegates resolution to serial recovery. | `.agents/skills/autonomous/scripts/git_adapter.py:171-181`; `tools/test_git_adapter.py:188-208` asserts exact serial conflict receipt, restored HEAD, and clean status. | PASS |

**Spec-anchored status:** 5 PASS, 1 FAIL, 0 spec-precision gaps for Slice C.

### Test Contract Disposition

| Case | Contracted outcome | Evidence | Result |
| --- | --- | --- | --- |
| UT-004 | Exact producer rebase or byte-stable ancestor no-op. | `tools/test_git_adapter.py:54-70` asserts both exact branches. | PASS |
| UT-005 | Conflict abort restores pre-sync HEAD and clean state and halts the lane. | `tools/test_git_adapter.py:76-95` asserts serial recovery, identical HEAD, and clean status. | PASS |
| UT-006 | Changed-HEAD evidence invalidates before follow-up; verified merges are stable; conflict aborts cleanly. | Merge/conflict outcomes pass at `tools/test_git_adapter.py:163-208`; invalidation values and new-lane blocking pass at `tools/test_git_adapter.py:59-65` and `tools/test_parallel_executor.py:1053-1135`. The waiting-lane follow-up outcome is hollow under `docs/guidelines/TEST-CONTRACT.md:53-65`: M2 survives. | FAIL |

### Gate Evidence

- `python3 tools/test_git_adapter.py` -> exit 0, `7 passed, 0 failed`; 0 skipped.
- `python3 tools/test_parallel_executor.py` -> exit 0, `34 passed, 0 failed`; 0 skipped.
- `python3 tools/test_orca_adapter.py` -> exit 0, `20 passed, 0 failed`; 0 skipped.
- Scoped total: 61 passed, 0 failed, 0 skipped. T4R1 adds 2 executor cases over `a799eac`; Git remains 7 and Orca remains 20.
- `python3 .agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-executor/spec.md --strict` -> exit 0, 0 errors, 0 warnings.
- `python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-executor/tasks.md --strict` -> exit 0, 0 errors, 0 warnings.
- `python3 tools/ad-index.py --check` -> exit 0, `AD-INDEX.md up to date`.
- `git diff --check b797777..4c0a7fc` and `git diff --check a799eac..4c0a7fc` -> exit 0, no output.
- `python3 -m py_compile .agents/skills/autonomous/scripts/git_adapter.py tools/test_git_adapter.py .agents/skills/autonomous/scripts/orca_adapter.py tools/test_orca_adapter.py .agents/skills/autonomous/scripts/parallel_execute.py tools/test_parallel_executor.py` -> exit 0.
- `git diff --check` after report/ledger update -> exit 0, no output.
- `python3 .agents/skills/tlc-spec-driven/scripts/validate_state.py parallel-slice-executor` -> exit 1 as required for this FAIL verdict; the ranked EXE-15 fix task remains open.

### Discrimination Sensor

Real-tree porcelain was empty before each sensor batch and empty after cleanup. Mutations ran in
detached temporary worktrees at `4c0a7fc`; every scratch and parent directory was removed.

| Mutation | Behavior fault | Directed result | Outcome |
| --- | --- | --- | --- |
| M1 | Ignore the changed-checkpoint invalidation branch. | Executor exit 1 at `tools/test_parallel_executor.py:1072`; lane was not `gate_required`. | KILLED |
| M2 | For a changed checkpoint on a `waiting` lane, skip invalidation and return to dependency-event handling, permitting follow-up without a gate. | Executor exit 0, `34 passed, 0 failed`. | SURVIVED |
| M3 | Accept `passed=false` or wrong-HEAD gate receipts. | Executor exit 1 at `tools/test_parallel_executor.py:1087`; failed gate advanced the lane. | KILLED |
| M4 | Bypass `_consume_gate` entirely. | Executor exit 1 at `tools/test_parallel_executor.py:1098`; state no longer followed the exact-gate transition. | KILLED |

**Sensor:** lightweight, 4 injected, 3 killed, 1 survived. FAIL.

### Fingerprint Accounting

`python3 .agents/skills/tlc-spec-driven/scripts/review_convergence.py ... --previous-fingerprint da76f3... --verifier-failed --gate-passed`
recorded the repeated EXE-15 failure. Fingerprint `da76f3bbc70678913965eb0efd1c1590a01bad1f1aa2cdffbbd381c96a0bf00b`
remains `open`; failed-remediation count changed from 1 to 2. No halt occurs before count 3.

### Ranked Gaps

1. **Major / fix task — EXE-15, UT-006:** Extend the canonical executor integration suite with a
   persisted `waiting` lane, accepted worker receipt, changed checkpoint, and dependency delivery.
   Assert zero follow-up before a passing gate receipt correlated to lane and current HEAD; then assert
   same-terminal follow-up only after that receipt. The surviving mutant must die.

### Slice C Summary

**Overall:** FAIL for Slice C after T4R1. Five of six ACs pass; 61 scoped regression tests pass; one
of four behavior mutants survives. Slice D, grouped C-D deep-review, real Orca pilot, feature close,
QA Plan, and QA Execute remain outside this verdict.

## T4R2 post-remediation

T4R2 closes the surviving waiting-lane EXE-15 path. A persisted `waiting` lane with a dependency
delivery now consumes its changed `sync_after` checkpoint before event handling, persists
`gate_required/current_head/invalidated_evidence`, performs no `wait_events`, `start_worker`, or
`follow_up` effect before a correlated passing gate, restores `waiting` after gate acceptance, and
performs exactly one same-terminal follow-up across restart. The fingerprint ledger is now at
`failed_remediations: 2`; this successful final remediation does not increment it again.

## Slice C / T4R2 Final Technical Re-verification

**Slice verdict:** PASS. EXE-12–EXE-17 match their spec-defined outcomes. T4R2 closes the prior
EXE-15 waiting-lane gap: checkpoint synchronization precedes dependency-event consumption, a changed
HEAD blocks all follow-up behind the exact affected gate, and the accepted follow-up remains
exactly-once across restart. This slice verdict does not close the feature, Slice D, grouped C-D
deep-review, the real Orca pilot, QA Plan, or QA Execute.

### Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| EXE-12 | A clean consumer rebases onto the exact recorded producer commit before dependent work. | `tools/test_git_adapter.py:54-65` — `status == "synced"`, exact pre/post HEAD, changed path, invalidations, and producer ancestry; `tools/test_git_adapter.py:101-110` rejects a dirty consumer without touching it. | PASS |
| EXE-13 | An already-ancestor producer makes synchronization a byte-stable no-op. | `tools/test_git_adapter.py:67-70` — `status == "noop"`, identical pre/post HEAD, and no changed paths. | PASS |
| EXE-14 | Rebase conflict or undeclared change restores pre-sync HEAD and clean state and returns serial recovery. | `tools/test_git_adapter.py:76-95,147-157` — exact serial receipt, restored HEAD, clean porcelain, and empty invalidations. | PASS |
| EXE-15 | Changed checkpoint HEAD invalidates gate, Technical Verifier, and deep-review evidence and requires the exact affected gate before follow-up. | `tools/test_parallel_executor.py:985-1057` — waiting checkpoint enters `gate_required`, records `waiting-checkpoint-head`, performs zero pre-gate event/follow-up effects, accepts a correlated passing gate, and performs one same-terminal follow-up across restart; `tools/test_parallel_executor.py:1183-1211` rejects wrong-HEAD gate receipts and removes only gate invalidation. | PASS |
| EXE-16 | Technically verified slice commits merge in deterministic slice order without rewriting them. | `tools/test_git_adapter.py:163-183` — merged result is `[commit_a, commit_b]`, both original commits remain ancestors, and changed paths are stable. | PASS |
| EXE-17 | Integration conflict aborts, restores the clean pre-operation HEAD, and delegates to serial recovery. | `tools/test_git_adapter.py:188-208` — exact `merge-conflict` serial receipt, identical HEAD, and clean porcelain. | PASS |

**Spec-anchored status:** 6 PASS, 0 FAIL, 0 spec-precision gaps for Slice C.

### Test Contract Disposition

| Case | Evidence | Result |
| --- | --- | --- |
| UT-004 | `tools/test_git_adapter.py:54-70` asserts exact checkpoint rebase and ancestor no-op. | PASS |
| UT-005 | `tools/test_git_adapter.py:76-95,147-157` asserts conflict/undeclared-path serial recovery and unchanged clean state. | PASS |
| UT-006 | `tools/test_parallel_executor.py:985-1057,1183-1211` asserts waiting-lane invalidation, pre-gate blocking, exact gate identity, and exactly-once follow-up; `tools/test_git_adapter.py:163-208` asserts deterministic integration and conflict abort. | PASS |

### Gate Evidence

- `python3 tools/test_git_adapter.py` -> exit 0, `7 passed, 0 failed`; 0 skipped.
- `python3 tools/test_parallel_executor.py` -> exit 0, `35 passed, 0 failed`; 0 skipped.
- `python3 tools/test_orca_adapter.py` -> exit 0, `20 passed, 0 failed`; 0 skipped.
- Scoped total: 62 passed, 0 failed, 0 skipped. T4R2 adds one executor case; Git remains 7 and Orca remains 20.
- `python3 .agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-executor/spec.md --strict` -> exit 0, 0 errors, 0 warnings.
- `python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-executor/tasks.md --strict` -> exit 0, 0 errors, 0 warnings.
- `python3 tools/ad-index.py --check` -> exit 0, `AD-INDEX.md up to date`.
- `git diff --check b797777..c33425e` and `git diff --check 4c0a7fc..c33425e` -> exit 0, no output.
- `python3 -m py_compile .agents/skills/autonomous/scripts/git_adapter.py tools/test_git_adapter.py .agents/skills/autonomous/scripts/orca_adapter.py tools/test_orca_adapter.py .agents/skills/autonomous/scripts/parallel_execute.py tools/test_parallel_executor.py` -> exit 0.

### Discrimination Sensor

Real-tree porcelain was empty before sensor setup and unchanged after scratch cleanup. Mutations ran
in detached temporary worktree `/tmp/exe15-sensor.QDzflF/tree` at `c33425e`; scratch and parent were
removed.

| Mutation | Behavior fault | Directed result | Outcome |
| --- | --- | --- | --- |
| M1 | Exclude a `waiting` lane from changed-checkpoint invalidation, allowing dependency handling before a fresh gate. | Executor exits 1 at `tools/test_parallel_executor.py:1037`; expected `gate_required`. | KILLED |
| M2 | Accept a passing gate receipt whose `current_head` does not match the lane checkpoint. | Executor exits 1 at `tools/test_parallel_executor.py:1202`; wrong-HEAD receipt advanced the lane. | KILLED |
| M3 | Repeat the `follow_up` side effect after the correlated gate instead of preserving exactly-once execution. | Directed T4R2 case exits 1 at `tools/test_parallel_executor.py:1049`; observed call list contains a duplicate follow-up. | KILLED |

**Sensor:** lightweight, 3 injected, 3 killed, 0 survived. PASS.

### Fingerprint Accounting

Fingerprint `da76f3bbc70678913965eb0efd1c1590a01bad1f1aa2cdffbbd381c96a0bf00b`
is `closed`. Historical `failed_remediations: 2` is preserved; this passing verification does not
increment it and therefore does not trigger the third-remediation halt.

### Slice C Summary

**Overall:** PASS for Slice C after T4R2. Six of six ACs and all three contracted cases pass; 62
scoped tests are green; all three behavior mutants die. Feature-level `FAIL` remains intentional
until Slice D, grouped C-D deep-review, the real Orca pilot, and separate QA phases complete.

## Slice D / T5-T7 Technical Verification

**Date:** 2026-08-24
**Diff range:** `a26e7f4^..2a155b7`
**Verifier:** independent Technical Verifier (author != verifier)
**Slice verdict:** FAIL. The configuration, resource planning, provider lifecycle, capability
fallback, checkpoint, merge, and cleanup contracts are technically discriminated. The checked-in
E2E-001 handoff cannot start its declared journey: it targets this feature's frozen `disabled`
snapshot after all tasks are complete, so the documented plan has zero lanes and executor `start`
returns `disabled-mode` before Orca can create either lane. No real Orca pilot was attempted in this
technical phase.

### Task Completion

| Task | Result | Evidence |
| --- | --- | --- |
| T5 | PASS | `tools/test_workflow_config.py:145-218` freezes a safe executable and preserves the prior snapshot for absolute, traversal, missing, directory, non-executable, and symlink inputs. |
| T6 | PASS | `tools/test_parallel_plan.py:361-392` asserts stable normalized resource arrays and exact serial reasons for missing or ambiguous metadata. |
| T7 | FAIL | `tools/test_parallel_executor.py:665-704` discriminates the capability/zero-effect fallback, but `.specs/features/parallel-slice-executor/qa-pilot.md:6-14` directs QA to a frozen disabled/completed feature and therefore cannot create its two required lanes. |

### Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| EXE-18 | `Resources: none` starts without a provider. | `tools/test_parallel_executor.py:307-356` - `provider_calls == 0`, worktree/worker effects occur, while a resource lane requires a prepared correlated lease; `tools/test_parallel_plan.py:361-369` - `none` becomes `[]`. | PASS |
| EXE-19 | Resource lanes invoke the frozen provider with the exact argv-only correlated request. | `tools/test_parallel_executor.py:345-353,459-478` - exact request keys/body and executable-only argv; `tools/test_workflow_config.py:145-156` - normalized frozen path persists. | PASS |
| EXE-20 | Only a unique correlated prepared lease is accepted and persisted with redacted environment values. | `tools/test_parallel_executor.py:355-356,404-471` - prepared receipt, correlation failures, duplicate live lease, exact resource names, and `<redacted>` environment assertion. | PASS |
| EXE-21 | Missing/unsupported/timeout/malformed/duplicate/cleanup failure refuses parallel dispatch with an exact serial reason. | `tools/test_parallel_executor.py:522-580` - worker count remains zero for acquisition failures and cleanup returns `cleanup-failed`; `tools/test_parallel_plan.py:373-392` - invalid resource metadata falls back before execution. | PASS |
| EXE-22 | Terminal or abandoned lanes release an owned lease exactly once and retain cleanup evidence. | `tools/test_parallel_executor.py:363-399,547-580` - foreign duplicate cleanup is rejected, repeated owned release is idempotent, terminal statuses release once, and failed cleanup receipt persists. | PASS |
| SEC-007 | A resource-bearing lane cannot start without a proven lease/prepared checkout. | `tools/test_parallel_executor.py:307-356,522-540` - no worker starts without the provider or after acquisition failure. | PASS |
| SEC-008 | Cleanup targets the current lane's lease and is idempotent. | `tools/test_parallel_executor.py:363-399` - cross-lane duplicate lease is rejected and the second owned release returns its existing receipt with one provider release. | PASS |
| IT-005 | Provider configuration freezes only a safe repository-relative executable without replacing valid state on failure. | `tools/test_workflow_config.py:145-218` - exact frozen snapshot and byte-identical prior state after every unsafe case. | PASS |
| IT-006 | Planning exposes exact resource names or serializes missing/ambiguous metadata. | `tools/test_parallel_plan.py:361-392` - stable sorted names and seven exact invalid-metadata outcomes. | PASS |
| IT-007 | Autonomous capability/fallback and unchanged lifecycle boundaries remain mandatory. | `tools/test_parallel_executor.py:665-704,1027-1097`; `tools/test_git_adapter.py:163-208`; `tools/shared/tests/autonomous-parallelization.test.ts:12-107` assert capability fallback, checkpoint/gate/follow-up, deterministic preserved-commit merge, conflict abort, and TLC/review/QA/full-gate policy. | PASS |
| E2E-001 handoff readiness | Fresh QA can execute the documented two-lane disposable Orca journey. | Dry-run of the exact `.specs/features/parallel-slice-executor/qa-pilot.md:6-14` commands returned `mode: disabled`, `lanes: []`, then `fallback: true`, `reason: disabled-mode`; no Orca effect occurred. | FAIL |

**Spec-anchored status:** 10 PASS, 1 FAIL, 0 spec-precision gaps in Slice D scope.

### Gate Evidence

- `python3 tools/test_workflow_config.py` -> exit 0, 18 passed, 0 failed, 0 skipped.
- `python3 tools/test_parallel_plan.py` -> exit 0, 16 passed, 0 failed, 0 skipped.
- `python3 tools/test_parallel_executor.py` -> exit 0, 37 passed, 0 failed, 0 skipped.
- `npm run test:all` -> exit 0: 110 Vitest tests in 9 files plus all 11 discovered Python suites; reported Python case totals were 145 passed with 0 failed/skipped, with the contract smoke suite additionally reporting `ok`.
- `python3 .agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-executor/spec.md --strict` -> exit 0, 0 errors, 0 warnings.
- `python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-executor/tasks.md --strict` -> exit 0, 0 errors, 0 warnings.
- `python3 tools/ad-index.py --check` -> exit 0, index up to date.
- `git diff --check a26e7f4^..2a155b7` -> exit 0, no output.
- `python3 -m py_compile` over all four changed Python implementation files and their three directed suites -> exit 0.
- `check_commit.py` accepted all three T5-T7 Conventional Commit messages.

### Discrimination Sensor

Baseline real-tree porcelain was empty. Mutations ran in detached temporary worktree
`/tmp/parallel-slice-d-sensor.JE20ri/tree` at `2a155b7`; the scratch was removed and real-tree
porcelain matched the baseline before this report/ledger update.

| Mutation | Behavior fault | Directed result | Outcome |
| --- | --- | --- | --- |
| M1 | Force `Resources: none` lanes through resource acquisition instead of bypassing the provider. | Executor suite exits 1 before dispatching the expected lane state. | KILLED |
| M2 | Accept an Orca adapter whose declared capability is not `orchestration.contract.v1`. | Executor suite exits 1 at `tools/test_parallel_executor.py:675`. | KILLED |
| M3 | Treat missing `Resources` metadata as an explicit empty resource list. | Planner suite exits 1 at `tools/test_parallel_plan.py:387`. | KILLED |

**Sensor:** lightweight, 3 behavior mutations, 3 killed, 0 survived. PASS.

### Fingerprint Accounting

Fingerprint `5ea1f781dc2dd658fbad3fcf0a4ebcc17575f004bd0897db1e6edb48c9c25082`
is open with `failed_remediations: 1` for `E2E-001/EXE-06/EXE-18 + QA handoff targets the
frozen disabled completed feature + documented plan returns zero lanes and executor returns
disabled-mode before two Orca lanes can start`. The full gate passed, so this count records the
failed Technical Verifier outcome, not a build failure.

### Ranked Gaps

1. **Major / fix task - E2E-001, T7:** Replace the unusable self-feature commands in
   `qa-pilot.md` with a deterministic disposable pilot setup that creates a temporary feature
   snapshot in `full` mode and two pending `Resources: none` lanes, points both executor commands
   at that fixture, and defines cleanup for the fixture's state/worktrees. Add a directed contract
   assertion proving the handoff cannot silently target a disabled or completed plan. Do not run
   the real Orca pilot in the remediation; fresh QA Execute owns it.

### Slice D Summary

**Overall:** FAIL for Slice D. Automated implementation evidence is green and all three mutations
die, but T7's only real-pilot interface deterministically cannot reach the journey it hands to QA.
Grouped deep-review C-D, the actual Orca pilot, final QA, and feature closure remain pending.

## T7R1 post-remediation

The Major E2E-001 handoff gap is closed by `tools/qa_parallel_pilot.py`: setup creates a disposable
Git fixture with frozen `safe` mode and two pending independent `Resources: none` lanes; dry-run
asserts exactly two ready lanes before any Orca mutation; cleanup removes only the marked fixture and
owned sibling worktrees. `tools/test_qa_parallel_pilot.py` rejects the disabled/completed production
feature target and proves setup/dry-run/cleanup. The real Orca start remains untested and owned by a
fresh QA Verifier. Fingerprint `5ea1f781...` remains at count 1; this successful remediation does
not increment it.

## Slice D / T7R1 Independent Technical Re-verification

**Date:** 2026-08-24
**Diff range:** a26e7f4^..ff93843
**Verifier:** independent Technical Verifier (author != verifier)
**Slice verdict:** FAIL. T7R1 fixes the prior disabled/completed-target blocker, but the disposable
pilot is not restart-safe and its frozen source checkpoint is not discriminated. No real Orca pilot
was executed in this technical phase.

### Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | file:line + assertion | Result |
| --- | --- | --- | --- |
| E2E-001 / EXE-18 | Disposable safe fixture exposes exactly two independent ready Resources:none lanes. | tools/qa_parallel_pilot.py:38-55,70-85; tools/test_qa_parallel_pilot.py:22-37 assert safe mode, validated true, two ready lanes, and empty resources. Public dry-run returned slice-A and slice-B. | PASS |
| E2E-001 / EXE-06 | Lanes derive from exact real frozen source HEAD before worktree creation. | tools/qa_parallel_pilot.py:35,43-49 writes current HEAD, but tools/qa_parallel_pilot.py:70-85 never correlates it to repository HEAD and tools/test_qa_parallel_pilot.py:22-37 never asserts it. Replacing git_head with forty zeroes survived canonical harness. | FAIL |
| E2E-001 / SEC-008 | Cleanup removes only marker-owned fixture/worktrees and remains idempotent across restart/retry. | tools/qa_parallel_pilot.py:63-67,88-97 validates ownership before deletion, but second cleanup fails after first removed marker. tools/test_qa_parallel_pilot.py:38-40 exercises cleanup once only. | FAIL |
| Production isolation | Versioned workflow remains frozen disabled; pilot setup changes only temporary root. | .specs/features/parallel-slice-executor/workflow.json:1 remained disabled; real-tree porcelain matched baseline after fixture and sensor cleanup. | PASS |

**Spec-anchored status:** 2 PASS, 2 FAIL, 0 spec-precision gaps in T7R1 scope.

### Gate Evidence

- Canonical harness: 1 passed, 0 failed.
- IT-007: 2 passed, 0 failed.
- Directed Slice D suites: config 18, planner 16, executor 37, Orca 20, Git 7; 98 passed, 0 failed.
- Full gate: 110 Vitest plus 146 Python cases, 0 failed/skipped, and contract smoke ok.
- Strict spec/tasks validators: 0 errors, 0 warnings; AD index current.
- Python compile, diff check, and all four commit-message checks: exit 0.

### Discrimination Sensor

Mutations ran in detached temporary worktree /tmp/parallel-slice-d-r1-sensor.KuxFI8/tree at
ff93843; scratch removal restored real-tree porcelain to baseline.

| Mutation | Behavior fault | Directed result | Outcome |
| --- | --- | --- | --- |
| M1 | Freeze pilot mode as full instead of required safe. | Canonical harness exits 1 during dry-run. | KILLED |
| M2 | Freeze source git_head as forty zeroes instead of repository HEAD. | Canonical harness still reports 1 passed. | SURVIVED |
| M3 | Give one lane a database resource instead of Resources:none. | Canonical harness exits 1 during dry-run. | KILLED |

**Sensor:** lightweight, 3 mutations, 2 killed, 1 survived. FAIL.

### Fingerprint Accounting

- 5ea1f781 is closed at historical count 1: handoff no longer targets frozen disabled/completed production feature.
- c81a953f is open at count 1: dry-run does not correlate frozen git_head to repository HEAD.
- d8cf8d2e is open at count 1: repeated cleanup raises ValueError instead of stable cleanup evidence.

### Ranked Gaps

1. **Major / E2E-001, SEC-008:** Make cleanup retry/restart-idempotent and extend canonical harness
   to call cleanup twice while proving no unrelated path is removed.
2. **Major / E2E-001, EXE-06:** Make dry-run reject a frozen git_head that is not disposable
   repository's exact HEAD; add zero-checkpoint regression assertion.

**Overall:** FAIL for Slice D after T7R1. Grouped C-D deep-review, real Orca E2E-001, QA, and feature
closure remain blocked on these two remediation tasks.

## T7R2 post-remediation

T7R2 hardens the pilot lifecycle without touching the production disabled workflow: dry-run now
rejects a missing or mismatched frozen source HEAD and returns equal `source_git_head`/
`repository_head` alongside the two validated lanes. Cleanup accepts only the bounded marked fixture,
records an attestation, and returns an explicit idempotent success on repeat; unmarked roots remain
untouched. Canonical tests cover both verifier mutants. Fingerprints `c81a953f...` and `d8cf8d2e...`
remain at count 1 pending fresh verifier closure; this remediation does not edit their ledger counts.

## Slice D / T7R2 Independent Technical Re-verification

**Date:** 2026-08-24
**Diff range:** c478fca^..c478fca
**Verifier:** independent Technical Verifier (author != verifier)
**Slice verdict:** FAIL. Both prior blockers are resolved, but cleanup can delete an unmarked derived
sibling directory. No real Orca pilot was executed in this technical phase.

### Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | file:line + assertion | Result |
| --- | --- | --- | --- |
| E2E-001 / EXE-06 | Frozen source HEAD must equal the disposable repository HEAD before planner or Orca effects. | `tools/qa_parallel_pilot.py:74-80`; `tools/test_qa_parallel_pilot.py:32-35,53-58` assert equality and rejection. Direct probes rejected missing, zero, nonexistent, and mismatched real HEAD before planner/Orca. | PASS |
| E2E-001 / EXE-18 | Dry-run exposes exactly two ready `Resources: none` lanes. | `tools/test_qa_parallel_pilot.py:32-38` asserts safe mode, validated state, two lanes, empty resources, and ready state. A real disposable repository returned two lanes and exact HEAD `66ff68a32220b35b22736733e1a8d41dc7cbd0ff`. | PASS |
| E2E-001 / SEC-008 retry | Cleanup is explicitly idempotent after process restart for the same attested root and rejects a tampered attestation. | `tools/qa_parallel_pilot.py:105-114`; `tools/test_qa_parallel_pilot.py:40-43` assert first cleanup false and second-process cleanup true. Direct tampering probe was rejected. | PASS |
| E2E-001 / SEC-008 ownership | Cleanup targets only owned fixture/worktree receipts; unmarked sibling paths survive. | `tools/qa_parallel_pilot.py:116-123` recursively scans and removes `.<fixture>-parallel-slices` without an ownership marker or attestation. Direct adverse probe created an unmarked derived sibling and returned `unowned_derived_sibling_survived=false`. No canonical assertion covers this path. | FAIL |

**Spec-anchored status:** 3 PASS, 1 FAIL, 0 spec-precision gaps in T7R2 scope.

### Gate Evidence

- Canonical pilot harness: 2 passed, 0 failed.
- IT-007: 2 passed, 0 failed.
- Directed Slice D suites: executor 37, Git 7, Orca 20, planner 16, config 18; 98 passed, 0 failed.
- Full `npm run test:all`: 110 Vitest tests in 9 files plus 147 reported Python cases and contract smoke; 0 failed/skipped.
- Strict spec/tasks validators: 0 errors, 0 warnings; AD index current.
- Python compile, commit-message validation, commit diff check, and real-tree diff check: exit 0.

### Adverse Probes and Discrimination Sensor

Real-tree porcelain was empty before the sensor. Mutations ran in detached temporary worktree
`/var/folders/lc/_v1mn5h560d2tsmz474y7d1c0000gn/T/tmp.vItjRHf5bG/tree` at `c478fca`; the scratch
was removed before report/ledger edits.

| Probe / mutation | Behavior | Result |
| --- | --- | --- |
| P1 | Missing, zero, nonexistent, and mismatched real `git_head` must stop before planner/Orca. | All four rejected; no planner/Orca invocation recorded. PASS. |
| P2 | Valid dry-run must report repository HEAD exactly and two ready resource-free lanes. | Exact equality and two lanes observed. PASS. |
| P3 | First cleanup, restarted retry, and tampered attestation. | First non-idempotent success, restarted idempotent success, tamper rejected. PASS. |
| P4 | Unmarked derived sibling directory must survive cleanup. | Directory and sentinel were deleted. FAIL. |
| M1 | Disable frozen-HEAD mismatch rejection. | Canonical pilot suite exited 1 at `tools/test_qa_parallel_pilot.py:58`. KILLED. |
| M2 | Make repeated attested cleanup raise instead of return idempotent success. | Canonical pilot suite exited 1 at `tools/test_qa_parallel_pilot.py:42`. KILLED. |

**Sensor:** lightweight, 2 prior-blocker mutations, 2 killed, 0 survived. PASS. The direct ownership
probe exposes a separate implementation and coverage gap.

### Fingerprint Accounting

- `c81a953f...` is closed at historical count 1: source HEAD is now correlated and its mutant dies.
- `d8cf8d2e...` is closed at historical count 1: repeated cleanup now returns stable evidence and its mutant dies.
- `d0a63e2...` is open at count 1: unmarked derived sibling root is recursively removed during fixture cleanup. This is a distinct root cause and failure path, not another round of either prior blocker.

### Ranked Gaps

1. **Blocker / E2E-001, SEC-008:** Require explicit ownership evidence for the derived worktree root
   before traversing or deleting it, reject missing/mismatched ownership, and add a canonical test
   proving an unmarked derived sibling plus its sentinel survive fixture cleanup. Avoid recursive
   discovery of deletion targets; consume the exact owned worktree receipts.

**Overall:** FAIL for Slice D after T7R2. Prior blockers closed. New SEC-008 sibling-ownership
fingerprint is at count 1. Grouped C-D deep-review, real Orca E2E-001, QA, and feature closure remain
pending after remediation and fresh verification.

## T7R3 post-remediation

T7R3 binds cleanup to the setup ownership manifest and exact `parallel-pilot/A-T1` and `B-T2`
worktree paths. It removes only valid owned Git worktrees, never recursively deletes the derived
sibling root, preserves unowned sentinel content, and returns an honest residual error. Prior
source-HEAD correlation and idempotent retry behavior remain green. Fingerprint `d0a63e2...` stays
at count 1 pending fresh verifier closure; no ledger count is changed by this remediation.

## Slice D / T7R3 Independent Technical Re-verification

**Date:** 2026-08-24
**Diff range:** `8e58a8c^..8e58a8c`
**Verifier:** independent Technical Verifier (author != verifier)
**Slice verdict:** FAIL. The original broad sibling-deletion blocker is resolved, but cleanup still
trusts a tampered manifest source HEAD and loses residual failure state on retry. No real Orca pilot
was executed in this technical phase.

### Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion/probe | Result |
| --- | --- | --- | --- |
| E2E-001 / SEC-008 exact targets | Cleanup removes only the exact manifest-owned `A-T1`/`B-T2` Git worktrees and preserves unowned siblings. | `tools/qa_parallel_pilot.py:127-147`; `tools/test_qa_parallel_pilot.py:72-88` asserts exact `A-T1` removal, non-zero residual, and sentinel survival. Direct probe created both exact Git worktrees; both were removed and an unowned sentinel survived. | PASS |
| E2E-001 / SEC-008 manifest integrity | Every ownership binding, including the source HEAD, must be valid before cleanup authorizes deletion. | Setup binds `source_git_head` at `tools/qa_parallel_pilot.py:60-63`, but cleanup validation at `:77-80` checks only root, feature, and worktree list. Direct probe changed only `source_git_head` to forty zeroes; cleanup returned success and deleted the fixture and owned worktree. | FAIL |
| E2E-001 / SEC-008 bounded retry | Retrying cleanup after restart must reproduce owned cleanup evidence without concealing unresolved paths. | `tools/qa_parallel_pilot.py:119-125,148-150` writes unconditional `status: cleaned` and later returns `cleaned: true`. Direct probe's first call returned `cleaned: false` with the preserved sibling root; the restarted call returned `cleaned: true` while the sentinel still existed. | FAIL |
| E2E-001 / EXE-06 HEAD correlation | Dry-run rejects a frozen or ownership source HEAD different from repository HEAD. | `tools/qa_parallel_pilot.py:83-91`; `tools/test_qa_parallel_pilot.py:32-35,48-58` asserts exact equality and frozen-workflow rejection. Directed harness remained green. | PASS |

**Spec-anchored status:** 2 PASS, 2 FAIL, 0 spec-precision gaps in T7R3 scope.

### Gate Evidence

- Canonical pilot harness: 3 passed, 0 failed.
- IT-007: 2 passed, 0 failed.
- Directed Slice D suites: config 18, planner 16, executor 37, Orca 20, Git 7; 98 passed, 0 failed.
- Full `npm run test:all`: 110 Vitest tests in 9 files plus 148 reported Python cases and contract smoke; 0 failed/skipped.
- Strict spec/tasks validators: 0 errors, 0 warnings; AD index current.
- Python compile, T7R3 commit-message validation, commit/working-tree diff checks: exit 0.
- Real-tree porcelain was empty before sensors and empty after scratch cleanup.

### Adverse Probes and Discrimination Sensor

| Probe / mutation | Behavior | Result |
| --- | --- | --- |
| P1 | Exact `A-T1` and `B-T2` are real Git worktrees. | Both removed through `git worktree remove`; cleanup returned no residual. PASS. |
| P2 | Unowned derived sibling sentinel. | Sentinel survived and first cleanup returned a bounded non-zero residual. PASS. |
| P3 | Traversal injected into manifest worktree list and arbitrary unmarked root. | Both rejected before deletion; sentinel/path survived. PASS. |
| P4 | Only manifest `source_git_head` changed to forty zeroes. | Cleanup succeeded and deleted the owned worktree/root. FAIL. |
| P5 | Retry after P2 from a new process-equivalent call. | Returned `cleaned: true` while the preserved residual sentinel remained. FAIL. |
| M1 | Remove the manifest root/feature/worktree ownership check. | Canonical pilot suite still reported 3 passed. SURVIVED. |
| M2 | Reintroduce broad `rglob` discovery plus recursive sibling deletion. | Canonical pilot suite exited 1 at `tools/test_qa_parallel_pilot.py:86`; sentinel case killed it. KILLED. |

**Sensor:** lightweight, 2 mutations, 1 killed, 1 survived. FAIL.

### Fingerprint Accounting

- `d0a63e2380682516b1f6195379bc539f34cfe176f87627fffde63e7d2ee2a3fc` is closed at historical count 1: exact-target cleanup no longer recursively removes the derived sibling root, the sentinel probe passes, and broad-rglob reintroduction dies.
- `7009c8b0996b20dd6029a94d77596e129bf53efe2f7d99f8bc4d13667616d452` is open at count 1: cleanup does not validate manifest `source_git_head`; a tampered manifest authorizes destructive cleanup.
- `187464370a08ebbfae594e77e9c7a88f4f66545faf2b46249c62148c07a8c08b` is open at count 1: cleanup attestation discards residual failure state, so retry reports false success.

### Ranked Gaps

1. **Blocker / E2E-001, SEC-008:** Validate the ownership manifest's `source_git_head` against the
   fixture repository HEAD before any cleanup effect; add a canonical adverse assertion proving a
   source-HEAD-only tamper preserves the fixture and exact worktrees.
2. **Major / E2E-001, SEC-008:** Persist bounded residual paths/status in the cleanup attestation and
   return the same unresolved result on retry until those paths are independently removed; add a
   restart-style assertion that the second call cannot report clean while a residual sentinel exists.

**Overall:** FAIL for Slice D after T7R3. The prior fingerprint is closed, and these are two new
root causes at count 1 each. Grouped C-D deep-review, the real Orca pilot, QA, and feature closure
remain pending after remediation and fresh technical verification.

## T7R4 remediation handoff

T7R4 consumes the two T7R3 FAIL findings without changing their ledger counts. Cleanup now
correlates the independently derived fixture repository HEAD with the frozen workflow and ownership
source HEAD before any worktree or fixture deletion. The external tombstone records the exact
bounded residual paths and status before the fixture root is removed; restart retries re-evaluate
the derived sibling and remain `cleaned: false` while any unowned sentinel remains. The production
workflow stays disabled and no real Orca pilot was run by the author.

Canonical coverage is added in `tools/test_qa_parallel_pilot.py` for source-head-only attestation
tampering and residual retry after root removal. Existing T7R3 sentinel-survival, exact owned
worktree cleanup, frozen-head dry-run, and arbitrary-root rejection assertions remain intact.

### T7R4 implementation evidence

- `python3 tools/test_qa_parallel_pilot.py`: 5 passed, 0 failed.
- `python3 tools/test_parallel_executor.py`: 37 passed, 0 failed; IT-007: 2 passed, 0 failed.
- `npm_config_offline=true npm run test:all`: 110 Vitest tests and all discovered Python suites passed, 0 failed.
- Strict spec/tasks validation, AD index, Python compile, `git diff --check`, and commit-message validation passed.
- The two T7R3 fingerprints remain open at historical count 1 pending a fresh Technical Verifier; this remediation does not close or increment them.

## T7R5 remediation handoff

T7R5 adds a public cleanup-process ownership matrix for root, feature, missing, extra, duplicate,
outside, and reordered worktree attestation values. Every case creates a legitimate Git worktree
and an unowned sentinel, then asserts rejection, fixture/worktree/sentinel survival, and no external
cleanup tombstone. Existing source-head, residual retry, exact-path, dry-run, and arbitrary-root
coverage remains unchanged. No real Orca pilot was run by the author; the new `f46e5c21...`
fingerprint remains count 1 for fresh verifier closure.

## Slice D / T7R4 Independent Technical Re-verification

**Date:** 2026-08-24
**Diff range:** `3f2b174^..3f2b174`
**Verifier:** independent Technical Verifier (author != verifier)
**Slice verdict:** FAIL. Both T7R3 blockers are resolved at historical count 1, but removal of the
non-HEAD ownership validation still survives the canonical pilot suite. No real Orca pilot was run.

### Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion/probe | Result |
| --- | --- | --- | --- |
| E2E-001 / SEC-008 source ownership | A source-HEAD-only manifest tamper causes zero deletion. | `tools/qa_parallel_pilot.py:84-94`; `tools/test_qa_parallel_pilot.py:105-127` asserts rejection plus fixture and real owned worktree survival; independent probe passed. | PASS |
| E2E-001 / SEC-008 restart residual | Retry remains false with the identical bounded residual until external removal, then converges without deleting the sentinel. | `tools/qa_parallel_pilot.py:157-174`; `tools/test_qa_parallel_pilot.py:135-182` asserts identical residuals, sentinel survival, and later idempotent success; independent restart probe passed. | PASS |
| E2E-001 / SEC-008 tombstone boundary | Tombstone paths stay under the exact derived sibling and cannot widen cleanup. | `tools/qa_parallel_pilot.py:107-128`; independent outside-path tombstone probe was rejected with the fixture already absent. | PASS |
| E2E-001 / SEC-008 complete ownership | Cleanup rejects a manifest whose root, feature, or exact owned-worktree list is not the setup attestation. | `tools/qa_parallel_pilot.py:71-81` contains the check, but removing it leaves all five `tools/test_qa_parallel_pilot.py` cases green. | FAIL |

**Spec-anchored status:** 3 PASS, 1 FAIL, 0 spec-precision gaps in T7R4 scope.

### Gate Evidence

- Pilot harness: 5 passed, 0 failed; IT-007: 2 passed, 0 failed.
- Directed Slice D suites: executor 37, Orca 20, Git 7, config 18, planner 16; 98 passed, 0 failed.
- Full `npm_config_offline=true npm run test:all`: 110 Vitest tests plus every discovered Python suite passed; 0 failed/skipped.
- Strict spec/tasks validators: 0 errors, 0 warnings; AD index current; Python compile, diff check, and commit-message validation passed.
- Real-tree porcelain matched its pre-sensor baseline after the temporary worktree was removed.

### Discrimination Sensor

| Mutation | Result |
| --- | --- |
| Remove ownership `source_git_head` versus repository HEAD check. | KILLED by `tools/test_qa_parallel_pilot.py:105-127`. |
| Force a restarted residual cleanup down the `cleaned: true` branch. | KILLED by `tools/test_qa_parallel_pilot.py:159-169`. |
| Remove root, feature, and exact-worktree ownership validation. | SURVIVED: canonical pilot suite reported 5 passed. |

**Sensor:** lightweight, 3 mutations, 2 killed, 1 survived. FAIL.

### Fingerprint Accounting

- `7009c8b0996b20dd6029a94d77596e129bf53efe2f7d99f8bc4d13667616d452` closed at count 1.
- `187464370a08ebbfae594e77e9c7a88f4f66545faf2b46249c62148c07a8c08b` closed at count 1.
- `f46e5c21f55a5f436fccfddb8504677394d245e5e9b70b44b0003eb0043564ff` opened at count 1: the canonical suite omits adverse coverage for non-HEAD ownership fields.

### Ranked Gap

1. **Major / E2E-001, SEC-008:** Add a canonical adverse case that changes only the ownership
   `root`, `feature`, or exact `worktrees` list, proves cleanup rejects it before effects, and kills
   removal of the shared ownership check. Keep the existing constant-path deletion and HEAD tests.

**Overall:** FAIL for Slice D after T7R4. This is a distinct first-count coverage blocker, not a
repeat of either resolved T7R3 failure. Grouped C-D deep-review, real Orca pilot, QA, and feature
closure remain pending.

## Grouped C-D round 1 remediation handoff

The grouped review found ten Major blockers. This batch addresses exact Git common-directory
ownership, coordinator checkpoint/integration lifecycle, planner declared paths, malformed receipt
serial recovery, owned worktree cleanup, pilot source metadata, QA terminal lifecycle, and the
stale T7/STATE handoff. The review artifacts remain immutable evidence; fresh grouped verification
must re-run its findings against the committed batch. No real Orca pilot was executed by the author.

## Grouped C-D round 2 post-cap remediation handoff

This batch closes the six final review blockers without claiming E2E-001 execution. Git operations
now require exact persisted lane path, gitdir, branch, and HEAD ownership, including re-checks before
cleanup and recovery. Integration requires an explicit durable Technical Verifier receipt authored by
someone other than the implementer, exact current HEAD correlation, and a frozen feature-root HEAD;
successful integration persists gate/Verifier/deep-review invalidation and a required post-integration
gate state. Planner checkpoint paths are the normalized sorted producer-path union. The QA pilot uses
the canonical lifecycle checker, which rejects missing or misordered terminal/ack/release receipts.

## QA fix loop handoff

The prior fresh-QA report found two defects and remains a FAIL artifact owned by QA. This product
fix makes setup use a source worktree registered in the current repository common directory,
preserves bounded structured Orca worker-start failures and exact Run/Task partial effects for
resume, and requires lifecycle authorization before normal cleanup. `--abort-incomplete` is a
diagnostic-only path that refuses accepted or recoverable workers. No QA pass or author-run Orca
result is claimed by this implementation.

The lifecycle authorization control is now explicitly two-phase: public
`lifecycle-check --root <fixture>` writes the digest-bound authorization, and normal cleanup only
reloads that pre-existing record before deletion. The canonical pilot test covers missing
authorization, stale state after authorization, successful authorized cleanup, and diagnostic
abort refusal for recoverable worker effects.

## T7R5 implementation evidence

- `python3 tools/test_qa_parallel_pilot.py`: 6 tests passed, 0 failed; the ownership matrix covers root, feature, missing, extra, duplicate, outside, and reordered worktree values through subprocess cleanup.
- Every matrix case creates a real owned worktree and unowned sentinel, then asserts nonzero rejection, fixture/worktree/sentinel survival, and no tombstone.
- The `f46e5c21...` ledger entry remains open at count 1 for fresh verifier closure; no ledger count was changed by this remediation.

## Slice D / T7R5 Independent Technical Re-verification

**Date:** 2026-08-24
**Diff range:** `3f2b174..d1770a6` (T7R5 focus: `d1770a6^..d1770a6`)
**Verifier:** independent Technical Verifier (author != verifier)
**Slice verdict:** PASS. The canonical public cleanup matrix now discriminates every non-HEAD
ownership binding and closes `f46e5c21...` at its historical count 1. No real Orca pilot was run in
this technical phase.

### Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| E2E-001 / SEC-008 complete ownership | Cleanup rejects tampered root, feature, or exact worktree ownership before changing the fixture. | `tools/test_qa_parallel_pilot.py:192-229` invokes the public cleanup process for root, feature, missing, extra, duplicate, outside, and reordered worktree values; `:225-229` asserts nonzero rejection, fixture/worktree/sentinel survival, and no tombstone. | PASS |
| E2E-001 / SEC-008 source ownership | Source-HEAD-only tampering remains rejected with zero owned deletion. | `tools/test_qa_parallel_pilot.py:105-127` asserts process failure plus fixture and owned-worktree survival. | PASS |
| E2E-001 / SEC-008 bounded cleanup | Legitimate cleanup removes exact owned Git worktrees, preserves unowned siblings, retains residual evidence, and converges only after residual removal. | `tools/test_qa_parallel_pilot.py:72-94,130-189` asserts exact removal, sentinel survival, stable retry residuals, and final idempotent success. | PASS |
| E2E-001 / EXE-06 pilot preflight | The disposable public dry-run remains correlated to the repository HEAD and exposes exactly two ready resource-free lanes. | `tools/test_qa_parallel_pilot.py:15-43` asserts safe mode, exact HEAD equality, two ready lanes, and `Resources: none`. | PASS |

**Spec-anchored status:** 4 PASS, 0 FAIL, 0 spec-precision gaps in T7R5 scope.

### Public CLI Matrix and Regression Evidence

- `python3 tools/test_qa_parallel_pilot.py` -> exit 0, 6 passed, 0 failed. The seven tamper rows are
  iterations inside the canonical matrix at `tools/test_qa_parallel_pilot.py:193-201`.
- IT-007: `npm_config_offline=true npx vitest run tools/shared/tests/autonomous-parallelization.test.ts`
  -> exit 0, 2 passed, 0 failed.
- Directed Slice D regressions: executor 37, Orca 20, Git 7, planner 16, config 18; 98 passed,
  0 failed.
- Full `npm_config_offline=true npm run test:all` -> exit 0: 110 Vitest tests in 9 files and every
  discovered `tools/test_*.py` suite passed; 0 failed/skipped.
- Strict spec/tasks validators -> 0 errors, 0 warnings; AD index current; Python compile,
  `git diff --check 3f2b174..d1770a6`, and T7R5 Conventional Commit validation -> exit 0.

### Discrimination Sensor

Real-tree porcelain was empty before the sensor and empty after scratch cleanup. A detached
temporary worktree at `d1770a6` was removed after the run.

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| Bypass `_validate_root` in `_validate_fixture`, removing root/feature/exact-worktree ownership authorization from cleanup. | `python3 tools/test_qa_parallel_pilot.py` exited 1 at `tools/test_qa_parallel_pilot.py:226`; a tampered-root case deleted the fixture instead of preserving it. | KILLED |

**Sensor:** lightweight, 1 required ownership mutation injected, 1 killed, 0 survived. PASS.

### Fingerprint Accounting

- `f46e5c21f55a5f436fccfddb8504677394d245e5e9b70b44b0003eb0043564ff` is closed at historical
  count 1. The public adverse matrix covers every requested ownership field and the exact prior
  `_validate_root` bypass now dies; this passing re-verification adds no failed-remediation count.
- Prior T7 source-HEAD, residual-retry, sibling-ownership, frozen-HEAD, and idempotency fingerprints
  remain closed at their recorded counts; all canonical regressions pass.

### Ranked Gaps

None for Slice D technical verification.

**Overall:** PASS for Slice D technical verification after T7R5. Grouped C-D deep-review, the real
Orca E2E-001 pilot, QA Plan, QA Execute, and final feature closure remain pending and are outside
this verdict.

## QA remediation independent technical verification

**Date:** 2026-08-24
**Diff range:** `f7a1f366^..f7a1f366`
**Verifier:** independent Technical Verifier (author != verifier)
**Verdict:** FAIL. Shared-repository setup and structured Orca partial-effect recovery pass, but
the lifecycle-authorization control is not discriminated and remains unsafe to accept as proven.
No real Orca run was performed in this technical phase.

### Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion/probe | Result |
| --- | --- | --- | --- |
| E2E-001 / EXE-06 shared repository | Setup commits fixture task metadata before freezing HEAD; source and child lanes are registered worktrees of the exact current-project Git common directory. | `tools/qa_parallel_pilot.py:53-94`; `tools/test_qa_parallel_pilot.py:23-52` asserts common-directory identity, committed task visibility, and frozen child HEAD. | PASS |
| EXE-11 / SEC-006 structured Orca failure | A nonzero structured worker-start failure retains bounded redacted code, stage, residuals, Run and Task; resume exposes a pending action and reuses those IDs without duplicate creation. | `tools/test_orca_adapter.py:134-164` asserts redacted structured failure and exact Task reuse; `tools/test_parallel_executor.py:279-314` asserts pending partial effect, recoverable action, and successful reconciliation. Independent malformed/secret probe: 2 passed. | PASS |
| E2E-001 / SEC-008 incomplete abort | Diagnostic abort refuses a pending accepted/recoverable worker, remains `cleaned: false`, and is idempotent when safe. | `tools/test_qa_parallel_pilot.py:130-152` asserts `worker-may-be-live` and source survival; `tools/test_qa_parallel_pilot.py:53-62` asserts diagnostic false-cleaned and idempotent retry. | PASS |
| E2E-001 / SEC-008 lifecycle authorization | Normal cleanup must require exact two-lane terminal/read-ack-release proof plus persisted digest-bound authorization before any lane/source deletion; missing, stale, or tampered authorization has zero effects. | `tools/qa_parallel_pilot.py:343-388` derives and writes authorization, then immediately deletes. Removing only the pre-delete `_write_tombstone` at `:379` leaves `tools/test_qa_parallel_pilot.py` green at 9/9 while `:380-383` still deletes lane and source worktrees. | FAIL |

**Spec-anchored status:** 3 PASS, 1 FAIL, 0 spec-precision gaps in remediation scope.

### Gate Evidence

- Directed: Orca adapter 21, executor 41, pilot 9, planner 18, IT-007 2; **91 passed, 0 failed**.
- Full `npm run test:all`: 110 Vitest tests in 9 files plus all 12 discovered Python suites passed; 0 failed/skipped.
- Strict spec/tasks validators: 0 errors, 0 warnings; AD index current; Python compile, `git diff --check f7a1f366^..f7a1f366`, and Conventional Commit validation passed.
- Structured malformed/secret probe: 2 passed; invalid JSON reduced to return code, structured fields preserved, secret-shaped keys redacted, and oversized text bounded to 256 characters.
- Preexisting dirty/untracked `docs/qa/**` artifacts retained byte-for-byte; no real Orca execution occurred.

### Discrimination Sensor

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| Replace registered source worktree setup with standalone `git init`. | Pilot suite exited 1; common-directory/fixture execution failed. | KILLED |
| Erase structured worker-start `partial_effect` persistence in coordinator. | Executor suite exited 1 at `tools/test_parallel_executor.py:309` with missing `partial_effect`. | KILLED |
| Remove persisted digest-bound authorization write before lane/source deletion. | Pilot suite exited 0: 9 passed, 0 failed. | SURVIVED |

**Sensor:** lightweight, 3 mutations, 2 killed, 1 survived. FAIL. Real-tree porcelain and registered
worktree list returned to their pre-sensor baselines after scratch cleanup.

### Fingerprint Accounting

- `ac14ddc63c46bba3bae6cee000583abd3682ea59a8bee7c2146d4009f9fc43e9` opened at failed-remediation
  count 1 for E2E-001/SEC-008. This is distinct from prior ownership-field and residual-retry
  fingerprints: root cause is missing proof that durable lifecycle authorization precedes deletion.

### Ranked Gap

1. **Major / E2E-001, SEC-008.** Premise: `tools/qa_parallel_pilot.py:379-383` writes an authorization
   and immediately begins destructive removal, while `tools/test_qa_parallel_pilot.py:86-123`
   checks only final cleanup output. Path: remove or lose the pre-delete authorization write;
   lane and source worktrees still delete, and all nine canonical pilot tests pass. Verdict: require
   a digest-bound authorization receipt that is independently presented/read back before deletion,
   and add missing/stale/tampered-authorization cases proving zero effects.

**Overall:** FAIL for QA remediation technical verification. Real QA remains pending after local
remediation and fresh technical verification.

## QA remediation technical re-verification: persisted cleanup authorization

**Date:** 2026-08-25
**Diff range:** `d8c848e^..d8c848e`
**Verifier:** independent Technical Verifier (author != verifier)
**Verdict:** PASS. The public pilot now uses a two-phase protocol: `lifecycle-check --root` persists
the exact digest-bound authorization, and a later normal `cleanup` consumes it. No real Orca run was
performed. QA Execute remains pending.

### Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| E2E-001 / SEC-008 authorization | Normal cleanup has zero deletion without prior authorization; `lifecycle-check` authorizes the exact complete two-lane lifecycle before cleanup. | `tools/test_qa_parallel_pilot.py:55-56` asserts missing authorization is rejected; `:94-116` builds the exact terminal/read/ack/release state and asserts public authorization succeeds. | PASS |
| E2E-001 / SEC-008 stale or tampered binding | A stale or digest-tampered authorization cannot delete the source or lane worktrees. | `tools/test_qa_parallel_pilot.py:117-121` mutates authorized state and asserts rejection plus both worktrees remain. A scratch extension at `:115-124` replaced the persisted digest with 64 zeroes, asserted nonzero cleanup and both worktrees remained, then restored authorization; the full 9-case suite passed. | PASS |
| E2E-001 / SEC-008 valid cleanup and restart | Valid authorization removes only the owned fixture/worktrees and repeated cleanup reports truthful idempotent success. | `tools/test_qa_parallel_pilot.py:124-133` asserts successful deletion, bound lane identity, and idempotent restart. | PASS |
| E2E-001 / SEC-008 diagnostic abort | Incomplete/recoverable worker state remains diagnostic and cannot become normal success. | `tools/test_qa_parallel_pilot.py:140-157` asserts `worker-may-be-live` and source survival; `:251-299` asserts diagnostic retries remain `cleaned: false`, `aborted: true`, and idempotent after residual removal. | PASS |
| EXE-11 / SEC-006 regression | Structured Orca failure and shared-repository setup remain covered. | `tools/test_orca_adapter.py:134-164` asserts bounded structured failure; `tools/test_qa_parallel_pilot.py:23-53` asserts source/child Git common-directory identity and committed task visibility. | PASS |

**Spec-anchored status:** 5 PASS, 0 FAIL, 0 spec-precision gaps in this remediation scope.

### Gate Evidence

- `python3 tools/test_qa_parallel_pilot.py`: 9 passed, 0 failed.
- Directed regressions: Orca adapter 21, executor 41, planner 18, IT-007 2; 82 passed, 0 failed.
- `npm_config_offline=true npm run test:all`: exit 0; 110 Vitest tests in 9 files and all 12 discovered Python suites passed, 0 failed/skipped.
- Strict spec/tasks validators: 0 errors, 0 warnings. AD index current; changed Python compiled; commit message and `git diff --check` passed.
- Preexisting dirty/untracked `docs/qa/**` artifacts remained byte-identical. No real Orca execution occurred.

### Discrimination Sensor

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| Remove `_write_tombstone(attestation, record)` from `authorize_lifecycle`, leaving the public command's success response but no durable authorization. | Canonical `python3 tools/test_qa_parallel_pilot.py` exited 1 at `tools/test_qa_parallel_pilot.py:125`; normal cleanup returned `cleanup-authorization-missing` before deletion. | KILLED |

**Sensor:** lightweight, 1 mutation, 1 killed, 0 survived. PASS. The detached scratch worktree and
all sensor-created pilot fixtures were removed; real-tree porcelain and registered-worktree baseline
were restored.

### Fingerprint Accounting

- `ac14ddc63c46bba3bae6cee000583abd3682ea59a8bee7c2146d4009f9fc43e9` is closed at historical
  failed-remediation count 1. The exact prior authorization-persistence mutant now dies.

### Ranked Gaps

None for this technical remediation. QA retest remains outside this packet.

## Orca worktree discovery race technical verification

**Date:** 2026-08-25  
**Diff range:** `6b3f1f05f4673a9a801fd621fd8ddd327a1cd1f3..2fb2f4197404a46c9b604ab88a5d5fa395a7ecb1`  
**Verifier:** independent Technical Verifier (author != verifier)  
**Verdict:** PASS. Discovery is bounded, tolerates eventual Orca visibility, and precedes exactly
one worker start. Exhaustion preserves the accepted Run/Task selectors and produces no worker
effect; reconciliation reuses those selectors.

### Spec-anchored outcomes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| EXE-06 / SEC-004 discovery boundary | The adapter resolves the persisted checkout and proves Orca can address it before dispatch. | `tools/test_orca_adapter.py:112-130` asserts `show` precedes `worker-start` and the worker receives the exact resolved path; `:170-181` asserts eventual visibility after `selector_not_found`. | PASS |
| EXE-07 eventual visibility | A ready checkout may become visible within the bounded discovery window, after which exactly one correlated worker starts. | `tools/test_orca_adapter.py:170-181` asserts two `show` calls, one `worker-start`, and `dispatch_id == "dispatch-A"`. | PASS |
| EXE-11 bounded failure | Exhausted discovery halts before replacement dispatch and retains decisive recovery selectors. | `tools/test_orca_adapter.py:186-203` asserts `run_id == "run-A"`, `task_id == "task-A"`, stage `worktree-discovery`, attempts `3`, and zero `worker-start` calls. | PASS |
| EXE-04 retry idempotency | Retry reuses the accepted Run/Task partial effect and does not recreate either selector or duplicate worker effects. | `tools/test_orca_adapter.py:135-165` asserts structured failure retains/redacts Run/Task and reconciliation starts with exact `task-A`; `:208-216` asserts repeated accepted start returns the cached receipt with six total effects. | PASS |

**Spec-anchored status:** 4 PASS, 0 FAIL, 0 spec-precision gaps in this remediation scope.

### Gate evidence

- `python3 tools/test_orca_adapter.py` -> exit 0, 24 passed, 0 failed.
- `python3 tools/test_parallel_executor.py` -> exit 0, 43 passed, 0 failed.
- `npm_config_offline=true npm run test:all` -> exit 0: 110 Vitest tests in 9 files plus all 174
  named tests across 12 Python suites passed; 0 failed/skipped. Python count command:
  `rg -c '^\s*def test_' tools/test_*.py | awk -F: '{sum += $2} END {print sum}'`.
- Strict spec/tasks validators -> 0 errors, 0 warnings. AD index current; `git diff --check`
  passed.
- No real Orca QA was run. Existing 113 `docs/qa/**` files and the 14-path porcelain baseline
  remained byte-identical through verification and sensor cleanup.

### Discrimination sensor

One detached temporary worktree at commit `2fb2f4197404a46c9b604ab88a5d5fa395a7ecb1` was removed
after all mutations. The real checkout porcelain and `docs/qa/**` hashes matched their baselines.

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| Reduce discovery attempts from 3 to 1. | Adapter suite exited 1 in `test_worktree_discovery_retries_selector_visibility_before_one_worker_start`. | KILLED |
| Reject the exact discovered worktree path. | Adapter suite exited 1 with `uncorrelated Orca worktree discovery`. | KILLED |
| Drop Run/Task selectors from the structured discovery-timeout receipt. | Adapter suite exited 1 at `tools/test_orca_adapter.py:197`, missing `run_id`. | KILLED |

**Sensor:** lightweight, 3 mutations, 3 killed, 0 survived. PASS.

### Fingerprint accounting

No blocker or surviving mutant was found, so no new fingerprint was opened and no existing
failed-remediation count changed. Existing ledger entries remain closed at their historical counts.

### Ranked gaps

None for this technical remediation. Fresh real Orca QA remains outside this packet.
