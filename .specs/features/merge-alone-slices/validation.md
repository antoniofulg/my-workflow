# Merge-Alone Slice Derivation Validation

**Date**: 2026-08-27
**Spec**: `.specs/features/merge-alone-slices/spec.md`
**Diff range**: `d0dd82d..HEAD`
**Verifier**: independent sub-agent (author != verifier)
**Verdict**: FAIL

## Task Completion

| Task | Status | Evidence |
| --- | --- | --- |
| T1 | Done | `tools/test_tlc_validators.py:98` and `tools/test_parallel_plan.py:87`; scoped gates passed 16/16 and 19/19. |
| T2 | Done | `tools/test_workflow_config.py:174`; resolver gate passed 51/51. |
| T3 | Done | `tools/test_workflow_config.py:234`; resolver gate passed 51/51. |
| T4 | Done | `tools/shared/tests/workflow-config.test.ts:42`; Bun gate passed 116/116. |
| T5 | Done | `package.json:9` full gate passed 378/378. |

## Spec-Anchored Acceptance Criteria

All 11 acceptance criteria were evaluated. Six match their complete spec-defined outcome; five have
assertion gaps.

| AC | Spec-defined outcome | `file:line` + assertion evidence | Result |
| --- | --- | --- | --- |
| MAS-01 | Five primary tasks and one closure derive one slice. | `tools/test_tlc_validators.py:101` - `self.assertEqual(contract["slice_ids"], ["A"])`; `tools/test_workflow_config.py:179` - `assert snapshot["deep_review"]["groups"] == [[1]]` | PASS |
| MAS-02 | Two merge-alone outcomes derive two slices. | `tools/test_tlc_validators.py:109` - `self.assertEqual(contract["slice_ids"], ["A", "B"])`; `tools/test_workflow_config.py:189` - `assert snapshot["deep_review"]["groups"] == [[1, 2]]` | PASS |
| MAS-03 | Each incomplete field fails and the error names the invalid slice. | `tools/test_tlc_validators.py:121` - `assertRaisesRegex(ValueError, expected)` checks only the field label, not slice `A`. | GAP |
| MAS-04 | Zero/multiple/unknown membership and orphan slices fail while naming the inconsistent task or slice. | `tools/test_tlc_validators.py:143` - only the missing-field case requires `T1`; duplicate/unknown cases omit the task/slice identity. `tools/test_tlc_validators.py:153` omits orphan slice `B`. | GAP |
| MAS-05 | Initial and refresh count mismatches fail before create or replacement. | `tools/test_workflow_config.py:201` and `tools/test_workflow_config.py:204` prove only initial mismatch and absence of a new snapshot; no refresh mismatch preserves an existing snapshot byte-for-byte. | GAP |
| MAS-06 | Missing `tasks.md` derives exactly one slice. | `tools/test_workflow_config.py:213` - `assert snapshot["deep_review"]["groups"] == [[1]]` | PASS |
| MAS-07 | Malformed present Tasks fail before create or replacement. | `tools/test_workflow_config.py:225` and `tools/test_workflow_config.py:229` prove the create path only; no malformed refresh assertion protects an existing snapshot from replacement. | GAP |
| MAS-08 | Normal resume returns the frozen snapshot without reading changed or malformed Tasks. | `tools/test_workflow_config.py:235`, `tools/test_workflow_config.py:249`, and `tools/test_workflow_config.py:250` exercise valid two-slice and malformed current Tasks and assert object and bytes unchanged. | PASS |
| MAS-09 | Published template distinguishes slice, phase/cohort, and batch. | `tools/shared/tests/workflow-config.test.ts:50` through `tools/shared/tests/workflow-config.test.ts:59` assert closure, task slice, and all three unit definitions. | PASS |
| MAS-10 | `T2R1` and `TDR1` remediation records stay outside primary slice count. | `tools/test_tlc_validators.py:110` proves four primary tasks only, but fixture `tools/fixtures/tlc-validator/merge-alone-two-slices.md:64` contains only `TDR1`; `T2R1` is not exercised. | GAP |
| MAS-11 | Resolver and parallel planner share validated membership and slice IDs. | `tools/test_tlc_validators.py:110` asserts validator membership; `tools/test_parallel_plan.py:98` and `tools/test_parallel_plan.py:99` assert planner output from a separate handcrafted input, not equality to validator output. | GAP |

**Status**: 6/11 matched; 5 assertion gaps.

## Test Contract

All 16 contract rows were evaluated. Ten match their complete expected outcome; six have assertion
gaps.

| Contract | `file:line` + assertion evidence | Result |
| --- | --- | --- |
| MAS-UT-001 | `tools/test_tlc_validators.py:101`-`105` asserts slice `A`, five memberships, all `A`, merge-alone true, and validator success. | PASS |
| MAS-UT-002 | `tools/test_tlc_validators.py:109`-`110` asserts exactly `A`, `B` and exact primary-task membership. | PASS |
| MAS-UT-003 | `tools/test_tlc_validators.py:115`-`122` asserts missing field names, but never asserts invalid slice `A`. | GAP |
| MAS-UT-004 | `tools/test_tlc_validators.py:127`-`131` rejects `no`, empty, `Yes`, and `true` with `exact lowercase yes`. | PASS |
| MAS-UT-005 | `tools/test_tlc_validators.py:136`-`144` covers zero, multiple, and unknown membership, but duplicate/unknown assertions do not require the inconsistent task or slice identity. | GAP |
| MAS-UT-006 | `tools/test_tlc_validators.py:150` asserts duplicate `A`; `tools/test_tlc_validators.py:153` asserts an orphan error but not orphan slice `B`. | GAP |
| MAS-UT-007 | `tools/test_tlc_validators.py:110` proves remediation exclusion only for fixture `tools/fixtures/tlc-validator/merge-alone-two-slices.md:64` containing `TDR1`; required `T2R1` is absent. | GAP |
| MAS-IT-001 | `tools/test_workflow_config.py:179` asserts groups exactly `[[1]]`. | PASS |
| MAS-IT-002 | `tools/test_workflow_config.py:189` asserts groups exactly `[[1, 2]]`. | PASS |
| MAS-IT-003 | `tools/test_workflow_config.py:201`-`204` proves initial mismatch and no snapshot; refresh mismatch and byte-for-byte preservation are unasserted. | GAP |
| MAS-IT-004 | `tools/test_workflow_config.py:213` asserts missing Tasks yields exactly `[[1]]`. | PASS |
| MAS-IT-005 | `tools/test_workflow_config.py:225`-`229` asserts malformed closure failure and no snapshot. | PASS |
| MAS-IT-006 | `tools/test_workflow_config.py:235`-`250` asserts frozen result and bytes for changed valid and malformed Tasks. | PASS |
| MAS-IT-007 | `tools/test_workflow_config.py:265`-`272` asserts refresh derives `[[1, 2]]`, persists it, and preserves schema/version. | PASS |
| MAS-IT-008 | `tools/test_parallel_plan.py:98`-`99` asserts planner slices/tasks, but never compares them to validator-produced membership as required. | GAP |
| MAS-IT-009 | `tools/shared/tests/workflow-config.test.ts:50`-`62` asserts published unit vocabulary and removal of manual count ownership. | PASS |

**Status**: 10/16 matched; 6 assertion gaps.

## Discrimination Sensor

| Mutation | File:line | Description | Result |
| --- | --- | --- | --- |
| 1 | `.agents/skills/tlc-spec-driven/scripts/validate_tasks.py:180` | In isolated worktree, allowed `no` by changing exact-`yes` rejection to reject only values outside `yes/no`. | KILLED: `tools/test_tlc_validators.py:130` failed with `AssertionError: ValueError not raised`. |

**Sensor depth**: lightweight, exactly one highest-risk fail-closed behavior mutation.
**Result**: 1/1 killed; scratch worktree removed; real-tree porcelain matched the clean baseline.

## Edge Cases

- Exact `yes` values: covered, including `no`, empty, `Yes`, and `true` rejection.
- Duplicate closure IDs: covered.
- Zero/negative `--slices`: implementation rejects at `.agents/skills/workflow-config/scripts/workflow_config.py:790`, but no scoped test assertion was found.
- Frozen resume and explicit refresh after task changes: covered.

## Gate Check

- `python3 tools/test_tlc_validators.py`: 16 passed, 0 failed, 0 skipped.
- `python3 tools/test_workflow_config.py`: 51 passed, 0 failed, 0 skipped.
- `python3 tools/test_parallel_plan.py`: 19 passed, 0 failed, 0 skipped.
- `npm run test:all`: 378 passed (116 Bun + 262 Python), 0 failed, 0 skipped.
- `git diff --check d0dd82d..HEAD`: passed.
- Pre-sensor and post-sensor real-tree porcelain: identical and clean.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum implementation and no new dependency | PASS |
| Surgical feature scope and existing patterns | PASS |
| Fail-before-write ordering | PASS |
| Spec-anchored outcome assertions | FAIL: six contract rows are incomplete. |
| Per-layer coverage | FAIL: refresh failure atomicity and cross-component membership equality lack direct assertions. |
| Every in-scope test is claimed | PASS |
| Guidelines | PASS: `docs/guidelines/TEST-CONTRACT.md`, `docs/guidelines/VERIFICATION-EVIDENCE.md`, and TLC `references/validate.md`. |

## Ranked Gaps

1. Add refresh-path mismatch and malformed-contract tests that begin with an existing snapshot and assert its bytes remain unchanged (MAS-05, MAS-07, MAS-IT-003).
2. Make closure-field and membership error assertions require both defect and offending task/slice identity (MAS-03, MAS-04, MAS-UT-003, MAS-UT-005, MAS-UT-006).
3. Exercise both `T2R1` and `TDR1` remediation shapes and assert unchanged primary membership/count (MAS-10, MAS-UT-007).
4. Feed validator-produced membership into parallel planning, then assert exact equality rather than parallel expectations from a separate handcrafted document (MAS-11, MAS-IT-008).
5. Add zero and negative optional count assertions to pin the listed edge case.

## Summary

**Overall**: FAIL - implementation gates and mutation sensor pass, but evidence-or-zero validation
does not support a complete feature verdict.

**Spec-anchored check**: 6/11 ACs matched; 5 gaps.
**Test contract**: 10/16 rows matched; 6 gaps.
**Sensor**: 1/1 killed.
**Gate**: 378/378 passed.
