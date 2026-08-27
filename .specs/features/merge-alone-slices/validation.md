# Merge-Alone Slice Derivation Validation

**Date**: 2026-08-27
**Spec**: `.specs/features/merge-alone-slices/spec.md`
**Diff range**: `d0dd82d..HEAD`
**Verified head**: `babc616`
**Verifier**: fresh independent Technical Re-Verifier (author != verifier)
**Verdict**: FAIL

## Task Completion

| Task | Status | Evidence |
| --- | --- | --- |
| T1 | Done | `tools/test_tlc_validators.py:98` and `tools/test_parallel_plan.py:89`; targeted gates passed 16/16 and 19/19. |
| T2 | Done | `tools/test_workflow_config.py:174`; resolver gate passed 54/54. |
| T3 | Done | `tools/test_workflow_config.py:308`; frozen resume and refresh lifecycle assertions pass. |
| T4 | Done | `tools/shared/tests/workflow-config.test.ts:42`; Bun gate passed 116/116. |
| T5 | Done | `package.json:12`; full gate passed 380/380. |
| R1 | Partial | `babc616` closes four prior fingerprints and most error identities, but exact-`yes` rejection still does not assert the offending slice identity required by MAS-03. |

## Spec-Anchored Acceptance Criteria

All 11 acceptance criteria were independently re-derived. Ten have complete assertion evidence; one
retains an evidence-or-zero gap.

| AC | Spec-defined outcome | `file:line` + assertion evidence | Result |
| --- | --- | --- | --- |
| MAS-01 | Five primary tasks and one closure derive exactly one slice. | `tools/test_tlc_validators.py:101` - `self.assertEqual(contract["slice_ids"], ["A"])`; `tools/test_tlc_validators.py:102` - `self.assertEqual(len(contract["task_slices"]), 5)`; `tools/test_workflow_config.py:179` - `assert snapshot["deep_review"]["groups"] == [[1]]` | PASS |
| MAS-02 | Two merge-alone outcomes derive exactly two slices. | `tools/test_tlc_validators.py:113` - `self.assertEqual(contract["slice_ids"], ["A", "B"])`; `tools/test_workflow_config.py:189` - `assert snapshot["deep_review"]["groups"] == [[1, 2]]` | PASS |
| MAS-03 | Empty outcome/gate/reason or a non-exact-`yes` decision fails and names the invalid slice. | `tools/test_tlc_validators.py:122`, `:126`, `:130`, and `:134` assert slice `A` for empty fields. `tools/test_tlc_validators.py:140`-`:144` rejects `no`, empty, `Yes`, and `true`, but asserts only `exact lowercase yes`; it never asserts slice `A`. Implementation includes the identity at `.agents/skills/tlc-spec-driven/scripts/validate_tasks.py:181`, but evidence-or-zero requires a test assertion. | GAP |
| MAS-04 | Zero/multiple/unknown membership and orphan/duplicate closures fail while naming the inconsistent task or slice. | `tools/test_tlc_validators.py:152`, `:159`, `:163`, and `:168` require `T1` or `Z`; `tools/test_tlc_validators.py:175` and `:178` require duplicate `A` and orphan `B`. | PASS |
| MAS-05 | Initial and refresh count mismatches fail before snapshot creation or byte replacement; non-positive assertions fail. | `tools/test_workflow_config.py:201` and `:204` assert initial mismatch and absence; `tools/test_workflow_config.py:250` and `:253` assert refresh mismatch and byte equality; `tools/test_workflow_config.py:210`, `:222`, and `:225` assert both `0` and `-1` fail before write. | PASS |
| MAS-06 | Missing `tasks.md` derives exactly one slice. | `tools/test_workflow_config.py:287` - `assert snapshot["deep_review"]["groups"] == [[1]]` | PASS |
| MAS-07 | Malformed present Tasks fail before snapshot creation or replacement. | `tools/test_workflow_config.py:299`-`:303` assert named initial failure and no file; `tools/test_workflow_config.py:274`-`:278` assert named refresh failure and byte-for-byte preservation. | PASS |
| MAS-08 | Normal resume returns frozen state without deriving from changed or malformed Tasks. | `tools/test_workflow_config.py:309`-`:324` exercises both changed-valid and malformed Tasks, then asserts `resumed == first` and snapshot bytes unchanged. | PASS |
| MAS-09 | Published planning contract distinguishes slice, phase/cohort, and batch, with count derived from validated Tasks. | `tools/shared/tests/workflow-config.test.ts:50`-`:62` asserts closure/task fields, all three unit definitions, derived ownership, optional assertion wording, and removal of manual-count examples. | PASS |
| MAS-10 | Both `T2R1` and `TDR1` stay outside primary membership/count. | `tools/test_tlc_validators.py:110`-`:114` asserts both headings exist while the contract remains exactly four primary tasks across `A` and `B`; fixture identities are at `tools/fixtures/tlc-validator/merge-alone-two-slices.md:64` and `:71`. | PASS |
| MAS-11 | Validator and parallel planner use identical primary-task membership and slice IDs. | `tools/test_parallel_plan.py:100`-`:110` obtains both outputs from the same task document and directly asserts `planned_membership == contract["task_slices"]`, with planner slices exactly `["A", "B"]`. | PASS |

**Status**: 10/11 matched; 1 assertion gap.

## Test Contract

All 16 canonical contract rows match their stated expected outcomes. MAS-UT-004 itself requires exact
`yes` rejection but does not carry MAS-03's additional error-identity outcome, leaving the spec-level
gap above despite contract-row parity.

| Contract | `file:line` + assertion evidence | Result |
| --- | --- | --- |
| MAS-UT-001 | `tools/test_tlc_validators.py:101`-`:105` asserts `A`, five memberships, all `A`, merge-alone true, and validator success. | PASS |
| MAS-UT-002 | `tools/test_tlc_validators.py:113`-`:114` asserts exactly `A`, `B` and exact primary membership. | PASS |
| MAS-UT-003 | `tools/test_tlc_validators.py:119`-`:135` asserts slice `A` plus each missing field identity. | PASS |
| MAS-UT-004 | `tools/test_tlc_validators.py:140`-`:144` rejects `no`, empty, `Yes`, and `true` with `exact lowercase yes`. | PASS |
| MAS-UT-005 | `tools/test_tlc_validators.py:149`-`:169` asserts zero, multiple, and unknown membership with `T1` or `Z` identity. | PASS |
| MAS-UT-006 | `tools/test_tlc_validators.py:175`-`:179` asserts duplicate `A` and orphan `B`. | PASS |
| MAS-UT-007 | `tools/test_tlc_validators.py:110`-`:114` asserts `T2R1`, `TDR1`, and unchanged exact primary membership/count. | PASS |
| MAS-IT-001 | `tools/test_workflow_config.py:179` asserts groups exactly `[[1]]`. | PASS |
| MAS-IT-002 | `tools/test_workflow_config.py:189` asserts groups exactly `[[1, 2]]`. | PASS |
| MAS-IT-003 | `tools/test_workflow_config.py:201`-`:204` asserts initial mismatch/no file; `:250`-`:253` asserts refresh mismatch/unchanged bytes. | PASS |
| MAS-IT-004 | `tools/test_workflow_config.py:287` asserts missing Tasks yields exactly `[[1]]`. | PASS |
| MAS-IT-005 | `tools/test_workflow_config.py:299`-`:303` asserts malformed closure failure and no snapshot. | PASS |
| MAS-IT-006 | `tools/test_workflow_config.py:309`-`:324` asserts unchanged frozen object and bytes for changed-valid and malformed Tasks. | PASS |
| MAS-IT-007 | `tools/test_workflow_config.py:339`-`:346` asserts refresh derives and persists `[[1, 2]]` without schema/version change. | PASS |
| MAS-IT-008 | `tools/test_parallel_plan.py:100`-`:110` directly compares planner membership with validator output from the same document. | PASS |
| MAS-IT-009 | `tools/shared/tests/workflow-config.test.ts:50`-`:62` asserts the published vocabulary and resolver ownership contract. | PASS |

**Status**: 16/16 matched; 0 contract-row gaps.

## Prior Fingerprint Re-check

| Fingerprint | Current evidence | Result |
| --- | --- | --- |
| Error identities (`1f53e6...`) | Empty fields, membership, duplicate, and orphan identities are pinned; exact-`yes` rejection omits asserted slice identity at `tools/test_tlc_validators.py:143`. | PARTIAL / STILL OPEN |
| Refresh byte preservation (`4af4d6...`) | `tools/test_workflow_config.py:253` and `:278` directly assert unchanged bytes after mismatch and malformed refresh. | CLOSED BY EVIDENCE |
| `T2R1` / `TDR1` (`bc169e...`) | `tools/test_tlc_validators.py:110`-`:114` asserts both shapes and exact unchanged primary membership. | CLOSED BY EVIDENCE |
| Direct validator/planner equality (`c988fe...`) | `tools/test_parallel_plan.py:110` directly compares outputs produced from the same document. | CLOSED BY EVIDENCE |
| Zero/negative assertions (`0ea676...`) | `tools/test_workflow_config.py:210`-`:225` explicitly tests `0` and `-1`, named failure, and no snapshot. | CLOSED BY EVIDENCE |

The remaining gap has the same MAS-03/error-identity root cause and failure path recorded after
`c49b3c6`; `babc616` is a second failed remediation result for that immutable fingerprint. This
report does not edit the separately owned accounting file.

## Discrimination Sensor

| Mutation | File:line | Description | Result |
| --- | --- | --- | --- |
| 1 | `.agents/skills/tlc-spec-driven/scripts/validate_tasks.py:180` | In detached scratch worktree, changed exact-`yes` guard from `merge_alone != "yes"` to allow both `yes` and `no`. | KILLED: `tools/test_tlc_validators.py:143` failed with `AssertionError: ValueError not raised`; 15 passed, 1 failed. |

**Sensor depth**: lightweight, exactly one behavior mutation.
**Isolation**: scratch `/tmp/mas-reverify.8snzEp` removed; post-cleanup real-tree porcelain matched the
clean pre-sensor baseline.
**Result**: 1/1 killed; 0 survived.

## Edge Cases

- Exact `yes`: `tools/test_tlc_validators.py:140`-`:144` rejects `no`, empty, `Yes`, and `true`.
- Duplicate closure IDs: `tools/test_tlc_validators.py:175` rejects duplicate `A`.
- Zero/negative assertions: `tools/test_workflow_config.py:210`-`:225` rejects both before write.
- Frozen resume and refresh: `tools/test_workflow_config.py:309`-`:346` covers changed Tasks, byte preservation, re-derivation, and schema stability.

## Gate Check

- `python3 tools/test_tlc_validators.py`: 16 passed, 0 failed, 0 skipped.
- `python3 tools/test_workflow_config.py`: 54 passed, 0 failed, 0 skipped.
- `python3 tools/test_parallel_plan.py`: 19 passed, 0 failed, 0 skipped.
- `npm run test:all`: 380 passed (116 Bun + 264 Python), 0 failed, 0 skipped.
- Previous recorded `c49b3c6` full gate: 378 passed; current delta: +2 net tests.
- `git diff --check d0dd82d..HEAD`: passed.
- Pre-sensor and post-sensor real-tree porcelain: identical and clean.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum implementation and no new dependency | PASS |
| Surgical feature scope and existing patterns | PASS |
| Fail-before-write ordering and byte preservation | PASS |
| Spec-anchored outcome assertions | FAIL: exact-`yes` error path does not assert slice identity required by MAS-03. |
| Per-layer contract coverage | PASS: all 16 canonical rows have direct assertions. |
| Every in-scope test is claimed | PASS |
| Guidelines | PASS: `docs/guidelines/TEST-CONTRACT.md`, `docs/guidelines/REVIEW-ROUNDS.md`, `docs/guidelines/VERIFICATION-EVIDENCE.md`, and TLC `references/validate.md`. |

## Ranked Gaps

1. **Major — MAS-03 error identity remains unpinned.** Premise: `tools/test_tlc_validators.py:143`
   matches only `exact lowercase yes`. Path: the validator can regress to an identity-free or wrong-slice
   exact-`yes` error while all current tests remain green, leaving the operator without the invalid
   slice named by the spec. Verdict: extend the assertion to require both slice `A` and exact-`yes`
   identity for every invalid decision value.

## Summary

**Overall**: FAIL — full gate and sensor pass, and all 16 test-contract rows match, but evidence-or-zero
does not support MAS-03's full error-identity outcome.

**Spec-anchored check**: 10/11 ACs matched; 1 gap.
**Test contract**: 16/16 rows matched; 0 gaps.
**Sensor**: 1/1 killed.
**Gate**: 380/380 passed.
