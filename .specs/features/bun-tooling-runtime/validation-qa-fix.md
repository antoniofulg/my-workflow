# Bun QA History Guard Fix Validation

**Date**: 2026-08-29
**Spec**: `.specs/features/bun-tooling-runtime/spec.md`
**Diff range**: `66736ad..fb4c61f`
**Verifier**: independent Verifier (author != verifier)
**Verdict**: PASS

## Checkpoint Scope

This checkpoint verifies only `BUG-20260829-bun-history-gate-rejects-new-qa-charters`.
QA Execute still owns scenario and retest status.

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| BUN-16 / bug expected path | New current-cycle QA artifacts remain allowed, while baseline artifacts remain immutable. | `tools/shared/tests/qa-skills.test.ts:193`-`:221` builds the baseline path set and filters changed QA paths through it; `:1178` asserts the current tree has zero changed baseline artifacts; the current tree includes three new charters and one new report absent from baseline; `:1181`-`:1196` adds a new charter beside a changed baseline report and asserts only the baseline report is returned. | PASS |
| Baseline modification and deletion | Editing or deleting an artifact present at the frozen baseline is rejected. | `tools/shared/tests/qa-skills.test.ts:1186`-`:1196` changes a baseline report and expects its path; isolated real-tree sensors modifying and removing `docs/qa/reports/2026-08-20-workflow-0.3.0.md` both made `:1178` fail with that exact path. | PASS |
| BUN-14 | Active authority still rejects npm and npx command forms. | `tools/shared/tests/qa-skills.test.ts:152`-`:170` defines the scanner; `:1145`-`:1156` injects `npm run forbidden`, `npm start`, and `npx foo` into two active-authority files and requires exactly one violation each. | PASS |
| Final feature validity | Existing Bun feature validation remains complete and state-valid. | `.specs/features/bun-tooling-runtime/validation.md:7` records PASS; `:42` records 18/18 criteria; `.agents/skills/workflow-spec-driven/scripts/validate_state.py bun-tooling-runtime` returned 0 errors. | PASS |

**Status**: 4/4 checkpoint criteria match defined outcomes; 0 precision gaps.

## Gate Check

- `bun test tools/shared/tests/qa-skills.test.ts`: exit 0; 29 passed, 0 failed, 553 assertions.
- `bun install --frozen-lockfile && bun run test:all`: exit 0; frozen install reported no changes; Bun reported 122 passed, 0 failed, 1113 assertions across 8 files; all 17 tracked Python suites exited 0.
- `python3 .agents/skills/workflow-spec-driven/scripts/validate_state.py bun-tooling-runtime`: exit 0; 0 errors.
- `git diff --check`: exit 0.
- Real checkout porcelain was empty before and after scratch worktree cleanup.

## Discrimination Sensor

Sensors ran in detached scratch worktree `/var/tmp/bun-qa-fix-sensor.sXLiZT/tree`, removed after use.

| Mutation | Expected discriminator | Result |
| --- | --- | --- |
| Removed the baseline-membership filter at `tools/shared/tests/qa-skills.test.ts:220`. | New current-cycle paths must make the focused suite fail. | KILLED: 27 passed, 2 failed; failures named the three new charters, current report, and bug path. |
| Removed `npx` from the forbidden-command regex at `tools/shared/tests/qa-skills.test.ts:158`. | Existing npx mutation assertion must fail. | KILLED: 28 passed, 1 failed; expected one violation, received zero. |

Boundary probes in the same scratch checkout also proved both baseline-file modification and deletion fail the focused suite with the exact historical report path. A fixture variant containing a new charter and new report while deleting the baseline report passed 29/29 and returned only the deleted baseline path.

**Sensor depth**: lightweight, two behavior-level mutations plus boundary probes.
**Result**: 2/2 mutants killed; all boundary probes matched expected behavior.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum fix at the shared detector | PASS |
| No compatibility layer or scope creep | PASS |
| Test names the historical-integrity invariant | PASS |
| Existing active-authority discrimination retained | PASS |
| Guidelines followed: feature `tests.md` and TLC `validate.md` | PASS |

## Summary

**Overall**: PASS. The history guard now accepts new QA artifacts without weakening immutable-baseline protection or the Bun-only active-authority scanner. Fresh QA Execute remains required and is intentionally not marked here.
