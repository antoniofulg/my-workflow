# Release 0.3.5 Validation

**Date**: 2026-08-22
**Contract**: `CHANGELOG.md:5`
**Diff range**: `v0.3.4..067a6bf`
**Verifier**: independent sub-agent (author != verifier)
**Result**: PASS

## Release contract

| Public change | Evidence | Result |
| --- | --- | --- |
| PR #22: Deep Review handles symlink manifest entries without reading their targets | `.agents/skills/deep-review/scripts/_common.py:309`, `.agents/skills/deep-review/scripts/build_manifest.py:322`, `tools/test_deep_review_symlink_manifest.py:55` | PASS |
| PR #23: adoption can preserve existing `AGENTS.md` and `CLAUDE.md` by explicit opt-in | `scripts/adopt.py:212`, `scripts/adopt.py:222`, `scripts/test_adopt.py:176` | PASS |
| PR #40: authorized, pinned external security-skill onboarding | `scripts/adopt.py:242`, `scripts/install_security_skills.py:83`, `skills-lock.json:20` | PASS |
| PR #42: browser gates support feature-tag scoping | `docs/guidelines/GATES.md:19` | PASS |
| PR #43: adoption preserves a consumer-owned AD index | `scripts/adopt.py:61`, `scripts/test_adopt.py:216` | PASS |
| PR #44: pack guide remains source-only after adoption | `scripts/adopt.py:152`, `scripts/test_adopt.py:62` | PASS |
| PR #45: handoff consumers can version feature specs explicitly | `README.md:81`, `docs/guidelines/ARTIFACT-LIFECYCLE.md:37` | PASS |
| PR #46: TLC validators accept generated spec/task layouts while retaining rejection cases | `.agents/skills/tlc-spec-driven/scripts/validate_spec.py:48`, `.agents/skills/tlc-spec-driven/scripts/validate_tasks.py:111`, `tools/test_tlc_validators.py:23` | PASS |
| PR #47: Ponytail `full` remains active through the complete workflow cycle | `AGENTS.md:45`, `README.md:167`, `tools/shared/tests/qa-skills.test.ts:629` | PASS |
| All notable changes since 0.3.4 are documented | `CHANGELOG.md:9` through `CHANGELOG.md:16` includes PRs #22, #23, #40, and #42-#47 | PASS |

## Version surfaces

- `package.json:3`: `0.3.5`
- `package-lock.json:3`: `0.3.5`
- `package-lock.json:9`: `0.3.5`
- `tools/shared/tests/deep-review-installation.test.ts:70`: canonical assertion `0.3.5`
- `tools/shared/tests/qa-skills.test.ts:690`: canonical release-consistency case `0.3.5`
- `CHANGELOG.md:5`: release heading `0.3.5`
- `npm ls --depth=0`: root resolves as `my-workflow@0.3.5`; dependency tree has no errors.

## Gate evidence

- `python3 scripts/test_adopt.py`: PASS (`ok`).
- `python3 tools/test_ad_index.py`: PASS (`ok`).
- `python3 tools/test_deep_review_symlink_manifest.py`: 5/5 PASS.
- `python3 tools/test_deep_review_token_metrics.py`: 19/19 PASS.
- `python3 tools/test_tlc_validators.py`: 5/5 PASS.
- `python3 tools/test_workflow_config.py`: 11/11 PASS.
- `npm test`: 10 files, 140/140 PASS, 0 failed.
- `npm run knowledge`: 0 errors, 11 warnings; one warning is this checkout-local release validation, and ten are existing unharvested-state warnings.
- `git diff --check v0.3.4..HEAD`: PASS.
- `git diff --check HEAD^..HEAD`: PASS.
- `check_commit.py --message 'build(release): bump version to 0.3.5'`: PASS.
- `check_commit.py --message 'docs(release): complete 0.3.5 changelog'`: PASS.
- Added-line credential-pattern scan over `v0.3.4..HEAD`: PASS, no credential-shaped values found.
- GitHub reports PRs #22, #23, #40, and #42-#47 as merged; every merge commit is an ancestor of HEAD.

## Discrimination sensor

Scratch worktree at `067a6bf`; changed only `package.json` from `0.3.5` to `0.3.6`.

- `tools/shared/tests/deep-review-installation.test.ts:70` failed: expected `0.3.5`, received `0.3.6`.
- `tools/shared/tests/qa-skills.test.ts:697` failed: expected `0.3.5`, received `0.3.6`.
- Result: 1/1 behavior mutation killed. Scratch worktree removed.
- Real checkout `git status --porcelain` matched the empty pre-sensor baseline after cleanup.

## Code quality and release hygiene

- Diff matches the nine public changes named by the release contract; QA artifacts provide durable public-interface evidence.
- No version compatibility layer, dependency, or unrelated runtime abstraction was added by the release commits.
- Release notes now cover the two changes omitted by the prior validation: PR #22 and PR #23.
- No tracked files were changed by this verification.

## Verdict

PASS. Release 0.3.5 is internally consistent and ready for tag/release creation. Ranked gaps: none.
