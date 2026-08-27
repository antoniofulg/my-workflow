# Bun Test Runner Validation

## Validation: Bun Test Runner - PASS

**Date**: 2026-08-27
**Spec**: `.specs/features/bun-test-runner/spec.md`
**Diff range**: `047a806..b58da51` (post-round-2 fix delta: `39ac93f..b58da51`)
**Verifier**: independent Technical Verifier (author != verifier)
**Scope**: technical verification only; no product/code/test/spec/task/docs/QA/config edits, no
commit, tag, push, release, publication, deploy, or operator-state action
**Verdict**: PASS
**Technical scope**: PASS; QA remains pending
**Delivery status**: QA pending (`BTR-15` / `BTR-E2E-001`)

Runtime: `bun --version` -> `1.4.0`; npm -> `10.9.8`; Node.js -> `v22.23.1`.

## Task Completion

| Task | Status | Evidence |
| --- | --- | --- |
| T1 | Done | `tasks.md:50-72`; `bunfig.toml:1-3`; canonical discovery gate passed. |
| T2 | Done | `tasks.md:74-96`; eight suites use `bun:test`; Bun/npm gates passed. |
| T3 | Done | `tasks.md:98-120`; npm dependency tree and pack checks passed. |
| T4 | Done | `tasks.md:122-144`; tagged history and v0.7.0 assertions passed. |
| T5 | Done for technical scope | `tasks.md:146-168`; adoption/docs checks passed; fresh QA walk remains pending. |

All five task definitions are complete (`tasks.md:63-168`); no task is partial or blocked.

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined exact outcome | `file:line` + assertion/command evidence | Result |
| --- | --- | --- | --- |
| BTR-01 | Bun 1.4.x is the supported structural TypeScript runtime. | `README.md:262-270`, `docs/qa/README.md:48-56`; `package.json:16` declares Bun types; `bun --version` returned `1.4.0`. | PASS |
| BTR-02 | `npm test` runs exactly 8 canonical files / 115 tests with 0 failures. | `package.json:10`; fresh `npm test` exited 0: `115 pass`, `0 fail`, `Ran 115 tests across 8 files`. | PASS |
| BTR-03 | Root `bun test` excludes ignored QA evidence and matches npm. | `bunfig.toml:1-3`; isolated worktree with a failing ignored `docs/qa/evidence/sensor-copy.test.ts` exited 0 at 115/8. | PASS |
| BTR-04 | Canonical tests import `bun:test`; no active Vitest imports remain. | `tools/knowledge/tests/check.test.ts:5` and seven other tracked suites import `bun:test`; tracked scan returned 8 Bun imports and 0 `vitest` matches. | PASS |
| BTR-05 | Manifest and npm lock contain no Vitest direct/transitive dependency. | `package.json:14-21`, `package-lock.json:10-17`; `npm ls --all` and `npm ls vitest --all` exited 0, latter `(empty)`. | PASS |
| BTR-06 | `npm run test:all` runs Bun first, then all registered Python suites with 0 failures. | `package.json:10-12`; Build gate exited 0: Bun 115/8, 12 Python lanes (246 numbered cases plus `test_ad_index.py` `ok`). | PASS |
| BTR-07 | Bun `-t` filters by matching full nested test name. | `dx.md:13-19`; `bun test ./tools/shared/tests/qa-skills.test.ts -t "CT-003 / BTR-IT-007 / BTR-IT-008"` exited 0: 1 pass, 27 filtered, 0 fail. | PASS |
| BTR-08 | Missing Bun fails non-zero without Vitest/compatibility fallback. | `package.json:10`; PATH-isolated npm command exited 127 with exact `sh: bun: command not found`, no fallback output. | PASS |
| BTR-09 | HEAD v0.6.0 changelog section equals tag byte-for-byte. | `tools/shared/tests/qa-skills.test.ts:1025-1045`; independent compare: `head_v06_bytes=626`, `tag_v06_bytes=626`, `v06_equal=true`. | PASS |
| BTR-10 | v0.7.0 Unreleased records Bun migration under Changed. | `CHANGELOG.md:5-10`; exact `Bun 1.4` assertion at `qa-skills.test.ts:1048). | PASS |
| BTR-11 | v0.7.0 Removed records retired integration, host continuation, durable context, and external-state rule. | `CHANGELOG.md:12-17`; exact assertions at `qa-skills.test.ts:1049-1052). | PASS |
| BTR-12 | Migration note links tagged v0.5.0 guide and invents/executes no cleanup commands. | `CHANGELOG.md:19-24`; URL assertions at `qa-skills.test.ts:1053-1054`; verifier executed 0 cleanup commands. | PASS |
| BTR-13 | Package/lock remain 0.6.0 while unreleased; no tag/publication created. | `package.json:2-3`, `package-lock.json:3,9`; pack version 0.6.0; `git tag --points-at HEAD` returned no output. | PASS |
| BTR-14 | Current testing docs name Bun 1.4 and `tools` discovery root. | `README.md:262-267`, `docs/qa/README.md:48-56`, `docs/workflow/README.md:12-14`; release contract passed. | PASS |
| BTR-15 | Invalidated release scenario is reset and walked through declared CLI adapter before completion. | Reset is present at `docs/qa/scenarios/REL-report-current-workflow-release.md:9`; no fresh QA Execute report exists in this technical packet. | PENDING QA |
| BTR-16 | Adoption installs no Bun, edits no host settings, and creates no Bun lockfile. | `scripts/adopt.py:43-73`; `scripts/test_adopt.py:187-192,305-333`; adoption suite exited 0 with 20 registered checks and double-adoption coverage. | PASS |
| BTR-17 | Ignored `*.test.ts` evidence copies are not discovered. | `bunfig.toml:2`; failing ignored-copy worktree probe still exited 0 at 115/8. | PASS |
| BTR-18 | A tracked Vitest import is rejected by migration contract. | `tools/**/*.test.ts` tracked scan returned 0 Vitest imports; native imports are present at `tools/knowledge/tests/check.test.ts:5` and the seven other suite import lines; full suite passed. | PASS |
| BTR-19 | Changelog drift from tagged v0.6.0 is rejected. | Byte equality above; comparison assertion at `qa-skills.test.ts:1045`; changelog drift mutant failed the targeted contract. | PASS |
| BTR-20 | npm dry-run package excludes ignored QA evidence and Vitest artifacts. | `scripts/test_adopt.py:205-214`; parsed pack summary: version 0.6.0, 366 entries, all 8 canonical tests present, `qaEvidence=[]`, `vitestArtifacts=[]`, `bunLocks=[]`. | PASS |

**Spec-anchored status**: 19/20 local technical outcomes pass; BTR-15 is explicitly deferred to the
separate QA Execute phase; 0 spec-precision gaps. BTR-15 remains `In Tasks` in `spec.md:138`
until that walk supplies dated scenario evidence. No traceability file was modified.

## Test Contract Disposition

| Contract ID | Exact expected outcome | Evidence | Result |
| --- | --- | --- | --- |
| BTR-IT-001 | Exactly 8 tracked `tools` files run; ignored evidence copies do not. | `tests.md:11`; ignored failing-copy probe passed at 115/8; `bunfig.toml:2`. | PASS |
| BTR-IT-002 | `npm test` under Bun 1.4 passes 115 tests / 8 files. | `tests.md:12`; fresh npm output 115 pass, 0 fail, 8 files. | PASS |
| BTR-IT-003 | Every tracked runner import is `bun:test); zero active Vitest imports. | `tests.md:13`; tracked scan: 8 Bun imports, 0 Vitest. | PASS |
| BTR-IT-004 | Unique full-name `-t` filter runs only matching test and exits 0. | `tests.md:14`; targeted output: 1 pass, 27 filtered, 1 file. | PASS |
| BTR-IT-005 | No direct/transitive Vitest package; npm tree valid. | `tests.md:15`; `npm ls --all` exit 0 and Vitest query empty. | PASS |
| BTR-IT-006 | Bun suite plus every Python suite exits 0. | `tests.md:16`; Build gate exit 0, 115 Bun + 246 numbered Python + ad-index `ok`. | PASS |
| BTR-IT-007 | HEAD/tag v0.6.0 sections are byte-identical. | `tests.md:17`; 626/626 bytes, `v06_equal=true`. | PASS |
| BTR-IT-008 | v0.7.0 Unreleased has Bun/removal notes; package/lock remain 0.6.0. | `tests.md:18`; release contract and version assertions passed. | PASS |
| BTR-IT-009 | Double adoption has no Bun install/lock, host mutation, or second-run drift. | `tests.md:19`; `scripts/test_adopt.py` exit 0; double runs at `scripts/test_adopt.py:185,255,301,331`. | PASS |
| BTR-IT-010 | npm pack excludes ignored QA evidence and Vitest artifact. | `tests.md:20`; pack summary has empty QA/Vitest/Bun-lock lists. | PASS |
| BTR-E2E-001 | Release journey ends with current scenario pass plus dated evidence and no release action. | `tests.md:26`; technical gates pass, but scenario remains `qa_status: untested` at `REL-report-current-workflow-release.md:9`; fresh QA Execute outstanding. | PENDING QA |

All 11 contract IDs are assigned once in task `Tests` rows (`tasks.md:70,94,118,142,166`).

## Edge Cases

| Edge case | Result | Evidence |
| --- | --- | --- |
| BTR-17: ignored QA evidence contains copied tests | PASS | Isolated failing ignored copy remained undiscovered; root `bun test` stayed 115/8. |
| BTR-18: tracked test imports Vitest | PASS | Tracked test scan returned 0 Vitest imports; all 8 suites use `bun:test`. |
| BTR-19: v0.6.0 changelog differs from tag | PASS | Byte compare true; targeted release contract passed. |
| BTR-20: pack dry-run includes forbidden evidence/runtime | PASS | Parsed dry-run has no QA evidence, Vitest artifact, or Bun lock. |

## Round-2 Major Closure

| Finding | Closure evidence | Result |
| --- | --- | --- |
| Adopted targets must receive knowledge source modules but no Bun tests/config/guard/lock; source pack must retain canonical tests. | `scripts/adopt.py:43-52` copies `tools/knowledge/src` and `frontmatter.ts` only; `scripts/test_adopt.py:187-214` asserts target absence of `tools/knowledge/tests`, `tools/shared/tests`, `bun-version.ts`, `bunfig.toml`, `bun.lock`, while source paths are tracked and all 8 canonical tests appear in parsed npm pack. | PASS |
| `assertSupportedBunVersion` must accept 1.4.0, reject 1.5.0 exactly, and preload must invoke it with `Bun.version`. | `tools/shared/src/bun-version.ts:1-7`; `qa-skills.test.ts:1062-1068` exact assertions; direct Bun probe returned `preloadVersion=1.4.0` and exact rejection message. | PASS |

## Discrimination Sensor

Sensor depth: lightweight; three isolated temporary git worktrees; no `git stash`. Each scratch
was removed with `git worktree remove --force`; real-tree `git status --porcelain=v1` matched the
empty baseline after every cleanup.

| Mutation | Scratch fault | Directed result | Killed? |
| --- | --- | --- | --- |
| 1 | Changed `scripts/adopt.py:49` from `tools/knowledge/src` to `tools/knowledge`. | `python3 scripts/test_adopt.py` exited 1 at `test_adopt.py:188`: unexpected adopted `tools/knowledge/tests`. | PASS |
| 2 | Added `files: ["tools/knowledge/src"]` to scratch `package.json`, omitting canonical tests from npm pack. | `python3 scripts/test_adopt.py` exited 1 at `test_adopt.py:214`: missing `tools/knowledge/tests/check.test.ts`. | PASS |
| 3 | Widened `tools/shared/src/bun-version.ts:2` from `1.4.x` to `1.x`. | Targeted Bun release contract exited 1 at `qa-skills.test.ts:1062`, expected `Bun.semver.satisfies(version, "1.4.x")`. | PASS |

Result: 3/3 mutations killed, 0 survived. The separate ignored-copy discovery probe also remained
115/8 with its intentionally failing test excluded. No real-tree code, tests, specs, docs, QA state,
config, history, tags, remotes, or release files were changed by this verifier.

## Gate Check

| Gate | Command/result |
| --- | --- |
| Runtime | `bun --version` -> 1.4.0; `npm --version` -> 10.9.8; `node --version` -> v22.23.1. |
| Structural Bun | `bun test` -> exit 0; 115 pass, 0 fail, 1108 expect calls, 8 files. |
| Structural npm | `npm test` -> exit 0; 115 pass, 0 fail, 8 files. |
| Filter | `bun test ./tools/shared/tests/qa-skills.test.ts -t "CT-003 / BTR-IT-007 / BTR-IT-008"` -> exit 0; 1 pass, 27 filtered, 0 fail. |
| Full Build | `npm run test:all && python3 tools/test_workflow_config.py && python3 tools/test_ad_index.py && python3 tools/ad-index.py --check && npm ls --all && npm pack --dry-run --json && git diff --check` -> exit 0; Bun 115/8, Python 246 numbered cases across 12 lanes plus ad-index `ok`, workflow-config 44, AD index current, npm tree/pack/diff clean. |
| Adoption | `python3 scripts/test_adopt.py` -> exit 0, `ok`; 20 registered tests, double-adoption idempotence and no Bun target artifacts. |
| Package | Parsed `npm pack --dry-run --json`: version 0.6.0, 366 entries; all 8 canonical test paths included; QA evidence, Vitest artifacts, and Bun lock paths empty. |
| Import/dependency | Tracked `tools/**/*.test.ts`: 8 `bun:test` imports, 0 Vitest; `npm ls vitest --all` -> `(empty)`; no tracked Bun lock. |
| Missing Bun | `env PATH="/Users/antoniofulg/.local/share/mise/installs/node/22/bin:/opt/homebrew/bin:/usr/bin:/bin" npm test` -> exit 127, `sh: bun: command not found`, no fallback. |
| Changelog/version | Independent check -> `head_v06_bytes=626 tag_v06_bytes=626 v06_equal=true`; package, lock, root lock all 0.6.0; `git tag --points-at HEAD` empty. |
| TypeScript baseline | `npx tsc --noEmit` in current HEAD and a clean `047a806` worktree (dependencies installed with `npm ci --ignore-scripts --no-audit --no-fund`) both exit 2 with 15 diagnostics. Normalized `(file, code, message)` comparison: `normalized_equal=true`, current-minus-base `[]`, base-minus-current `[]`; zero migration diagnostics. |
| Spec/task validators | `validate_spec.py`: 0 errors/0 warnings; `validate_tasks.py`: 0 errors/0 warnings. |
| Diff hygiene | `git diff --check 047a806..HEAD`: no output before report edit; final report diff check rerun after writing. |

Test integrity: baseline at `047a806` records 8 files / 115 tests
(`.specs/features/host-owned-session-continuation/validation.md:104`); current Bun and npm runs are
also 8 files / 115 tests, delta 0. No test file was deleted, skipped, or weakened. The small
non-null assertions in runner migration only satisfy Bun/TypeScript typing and preserve runtime
assertions.

## Code Quality

| Check | Status |
| --- | --- |
| Minimum/surgical implementation | PASS — runner config, native imports, npm dependency boundary, release notes, docs, and adoption boundary only. |
| No scope creep or compatibility layer | PASS — no Vitest fallback, wrapper, dual-run mode, or Bun package-manager migration. |
| Changed files task-required | PASS — 28 files in `047a806..HEAD`; all belong to the five task surfaces. |
| Existing patterns preserved | PASS — npm remains install/pack/publish owner; Bun owns structural tests only. |
| Spec-anchored assertions | PASS for 19 technical ACs; BTR-15/E2E-001 explicitly handed to QA. |
| Test contract ownership | PASS — 11 unique IDs assigned once; no duplicate suite or hollow added case. |
| Per-layer coverage | PASS for runtime, dependency, package, changelog, adoption, and discovery boundaries; release journey awaits declared CLI walk. |
| Documented guidelines | PASS — `docs/guidelines/TEST-CONTRACT.md`, `GATES.md`, `QA-SCENARIOS.md`, `QA-EXECUTION.md`, `REVIEW-ROUNDS.md`, and `VERIFICATION-EVIDENCE.md` followed. |

## QA Disposition

This diff changes public test commands, package/tooling prerequisites, adoption behavior, and
docs-as-interface. The release scenario is correctly reset to `untested` at
`docs/qa/scenarios/REL-report-current-workflow-release.md:9`. This technical packet did not run
QA Plan/Execute and did not edit QA state. A fresh QA Plan followed by a separate QA Execute session
must walk `J-review-workflow-release` through its declared CLI adapter and record dated evidence
before delivery completion. That pending boundary is BTR-15 / BTR-E2E-001 only.

## Requirement Traceability

`spec.md:124-143` marks BTR-01–BTR-14 and BTR-16–BTR-20 `Verified`; BTR-15 remains `In Tasks`
because its required QA walk is pending. No traceability file was modified.

## Summary

**Overall technical verdict**: PASS
**Spec-anchored check**: 19/20 local technical outcomes matched exact spec values; 1 QA outcome
(`BTR-15`) deferred; 0 spec-precision gaps.
**Gate**: Bun/npm 115/115 across 8/8 files; mixed gate 246 numbered Python cases plus ad-index;
0 failures and 0 skips.
**Sensor**: 3/3 mutations killed; 0 survived; real-tree porcelain restored to empty baseline.
**What works**: Bun 1.4 native runner, canonical discovery, full-name filtering, Vitest removal,
npm packaging, v0.6.0 history preservation, v0.7.0 notes, exact version guard behavior,
source-pack/adoption boundaries, and host-neutral double adoption.
**Remaining delivery action**: Fresh QA Plan/Execute must close BTR-15 / BTR-E2E-001 and record the
scenario's dated pass evidence. No implementation fix task is indicated by this technical pass.
