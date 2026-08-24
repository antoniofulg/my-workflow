# Release 0.4.0 Validation

**Date**: 2026-08-24
**Phase**: technical
**Contract**: `.specs/features/ai-memory-handoff/spec.md` AIM-11 and `.specs/features/ai-memory-handoff/tests.md` IT-005
**Diff range**: `v0.3.6..1086c4b95fa73c2a4935d33b08f240fe7b79422d`
**Verifier**: independent Technical Verifier, author != verifier
**Scope**: local release preparation only; no tag, push, publication, or runtime QA execution
**Verdict**: PASS

## Spec-Anchored Evidence

| Criterion | Spec-defined outcome | Assertion evidence | Result |
| --- | --- | --- | --- |
| AIM-11 / IT-005 | `package.json`, both root lockfile fields, newest changelog heading, and canonical version assertions all report `0.4.0`; package and changelog drift fail the canonical suite. | Values: `package.json:3`, `package-lock.json:3`, `package-lock.json:9`, `CHANGELOG.md:5`. Assertions: `tools/shared/tests/qa-skills.test.ts:762`, `:764`-`:767`; secondary package/lock assertions: `tools/shared/tests/deep-review-installation.test.ts:70`-`:72`. | PASS |

**Spec-anchored result**: 1/1 AIM-11 criterion matched its exact outcome; 0 precision gaps.

## Task Completion

| Task | Status | Evidence |
| --- | --- | --- |
| T11 | Done | `.specs/features/ai-memory-handoff/tasks.md:167`-`:179`; release authorities report `0.4.0`. |
| T12 | Done | `.specs/features/ai-memory-handoff/tasks.md:181`-`:193`; canonical test protects the newest changelog heading and package version independently. |

## Gate Check

| Command | Result |
| --- | --- |
| `npm_config_offline=true npx vitest run tools/shared/tests/qa-skills.test.ts` | PASS, 1 file / 23 tests / 0 skipped |
| `python3 scripts/test_ai_memory.py` | PASS, 9 tests / 0 failed |
| `python3 scripts/test_adopt.py` | PASS |
| `python3 tools/test_ad_index.py && python3 tools/ad-index.py --check` | PASS; index current |
| `python3 tools/test_deep_review_contract.py` | PASS, 8 tests |
| `python3 tools/test_deep_review_symlink_manifest.py` | PASS, 5 tests |
| `python3 tools/test_deep_review_token_metrics.py` | PASS, 19 tests |
| `python3 tools/test_workflow_config.py` | PASS, 11 tests |
| `python3 tools/test_tlc_validators.py` | PASS, 9 tests |
| `npm_config_offline=true npm ls --depth=0` | PASS, 7 pinned dev dependencies |
| `npm_config_offline=true npm test` | PASS, 8 files / 108 tests / 0 skipped |
| `npm_config_offline=true npm run knowledge` | PASS, 0 errors / 17 non-gating warnings |
| Four tracked `spec.md` validators | PASS, 0 errors / 0 warnings |
| Two tracked `tasks.md` validators | PASS, 0 errors; 3 pre-existing warnings in `qa-skills/tasks.md` |
| `git diff --check v0.3.6..HEAD && git diff --check` | PASS |

## Discrimination Sensor

Both mutations ran independently in detached temporary worktrees at `1086c4b`, using checkout-local
source and linked dependencies. Both worktrees were removed. Real-tree porcelain matched the
pre-sensor baseline: only the two authorized validation artifacts were modified.

| Mutation | Expected | Observed | Result |
| --- | --- | --- | --- |
| Change `package.json:3` from `0.4.0` to `9.9.9`. | Canonical IT-005/AIM-11 test fails. | Scoped suite exited 1 at `tools/shared/tests/qa-skills.test.ts:762`; 1 failed / 22 passed. | KILLED |
| Change newest `CHANGELOG.md:5` heading from `0.4.0` to `9.9.9`. | Canonical IT-005/AIM-11 test fails. | Scoped suite exited 1 at `tools/shared/tests/qa-skills.test.ts:766`; 1 failed / 22 passed. | KILLED |

**Sensor depth**: lightweight, two independent release-identity mutations.
**Sensor result**: 2/2 killed — PASS.

## Changelog Evidence and QA Disposition

- `CHANGELOG.md:9`-`:19` describes repository changes backed by technical assertions and the current
  implementation/docs.
- `CHANGELOG.md:20` limits runtime-QA wording to the handoff and lifecycle setup/install/stop paths
  walked by `docs/qa/scenarios/WFL-ai-memory-handoff.md:19`-`:36` and reported for AIM-01–AIM-08 at
  `docs/qa/reports/2026-08-24-ai-memory-handoff.md:14`-`:17`.
- The same line labels reviewer isolation as technical validation unless later release QA covers it.
- The release journey remains stale for 0.4.0: `docs/qa/scenarios/REL-report-current-workflow-release.md:14`-`:20`
  still points to 0.3.6 evidence. Technical verification does not refresh that status or prove the
  complete release story through a current public-interface walk.

No QA artifacts were changed. Release QA Plan and QA Execute remain separate fresh Verifier phases.

## Release Hygiene

- Package manifest and both root lockfile fields agree at `0.4.0`; the canonical test script remains
  `vitest run --dir tools` at `package.json:10` and `tools/shared/tests/qa-skills.test.ts:763`.
- Manifest and root lock dependency pins are set-equal: 7 entries; `npm ls --depth=0` passed.
- No machine configuration, runtime data, tag, push, publication, or remote state changed.

## Ranked Gaps

None for technical AIM-11 / IT-005 verification.

QA limitation, not a technical gap: release 0.4.0 still requires separate QA Plan and QA Execute
against the existing REL journey before any QA-based release-readiness claim.

## Summary

**Overall**: PASS for technical release verification only.

**Spec-anchored check**: 1/1 AIM-11 criterion verified.
**Gate**: scoped 23/23 and full 108/108 Vitest tests passed; all release lanes exited 0.
**Sensor**: 2/2 mutations killed.
**Next step**: fresh release QA session; no tag or publication conclusion is made here.
