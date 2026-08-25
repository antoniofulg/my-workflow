# Stall-Based Remediation Halt Validation

**Date**: 2026-08-25
**Spec**: `.specs/features/stall-based-remediation-halt/spec.md`
**Diff range**: `70e447d31a8ada5db874bd62743b962c87968596..997ba25bb221a63385bee967115a85c49a5a6512`
**Verifier**: independent Verifier (author != verifier)
**Verdict**: PASS

## Diff Audit

- Branch: `fix/stall-based-remediation-halt`
- Range: 3 commits, 11 files, 320 insertions, 20 deletions.
- Final remediation commit: `997ba25` (`test(review): cover remediation stall boundaries`), 2 test files, 5 insertions.
- Real checkout porcelain before sensors: `?? .specs/features/stall-based-remediation-halt/validation.md`.
- Real checkout porcelain after scratch cleanup and report replacement: same single untracked path.

## Spec-Anchored Acceptance Criteria

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| 1 / SRH-01 | Accept only integers >= 0; default to `3` | `tools/test_workflow_config.py:837` - `test_resolves_remediation_stall_attempts_without_snapshot_persistence`; `tools/test_workflow_config.py:839`-`tools/test_workflow_config.py:852` - exact default `3`, positive `5`, zero `0`; `tools/test_workflow_config.py:861`-`tools/test_workflow_config.py:883` - string, boolean, TOML float, negative, and unknown-key inputs reject and `assert not ... workflow.json.exists()` | PASS |
| 2 / SRH-01 | `0` is unbounded | `tools/test_workflow_config.py:841`-`tools/test_workflow_config.py:852` - resolver emits `0`; `tools/shared/tests/qa-skills.test.ts:284` - `expect(remediation).toContain("`stall_attempts = 0` is unbounded")` | PASS |
| 3 / SRH-02 | Resolve and resume emit live threshold without persisting it | `tools/test_workflow_config.py:852`-`tools/test_workflow_config.py:856` - exact emitted value and absent persisted key; `tools/test_workflow_config.py:888`-`tools/test_workflow_config.py:909` - resume emits `7`, preserves every frozen field, and preserves snapshot bytes | PASS |
| 4 / SRH-03 | Each attempt runs scoped gate, then derives a stable sorted identifier signature with volatile data removed | `tools/shared/tests/qa-skills.test.ts:275`-`tools/shared/tests/qa-skills.test.ts:278` - exact gate and normalization text; `tools/shared/tests/qa-skills.test.ts:292`-`tools/shared/tests/qa-skills.test.ts:296` - gate precedes signature derivation | PASS |
| 5 / SRH-03 | Only a strict subset of running minimum resets stalls and continues | `tools/shared/tests/qa-skills.test.ts:279`-`tools/shared/tests/qa-skills.test.ts:281` - exact strict-subset reset; `tools/shared/tests/qa-skills.test.ts:295`-`tools/shared/tests/qa-skills.test.ts:300` - signature, progress, then halt ordering | PASS |
| 6 / SRH-03 | Any non-minimum increments stalls, including equal-size changed membership and larger sets | `tools/shared/tests/qa-skills.test.ts:282`-`tools/shared/tests/qa-skills.test.ts:283` - exact equal-size changed-membership and larger-set increment assertions; `tools/shared/tests/qa-skills.test.ts:301`-`tools/shared/tests/qa-skills.test.ts:303` - larger-set rule follows strict-subset rule | PASS |
| 7 / SRH-04 | Reached nonzero threshold halts with repeated signature, attempt count, and fixes tried | `tools/shared/tests/qa-skills.test.ts:284`-`tools/shared/tests/qa-skills.test.ts:287` - exact zero polarity and halt payload; `tools/shared/tests/qa-skills.test.ts:298`-`tools/shared/tests/qa-skills.test.ts:300` - threshold check follows progress check | PASS |
| 8 / SRH-05 | Unavailable scoped gate halts immediately and opens no review round | `tools/shared/tests/qa-skills.test.ts:288`-`tools/shared/tests/qa-skills.test.ts:290` - exact halt/no-round contract | PASS |
| 9 / SRH-05 | Existing loop never starts review round three | `tools/shared/tests/qa-skills.test.ts:291` - exact post-cap assertion; `tools/shared/tests/qa-skills.test.ts:324`-`tools/shared/tests/qa-skills.test.ts:354` - approved-loop anchors and order enforce correction, no round 3, then escalation | PASS |

**Status**: 9/9 ACs match precise spec outcomes with assertion evidence. No spec-precision gaps.

## Edge Cases

- PASS - negative, boolean, TOML float, string, and unknown remediation keys reject before snapshot creation: `tools/test_workflow_config.py:861`-`tools/test_workflow_config.py:883`.
- PASS - equal-size changed membership increments stalls: `tools/shared/tests/qa-skills.test.ts:282`.
- PASS - larger failure sets increment stalls and cannot satisfy the reset rule: `tools/shared/tests/qa-skills.test.ts:279`-`tools/shared/tests/qa-skills.test.ts:283`, ordering at `tools/shared/tests/qa-skills.test.ts:301`-`tools/shared/tests/qa-skills.test.ts:303`.
- PASS - changed live threshold on resume preserves frozen routing, cadence, and exact snapshot bytes: `tools/test_workflow_config.py:888`-`tools/test_workflow_config.py:909`.

## Implementation Evidence

- Schema boundary permits only `stall_attempts` and requires exact `int` type >= 0: `.agents/skills/workflow-config/scripts/workflow_config.py:167`-`.agents/skills/workflow-config/scripts/workflow_config.py:177`.
- Resolver derives the live value before resume and attaches it only to returned data: `.agents/skills/workflow-config/scripts/workflow_config.py:688`-`.agents/skills/workflow-config/scripts/workflow_config.py:699`.
- Persisted snapshot omits remediation while resolved output includes it: `.agents/skills/workflow-config/scripts/workflow_config.py:736`-`.agents/skills/workflow-config/scripts/workflow_config.py:747`.
- Canonical post-cap behavior is the docs-as-interface product contract: `docs/guidelines/REVIEW-ROUNDS.md:148`-`docs/guidelines/REVIEW-ROUNDS.md:149`.

## Discrimination Sensor

Detached temporary worktrees at `997ba25` contained every mutation. Each mutation was restored before the next run. Resolver mutants used `python3 tools/test_workflow_config.py`; contract mutants used `npx vitest run tools/shared/tests/qa-skills.test.ts`. Scratch worktrees were removed. Real porcelain matched the pre-sensor baseline.

| # | Mutation class | Result |
| --- | --- | --- |
| M01 | Default `3` -> `4` | KILLED |
| M02 | Accept booleans through `isinstance(..., int)` | KILLED |
| M03 | Remove negative-value rejection | KILLED |
| M04 | Persist `remediation` in `workflow.json` | KILLED |
| M05 | Resume reports default instead of current threshold | KILLED |
| M06 | Bypass resume short-circuit and re-resolve frozen route/cadence | KILLED |
| M07 | Reset on a not-larger set instead of a strict subset | KILLED |
| M08 | Remove equal-size changed-membership rule | KILLED |
| M09 | Use raw unsorted output as signature | KILLED |
| M10 | Make zero halt instead of unbounded | KILLED |
| M11 | Continue/start another round when gate is unavailable | KILLED |
| M12 | Start review round three after cap | KILLED |
| M13 | Omit repeated signature and fixes tried from halt report | KILLED |
| M14 | Reset counter for a larger failing-test set | KILLED at `tools/shared/tests/qa-skills.test.ts:283` |
| M15 | Accept TOML floats while still rejecting booleans, strings, negatives, and unknown keys | KILLED at `tools/test_workflow_config.py:882` for `float` |
| T01 | Weaken larger-set outcome to “does not reset” without requiring increment | KILLED at `tools/shared/tests/qa-skills.test.ts:283` |
| T02 | Broad numeric coercion accepts TOML floats (and booleans) | KILLED |

**Sensor result**: 17/17 killed, 0 survived - PASS.

## Gate Check

- Focused resolver: `python3 tools/test_workflow_config.py` - 37 passed, 0 failed.
- Focused docs-as-interface contract: `npx vitest run tools/shared/tests/qa-skills.test.ts` - 23 passed, 0 failed.
- Full current gate: `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py && git diff --check 70e447d..997ba25 && git diff --check` - 108 Vitest + 18 adoption (`rg -c '^def test_' scripts/test_adopt.py`) + 37 resolver = 163 passed, 0 failed, 0 skipped; both diff checks passed.
- Pre-feature detached gate at `70e447d`: `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py` - 108 Vitest + 18 adoption + 34 resolver = 160 passed, 0 failed.
- Test delta: +3 resolver tests; no decrease.

## Code Quality

- Minimum and surgical: PASS. One schema field, one live resolved field, no snapshot migration or compatibility layer.
- Scope and established patterns: PASS across 11 changed files.
- Owning layers: PASS. Resolver behavior is covered in its canonical Python suite; workflow policy is a docs-as-interface contract covered in the canonical QA-skills suite.
- Test contract: PASS under `docs/guidelines/TEST-CONTRACT.md:45`-`docs/guidelines/TEST-CONTRACT.md:55` and the docs-as-product exception at `docs/guidelines/TEST-CONTRACT.md:79`-`docs/guidelines/TEST-CONTRACT.md:85`; exact inputs and outcomes are asserted, including both former gaps.
- No unclaimed changed tests, weakened assertions, unrelated improvements, or scope creep found.

## Requirement Traceability

| Requirement | Verification |
| --- | --- |
| SRH-01 | VERIFIED |
| SRH-02 | VERIFIED |
| SRH-03 | VERIFIED |
| SRH-04 | VERIFIED |
| SRH-05 | VERIFIED |

## Ranked Gaps

None. No Blocker or Major findings.

## Summary

**Overall**: READY

All 9 ACs and listed edges have precise assertion evidence. Both prior gaps are closed. All 17 mutation probes were killed, including larger-set reset/no-reset weakening and float-only acceptance. Focused suites, full current gate, pre-feature baseline gate, and diff checks pass.
