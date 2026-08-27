# Merge-Alone Slice Derivation Validation

**Date**: 2026-08-27
**Spec**: `.specs/features/merge-alone-slices/spec.md`
**Diff range**: `d0dd82d..HEAD`
**Verified head**: `802aea9c27ca39e1b50cdd9f5149e96b59d5809f`
**Verifier**: fresh independent Technical Verifier (author != verifier)
**Verdict**: PASS

## Task Completion

| Task | Status | Evidence |
| --- | --- | --- |
| T1 | Done | `tools/test_tlc_validators.py:98`; validator 16/16 and planner 19/19 passed. |
| T2 | Done | `tools/test_workflow_config.py:174`; resolver 54/54 passed. |
| T3 | Done | `tools/test_workflow_config.py:308`; resume and refresh assertions passed. |
| T4 | Done | `tools/shared/tests/workflow-config.test.ts:42`; Bun 116/116 passed. |
| T5 | Done | `package.json:12`; full gate 380/380 passed. |
| R1 | Done | `tools/test_workflow_config.py:230` and `tools/test_parallel_plan.py:89`; prior atomicity and membership gaps remain closed. |
| R2 | Done | `tools/test_tlc_validators.py:143`; every invalid merge-alone value requires slice `A` and exact lowercase `yes`. |

## Spec-Anchored Acceptance Criteria

All 11 acceptance criteria match their exact spec-defined outcomes.

| AC | Spec-defined outcome | `file:line` + assertion evidence | Result |
| --- | --- | --- | --- |
| MAS-01 | Five primary tasks and one closure derive exactly one slice. | `tools/test_tlc_validators.py:101` — `self.assertEqual(contract["slice_ids"], ["A"])`; `tools/test_tlc_validators.py:102` — five memberships; `tools/test_workflow_config.py:179` — groups equal `[[1]]`. | PASS |
| MAS-02 | Two merge-alone outcomes derive exactly two slices. | `tools/test_tlc_validators.py:113` — slice IDs equal `["A", "B"]`; `tools/test_workflow_config.py:189` — groups equal `[[1, 2]]`. | PASS |
| MAS-03 | Empty outcome, gate, or reason, and every non-exact-`yes` decision fail while naming invalid slice `A`. | `tools/test_tlc_validators.py:122`, `tools/test_tlc_validators.py:126`, and `tools/test_tlc_validators.py:130` pin empty-field identity; `tools/test_tlc_validators.py:140` tests `no`, empty, `Yes`, and `true`; `tools/test_tlc_validators.py:143` requires `slice 'A'.*exact lowercase yes`. | PASS |
| MAS-04 | Zero, multiple, or unknown membership and orphan or duplicate closures fail while naming inconsistent task or slice. | `tools/test_tlc_validators.py:152`, `tools/test_tlc_validators.py:159`, and `tools/test_tlc_validators.py:163` require `T1` or `Z`; `tools/test_tlc_validators.py:175` and `tools/test_tlc_validators.py:178` require duplicate `A` and orphan `B`. | PASS |
| MAS-05 | Initial and refresh count mismatches fail before snapshot creation or byte replacement; non-positive assertions fail. | `tools/test_workflow_config.py:201` and `tools/test_workflow_config.py:204` pin initial mismatch and absence; `tools/test_workflow_config.py:250` and `tools/test_workflow_config.py:253` pin refresh mismatch and byte equality; `tools/test_workflow_config.py:210` through `tools/test_workflow_config.py:225` reject `0` and `-1` before write. | PASS |
| MAS-06 | Missing `tasks.md` derives exactly one slice. | `tools/test_workflow_config.py:287` — groups equal `[[1]]`. | PASS |
| MAS-07 | Malformed present Tasks fail before snapshot creation or replacement. | `tools/test_workflow_config.py:299` through `tools/test_workflow_config.py:303` assert initial failure and no file; `tools/test_workflow_config.py:274` through `tools/test_workflow_config.py:278` assert refresh failure and unchanged bytes. | PASS |
| MAS-08 | Normal resume returns frozen state without re-deriving changed or malformed Tasks. | `tools/test_workflow_config.py:309` through `tools/test_workflow_config.py:324` exercise both forms and assert object and byte equality. | PASS |
| MAS-09 | Published planning contract distinguishes slice, phase/cohort, and batch, and derives count from validated Tasks. | `tools/shared/tests/workflow-config.test.ts:50` through `tools/shared/tests/workflow-config.test.ts:62` pin closure fields, all three unit definitions, derived ownership, optional assertion wording, and removal of manual-count examples. | PASS |
| MAS-10 | `T2R1` and `TDR1` remain outside primary membership and count. | `tools/test_tlc_validators.py:110` through `tools/test_tlc_validators.py:114` assert both headings while preserving exactly four primary memberships across `A` and `B`; fixture identities appear at `tools/fixtures/tlc-validator/merge-alone-two-slices.md:64` and `tools/fixtures/tlc-validator/merge-alone-two-slices.md:71`. | PASS |
| MAS-11 | Validator and parallel planner use identical primary-task membership and slice IDs. | `tools/test_parallel_plan.py:100` through `tools/test_parallel_plan.py:110` derive both outputs from one document and assert direct equality. | PASS |

**Status**: 11/11 matched; 0 gaps; 0 spec-precision gaps.

## Test Contract

All 16 canonical rows match their stated outcomes.

| Contract | `file:line` + assertion evidence | Result |
| --- | --- | --- |
| MAS-UT-001 | `tools/test_tlc_validators.py:101` through `tools/test_tlc_validators.py:105` assert `A`, five primary memberships, merge-alone true, and validator success. | PASS |
| MAS-UT-002 | `tools/test_tlc_validators.py:113` and `tools/test_tlc_validators.py:114` assert exactly `A`, `B`, and exact membership. | PASS |
| MAS-UT-003 | `tools/test_tlc_validators.py:119` through `tools/test_tlc_validators.py:135` assert slice `A` plus each missing field. | PASS |
| MAS-UT-004 | `tools/test_tlc_validators.py:140` through `tools/test_tlc_validators.py:144` reject `no`, empty, `Yes`, and `true` while requiring slice `A` and exact lowercase `yes`. | PASS |
| MAS-UT-005 | `tools/test_tlc_validators.py:149` through `tools/test_tlc_validators.py:169` assert zero, multiple, and unknown membership with `T1` or `Z`. | PASS |
| MAS-UT-006 | `tools/test_tlc_validators.py:175` through `tools/test_tlc_validators.py:179` assert duplicate `A` and orphan `B`. | PASS |
| MAS-UT-007 | `tools/test_tlc_validators.py:110` through `tools/test_tlc_validators.py:114` assert `T2R1`, `TDR1`, and unchanged primary membership/count. | PASS |
| MAS-IT-001 | `tools/test_workflow_config.py:179` asserts groups exactly `[[1]]`. | PASS |
| MAS-IT-002 | `tools/test_workflow_config.py:189` asserts groups exactly `[[1, 2]]`. | PASS |
| MAS-IT-003 | `tools/test_workflow_config.py:201` through `tools/test_workflow_config.py:204` assert initial mismatch and no file; `tools/test_workflow_config.py:250` through `tools/test_workflow_config.py:253` assert refresh mismatch and unchanged bytes. | PASS |
| MAS-IT-004 | `tools/test_workflow_config.py:287` asserts missing Tasks yields exactly `[[1]]`. | PASS |
| MAS-IT-005 | `tools/test_workflow_config.py:299` through `tools/test_workflow_config.py:303` assert malformed closure failure and no snapshot. | PASS |
| MAS-IT-006 | `tools/test_workflow_config.py:309` through `tools/test_workflow_config.py:324` assert frozen object and bytes for changed-valid and malformed Tasks. | PASS |
| MAS-IT-007 | `tools/test_workflow_config.py:339` through `tools/test_workflow_config.py:346` assert refresh derives and persists `[[1, 2]]` without schema/version change. | PASS |
| MAS-IT-008 | `tools/test_parallel_plan.py:100` through `tools/test_parallel_plan.py:110` directly compare planner membership with validator output from the same document. | PASS |
| MAS-IT-009 | `tools/shared/tests/workflow-config.test.ts:50` through `tools/shared/tests/workflow-config.test.ts:62` assert published vocabulary and resolver ownership. | PASS |

**Status**: 16/16 matched; 0 contract-row gaps.

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
| 1 | `.agents/skills/tlc-spec-driven/scripts/validate_tasks.py:181` | In detached scratch worktree, replaced correct slice identity with `<unknown>` in the exact-lowercase-`yes` error. | KILLED: `tools/test_tlc_validators.py:143` failed because `slice 'A'.*exact lowercase yes` no longer matched; 15 passed, 1 failed. |

**Sensor depth**: lightweight, exactly one behavior mutation.
**Isolation**: scratch `/tmp/mas-final-verifier.PrEtpx` removed; pre-sensor and post-cleanup real-tree porcelain were identical and clean.
**Result**: 1/1 killed; 0 survived.

## Edge Cases

- Exact `yes`: `tools/test_tlc_validators.py:140` through `tools/test_tlc_validators.py:144` reject `no`, empty, `Yes`, and `true`, naming slice `A`.
- Duplicate closure IDs: `tools/test_tlc_validators.py:175` rejects duplicate `A`.
- Zero/negative assertions: `tools/test_workflow_config.py:210` through `tools/test_workflow_config.py:225` reject both before write.
- Frozen resume and refresh: `tools/test_workflow_config.py:309` through `tools/test_workflow_config.py:346` cover changed Tasks, byte preservation, re-derivation, and schema stability.

## Gate Check

- `python3 tools/test_tlc_validators.py`: 16 passed, 0 failed, 0 skipped.
- `python3 tools/test_workflow_config.py`: 54 passed, 0 failed, 0 skipped.
- `python3 tools/test_parallel_plan.py`: 19 passed, 0 failed, 0 skipped.
- `npm run test:all`: 380 passed (116 Bun + 264 Python), 0 failed, 0 skipped.
- Prior recorded full-gate baseline at `c49b3c6`: 378 passed; current delta: +2 net tests.
- `git diff --check d0dd82d..HEAD`: passed.
- Pre-sensor and post-sensor real-tree porcelain: identical and clean.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum implementation and no new dependency | PASS |
| Surgical feature scope and existing patterns | PASS |
| Fail-before-write ordering and byte preservation | PASS |
| Spec-anchored outcome assertions | PASS: 11/11 exact outcomes have assertion evidence. |
| Per-layer contract coverage | PASS: all 16 canonical rows have direct assertions. |
| Every in-scope test is claimed | PASS |
| Guidelines | PASS: `docs/guidelines/TEST-CONTRACT.md`, `docs/guidelines/REVIEW-ROUNDS.md`, `docs/guidelines/VERIFICATION-EVIDENCE.md`, and TLC `references/validate.md`. |

## Ranked Gaps

None.

## Summary

**Overall**: PASS — ready for the next workflow stage.

**Spec-anchored check**: 11/11 ACs matched; 0 gaps.
**Test contract**: 16/16 rows matched; 0 gaps.
**Sensor**: 1/1 killed; 0 survived.
**Gate**: 380/380 passed; 0 failed; 0 skipped.
