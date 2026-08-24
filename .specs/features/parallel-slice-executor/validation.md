# Parallel Slice Executor Validation

**Verdict**: FAIL
**Date:** 2026-08-24
**Phase:** Technical Verification
**Scope:** Slice A prior PASS retained; Slice B/T3 PASS retained; Slice C/T4 independently verified
**Spec:** `.specs/features/parallel-slice-executor/spec.md`
**Diff range:** `d73071c..a799eac`
**Incremental slice:** `b797777..a799eac`
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

## Slice C / T4 Technical Verification

**Slice verdict:** FAIL. EXE-12–EXE-14 and EXE-16–EXE-17 are directly discriminated at the Git
adapter layer. EXE-15 is not implemented at its owning coordinator boundary: the adapter returns an
`invalidated_evidence` list, but no coordinator consumes it, invalidates stored receipts, or blocks
follow-up until the affected gate reruns. A passing adapter payload assertion is not evidence of that
state transition.

### Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | Evidence | Result |
| --- | --- | --- | --- |
| EXE-12 | A clean consumer rebases onto the exact recorded producer commit before dependent work. | `.agents/skills/autonomous/scripts/git_adapter.py:99-137`; `tools/test_git_adapter.py:54-65` asserts clean sync, exact producer ancestry, changed HEAD, and exact changed path; `tools/test_git_adapter.py:101-110` rejects a dirty consumer without changing HEAD/content. | PASS |
| EXE-13 | An already-ancestor producer makes checkpoint sync a byte-stable no-op. | `.agents/skills/autonomous/scripts/git_adapter.py:120-130`; `tools/test_git_adapter.py:67-70` asserts `status == "noop"`, equal pre/post HEAD, and no changed path. Sensor M1 kills reversing the ancestry test. | PASS |
| EXE-14 | Rebase conflict or undeclared path aborts, restores the clean pre-sync HEAD, and returns serial recovery. | `.agents/skills/autonomous/scripts/git_adapter.py:131-142`; `tools/test_git_adapter.py:76-95` asserts conflict serial recovery, identical pre/post HEAD, and clean status; `tools/test_git_adapter.py:147-157` asserts undeclared-path reason, restored HEAD, exact changed path, and clean status. Sensor M2 kills omitted conflict cleanup. | PASS |
| EXE-15 | A changed checkpoint HEAD causes the coordinator to invalidate gate, Technical Verifier, and deep-review receipts and require the affected gate before follow-up. | `.agents/skills/autonomous/scripts/git_adapter.py:143-151` only returns three names; `tools/test_git_adapter.py:59-65` only asserts that return value. `rg -n 'GitAdapter|sync_checkpoint|invalidated_evidence' .agents/skills/autonomous/scripts tools` finds no coordinator consumer outside the adapter and its direct test. No assertion proves receipt mutation or follow-up refusal. | FAIL |
| EXE-16 | Technically verified slice commits merge into the feature branch in deterministic slice order without rewriting them. | `.agents/skills/autonomous/scripts/git_adapter.py:153-190` sorts then merges with `--no-ff`; `tools/test_git_adapter.py:163-183` supplies B then A, asserts merged A/B order, exact paths, and both original commits as HEAD ancestors. | PASS |
| EXE-17 | Integration conflict aborts, restores the clean pre-operation HEAD, and delegates resolution to serial recovery. | `.agents/skills/autonomous/scripts/git_adapter.py:171-181`; `tools/test_git_adapter.py:188-208` asserts `merge-conflict`, serial status, identical pre/post HEAD, and clean status. | PASS |

**Spec-anchored status:** 5 PASS, 1 FAIL, 0 spec-precision gaps for Slice C.

### Test Contract Disposition

| Case | Contracted outcome | Evidence | Result |
| --- | --- | --- | --- |
| UT-004 | Exact producer rebase or byte-stable ancestor no-op. | `tools/test_git_adapter.py:54-70` asserts both branches with exact values; M1 is killed. | PASS |
| UT-005 | Conflict abort restores pre-sync HEAD and clean state and halts the lane. | `tools/test_git_adapter.py:76-95` asserts serial recovery, identical HEAD, and clean status; M2 is killed. | PASS |
| UT-006 | Changed-HEAD evidence is invalidated before follow-up; verified merges are stable; conflict aborts cleanly. | Merge and conflict outcomes are asserted at `tools/test_git_adapter.py:163-208`; evidence names are asserted only at `tools/test_git_adapter.py:59-65`. The coordinator transition and required-gate-before-follow-up outcome have no test. Under `docs/guidelines/TEST-CONTRACT.md:45-57`, this boundary behavior needs an integration-layer assertion; existence of the adapter payload alone is hollow for EXE-15. | FAIL |

### Gate Evidence

- `python3 tools/test_git_adapter.py` -> exit 0, `7 passed, 0 failed`; 0 skipped.
- `python3 tools/test_orca_adapter.py` -> exit 0, `20 passed, 0 failed`; 0 skipped.
- `python3 tools/test_parallel_executor.py` -> exit 0, `32 passed, 0 failed`; 0 skipped.
- Scoped total: 59 passed, 0 failed, 0 skipped. Git adapter suite at `b797777`: absent; at `a799eac`: 7 tests; delta +7.
- `python3 .../tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-executor/spec.md --strict` -> exit 0, 0 errors, 0 warnings.
- `python3 .../tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-executor/tasks.md --strict` -> exit 0, 0 errors, 0 warnings.
- `python3 tools/ad-index.py --check` -> exit 0, `AD-INDEX.md up to date`.
- `git diff --check b797777..a799eac` -> exit 0, no output.
- `python3 -m py_compile .agents/skills/autonomous/scripts/git_adapter.py tools/test_git_adapter.py .agents/skills/autonomous/scripts/orca_adapter.py tools/test_orca_adapter.py .agents/skills/autonomous/scripts/parallel_execute.py tools/test_parallel_executor.py` -> exit 0.
- `python3 .../tlc-spec-driven/scripts/check_commit.py --message 'feat(workflow): reconcile slice checkpoints'` -> exit 0, `check_commit: OK`.
- `git diff --check` after this report edit -> exit 0, no output.
- `python3 .../tlc-spec-driven/scripts/validate_state.py parallel-slice-executor` -> exit 1 because this report correctly retains verdict `FAIL` and routes the EXE-15 gap; feature completion is blocked.

### Discrimination Sensor

Real-tree porcelain was empty before the sensor. Each mutation ran in its own detached temporary
worktree at `a799eac`; all scratch worktrees and their parent directory were removed. Real-tree
porcelain returned to the same empty baseline.

| Mutation | Behavior fault | Directed result | Outcome |
| --- | --- | --- | --- |
| M1 | Reverse producer/pre-HEAD ancestry detection, breaking ancestor no-op. | Git suite exit 1 at `tools/test_git_adapter.py:68`, expected `status == "noop"`. | KILLED |
| M2 | Omit `_restore` after a rebase conflict. | Git suite exit 1 at `tools/test_git_adapter.py:95`, expected clean `git status --porcelain`. | KILLED |
| M3 | Return no invalidated evidence after a successful changed-HEAD sync. | Git suite exit 1 at `tools/test_git_adapter.py:64`, expected gate/Technical Verifier/deep-review names. | KILLED |

**Sensor:** lightweight, 3 injected, 3 killed, 0 survived. PASS. This proves adapter-level
discrimination; it does not supply the missing coordinator integration for EXE-15.

### AD-012 Fingerprint Accounting

| Fingerprint | Disposition | Prior failed-remediation count | This verification increment | Resulting count |
| --- | --- | ---: | ---: | ---: |
| `EXE-15 + coordinator never consumes Git sync invalidated_evidence + changed-head lane can follow up without rerunning the affected gate` | OPEN; Major fix task required. This is the initial finding, not a failed post-fix re-verification. | 0 | 0 | 0 |

AD-012 and `docs/guidelines/REVIEW-ROUNDS.md:89-91` halt only after the third failed remediation of
this same fingerprint. No historical fingerprint was renamed, reopened, or incremented by this
Slice C verification.

### Ranked Gaps

1. **Major / fix task — EXE-15:** Premise: `.agents/skills/autonomous/scripts/git_adapter.py:143-151`
   emits invalidation labels, while no coordinator code consumes them. Path: checkpoint sync changes
   HEAD -> adapter returns labels -> coordinator has no persisted receipt invalidation or required-gate
   transition -> dependent follow-up can proceed on stale gate/Verifier/deep-review evidence. Verdict:
   implement the coordinator boundary and extend the canonical executor integration suite to assert
   invalidation plus follow-up refusal until the affected gate passes.

### Slice C Summary

**Overall:** FAIL for Slice C. Five of six ACs match their spec-defined outcomes, 59 scoped
regression tests pass, and all three adapter mutants die. EXE-15 remains evidence-zero at the
coordinator layer. This verdict does not close the feature, grouped C-D deep-review, real Orca pilot,
QA Plan, or QA Execute.

## T4R1 post-remediation

T4R1 closes the EXE-15 coordinator-boundary gap while the feature-level report remains FAIL for
the still-planned T5–T7 work. `sync_after` now resolves exact producer `current_head` receipts,
persists the sync action before the Git effect, stores changed-head/current-head evidence, and
blocks worker start or follow-up at `gate_required`. Restart reuses the accepted sync receipt
without resync. A gate receipt is accepted only when `passed` is true and lane, gate, and
`current_head` match; only `gate` invalidation is removed.

Evidence: `tools/test_parallel_executor.py` exercises changed-head blocking, restart-safe receipt
reuse, exact gate rejection/acceptance, and no worker effect before acceptance; the Git and Orca
regressions remain green. The persisted fingerprint ledger remains at count 1 for `da76f3...`;
this successful remediation does not increment it.

The earlier AD-012 table above records the pre-ledger verifier snapshot; the persisted
`.specs/features/parallel-slice-executor/review-fingerprints.json` is authoritative for this
remediation and records `failed_remediations: 1` for `da76f3...`.
