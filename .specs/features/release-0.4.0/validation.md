# Release 0.4.0 Validation

**Date**: 2026-08-24
**Contract**: `.specs/features/ai-memory-handoff/spec.md` AIM-11 and `CHANGELOG.md:5`
**Scope**: local release preparation only; no tag, push, or publication
**Verdict**: PASS

## Contract Evidence

| Release outcome | Evidence | Result |
| --- | --- | --- |
| Opt-in ai-memory integration is documented without automatic installation | `CHANGELOG.md:7`-`9`, `README.md:144`-`147`, `docs/workflow/ai-memory.md:10`-`16` | PASS |
| Codex wrapper is safe and reviewer continuity is isolated | `CHANGELOG.md:10`-`14`, `docs/workflow/ai-memory.md:136`-`149`, `docs/guidelines/REVIEW-ROUNDS.md:75`-`80` | PASS |
| Lifecycle controls are documented, including reversible disablement and separate purge | `CHANGELOG.md:9`, `docs/workflow/ai-memory.md:169`-`231`, `.specs/features/ai-memory-handoff/tests.md:24` | PASS |
| Version surfaces report `0.4.0` consistently | `package.json:3`, `package-lock.json:3`, `package-lock.json:9`, `CHANGELOG.md:5`, `tools/shared/tests/deep-review-installation.test.ts:70`-`72`, `tools/shared/tests/qa-skills.test.ts:750`-`763` | PASS |

**Spec-anchored result**: 4/4 release outcomes match AIM-11 and the release contract.

## Gate Check

| Command | Result |
| --- | --- |
| Version consistency assertion | PASS — package manifest, both lock roots, and changelog report `0.4.0` |
| `python3 scripts/test_adopt.py` | PASS |
| `python3 tools/test_ad_index.py` | PASS |
| `python3 tools/test_deep_review_contract.py` | PASS — 8 tests |
| `python3 tools/test_deep_review_symlink_manifest.py` | PASS — 5 tests |
| `python3 tools/test_deep_review_token_metrics.py` | PASS — 19 tests |
| `python3 tools/test_workflow_config.py` | PASS — 11 tests |
| `python3 tools/test_tlc_validators.py` | PASS — 9 tests |
| `npm ls --depth=0` | PASS |
| `npm test` | PASS — 8 files / 108 tests / 0 skipped |
| `npm run knowledge` | PASS — 0 errors, 16 non-gating warnings |
| `validate_spec.py` and `validate_tasks.py` | PASS — 0 errors, 0 warnings |
| `git diff --check` | PASS |

## Release Hygiene

- ai-memory QA remains the existing passing WFL journey; no duplicate release QA scenario was created.
- No machine configuration, runtime data, remote, tag, or publication was changed.
- Release is prepared locally and requires separate authorization for tag or publication.

**Overall**: PASS — ready for a separately authorized tag/publication step.
