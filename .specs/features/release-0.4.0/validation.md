# Release 0.4.0 Validation

**Date**: 2026-08-24
**Phase**: technical
**Contract**: `.specs/features/ai-memory-handoff/spec.md` AIM-11/AIM-12 and `.specs/features/ai-memory-handoff/tests.md` IT-005
**Feature diff range**: `v0.3.6..6eebb9d10270622b6db70104137d356ec7fff8ce`
**QA-fix slice**: `162b86a..61f2e74d5adb1c1bb49efe7bb7e72109286c8106`
**Final QA record**: `6eebb9d10270622b6db70104137d356ec7fff8ce`
**Verifier**: independent Technical Verifier, author != verifier
**Scope**: local release verification only; no QA execution, product/config change, commit, tag, push, publication, or machine lifecycle action
**Verdict**: PASS

## Spec-Anchored Evidence

| Criterion | Spec-defined outcome | Assertion evidence | Result |
| --- | --- | --- | --- |
| AIM-11 / IT-005 | `package.json`, both root `package-lock.json` version fields, newest changelog heading, and canonical assertions report `0.4.0`. | Values: `package.json:3`, `package-lock.json:3`, `package-lock.json:9`, `CHANGELOG.md:5`. Exact assertions: `tools/shared/tests/qa-skills.test.ts:765`-`:770`. | PASS |
| AIM-12 / IT-005 | Release QA wording distinguishes runtime-walked handoff evidence, documented/command-checked lifecycle dry-runs, and technical reviewer-isolation validation. | `CHANGELOG.md:20` states all three categories. Exact positive assertions: `tools/shared/tests/qa-skills.test.ts:771`-`:773`; historical overclaim rejection: `tools/shared/tests/qa-skills.test.ts:774`. | PASS |

**Spec-anchored result**: 2/2 criteria matched exact outcomes; 0 precision gaps.

## Changelog Evidence Categories

| Category | Exact release claim | Durable support | Result |
| --- | --- | --- | --- |
| Runtime walked | Handoff delivery, single-use/no replay, Codex wrapper/fallback/noninteractive fix, and adoption canary. | `docs/qa/reports/2026-08-24-ai-memory-handoff.md:14`-`:17`, `:26`-`:51` records those runtime probes and no lifecycle-control walk. | PASS |
| Documented/dry-run | Lifecycle controls are documented and command-checked/dry-run only. | `docs/qa/reports/2026-08-24-release-0-4-0.md:32`-`:35` records help and hook-only dry-run inspection, with no `--apply`, service change, re-enable, or purge. | PASS |
| Technical validation | Reviewer isolation remains labeled technical validation; final release QA also walked its public documentation pointers without claiming live reviewer execution. | `CHANGELOG.md:20` and `tools/shared/tests/qa-skills.test.ts:773` enforce the label; `docs/qa/reports/2026-08-24-release-0-4-0.md:59`-`:62` records the documentation-pointer walk. | PASS |

The categories are exact and non-overlapping. No runtime evidence is claimed for disable, re-enable,
or purge.

## Task Completion

| Task | Status | Evidence |
| --- | --- | --- |
| T12 | Done | `.specs/features/ai-memory-handoff/tasks.md:181`-`:193`; IT-005 protects version parity and the newest release heading. |
| T13 | Done | `.specs/features/ai-memory-handoff/tasks.md:195`-`:207`; IT-005 protects the three evidence categories and rejects the reported overclaim. |

## Gate Check

| Command | Current result |
| --- | --- |
| `npm_config_offline=true npx vitest run tools/shared/tests/qa-skills.test.ts` | PASS, 1 file / 23 tests / 0 skipped |
| `python3 scripts/test_ai_memory.py && python3 scripts/test_adopt.py && python3 tools/test_ad_index.py && python3 tools/ad-index.py --check` | PASS; 9 helper tests, adoption checks, and AD-index checks exited 0 |
| `python3 tools/test_deep_review_contract.py && python3 tools/test_deep_review_symlink_manifest.py && python3 tools/test_deep_review_token_metrics.py && python3 tools/test_workflow_config.py && python3 tools/test_tlc_validators.py` | PASS; 8 + 5 + 19 + 11 + 9 tests |
| `npm_config_offline=true npm ls --depth=0` | PASS, 7 exact dev dependencies |
| `npm_config_offline=true npm test && npm run knowledge && git diff --check` | PASS; 8 files / 108 tests / 0 skipped; knowledge 0 errors / 17 non-gating warnings |
| Four tracked `spec.md` validators | PASS, 0 errors / 0 warnings |
| Two tracked `tasks.md` validators | PASS, 0 errors; 3 pre-existing warnings in `qa-skills/tasks.md` |
| `git diff --check v0.3.6..HEAD && git diff --check` | PASS |

## Discrimination Sensor

Both mutations ran independently in detached temporary worktrees at `61f2e74`, using checkout-local
source and linked dependencies. Both worktrees were removed. Real-checkout porcelain matched the
clean pre-sensor baseline after cleanup.

| Mutation | Expected | Observed | Result |
| --- | --- | --- | --- |
| Restore the reported overclaim: `QA runtime walks cover the ai-memory handoff and lifecycle-control paths`. | IT-005/AIM-12 fails. | Scoped suite exited 1 at `tools/shared/tests/qa-skills.test.ts:771`; 1 failed / 22 passed. | KILLED |
| Change newest `CHANGELOG.md:5` heading from `0.4.0` to `9.9.9`. | IT-005/AIM-11 fails. | Scoped suite exited 1 at `tools/shared/tests/qa-skills.test.ts:769`; 1 failed / 22 passed. | KILLED |

**Sensor depth**: lightweight, two independent release-contract mutations.
**Sensor result**: 2/2 killed — PASS.

## QA Disposition

Fresh QA Execute completed after the technical PASS. The release report records `PASS after retest`
at `docs/qa/reports/2026-08-24-release-0-4-0.md:10` and the fixed-path evidence, package dry-run,
adjacent canaries, and final gates at `:38`-`:73`. The durable scenario is `qa_status: pass`,
`fix_status: fixed`, and `retest_status: pass` at
`docs/qa/scenarios/REL-report-current-workflow-release.md:9`-`:15`; the linked major bug is fixed
with a passing retest at `docs/qa/bugs/BUG-20260824-release-overstates-lifecycle-qa.md:3`-`:17`.

No release-journey QA item remains pending or blocked. Recorded limitations remain: this repository
has no browser, API, mobile, auth, server-application, or production-health surface, and the secret
scan was bounded and heuristic rather than a dedicated entropy/history scan
(`docs/qa/reports/2026-08-24-release-0-4-0.md:75`-`:80`).

## Ranked Gaps

None for technical AIM-11/AIM-12 verification.

## Summary

**Overall**: PASS for technical release verification and final release QA.

**Spec-anchored check**: 2/2 outcomes matched; 0 precision gaps.
**Gate**: scoped 23/23 and full 108/108 Vitest tests passed; all release lanes exited 0.
**Sensor**: 2/2 mutations killed.
**QA**: PASS after fix and fresh retest; no pending items or blockers.
**Limitations**: no browser/API/mobile/auth/server/production-health surface; secret scan was bounded and heuristic.
**Next step**: release evidence is synchronized; no tag or publication action was taken.
