# Parallel Slice Dispatch Validation

**Date:** 2026-08-24
**Spec:** `.specs/features/parallel-slice-dispatch/spec.md`
**Feature status:** IN PROGRESS
**Verifier:** independent Verifier (author != verifier)

This report is incremental. It validates Slice 1/T1 only. It does not claim final feature PASS.

## Slice 1 — T1 Technical Verification

**Diff range:** `6675d5574e692a7534b676519e89fbc484289b46..217ac8c`
**Slice verdict:** PASS
**Task:** T1 — Freeze the parallelization mode
**Requirements:** PAR-01, PAR-02, PAR-03, PAR-04

### Task completion

| Task | Status | Evidence |
| --- | --- | --- |
| T1 | Verified | Scoped gate passed and 3/3 sensor mutations were killed. |
| T2 | Pending | Outside this verification packet. |
| T3 | Pending | Outside this verification packet. |
| T4 | Pending | Outside this verification packet. |

### Spec-anchored acceptance criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| PAR-01 | Absent `[parallelization]` freezes `mode = "disabled"` in the snapshot. | `tools/test_workflow_config.py:42` — `assert snapshot["parallelization"] == {"mode": "disabled"}`; `tools/test_workflow_config.py:453` — `assert on_disk["parallelization"] == {"mode": "disabled"}` | PASS |
| PAR-02 | Each exact supported value, `disabled`, `safe`, and `full`, is accepted and frozen unchanged. | `tools/test_workflow_config.py:54` iterates the exact enum; `tools/test_workflow_config.py:75` — `assert result.returncode == 0`; `tools/test_workflow_config.py:77` and `:81` assert the emitted and persisted mode equal the input. | PASS |
| PAR-03 | An unsupported mode fails resolution and leaves the valid snapshot bytes unchanged. | `tools/test_workflow_config.py:95` supplies `speculative`; `tools/test_workflow_config.py:105-108` requires `ConfigError`; `tools/test_workflow_config.py:109` — `assert path.read_bytes() == original`; `tools/test_workflow_config.py:180` covers the CLI non-zero mapping for resolver validation errors. | PASS |
| PAR-04 | Resume returns the previously frozen mode even after configuration and invocation inputs change. | `tools/test_workflow_config.py:130` — `assert resumed == first`; `tools/test_workflow_config.py:131` — `assert resumed["parallelization"] == {"mode": "full"}` | PASS |

**Spec-anchored result:** 4/4 criteria match precise spec outcomes. No spec-precision gap.

### Gate check

| Command | Result |
| --- | --- |
| `python3 tools/test_workflow_config.py` | PASS — 14 passed, 0 failed |
| `python3 .agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-dispatch/spec.md` | PASS — 0 errors, 0 warnings |
| `python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-dispatch/tasks.md` | PASS — 0 errors, 0 warnings |
| `python3 tools/ad-index.py --check` | PASS — `AD-INDEX.md up to date` |
| `git diff --check 6675d5574e692a7534b676519e89fbc484289b46..217ac8c` | PASS — no output |

Baseline command `python3 tools/test_workflow_config.py` at `6675d5574e692a7534b676519e89fbc484289b46` reported 11 passed, 0 failed. T1 reports 14 passed, 0 failed: +3 test functions, no deleted or skipped tests.

### Discrimination sensor

Sensor ran in detached temporary worktree at commit `217ac8c`. Each mutation ran `python3 tools/test_workflow_config.py`. Scratch was removed after the run; real-tree porcelain matched the empty pre-sensor baseline.

| Mutation | Source evidence | Expected regression | Result |
| --- | --- | --- | --- |
| Change `PARALLELIZATION_DEFAULT` from `disabled` to `safe`. | `.agents/skills/workflow-config/scripts/workflow_config.py:28` | PAR-01 default becomes wrong. | KILLED at `tools/test_workflow_config.py:42` |
| Remove `full` from `PARALLELIZATION_MODES`. | `.agents/skills/workflow-config/scripts/workflow_config.py:29` | PAR-02 no longer accepts every supported value. | KILLED at `tools/test_workflow_config.py:75` |
| Replace the frozen mode with current config during resume. | `.agents/skills/workflow-config/scripts/workflow_config.py:318-324` | PAR-04 silently re-resolves `full` as `disabled`. | KILLED at `tools/test_workflow_config.py:130` |

**Sensor depth:** lightweight, 3 targeted behavior mutations.
**Sensor result:** PASS — 3/3 killed, 0 survived.

### Code quality and contract parity

| Check | Result |
| --- | --- |
| Minimum implementation; no speculative executor or planner work | PASS |
| Changes limited to resolver schema, frozen snapshot, canonical tests, config example, and feature workflow artifacts | PASS |
| Existing atomic snapshot writer reused | PASS |
| Tests use the canonical integration suite and assert exact persisted values | PASS |
| IT-001–IT-004 map exactly once to T1 | PASS |
| No `.agents/skills/tlc-spec-driven/` file changed in the diff | PASS |
| Guidelines followed | PASS — `TEST-CONTRACT.md`, `GATES.md`, `VERIFICATION-EVIDENCE.md`, `REVIEW-ROUNDS.md`, `BRANCHING.md`, `ARTIFACT-LIFECYCLE.md` |

### QA disposition

The diff adds a public configuration key. This technical packet did not run QA Plan or QA Execute; those require separate fresh Verifier packets. No product runtime was launched.

### Ranked gaps

None for Slice 1/T1.

## Slice 2 — T2 Technical Verification

**Diff range:** `d6ff064..60a719e`
**Slice verdict:** FAIL
**Task:** T2 — Generate deterministic slice plans
**Requirements:** PAR-05, PAR-06, PAR-07, PAR-08, PAR-09, PAR-10, PAR-11

### Task completion

| Task | Status | Evidence |
| --- | --- | --- |
| T2 | Needs fix | Scoped gate passed and 3/3 sensor mutations were killed, but PAR-09 behavior fails and PAR-09/PAR-10 lack complete spec-anchored assertions. |

### Spec-anchored acceptance criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| PAR-05 | No slice exposes more than its first incomplete task. | `tools/test_parallel_plan.py:74` — fixture contains two pending tasks in Slice A; `tools/test_parallel_plan.py:78` — `assert [item["task"] for item in plan["lanes"]] == ["T1", "T3"]`; `tools/test_parallel_plan.py:79` asserts T2 is blocked by `slice-order:T1`. | PASS |
| PAR-06 | Disabled mode emits one serial lane beginning at the first task in declaration order. | `tools/test_parallel_plan.py:84`; `tools/test_parallel_plan.py:89` — exact lane assertion names T1, Slice A, `status = ready`, and empty `sync_after`; `tools/test_parallel_plan.py:92` asserts T2 is blocked by `disabled-mode`. | PASS |
| PAR-07 | Safe mode exposes a cross-slice consumer only after its producer slice is verified; independent roots remain candidates. | `tools/test_parallel_plan.py:97`; `tools/test_parallel_plan.py:105` exposes only independent T3 before verification; `tools/test_parallel_plan.py:106` asserts `awaiting-verified-slice:A`; `tools/test_parallel_plan.py:109` exposes T2 and T3 after Slice A is verified. | PASS |
| PAR-08 | Full mode exposes a consumer whose upstream task is complete and records that task as required sync checkpoint. | `tools/test_parallel_plan.py:114`; `tools/test_parallel_plan.py:120` — `sync_after == ["T1"]`; `tools/test_parallel_plan.py:121` — `status == "ready"`. | PASS |
| PAR-09 | An incomplete dependency blocks its consumer and no later task from that slice is dispatched. | No test contains an incomplete declared dependency and asserts the consumer's `dependency-incomplete:*` reason. The overlapping conflict probe also demonstrated wrong behavior: `.agents/skills/workflow-config/scripts/parallel_plan.py:212` computes write conflicts before dependency blocking at `:238-249`, returns early at `:214-227`, and omits the consumer from `blocked`. | FAIL |
| PAR-10 | Missing slice metadata, cycles, ambiguous writes, and conflicts among ready candidates produce serial fallback with every decisive reason. | `tools/test_parallel_plan.py:126-144` exercises four graph failures, but `:141` checks only that any reason contains a substring; it does not assert the complete exact reason set. `tools/test_parallel_plan.py:147-153` proves the exact ready-candidate collision reason. Coverage is partial and does not prove “every decisive reason.” | FAIL |
| PAR-11 | Identical feature state and Git head produce byte-equivalent JSON. | `tools/test_parallel_plan.py:157-164` invokes the CLI twice and asserts exact stdout bytes; `tools/test_parallel_plan.py:169-202` asserts the complete point-in-time JSON projection. | PASS |

**Spec-anchored result:** 5/7 criteria match precise spec outcomes. PAR-09 fails behavior and evidence; PAR-10 has incomplete assertion evidence.

### Gate check

| Command | Result |
| --- | --- |
| `python3 tools/test_parallel_plan.py` | PASS — 8 passed, 0 failed |
| `python3 tools/test_workflow_config.py` | PASS — 14 passed, 0 failed |
| `python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-dispatch/tasks.md` | PASS — 0 errors, 0 warnings |
| `python3 .agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-dispatch/spec.md` | PASS — 0 errors, 0 warnings |
| `python3 tools/ad-index.py --check` | PASS — `AD-INDEX.md up to date` |
| `git diff --check d6ff064..60a719e` | PASS — no output |

`tools/test_parallel_plan.py` did not exist at `d6ff064`; T2 adds 8 test functions, deletes none, and skips none. Existing resolver count remains 14 passed.

### Discrimination sensor

Sensor ran in a detached temporary worktree at commit `60a719e`. Each mutation ran `python3 tools/test_parallel_plan.py`. Scratch was removed after the run; real-tree porcelain matched the empty pre-sensor baseline.

| Mutation | Source evidence | Expected regression | Result |
| --- | --- | --- | --- |
| Bypass first-incomplete-per-slice filtering. | `.agents/skills/workflow-config/scripts/parallel_plan.py:203-210` | PAR-05 exposes T2 beside earlier T1 in Slice A. | KILLED at `tools/test_parallel_plan.py:78` |
| Disable safe-mode verified-producer check. | `.agents/skills/workflow-config/scripts/parallel_plan.py:242-246` | PAR-07 exposes T2 before Slice A is verified. | KILLED at `tools/test_parallel_plan.py:105` |
| Disable exact write-collision detection. | `.agents/skills/workflow-config/scripts/parallel_plan.py:142-148` | PAR-10 no longer falls back for two ready tasks writing `src/shared.py`. | KILLED at `tools/test_parallel_plan.py:151` |

**Sensor depth:** lightweight, 3 targeted behavior mutations.
**Sensor result:** PASS — 3/3 killed, 0 survived.

### Code quality and contract parity

| Check | Result |
| --- | --- |
| Standard-library-only, read-only CLI with no executor or worktree side effects | PASS |
| Changes limited to planner, canonical planner tests, and T2 workflow state | PASS |
| Intra-slice ordering and safe/full checkpoint rules remain explicit | PASS |
| Tests map to UT-001–UT-007 and IT-005 without an extra suite | PASS |
| Every PAR-05–PAR-11 outcome has non-hollow evidence | FAIL — PAR-09 has no matching assertion; PAR-10 asserts only one matching substring per malformed graph. |
| State transitions are guarded | FAIL — `.agents/skills/workflow-config/scripts/parallel_plan.py:203-207` treats `in_progress` and `waiting` as fresh candidates, and `:250-257` emits either as `ready`; the spec does not define or test this redispatch transition. |
| Guidelines followed | FAIL — violates evidence-or-zero and hollow-case rules in `TEST-CONTRACT.md` and `VERIFICATION-EVIDENCE.md`. |

### Edge cases

- Exact write collision between two ready candidates: PASS at `tools/test_parallel_plan.py:147-153`.
- Unknown dependency selects fallback and names the ID: PASS at `tools/test_parallel_plan.py:132` and `:139-142`.
- Incomplete dependency plus overlapping write target: FAIL. A fresh probe returned `fallback = true`, reason `write-conflict:T1:T2:src/shared.py`, and no blocked T2, although T2 depended on incomplete T3.
- `in_progress` or `waiting` first task: spec-precision gap. A fresh probe with T1 `in_progress` returned a `ready` lane, permitting duplicate dispatch; no criterion or test defines the intended transition.
- Dirty waiting worker and final reconciliation: outside T2; owned by T3/PAR-13–PAR-15.

### Ranked gaps

1. **Major — PAR-09 behavior deviation.** Premise: `.agents/skills/workflow-config/scripts/parallel_plan.py:212` checks write collisions across all first-incomplete tasks before dependency eligibility at `:238-249`. Path: blocked consumer shares a path with a ready task → planner returns early with serial fallback → consumer is absent from `blocked`, contradicting PAR-09. Fix task: compute dependency eligibility first, compute collisions only across ready candidates, preserve every blocked reason, and add the incomplete-dependency-plus-overlap regression case.
2. **Major — PAR-09 and PAR-10 are not fully proved.** Premise: `tools/test_parallel_plan.py` never asserts `dependency-incomplete:*`, while `tools/test_parallel_plan.py:141` accepts any matching reason substring. Path: dependency blocking or additional decisive reasons can regress while all 8 tests stay green. Fix task: add exact assertions for an incomplete dependency, its later same-slice task, and the complete ordered reason set for a graph with multiple simultaneous failures.
3. **Major spec-precision gap — active/waiting task eligibility is undefined.** Premise: accepted statuses include `in_progress` and `waiting` at `.agents/skills/workflow-config/scripts/parallel_plan.py:16`, but every non-`complete` status becomes a fresh `ready` dispatch at `:203-207` and `:250-257`. Path: replanning can dispatch a second worker for an active task. Fix task: define the intended status transition in PAR-05/PAR-09, then add exact fixtures and implement that rule.

### QA disposition

T2 adds an internal planning CLI for orchestrators. This packet ran technical verification only; no product runtime or QA phase was required.

## Slice 2 — T2 Remediation Re-verification

**Diff range:** `d6ff064..8f8ea1e`
**Remediation commit:** `8f8ea1e`
**Slice verdict after remediation:** PASS
**Feature status:** IN PROGRESS
**Task:** T2/T2R1 — Generate deterministic slice plans and harden planner readiness
**Requirements:** PAR-05, PAR-06, PAR-07, PAR-08, PAR-09, PAR-10, PAR-11, plus the Planner task-status contract

This fresh Verifier retained the preceding FAIL as historical evidence and independently rechecked the remediated tree. The three prior Major gaps are closed; this is not a final feature verdict.

### Task completion

| Task | Status | Evidence |
| --- | --- | --- |
| T2 | Verified after remediation | Scoped gates passed and 4/4 targeted sensor mutations were killed. |
| T2R1 | Verified | Dependency readiness precedes conflict detection; complete decisive reasons and active/waiting transitions are asserted exactly. |

### Spec-anchored acceptance criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| PAR-05 | No slice exposes more than its first incomplete task. | `tools/test_parallel_plan.py:74-79` — two pending Slice A tasks yield lanes `T1`, `T3`, while T2 is exactly blocked by `slice-order:T1`. | PASS |
| PAR-06 | Disabled mode emits one serial lane in declaration order. | `tools/test_parallel_plan.py:84-92` — exact lane equals T1/Slice A/`ready`/no sync and T2 is blocked by `disabled-mode`. | PASS |
| PAR-07 | Safe mode exposes independent roots and holds a cross-slice consumer until its producer slice is verified. | `tools/test_parallel_plan.py:97-109` — before verification only T3 is ready and T2 has exact reason `awaiting-verified-slice:A`; after verification T2 and T3 are ready. | PASS |
| PAR-08 | Full mode exposes a consumer after its upstream task completes and records that checkpoint. | `tools/test_parallel_plan.py:114-121` — T2 has `sync_after == ["T1"]` and `status == "ready"`. | PASS |
| PAR-09 | An incomplete dependency blocks its consumer before conflict evaluation and no later same-slice task is dispatched. | `tools/test_parallel_plan.py:157-167` — T2 shares T1's write path but remains exactly blocked by `dependency-incomplete:T3`, while only T1 and T3 are lanes; `tools/test_parallel_plan.py:74-79` proves a later same-slice task stays blocked. | PASS |
| PAR-10 | Invalid graph metadata and every decisive graph reason cause serial fallback; collisions are evaluated only among ready candidates and name both tasks. | `tools/test_parallel_plan.py:126-153` covers each required class and the exact collision; `tools/test_parallel_plan.py:172-187` asserts the complete ordered four-reason set; `tools/test_parallel_plan.py:157-167` proves a blocked consumer cannot create a false collision fallback. | PASS |
| PAR-11 | Identical feature state and Git head emit byte-identical JSON. | `tools/test_parallel_plan.py:233-240` — two CLI invocations assert exact stdout bytes; `tools/test_parallel_plan.py:245-278` asserts the complete projection. | PASS |

**Spec-anchored result:** 7/7 PAR-05–PAR-11 criteria match precise outcomes. No spec-precision gap remains.

### Status-transition and edge precision

| Contract / edge | `file:line` + assertion | Result |
| --- | --- | --- |
| `in_progress` never starts another worker | `tools/test_parallel_plan.py:192-199` — only T2 is a lane and T1 is exactly blocked by `in-progress:T1`. | PASS |
| `waiting` stays blocked while a dependency is incomplete | `tools/test_parallel_plan.py:203-209` — only T2 is a lane and T1 is exactly blocked by `waiting-on-dependency:T2`. | PASS |
| `waiting` becomes `follow_up` only after all declared dependencies complete | `tools/test_parallel_plan.py:213-228` — the exact sole lane is T1 with `status = follow_up` and `sync_after = ["T2"]`. | PASS |
| Exact write collision selects fallback | `tools/test_parallel_plan.py:147-152` — fallback is true and names `write-conflict:T1:T2:src/shared.py`. | PASS |
| Unknown dependency selects fallback and names the unknown ID | `tools/test_parallel_plan.py:132-142` plus the exact combined assertion at `tools/test_parallel_plan.py:172-187` names `unknown-dependency:T1->T99`. | PASS |

Dirty waiting workers and final reconciliation remain outside T2 and are owned by T3/PAR-13–PAR-15.

### Fresh gate check

| Command | Result |
| --- | --- |
| `python3 tools/test_parallel_plan.py` | PASS — 11 passed, 0 failed, 0 skipped |
| `python3 tools/test_workflow_config.py` | PASS — 14 passed, 0 failed, 0 skipped |
| `python3 /Users/antoniofulg/Projects/my-workflow/.agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-dispatch/tasks.md` | PASS — 0 errors, 0 warnings |
| `git diff --check d6ff064..8f8ea1e` | PASS — no output |

The prior T2 report recorded 8 planner tests. Remediation adds 3 regression functions, for 11 total; no planner test was deleted or skipped.

### Fresh discrimination sensor

Sensor ran in detached temporary worktree `/tmp/parallel-sensor.AMSDrV/tree` at `8f8ea1e`. Each mutation ran `python3 tools/test_parallel_plan.py`; the scratch was removed and real-tree porcelain remained identical to the empty baseline.

| Mutation | Source evidence | Expected regression | Result |
| --- | --- | --- | --- |
| Bypass incomplete-dependency blocking. | `.agents/skills/workflow-config/scripts/parallel_plan.py:243-247` | A blocked consumer is exposed and can participate in a false write conflict. | KILLED at `tools/test_parallel_plan.py:167` |
| Stop recognizing `in_progress` as active. | `.agents/skills/workflow-config/scripts/parallel_plan.py:237-240` | An active task is redispatched as a fresh lane. | KILLED at `tools/test_parallel_plan.py:198` |
| Emit `ready` instead of `follow_up` for a satisfied waiting worker. | `.agents/skills/workflow-config/scripts/parallel_plan.py:257-263` | Resume semantics collapse into a new-worker dispatch. | KILLED at `tools/test_parallel_plan.py:220` |
| Retain only the first decisive graph reason. | `.agents/skills/workflow-config/scripts/parallel_plan.py:214-218` | Combined invalid input hides later decisive reasons. | KILLED at `tools/test_parallel_plan.py:182` |

**Sensor depth:** lightweight, 4 targeted behavior mutations focused on the historical gaps.
**Sensor result:** PASS — 4/4 killed, 0 survived.

### Code quality and contract parity

| Check | Result |
| --- | --- |
| Read-only, standard-library planner remains the minimum implementation | PASS |
| Dependency eligibility is computed before write conflicts | PASS — `.agents/skills/workflow-config/scripts/parallel_plan.py:237-267` |
| Every PAR-05–PAR-11 outcome has non-hollow assertion evidence | PASS |
| Active and waiting transitions match the newly precise spec table | PASS |
| Remediation is limited to planner, canonical tests, spec precision, and workflow state | PASS |
| Test contract followed | PASS — exact inputs and outcomes live in the canonical `tools/test_parallel_plan.py` suite; no duplicate suite or implementation-mirroring assertion was added. |

### Ranked gaps

None for Slice 2/T2 after remediation.

## Feature Summary

**Overall:** IN PROGRESS

Slice 1/T1 remains technically verified. Slice 2/T2 now passes fresh technical re-verification after remediation; its prior FAIL remains above as historical evidence. T3–T4, resolved deep-review group, final gate, and final QA remain pending. `validate_state.py` remains intentionally deferred until the feature can truthfully claim final PASS.

## Slice 3 — T3/T4 Technical Verification

**Diff range:** `51a8aaa..723e098`
**Slice verdict:** FAIL
**Tasks:** T3 — autonomous inter-slice orchestration; T4 — durable decisions
**Requirements:** PAR-12, PAR-13, PAR-14, PAR-15, PAR-16

### Task completion

| Task | Status | Evidence |
| --- | --- | --- |
| T3 | Needs fix | Full gates pass, but IT-006 does not discriminate every precise PAR-13–PAR-15 outcome; 1/3 final sensor mutations survived. |
| T4 | Verified | Decisions are present at `.specs/features/parallel-slice-dispatch/decisions.md:20`; `python3 tools/ad-index.py --check` passed. |

### Spec-anchored acceptance criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| PAR-12 | Missing isolated executor uses existing serial path without creating worker/worktree. | `tools/shared/tests/autonomous-parallelization.test.ts:29-31` asserts all three exact clauses; policy at `.agents/skills/autonomous/references/parallelization.md:20-23`. | PASS |
| PAR-13 | Unavailable dependency requires clean committed checkpoint with exact dependency/head, turn end, and event-only follow-up. | `tools/shared/tests/autonomous-parallelization.test.ts:34-36` asserts turn end, dependency event, and no polling, but does not assert reporting exact dependency/head; policy at `.agents/skills/autonomous/references/parallelization.md:40-47`. | FAIL |
| PAR-14 | New upstream checkpoint is synchronized before consumption and its affected gate reruns before continuation. | `tools/shared/tests/autonomous-parallelization.test.ts:37-39` asserts checkpoint sync cadence and final reconciliation wording, but not the affected-gate rerun at `.agents/skills/autonomous/references/parallelization.md:51-54`. | FAIL |
| PAR-15 | A changed reviewed tree invalidates every affected gate/Verifier/deep-review verdict and repeats the affected gate. | `tools/shared/tests/autonomous-parallelization.test.ts:40` asserts invalidation of all three verdict classes, but not the repeat-gate clause at `.agents/skills/autonomous/references/parallelization.md:63`. | FAIL |
| PAR-16 | Sequential TLC tasks retain atomic commit/scoped gate, slice Verifier, frozen-group deep-review, final QA, and final-tree full gate. | `tools/shared/tests/autonomous-parallelization.test.ts:33,41-46` asserts each exact retained stage; policy at `.agents/skills/autonomous/references/parallelization.md:65-74`. | PASS |

**Spec-anchored result:** 2/5 Slice 3 criteria fully match precise outcomes. PAR-13–PAR-15 have partial, hollow contract assertions.

### Edge cases

| Edge | Evidence | Result |
| --- | --- | --- |
| Same exact write path selects serial fallback. | `tools/test_parallel_plan.py:147-153` asserts the named collision. | PASS |
| Unknown dependency selects fallback and names ID. | `tools/test_parallel_plan.py:172-187` asserts the complete ordered reason set including `unknown-dependency:T1->T99`. | PASS |
| Dirty waiting worker refuses waiting and selects serial recovery. | Policy exists at `.agents/skills/autonomous/references/parallelization.md:44-47,78-81`; no assertion in `tools/shared/tests/autonomous-parallelization.test.ts:12-48` names dirty state. | FAIL |
| Already-consumed final base makes final reconciliation a no-op. | Policy exists at `.agents/skills/autonomous/references/parallelization.md:56-57`; `tools/shared/tests/autonomous-parallelization.test.ts:39` asserts only the phrase `final reconciliation`. A contrary behavior mutation survived. | FAIL |

### Fresh full and build gates

| Command | Result |
| --- | --- |
| `npm_config_offline=true npm test` | PASS — 9 files, 109 tests passed, 0 failed, 0 skipped. |
| `for test_file in tools/test_*.py; do python3 "$test_file" || exit 1; done` | PASS — seven suites: ad-index `ok`; numbered suites 8 + 5 + 19 + 11 + 9 + 14 = 66 passed, 0 failed, 0 skipped. |
| `python3 .agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-slice-dispatch/spec.md` | PASS — 0 errors, 0 warnings. |
| `python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-dispatch/tasks.md` | PASS — 0 errors, 0 warnings. |
| `python3 tools/ad-index.py --check` | PASS — `AD-INDEX.md up to date`. |
| `git diff --check 6675d5574e692a7534b676519e89fbc484289b46..723e098` | PASS — no output. |

Baseline at `6675d5574e692a7534b676519e89fbc484289b46`, measured in detached worktree with the same commands: Vitest 8 files/108 tests; Python ad-index `ok` plus 52 numbered tests. Current delta: +1 Vitest contract test and +14 Python tests; no deletion or skip observed.

### Fresh discrimination sensor

Sensor ran in three detached temporary worktrees at `723e098`. Scratch worktrees were removed; real-tree porcelain matched the empty pre-sensor baseline.

| Mutation | Expected regression | Result |
| --- | --- | --- |
| `.agents/skills/workflow-config/scripts/parallel_plan.py:245` bypassed incomplete-dependency blocking. | PAR-09 consumer becomes dispatchable. | KILLED by `tools/test_parallel_plan.py:167`. |
| `.agents/skills/autonomous/references/parallelization.md:56-57` changed conditional no-op reconciliation into unconditional rebase while retaining `final reconciliation`. | Final-base edge contract becomes false. | SURVIVED — `tools/shared/tests/autonomous-parallelization.test.ts` remained 1/1 green. |
| `.agents/skills/autonomous/references/parallelization.md:63` preserved stale verdicts instead of invalidating them. | PAR-15 evidence becomes unsafe. | KILLED by `tools/shared/tests/autonomous-parallelization.test.ts:40`. |

**Sensor depth:** lightweight, 3 targeted behavior mutations across planner and orchestration contract.
**Sensor result:** FAIL — 2/3 killed, 1 survived.

### Ranked gaps

1. **Major — IT-006 is hollow for precise synchronization/waiting outcomes.** Premise: `tools/shared/tests/autonomous-parallelization.test.ts:34-40` omits exact dependency/head reporting, affected-gate rerun before continuation, repeat-gate behavior after invalidation, dirty-worker refusal, and conditional final-reconciliation no-op. Path: these safety clauses can regress while the canonical contract suite stays green; the observed unconditional-rebase mutant did exactly that. Fix task: extend existing IT-006 in the canonical suite with exact assertions for these clauses; do not create another suite. Gate: targeted Vitest file, full `npm_config_offline=true npm test`, then rerun proportional sensor.

### QA disposition

This diff changes public configuration/CLI and docs-as-interface. Technical validation does not replace QA. Fresh QA Plan and QA Execute sessions remain required after technical PASS and deep-review closure.

## Final Feature Technical Verdict

**Diff range:** `6675d5574e692a7534b676519e89fbc484289b46..723e098`
Verdict: FAIL

| Requirement group | Result |
| --- | --- |
| PAR-01–PAR-04 | PASS — retained Slice 1 evidence; current resolver suite 14/14 green. |
| PAR-05–PAR-11 | PASS — retained remediated Slice 2 evidence; current planner suite 11/11 green. |
| PAR-12, PAR-16 | PASS — exact orchestration fallback and retained-stage assertions. |
| PAR-13–PAR-15 | FAIL — precise clauses are present in source contract but not fully discriminated by IT-006. |

All recorded tasks are marked complete, all fresh gates pass, and baseline counts did not decrease. Technical completion still fails because evidence-or-zero and sensor requirements are stronger than a green gate. Deep-review and QA remain delivery stages outside this technical verdict; neither should run as a substitute for closing this test gap.
