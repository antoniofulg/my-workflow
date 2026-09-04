# Right-size UI Corrections Validation

**Verdict**: PASS
**Date**: 2026-09-04
**Spec**: `.specs/features/right-size-ui-corrections/spec.md`
**Diff range**: `eac6938019671e081ece58c151e208f03c2a5d5c^..eac6938019671e081ece58c151e208f03c2a5d5c`
**Verifier**: independent sub-agent (author != verifier)

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| T1: right-size UI classification | Done | Implementation commit `eac69380`; ownership remediation commit `5192eff5`; scoped gates green. |

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| RSG-01 | Exact bounded reuse with no listed risk becomes Direct correction. | `tools/test_phase_skills.py:590` - `assert "one bounded surface" in router`; `tools/test_phase_skills.py:591` - existing/reference assertion; `tools/test_phase_skills.py:592` - complete risk-list loop | PASS |
| RSG-02 | Direct correction uses inspect, implement, scoped validation, one commit, and skips feature ceremony. | `tools/test_phase_skills.py:609` - `assert "without a Verifier, QA Plan/Execute, deep review" in router`; `.agents/skills/workflow-spec-driven/SKILL.md:79` - direct-correction sequence and skipped artifacts | PASS |
| RSG-03 | Planner states tier, decisive facts, and validation layer before dispatch. | `tools/test_phase_skills.py:583` - classification/tier assertion; `tools/test_phase_skills.py:584` - validation-layer assertion; `templates/agents/codex/planner.toml:37` - required output fields | PASS |
| RSG-04 | UI presence alone never selects integration, e2e, or full gate. | `.agents/skills/workflow-spec-driven/SKILL.md:85` - explicit non-escalation rule; `docs/guidelines/GATES.md:15` - UI presence is not escalation evidence | PASS |
| RSG-05 | Missing browser selector chooses narrowest available check, not full e2e. | `tools/test_phase_skills.py:608` - selector assertion; `tools/test_phase_skills.py:615` - absent-selector gate assertion; `tools/test_phase_skills.py:616` - no-full-e2e assertion | PASS |
| RSG-06 | Explicit browser-only invariant uses existing targeted scenario without a QA cycle. | `.agents/skills/workflow-spec-driven/SKILL.md:85` - targeted-scenario rule; `docs/guidelines/QA-SCENARIOS.md:124` - existing owning scenario only | PASS |
| RSG-07 | Named behavior or cross-cutting risk selects smallest feature tier with feature controls. | `tools/test_phase_skills.py:592` - assertions cover journey, state, data/API, auth, persistence, dependency, build, token, and architecture risks; `docs/guidelines/GATES.md:16` - named-evidence escalation | PASS |
| RSG-08 | Requests outside predicate retain existing feature sizing and gates. | `.agents/skills/workflow-spec-driven/SKILL.md:82` - failed predicate routes to smallest feature tier; `docs/guidelines/GATES.md:27` - feature-close full gate remains | PASS |
| RSG-09 | Reused upstream primitives validate project-owned composition, not upstream internals. | `tools/test_phase_skills.py:606` - `assert "do not retest upstream shadcn/TanStack internals" in router`; `.agents/skills/workflow-spec-driven/SKILL.md:85` - composition/wiring rule | PASS |
| RSG-10 | One passing scoped validation closes without more verifier/review rounds. | `tools/test_phase_skills.py:609` - no additional verifier/QA/deep-review assertion; `docs/guidelines/GATES.md:13` - closes after one scoped validation | PASS |
| RSG-11 | Explicit direct/UI-only wording selects fast path only when predicate passes. | `tools/test_phase_skills.py:576` - router and all provider templates loop; `tools/test_phase_skills.py:577` and `tools/test_phase_skills.py:578` - both terms required | PASS |
| RSG-12 | `feature` sets at least Small. | `tools/test_phase_skills.py:587` - exact Small-floor assertion | PASS |
| RSG-13 | `cross-feature change` sets at least Medium and maps promises. | `tools/test_phase_skills.py:586` - exact Medium-floor assertion; `.agents/skills/workflow-spec-driven/SKILL.md:57` - promise-mapping rule | PASS |
| RSG-14 | `issue`, bug, refactor, small/UI change remain neutral. | `tools/test_phase_skills.py:581` - neutral term required across sources; `tools/test_phase_skills.py:619` - review authority asserts issue neutrality | PASS |
| RSG-15 | Contradictory repository evidence is named before escalation. | `tools/test_phase_skills.py:582` - repository-evidence requirement across sources; `.agents/skills/workflow-spec-driven/SKILL.md:56` - name concrete surface before reclassification | PASS |
| RSG-16 | Agreed classification stays unless newly discovered evidence is stated. | `.agents/skills/workflow-spec-driven/SKILL.md:61` - explicit floor preservation and newly discovered named-evidence condition; `templates/agents/codex/planner.toml:50` - named evidence before escalation | PASS |

**Status**: 16/16 criteria match precise spec outcomes; 0 spec-precision gaps.

## Edge Cases

- PASS: unavailable component cannot satisfy the existing-component predicate; dependency impact is an escalation surface (`.agents/skills/workflow-spec-driven/SKILL.md:85`).
- PASS: undecided timing, dismissal, message meaning, or trigger behavior fails the no-product-ambiguity/preserved-behavior predicate (`.agents/skills/workflow-spec-driven/SKILL.md:79`; `templates/agents/codex/planner.toml:43`).
- PASS: several files do not reclassify a bounded correction by themselves (`tools/test_phase_skills.py:589`; `.agents/skills/workflow-spec-driven/SKILL.md:61`).

## Impacted QA Scenarios

- `QAS-enforce-spec-anchored-qa-contracts`: not rerun; technical packet explicitly excluded QA Plan/Execute.
- `QAS-write-specify-impact-and-uiux`: not rerun; technical packet explicitly excluded QA Plan/Execute.
- `QAS-offer-gap-hunt-at-plan-approval`: not rerun; technical packet explicitly excluded QA Plan/Execute.

These are phase-scope limitations, not technical acceptance gaps. No public product behavior changed.

## Gate Check

- `python3 tools/test_phase_skills.py`: 19 passed, 0 failed, 0 skipped.
- `bun test tools/shared/tests/qa-skills.test.ts`: 31 passed, 0 failed, 0 skipped; 590 `expect()` calls.
- Combined assigned suites: 50 passed, 0 failed, 0 skipped.
- Before feature: 48 tests (18 Python + 30 Bun).
- After feature: 50 tests (19 Python + 31 Bun).
- Delta: +2 tests.
- Spec validator: 0 errors, 0 warnings.
- `git diff --check`: passed.

## Discrimination Sensor

| Mutation | File:line | Description | Killed? |
| --- | --- | --- | --- |
| M1 | `.agents/skills/workflow-spec-driven/SKILL.md:57` | Lowered `cross-feature change` floor from Medium to Small in detached scratch worktree. | Killed by Python owner suite. |
| M2 | `docs/guidelines/GATES.md:65` | Removed `not` from the missing-selector no-full-e2e rule in detached scratch worktree. | Killed by Bun QA-guideline owner suite. |

**Sensor depth**: lightweight, two behavior-level routing mutations across the split ownership lanes.
**Result**: 2/2 killed - PASS.
**Isolation**: scratch worktree removed; real-tree status retained only this pre-existing untracked validation artifact.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum code | PASS: router/provider assertions live in Python; QA-guideline bridge assertions live in Bun. |
| Surgical changes | PASS |
| No scope creep | PASS |
| Matches patterns | PASS |
| Spec-anchored outcome check | PASS |
| Per-layer coverage expectation | PASS for instruction-contract artifacts |
| Every test maps to a spec requirement | PASS |
| Documented guidelines followed | PASS: `docs/guidelines/TEST-CONTRACT.md:76` single-suite ownership restored; `tools/test_phase_skills.py:568` owns router/providers and `tools/shared/tests/qa-skills.test.ts:249` owns QA bridges. |

## Requirement Traceability

| Requirement | Previous Status | New Status |
| --- | --- | --- |
| RSG-01..RSG-16 | Verified | Verified |

## Summary

**Overall**: Ready.
**Spec-anchored check**: 16/16 matched; 0 precision gaps.
**Sensor**: 2/2 killed.
**Gate**: 50 passed, 0 failed.
**Issues found**: none.
**Next step**: `validate_state.py right-size-ui-corrections` must pass.
