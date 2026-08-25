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

T2R4 also matches AD-014: remediation accounting is keyed by requirement, root cause, and concrete
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
| T2R1-T2R3 distinct blockers | Remain closed by their existing direct assertions; they do not consume the IT-001 fingerprint count under AD-014 and `docs/guidelines/REVIEW-ROUNDS.md:89-91`. |

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

### Prior Fingerprint Re-derivation and AD-014 Counts

AD-014 identity remains requirement + root cause + concrete failure path. A passing scoped
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

## Orca stalled-dispatch recovery technical verification

**Date:** 2026-08-25  
**Diff range:** `3a9f346..8675c6d64fe02bca8f1471fd4161b5327516b1b0`  
**Verifier:** independent Technical Verifier (author != verifier)  
**Verdict:** FAIL. Bounded start, structured partial-effect preservation, live-dispatch refusal,
one correlated retry, and same-process retry caching are directly asserted. Restart after a persisted
recovery release cannot converge, and two required safety branches are not discriminated.

### Spec-anchored outcomes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| EXE-07 / SEC-003 bounded start | Every initial or follow-up worker start carries an explicit bounded timeout. | `tools/test_orca_adapter.py:112-131` asserts the exact `--timeout-ms` value on the initial `worker-start`; production applies it at `.agents/skills/autonomous/scripts/orca_adapter.py:393-396,585-589`. Sensor M1 removes the flag and dies. | PASS |
| EXE-04 / EXE-07 structured partial effect | `agent_prompt_stalled` preserves redacted Run, Task, Dispatch, and terminal selectors for deterministic recovery. | `tools/test_orca_adapter.py:136-156` asserts the exact four selectors and redacted nested token; normalization is `.agents/skills/autonomous/scripts/orca_adapter.py:134-158`. | PASS |
| EXE-04 one retry / same selectors | A reclaimable failed dispatch releases once, then one `worker-start --retry-of` reuses the exact Run and Task; replay in the same process creates no second effect. | `tools/test_orca_adapter.py:158-177` asserts `worker-show, worker-release, show, worker-start`, exact `task-A`, `--retry-of dispatch-A`, equal replay receipt, and four total calls. | PASS |
| EXE-04 restart idempotency | After recovery release is persisted, restart continues the same logical retry without another release or duplicate Run/Task. | Adversarial restart probe supplied `partial_effect.recovery_release`, `worker-show status=released`, exact Run/Task, and a correlated retry response. `.agents/skills/autonomous/scripts/orca_adapter.py:576-583` rejected `released` as `worker_still_live` before consulting the persisted release, so no retry occurred. No canonical `file:line` assertion covers this restart boundary. | FAIL |
| EXE-11 live/unknown safety | Live or unknown stalled dispatches halt with no release and no replacement retry. | `tools/test_orca_adapter.py:220-234` asserts the live `running` case and only one `worker-show`. No assertion covers `unknown`; sensor M4 makes `unknown` reclaimable and all 26 adapter tests still pass. | FAIL |
| EXE-08 / EXE-11 stale revoked delivery | Release establishes revocation, and later `worker_done` for that dispatch is rejected. | `tools/test_orca_adapter.py:239-251` inserts `worker._revoked_dispatches.add(...)` directly, then asserts rejection. It never proves the release path at `.agents/skills/autonomous/scripts/orca_adapter.py:608-621` establishes the state; sensor M5 removes that registration and all 26 adapter tests still pass. This is a hollow contracted case under `docs/guidelines/TEST-CONTRACT.md:38-39`. | FAIL |

**Spec-anchored status:** 3 PASS, 3 FAIL, 0 spec-precision gaps in this remediation scope.

### Gate evidence

- `python3 tools/test_orca_adapter.py` -> exit 0, 26 passed, 0 failed.
- `python3 tools/test_parallel_executor.py` -> exit 0, 43 passed, 0 failed.
- `npm run test:all` -> exit 0: 110 Vitest tests in 9 files plus 174 named tests across 12
  Python suites passed; 0 failed/skipped.
- `python3 -m py_compile .agents/skills/autonomous/scripts/orca_adapter.py tools/test_orca_adapter.py`
  and `git diff --check 3a9f346..8675c6d64fe02bca8f1471fd4161b5327516b1b0` -> exit 0.
- No real Orca command, retained Run/Task/Dispatch/terminal, pilot fixture, or QA execution was used.
  All 15 pre-existing dirty/untracked `docs/qa/**` paths retained their baseline SHA-256 values.

### Discrimination sensor

Detached temporary worktrees at `8675c6d64fe02bca8f1471fd4161b5327516b1b0` were removed after
each run. The retained checkout was never mutated by a sensor.

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| M1: remove initial `--timeout-ms`. | Adapter suite exited 1 at `tools/test_orca_adapter.py:123`. | KILLED |
| M2: treat live `running` dispatch as reclaimable. | Adapter suite exited 1 in `test_live_stalled_dispatch_fails_safely_without_release_or_retry`. | KILLED |
| M3: remove stale-delivery rejection guard. | Adapter suite exited 1 at `tools/test_orca_adapter.py:251`. | KILLED |
| M4: treat `unknown` dispatch as reclaimable. | Adapter suite exited 0, 26 passed. | SURVIVED |
| M5: remove revoked-dispatch registration from successful release. | Adapter suite exited 0, 26 passed. | SURVIVED |

**Sensor:** lightweight, 5 mutations, 3 killed, 2 survived. FAIL.

### Fingerprint accounting

- `d2990822a9e55159df279a3589e8be3a245fcb9dbe1ddd537dd1934dc2aa3685` opened at count 1:
  EXE-04 restart classifies a persisted released recovery as live before retry.
- `f719a74c8684c3ed7be2f89e9b02aa6ee132c4cbb395d6dbb1859e36d6a9846a` opened at count 1:
  EXE-11 unknown-status safety has no discriminating assertion.
- `d493f883d50981fe0c2d9e1c4b7244a3e0cd456b26822144cb98a9fec3a529a2` opened at count 1:
  EXE-08/EXE-11 stale-delivery test injects private state and does not prove release-to-revocation.

### Ranked gaps

1. **Major / EXE-04.** Reorder/extend reconciliation so a correlated persisted recovery release and
   authoritative terminal `released|complete|completed` status can continue exactly one
   `worker-start --retry-of` with the original Run/Task and zero additional release. Add a fresh
   adapter/reloaded-action test that fails if release or retry duplicates.
2. **Major / EXE-11.** Add a canonical `unknown`/missing-status case proving `worker_outcome_unknown`,
   one `worker-show`, zero release, and zero retry.
3. **Major / EXE-08, EXE-11.** Replace private-set injection with a public release-to-stale-delivery
   lifecycle assertion; it must fail if successful release no longer registers revocation.

**Overall:** FAIL for commit `8675c6d64fe02bca8f1471fd4161b5327516b1b0`. Gates are green but
restart convergence and two required safety contracts lack valid proof. No real Orca QA was run.

## Orca stalled-dispatch recovery re-verification — round 1

**Date:** 2026-08-25  
**Diff range:** `8675c6d64fe02bca8f1471fd4161b5327516b1b0..6419d2411d3d47f6466c39623aa25bf0d4b911d6`  
**Verifier:** independent Technical Verifier (author != verifier)  
**Verdict:** FAIL. All three prior fingerprints close at their historical count 1. Adding the
unknown-status assertion removed the previously valid live/running-status assertion, producing one
new EXE-11 coverage blocker.

### Prior fingerprint disposition

| Fingerprint | Required outcome | Evidence | Result |
| --- | --- | --- | --- |
| `d2990822a9e55159df279a3589e8be3a245fcb9dbe1ddd537dd1934dc2aa3685` | Persisted accepted recovery release plus authoritative `released` status proceeds to exactly one retry without another release. | `tools/test_orca_adapter.py:239-259` asserts persisted correlated release and exact `worker-show, show, worker-start`; implementation validates release before retry at `.agents/skills/autonomous/scripts/orca_adapter.py:576-605`. Sensor R1 removes `released` from reclaimable terminal states and dies. | CLOSED, count 1 |
| `f719a74c8684c3ed7be2f89e9b02aa6ee132c4cbb395d6dbb1859e36d6a9846a` | Unknown status remains non-reclaimable with zero release/retry. | `tools/test_orca_adapter.py:220-235` asserts `worker_outcome_unknown` and only `worker-show`. Sensor R2 makes `unknown` reclaimable and dies on unexpected `worker-release`. | CLOSED, count 1 |
| `d493f883d50981fe0c2d9e1c4b7244a3e0cd456b26822144cb98a9fec3a529a2` | Successful public worker release establishes revocation and stale `worker_done` is rejected. | `tools/test_orca_adapter.py:263-277` calls public `release`, asserts accepted release, then rejects stale delivery; production registers revocation at `.agents/skills/autonomous/scripts/orca_adapter.py:618-631`. Sensor R3 removes registration and dies. | CLOSED, count 1 |

### New regression

| Criterion | Spec-defined outcome | Evidence | Result |
| --- | --- | --- | --- |
| EXE-11 live stalled dispatch | Authoritative `running` status halts after one `worker-show`, with zero release and zero replacement retry. | No canonical test now supplies `status=running`; the former running case was replaced by the unknown case. Sensor R4 makes `running` reclaimable and `python3 tools/test_orca_adapter.py` still exits 0 with 27/27 passing. | FAIL |

### Gate evidence

- `python3 tools/test_orca_adapter.py` -> 27 passed, 0 failed.
- `python3 tools/test_parallel_executor.py` -> 43 passed, 0 failed.
- `npm run test:all` -> 110 Vitest + 175 Python = 285 passed, 0 failed/skipped.
- No real Orca state or QA execution was used. Retained QA artifacts remained byte-identical.

### Discrimination sensor

| Mutation | Result | Outcome |
| --- | --- | --- |
| R1 remove `released` from correlated persisted-release recovery. | Adapter suite fails in `test_persisted_release_receipt_allows_retry_when_dispatch_status_is_released`. | KILLED |
| R2 make `unknown` reclaimable. | Adapter suite fails in `test_unknown_stalled_dispatch_fails_safely_without_release_or_retry`. | KILLED |
| R3 remove revocation registration from successful worker release. | Adapter suite fails at `tools/test_orca_adapter.py:276`. | KILLED |
| R4 make live `running` reclaimable. | Adapter suite passes 27/27. | SURVIVED |

**Sensor:** lightweight, 4 mutations, 3 killed, 1 survived. FAIL. Detached scratch removed; retained
checkout never received sensor mutations.

### Fingerprint accounting

- Prior three fingerprints: `closed`, failed-remediation count remains 1 each.
- `8917833abd974503a1d2c644cf910a1cee764e426a8181c2fc64170002e79d17` opened at count 1 for
  EXE-11: adding unknown coverage replaced live/running coverage.

### Ranked gap

1. **Major / EXE-11.** Keep the unknown case and restore a separate `status=running` case asserting
   `worker_still_live`, exactly one `worker-show`, zero `worker-release`, and zero `worker-start`.

**Overall:** FAIL for round 1 at `6419d2411d3d47f6466c39623aa25bf0d4b911d6`. The exact three prior
blockers are fixed; one distinct live-status coverage blocker remains.

## Orca stalled-dispatch recovery re-verification — round 2

**Date:** 2026-08-25  
**Diff range:** `6419d2411d3d47f6466c39623aa25bf0d4b911d6..453a8ab28cba313142cacf433e27d2572bb5695d`  
**Verifier:** independent Technical Verifier (author != verifier)  
**Verdict:** PASS. The canonical suite now keeps separate live/running and unknown stalled-dispatch
cases. Both refuse release and replacement retry after exactly one authoritative status read.

### Spec-anchored outcomes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| EXE-11 live stalled dispatch | `running` halts with `worker_still_live`, one `worker-show`, zero release, and zero retry. | `tools/test_orca_adapter.py:239-255` asserts the exact error and command/effect absence. | PASS |
| EXE-11 unknown stalled dispatch regression | `unknown` halts with `worker_outcome_unknown`, one `worker-show`, zero inferred recovery effects. | `tools/test_orca_adapter.py:220-234` asserts the exact error and sole command. | PASS |

### Gate evidence

- `python3 tools/test_orca_adapter.py` -> 28 passed, 0 failed.
- `python3 tools/test_parallel_executor.py` -> 43 passed, 0 failed.
- `npm run test:all` -> 110 Vitest + 176 Python = 286 passed, 0 failed/skipped.
- Changed Python compiles and committed/in-checkout diffs pass `git diff --check`.
- No real Orca command or QA execution ran; retained QA artifacts remained byte-identical.

### Discrimination sensor

| Mutation | Result | Outcome |
| --- | --- | --- |
| R2-M1 make authoritative `running` reclaimable. | Adapter suite exits 1 in `test_running_stalled_dispatch_fails_safely_without_release_or_retry` on unexpected `worker-release`. | KILLED |
| R2-M2 make authoritative `unknown` reclaimable. | Adapter suite exits 1 in `test_unknown_stalled_dispatch_fails_safely_without_release_or_retry` on unexpected `worker-release`. | KILLED |

**Sensor:** lightweight, 2 mutations, 2 killed, 0 survived. PASS. Detached scratch removed; retained
checkout never received sensor mutations.

### Fingerprint accounting

- `8917833abd974503a1d2c644cf910a1cee764e426a8181c2fc64170002e79d17` closed at historical
  failed-remediation count 1.
- All feature fingerprints are now closed; this passing re-verification increments none.

### Ranked gaps

None in this remediation scope.

**Overall:** PASS at `453a8ab28cba313142cacf433e27d2572bb5695d`. All stalled-dispatch
recovery technical fingerprints are closed. Real Orca QA remains outside this technical phase.

## Nested Orca dispatch identity technical verification

**Date:** 2026-08-25  
**Diff range:** `fd9fbc1..5687696f43d4bd7c07cc300be8d2905d2243f9cc`  
**Verifier:** independent Technical Verifier (author != verifier)  
**Verdict:** FAIL. Nested Orca dispatch IDs are normalized and preserved through the stalled-worker
recovery path, canonical IDs retain precedence, valid `ctx_...` values remain opaque, and unsafe
tokens are rejected before argv execution. A missing dispatch ID in the authoritative
`worker-show` response is still accepted as correlated, allowing `worker-release` and replacement
`worker-start` mutations.

### Spec-anchored outcomes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| EXE-04 / EXE-07 nested identity continuity | Real `error.dispatch.id` and `result.dispatch.id` normalize to the same dispatch identity across stalled failure, status read, release, and `--retry-of`. | `tools/test_orca_adapter.py:182-212` asserts exact `ctx_5f619d0f6298` extraction from the error, nested result status/release receipts, and exact retry argv identity. | PASS |
| SEC-005 canonical precedence | An explicit canonical `dispatch_id` cannot be overwritten by a nested alias. | `tools/test_orca_adapter.py:217-218` asserts `ctx_explicit` wins over `dispatch.id == ctx_other`; production precedence is `.agents/skills/autonomous/scripts/orca_adapter.py:103-118,130-133`. | PASS |
| EXE-07 opaque provider identity | A real `ctx_...` identity remains byte-for-byte opaque instead of being rewritten to an invented format. | `tools/test_orca_adapter.py:184,193-194,211-212` asserts the same `ctx_5f619d0f6298` at extraction and `--retry-of`. | PASS |
| SEC-003 unsafe-token boundary | Empty, whitespace, control, quote, backtick, and shell-delimiter forms are rejected without shell interpolation. | Canonical assertions at `tools/test_orca_adapter.py:217-224` reject representative whitespace/newline/semicolon/backtick/quote values; `:750-758` asserts every Orca call is argv-only with `shell=False`. An independent 20-value probe rejected all requested classes and an unsafe persisted token produced zero CLI calls. | PASS |
| EXE-11 / SEC-005 missing authoritative identity | A `worker-show` response missing its nested dispatch ID must halt before release or replacement mutation. | No canonical assertion exists. Independent probe returned `status=failed` without a dispatch ID and observed `worker-show, worker-release, show, worker-start`. Production explicitly accepts `actual_dispatch is None` at `.agents/skills/autonomous/scripts/orca_adapter.py:614-617`, then mutates at `:633-641`. | FAIL |

**Spec-anchored status:** 4 PASS, 1 FAIL, 0 spec-precision gaps in this remediation scope.

### Gate evidence

- `python3 tools/test_orca_adapter.py` -> 30 passed, 0 failed.
- `python3 tools/test_parallel_executor.py` -> 43 passed, 0 failed.
- `npm run test:all` -> exit 0: 110 Vitest tests in 9 files plus 180 named Python tests across
  12 suites, 290 passed, 0 failed/skipped. Python count command:
  `rg -c '^\s*def test_' tools/test_*.py | awk -F: '{sum += $2} END {print sum}'`.
- Adapter suite changed from 28 tests at `fd9fbc1` to 30 at `5687696`; delta +2.
- `git diff --check fd9fbc1..5687696f43d4bd7c07cc300be8d2905d2243f9cc` -> exit 0.
- No real Orca Run, Task, Dispatch, terminal, pilot state, or QA evidence was read or mutated.
  The retained `docs/qa/**` porcelain baseline remained unchanged.

### Discrimination sensor

One detached temporary worktree at `5687696f43d4bd7c07cc300be8d2905d2243f9cc` was removed after
the mutations. The retained checkout never received sensor mutations.

| Mutation | Result | Outcome |
| --- | --- | --- |
| Return an invented dispatch value instead of nested `dispatch.id`. | Adapter suite exited 1 in the unsafe/nested identity contract. | KILLED |
| Force nested `dispatch.id` to override explicit canonical `dispatch_id`. | Adapter suite exited 1 at `tools/test_orca_adapter.py:218`. | KILLED |
| Disable dispatch-token character validation. | Adapter suite exited 1 at `tools/test_orca_adapter.py:224`. | KILLED |

**Sensor:** lightweight, 3 mutations, 3 killed, 0 survived. PASS.

### Fingerprint accounting

- `e83afdfc460cf5e658dcb0575b589ad3f842ee0ec230335bc715fbe589dcd3b4` opened at failed-remediation
  count 1: EXE-11/SEC-005, missing nested `worker-show` dispatch identity permits release and
  replacement retry.
- Prior closed fingerprints remain closed and their historical counts are unchanged.

### Ranked gap

1. **Major / EXE-11, SEC-005.** Require the authoritative `worker-show` receipt to carry a
   normalized dispatch ID equal to the persisted ID before interpreting status. Add a canonical
   missing-ID case that asserts one `worker-show`, zero `worker-release`, and zero replacement
   `worker-start`.

**Overall:** FAIL for commit `5687696f43d4bd7c07cc300be8d2905d2243f9cc`. Green gates and killed
mutants do not close the missing-correlation safety gap. Real Orca QA remains outside this technical
packet.

## Nested Orca dispatch correlation re-verification

**Date:** 2026-08-25  
**Diff range:** `5687696f43d4bd7c07cc300be8d2905d2243f9cc..941bbc5ddd02b6bd7893165c2be67a8a3044fce1`  
**Verifier:** independent Technical Verifier (author != verifier)  
**Verdict:** PASS. Missing, malformed, and mismatched authoritative dispatch identities now halt
after exactly one `worker-show`, before release or replacement retry. The matching nested
`ctx_...` recovery path remains intact.

### Spec-anchored outcomes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| EXE-11 / SEC-005 missing identity | A nested `worker-show` response without a dispatch ID halts before any release or replacement worker. | `tools/test_orca_adapter.py:329-344` asserts `uncorrelated_dispatch` and the sole command `worker-show`; production validates before mutation at `.agents/skills/autonomous/scripts/orca_adapter.py:614-624,640-647`. | PASS |
| EXE-11 / SEC-005 malformed or mismatched identity | Unsafe or foreign authoritative IDs cannot correlate to the persisted dispatch and produce zero recovery mutation. | Independent probes supplied `ctx bad` and `ctx_other`; both raised after one `worker-show` with zero release/retry. Shared validation is `.agents/skills/autonomous/scripts/orca_adapter.py:615-624`; canonical unsafe-token assertions remain at `tools/test_orca_adapter.py:217-224`. | PASS |
| EXE-04 / EXE-07 matching nested identity | A matching real nested `ctx_...` value remains opaque through show, release, and `--retry-of`. | `tools/test_orca_adapter.py:182-212` asserts exact `ctx_5f619d0f6298` extraction and retry identity. | PASS |

**Spec-anchored status:** 3 PASS, 0 FAIL, 0 spec-precision gaps in this remediation scope.

### Gate evidence

- `python3 tools/test_orca_adapter.py` -> 31 passed, 0 failed.
- `python3 tools/test_parallel_executor.py` -> 43 passed, 0 failed.
- `npm run test:all` -> exit 0: 110 Vitest tests plus 181 named Python tests, 291 passed,
  0 failed/skipped.
- Adapter suite changed from 30 tests at `5687696` to 31 at `941bbc5`; delta +1.
- No real Orca state or retained QA/evidence artifact was mutated.

### Discrimination sensor

One detached temporary worktree at `941bbc5ddd02b6bd7893165c2be67a8a3044fce1` restored the prior
fault by accepting `None` as correlated. The canonical adapter suite failed when the missing-ID
case attempted `worker-release`. Scratch removed; retained checkout unchanged.

**Sensor:** lightweight, 1 mutation, 1 killed, 0 survived. PASS.

### Fingerprint accounting

- `e83afdfc460cf5e658dcb0575b589ad3f842ee0ec230335bc715fbe589dcd3b4` is CLOSED at historical
  failed-remediation count 1.
- No new fingerprint opened.

### Ranked gaps

None in this remediation scope.

**Overall:** PASS at `941bbc5ddd02b6bd7893165c2be67a8a3044fce1`. The exact correlation
blocker is closed. Real Orca QA remains outside this technical packet.

## Persisted nested dispatch restart re-verification

**Date:** 2026-08-25  
**Diff range:** `b0d2c22..e24228c7e1e285a1b718e1c87466cfad29e1a078`  
**Verifier:** independent Technical Verifier (author != verifier)  
**Verdict:** PASS. The exact persisted QA shape with no top-level `dispatch_id` is normalized before
the first adapter call, retains its Run/Task/terminal identity, and retries the same dispatch once.

### Spec-anchored outcomes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| EXE-04 restart normalization | `partial_effect.result.dispatchId` and `partial_effect.result.dispatch.id` normalize to one canonical opaque dispatch ID while preserving Run/Task. | `tools/test_orca_adapter.py:182-212` covers `result.dispatch.id`; `tools/test_orca_adapter.py:348-368` supplies exact `ctx_5f619d0f6298` through `result.dispatchId`, asserts `run-A`, `task-A`, and the canonical persisted `dispatch_id`. | PASS |
| SEC-005 canonical precedence | An explicit canonical dispatch identity wins over nested aliases and cannot be replaced by a foreign nested value. | `tools/test_orca_adapter.py:217-224` asserts canonical `dispatch_id == ctx_explicit` over `dispatch.id == ctx_other`; production precedence and validation are `.agents/skills/autonomous/scripts/orca_adapter.py:103-154`. | PASS |
| EXE-04 exact recovery order | Restart performs one correlated `worker-show`, one release, then one `worker-start --retry-of` with the original task and dispatch; replay is idempotent. | `tools/test_orca_adapter.py:158-177` asserts exact command order, exact task/retry IDs, equal replay receipt, and no fifth call; `tools/test_orca_adapter.py:348-368` repeats the exact nested persisted shape. | PASS |
| EXE-05 / EXE-11 invalid identity safety | Missing, malformed, or mismatched nested dispatch identities halt before any release or replacement-worker mutation. | `tools/test_orca_adapter.py:217-224,329-344,373-387` asserts unsafe/missing persisted or authoritative IDs and zero mutating calls; correlation guard precedes mutation at `.agents/skills/autonomous/scripts/orca_adapter.py:611-647`. | PASS |

**Spec-anchored status:** 4 PASS, 0 FAIL, 0 spec-precision gaps in this remediation scope.

### Gate evidence

- `python3 tools/test_orca_adapter.py` -> 33 passed, 0 failed; 0 skipped.
- `npm run test:all` -> exit 0: 110 Vitest tests plus 181 Python tests, 291 passed,
  0 failed/skipped.
- Adapter suite changed from 31 tests at `b0d2c22` to 33 at `e24228c7`; delta +2.
- `git diff --check b0d2c22..e24228c7e1e285a1b718e1c87466cfad29e1a078` -> exit 0.
- No real Orca command/state, product code, test, or retained `docs/qa/**` artifact was mutated by
  this verification.

### Discrimination sensor

One detached temporary worktree at `e24228c7e1e285a1b718e1c87466cfad29e1a078` received three
behavior faults. It was removed afterward; retained-checkout porcelain exactly matched its baseline.

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| M1 disable `result` envelope unwrapping. | Adapter suite exited 1 in nested dispatch recovery before a valid terminal status could be proven. | KILLED |
| M2 replace the recovered `--retry-of` value with a foreign dispatch. | Adapter suite exited 1 at `tools/test_orca_adapter.py:212`. | KILLED |
| M3 disable the cached-receipt replay short circuit. | Adapter suite exited 1 on an unexpected second `worker-show`. | KILLED |

**Sensor:** lightweight, 3 mutations, 3 killed, 0 survived. PASS.

### Fingerprint accounting

- No new fingerprint opened; all prior dispatch-recovery fingerprints remain closed at their
  historical counts.

### Ranked gaps

None in this remediation scope.

**Overall:** PASS at `e24228c7e1e285a1b718e1c87466cfad29e1a078`. Exact persisted nested
dispatch restart recovery is spec-correlated, idempotent, and discriminating. Real Orca QA remains
outside this technical phase.

## Authoritative Orca terminal recovery technical verification

**Date:** 2026-08-25  
**Diff range:** `40de33e..c17e274bbe66739c203857122b54e0186b929718`  
**Verifier:** independent Technical Verifier (author != verifier)  
**Verdict:** FAIL. Production correlates dispatch before terminal, extracts and validates the
authoritative terminal from nested `worker-show`, persists it, then releases and retries the
original Run/Task once. The exact missing-persisted-terminal contract is not discriminating:
removing the persistence write leaves the complete adapter suite green.

### Spec-anchored outcomes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| EXE-04 / SEC-005 dispatch-before-terminal correlation | Persisted dispatch identity is validated against authoritative `worker-show` before terminal recovery or mutation. | `.agents/skills/autonomous/scripts/orca_adapter.py:642-668` orders dispatch correlation before terminal extraction/persistence; `tools/test_orca_adapter.py:393-415` asserts missing, malformed, and conflicting authoritative terminals halt after one `worker-show`. | PASS |
| EXE-04 authoritative terminal recovery | A persisted partial containing valid nested Run/Task/dispatch but no terminal obtains the owned terminal from nested `worker-show` and persists it before release/retry. | Production writes the recovered handle at `.agents/skills/autonomous/scripts/orca_adapter.py:654-668`. Canonical positive cases already provide a persisted terminal at `tools/test_orca_adapter.py:167,206,360`; no assertion starts without it. Removing line 668 leaves 34/34 adapter tests green. | FAIL |
| EXE-04 exact release/retry/replay | Only after correlation, recovery performs one release and one `worker-start --retry-of` for the original task; replay creates no fifth command. | `tools/test_orca_adapter.py:158-177` asserts exact `worker-show, worker-release, show, worker-start`, original task/dispatch, equal replay receipt, and four total calls. | PASS |
| EXE-11 / SEC-005 invalid terminal safety | Missing, malformed, or conflicting authoritative terminal halts after one show with zero release, retry, or persisted-terminal mutation. | `tools/test_orca_adapter.py:393-415` supplies all three invalid forms, asserts `uncorrelated_terminal`, and asserts the sole CLI command is `worker-show`; mutation occurs only after the guards at `.agents/skills/autonomous/scripts/orca_adapter.py:654-668`. | PASS |

**Spec-anchored status:** 3 PASS, 1 FAIL, 0 spec-precision gaps in this remediation scope.

### Gate evidence

- `python3 tools/test_orca_adapter.py` -> 34 passed, 0 failed; 0 skipped.
- `python3 tools/test_parallel_executor.py` -> 43 passed, 0 failed; 0 skipped.
- `npm run test:all` -> exit 0: 110 Vitest tests plus 184 Python tests, 294 passed,
  0 failed/skipped.
- Adapter suite changed from 33 tests at `40de33e` to 34 at `c17e274`; delta +1.
- `git diff --check 40de33e c17e274bbe66739c203857122b54e0186b929718` and
  `python3 -m py_compile .agents/skills/autonomous/scripts/orca_adapter.py tools/test_orca_adapter.py`
  -> exit 0.
- No real Orca command/state, product code, test, or retained `docs/qa/**` artifact was mutated by
  this verification.

### Discrimination sensor

One detached temporary worktree at `c17e274bbe66739c203857122b54e0186b929718` received the
behavior fault and was removed afterward. Retained-checkout porcelain exactly matched its baseline
except for this report and convergence ledger.

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| Remove `partial["terminal_handle"] = authoritative_terminal` after successful authoritative `worker-show` correlation. | `python3 tools/test_orca_adapter.py` exited 0 with 34/34 passing. | SURVIVED |

**Sensor:** lightweight, 1 mutation, 0 killed, 1 survived. FAIL.

### Fingerprint accounting

- `f75de026b0aedf16589fe20f53a89fcf013196c731ff602b7a181d33a04e10b8` opened at
  failed-remediation count 1 for EXE-04/SEC-005. Prior fingerprints remain unchanged.

### Ranked gap

1. **Major / EXE-04, SEC-005.** Add one canonical positive restart case whose persisted partial has
   nested Run/Task/dispatch but no terminal. Return the owned terminal only from the real nested
   `worker-show` envelope; assert it is persisted before the one release and one exact retry, then
   assert replay adds no command. The test must fail when the persistence write is removed.

**Overall:** FAIL for `c17e274bbe66739c203857122b54e0186b929718`. Runtime logic matches the
requested recovery path, but evidence-or-zero rejects completion because the exact persistence
behavior has a surviving mutant. Real Orca QA remains outside this technical phase.

## Authoritative Orca terminal recovery re-verification

**Date:** 2026-08-25  
**Diff range:** `c17e274bbe66739c203857122b54e0186b929718..35a49bf8d5ddb3e3d836fa4963b3665c0f8a17cd`  
**Verifier:** independent Technical Verifier (author != verifier)  
**Verdict:** PASS. The canonical positive restart case now begins with nested Run/Task/dispatch and
no terminal, obtains the owned terminal solely from nested `worker-show`, proves persistence before
release, then proves one exact retry and idempotent replay.

### Spec-anchored outcomes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| EXE-04 / SEC-005 missing-terminal recovery | A persisted partial with Run/Task/dispatch but no terminal recovers and persists the authoritative owned terminal before mutation. | `tools/test_orca_adapter.py:380-402` creates the exact terminal-free partial, asserts absence, supplies the terminal only in nested `worker-show`, and observes persistence before `worker-release`. | PASS |
| EXE-04 single release/retry | Recovery issues one release and one retry of the same dispatch and original task. | `tools/test_orca_adapter.py:393-406` asserts exact `worker-show, worker-release, show, worker-start`, `--retry-of == ctx_5f619d0f6298`, and `--task == task-A`. | PASS |
| EXE-04 replay idempotency | Replaying the accepted action returns the cached receipt and creates no external call. | `tools/test_orca_adapter.py:407-408` asserts equal receipt and four total calls after replay. | PASS |
| EXE-11 / SEC-005 invalid terminal safety | Missing, malformed, or conflicting authoritative terminal still halts after one show with zero release/retry. | `tools/test_orca_adapter.py:432-454` retains all three fail-closed cases and asserts only `worker-show`. | PASS |

**Spec-anchored status:** 4 PASS, 0 FAIL, 0 spec-precision gaps.

### Gate evidence

- `python3 tools/test_orca_adapter.py` -> 35 passed, 0 failed; 0 skipped.
- `python3 tools/test_parallel_executor.py` -> 43 passed, 0 failed; 0 skipped.
- `npm run test:all` -> exit 0: 110 Vitest tests plus 185 Python tests, 295 passed,
  0 failed/skipped.
- Adapter suite changed from 34 tests at `c17e274` to 35 at `35a49bf`; delta +1.
- `git diff --check c17e274bbe66739c203857122b54e0186b929718 35a49bf8d5ddb3e3d836fa4963b3665c0f8a17cd`
  -> exit 0.
- No real Orca command/state, product code, test, or retained `docs/qa/**` artifact was mutated by
  this verification.

### Discrimination sensor

One detached temporary worktree at `35a49bf8d5ddb3e3d836fa4963b3665c0f8a17cd` removed
`partial["terminal_handle"] = authoritative_terminal`. The directed adapter suite exited 1 in the
new canonical case before release because the expected persisted terminal was absent. Scratch was
removed; retained-checkout porcelain returned to its baseline except for this report and ledger.

**Sensor:** lightweight, 1 mutation, 1 killed, 0 survived. PASS.

### Fingerprint accounting

- `f75de026b0aedf16589fe20f53a89fcf013196c731ff602b7a181d33a04e10b8` is CLOSED at historical
  failed-remediation count 1. No new fingerprint opened.

### Ranked gaps

None in this remediation scope.

**Overall:** PASS at `35a49bf8d5ddb3e3d836fa4963b3665c0f8a17cd`. The exact authoritative
terminal persistence contract is now spec-correlated, ordered, idempotent, and discriminating.
Real Orca QA remains outside this technical phase.

## Orphaned Orca release reconciliation technical verification

**Date:** 2026-08-25  
**Diff range:** `48ec1cb97ce843fa084340b9c41e3fd320416686..87f1bb5b55255beb84b66b1c7621041ff6695cd8`  
**Verifier:** independent Technical Verifier (author != verifier)  
**Verdict:** FAIL. Runtime accepts only a structured `tab_not_found`, performs an authoritative
post-release `worker-show`, requires the same dispatch and terminal to be exited, disconnected, and
non-writable, persists a reconciled release receipt, revokes the old dispatch, and retries the
original Run/Task once. The new canonical tests do not discriminate all of those safety boundaries.

### Spec-anchored outcomes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| EXE-04 / SEC-005 exact release recovery | Only structured `tab_not_found` enters recovery; an authoritative post-release show must correlate the same dispatch and terminal. | Catch/dispatch is `.agents/skills/autonomous/scripts/orca_adapter.py:743-750`; correlation guard is `:291-316`; `tools/test_orca_adapter.py:419-435` proves the positive structured error and exact command order. Removing the post-show dispatch comparison leaves 37/37 tests green. | FAIL |
| EXE-11 terminal liveness safety | Live, connected, writable, unknown, missing, or mismatched state remains `release_unknown` with zero replacement retry. | `.agents/skills/autonomous/scripts/orca_adapter.py:302-316`; `tools/test_orca_adapter.py:440-463` asserts connected, writable, terminal mismatch, and unknown cases stop after the post-show. The status mutant dies, but post-show dispatch mismatch/missing correlation is not discriminated. | FAIL |
| EXE-03 / EXE-04 persisted release receipt | The repeated release uses the derived recovery request key and persists an explicit correlated reconciliation receipt before retry/restart. | Request and persistence are `.agents/skills/autonomous/scripts/orca_adapter.py:743-750`; receipt fields are `:318-329`; `tools/test_orca_adapter.py:428-435` asserts persistence, replay, and selected receipt fields. Replacing the request key or persisting `connected: true` leaves 37/37 tests green. | FAIL |
| EXE-04 same Run/Task retry and replay | Accepted reconciliation starts one `worker-start --retry-of` for the original task/dispatch and replay creates no extra effect. | `.agents/skills/autonomous/scripts/orca_adapter.py:751-762`; `tools/test_orca_adapter.py:431-435` asserts Run/Task receipt, retry dispatch, equal replay, and five calls; `tools/test_orca_adapter.py:400-408` independently asserts the original task argument. Mutating the task argument kills the suite. | PASS |
| EXE-08 / EXE-11 stale dispatch revocation | A reconciled orphaned dispatch is revoked before replacement so a late delivery cannot be accepted. | Revocation is `.agents/skills/autonomous/scripts/orca_adapter.py:317`; stale rejection is `:551-557`. `tools/test_orca_adapter.py:512-527` proves revocation for normal release only. Removing reconciliation-path revocation leaves 37/37 tests green. | FAIL |

**Spec-anchored status:** 1 PASS, 4 FAIL, 0 spec-precision gaps in this remediation scope.

### Gate evidence

- `python3 tools/test_orca_adapter.py` -> 37 passed, 0 failed; 0 skipped.
- `python3 tools/test_parallel_executor.py` -> 43 passed, 0 failed; 0 skipped.
- `npm run test:all` -> exit 0: 110 Vitest tests plus 185 Python tests, 295 passed,
  0 failed/skipped.
- Adapter suite changed from 35 tests at `48ec1cb` to 37 at `87f1bb5`; delta +2.
- Strict spec/tasks validators, AD index, `git diff --check 48ec1cb 87f1bb5`, and Python compile
  -> exit 0.
- No real Orca command/state, product code, test, or retained `docs/qa/**` artifact was mutated.

### Discrimination sensor

Two detached temporary worktrees at `87f1bb5b55255beb84b66b1c7621041ff6695cd8` received seven
behavior faults and were removed. Retained-checkout porcelain returned to its baseline plus only
this report and the convergence ledger.

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| M1 ignore post-release dispatch mismatch. | Adapter suite exited 0, 37/37 passed. | SURVIVED |
| M2 accept unknown post-release status. | Adapter suite exited 1 in `test_tab_not_found_postcheck_live_unknown_or_mismatched_blocks_retry`. | KILLED |
| M3 replace derived recovery idempotency key with a foreign constant. | Adapter suite exited 0, 37/37 passed. | SURVIVED |
| M4 omit persisted `partial_effect.recovery_release`. | Adapter suite exited 1 with missing `recovery_release`. | KILLED |
| M5 persist reconciled receipt as `connected: true`. | Adapter suite exited 0, 37/37 passed. | SURVIVED |
| M6 omit reconciliation-path revoked-dispatch registration. | Adapter suite exited 0, 37/37 passed. | SURVIVED |
| M7 retry a foreign task instead of the original task. | Adapter suite exited 1 at `tools/test_orca_adapter.py:406`. | KILLED |

**Sensor:** lightweight, 7 mutations, 3 killed, 4 survived. FAIL.

### Code quality and contract integrity

- Production diff is surgical: one recovery helper plus one guarded call site; no unrelated
  abstraction or dependency was added.
- Assertions map to EXE-03/04/08/11 and SEC-005/008 at the adapter boundary, but four surviving
  behavior mutations make the new cases hollow for those exact outcomes under
  `docs/guidelines/TEST-CONTRACT.md:53-55`.
- Product style and existing adapter patterns are preserved. Scope failure is evidence quality,
  not an observed production-logic defect.

### Fingerprint accounting

- `daed6fc5e10de538fa15332810deb01973479f64eaa7e5ef4c2695b5c895f6c9` opened at
  failed-remediation count 1 for EXE-03/EXE-04/EXE-11/SEC-005/SEC-008.
- `e62a4e34b185bffdd09360d8ea603a47cf7007968bb19c3a7c5d93704c1c244c` opened at
  failed-remediation count 1 for EXE-08/EXE-11.
- Prior fingerprints remain closed at their historical counts.

### Ranked gaps

1. **Major / EXE-03, EXE-04, EXE-11, SEC-005, SEC-008.** Extend the canonical
   `tab_not_found` recovery case to assert the derived recovery request key and every persisted
   receipt field; add missing/mismatched post-show dispatch cases. The suite must fail if any
   correlation or receipt field is weakened.
2. **Major / EXE-08, EXE-11.** After accepted `tab_not_found` reconciliation, present a late
   delivery from the orphaned dispatch and assert stale rejection. The test must fail if the helper
   does not register that dispatch as revoked.

**Overall:** FAIL for `87f1bb5b55255beb84b66b1c7621041ff6695cd8`. Runtime behavior matches the
intended recovery path, and all gates are green, but evidence-or-zero rejects completion because
four safety mutations survive. Real Orca QA remains outside this technical packet.

## Orphaned Orca release reconciliation re-verification

**Date:** 2026-08-25  
**Diff range:** `87f1bb5b55255beb84b66b1c7621041ff6695cd8..f7930ff8c218ca466d0a971c6fffd97ce7576406`  
**Verifier:** independent Technical Verifier (author != verifier)  
**Verdict:** FAIL. Exact recovery key, complete persisted receipt, and reconciliation-path dispatch
revocation are now directly asserted and discriminating. Post-release `worker-show` dispatch
correlation remains undiscriminated: removing the comparison still leaves the adapter suite green.

### Spec-anchored outcomes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| EXE-03 / EXE-04 recovery key | Recovery and replay use `action_key + ":recovery-release"`; a foreign key is rejected. | Production derives and validates the key at `.agents/skills/autonomous/scripts/orca_adapter.py:730-749,758-765`; `tools/test_orca_adapter.py:430-442` asserts the exact persisted key and `:305-324` rejects a mismatched persisted receipt. Key mutation kills the suite. | PASS |
| EXE-04 / SEC-008 complete receipt | Persisted reconciled receipt proves exact dispatch, terminal, exited state, disconnected/non-writable state, and `tab_not_found` reason. | `.agents/skills/autonomous/scripts/orca_adapter.py:318-329,738-749`; exact receipt equality is `tools/test_orca_adapter.py:429-442`. Changing `connected` kills the suite. | PASS |
| EXE-08 / EXE-11 revocation | Accepted reconciliation revokes the orphaned dispatch; a late `worker_done` from it is stale. | Revocation is `.agents/skills/autonomous/scripts/orca_adapter.py:317`; `tools/test_orca_adapter.py:446-455` presents a late delivery and asserts stale rejection. Removing revocation kills the suite. | PASS |
| EXE-04 / EXE-11 / SEC-005 post-show dispatch correlation | The authoritative post-release show must name the same dispatch; missing or foreign dispatch remains `release_unknown` and causes zero retry. | Guard exists at `.agents/skills/autonomous/scripts/orca_adapter.py:291-316`, but adverse table `tools/test_orca_adapter.py:462-485` varies status, connection, writability, and terminal only. Removing line 305 leaves 37/37 tests green. | FAIL |

**Spec-anchored status:** 3 PASS, 1 FAIL, 0 spec-precision gaps.

### Gate evidence

- `python3 tools/test_orca_adapter.py` -> 37 passed, 0 failed; 0 skipped.
- `python3 tools/test_parallel_executor.py` -> 43 passed, 0 failed; 0 skipped.
- `npm run test:all` -> exit 0: 110 Vitest tests plus 185 Python tests, 295 passed,
  0 failed/skipped.
- Strict spec/tasks validators, AD index, incremental `git diff --check`, and Python compile -> exit 0.
- No real Orca command/state, product code, test, or retained `docs/qa/**` artifact was mutated.

### Discrimination sensor

One detached temporary worktree at `f7930ff8c218ca466d0a971c6fffd97ce7576406` received the four
prior surviving behavior faults and was removed. Retained-checkout porcelain returned to baseline
plus this report and convergence ledger.

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| M1 ignore post-release dispatch mismatch. | Adapter suite exited 0, 37/37 passed. | SURVIVED |
| M2 derive a foreign recovery idempotency key. | Adapter suite exited 1 because persisted key no longer correlated. | KILLED |
| M3 persist reconciled receipt as `connected: true`. | Adapter suite exited 1 at exact receipt equality. | KILLED |
| M4 omit reconciliation-path revoked-dispatch registration. | Adapter suite exited 1 at late-delivery stale assertion. | KILLED |

**Sensor:** lightweight, 4 mutations, 3 killed, 1 survived. FAIL.

### Fingerprint accounting

- `daed6fc5e10de538fa15332810deb01973479f64eaa7e5ef4c2695b5c895f6c9` remains OPEN at
  failed-remediation count 2. Same requirement/root cause/failure path: post-release dispatch
  identity is still not varied by the canonical adverse table.
- `e62a4e34b185bffdd09360d8ea603a47cf7007968bb19c3a7c5d93704c1c244c` is CLOSED at historical
  failed-remediation count 1. The production revocation path now owns a direct stale-delivery assertion.
- No fingerprint reached the three-failure halt threshold.

### Ranked gap

1. **Major / EXE-04, EXE-11, SEC-005.** Add missing and foreign `dispatch.id` variants to the
   post-`tab_not_found` authoritative `worker-show` table. Each must return `release_unknown`, make
   exactly `worker-show, worker-release, worker-show`, and issue zero worktree discovery or
   replacement `worker-start`. This assertion must kill removal of `actual_dispatch != dispatch_id`.

**Overall:** FAIL for `f7930ff8c218ca466d0a971c6fffd97ce7576406`. Three prior safety gaps are
closed; one same-fingerprint correlation gap remains at failed-remediation count 2. Real Orca QA
remains outside this technical packet.

## Orphaned Orca post-release dispatch correlation re-verification

**Date:** 2026-08-25  
**Diff range:** `f7930ff8c218ca466d0a971c6fffd97ce7576406..543d0a405cd27803e02f1aaf8bde1abe5731375f`  
**Verifier:** independent Technical Verifier (author != verifier)  
**Verdict:** PASS. Missing and foreign post-`tab_not_found` dispatch identities now remain
`release_unknown`, persist no recovery receipt, register no revocation, and issue no worktree
discovery or replacement retry. The valid matching `ctx` recovery path remains green.

### Spec-anchored outcomes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| EXE-04 / EXE-11 / SEC-005 missing dispatch | A post-release authoritative show without `dispatch.id` returns `release_unknown` and performs no later effect. | `tools/test_orca_adapter.py:462-496` includes `post_dispatch: None`, asserts exact `worker-show, worker-release, worker-show`, no `recovery_release`, and no revocation. | PASS |
| EXE-04 / EXE-11 / SEC-005 foreign dispatch | A post-release authoritative show naming another opaque dispatch follows the same fail-closed path. | `tools/test_orca_adapter.py:462-496` includes `post_dispatch: "ctx_foreign"` and the same zero-mutation assertions. | PASS |
| EXE-04 valid matching dispatch | Matching `ctx_5f619d0f6298` still persists the complete correlated receipt and retries the original task/dispatch once. | `tools/test_orca_adapter.py:413-457` asserts exact receipt, command order, retry ID, stale late-delivery rejection, and idempotent replay. | PASS |

**Spec-anchored status:** 3 PASS, 0 FAIL, 0 spec-precision gaps.

### Gate evidence

- `python3 tools/test_orca_adapter.py` -> 37 passed, 0 failed; 0 skipped.
- `python3 tools/test_parallel_executor.py` -> 43 passed, 0 failed; 0 skipped.
- `npm run test:all` -> exit 0: 110 Vitest tests plus 185 Python tests, 295 passed,
  0 failed/skipped.
- Strict spec/tasks validators, AD index, incremental `git diff --check`, and Python compile -> exit 0.
- No real Orca command/state, product code, test, or retained `docs/qa/**` artifact was mutated.

### Discrimination sensor

One detached temporary worktree at `543d0a405cd27803e02f1aaf8bde1abe5731375f` removed the
post-release `actual_dispatch != dispatch_id` guard. The adapter suite exited 1 when the new adverse
case proceeded toward unexpected worktree discovery instead of returning `release_unknown`.
Scratch removed; retained-checkout porcelain returned to baseline plus this report and ledger.

**Sensor:** lightweight, 1 mutation, 1 killed, 0 survived. PASS.

### Fingerprint accounting

- `daed6fc5e10de538fa15332810deb01973479f64eaa7e5ef4c2695b5c895f6c9` is CLOSED at historical
  failed-remediation count 2. This passing verification does not increment it to 3.
- `e62a4e34b185bffdd09360d8ea603a47cf7007968bb19c3a7c5d93704c1c244c` remains CLOSED at historical
  count 1.
- No R7 fingerprint is open or halted.

### Ranked gaps

None in this remediation scope.

**Overall:** PASS at `543d0a405cd27803e02f1aaf8bde1abe5731375f`. Exact orphaned-release
correlation, receipt persistence, revocation, stale-delivery rejection, retry identity, and replay
are now spec-correlated and discriminating. Real Orca QA remains outside this technical packet.

## Canonical Orca Effect Projection Re-verification

**Date:** 2026-08-25  
**Commit under test:** `2c80174f494954be3205922b853f59a0a7b3895c`  
**Base:** `a1a49a2a07954e46e30408496c4ba85ba79220b9`  
**Diff range:** `a1a49a2..2c80174f494954be3205922b853f59a0a7b3895c`  
**Verifier:** fresh independent Technical Verifier (author != verifier)  
**Current scoped verdict:** **FAIL**

This pass covers only the canonical Orca effect projection change in
`.agents/skills/autonomous/scripts/orca_adapter.py` and its directed adapter coverage. The
pre-existing `docs/qa/**` modifications in the checkout were preserved. No real Orca command,
product file, test file, or QA artifact was changed.

### Spec-anchored outcomes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| Outer IDs survive a nested `result` envelope | The outer envelope remains intact while canonical IDs are projected. | `tools/test_orca_adapter.py:245-282` asserts the original `result`, canonical IDs, `state`, and `lastError`; projection is `.agents/skills/autonomous/scripts/orca_adapter.py:235-274`. | PASS |
| All-nested and mixed camel/snake IDs project | `run_id`, `task_id`, `dispatch_id`, `terminal_handle`, and `request_id` resolve from nested containers and aliases. | `tools/test_orca_adapter.py:254-278`; recursive candidate collection is `.agents/skills/autonomous/scripts/orca_adapter.py:201-232`. | PASS |
| Equal aliases are accepted | Repeated equal aliases produce one canonical identity. | `tools/test_orca_adapter.py:267-278`; deduplication is `.agents/skills/autonomous/scripts/orca_adapter.py:239-260`. | PASS |
| Conflicting identity/request keys halt before effects | Conflicting run/task/dispatch/terminal/request/idempotency/retry keys raise `correlation_conflict`; adapter reconciliation performs no CLI call. | Direct conflict assertions: `tools/test_orca_adapter.py:285-302`; reconciliation projects before `worker-show` at `.agents/skills/autonomous/scripts/orca_adapter.py:772-808`. A separate two-case smoke check reported `conflict-before-effects: 2 passed, 0 failed` with zero recorded calls. | PASS |
| `error.result`, nested dispatch, and terminal forms normalize | Failure details retain the envelope and project nested run/task/dispatch/terminal IDs plus failure evidence. | `tools/test_orca_adapter.py:305-332` asserts nested failure details; nested retry coverage is `:182-225`; failure normalization is `.agents/skills/autonomous/scripts/orca_adapter.py:297-311`. | PASS |
| `mutation.requestId` and `state` evidence survive reconciliation | Canonical `request_id` and `state`, plus the nested mutation evidence, remain on the persisted partial effect. | `tools/test_orca_adapter.py:206-225` asserts `partial_effect.request_id`, `partial_effect.state`, and `result.mutation.requestId`; projection assertions are `:245-282`. | PASS |
| `lastError` and release evidence survive reconciliation | The normalized auxiliary evidence fields must remain in the persisted partial effect before retry/restart. | Copy list is `.agents/skills/autonomous/scripts/orca_adapter.py:785-791`, but no canonical assertion checks `partial_effect.lastError` or the release evidence fields. Removing `lastError` alone, or removing the release-evidence copy fields, leaves `40/40` adapter tests green. | **FAIL** |
| Missing Run/Task halts before effects | A partial effect without both run and task identity is rejected before recovery calls. | `tools/test_orca_adapter.py:333-346` asserts the error and `cli.calls == []`. | PASS |
| R8 `tab_not_found` success has one reconciled release and one retry of the same Run/Task/Dispatch | Post-check proves exited/disconnected/non-writable state, one release reconciliation, original task, original dispatch retry, and idempotent replay. | `tools/test_orca_adapter.py:537-581` asserts exact release evidence, command sequence, retry dispatch, and replay; post-check is `.agents/skills/autonomous/scripts/orca_adapter.py:362-404`. | PASS |
| R8 live/mismatch safety | Live, unknown, terminal-mismatch, missing-dispatch, and foreign-dispatch post-checks return `release_unknown` with no retry/release receipt. | `tools/test_orca_adapter.py:586-620` asserts exact three-call sequence, no `recovery_release`, and no revocation. | PASS |
| Replay is idempotent | A reconciled worker action returns the cached receipt without another Orca effect. | `tools/test_orca_adapter.py:218-225` and `:580-581`; cache is `.agents/skills/autonomous/scripts/orca_adapter.py:779-782`. | PASS |

**Spec-anchored status:** 10 PASS, 1 FAIL, 0 additional spec-precision gaps.

### Gate evidence

- `rtk python3 tools/test_orca_adapter.py` -> exit 0, **40 passed, 0 failed**.
- `rtk python3 tools/test_parallel_executor.py` -> exit 0, **43 passed, 0 failed**.
- `rtk env npm_config_offline=true npm run test:all` -> exit 0, **110 Vitest tests + 190 Python tests = 300 passed, 0 failed/skipped**.
- Full Python discovery covered all 12 `tools/test_*.py` suites; the scoped adapter and executor counts above are included in the 190 Python tests.
- `validate_spec.py --strict`, `validate_tasks.py --strict`, `validate_state.py parallel-slice-executor`, `tools/ad-index.py --check`, target-range `git diff --check`, and Python compile -> exit 0.
- The state validator's historical top-level PASS remains green; this appended current-head section is FAIL because the discrimination sensor found a surviving evidence mutation.

### Discrimination sensor

Eight behavior mutations ran in two detached temporary worktrees (`/tmp/orca-projection-sensor.RIkgEM`
and `/tmp/orca-projection-sensor2.RdHYyz`), then both worktrees were removed. The real checkout's
porcelain matched its pre-sensor baseline (the pre-existing `docs/qa/**` changes) before the allowed
review-ledger edit.

| Mutation | Behavior fault | Directed result | Outcome |
| --- | --- | --- | --- |
| M1 | Replace the outer projection with `result`, dropping the outer envelope. | Adapter suite failed at `tools/test_orca_adapter.py:280` because `result` disappeared. | KILLED |
| M2 | Accept two conflicting canonical identity candidates by changing the conflict threshold. | Adapter suite failed at `tools/test_orca_adapter.py:302`. | KILLED |
| M3 | Remove the camel-case `requestId` alias. | Adapter suite failed at `tools/test_orca_adapter.py:278`. | KILLED |
| M4 | Persist an empty `recovery_release` after the R8 reconciliation. | Adapter suite failed at `tools/test_orca_adapter.py:554`. | KILLED |
| M5 | Bypass the cached reconciled-worker return so replay calls Orca again. | Adapter suite failed at `tools/test_orca_adapter.py:224` on an unexpected second call. | KILLED |
| M6a | Remove only `lastError` from the normalized partial-effect copy list. | Adapter suite still passed **40/40**. | **SURVIVED** |
| M6b | Remove the release-evidence fields (`releaseState`, `releaseError`, `released`, `reconciled`, terminal status/connectivity, reason, and `release_error`) from that copy list. | Adapter suite still passed **40/40**. | **SURVIVED** |
| M7 | Ignore the authoritative post-release dispatch identity mismatch. | Adapter suite failed at `tools/test_orca_adapter.py:611` while the mismatched R8 case attempted a forbidden next effect. | KILLED |

**Sensor:** 8 injected, 6 killed, 2 survived. **FAIL**.

### Ranked gap and fix plan

1. **Major — EXE-04 / SEC-005.** Extend the canonical nested-effect/recovery test to assert every
   normalized auxiliary field that `reconcile_action` copies into `partial_effect`, at minimum
   `lastError`, `releaseState`, `releaseError`, `released`, `reconciled`, `terminal_status`,
   `connected`, `writable`, `reason`, and `release_error`. The tests must fail independently when
   either the `lastError` copy or release-evidence copy is removed. The immutable fingerprint is
   `ba7b951077322d54c5f2b6e0ed00939b3a89ad6763f1a916795387beefa7b1b5` at failed-remediation count 1.

**Overall:** **FAIL** for `2c80174f494954be3205922b853f59a0a7b3895c`. Runtime projection, conflict
handling, R8 reconciliation, live/mismatch safety, and replay behavior pass; the canonical test
contract does not yet prove preservation of `lastError` and release evidence. No code or tests were
modified by this verification.

## Canonical Orca Effect Projection Re-verification — Fingerprint Closed

**Date:** 2026-08-25  
**Commit under test:** `7edfaf5746413b54711b7da7c39c52d4583b5553`  
**Base:** `2c80174f494954be3205922b853f59a0a7b3895c`  
**Verifier:** fresh independent Technical Verifier (author != verifier)  
**Current scoped verdict:** **PASS**

The remediation adds canonical assertions for every persisted `lastError` and release-evidence
field at `tools/test_orca_adapter.py:577-601`, while the production copy list remains at
`.agents/skills/autonomous/scripts/orca_adapter.py:785-791`. The earlier fingerprint is now closed;
its failed-remediation count remains 1.

### Reverification outcomes

| Criterion | Evidence | Result |
| --- | --- | --- |
| Persisted `lastError` survives nested projection/reconciliation | `tools/test_orca_adapter.py:579-583` asserts the exact `lastError`; removing only the production copy entry causes the adapter suite to fail with `KeyError: 'lastError'` at `:583`. | PASS |
| Persisted release evidence survives nested projection/reconciliation | `tools/test_orca_adapter.py:579-590` asserts `releaseState`, `releaseError`, `released`, `reconciled`, terminal status/connectivity, reason, and `release_error`; removing that copy group causes `KeyError: 'releaseState'` at `:583`. | PASS |
| R8 `tab_not_found` flow remains green | `tools/test_orca_adapter.py:537-631` passes the exact reconciled release, one retry of the same task/dispatch, stale late-delivery rejection, and replay assertions. Direct R8 run: `1 passed, 0 failed`. | PASS |

### Gate evidence

- `rtk python3 tools/test_orca_adapter.py` -> exit 0, **40 passed, 0 failed**.
- `rtk python3 tools/test_parallel_executor.py` -> exit 0, **43 passed, 0 failed**.
- `rtk env npm_config_offline=true npm run test:all` -> exit 0, **110 Vitest + 190 Python = 300 passed, 0 failed/skipped**.
- Strict spec/tasks/state validators, AD index check, compile, and diff checks -> exit 0.
- `validate_state.py parallel-slice-executor` -> exit 0; the current-head PASS is recorded in this section.

### Discrimination sensor

Two detached scratch mutations ran at `/tmp/orca-projection-reverify.YOm7GP` and were removed;
the real checkout porcelain returned to its pre-sensor baseline.

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| Remove only persisted `lastError` copy | Adapter suite failed at the new exact-evidence assertion (`tools/test_orca_adapter.py:583`). | KILLED |
| Remove all persisted release-evidence copy fields | Adapter suite failed at the new `releaseState` assertion (`tools/test_orca_adapter.py:583`). | KILLED |

**Sensor:** 2 injected, 2 killed, 0 survived. **PASS**.

### Fingerprint accounting

- `ba7b951077322d54c5f2b6e0ed00939b3a89ad6763f1a916795387beefa7b1b5` is **CLOSED**, count **1**.
- No fingerprint reached the third-failure halt threshold.

**Overall:** **PASS** for `7edfaf5746413b54711b7da7c39c52d4583b5553`. No real Orca state,
product code, QA artifact, or test outside the committed remediation was touched; no commit, push,
or merge was performed.

## R9 retained-release evidence technical verification

**Date:** 2026-08-25  
**Commit under test:** `6975d4e610662c153105e1dac4f69ce0bcee839f`  
**Base:** `cb919c1`  
**Diff range:** `cb919c1..6975d4e610662c153105e1dac4f69ce0bcee839f`  
**Verifier:** fresh independent Technical Verifier (author != verifier)  
**Scoped verdict:** **PASS**

This verification covers the R9 retained-release behavior in the Orca adapter and coordinator
fallback. It did not run real Orca, mutate product files, alter tests, or touch the pre-existing
`docs/qa/**` checkout changes. No release, cleanup, retry, or acknowledgment was sent to a real
provider.

### Spec-anchored outcomes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| R9 retained release | A correlated `released: false`, `releaseState: retained`, `retainedReason: identity_unproven` response remains blocked while preserving exact release evidence and a stable error. | `.agents/skills/autonomous/scripts/orca_adapter.py:896-930` stores the correlated failure; `tools/test_orca_adapter.py:737-766` asserts the exact retained/ownership/reason/error/timestamp/Run identity fields and `release_identity_unproven`. | PASS |
| R9 replay safety | Replaying the retained release returns the same stable error with an idempotent marker and makes no new release, retry, cleanup, or revocation effect. | `tools/test_orca_adapter.py:769-778` asserts one `worker-release`, stable error, one CLI call, and no revoked dispatch; `:822-840` asserts reconcile stops after `worker-show, worker-release` with no `show` or `worker-start`. | PASS |
| Coordinator persistence/fallback | Retained evidence is persisted into the pending worker action, selects named `worker-failed` serial fallback, and restart does not recreate the worker or worktree. | `tools/test_parallel_executor.py:330-376` asserts all evidence fields on both attempts, one start attempt, one reconcile attempt, zero worker effects, and one worktree effect. | PASS |
| Explicit completed receipt | A correlated `releaseState: completed` receipt is accepted as released; full reconciliation permits exactly one same-Run/Task retry and replay is idempotent. | `tools/test_orca_adapter.py:783-794` supplies nested dispatch/terminal identity, asserts `released == True`, matching dispatch, one call, and idempotent replay; the ephemeral completed-reconcile probe exercised `worker-show, worker-release, show, worker-start`, exact `--retry-of`, and zero replay calls. | PASS |
| Conflict/missing ownership or origin | Conflicting identities, missing Run/Task/Dispatch/terminal ownership, malformed persisted identity, and foreign source identity halt before mutation. | `tools/test_orca_adapter.py:230-242,285-302,305-346,453-467,680-714,799-817,1087-1121` asserts correlation errors, zero calls, and no release/retry; the independent sensor also killed dispatch-correlation bypass. | PASS |
| Fully proven `tab_not_found` path | Only an exited, disconnected, non-writable correlated terminal is reconciled; exactly one release reconciliation and one same-Run/Task retry occur, late delivery is stale, and replay adds no call. | `tools/test_orca_adapter.py:537-631` asserts complete evidence, exact five-call order, same `--retry-of`, stale-delivery rejection, and six-call total after replay. | PASS |

**Spec-anchored status:** 6 PASS, 0 FAIL, 0 spec-precision gaps.

### Gate evidence

- `rtk python3 tools/test_orca_adapter.py` -> exit 0, **44 passed, 0 failed**.
- `rtk python3 tools/test_parallel_executor.py` -> exit 0, **44 passed, 0 failed**.
- Ephemeral completed-reconcile probe -> **1 release, 1 retry, 0 additional replay calls**.
- Scoped test delta from `cb919c1`: adapter **40 -> 44** (+4); executor **43 -> 44** (+1).
- `rtk env npm_config_offline=true npm run test:all` -> exit 0, **110 Vitest tests** and all
  discovered Python suites passed; the named Python count command reported **195**, with 0 failed
  or skipped.
- Strict spec/tasks validators, `tools/ad-index.py --check`, `validate_state.py
  parallel-slice-executor`, Python compile, and `git diff --check cb919c1 6975d4e` -> exit 0.

### Discrimination sensor

Four behavior mutations ran one at a time in detached scratch worktree `.r9-release-sensor` at the
target commit. The scratch was removed after each run. Real-checkout porcelain matched the
pre-sensor baseline, which consists only of the pre-existing QA edits/untracked artifacts.

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| Remove the post-release `actual_dispatch != dispatch_id` guard (unsafe promotion). | Adapter suite failed in `test_release_identity_missing_or_foreign_blocks_without_revocation` at `tools/test_orca_adapter.py:813`; a foreign/missing identity was promoted to retained failure. | KILLED |
| Drop the response envelope from retained failure details (evidence loss). | Adapter suite failed at `tools/test_orca_adapter.py:765` with missing `state`. | KILLED |
| Disable the retained-failure replay cache (duplicate release). | Adapter suite failed at `tools/test_orca_adapter.py:771` on an unexpected second `worker-release`. | KILLED |
| Remove `releaseState in {released, completed}` acceptance (completed-path regression). | Adapter suite failed at `tools/test_orca_adapter.py:791` with `release_identity_unproven` instead of accepting the correlated completed receipt. | KILLED |

**Sensor:** lightweight, 4 injected, 4 killed, 0 survived. **PASS**.

### Fingerprint accounting

No new blocker or surviving mutant was found. Existing fingerprints remain closed at their recorded
counts; no `review-fingerprints.json` update is required.

**Overall:** **PASS** for `6975d4e610662c153105e1dac4f69ce0bcee839f`. Real Orca QA remains outside
this technical verification; only this validation report changed in the checkout. No commit, push,
merge, product/test change, or `docs/qa/**` evidence change was performed.

## R10 retained-release envelope technical verification

**Date:** 2026-08-25  
**Commit under test:** `cd27409ca010fe7fa5296506ce596e1d05aa9b67`  
**Base:** `bf1c8f2`  
**Diff range:** `bf1c8f2..cd27409ca010fe7fa5296506ce596e1d05aa9b67`  
**Verifier:** fresh independent Technical Verifier (author != verifier)  
**Scoped verdict:** **PASS**

This verification covers the R10 retained-release envelope and restart boundary only. No real Orca
command ran. No product, QA, evidence, or test file outside the committed R10 change was modified.
The existing dirty `docs/qa/**` paths were preserved byte-for-byte.

### Spec-anchored outcomes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| Nested/camel/snake retained envelope promotion | A correlated retained release whose identity-unproven evidence is nested or aliased returns stable `release_identity_unproven`, not the provider's generic failure. | `.agents/skills/autonomous/scripts/orca_adapter.py:248-298,364-380,928-970` canonicalizes nested aliases and normalizes the worker-release failure; `tools/test_orca_adapter.py:783-824` asserts the stable code, provider code, retained state/reason, and correlated IDs. Read-only probes also returned the stable code for nested camel, nested snake, and outer state-alias envelopes. | PASS |
| Retained evidence preservation | The failure retains `tab_not_found`, mutation, archive, request, ownership, and release-state/error evidence. | `tools/test_orca_adapter.py:817-827` asserts `lastError`/`releaseError`=`tab_not_found`, request ID, ownership, state/reason, nested mutation/archive, and `processAction`; `:758-766` retains release timestamps and resource ownership evidence. | PASS |
| Executor fallback persistence | Adapter failure details are copied into the pending worker action and public serial fallback before the state is saved. | `.agents/skills/autonomous/scripts/parallel_execute.py:1432-1457` merges `AdapterError.details` into `partial_effect` before `_save`; `tools/test_parallel_executor.py:330-376` asserts every retained field on first fallback and restart, one start/reconcile attempt, one worktree effect, and no worker effect. | PASS |
| Read-only replay | Replaying persisted retained evidence returns the same stable error and performs only authoritative `worker-show`; it emits no new release, retry, cleanup, or revocation effect. | `tools/test_orca_adapter.py:830-839` asserts one release call, stable idempotent error, and no revoked dispatch; `:906-915` asserts restart replay returns the stable idempotent error after `worker-show` only, with no `worker-release`, `show`, or `worker-start`. | PASS |
| Other non-accepted reasons stay distinct | A retained response without `identity_unproven` keeps its provider/generic rejection code rather than being promoted to the R10 code. | `.agents/skills/autonomous/scripts/orca_adapter.py:954-970` gates promotion on `_is_identity_unproven_release` or the explicit `identity_unproven` code; read-only probes returned `other_reason` and `release_not_accepted` unchanged, each with one `worker-release` call. | PASS |
| Completed path unchanged | Correlated `releaseState: completed` remains accepted and idempotent. | `tools/test_orca_adapter.py:844-857` asserts `released is True`, the expected dispatch, one provider call, and idempotent replay. | PASS |

**Spec-anchored status:** 6 PASS, 0 FAIL, 0 spec-precision gaps for the scoped R10 contract.

### Gate evidence

- `rtk python3 tools/test_orca_adapter.py` -> exit 0, **45 passed, 0 failed**.
- `rtk python3 tools/test_parallel_executor.py` -> exit 0, **44 passed, 0 failed**.
- Parent comparison at `bf1c8f2`: adapter **44 -> 45** (+1); executor **44 -> 44** (+0).
- `rtk env npm_config_offline=true npm run test:all` -> exit 0, **110 Vitest + 195 Python = 305 passed, 0 failed/skipped**.
- Strict spec/tasks validators, `rtk python3 tools/ad-index.py --check`, Python compile, and `git diff --check bf1c8f2 cd27409ca010fe7fa5296506ce596e1d05aa9b67` -> exit 0.

### Discrimination sensor

Five detached scratch worktrees were created under `/tmp/r10-sensor-*`, mutated independently, run,
and removed. The real checkout porcelain hash before and after the sensor was
`561d12300a298de04ba18cb093902c48c5c5ab76db65134802d4c79c89b2de89`.

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| Remove the nested snake `ownership_state` alias used by retained envelope promotion. | Adapter suite failed at `tools/test_orca_adapter.py:824` with missing `ownershipState`. | KILLED |
| Replace the normalized `release_identity_unproven` code with `release_not_accepted`. | Adapter suite failed at `tools/test_orca_adapter.py:815`. | KILLED |
| Drop nested `result` evidence during failure projection. | Adapter suite failed at `tools/test_orca_adapter.py:331` because `result` disappeared. | KILLED |
| Stop merging adapter details at the executor fallback boundary. | Executor suite failed at `tools/test_parallel_executor.py:363` with missing `dispatch_id`. | KILLED |
| Bypass the persisted retained check during reconciliation. | Adapter suite attempted an unexpected second `worker-release` during replay and failed at `tools/test_orca_adapter.py:33`. | KILLED |

**Sensor:** targeted, 5 injected, 5 killed, 0 survived. **PASS**.

### Fingerprint accounting

No new blocker or surviving mutant was found. Existing fingerprints remain closed at their recorded
counts; `review-fingerprints.json` was not changed. No fingerprint reached the third-failure halt
threshold.

**Overall:** **PASS** for `cd27409ca010fe7fa5296506ce596e1d05aa9b67`. The exact R10 retained release
envelope is normalized, persisted, and replay-safe; completed releases and other rejection reasons
remain distinct. No commit, push, merge, real Orca action, product/test edit, or `docs/qa/**` edit
was performed.

## R13 Contextual Worktree Receipt Technical Verification

**Date:** 2026-08-25
**Commit under test:** `1e4017124e369deacc59d09e29580b659dde1ffe`
**Base:** `15cd385cbac0ceed3eaccfebacde41bbfe650ca2`
**Diff range:** `15cd385..1e4017124e369deacc59d09e29580b659dde1ffe`
**Verifier:** fresh independent Technical Verifier (author != verifier)
**Scoped verdict:** **PASS**

This pass covers only contextual Orca worktree receipt projection and the exact worker-start
boundary. No real Orca command ran. No product file, product test, or `docs/qa/**` evidence file
was changed. The pre-existing dirty `docs/qa/**` paths were preserved.

### Spec-anchored outcomes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| Nested worktree identity and path | `result.worktree.id` and `result.worktree.path` project to canonical `worktree_id` and `worktree_path`; an outer request UUID remains evidence only. | `.agents/skills/autonomous/scripts/orca_adapter.py:236-259,265-321` scopes `id` to the named `worktree` container and projects path; `tools/test_orca_adapter.py:515-524` drives nested receipts; the read-only projection probe asserted `worktree_id == "wt-real"` and `worktree_id != "request-uuid"`. | PASS |
| Camel aliases and Git fallback | `worktreeId`/`worktreePath` and nested `worktree.git.path` are accepted as equivalent contextual fields. | `.agents/skills/autonomous/scripts/orca_adapter.py:160,210,238-257`; `tools/test_orca_adapter.py:515-524`; the positive receipt matrix exercised nested, camel, and `git.path` forms, each with one `show` and one `worker-start`. | PASS |
| Equal aliases | Equal outer and nested path/ID aliases are accepted without a false conflict. | `.agents/skills/autonomous/scripts/orca_adapter.py:269-292,307-314` deduplicates equal identities and rejects only divergent values; the read-only equal-alias adapter case completed with one worker start. | PASS |
| Missing, malformed, and mismatched paths | Missing path, relative path, or a foreign absolute path halts before worker start; the selector remains absolute and exact. | `.agents/skills/autonomous/scripts/orca_adapter.py:493-522` requires `path:<recorded absolute path>`, rejects non-absolute values, and compares resolved equality; `tools/test_orca_adapter.py:449-505,529-554` asserts timeout/malformed/mismatch failure and zero worker starts. | PASS |
| Path and ID conflicts | Divergent contextual path or worktree IDs fail closed with `correlation_conflict` before downstream effects. | `.agents/skills/autonomous/scripts/orca_adapter.py:269-285,307-314`; `tools/test_orca_adapter.py:529-554` asserts conflict code and no `worker-start`; the negative matrix covered both conflicts. | PASS |
| Blank branch/head | Empty branch and head fields in a valid contextual receipt do not block discovery or worker attachment. | `tools/test_orca_adapter.py:515-524` supplies `branch: ""` and `head: ""` in the nested receipt and asserts successful attachment. | PASS |
| Watchdog and ordering | Selector-not-found retry remains bounded; worker start occurs once only after successful exact-path correlation. | `.agents/skills/autonomous/scripts/orca_adapter.py:501-533,720-735`; `tools/test_orca_adapter.py:433-479,510-524` asserts 5-attempt/1-second watchdog, two-show retry, and one worker start; direct watchdog probe passed. | PASS |

**Spec-anchored status:** 7 PASS, 0 FAIL, 0 spec-precision gaps for the R13 scope.

### Gate evidence

- `rtk proxy python3 tools/test_orca_adapter.py` -> exit 0, **51 passed, 0 failed**; 0 skipped.
- `rtk proxy python3 tools/test_parallel_executor.py` -> exit 0, **44 passed, 0 failed**; 0 skipped.
- `rtk env npm_config_offline=true npm run test:all` -> exit 0, **110 Vitest + 202 Python = 312 passed**, 0 failed/skipped.
- Strict spec validator -> exit 0, 0 errors, 0 warnings.
- Strict tasks validator -> exit 0, 0 errors, 0 warnings.
- `rtk python3 .agents/skills/tlc-spec-driven/scripts/validate_state.py parallel-slice-executor` -> exit 0, 0 errors.
- `rtk python3 tools/ad-index.py --check` -> exit 0, `AD-INDEX.md up to date`.
- Python compile for changed adapter/test and owning executor files -> exit 0.
- `rtk git diff --check 15cd385..1e4017124e369deacc59d09e29580b659dde1ffe` -> exit 0, no whitespace errors.

### Discrimination sensor

The real checkout baseline was the pre-existing `docs/qa/**` modification/untracked set. Five
detached scratch worktrees were created under `/tmp/r13-sensor-*`, mutated one at a time, tested,
and removed. The real-checkout porcelain and HEAD matched the baseline afterward; no scratch
worktree remains.

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| Prefer outer generic `id` as `worktree_id`, allowing a request UUID to replace contextual identity. | The isolated projection assertion failed with `conflicting Orca worktree_id`; nested `wt-real` could not be confused with `request-uuid`. | KILLED |
| Omit nested `result.worktree.path` projection. | Adapter suite failed at `tools/test_orca_adapter.py:521` with `malformed Orca worktree discovery`. | KILLED |
| Relax path-conflict threshold so two divergent aliases pass. | Adapter suite failed at `tools/test_orca_adapter.py:543` on an unexpected `worker-start`. | KILLED |
| Remove nested `worktree.git.path` fallback. | Adapter suite failed at `tools/test_orca_adapter.py:521` with `malformed Orca worktree discovery`. | KILLED |
| Bypass `_discover_worktree` before `worker-start`. | Adapter suite failed at `tools/test_orca_adapter.py:1141` with `invalid Orca dispatch id`, proving the discovery response was consumed as a worker response. | KILLED |

**Sensor:** targeted R13 receipt/order sensor, 5 injected, 5 killed, 0 survived. **PASS**.

### Fingerprint accounting

No new blocker, spec gap, or surviving mutant was found. Existing fingerprints remain closed at
their recorded counts; `.specs/features/parallel-slice-executor/review-fingerprints.json` was not
changed. No fingerprint reached the third-failure halt threshold.

### Summary

**Overall:** **PASS** for `1e4017124e369deacc59d09e29580b659dde1ffe`. Contextual nested/camel/Git
worktree receipts, exact absolute selectors, equal-alias acceptance, fail-closed conflict and
malformed handling, bounded watchdog behavior, and single-shot post-correlation worker start are
evidenced. No commit, push, merge, real Orca action, product/test edit, or `docs/qa/**` edit was
performed.

## R11 Run/Task identity technical verification

**Date:** 2026-08-25
**Commit under test:** `f02b679fcdda0de40e6190bc37d36604363560d1`
**Base:** `9493f9a`
**Diff range:** `9493f9a..f02b679fcdda0de40e6190bc37d36604363560d1`
**Verifier:** fresh independent Technical Verifier (author != verifier)
**Scoped verdict:** **PASS**

This pass covers only the R11 Orca Run/Task identity correlation change in
`.agents/skills/autonomous/scripts/orca_adapter.py` and its directed adapter assertions. The
pre-existing `docs/qa/**` modifications in the checkout were preserved. No real Orca command,
product file, test file, or QA artifact was changed.

### Spec-anchored outcomes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| Exact R11 create envelopes | Outer operation/request IDs remain evidence only; the nested `result.run.id` and `result.task.id` are the selected identities, with exact objective/spec/Run ownership. | `tools/test_orca_adapter.py:76-84` supplies `id`/`requestId` envelopes with nested Run/Task records; `:112-131` asserts the correlated receipt fields and lifecycle. | PASS |
| Generic operation/request IDs never become Run or Task identity | Generic `id`/`requestId` values are ignored when scoped IDs exist; worker-start receives the scoped Task ID. | `tools/test_orca_adapter.py:136-155` asserts `run_658585e3a862`, `task_78fcfca161b8`, and `--task == task_78fcfca161b8 != operation-task`; selection is `.agents/skills/autonomous/scripts/orca_adapter.py:299-310,658-670`. | PASS |
| Only canonical scoped Run/Task forms are accepted | Accepted forms are `run_id`, `runId`, `run.id` and `task_id`, `taskId`, `task.id`; generic outer `id` is not a fallback. | `.agents/skills/autonomous/scripts/orca_adapter.py:299-310` limits scoped lookup to field aliases or the named container's `id`; the fresh ephemeral alias matrix exercised all three Run/Task forms and passed 3/3. | PASS |
| Missing Run/Task identity halts before downstream effects | A response with only generic/request identity raises before worktree discovery or worker-start; the same holds for Task creation. | `tools/test_orca_adapter.py:160-186` asserts generic-only Run/Task failures and exact call prefixes ending at `run-create`/`task-create`, with no `show` or `worker-start`. | PASS |
| Conflicting canonical IDs halt before downstream effects | Conflicting scoped aliases raise `correlation_conflict` and do not reach worktree/worker effects. | `tools/test_orca_adapter.py:189-215` asserts `details["code"] == "correlation_conflict"` and exact call prefixes; conflict detection is `.agents/skills/autonomous/scripts/orca_adapter.py:242-263`. | PASS |
| Selected Run objective is exact | Run-create accepts only the exact `parallel-slice:<feature>:<key>` objective; wrong objective stops before Task lookup. | `.agents/skills/autonomous/scripts/orca_adapter.py:507-516` compares the response objective exactly; fresh ephemeral negative probe asserted wrong objective stops after `run-create` (no `task-list`). | PASS |
| Task spec and Run ownership are exact | Task-create accepts only the exact spec and either the absent or exact current Run ID; wrong spec/foreign Run stops before worktree discovery. | `.agents/skills/autonomous/scripts/orca_adapter.py:534-548` checks Run and spec; fresh ephemeral probes asserted wrong spec and foreign Run stop after `task-create` (no `show`/worker-start). | PASS |
| Worker-start receives the exact canonical Task | The argv `--task` value is the selected scoped Task identity, never an operation/request UUID. | `tools/test_orca_adapter.py:151-155` asserts the exact `--task` argument; production argv construction is `.agents/skills/autonomous/scripts/orca_adapter.py:658-664`. | PASS |

**Spec-anchored status:** 8 PASS, 0 FAIL, 0 spec-precision gaps for the R11 scope.

### Test contract disposition

| Case | Contracted outcome | Evidence | Result |
| --- | --- | --- | --- |
| R11 positive envelope | Nested canonical Run/Task identities survive operation/request envelopes and drive the worker. | `tools/test_orca_adapter.py:136-155`; `python3 tools/test_orca_adapter.py` -> 48 passed. | PASS |
| R11 canonical-only negatives | Generic-only, missing, and conflicting scoped identities reject before downstream effects. | `tools/test_orca_adapter.py:160-215`; fresh alias/negative matrix -> 10/10 probes passed. | PASS |
| Objective/spec/ownership negatives | Wrong Run objective, wrong Task spec, and foreign Task Run are rejected before worktree/worker effects. | Fresh ephemeral probes asserted exact call prefixes; source checks at `.agents/skills/autonomous/scripts/orca_adapter.py:507-548`. | PASS |

### Gate evidence

- `rtk python3 tools/test_orca_adapter.py` -> exit 0, **48 passed, 0 failed**; 0 skipped.
- `rtk python3 tools/test_parallel_executor.py` -> exit 0, **44 passed, 0 failed**; 0 skipped.
- `rtk env npm_config_offline=true npm run test:all` -> exit 0; **110 Vitest passed**, all discovered Python suites passed, and 0 failures/skips (the scoped adapter/executor counts above are included).
- `rtk python3 .agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-executor/spec.md --strict` -> exit 0, 0 errors, 0 warnings.
- `rtk python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-executor/tasks.md --strict` -> exit 0, 0 errors, 0 warnings.
- `rtk python3 tools/ad-index.py --check` -> exit 0, `AD-INDEX.md up to date`.
- `rtk python3 -m py_compile .agents/skills/autonomous/scripts/orca_adapter.py tools/test_orca_adapter.py .agents/skills/autonomous/scripts/parallel_execute.py tools/test_parallel_executor.py` -> exit 0.
- `rtk git diff --check f02b679^ f02b679` -> exit 0, no whitespace errors.

### Discrimination sensor

The real checkout baseline was the pre-existing QA-only porcelain listed above. Five behavior
mutations ran in separate detached temporary worktrees and were removed; the real checkout
porcelain matched the baseline afterward. The two ephemeral negative probes were verifier-only
stdin harnesses and were not added to the product test tree.

| Mutation | Behavior fault | Directed result | Outcome |
| --- | --- | --- | --- |
| M1 | Prefer outer generic `id` in `_scoped_identifier`, allowing an operation UUID to replace a scoped Run/Task ID. | Adapter suite exited 1 with `uncorrelated Orca task receipt` during the clean-waiter path; the generic-ID contract could no longer complete. | KILLED |
| M2 | Raise only when more than two canonical identity candidates conflict. | Adapter suite exited 1 at `tools/test_orca_adapter.py:384` (`conflicting run_id must halt`). | KILLED |
| M3 | Remove the exact Run objective comparison. | Adapter suite remained green, but the fresh wrong-objective probe exited 1 on an unexpected downstream `task-list`; the mutant accepted the wrong Run and was detected before worker effects. | KILLED |
| M4 | Remove the exact Task spec comparison. | Adapter suite remained green, but the fresh wrong-spec probe exited 1 on an unexpected downstream `worktree show`; the mutant accepted the wrong Task spec. | KILLED |
| M5 | Replace worker-start `--task task_id` with the generic operation ID. | Adapter suite exited 1 at `tools/test_orca_adapter.py:154` on the exact `--task` assertion. | KILLED |

**Sensor:** targeted R11, 5 injected, 5 killed, 0 survived. **PASS**.

### Fingerprint accounting

No new blocker or surviving mutant was found. Existing fingerprints remain closed at their recorded
counts; `review-fingerprints.json` was not changed. No fingerprint reached the third-failure halt
threshold.

**Overall:** **PASS** for `f02b679fcdda0de40e6190bc37d36604363560d1` in the requested R11 scope. Generic
operation/request UUIDs cannot become Run/Task identities; scoped aliases, exact objective/spec/
ownership, conflict/missing rejection, and worker Task propagation are all evidenced. No commit,
push, merge, real Orca action, product/test edit, or `docs/qa/**` edit was performed.

## R12 bounded Orca worktree discovery technical verification

**Date:** 2026-08-25
**Commit under test:** `53e2d96de8e645418de72366967d89c9b4819fc4`
**Base:** `84ef849`
**Diff range:** `84ef849..53e2d96de8e645418de72366967d89c9b4819fc4`
**Verifier:** fresh independent Technical Verifier (author != verifier)
**Scoped verdict:** **PASS**

This pass covers only bounded exact-selector worktree discovery and its worker-start boundary.
No real Orca command ran. The existing dirty `docs/qa/**` paths were preserved byte-for-byte;
no product code, product tests, or QA/evidence files were changed.

### Spec-anchored outcomes

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| EXE-06 exact selector and path | Discovery uses the recorded exact worktree path before worker attachment. | `.agents/skills/autonomous/scripts/orca_adapter.py:465-488,676-693` builds `path:<recorded path>`, validates the resolved candidate, and calls worker-start only afterward; `tools/test_orca_adapter.py:112-123,433-444` asserts exact path, call order, two discovery shows after one selector miss, and one worker-start. | PASS |
| EXE-07 correlated worker receipt | A successful start returns correlated Run, Task, Dispatch, Terminal, worktree, branch, HEAD, and idempotency fields. | `tools/test_orca_adapter.py:124-131` asserts each returned identity/receipt field; `tools/test_orca_adapter.py:433-444` asserts the worker starts once only after exact discovery. | PASS |
| EXE-11 fail-closed discovery | Mismatch, malformed, permission/auth failure, or exhausted selector discovery halts without a replacement worker. | `.agents/skills/autonomous/scripts/orca_adapter.py:489-503` retries only `selector_not_found` and emits stage/attempts/elapsed/selector; `tools/test_orca_adapter.py:449-479,484-505` asserts fake-clock exhaustion, bounded sleep, immediate adverse failures, and zero worker-start. | PASS |
| SEC-005 correlated selector result | Only the expected worktree identity is accepted; foreign paths are rejected before effects. | `.agents/skills/autonomous/scripts/orca_adapter.py:479-487`; `tools/test_orca_adapter.py:484-505` supplies foreign, empty, and `permission_denied` responses and asserts exactly one `show`, no sleep, and no worker-start. | PASS |
| EXE-02/EXE-03 at-most-once effects | Replaying the same idempotency key does not recreate Run, Task, worktree discovery, or worker effects. | `.agents/skills/autonomous/scripts/orca_adapter.py:681-700` checks cached worker receipts before Run/Task/discovery/start; the isolated duplicate-effect stdin harness asserted one each of `run-create`, `task-create`, `show`, and `worker-start` on two calls. | PASS |

**Spec-anchored status:** 5/5 scoped criteria matched the specified outcome; 0 FAIL; 0
spec-precision gaps.

### Gate evidence

- `rtk python3 tools/test_orca_adapter.py` -> exit 0, **49 passed, 0 failed**.
- `rtk python3 tools/test_parallel_executor.py` -> exit 0, **44 passed, 0 failed**.
- `rtk env npm_config_offline=true npm run test:all` -> exit 0, **110 Vitest + 200 Python = 310 passed**, 0 failed/skipped.
- Strict spec validator -> exit 0, 0 errors, 0 warnings.
- Strict tasks validator -> exit 0, 0 errors, 0 warnings.
- `rtk python3 tools/ad-index.py --check` -> exit 0, `AD-INDEX.md up to date`.
- `rtk git diff --check 84ef849..53e2d96de8e645418de72366967d89c9b4819fc4` -> exit 0.
- Sensor scratch `git diff --exit-code` and real-tree porcelain comparison -> exit 0; baseline
  remained the pre-existing QA-only edits/untracked artifacts.

### Discrimination sensor

One detached scratch worktree was used for five sequential behavior mutations; each mutant was
reverted before the next, and the scratch was removed afterward. No real Orca command ran.

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| Bound `while True` to three attempts (unbounded-loop regression). | Adapter suite failed at `tools/test_orca_adapter.py:473` because exhaustion attempts changed from 5. | KILLED |
| Replace `delay = min(backoff, remaining)` with `delay = backoff` (sleep-past-deadline regression). | Adapter suite failed at `tools/test_orca_adapter.py:474` because fake-clock elapsed time exceeded the 1-second deadline. | KILLED |
| Retry every `AdapterError` instead of only `selector_not_found`. | Adapter suite failed at `tools/test_orca_adapter.py:498` on an unexpected second discovery call for mismatch/malformed/auth input. | KILLED |
| Bypass `_discover_worktree` before worker-start. | Adapter suite failed in the clean-waiter lifecycle with an invalid dispatch receipt because the discovery response was consumed as worker-start input. | KILLED |
| Disable the cached worker receipt branch. | Duplicate-effect stdin harness failed on an unexpected second `run-list`; the original harness passed with one each of Run/Task/show/worker-start effects. | KILLED |

**Sensor:** targeted fake-clock/idempotency sensor, 5 injected, 5 killed, 0 survived. **PASS**.

### Fingerprint accounting

No new blocker, spec gap, or surviving mutant. Existing fingerprints remain closed at their recorded
counts; `.specs/features/parallel-slice-executor/review-fingerprints.json` was not changed. No
fingerprint reached the third-failure halt threshold.

**Overall:** **PASS** for `53e2d96de8e645418de72366967d89c9b4819fc4`. Exact-selector discovery is
monotonic, bounded, fail-closed, structured on exhaustion, and worker-start is single-shot after
exact discovery. No commit, push, merge, real Orca action, product/test edit, or `docs/qa/**` edit
was performed.

## R14/R15 live failed-worker stop and retry technical verification

**Date:** 2026-08-25
**Commit under test:** `5b7a9ddc406a555a135075c08cbcc0b967ee254e`
**Base:** `0bdc73e`
**Diff range:** `0bdc73e..5b7a9dd`
**Verifier:** fresh independent Technical Verifier (author != verifier)
**Scoped verdict:** **FAIL**
Verdict: FAIL

This pass covers the live failed/revoked Orca worker recovery change in
`.agents/skills/autonomous/scripts/orca_adapter.py` and its directed adapter assertions. No real
Orca command ran. No product code, product tests, or `docs/qa/**` artifact was edited. The pre-existing
dirty/untracked `docs/qa/**` porcelain was preserved byte-for-byte.

### Spec-anchored outcomes

| Requested outcome | Evidence | Result |
| --- | --- | --- |
| Failed, exact owned/supervised/live terminal stops once with the deterministic request, proves the fence, releases, then retries the same task/dispatch | Recovery ordering is `.agents/skills/autonomous/scripts/orca_adapter.py:991-1051`; stop receipt/request and retry argv are asserted by `tools/test_orca_adapter.py:578-616`; the fresh matrix observed `worker-show, worker-stop, worker-show, worker-release, show, worker-start`, `--retry-request K:recovery-stop`, and `--retry-of ctx_probe_dispatch`. | PASS |
| Revoked, exact owned/supervised/live terminal follows the same stop/release/retry path | The fresh matrix drove `status=revoked` with matching ownership/origin and observed the same six-effect order and exact retry selector. | PASS |
| Stop intent is persisted before the effect and an accepted stop receipt is replayed with the same request | Pending/accepted recovery-stop persistence is at `.agents/skills/autonomous/scripts/orca_adapter.py:994-1017`; the directed restart case is `tools/test_orca_adapter.py:639-654`; the same request was observed on replay. | PASS |
| Post-stop show proves terminal `exited`, disconnected, and non-writable before release/retry | The post-stop guard checks dispatch identity, terminal handle, dispatch status, `connected=false`, and `writable=false` at `.agents/skills/autonomous/scripts/orca_adapter.py:1019-1031`, but never checks `stopped_state["status"] == "exited"`. A fresh probe supplied dispatch `stopped`, terminal `status=running`, `connected=false`, `writable=false`; the adapter unexpectedly completed release/retry with `worker-show, worker-stop, worker-show, worker-release, show, worker-start`. | **FAIL — fingerprint `9744e73f37a4c196fc4bc2a2ed3a937c85491120395cc9b6d9ec0793712d27f3`** |
| Running, ready, unknown, and outcome_unknown states perform no unsafe recovery effect | The existing running/unknown cases are `tools/test_orca_adapter.py:559-576,679-697`; the fresh matrix added `ready` and `outcome_unknown`. Each stopped after one `worker-show`; no stop/release/retry occurred. | PASS |
| user_owned, user_takeover, foreign, missing, mismatch, and unsupervised ownership/state perform no unsafe effect | `tools/test_orca_adapter.py:619-637,724-742` covers takeover/unsupervised and identity failures. Fresh probes for `user_owned`, `user_takeover`, `unsupervised`, foreign/missing owner/origin/resource, and terminal mismatch each stopped after `worker-show`. | PASS |
| Retained release state performs no stop/release/retry | The persisted retained guard is after the recovery-stop block at `.agents/skills/autonomous/scripts/orca_adapter.py:1038-1045`. Fresh probes with persisted `releaseState=retained, retainedReason=identity_unproven` and with a retained resource both attempted `worker-stop` after `worker-show`, violating the required zero-unsafe-effect outcome. | **FAIL — fingerprint `a5497630c1fc90729707f6f231d6d70774a045651cf444280ece5b8481fa96b5`** |
| Stop failure or unknown result blocks release and retry | `_stop_worker` records a failed stop and raises before release at `.agents/skills/autonomous/scripts/orca_adapter.py:1129-1150`; directed coverage is `tools/test_orca_adapter.py:659-677`; fresh failure/unknown probes observed only `worker-show, worker-stop`. | PASS |
| Release revokes the old dispatch and late `worker_done` is stale after retry/replay | Same-process stale rejection is asserted at `tools/test_orca_adapter.py:599-612`, and normal release registers revocation at `.agents/skills/autonomous/scripts/orca_adapter.py:1126`; however, a fresh adapter replay with the persisted accepted release did not restore `_revoked_dispatches`. A late `worker_done` reusing the old dispatch was unexpectedly accepted (`worker-show, show, worker-start, check`). | **FAIL — fingerprint `192f2dc513f263367b30600c500f83f82c61825d55d181b1f10f3ce893367230`** |

**Spec-anchored status:** 6 PASS, 3 FAIL, 0 spec-precision gaps for the requested stop/retry scope.

### Gate evidence

- `rtk proxy python3 tools/test_orca_adapter.py` -> exit 0, **55 passed, 0 failed**; base count was 51 and did not decrease.
- `rtk proxy python3 tools/test_parallel_executor.py` -> exit 0, **44 passed, 0 failed**.
- `rtk env npm_config_offline=true npm run test:all` -> exit 0; **110 Vitest passed**, all **12 discovered Python suites passed** (including adapter 55 and executor 44), 0 failures.
- `rtk proxy python3 .agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-executor/spec.md --strict` -> exit 0, 0 errors, 0 warnings.
- `rtk proxy python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-executor/tasks.md --strict` -> exit 0, 0 errors, 0 warnings.
- `rtk proxy python3 .agents/skills/tlc-spec-driven/scripts/validate_state.py parallel-slice-executor` -> exit 0, because this legacy validator selects the first historical `Verdict: PASS` in the append-only report and does not inspect the new scoped FAIL; the scoped verdict above remains authoritative for this pass.
- `rtk proxy python3 tools/ad-index.py --check` -> exit 0, `AD-INDEX.md up to date`.
- `rtk proxy python3 -m py_compile .agents/skills/autonomous/scripts/orca_adapter.py tools/test_orca_adapter.py .agents/skills/autonomous/scripts/parallel_execute.py tools/test_parallel_executor.py` -> exit 0.
- `rtk git diff --check 0bdc73e..5b7a9dd` -> exit 0.

The green gates do not override the three evidence-backed contract failures above.

### Discrimination sensor

Six detached scratch worktrees were created under `/tmp/r15-sensor-*`, mutated one behavior at a
time, tested, and removed. The real checkout porcelain remained exactly the pre-sensor baseline;
no scratch worktree remains.

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| Bypass exact ownership/origin guard | Fresh takeover probe observed `worker-stop`; expected zero unsafe effects. | KILLED |
| Add `running` to reclaimable states | Adapter suite failed in `test_running_stalled_dispatch_fails_safely_without_release_or_retry`. | KILLED |
| Substitute `:wrong-stop` for the derived retry request | Adapter suite failed on the exact persisted/requested retry key assertion. | KILLED |
| Bypass the post-stop identity/fence condition | Fresh mismatched-terminal probe observed `worker-release`; expected post-show halt. | KILLED |
| Accept `status=unknown` as a successful stop | Fresh stop-unknown probe reached a second post-stop show instead of halting at the stop result. | KILLED |
| Remove successful-release dispatch revocation | Adapter suite failed on late delivery stale rejection. | KILLED |

**Sensor:** 6 mutations injected, 6 killed, 0 survived. **PASS**. The three baseline probes listed
in the outcome table are separate unmet contracts, not sensor survivors.

### Fingerprint accounting

Three new open fingerprints were persisted in
`.specs/features/parallel-slice-executor/review-fingerprints.json`, each at
`failed_remediations=1` with `gate_passed=true`: retained-state stop ordering
(`a5497630c1fc90729707f6f231d6d70774a045651cf444280ece5b8481fa96b5`), missing post-stop terminal
status proof (`9744e73f37a4c196fc4bc2a2ed3a937c85491120395cc9b6d9ec0793712d27f3`), and stale replay
revocation (`192f2dc513f263367b30600c500f83f82c61825d55d181b1f10f3ce893367230`). No existing
fingerprint was changed or halted. Lessons state was not edited because the user restricted
verifier writes to `validation.md` and `review-fingerprints.json`.

### Summary

**Overall:** **FAIL** for `5b7a9ddc406a555a135075c08cbcc0b967ee254e`. The positive failed/revoked
owned-live stop path, exact retry key, stop/release ordering, unsafe-state rejection, and stop
failure handling are evidenced, but retained state can still trigger stop, post-stop terminal
status is under-validated, and a fresh replay can accept a late worker delivery. No commit, push,
merge, real Orca action, product/test edit, or `docs/qa/**` edit was performed.

## R16 fresh re-verification of live worker stop safety

**Date:** 2026-08-25
**Commit under test:** `48e53226b6647572aeac2670351c998b46c16848`
**Previous failing scope:** `5b7a9ddc406a555a135075c08cbcc0b967ee254e`
**Verifier:** fresh independent Technical Verifier (author != verifier)
**Scoped verdict:** **PASS**
Verdict: PASS

This pass re-verifies fingerprints `a5497630`, `9744e73f`, and `192f2dc5` after the recovery-stop
hardening. No real Orca command ran. No product code, product tests, or `docs/qa/**` artifact was
edited. Existing QA-only dirt was preserved.

### Exact fingerprint probes

| Fingerprint | Probe and evidence | Result |
| --- | --- | --- |
| `a5497630c1fc90729707f6f231d6d70774a045651cf444280ece5b8481fa96b5` | Live `failed`, exact owned/origin dispatch, plus persisted retained evidence or provider `releaseState=retained`; expected zero unsafe effects. The adapter now derives retained state/reason before stop at `.agents/skills/autonomous/scripts/orca_adapter.py:996-1017`; `tools/test_orca_adapter.py:647-668` asserts `release_identity_unproven` and calls exactly `worker-show`. | PASS |
| `9744e73f37a4c196fc4bc2a2ed3a937c85491120395cc9b6d9ec0793712d27f3` | Post-stop show returned the same dispatch, terminal handle, dispatch `stopped`, terminal `status=running`, `connected=false`, `writable=false`; expected halt before release/retry. The new `stopped_state["status"] == "exited"` guard is `.agents/skills/autonomous/scripts/orca_adapter.py:1048-1055`; `tools/test_orca_adapter.py:672-690` asserts `worker-show, worker-stop, worker-show` only. | PASS |
| `192f2dc513f263367b30600c500f83f82c61825d55d181b1f10f3ce893367230` | Fresh adapter replay consumed a persisted accepted recovery release, then received late `worker_done` for the reused old dispatch; expected stale rejection. Replay now restores revocation at `.agents/skills/autonomous/scripts/orca_adapter.py:986-987`; `tools/test_orca_adapter.py:578-623` asserts fresh-adapter stale rejection. | PASS |

Fresh probe output was: retained-persisted and retained-provider both
`release_identity_unproven`, calls `[worker-show]`; post-stop-running `recovery_stop_unproven`,
calls `[worker-show, worker-stop, worker-show]`; fresh-replay-late `stale Orca delivery from
revoked dispatch`.

### Directed and full gates

- `rtk proxy python3 tools/test_orca_adapter.py` -> exit 0, **57 passed, 0 failed**.
- `rtk proxy python3 tools/test_parallel_executor.py` -> exit 0, **44 passed, 0 failed**.
- `rtk env npm_config_offline=true npm run test:all` -> exit 0; **110 Vitest passed**, all 12 discovered Python suites passed, including adapter 57 and executor 44.
- Strict spec validator -> exit 0, 0 errors, 0 warnings.
- Strict tasks validator -> exit 0, 0 errors, 0 warnings.
- `rtk proxy python3 -m py_compile .agents/skills/autonomous/scripts/orca_adapter.py tools/test_orca_adapter.py .agents/skills/autonomous/scripts/parallel_execute.py tools/test_parallel_executor.py` -> exit 0.
- `rtk proxy python3 tools/ad-index.py --check` -> exit 0, `AD-INDEX.md up to date`.
- `rtk proxy git diff --check` -> exit 0.
- `rtk proxy python3 .agents/skills/tlc-spec-driven/scripts/validate_state.py parallel-slice-executor` -> exit 0.

### Discrimination sensor

Six detached scratch worktrees under `/tmp/r16-sensor-*` were mutated one at a time and removed;
the real checkout porcelain matched its pre-sensor baseline and no scratch worktree remains.

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| Disable retained-state pre-stop guard | Adapter suite failed in retained replay safety. | KILLED |
| Remove terminal `status=exited` post-stop check | Adapter suite failed in `test_r15_post_stop_running_terminal_blocks_before_release_or_retry`. | KILLED |
| Remove persisted replay revocation restoration | Adapter suite failed on fresh-adapter stale delivery. | KILLED |
| Bypass exact ownership/origin guard | Independent takeover probe observed `worker-stop`; expected only `worker-show`. | KILLED |
| Substitute the deterministic retry request key | Adapter suite failed on the exact `recovery-stop` request assertion. | KILLED |
| Add `running` to reclaimable states | Adapter suite failed in live stalled-dispatch safety. | KILLED |

**Sensor:** 6 mutations injected, 6 killed, 0 survived. **PASS**.

### Fingerprint disposition

The three repaired fingerprints are closed at `failed_remediations=1` in
`.specs/features/parallel-slice-executor/review-fingerprints.json`. No new fingerprints were
created, and no existing unrelated fingerprint changed.

### Summary

**Overall:** **PASS** for `48e53226b6647572aeac2670351c998b46c16848` in the requested recovery-stop
scope. Retained evidence blocks before stop, post-stop terminal exit is proven, persisted replay
restores dispatch revocation, all directed/full gates pass, and all six sensor mutants die. No
commit, push, merge, real Orca action, product/test edit, or `docs/qa/**` edit was performed.

## R17 contextual terminal-resource ownership technical verification

**Date:** 2026-08-25
**Commit under test:** `a7367570c19a9123d4d23e4081eaf82471783ba6`
**Base:** `6db749d`
**Diff range:** `6db749d..a7367570c19a9123d4d23e4081eaf82471783ba6`
**Verifier:** fresh independent Technical Verifier (author != verifier)
**Scoped verdict:** **PASS**

This pass covers only the terminal-resource projection and recovery changes in
`.agents/skills/autonomous/scripts/orca_adapter.py` plus their directed adapter assertions. No
real Orca command ran. The pre-existing dirty/untracked `docs/qa/**` paths were preserved byte-for-byte;
no product file or test file was changed. Only this validation report was updated.

### Spec-anchored outcomes

| Requested outcome | Evidence | Result |
| --- | --- | --- |
| Strict contextual `terminalResource` projection | `_resource_dispatch_identity` accepts only snake/camel owner/origin aliases and rejects conflicting values at `.agents/skills/autonomous/scripts/orca_adapter.py:168-183`; `_canonical_projection` projects owner/origin only from `_nested_resource` at `:297-359`. Fresh projection probes asserted terminal, worktree, resource, owner/origin, ownership, release, and retained fields while an outer generic `id` remained non-authoritative. | PASS |
| Equal aliases are accepted | `tools/test_orca_adapter.py:647-651` asserts equal camel/snake owner/origin aliases; the fresh matrix also asserted equal terminal/worktree/resource aliases. | PASS |
| Conflicting or missing identity fails before stop | `tools/test_orca_adapter.py:652-676` asserts owner/origin alias conflicts and missing owner/origin with calls limited to `worker-show`; fresh probes extended this to terminal/worktree/resource alias conflicts. | PASS |
| Exact R16 owned resource reaches one stop, release, and retry | `tools/test_orca_adapter.py:627-642` asserts `worker-show, worker-stop, worker-show, worker-release, show, worker-start` and projected owner/origin/resource evidence. Fresh probe additionally asserted one count for each destructive/retry effect and same-instance replay with no new calls. | PASS |
| R14 user-owned/takeover and retained/identity-unproven states have zero unsafe effects | Ownership guard is `.agents/skills/autonomous/scripts/orca_adapter.py:1200-1218`; takeover/foreign zero-effect assertions are `tools/test_orca_adapter.py:678-695`, and retained persisted/provider evidence is `:698-720`. Fresh probes added `user_owned`, missing owner/origin, and both retained sources; each observed only `worker-show`. | PASS |
| Recovery replay is idempotent | Accepted release restores dispatch revocation at `.agents/skills/autonomous/scripts/orca_adapter.py:1001-1022`; fresh-adapter replay coverage is `tools/test_orca_adapter.py:578-623`, and verifier replay asserted no duplicate stop/release and one retry. | PASS |

**Spec-anchored status:** 6/6 requested outcomes matched; 0 FAIL; 0 spec-precision gaps.

### Directed and full gates

- `rtk python3 tools/test_orca_adapter.py` -> exit 0, **59 passed, 0 failed**; base adapter count was 57, so this commit adds 2 directed cases.
- `rtk python3 tools/test_parallel_executor.py` -> exit 0, **44 passed, 0 failed**.
- Verifier-only stdin matrix -> exit 0, **17 scenarios passed** (4 projection, 5 alias conflicts, 1 owned R16 recovery, 6 R14 zero-effect, 1 replay).
- `rtk env npm_config_offline=true npm run test:all` -> exit 0; **110 Vitest passed**, all **12 discovered Python suites passed**, including adapter 59 and executor 44; 0 failures/skips.
- `rtk python3 .agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-executor/spec.md --strict` -> exit 0, 0 errors, 0 warnings.
- `rtk python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-executor/tasks.md --strict` -> exit 0, 0 errors, 0 warnings.
- `rtk python3 .agents/skills/tlc-spec-driven/scripts/validate_state.py parallel-slice-executor` -> exit 0, 0 errors.
- `rtk python3 tools/ad-index.py --check` -> exit 0, `AD-INDEX.md up to date`.
- `rtk python3 -m py_compile .agents/skills/autonomous/scripts/orca_adapter.py tools/test_orca_adapter.py .agents/skills/autonomous/scripts/parallel_execute.py tools/test_parallel_executor.py` -> exit 0.
- `rtk git diff --check 6db749d..a7367570c19a9123d4d23e4081eaf82471783ba6` -> exit 0.

### Discrimination sensor

Five detached scratch worktrees under `/tmp/r17-sensor-*` were mutated one at a time and removed.
Real-tree porcelain before and after matched the pre-existing QA-only baseline; no scratch
worktree remains.

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| Remove camel owner/origin alias support from `_resource_dispatch_identity`. | Adapter suite failed in `test_r16_camel_terminal_resource_owner_origin_and_terminal_aliases_drive_stop` before `worker-stop`. | KILLED |
| Suppress terminal-resource alias conflict rejection. | Adapter suite failed in `test_r16_terminal_resource_aliases_equal_or_conflicting_and_missing_owner`. | KILLED |
| Fall back to outer generic `id` for scoped Run/Task identity. | Canonical adapter suite stayed green, but the fresh outer-generic-ID probe observed downstream `task-list`, `show`, and `worker-start` instead of halting after `run-create`; probe assertion failed. | KILLED |
| Bypass exact owned owner/origin recovery guard. | Adapter suite failed on the missing-owner case after an unexpected `worker-stop`. | KILLED |
| Skip persisted replay dispatch revocation. | Adapter suite failed on fresh-adapter stale `worker_done` replay. | KILLED |

**Sensor:** 5 mutations injected, 5 killed, 0 survived. **PASS**.

### Fingerprint disposition

No new blocker, spec gap, or surviving mutant was found. Existing fingerprints remain closed at
their recorded counts; `.specs/features/parallel-slice-executor/review-fingerprints.json` was not
changed. No fingerprint reached the third-failure halt threshold.

### Summary

**Overall:** **PASS** for `a7367570c19a9123d4d23e4081eaf82471783ba6` in the requested contextual
terminal-resource scope. Camel/snake ownership projection, exact identity correlation, fail-closed
conflict/missing handling, owned stop/release/retry, adverse zero-effect states, and replay
idempotency are evidenced. No commit, push, merge, real Orca action, product/test edit, or
`docs/qa/**` edit was performed.

## R18 resource-provider preflight technical verification

**Date:** 2026-08-25
**Commit under test:** `0ed8b552a58bda20e1ab858c5648d95042272ee1`
**Base:** `6fba686`
**Diff range:** `6fba686..0ed8b552a58bda20e1ab858c5648d95042272ee1`
**Verifier:** fresh independent Technical Verifier (author != verifier)
**Scoped verdict:** **PASS**

This pass covers the plan-wide resource-provider preflight in
`.agents/skills/autonomous/scripts/parallel_execute.py` and its executor assertions. No real Orca
command ran. The pre-existing dirty/untracked `docs/qa/**` paths were preserved byte-for-byte; no
product file or test file was changed. Only this validation report was updated.

### Spec-anchored outcomes

| Requested outcome | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| Any ready resource-bearing lane with a missing provider falls back deterministically before lane effects, regardless of lane order. | EXE-21 / SEC-007: parallel dispatch is refused with `missing-resource-provider` before a worker can start. | `.agents/skills/autonomous/scripts/parallel_execute.py:1207-1229` performs all lane/provider preflight before adapter construction or action recording; `tools/test_parallel_executor.py:466-503` runs resource-free-first, resource-first, and multi-resource orders and asserts exact reason, empty actions, zero adapter/provider/worktree calls, no state, and no runtime-state file. | PASS |
| A configured but unproven provider is rejected before worktree, lease, worker, action, or runtime-state effects. | EXE-21 / SEC-007: provider absence or failed proof selects serial fallback. | `tools/test_parallel_executor.py:507-529` returns `missing-resource-provider`, asserts `actions == []`, provider construction only once, and `worktree == 0`; the verifier existing-state matrix also proved the persisted state bytes and mtime remain unchanged. | PASS |
| Dry-run/start parity and restart replay preserve the same fallback and do not duplicate effects. | EXE-03 / EXE-04: deterministic plan/result parity and at-most-once effects across restart. | Verifier parity/replay matrix compared the frozen lane projection with `start()` and `resume=True`, then asserted identical `missing-resource-provider` results, empty actions, no state file, and zero effects; provider-backed replay also kept acquire/release at one each. Existing restart assertions remain at `tools/test_parallel_executor.py:255-274,595-657`. | PASS |
| A proven provider-backed resource lane still proceeds and retains correlated lease evidence. | EXE-18–EXE-20: resource-free lanes bypass acquisition; resource lanes require a correlated prepared lease. | `tools/test_parallel_executor.py:410-460` asserts provider bypass for `Resources: none`, one correlated acquire for `port`, exact request fields, prepared-worktree confirmation, and redacted environment. | PASS |
| Disabled mode remains serial and adapter-unsupported mode remains serial without effects. | EXE-01: disabled/unsupported execution does not construct or invoke parallel effects. | `tools/test_parallel_executor.py:189-207` asserts disabled mode does not construct the adapter; `:883-1002` asserts CLI status/start/resume and missing-capability fallback with no worktree effect. | PASS |
| Resource cleanup and provider receipt validation remain unchanged by preflight. | EXE-20–EXE-22 / SEC-008: only unique correlated leases are accepted and owned cleanup is idempotent. | `tools/test_parallel_executor.py:661-780,820-880` covers duplicate/foreign/malformed receipts, failure fallback, one release, and cleanup evidence; the directed executor suite remained green. | PASS |

**Spec-anchored status:** 6/6 requested outcomes matched; 0 FAIL; 0 spec-precision gaps.

### Directed and full gates

- `rtk python3 tools/test_parallel_executor.py` -> exit 0, **45 passed, 0 failed**.
- `rtk python3 tools/test_parallel_plan.py` -> exit 0, **18 passed, 0 failed**.
- `rtk python3 tools/test_workflow_config.py` -> exit 0, **18 passed, 0 failed** (resource-provider configuration path).
- `rtk python3 tools/test_git_adapter.py` -> exit 0, **9 passed, 0 failed**.
- `rtk env npm_config_offline=true npm run test:all` -> exit 0; **110 Vitest + 211 Python = 321 passed**, 0 failed/skipped.
- `rtk python3 .agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-executor/spec.md --strict` -> exit 0, 0 errors, 0 warnings.
- `rtk python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-executor/tasks.md --strict` -> exit 0, 0 errors, 0 warnings.
- `rtk python3 .agents/skills/tlc-spec-driven/scripts/validate_state.py parallel-slice-executor` -> exit 0, 0 errors.
- `rtk python3 tools/ad-index.py --check` -> exit 0, `AD-INDEX.md up to date`.
- `rtk python3 -m py_compile .agents/skills/autonomous/scripts/parallel_execute.py tools/test_parallel_executor.py` -> exit 0.
- `rtk git diff --check 6fba686..0ed8b552a58bda20e1ab858c5648d95042272ee1` -> exit 0.
- Public disposable pilot `setup` + `dry-run` -> exit 0, `validated: true`, equal source/repository HEADs, and exactly two ready `Resources: none` lanes; explicit diagnostic cleanup returned no residual paths. No executor start was issued because `/usr/local/bin/orca` is installed and real Orca use was out of scope.
- Verifier-only preflight, existing-state, parity/replay, provider-backed, disabled, and unsupported matrices -> exit 0; all assertions passed.

### Discrimination sensor

Five detached scratch worktrees under `/tmp/parallel-preflight-sensor-*` were mutated one at a time
and removed. Real-tree porcelain matched the pre-sensor baseline: the same 20 pre-existing QA-only
paths remained, with no implementation, test, or validation path changed by sensor work.

| Mutation | Directed result | Outcome |
| --- | --- | --- |
| Remove the new plan-wide provider guard. | Canonical preflight test exited 1 at `tools/test_parallel_executor.py:500` after adapter/worktree effects appeared. | KILLED |
| Construct the adapter before provider preflight. | Canonical preflight test exited 1 at `tools/test_parallel_executor.py:500` on unexpected adapter construction. | KILLED |
| Persist runtime state before provider preflight. | Canonical preflight test exited 1 at `tools/test_parallel_executor.py:501` because state became observable. | KILLED |
| Bypass the `provider is None` proof guard. | Canonical preflight test exited 1 at `tools/test_parallel_executor.py:500` after unproven dispatch effects. | KILLED |
| Check only the first lane for resource requirements. | Canonical preflight test exited 1 at `tools/test_parallel_executor.py:500` for resource-free-first ordering. | KILLED |

**Sensor:** 5 mutations injected, 5 killed, 0 survived. **PASS**.

### Fingerprint disposition

No new blocker, spec gap, or surviving mutant was found. `.specs/features/parallel-slice-executor/review-fingerprints.json`
was unchanged: 21 fingerprints remain closed, maximum `failed_remediations` is 2, and none reached
the third-failure halt threshold. Clean PASS produced no lesson entry.

### Summary

**Overall:** **PASS** for `0ed8b552a58bda20e1ab858c5648d95042272ee1` in the requested resource-provider
preflight scope. Missing and unproven providers now fail closed before any lane mutation, independent
of order; dry-run/start parity and replay remain deterministic; proven resource lanes proceed; disabled
and unsupported behavior remains unchanged. No commit, push, merge, real Orca action, product/test
edit, or `docs/qa/**` edit was performed.
