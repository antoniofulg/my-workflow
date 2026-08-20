# Add Deep Review Skill Validation

**Date**: 2026-08-20
**Spec**: inline acceptance criteria supplied to the verifier (AC1-AC9); this small feature has no separate `spec.md`
**Diff range**: `e9856d4f908a63ffdde5fa981cc120c519240732..090e25e4d78b6bc1fe9756768fba4b2832365f73`
**Verifier**: independent sub-agent (author != verifier)
**Verdict**: PASS

## Task completion

| Slice | Commit | Status | Evidence |
| --- | --- | --- | --- |
| Install skill and set release version | `75759002ce106bf9870ec7001868064f6124d3b2` | PASS | 19 skill files plus `skills-lock.json`, `package.json`, and `package-lock.json` |
| Add canonical regression guard | `58c8a4b7b31ba5fcbb77a746080e79d5652f7d02` | PASS | `tools/shared/tests/deep-review-installation.test.ts` added |
| Verify full tree and local CLI | `a6ab38a9b8cf4db8985e3f3cd51b948eead4f33d` | PASS | Complete-tree hash and project-local executable checks |
| Pin the discovery CLI version | `415df22cc9d110a06f02c1bcce70e56be32a21e1` | PASS | Manifest, lockfile, installed lock entry, and installed package assert `skills@1.5.23` |
| Ignore generated Python caches | `090e25e4d78b6bc1fe9756768fba4b2832365f73` | PASS | `__pycache__` directories and `*.pyc` files excluded from the installation hash |

## Spec-anchored acceptance criteria

| AC | Spec-defined outcome | Evidence and assertion | Result |
| --- | --- | --- | --- |
| AC1 | The complete `deep-review` skill is versioned under `.agents/skills/deep-review/`. | `.agents/skills/deep-review/SKILL.md:2` declares `name: deep-review`; `tools/shared/tests/deep-review-installation.test.ts:46` asserts the entry file exists; line 60 asserts the collected tracked-file hash equals the installed hash. `git ls-tree -r --name-only 090e25e .agents/skills/deep-review \| wc -l` returned 19. All 8 bundled Python files accepted `--help`, and `.agents/skills/deep-review/assets/findings.schema.json:1` parsed as JSON. | PASS |
| AC2 | The lock records the GitHub origin, skill path, and installed hash. | `skills-lock.json:14` through line 18 contain the lock entry; `tools/shared/tests/deep-review-installation.test.ts:54` through line 60 assert exact source, source type, skill path, declared hash, and computed tree hash. | PASS |
| AC3 | Project discovery returns `deep-review` from the expected source. | `tools/shared/tests/deep-review-installation.test.ts:82` through line 96 invoke the project-local CLI and assert the exact project-scoped discovery row with `expect(discovered).toContainEqual(...)`. | PASS |
| AC4 | Both package manifests declare release version `0.2.2`. | `package.json:3`, `package-lock.json:3`, and `package-lock.json:9` contain `0.2.2`; `tools/shared/tests/deep-review-installation.test.ts:70` through line 72 assert all three values with `toBe("0.2.2")`. | PASS |
| AC5 | The repository gate passes without regressions. | `package.json:8` defines `vitest run`. `npm_config_offline=true npm test` at `090e25e` passed 39/39 tests across 4 files. The same offline command at base `e9856d4` passed 38/38 across 3 files. | PASS |
| AC6 | The installation commit contains only the requested skill and release metadata. | `.agents/skills/deep-review/SKILL.md:1`, `skills-lock.json:14`, `package.json:3`, and `package-lock.json:3` identify the requested surfaces. `git diff-tree --no-commit-id --name-status -r 7575900` returned exactly 19 added skill files plus `skills-lock.json`, `package.json`, and `package-lock.json`. | PASS |
| AC7 | `npm test` fails when the skill origin, path, or hash changes, or when release versions diverge; a canonical test owns the invariant. | `tools/shared/tests/deep-review-installation.test.ts:54` through line 60 assert origin, path, declared hash, and computed tree hash; lines 70 through 80 assert release and dependency versions. The current scratch mutation of a tracked support file failed at line 60 with 1 failed and 38 passed. | PASS |
| AC8 | The gate validates the complete tree against `computedHash` offline and invokes exact project-local `skills@1.5.23`, without `npx` or network access. | Complete-tree assertion: `tools/shared/tests/deep-review-installation.test.ts:60`. Exact dependency assertions: lines 73 through 80. Project-local executable invocation: lines 82 through 87. `package.json:12`, `package-lock.json:12`, and `package-lock.json:1464` declare `1.5.23`. `npm_config_offline=true npm test` passed through the project-local executable. | PASS |
| AC9 | Generated `__pycache__` directories and `*.pyc` files do not alter the hash or gate, while a changed tracked skill file is detected. | `tools/shared/tests/deep-review-installation.test.ts:21` through line 24 exclude both cache forms; line 60 asserts the remaining tree hash. In scratch, adding `scripts/__pycache__/sensor.pyc` and `scripts/sensor.pyc` kept 39/39 passing; changing tracked `references/taxonomy.md:1` then failed line 60 with a computed hash mismatch. | PASS |

**Status**: 9/9 ACs matched the specified outcomes. No spec-precision gaps.

## Discrimination sensor

| Probe or mutation | Assertion or behavior | Result |
| --- | --- | --- |
| Added `.agents/skills/deep-review/scripts/__pycache__/sensor.pyc` and `.agents/skills/deep-review/scripts/sensor.pyc`. | Cache exclusions at `tools/shared/tests/deep-review-installation.test.ts:21` through line 24 preserve the tracked-tree hash. | ACCEPTED: 39 passed, 0 failed |
| Changed tracked `.agents/skills/deep-review/references/taxonomy.md:1`. | Complete-tree hash assertion at `tools/shared/tests/deep-review-installation.test.ts:60`. | KILLED: 1 failed, 38 passed |

**Sensor depth**: lightweight, one benign-cache probe and one tracked-file mutation in a detached temporary worktree at `090e25e`
**Result**: cache probe accepted and tracked-file mutant killed, PASS
**Isolation**: real-tree `git status --porcelain=v1` hashed to `78c9b65dd5a3c100bde2d6083a583057ddc27136ae81099f3eb117eb6f0f96bd` before and after cleanup. Both snapshots contained only the pre-existing untracked `.deep-review/`; no sensor file reached the real tree.

## Gate check

- **Gate command**: `npm_config_offline=true npm test`
- **Current result**: 39 passed, 0 failed, 0 skipped across 4 files
- **Base result at `e9856d4`**: 38 passed, 0 failed, 0 skipped across 3 files
- **Test-count delta**: +1 canonical test
- **Additional commands**: `git ls-tree -r --name-only 090e25e .agents/skills/deep-review | wc -l` returned 19; all `.agents/skills/deep-review/scripts/*.py --help` exited 0; the findings schema parsed as JSON; `git diff --check e9856d4..090e25e` exited 0; `git diff-tree --no-commit-id --name-status -r 7575900` confirmed installation scope.
- **Skipped tests**: none
- **Failures**: none in the unmutated gate

## Code quality and scope

- Minimum installation diff: PASS
- Complete-tree hash check at the canonical repository gate: PASS
- Offline project-local CLI invocation without `npx`: PASS
- Exact `skills@1.5.23` dependency protected across manifest, lockfile, installed lock entry, and installed package: PASS
- No compatibility path or unrelated cleanup: PASS
- Every test in scope maps to AC1-AC9: PASS

## Edge cases

- Altered support file: detected
- Generated `__pycache__` and loose `*.pyc`: ignored without weakening the tracked-file hash
- Manifest dependency divergence: detected
- Installed dependency divergence: detected
- Missing local CLI, changed origin, changed path, changed hash, and release-version divergence: covered by exact canonical assertions; the current tracked-file mutation exercised the hash failure path

## Summary

**Overall**: PASS, ready for the authorized PR and release workflow.

**Spec-anchored check**: 9/9 ACs matched; 0 spec-precision gaps
**Sensor**: benign cache probe accepted; tracked-file mutation killed
**Gate**: 39/39 passed offline

No ranked gaps. No lesson distilled because validation found no failure signal.
