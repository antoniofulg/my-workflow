# README Installation Contract Validation

**Date**: 2026-08-22
**Spec**: `.specs/features/qa-skills/spec.md` (QA-13 and QA-17); defect-specific outcomes came from the reviewed QA report
**Diff range**: `786aadb..f0fc80b`
**Verifier**: independent sub-agent (author != verifier)

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| Clarify README installation contract | Done | Commit `f0fc80b`; docs and canonical regression test only |

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| QA-13: adopted setup discovers actual project capabilities without inventing install requirements | README distinguishes adoption prerequisites, resolver Git-HEAD prerequisite, and source-pack gates | `README.md:53`; `tools/shared/tests/qa-skills.test.ts:591` — exact positive assertions for each prerequisite | PASS |
| QA-17: suggested setup remains safe and actionable | Bundled skills use the pack's adoption path; obsolete external installer and cleanup instructions are absent | `README.md:151`; `tools/shared/tests/qa-skills.test.ts:597` — positive bundled-skill assertion plus negative forbidden-command assertions at `:600` | PASS |

**Status**: 2/2 relevant criteria covered. The original feature spec states broad setup outcomes; the reviewed QA defects supplied the precise remediation values checked here.

## Adoption and Resolver Smoke

- `python3 scripts/adopt.py <empty-existing-directory>` succeeded without a Git repository or Node/npm step.
- Adopted 12 canonical skill directories. `tlc-spec-driven`, `ponytail`, and `deep-review` each contained `SKILL.md`.
- Created zero `.cursor/skills`, `.codex/skills`, or `.opencode/skills` trees and zero `skills-lock.json` files.
- Resolver before first commit exited 1 with `workflow config: cannot resolve git head ...`.
- Resolver after `git init` plus one commit exited 0 and wrote `workflow.json`.
- Runtime authority: `scripts/adopt.py:26` copies bundled skills; `.agents/skills/workflow-config/scripts/workflow_config.py:147` requires `git rev-parse HEAD` only during resolution.

## Discrimination Sensor

| Mutation | File:line | Description | Killed? |
| --- | --- | --- | --- |
| 1 | `README.md:154` in isolated worktree | Reintroduced `@tech-leads-club/agent-skills install` | Yes — IT-019 failed; 1 failed, 19 passed |

**Sensor depth**: lightweight
**Result**: 1/1 killed — PASS

Real checkout porcelain was empty before and after scratch cleanup.

## Gate Check

- Scoped: `npm_config_offline=true npx vitest run tools/shared/tests/qa-skills.test.ts` — 20 passed, 0 failed, 0 skipped.
- Clean-worktree full gate: `npm test` — 62 passed in 6 files, 0 failed, 0 skipped.
- Parent clean-worktree baseline: `npm test` at `786aadb` — 61 passed in 6 files. Delta: +1 regression test.
- Active-checkout full gate: `npm test` — 100 passed in 9 files. Ignored QA evidence contains duplicate test fixtures, so clean-worktree 62 is the canonical count.
- Adoption regression suite: `python3 scripts/test_adopt.py` — `ok`.
- Resolver unit suite: `python3 tools/test_workflow_config.py` — 11 passed, 0 failed.
- Token-metrics unit suite: `python3 tools/test_deep_review_token_metrics.py` — 19 passed.
- AD index suite: `python3 tools/test_ad_index.py` — `ok`.
- Knowledge gate: `npm run knowledge` — 0 errors, 8 existing gap warnings.
- Diff hygiene: `git diff f0fc80b^ f0fc80b --check` — PASS.
- Commit contract: `check_commit.py --message "docs(readme): clarify bundled installation contract"` — PASS.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum change | PASS — two files, no new mechanism |
| Surgical scope | PASS — README contract plus one canonical assertion |
| No scope creep | PASS |
| Matches existing test pattern | PASS |
| Assertions discriminate required prose and forbidden commands | PASS |

## Summary

**Overall**: PASS — ready for delivery.

No blocking or scoped gaps. Environment note only: ignored QA evidence in the active checkout is discoverable by Vitest; clean checkout results remain deterministic.
