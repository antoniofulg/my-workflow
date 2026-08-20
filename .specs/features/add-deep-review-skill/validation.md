# Add Deep Review Skill Validation

**Date**: 2026-08-20
**Spec**: inline acceptance criteria supplied to the verifier
**Diff range**: `e9856d4ce06625ccefd2a377cbb785292209a4cb..75759002ce106bf9870ec7001868064f6124d3b2`
**Verifier**: independent sub-agent (author != verifier)
**Verdict**: PASS

## Spec-anchored acceptance criteria

| AC | Spec-defined outcome | Evidence and assertion | Result |
| --- | --- | --- | --- |
| AC1 | The complete `deep-review` skill is versioned under `.agents/skills/deep-review/`. | `.agents/skills/deep-review/SKILL.md:2` declares `name: deep-review`; `.agents/skills/deep-review/assets/PROMPT.md:1`, `.agents/skills/deep-review/assets/findings.schema.json:1`, `.agents/skills/deep-review/references/context-pack.md:1`, and `.agents/skills/deep-review/scripts/build_manifest.py:1` evidence the bundled asset, schema, reference, and executable layers. `git ls-tree` asserted 19 tracked files; every bundled Python CLI accepted `--help`; the JSON schema parsed successfully. | PASS |
| AC2 | The skill lock records the GitHub origin and remains consistent with the installed skill. | `skills-lock.json:14` through `skills-lock.json:18` assert `source === "pedronauck/skills"`, `sourceType === "github"`, `skillPath === "skills/mine/deep-review/SKILL.md"`, and a non-empty `computedHash`. In a clean worktree, `npx --yes skills update deep-review -p -y` left the skill tree and this lock block unchanged. | PASS |
| AC3 | A clean project query discovers `deep-review` from the expected source. | `.agents/skills/deep-review/SKILL.md:2` supplies the discovery name. In a detached clean worktree, `npx --yes skills list --json` returned a project-scoped row with `name === "deep-review"`, `source === "pedronauck/skills"`, and `sourceType === "github"`. | PASS |
| AC4 | Both package manifests declare version `0.2.2`. | `package.json:3`, `package-lock.json:3`, and `package-lock.json:9`; a Node assertion required all three values to equal `0.2.2`. | PASS |
| AC5 | The repository gate passes without regressions. | `package.json:8` defines `vitest run`. `npm test` at the slice commit passed 3 files and 38 tests, with 0 failed and 0 skipped. The parent commit also passed 3 files and 38 tests. | PASS |
| AC6 | The commit contains only the requested skill installation and release-version metadata. | `git diff-tree --name-status -r 7575900` asserted 19 added files under `.agents/skills/deep-review/` plus only `skills-lock.json`, `package.json`, and `package-lock.json`; `git show --stat` reported 22 files, 4,967 insertions, and 3 deletions. | PASS |

**Status**: 6/6 ACs match the specified outcome. No spec-precision gaps.

## Discrimination sensor

| Mutation | Evidence | Result |
| --- | --- | --- |
| Removed `.agents/skills/deep-review/SKILL.md` in a detached scratch worktree. | The same `npx --yes skills list --json` assertion no longer found the required project skill and exited 1. | KILLED |
| Changed `package.json:3` from `0.2.2` to `9.9.9` in scratch. | The manifest consistency assertion exited 1. | KILLED |

**Sensor depth**: lightweight, 2 behavior-level mutations
**Result**: 2/2 killed, PASS
**Isolation**: real-tree `git status --porcelain=v1` matched the empty pre-sensor baseline after both temporary worktrees were removed.

## Gate check

- **Gate command**: `npm test`
- **Current result**: 38 passed, 0 failed, 0 skipped across 3 files
- **Parent result**: 38 passed, 0 failed, 0 skipped across 3 files
- **Test-count delta**: 0
- **Additional checks**: 9 bundled Python files accepted `--help`; `findings.schema.json` parsed; clean skill discovery and targeted upstream update passed

## Code quality and scope

- Minimum installation diff: PASS
- Canonical project skill location: PASS
- No compatibility path or unrelated cleanup: PASS
- Package and lock versions agree: PASS
- Every verifier assertion maps to AC1 through AC6: PASS
- Documented project gate used: `package.json:8`

## Summary

**Overall**: PASS, ready for PR and release workflow.

No ranked gaps. No lesson distilled because validation found no failure signal.
