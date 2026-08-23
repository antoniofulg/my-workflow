# QA Skills Final Validation — PASS

**Date**: 2026-08-20
**Spec**: `.specs/features/qa-skills/spec.md`
**Diff range**: `281ed81200138650b57bc766d9a03b1bf06031ca..92fc3e4a0e7e605de10440d023d440ad65ababdd` (`origin/main..92fc3e4`)
**Verifier**: independent final Verifier (author != verifier)
**Phase**: `technical`

## Verdict

PASS. All 22 acceptance criteria match spec-defined outcomes. The final offline gate passes 55/55,
the baseline passes 39/39, all four targeted mutants are killed, and all five durable QA scenarios
are `pass` with no pending, untested, or failed status.

## Task Completion

| Task | Status | Evidence |
| --- | --- | --- |
| T1 | PASS | Local status is complete at `.specs/features/qa-skills/tasks.md:35`; artifact-policy assertions are `tools/shared/tests/qa-skills.test.ts:58`. |
| T2 | PASS | Local status is complete at `.specs/features/qa-skills/tasks.md:52`; skill assertions are `tools/shared/tests/qa-skills.test.ts:147`. |
| T3 | PASS | Local status is complete at `.specs/features/qa-skills/tasks.md:70`; provider assertions are `tools/shared/tests/qa-skills.test.ts:221`. |
| T4 | PASS | Local status is complete at `.specs/features/qa-skills/tasks.md:91`; adoption assertions are `tools/shared/tests/qa-skills.test.ts:327`. |
| T5 | PASS | Local status is complete at `.specs/features/qa-skills/tasks.md:113`; two journeys, five scenarios, and two charters are durable under `docs/qa/`. |
| T6 | PASS | Local status is complete at `.specs/features/qa-skills/tasks.md:132`; terminal results are `docs/qa/reports/2026-08-20-workflow-0.3.0.md:15`. |

All 14 commits in the range match Conventional Commit syntax.

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome and assertion evidence | Result |
| --- | --- | --- |
| QA-01 | Canonical model-invoked `qa-plan` metadata at `.agents/skills/qa-plan/SKILL.md:1`; exact discovery assertions at `tools/shared/tests/qa-skills.test.ts:147`. | PASS |
| QA-02 | Planning owns journeys, scenarios, and charters and stops before execution at `.agents/skills/qa-plan/SKILL.md:26` and `:96`; boundary assertions at `tools/shared/tests/qa-skills.test.ts:169`; durable charters exist under `docs/qa/charters/`. | PASS |
| QA-03 | Canonical model-invoked `qa-execute` metadata at `.agents/skills/qa-execute/SKILL.md:1`; exact discovery assertions at `tools/shared/tests/qa-skills.test.ts:147`. | PASS |
| QA-04 | Execution consumes plans, uses public adapters, and separates disposable evidence from durable results at `.agents/skills/qa-execute/SKILL.md:23` and `:28`; assertions at `tools/shared/tests/qa-skills.test.ts:186`; executed matrix at `docs/qa/reports/2026-08-20-workflow-0.3.0.md:15`. | PASS |
| QA-05 | Defects return to an Implementer, close the session, require a fresh Verifier, and resume the affected journey at `.agents/skills/qa-execute/SKILL.md:94` and `:103`; exact assertions at `tools/shared/tests/qa-skills.test.ts:195`. | PASS |
| QA-06 | Each provider's existing Verifier routes exactly one technical/qa-plan/qa-execute phase; Codex evidence at `.codex/agents/verifier.toml:23`; three-provider assertions at `tools/shared/tests/qa-skills.test.ts:221`. | PASS |
| QA-07 | Scenario schema/status authority remains `QA-SCENARIOS.md`; dispatch bridge at `docs/guidelines/QA-EXECUTION.md:27`; anti-duplication assertions at `tools/shared/tests/qa-skills.test.ts:254`. | PASS |
| QA-08 | README directly credits TLC and Pedro at `README.md:27`; exact name and URL assertions at `tools/shared/tests/qa-skills.test.ts:305`. | PASS |
| QA-09 | Antonio authors both adaptations and each skill links its corresponding Pedro source at `.agents/skills/qa-plan/SKILL.md:13` and `.agents/skills/qa-execute/SKILL.md:14`; assertions at `tools/shared/tests/qa-skills.test.ts:147`. | PASS |
| QA-10 | Both skills declare original project-owned adaptations at `.agents/skills/qa-plan/SKILL.md:17` and `.agents/skills/qa-execute/SKILL.md:18`; the contract requires that phrase and rejects copied/verbatim claims at `tools/shared/tests/qa-skills.test.ts:160`. The exact requested provenance mutant was killed. | PASS |
| QA-11 | README declares stack neutrality without product/stack leaks at `README.md:121`; exact positive/negative assertion at `tools/shared/tests/qa-skills.test.ts:320`. | PASS |
| QA-12 | `.deep-review/*` is ignored and `learnings.md` is re-included at `.gitignore:12`; Git-behaviour assertions at `tools/shared/tests/qa-skills.test.ts:58`. | PASS |
| QA-13 | Adoption prompt requires clean-state and read-only discovery of the declared capability set at `README.md:58`; exact assertions at `tools/shared/tests/qa-skills.test.ts:327`. | PASS |
| QA-14 | Operational profile records interface, runner, command authority, auth/test data, cleanup, and limitations at `docs/qa/README.md:8`, `:20`, `:34`, `:45`, and `:55`; assertions at `tools/shared/tests/qa-skills.test.ts:351`. Existing consumer profiles survive adoption through `scripts/adopt.py:40` and `scripts/test_adopt.py:76`. | PASS |
| QA-15 | Missing tooling selects the closest public/manual adapter without installs or invented commands at `.agents/skills/qa-execute/SKILL.md:28`; assertions at `tools/shared/tests/qa-skills.test.ts:371`. | PASS |
| QA-16 | Verifier reads the profile and reports adapter, exact path, evidence, and limitations at `.codex/agents/verifier.toml:31`; exact assertions at `tools/shared/tests/qa-skills.test.ts:283`; final report records them at `docs/qa/reports/2026-08-20-workflow-0.3.0.md:5`. | PASS |
| QA-17 | Suggested prompt requires status check, read-only discovery, product-doc preservation, managed-path review, complete diff, and declared gate at `README.md:58` and `:64`; exact assertions at `tools/shared/tests/qa-skills.test.ts:327`. | PASS |
| QA-18 | README routes public changes to fresh `qa-plan` and `qa-execute` packets through the existing Verifier without embedding their procedures at `README.md:77`; assertions at `tools/shared/tests/qa-skills.test.ts:327`. | PASS |
| QA-19 | `.specs/features/` remains eligible for Git alongside STATE/index; Git-backed assertions at `tools/shared/tests/qa-skills.test.ts:72`-`:76` and tracked task state at `:153`-`:155`. | PASS |
| QA-20 | Versioned task state is closed before the atomic commit, with task/status updates allowed in that commit; ordering and positive contract assertions at `tools/shared/tests/qa-skills.test.ts:104`-`:146`. | PASS |
| QA-21 | Adoption removes exact duplicate legacy feature-ignore entries, preserves consumer rules, and does not stage files; canonical adoption assertions at `scripts/test_adopt.py:364`-`:414` and contract wording at `tools/shared/tests/qa-skills.test.ts:77`-`:83`. | PASS |
| QA-22 | Package and root lockfile declarations all equal `0.3.0` at `package.json:3` and `package-lock.json:3`; exact assertions at `tools/shared/tests/qa-skills.test.ts:383`. | PASS |

**Spec-anchored status**: 22/22 matched; 0 gaps; 0 spec-precision gaps.

## Durable QA Results

- Two journeys, five scenarios, two charters, one report, one profile, and one personas file are
  durable under `docs/qa/`.
- Deterministic status check found exactly five scenarios, all `qa_status: pass`; none is `pending`,
  `untested`, or `fail`.
- Raw evidence exists at `docs/qa/evidence/2026-08-20-workflow-0.3.0/session.md` and is ignored as
  required by `.gitignore:10`.
- Final report records CLI/manual adapter, exact adoption path, evidence, limitations, ten probes,
  and the 55/55 gate at `docs/qa/reports/2026-08-20-workflow-0.3.0.md:5`.

## Discrimination Sensor

Mutations ran in detached temporary worktrees. The real checkout was clean before and after cleanup.

| Mutation | Fault | Result |
| --- | --- | --- |
| M1 | Replaced qa-plan `original project-owned adaptation` with `copied verbatim`. | KILLED by IT-001 at `tools/shared/tests/qa-skills.test.ts:160`. |
| M2 | Changed the README adoption contract from `never overwrite existing content` to overwrite it. | KILLED by IT-010 at `tools/shared/tests/qa-skills.test.ts:341`. |
| M3 | Changed one durable scenario from `qa_status: pass` to `pending`. | KILLED by the T6 terminal-status gate derived from `.specs/features/qa-skills/tasks.md:148`. |
| M4 | Routed Codex `qa-execute` to `qa-plan`. | KILLED by IT-003 at `tools/shared/tests/qa-skills.test.ts:233`. |

**Sensor depth**: lightweight, targeted at provenance, consumer ownership, terminal QA state, and
provider routing.
**Result**: 4/4 killed — PASS.

## Gate Evidence

- Scoped suite: `npm_config_offline=true npx vitest run tools/shared/tests/qa-skills.test.ts` — 16
  passed, 0 failed, 0 skipped.
- HEAD full offline gate: `npm_config_offline=true npm test` — 55 passed, 0 failed, 0 skipped across
  five files.
- `origin/main` baseline full gate in a detached worktree: 39 passed, 0 failed, 0 skipped across four
  files. Delta: +16; no test-count regression.
- Adoption smoke: `python3 scripts/test_adopt.py` — `ok`, including consumer-owned profile retention
  at `scripts/test_adopt.py:76`.
- Skill metadata validators: 2/2 success.
- Spec validator `--strict`: 0 errors, 0 warnings.
- Tasks validator: 0 errors; three non-blocking granularity/diagram warnings.
- Decision index regenerated with no diff.
- `git diff --check origin/main..HEAD`: exit 0.
- Commit contract: 14/14 subjects match Conventional Commit syntax.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum code and no unrequested framework | PASS |
| Surgical, scope-aligned changes | PASS |
| Provider and guideline patterns preserved | PASS |
| Tests map to acceptance criteria | PASS |
| Assertions target spec-defined outcomes | PASS |
| Public adoption path covered at the integration layer | PASS |
| Documented contracts followed: `docs/guidelines/QA-EXECUTION.md`, `docs/guidelines/REVIEW-ROUNDS.md` | PASS |

## Ranked Gaps

None.

## Summary

**Overall**: PASS — ready for delivery.
**Spec-anchored check**: 22/22.
**Sensor**: 4/4 killed.
**Gate**: 55/55.
**QA status**: 5/5 scenarios pass; no pending state.
