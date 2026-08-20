# Add Deep Review Skill Validation

**Date**: 2026-08-20
**Spec**: inline acceptance criteria supplied to the verifier (AC1-AC7)
**Diff range**: `e9856d4f908a63ffdde5fa981cc120c519240732..58c8a4b7b31ba5fcbb77a746080e79d5652f7d02`
**Verifier**: independent sub-agent (author != verifier)
**Verdict**: PASS

## Task completion

| Slice | Commit | Status | Evidence |
| --- | --- | --- | --- |
| Install skill and set release version | `75759002ce106bf9870ec7001868064f6124d3b2` | PASS | 19 skill files plus `skills-lock.json`, `package.json`, and `package-lock.json` |
| Record initial verification | `42974faeb7399ce9f436d62596e82b79c2b37fe2` | PASS | Validation artifact committed |
| Add canonical regression guard | `58c8a4b7b31ba5fcbb77a746080e79d5652f7d02` | PASS | `tools/shared/tests/deep-review-installation.test.ts` added |

## Spec-anchored acceptance criteria

| AC | Spec-defined outcome | Evidence and assertion | Result |
| --- | --- | --- | --- |
| AC1 | The complete `deep-review` skill is versioned under `.agents/skills/deep-review/`. | `.agents/skills/deep-review/SKILL.md:2` declares `name: deep-review`; `tools/shared/tests/deep-review-installation.test.ts:15` asserts `expect(existsSync(join(skillDirectory, "SKILL.md"))).toBe(true)`. `git ls-tree -r --name-only HEAD .agents/skills/deep-review \| wc -l` returned 19 tracked files; all 8 bundled Python files accepted `--help`; `.agents/skills/deep-review/assets/findings.schema.json:1` parsed as JSON. | PASS |
| AC2 | The lock records the GitHub origin, skill path, and installed hash. | `skills-lock.json:14` through `skills-lock.json:18` contain the `deep-review` block. `tools/shared/tests/deep-review-installation.test.ts:20` through `tools/shared/tests/deep-review-installation.test.ts:25` assert exact object equality for `source: "pedronauck/skills"`, `sourceType: "github"`, `skillPath: "skills/mine/deep-review/SKILL.md"`, and `computedHash: "f87524f4e50f1311ebd14a8590bfffac2866a8e333fd4813e12aa2f5803bfe75"`. | PASS |
| AC3 | Project discovery returns `deep-review` from the expected source. | `tools/shared/tests/deep-review-installation.test.ts:38` through `tools/shared/tests/deep-review-installation.test.ts:52` run `npx --yes skills list --json` and assert a project-scoped row whose name, path, source, and source type match the installed skill. The targeted canonical test passed. | PASS |
| AC4 | Both package manifests declare release version `0.2.2`. | `package.json:3`, `package-lock.json:3`, and `package-lock.json:9` contain `0.2.2`; `tools/shared/tests/deep-review-installation.test.ts:34` through `tools/shared/tests/deep-review-installation.test.ts:36` assert all three values with `toBe("0.2.2")`. | PASS |
| AC5 | The repository gate passes without regressions. | `package.json:8` defines `vitest run`. `npm test` at `58c8a4b` passed 4 files and 39 tests, with 0 failed and 0 skipped. The same command at base `e9856d4` passed 3 files and 38 tests, with 0 failed and 0 skipped. | PASS |
| AC6 | The installation commit contains only the requested skill and release metadata. | `.agents/skills/deep-review/SKILL.md:1`, `skills-lock.json:14`, `package.json:3`, and `package-lock.json:3` identify the requested surfaces. `git diff-tree --no-commit-id --name-status -r 7575900` asserted exactly 19 added files under `.agents/skills/deep-review/` and only three other changed files: `skills-lock.json`, `package.json`, and `package-lock.json`. The later two commits add only verifier evidence and its canonical regression test. | PASS |
| AC7 | `npm test` fails when the skill origin, path, or hash changes, or when release versions diverge; a canonical test owns the invariant. | `tools/shared/tests/deep-review-installation.test.ts:20` through `tools/shared/tests/deep-review-installation.test.ts:25` assert exact origin, path, and hash; lines 34 through 36 assert all release versions. Four separate scratch mutations were run with `npm test`; each produced 1 failed and 38 passed tests, killing origin, path, hash, and version-divergence mutants. | PASS |

**Status**: 7/7 ACs match the specified outcomes. No spec-precision gaps.

## Discrimination sensor

| Mutation | Assertion that killed it | Result |
| --- | --- | --- |
| Changed `skills-lock.json:15` source from `pedronauck/skills` to `wrong/skills`. | Exact lock-object equality at `tools/shared/tests/deep-review-installation.test.ts:20` failed under `npm test`. | KILLED |
| Changed `skills-lock.json:17` path from `skills/mine/deep-review/SKILL.md` to `skills/wrong/deep-review/SKILL.md`. | Exact lock-object equality at `tools/shared/tests/deep-review-installation.test.ts:20` failed under `npm test`. | KILLED |
| Replaced `skills-lock.json:18` computed hash with 64 zeroes. | Exact lock-object equality at `tools/shared/tests/deep-review-installation.test.ts:20` failed under `npm test`. | KILLED |
| Changed top-level `package-lock.json:3` version from `0.2.2` to `9.9.9`. | Version equality at `tools/shared/tests/deep-review-installation.test.ts:35` failed under `npm test`. | KILLED |

**Sensor depth**: lightweight, 4 targeted behavior-level mutations
**Result**: 4/4 killed, PASS
**Isolation**: mutations ran in detached temporary worktree `/tmp/my-workflow-deep-review-sensor.mKHmqt/tree`. After forced worktree removal, real-tree `git status --porcelain=v1` matched the pre-sensor baseline exactly: only the pre-existing untracked `.deep-review/` directory.

## Gate check

- **Gate command**: `npm test`
- **Current result**: 39 passed, 0 failed, 0 skipped across 4 files
- **Base result at `e9856d4`**: 38 passed, 0 failed, 0 skipped across 3 files
- **Test-count delta**: +1 canonical test
- **Targeted result**: `npx vitest run tools/shared/tests/deep-review-installation.test.ts` passed 1/1
- **Additional checks**: 19 tracked skill files; all 8 bundled Python files accepted `--help`; `findings.schema.json` parsed; `git diff --check e9856d4..58c8a4b` passed

## Code quality and scope

- Minimum installation diff: PASS
- Canonical project skill location: PASS
- No compatibility path or unrelated cleanup: PASS
- Package and lock versions agree: PASS
- Canonical test protects the installed-skill metadata and release-version invariant at the cheapest discriminating layer: PASS
- Every test in scope maps to AC1-AC5 or AC7; AC6 is a commit-scope assertion: PASS
- Documented guideline followed: `docs/guidelines/TEST-CONTRACT.md:65` through `docs/guidelines/TEST-CONTRACT.md:83`; the configuration files are the product contract and no stronger repository gate owns this invariant: PASS

## Edge cases

No separate edge cases were specified beyond the origin, path, hash, discovery, and version-divergence cases in AC1-AC7.

## Summary

**Overall**: PASS, ready for the authorized PR and release workflow.

**Spec-anchored check**: 7/7 ACs matched; 0 spec-precision gaps
**Sensor**: 4/4 mutations killed
**Gate**: 39/39 passed

No ranked gaps. No lesson distilled because validation found no failure signal.
