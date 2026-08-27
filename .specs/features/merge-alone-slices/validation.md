# Merge-Alone Slice Derivation Validation

**Date**: 2026-08-27
**Spec**: `.specs/features/merge-alone-slices/spec.md`
**Diff range**: `d0dd82d..HEAD`
**Verified head**: `100f963c25f7eb5f904431087fd383dc5ffffa4a`
**Verifier**: fresh independent Technical Verifier (author != verifier)
**Verdict**: FAIL

## Task Completion

| Task | Status | Evidence |
| --- | --- | --- |
| T1 | Needs Fix | Validator 17/17 and planner 20/20 passed, but `tools/fixtures/tlc-validator/merge-alone-one-slice.md:17` does not exercise MAS-UT-001's three-cohort input. |
| T2 | Done | `tools/test_workflow_config.py:174`; resolver 54/54 passed. |
| T3 | Done | `tools/test_workflow_config.py:308`; resume and refresh assertions passed. |
| T4 | Done | `tools/shared/tests/workflow-config.test.ts:42`; Bun 116/116 passed. |
| T5 | Done | `package.json:12`; full gate 380/380 passed. |
| R1 | Done | `tools/test_workflow_config.py:230` and `tools/test_parallel_plan.py:89`; prior atomicity and membership gaps remain closed. |
| R2 | Done | `tools/test_tlc_validators.py:143`; every invalid merge-alone value requires slice `A` and exact lowercase `yes`. |
| QA1 | Done — independently verified | `tools/test_parallel_plan.py:127`, `tools/test_parallel_executor.py:120`, and `tools/test_qa_parallel_pilot.py:32`; real v2 resolver flow, planner/executor rejection, and pilot lifecycle passed. |

## Spec-Anchored Acceptance Criteria

Twelve acceptance criteria match their exact spec-defined outcomes. MAS-01 lacks a discriminating
three-cohort regression fixture.

| AC | Spec-defined outcome | `file:line` + assertion evidence | Result |
| --- | --- | --- | --- |
| MAS-01 | Five primary tasks, three technical cohorts, and one closure derive exactly one slice. | `tools/test_tlc_validators.py:115` through `tools/test_tlc_validators.py:122` assert five tasks and one closure, but `tools/fixtures/tlc-validator/merge-alone-one-slice.md:17` declares only one phase/cohort. No current assertion proves three cohorts remain one slice. | GAP |
| MAS-02 | Two merge-alone outcomes derive exactly two slices. | `tools/test_tlc_validators.py:130` — slice IDs equal `["A", "B"]`; `tools/test_workflow_config.py:189` — groups equal `[[1, 2]]`. | PASS |
| MAS-03 | Empty outcome, gate, or reason, and every non-exact-`yes` decision fail while naming invalid slice `A`. | `tools/test_tlc_validators.py:133` through `tools/test_tlc_validators.py:156` pin empty-field identity; `tools/test_tlc_validators.py:161` tests `no`, empty, `Yes`, and `true`; `tools/test_tlc_validators.py:164` requires `slice 'A'.*exact lowercase yes`. | PASS |
| MAS-04 | Zero, multiple, or unknown membership and orphan or duplicate closures fail while naming inconsistent task or slice. | `tools/test_tlc_validators.py:167` through `tools/test_tlc_validators.py:190` require `T1` or `Z`; `tools/test_tlc_validators.py:196` and `tools/test_tlc_validators.py:199` require duplicate `A` and orphan `B`. | PASS |
| MAS-05 | Initial and refresh count mismatches fail before snapshot creation or byte replacement; non-positive assertions fail. | `tools/test_workflow_config.py:201` and `tools/test_workflow_config.py:204` pin initial mismatch and absence; `tools/test_workflow_config.py:250` and `tools/test_workflow_config.py:253` pin refresh mismatch and byte equality; `tools/test_workflow_config.py:210` through `tools/test_workflow_config.py:225` reject `0` and `-1` before write. | PASS |
| MAS-06 | Missing `tasks.md` derives exactly one slice. | `tools/test_workflow_config.py:287` — groups equal `[[1]]`. | PASS |
| MAS-07 | Malformed present Tasks fail before snapshot creation or replacement. | `tools/test_workflow_config.py:299` through `tools/test_workflow_config.py:303` assert initial failure and no file; `tools/test_workflow_config.py:274` through `tools/test_workflow_config.py:278` assert refresh failure and unchanged bytes. | PASS |
| MAS-08 | Normal resume returns frozen state without re-deriving changed or malformed Tasks. | `tools/test_workflow_config.py:309` through `tools/test_workflow_config.py:324` exercise both forms and assert object and byte equality. | PASS |
| MAS-09 | Published planning contract distinguishes slice, phase/cohort, and batch, and derives count from validated Tasks. | `tools/shared/tests/workflow-config.test.ts:50` through `tools/shared/tests/workflow-config.test.ts:62` pin closure fields, all three unit definitions, derived ownership, optional assertion wording, and removal of manual-count examples. | PASS |
| MAS-10 | `T2R1` and `TDR1` remain outside primary membership and count. | `tools/test_tlc_validators.py:124` through `tools/test_tlc_validators.py:131` assert both headings while preserving exactly four primary memberships across `A` and `B`; fixture identities appear at `tools/fixtures/tlc-validator/merge-alone-two-slices.md:64` and `tools/fixtures/tlc-validator/merge-alone-two-slices.md:71`. | PASS |
| MAS-11 | Validator and parallel planner use identical primary-task membership and slice IDs. | `tools/test_parallel_plan.py:112` through `tools/test_parallel_plan.py:122` derive both outputs from one document and assert direct equality. | PASS |
| MAS-12 | Real resolver v2 output reaches planner with identical task/slice membership; planner and executor accept v2 while feature, mode, and Git-head checks remain. | `tools/test_parallel_plan.py:127` through `tools/test_parallel_plan.py:152` assert resolver output version, validator equality, and frozen Git head; `tools/test_parallel_executor.py:120` through `tools/test_parallel_executor.py:126` assert executor v2 acceptance; `tools/test_parallel_plan.py:370` through `tools/test_parallel_plan.py:420` preserve feature/mode/version validation. | PASS |
| MAS-13 | Planner and executor reject workflow snapshot v1 without fallback or migration. | `tools/test_parallel_plan.py:370` through `tools/test_parallel_plan.py:394` require `invalid workflow snapshot` for v1; `tools/test_parallel_executor.py:127` through `tools/test_parallel_executor.py:136` require the same executor error after rewriting v2 to v1. | PASS |

**Status**: 12/13 matched; 1 coverage gap; 0 spec-precision gaps.

## Test Contract

Eighteen canonical rows match their stated outcomes. MAS-UT-001 does not exercise its contracted
three-cohort input.

| Contract | `file:line` + assertion evidence | Result |
| --- | --- | --- |
| MAS-UT-001 | `tools/test_tlc_validators.py:115` through `tools/test_tlc_validators.py:122` assert `A`, five primary memberships, merge-alone true, and validator success, but the fixture at `tools/fixtures/tlc-validator/merge-alone-one-slice.md:17` contains only one phase/cohort instead of three. | GAP |
| MAS-UT-002 | `tools/test_tlc_validators.py:124` through `tools/test_tlc_validators.py:131` assert exactly `A`, `B`, and exact membership. | PASS |
| MAS-UT-003 | `tools/test_tlc_validators.py:133` through `tools/test_tlc_validators.py:156` assert slice `A` plus each missing field. | PASS |
| MAS-UT-004 | `tools/test_tlc_validators.py:158` through `tools/test_tlc_validators.py:165` reject `no`, empty, `Yes`, and `true` while requiring slice `A` and exact lowercase `yes`. | PASS |
| MAS-UT-005 | `tools/test_tlc_validators.py:167` through `tools/test_tlc_validators.py:190` assert zero, multiple, and unknown membership with `T1` or `Z`. | PASS |
| MAS-UT-006 | `tools/test_tlc_validators.py:192` through `tools/test_tlc_validators.py:200` assert duplicate `A` and orphan `B`. | PASS |
| MAS-UT-007 | `tools/test_tlc_validators.py:124` through `tools/test_tlc_validators.py:131` assert `T2R1`, `TDR1`, and unchanged primary membership/count. | PASS |
| MAS-IT-001 | `tools/test_workflow_config.py:179` asserts groups exactly `[[1]]`. | PASS |
| MAS-IT-002 | `tools/test_workflow_config.py:189` asserts groups exactly `[[1, 2]]`. | PASS |
| MAS-IT-003 | `tools/test_workflow_config.py:201` through `tools/test_workflow_config.py:204` assert initial mismatch and no file; `tools/test_workflow_config.py:250` through `tools/test_workflow_config.py:253` assert refresh mismatch and unchanged bytes. | PASS |
| MAS-IT-004 | `tools/test_workflow_config.py:287` asserts missing Tasks yields exactly `[[1]]`. | PASS |
| MAS-IT-005 | `tools/test_workflow_config.py:299` through `tools/test_workflow_config.py:303` assert malformed closure failure and no snapshot. | PASS |
| MAS-IT-006 | `tools/test_workflow_config.py:309` through `tools/test_workflow_config.py:324` assert frozen object and bytes for changed-valid and malformed Tasks. | PASS |
| MAS-IT-007 | `tools/test_workflow_config.py:339` through `tools/test_workflow_config.py:346` assert refresh derives and persists `[[1, 2]]` without schema/version change. | PASS |
| MAS-IT-008 | `tools/test_parallel_plan.py:112` through `tools/test_parallel_plan.py:122` directly compare planner membership with validator output from the same document. | PASS |
| MAS-IT-009 | `tools/shared/tests/workflow-config.test.ts:50` through `tools/shared/tests/workflow-config.test.ts:62` assert published vocabulary and resolver ownership. | PASS |
| MAS-IT-010 | `tools/test_parallel_plan.py:127` through `tools/test_parallel_plan.py:152` pass real resolver v2 output to the planner and assert exact validator membership plus Git head. | PASS |
| MAS-IT-011 | `tools/test_parallel_plan.py:370` through `tools/test_parallel_plan.py:394` and `tools/test_parallel_executor.py:120` through `tools/test_parallel_executor.py:136` accept v2 and reject v1 with `invalid workflow snapshot`. | PASS |
| MAS-IT-012 | `tools/test_qa_parallel_pilot.py:32` through `tools/test_qa_parallel_pilot.py:57` assert pilot workflow v2 and current dry-run/worktree lifecycle; `tools/test_qa_parallel_pilot.py:168` through `tools/test_qa_parallel_pilot.py:187` reject v1 and stale Git head. | PASS |

**Status**: 18/19 matched; 1 contract-row gap.

## Prior Fingerprint Re-check

| Fingerprint | Current evidence | Result |
| --- | --- | --- |
| Error identities (`1f53e6...`) | `tools/test_tlc_validators.py:143` now requires both offending slice `A` and exact lowercase `yes` for all four invalid decisions. | CLOSED BY EVIDENCE |
| Refresh byte preservation (`4af4d6...`) | `tools/test_workflow_config.py:253` and `tools/test_workflow_config.py:278` assert unchanged bytes. | CLOSED BY EVIDENCE |
| Remediation shapes (`bc169e...`) | `tools/test_tlc_validators.py:110` through `tools/test_tlc_validators.py:114` cover `T2R1` and `TDR1`. | CLOSED BY EVIDENCE |
| Validator/planner equality (`c988fe...`) | `tools/test_parallel_plan.py:110` compares outputs from one document. | CLOSED BY EVIDENCE |
| Non-positive assertions (`0ea676...`) | `tools/test_workflow_config.py:210` through `tools/test_workflow_config.py:225` reject `0` and `-1`. | CLOSED BY EVIDENCE |

The immutable `1f53e6...` fingerprint had two failed remediation results before R2. This result passes,
so no third-failure halt is triggered. The separately owned accounting file was not edited by this
Verifier.

## Discrimination Sensor

| Mutation | File:line | Description | Result |
| --- | --- | --- | --- |
| 1 | `.agents/skills/workflow-config/scripts/parallel_plan.py:46` | In detached scratch worktree, changed active workflow predicate `version != 2` to `version != 1`. | KILLED: `python3 tools/test_parallel_plan.py` exited 1 because v2 resolver/fixture snapshots were rejected. |
| 2 | `.agents/skills/autonomous/scripts/parallel_execute.py:496` | In the same detached scratch, changed executor workflow predicate `version != 2` to `version != 1`. | KILLED: `python3 tools/test_parallel_executor.py` exited 1 because v2 workflow snapshots were rejected. |

**Sensor depth**: lightweight, two behavior mutations covering both changed consumer predicates.
**Isolation**: scratch `/tmp/mas-qa1-verifier.zhPoT6` removed; pre-sensor and post-cleanup real-tree porcelain were identical and clean.
**Result**: 2/2 killed; 0 survived.

## Edge Cases

- Exact `yes`: `tools/test_tlc_validators.py:140` through `tools/test_tlc_validators.py:144` reject `no`, empty, `Yes`, and `true`, naming slice `A`.
- Duplicate closure IDs: `tools/test_tlc_validators.py:175` rejects duplicate `A`.
- Zero/negative assertions: `tools/test_workflow_config.py:210` through `tools/test_workflow_config.py:225` reject both before write.
- Frozen resume and refresh: `tools/test_workflow_config.py:309` through `tools/test_workflow_config.py:346` cover changed Tasks, byte preservation, re-derivation, and schema stability.
- Version boundary: planner and executor reject v1 at `tools/test_parallel_plan.py:370` and `tools/test_parallel_executor.py:120`; pilot rejects v1 and a stale Git head at `tools/test_qa_parallel_pilot.py:168`.

## Gate Check

- `python3 tools/test_tlc_validators.py`: 17 passed, 0 failed, 0 skipped.
- `python3 tools/test_workflow_config.py`: 54 passed, 0 failed, 0 skipped.
- `python3 tools/test_parallel_plan.py`: 20 passed, 0 failed, 0 skipped.
- `python3 tools/test_parallel_executor.py`: 46 passed, 0 failed, 0 skipped.
- `python3 tools/test_qa_parallel_pilot.py`: 13 passed, 0 failed, 0 skipped.
- `python3 scripts/test_adopt.py`: passed (`ok`).
- `npm run test:all`: 383 passed (116 Bun + 267 Python), 0 failed, 0 skipped.
- Prior recorded full-gate baseline at verified head `802aea9`: 380 passed; current delta: +3 tests.
- `git diff --check`: passed.
- Pre-sensor and post-sensor real-tree porcelain: identical and clean.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum implementation and no new dependency | PASS |
| Surgical feature scope and existing patterns | PASS |
| Fail-before-write ordering and byte preservation | PASS |
| Spec-anchored outcome assertions | FAIL: MAS-01's three-cohort input is absent. |
| Per-layer contract coverage | FAIL: MAS-UT-001 exercises one cohort, not three. |
| Every in-scope test is claimed | PASS |
| Guidelines | PASS: `docs/guidelines/TEST-CONTRACT.md`, `docs/guidelines/REVIEW-ROUNDS.md`, `docs/guidelines/VERIFICATION-EVIDENCE.md`, and TLC `references/validate.md`. |

## Protocol Boundary Check

- Active workflow snapshots are v2: `.agents/skills/workflow-config/scripts/parallel_plan.py:46` and `.agents/skills/autonomous/scripts/parallel_execute.py:496` reject every other version.
- Plan, runtime state, and executor result schemas remain v1 at `.agents/skills/workflow-config/scripts/parallel_plan.py:226`, `.agents/skills/autonomous/scripts/parallel_execute.py:86`, and `.agents/skills/autonomous/scripts/parallel_execute.py:417`.
- Pilot lifecycle remains v1, asserted at `tools/test_qa_parallel_pilot.py:134`.
- `git diff --exit-code 459ece2..100f963 -- '.specs/features/*/workflow.json'` passed: all tracked historical workflow snapshots are byte-unchanged.

## Ranked Gaps

1. MAS-01 / MAS-UT-001 — `tools/fixtures/tlc-validator/merge-alone-one-slice.md:17` contains one phase/cohort although the contract requires three. Add three technical cohorts around the same five primary tasks and keep the exact one-slice assertions. This must fail if phase/cohort count owns slice count.

## Summary

**Overall**: FAIL — QA1's v2 consumer hard cut is verified, but the feature cannot close with the
MAS-01/MAS-UT-001 discrimination gap.

**Spec-anchored check**: 12/13 ACs matched; 1 gap.
**Test contract**: 18/19 rows matched; 1 gap.
**Sensor**: 2/2 killed; 0 survived.
**Gate**: 383/383 passed; 0 failed; 0 skipped.

QA1 is independently verified. Next workflow stage is remediation of MAS-01/MAS-UT-001 followed by
fresh Technical Verification; QA Execute retest remains after a PASS.

## R3 Implementation Check

R3 replaces the one-cohort Praxis fixture with exactly three technical phase headings around the
same five primary tasks and one closure. `tools/test_tlc_validators.py` now asserts the 3/5/1
boundary, and the MAS-IT-001 resolver coverage consumes that fixture while still deriving one
slice. This is implementation evidence only; the prior overall FAIL remains pending fresh
independent Technical Verification.
