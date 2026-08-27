# Merge-Alone Slice Derivation Validation

**Date**: 2026-08-27
**Spec**: `.specs/features/merge-alone-slices/spec.md`
**Diff range**: `d0dd82d..5dee2e2`
**Verified head**: `5dee2e245d7243db8b52cd1cbd2452aaddc9c353`
**Verifier**: fresh independent Technical Verifier (author != verifier)
**Verdict**: PASS

## Task Completion

| Task group | Status | Evidence |
| --- | --- | --- |
| T1-T5 | Verified | Validator, resolver, public-contract, adoption, and full gates passed; `tasks.md:52` through `tasks.md:212` retain exact task gates. |
| R1-R2 | Verified | Error identity, byte preservation, remediation exclusion, membership equality, and count bounds pass at `tools/test_tlc_validators.py:146` and `tools/test_workflow_config.py:195`. |
| DR1-DR2 | Verified | Canonical heading, Slice-field, closure-gate, and remediation-boundary cases pass in `tools/test_tlc_validators.py:1`. |
| QA1 | Verified | Active v2 consumers pass at `tools/test_parallel_plan.py:127`, `tools/test_parallel_executor.py:120`, and `tools/test_qa_parallel_pilot.py:23`. |
| R3 | Verified | `tools/test_tlc_validators.py:115` proves three cohorts, five primary tasks, and one closure-owned slice; the cohort-count mutant is killed by `tools/test_workflow_config.py:174`. |

R3 fixture counts are independently reproduced by `rg -c '^### Phase ' tools/fixtures/tlc-validator/merge-alone-one-slice.md` = 3, `rg -c '^### T[0-9]+:' tools/fixtures/tlc-validator/merge-alone-one-slice.md` = 5, and `rg -c '^\| [A-Z]+ \| ' tools/fixtures/tlc-validator/merge-alone-one-slice.md` = 1 closure.

## Spec-Anchored Acceptance Criteria

| AC | Spec-defined outcome | `file:line` + assertion evidence | Result |
| --- | --- | --- | --- |
| MAS-01 | Five primary tasks, three technical cohorts, and one closure derive exactly one slice. | `tools/test_tlc_validators.py:115` through `tools/test_tlc_validators.py:135` assert 3 cohorts, 5 primary tasks, `slice_ids == ["A"]`, 5 memberships, and exact `A` ownership; `tools/test_workflow_config.py:174` through `tools/test_workflow_config.py:180` assert resolver groups `[[1]]`. | PASS |
| MAS-02 | Two merge-alone outcomes derive exactly two slices. | `tools/test_tlc_validators.py:137` through `tools/test_tlc_validators.py:144` assert `A`, `B`, and exact membership; `tools/test_workflow_config.py:185` through `tools/test_workflow_config.py:190` assert groups `[[1, 2]]`. | PASS |
| MAS-03 | Empty closure fields and every non-exact-`yes` decision fail while naming the invalid slice. | `tools/test_tlc_validators.py:146` through `tools/test_tlc_validators.py:178` require slice `A`, each missing field, and exact lowercase `yes` for `no`, empty, `Yes`, and `true`. | PASS |
| MAS-04 | Zero, multiple, unknown, orphan, and duplicate membership fail with task or slice identity. | `tools/test_tlc_validators.py:180` through `tools/test_tlc_validators.py:213` require `T1`, `Z`, duplicate `A`, or orphan `B`. | PASS |
| MAS-05 | Initial/refresh count mismatch and non-positive assertions fail before snapshot mutation. | `tools/test_workflow_config.py:195` through `tools/test_workflow_config.py:254` assert mismatch messages, absent initial snapshot, and byte-identical refresh snapshot; `tools/test_workflow_config.py:210` rejects `0` and `-1`. | PASS |
| MAS-06 | Missing `tasks.md` derives one slice. | `tools/test_workflow_config.py:284` through `tools/test_workflow_config.py:290` assert `[[1]]`. | PASS |
| MAS-07 | Malformed present Tasks fail before snapshot creation or replacement. | `tools/test_workflow_config.py:259` through `tools/test_workflow_config.py:304` assert named closure failure, no initial file, and unchanged refresh bytes. | PASS |
| MAS-08 | Resume returns frozen state without reading changed or malformed Tasks. | `tools/test_workflow_config.py:309` through `tools/test_workflow_config.py:325` assert frozen object and bytes for both task states. | PASS |
| MAS-09 | Published contract distinguishes slice, phase/cohort, and batch and removes manual count ownership. | `tools/shared/tests/workflow-config.test.ts:50` through `tools/shared/tests/workflow-config.test.ts:62` assert all three terms, closure fields, derived ownership, and optional assertion wording. | PASS |
| MAS-10 | `T2R1` and `TDR1` do not enter primary membership or count. | `tools/test_tlc_validators.py:137` through `tools/test_tlc_validators.py:144` assert both headings and exactly four primary memberships; fixtures appear at `tools/fixtures/tlc-validator/merge-alone-two-slices.md:64` and `tools/fixtures/tlc-validator/merge-alone-two-slices.md:71`. | PASS |
| MAS-11 | Validator and planner preserve identical primary-task membership and slice IDs. | `tools/test_parallel_plan.py:101` through `tools/test_parallel_plan.py:122` compare outputs derived from one task document. | PASS |
| MAS-12 | Planner and executor accept resolver snapshot v2 while preserving identity validation. | `tools/test_parallel_plan.py:127` through `tools/test_parallel_plan.py:152` assert real resolver v2, membership equality, and Git head; `tools/test_parallel_executor.py:120` through `tools/test_parallel_executor.py:126` assert executor acceptance. | PASS |
| MAS-13 | Planner and executor reject active snapshot v1 without fallback or migration. | `tools/test_parallel_plan.py:370` through `tools/test_parallel_plan.py:394` and `tools/test_parallel_executor.py:127` through `tools/test_parallel_executor.py:136` require `invalid workflow snapshot`. | PASS |

**Status**: 13/13 matched; 0 uncovered; 0 spec-precision gaps. Count command: `rg -c '^\| MAS-[0-9]{2} \|' .specs/features/merge-alone-slices/validation.md`.

## Test Contract

| Contract | `file:line` + assertion evidence | Result |
| --- | --- | --- |
| MAS-UT-001 | `tools/test_tlc_validators.py:115` through `tools/test_tlc_validators.py:135` assert exactly 3 cohorts, 5 primary tasks, closure `A`, 5 `A` memberships, and exact merge-alone `true`. | PASS |
| MAS-UT-002 | `tools/test_tlc_validators.py:137` through `tools/test_tlc_validators.py:144` assert exactly `A`, `B`, and exact membership. | PASS |
| MAS-UT-003 | `tools/test_tlc_validators.py:146` through `tools/test_tlc_validators.py:169` assert slice `A` plus each missing field. | PASS |
| MAS-UT-004 | `tools/test_tlc_validators.py:171` through `tools/test_tlc_validators.py:178` reject `no`, empty, `Yes`, and `true` with exact error identity. | PASS |
| MAS-UT-005 | `tools/test_tlc_validators.py:180` through `tools/test_tlc_validators.py:203` assert zero, multiple, and unknown membership. | PASS |
| MAS-UT-006 | `tools/test_tlc_validators.py:205` through `tools/test_tlc_validators.py:213` assert duplicate `A` and orphan `B`. | PASS |
| MAS-UT-007 | `tools/test_tlc_validators.py:137` through `tools/test_tlc_validators.py:144` assert both remediation forms and unchanged primary membership. | PASS |
| MAS-IT-001 | `tools/test_workflow_config.py:174` through `tools/test_workflow_config.py:180` resolve the shared three-cohort fixture to `[[1]]`. | PASS |
| MAS-IT-002 | `tools/test_workflow_config.py:185` through `tools/test_workflow_config.py:190` resolve two closures to `[[1, 2]]`. | PASS |
| MAS-IT-003 | `tools/test_workflow_config.py:195` through `tools/test_workflow_config.py:254` assert mismatch failure and absent/byte-identical snapshot state. | PASS |
| MAS-IT-004 | `tools/test_workflow_config.py:284` through `tools/test_workflow_config.py:290` assert no-Tasks `[[1]]`. | PASS |
| MAS-IT-005 | `tools/test_workflow_config.py:293` through `tools/test_workflow_config.py:304` assert malformed closure failure and no snapshot. | PASS |
| MAS-IT-006 | `tools/test_workflow_config.py:309` through `tools/test_workflow_config.py:325` assert byte-for-byte frozen resume. | PASS |
| MAS-IT-007 | `tools/test_workflow_config.py:330` through `tools/test_workflow_config.py:347` assert refresh `[[1, 2]]` with unchanged schema/version. | PASS |
| MAS-IT-008 | `tools/test_parallel_plan.py:101` through `tools/test_parallel_plan.py:122` directly compare validator and planner membership. | PASS |
| MAS-IT-009 | `tools/shared/tests/workflow-config.test.ts:50` through `tools/shared/tests/workflow-config.test.ts:62` assert the published planning contract. | PASS |
| MAS-IT-010 | `tools/test_parallel_plan.py:127` through `tools/test_parallel_plan.py:152` pass real resolver v2 output to planner and assert exact membership. | PASS |
| MAS-IT-011 | `tools/test_parallel_plan.py:370` through `tools/test_parallel_plan.py:394` and `tools/test_parallel_executor.py:120` through `tools/test_parallel_executor.py:136` accept v2 and reject v1. | PASS |
| MAS-IT-012 | `tools/test_qa_parallel_pilot.py:23` through `tools/test_qa_parallel_pilot.py:67` assert pilot v2 lifecycle; `tools/test_qa_parallel_pilot.py:168` through `tools/test_qa_parallel_pilot.py:187` reject v1 and stale Git head. | PASS |

**Status**: 19/19 matched. Count command: `rg -c '^\| MAS-(UT|IT)-[0-9]{3} \|' .specs/features/merge-alone-slices/validation.md`.

## Discrimination Sensor

Sensor used detached temporary worktree `/tmp/mas-r3-sensor.GQo9yW/tree`; real-tree porcelain was empty before creation and after forced removal.

| Mutation | File:line | Targeted command | Result |
| --- | --- | --- | --- |
| Replace closure-owned `len(slice_ids)` with `tasks.md` `### Phase` count. | `.agents/skills/workflow-config/scripts/workflow_config.py:643` | `python3 -c 'import tools.test_workflow_config as t; t.test_initial_resolution_derives_one_slice_from_tasks()'` | KILLED: expected `[[1]]`, mutant derived 3 cohorts. |
| Change planner active workflow predicate from v2 to v1. | `.agents/skills/workflow-config/scripts/parallel_plan.py:46` | `python3 tools/test_parallel_plan.py` | KILLED: suite exited 1. |
| Change executor active workflow predicate from v2 to v1. | `.agents/skills/autonomous/scripts/parallel_execute.py:496` | `python3 tools/test_parallel_executor.py` | KILLED: suite exited 1 with `invalid workflow snapshot`. |

**Sensor depth**: lightweight, highest-risk closure/cohort and active-version boundaries.
**Result**: 3/3 killed; 0 survived. Count command: `rg -c '^\| (Replace|Change) ' .specs/features/merge-alone-slices/validation.md`.

## Gate Check

| Gate | Command | Fresh result |
| --- | --- | --- |
| Actual feature contract | `python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/merge-alone-slices/tasks.md --slice-contract-json` | Exit 0; 5 primary tasks, 1 slice, 1 closure. |
| Validator | `python3 tools/test_tlc_validators.py` | 17 passed, 0 failed. |
| Resolver | `python3 tools/test_workflow_config.py` | 54 passed, 0 failed. |
| Planner | `python3 tools/test_parallel_plan.py` | 20 passed, 0 failed. |
| Executor | `python3 tools/test_parallel_executor.py` | 46 passed, 0 failed. |
| QA pilot | `python3 tools/test_qa_parallel_pilot.py` | 13 passed, 0 failed. |
| Adoption | `python3 scripts/test_adopt.py` | Exit 0, final `ok`. |
| Full | `npm run test:all` | 383 passed: 116 Bun + 267 Python; 0 failed, 0 skipped. `expr 9 + 59 + 46 + 20 + 13 + 6 + 54 + 10 + 5 + 28 + 17` = 267; `expr 116 + 267` = 383. Bun count was emitted by `bun test`. |

No test count decreased from the prior 380-check verified tree; `expr 383 - 380` = +3. No tests were weakened, removed, or skipped.

## Schema and History Boundaries

- Resolver emits active workflow v2 at `.agents/skills/workflow-config/scripts/workflow_config.py:834`.
- Planner output remains plan schema v1 at `.agents/skills/workflow-config/scripts/parallel_plan.py:224`; executor runtime/result schemas remain v1 at `.agents/skills/autonomous/scripts/parallel_execute.py:82` and `.agents/skills/autonomous/scripts/parallel_execute.py:415`.
- QA pilot workflow is v2 at `tools/qa_parallel_pilot.py:72`; its lifecycle/tombstone schemas remain v1 at `tools/qa_parallel_pilot.py:24` and `tools/qa_parallel_pilot.py:191`.
- `git diff --exit-code 459ece2..HEAD -- '.specs/features/*/workflow.json'` exited 0. Historical v1 snapshots remain at `.specs/features/optional-design-tools/workflow.json:35`, `.specs/features/parallel-slice-dispatch/workflow.json:37`, and `.specs/features/security-skills/workflow.json:36`.

## Code Quality and QA Impact

| Check | Result |
| --- | --- |
| Minimum code, surgical scope, no speculative compatibility | PASS |
| Existing validator/resolver/planner/executor patterns preserved | PASS |
| All tests map to ACs, test-contract rows, or existing lifecycle invariants | PASS |
| Guidelines followed: `TEST-CONTRACT.md`, `VERIFICATION-EVIDENCE.md`, `GATES.md`, `REVIEW-ROUNDS.md`, `QA-SCENARIOS.md` | PASS |
| QA impact | Public workflow behaviour changed; existing `CFG-plan-parallel-slice-dispatch` remains pending retest. Technical verification authorizes QA retest, not feature closure. |

## Summary

**Overall**: PASS — R3 verified; whole feature ready for QA retest.

**Spec-anchored check**: 13/13 ACs matched; 0 precision gaps.
**Test contract**: 19/19 rows matched.
**Sensor**: 3/3 mutants killed.
**Full gate**: 383 passed, 0 failed, 0 skipped.
**Next step**: Fresh QA Execute retest for `CFG-plan-parallel-slice-dispatch`, then feature-closing QA decision.
