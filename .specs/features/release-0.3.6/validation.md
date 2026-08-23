# Release 0.3.6 Validation

**Date**: 2026-08-23
**Phase**: technical
**Contract**: `CHANGELOG.md` 0.3.6 section and release verification packet; no feature `spec.md` exists for this build-only release
**Diff range**: `v0.3.5..c874b83d0c07615ae2d50b516f4237b2a79b8e60`
**Verifier**: independent sub-agent (author != verifier)
**Verdict**: PASS

## Contract Evidence

| Release outcome | Assertion evidence | Result |
| --- | --- | --- |
| Optional Graft and OpenDesign remain non-mandatory, repository-authoritative, fallback-capable, and bounded writers | `tools/shared/tests/qa-skills.test.ts:486` — `IT-023`; exact assertions at `tools/shared/tests/qa-skills.test.ts:494`; policy at `docs/guidelines/UI-UX.md:15` and `docs/guidelines/SECURITY.md:19` | PASS |
| Feature workflow state is versioned and exact legacy ignore rules migrate without staging or committing | `tools/shared/tests/qa-skills.test.ts:68` — `IT-014`; outcomes at `tools/shared/tests/qa-skills.test.ts:72` and `tools/shared/tests/qa-skills.test.ts:81` | PASS |
| Deep Review learnings are trackable; QA charters are immutable; test cases map to acceptance criteria | `tools/shared/tests/qa-skills.test.ts:58` — Git eligibility assertions; `tools/shared/tests/qa-skills.test.ts:336` — `IT-022`; exact contract assertions at `tools/shared/tests/qa-skills.test.ts:343` and `tools/shared/tests/qa-skills.test.ts:350` | PASS |
| Remote actions require explicit authority separate from autonomous readiness | `tools/shared/tests/remote-approval.test.ts:14` — five canonical sources; negative merge assertions at `tools/shared/tests/remote-approval.test.ts:33` | PASS |
| Explicit TLC `Verdict` is authoritative, with legacy `Result` used only when no verdict exists | `tools/test_tlc_validators.py:25` — FAIL-over-PASS; `tools/test_tlc_validators.py:32` — PASS-over-FAIL; implementation precedence at `.agents/skills/tlc-spec-driven/scripts/validate_state.py:68` and `.agents/skills/tlc-spec-driven/scripts/validate_state.py:95` | PASS |
| Deep Review incremental manifests use the effective base and validation freezes input before acceptance | `tools/test_deep_review_contract.py:254` — effective-base assertions at lines 278-281; implementation at `.agents/skills/deep-review/scripts/build_manifest.py:304` and `.agents/skills/deep-review/scripts/build_manifest.py:312`; validation freeze at `.agents/skills/deep-review/scripts/run_jobs.py:223` | PASS |
| Knowledge rejects duplicate decision identities, uses author dates, and stays separate from repository-bundle checking | `tools/knowledge/tests/check.test.ts:247` — author-date rebase case; `tools/knowledge/tests/check.test.ts:496` and `tools/knowledge/tests/check.test.ts:520` — duplicate identities; `tools/knowledge/tests/cli.test.ts:39` — bundle checker not embedded in full test script | PASS |
| Walkthrough publishing sends one POST when absent and one PATCH when present | `tools/test_deep_review_contract.py:243` — exact fake-`gh` call arrays asserted at lines 245-252 | PASS |
| Full Vitest gate runs every tracked canonical test under `tools` and ignores copied QA evidence | `package.json:10` — `vitest run --dir tools`; `tools/shared/tests/qa-skills.test.ts:750` — version and gate assertion; tracked inventory and three killed probes below | PASS |

**Spec-anchored result**: 9/9 explicit release outcomes match their defined values. PRs #49 through #57 and the subsequent gate-scoping fix are represented by `CHANGELOG.md:9-22`.

## Canonical Vitest Inventory

`git ls-files` found exactly these eight tracked Vitest files; no tracked `*.spec.*` files or Vitest config adds another root:

- `tools/knowledge/tests/check.test.ts`
- `tools/knowledge/tests/cli.test.ts`
- `tools/shared/tests/deep-review-installation.test.ts`
- `tools/shared/tests/frontmatter.test.ts`
- `tools/shared/tests/qa-skills.test.ts`
- `tools/shared/tests/remote-approval.test.ts`
- `tools/shared/tests/security-skills-installation.test.ts`
- `tools/shared/tests/workflow-config.test.ts`

`npm test` discovered all 8 files and passed all 108 runtime cases. The `v0.3.5` baseline passed 7 files / 102 cases, so the release adds 1 file and 6 cases; no tracked Vitest file was removed.

## Gate Check

| Command | Result |
| --- | --- |
| `npm ci --ignore-scripts` in detached scratch | PASS — 95 packages installed, 0 vulnerabilities |
| `npm test` | PASS — 8 files / 108 tests / 0 skipped |
| `npm ls --all` | PASS — exit 0; reported unmet entries are optional platform/style peers |
| `python3 scripts/test_adopt.py` | PASS |
| `python3 tools/test_ad_index.py` | PASS |
| `python3 tools/test_deep_review_contract.py` | PASS — 8 tests |
| `python3 tools/test_deep_review_symlink_manifest.py` | PASS — 5 tests |
| `python3 tools/test_deep_review_token_metrics.py` | PASS — 19 tests |
| `python3 tools/test_workflow_config.py` | PASS — 11 tests |
| `python3 tools/test_tlc_validators.py` | PASS — 9 tests |
| `npm run knowledge` | PASS — 0 errors, 14 non-gating harvest warnings with this release report present |
| `git diff --check v0.3.5..HEAD` | PASS |

## Discrimination Sensor

All probes ran sequentially in one detached scratch worktree at `c874b83`; the scratch was removed afterward.

| Mutation | Expected | Observed | Result |
| --- | --- | --- | --- |
| Add failing `docs/qa/evidence/release036-failing.test.ts` | Full gate excludes ignored QA evidence, while direct execution proves the test fails | `npm test`: 8/108 PASS; direct Vitest: 1/1 FAIL | KILLED |
| Add failing case to tracked `tools/knowledge/tests/check.test.ts` | Full gate fails | `npm test`: 1 failed + 108 passed across all 8 files, exit 1 | KILLED |
| Mutate `package.json` release version from `0.3.6` to `0.3.7` | Canonical assertions fail | `npm test`: 2 files failed; `tools/shared/tests/qa-skills.test.ts:760` reported expected `0.3.6`, exit 1 | KILLED |

**Sensor result**: 3/3 killed. Real checkout porcelain before and after remained exactly `?? .specs/features/release-0.3.6/`.

## Version, Dependency, and History Integrity

- `package.json:3`, `package-lock.json:3`, and `package-lock.json:9` report `0.3.6`; canonical assertions at `tools/shared/tests/qa-skills.test.ts:760-763` enforce all three surfaces plus the test command.
- Manifest and root lock dependency pins match exactly. Graft remains `0.10.1`; security CLI remains `1.5.23`; Vitest remains `4.1.10`.
- `skills-lock.json` retains all three external security refs and hashes. Only the bundled Deep Review computed hash changed, and `tools/shared/tests/deep-review-installation.test.ts:54-60` recomputes and asserts it.
- `npm ls --all` exited 0 after the clean install.
- GitHub reports PRs #49-#57 `MERGED`, with merge commits matching the first-parent sequence.
- TLC `check_commit.py` accepted all 29 non-merge commit subjects in `v0.3.5..HEAD`.
- `gh issue list --state open --limit 100` returned `[]`.
- No tag points at `HEAD`; release publication has not occurred during verification.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum release-only gate correction | PASS |
| Canonical tests claimed by the gate | PASS |
| Evidence artifacts excluded without broad hidden exclusions | PASS |
| Version and lock surfaces aligned | PASS |
| No dependency drift beyond declared pins | PASS |
| Real checkout preserved by scratch sensors | PASS |

## Limitation

This build-only release has no `.specs/features/release-0.3.6/spec.md`; verification therefore uses the explicit 0.3.6 changelog and requested release checklist as the contract. No acceptance criterion was inferred beyond those two sources.

## Summary

**Overall**: PASS — ready for tag and release publication.

**Contract**: 9/9 outcomes matched.

**Gate**: 108/108 Vitest plus all 7 Python lanes passed.

**Sensor**: 3/3 mutations killed.

**Issues**: 0 open.
