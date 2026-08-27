# Bun Test Runner Validation

**Date**: 2026-08-26
**Spec**: `.specs/features/bun-test-runner/spec.md`
**Diff range**: `047a806..00c5219`
**Verifier**: independent Technical Verifier (author != verifier)
**Scope**: local technical verification only; no product/code/test/spec/task/docs/QA/config edits,
no commit, tag, push, release, publication, deploy, or operator-state action
**Verdict**: PASS
**Delivery status**: QA pending (`BTR-15` / `BTR-E2E-001`)

Runtime used: `bun --version` -> `1.4.0`; npm -> `10.9.8`; Node.js -> `v22.23.1`.
Bun semantics were checked against the official Bun documentation for test configuration,
discovery, test-name filtering, and TypeScript types:
`https://bun.com/docs/test/configuration`, `https://bun.com/docs/test/discovery`,
`https://bun.com/docs/test`, and `https://bun.com/docs/typescript`.

## Task Completion

| Task | Status | Evidence |
| --- | --- | --- |
| T1 | Done | `tasks.md:54-72`; `bunfig.toml:1-2`; Bun discovery gate passed. |
| T2 | Done | `tasks.md:74-98`; eight suites import `bun:test`; runtime gate passed. |
| T3 | Done | `tasks.md:100-120`; dependency, npm-tree, and pack checks passed. |
| T4 | Done | `tasks.md:122-144`; v0.6.0 byte comparison and v0.7.0 assertions passed. |
| T5 | Done for technical scope | `tasks.md:146-168`; docs and scenario reset are present; fresh QA walk remains pending by design. |

All 20 task checkboxes are checked (`tasks.md:65-168`); no task is partial or blocked.

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined exact outcome | `file:line` + assertion/command evidence | Result |
| --- | --- | --- | --- |
| BTR-01 | Bun 1.4.x is the supported structural TypeScript runtime. | `README.md:263-268` and `docs/qa/README.md:48-54` name Bun 1.4.x; `package.json:16` declares `@types/bun`; `bun --version` returned `1.4.0`. | PASS |
| BTR-02 | `npm test` runs exactly 8 canonical files / 115 tests under `tools`, with 0 failures. | `package.json:10` is `bun test`; fresh `npm test` retry exited 0 with `115 pass`, `0 fail`, `Ran 115 tests across 8 files`. | PASS |
| BTR-03 | Root `bun test` excludes ignored QA evidence and matches the npm suite. | `bunfig.toml:1-2` sets `test.root = "./tools"`; an isolated scratch with a failing `docs/qa/evidence/sensor-copy.test.ts` still exited 0 with `115 pass` across `8 files` and did not run the copy. | PASS |
| BTR-04 | Canonical tests import `bun:test`; no active `vitest` imports remain. | `git grep -n -i vitest -- tools/**/*.test.ts` returned no matches; all eight tracked imports are shown at `tools/knowledge/tests/check.test.ts:5`, `tools/knowledge/tests/cli.test.ts:5`, `tools/shared/tests/{autonomous-parallelization,deep-review-installation,frontmatter,qa-skills,security-skills-installation,workflow-config}.test.ts` import lines; active-contract negative assertion is `tools/shared/tests/qa-skills.test.ts:1048-1076`. | PASS |
| BTR-05 | Manifest and npm lock contain no Vitest direct/transitive dependency. | `package.json:14-21` and `package-lock.json:7-17` contain no Vitest entry; `npm ls --all` exited 0; `npm ls vitest --all` reported `(empty)`. | PASS |
| BTR-06 | `npm run test:all` runs Bun first, then every registered Python suite, all zero. | `package.json:12` orders `npm run test` before `npm run test:python`; Build gate output: Bun `115 pass`, then 12 Python lanes all exit 0 (246 numbered passes plus ad-index `ok`). | PASS |
| BTR-07 | Bun `-t` filters by the matching full nested test name. | `dx.md:16`; `bun test ./tools/shared/tests/qa-skills.test.ts -t "CT-003 / BTR-IT-007 / BTR-IT-008"` exited 0 with `1 pass`, `27 filtered out`, `Ran 1 test across 1 file`. | PASS |
| BTR-08 | Missing Bun fails non-zero without Vitest/compatibility fallback. | `package.json:10`; `env PATH="...node/22/bin:/opt/homebrew/bin:/usr/bin:/bin" npm test` exited `127` with `sh: bun: command not found` and no fallback output. | PASS |
| BTR-09 | HEAD v0.6.0 changelog section is byte-for-byte equal to tag `v0.6.0`. | `tools/shared/tests/qa-skills.test.ts:1018-1035` compares extracted sections with `toBe`; independent byte check returned `head_bytes=626 tag_bytes=626 equal=True`. | PASS |
| BTR-10 | `0.7.0 - Unreleased` records Bun migration under `Changed`. | `CHANGELOG.md:5-10`; exact assertions at `tools/shared/tests/qa-skills.test.ts:1032-1037`. | PASS |
| BTR-11 | v0.7.0 `Removed` records retired integration, host-owned continuation, durable context, and external-state rule. | `CHANGELOG.md:12-17`; exact assertions at `tools/shared/tests/qa-skills.test.ts:1038-1041`. | PASS |
| BTR-12 | Migration note links tagged v0.5.0 lifecycle guide and invents/executes no cleanup commands. | `CHANGELOG.md:19-24`; exact URL assertions at `tools/shared/tests/qa-skills.test.ts:1042-1043`; release cleanup commands executed by this verifier: 0. | PASS |
| BTR-13 | While v0.7.0 is unreleased, package/lock versions stay 0.6.0 and no tag/publication is created. | `package.json:3`, `package-lock.json:3,9`, and `tools/shared/tests/qa-skills.test.ts:1028-1031`; `git tag --points-at HEAD` returned no tag; only `npm pack --dry-run` was run. | PASS |
| BTR-14 | Current testing docs name Bun 1.4 and `tools` discovery root. | `README.md:263-265`, `docs/qa/README.md:48-54`, `docs/workflow/README.md:13-15`; release-scenario wording assertion at `tools/shared/tests/qa-skills.test.ts:1036`. | PASS |
| BTR-15 | Invalidated release scenario is reset and walked through the declared CLI adapter before completion. | Reset is present at `docs/qa/scenarios/REL-report-current-workflow-release.md:9` and required next walk at `:29-33`; no fresh QA Execute report exists in this technical packet. | PENDING QA |
| BTR-16 | Adoption installs no Bun, edits no host settings, and creates no Bun lockfile. | `README.md:268`; adoption implementation copies no package/toolchain path (`scripts/adopt.py:43-74`); disposable double-adoption check returned `idempotent=True`, `host_unchanged=True`, `no_bun_lock=True`, `no_bun_install=True`. | PASS |
| BTR-17 | Ignored `*.test.ts` evidence copies are not discovered. | Correct-root scratch with intentionally failing ignored copy exited 0 at 115/8; broad-root mutant discovered and failed the copy. | PASS |
| BTR-18 | A tracked Vitest import is rejected by migration contract. | Tracked test scan returned no matches; all eight test import lines use `bun:test`; active contract rejects retired runner wording at `tools/shared/tests/qa-skills.test.ts:1076`. | PASS |
| BTR-19 | Changelog drift from tagged v0.6.0 is rejected. | Byte comparison above is equal; the release contract comparison is `tools/shared/tests/qa-skills.test.ts:1018-1035`; changelog mutant was killed at `:1037`. | PASS |
| BTR-20 | npm dry-run package excludes ignored QA evidence and Vitest runtime artifacts. | Parsed `npm pack --dry-run --json` summary: `version=0.6.0`, `entryCount=370`, `qaEvidence=[]`, `vitestArtifacts=[]`, `bunLocks=[]`. | PASS |

**Spec-anchored status**: 19/20 local technical outcomes pass; BTR-15 is explicitly deferred to the
separate QA Execute phase; 0 spec-precision gaps. BTR-15 remains `In Tasks` in `spec.md:138` until
that walk supplies dated scenario evidence. No other requirement status was changed.

## Test Contract Disposition

| Contract ID | Exact expected outcome | Evidence | Result |
| --- | --- | --- | --- |
| BTR-IT-001 | Exactly 8 tracked `tools` files run; ignored evidence copies do not. | `tests.md:11`; correct-root failing-copy scratch passed 115/8; root-broadening sensor killed. | PASS |
| BTR-IT-002 | `npm test` under Bun 1.4 passes 115 tests / 8 files. | `tests.md:12`; fresh npm gate output `115 pass`, `0 fail`, `8 files`. | PASS |
| BTR-IT-003 | Every tracked runner import is `bun:test`; zero active Vitest imports. | `tests.md:13`; tracked `git grep` scans returned zero Vitest matches and eight Bun imports. | PASS |
| BTR-IT-004 | Unique full-name `-t` filter runs only its matching test and exits 0. | `tests.md:14`; targeted command output `1 pass`, `27 filtered out`, `1 file`. | PASS |
| BTR-IT-005 | No direct/transitive Vitest package; npm tree valid. | `tests.md:15`; `npm ls --all` exit 0, Vitest query empty, lock scan empty. | PASS |
| BTR-IT-006 | Bun structural suite plus every Python suite exits 0. | `tests.md:16`; exact Build gate exited 0 with Bun 115 and Python 246 numbered passes plus ad-index `ok`. | PASS |
| BTR-IT-007 | HEAD/tag v0.6.0 sections are byte-identical. | `tests.md:17`; `head_bytes=626 tag_bytes=626 equal=True`; assertion at `qa-skills.test.ts:1035`. | PASS |
| BTR-IT-008 | v0.7.0 Unreleased has Bun/removal notes and package/lock remain 0.6.0. | `tests.md:18`; assertions at `qa-skills.test.ts:1028-1043`; release test passed. | PASS |
| BTR-IT-009 | Double adoption has no Bun install/lock, host mutation, or second-run drift. | `tests.md:19`; disposable fixture output `idempotent=True host_unchanged=True no_bun_lock=True no_bun_install=True`; `scripts/test_adopt.py` exited 0 (`ok`). | PASS |
| BTR-IT-010 | npm pack excludes ignored QA evidence and Vitest artifact. | `tests.md:20`; parsed dry-run summary has empty `qaEvidence`, `vitestArtifacts`, and `bunLocks`. | PASS |
| BTR-E2E-001 | Release journey ends with current scenario `pass` plus dated evidence and no release action. | `tests.md:26`; technical gates/adoption/pack passed, but scenario is intentionally `qa_status: untested` at `docs/qa/scenarios/REL-report-current-workflow-release.md:9`; fresh QA Execute is outstanding. | PENDING QA |

All 11 contract IDs are assigned once in the task `Tests` rows (`tasks.md:70,94,118,142,166`).

## Edge Cases

| Edge case | Result | Evidence |
| --- | --- | --- |
| BTR-17: ignored QA evidence contains copied tests | PASS | Correct-root failing-copy scratch remained 115/8; root-broadening mutant was killed. |
| BTR-18: tracked test imports Vitest | PASS | Tracked test scan has zero Vitest matches; all eight imports are `bun:test`. |
| BTR-19: v0.6.0 changelog differs from tag | PASS | Byte equality is true; release assertion is at `qa-skills.test.ts:1035`. |
| BTR-20: pack dry-run includes forbidden evidence/runtime | PASS | Parsed pack has no QA evidence, Vitest artifact, or Bun lock. |

## Discrimination Sensor

Sensor depth: lightweight, three isolated temporary git worktrees; no `git stash`.

| Mutation | Fault injected in scratch | Directed result | Killed? |
| --- | --- | --- | --- |
| 1 | Changed `bunfig.toml:2` from `root = "./tools"` to `root = "."` and added a failing ignored `docs/qa/evidence/sensor-copy.test.ts`. | `bun test` discovered the copy and failed it (`Expected: false / Received: true`); scratch ended `114 pass / 2 fail / 116 tests / 9 files` because the intentionally broadened root also exposed the worktree's missing local dependency path. | ✅ Killed |
| 2 | Added `"vitest": "4.1.10"` to scratch `package.json` devDependencies. | Targeted release contract exited 1 at `tools/shared/tests/qa-skills.test.ts:1076`: `retired runner wording in active contracts: package.json`. | ✅ Killed |
| 3 | Changed scratch `CHANGELOG.md:9` from Bun 1.4 to Bun 1.3. | Targeted release contract exited 1 at `tools/shared/tests/qa-skills.test.ts:1037`, expecting `Bun 1.4`. | ✅ Killed |

Result: 3/3 mutations killed, 0 survived. Each scratch worktree was removed with
`git worktree remove --force`; real-tree `git status --porcelain=v1` matched the empty baseline
after cleanup. No code, tests, specs, docs, QA state, config, history, tags, remotes, or release
files were changed by this verifier. The mandatory pre-existing Python QA-pilot tests created or
retained disposable residual-preservation directories outside this repository (for example
`/Users/antoniofulg/Projects/.parallel-slice-pilot-od0p8j61-parallel-slices`); those are not Bun or
adoption outputs and were left untouched because this packet has no operator-state cleanup authority.

## Gate Check

| Gate | Command/result |
| --- | --- |
| Bun runtime | `bun --version` -> `1.4.0`. |
| Structural Bun | `bun test` -> exit 0; 115 pass, 0 fail, 1098 expect calls, 8 files. |
| npm structural | `npm test` -> final retry exit 0; 115 pass, 0 fail, 8 files. One earlier invocation timed out two unrelated 5-second security tests (`113 pass / 2 fail`); the immediate retry and all closing gates passed. |
| Filter | Targeted `bun test ... -t "CT-003 / BTR-IT-007 / BTR-IT-008"` -> exit 0; 1 pass, 27 filtered, 0 fail. |
| Full | `npm test && python3 scripts/test_adopt.py && npm pack --dry-run --json` -> exit 0; Bun 115/8, adoption `ok`, npm pack JSON emitted. |
| Build | `npm run test:all && python3 tools/test_workflow_config.py && python3 tools/test_ad_index.py && python3 tools/ad-index.py --check && npm ls --all && npm pack --dry-run --json && git diff --check` -> exit 0. `test:all`: 115 Bun tests + 246 numbered Python tests and ad-index `ok`; extra workflow-config 44 passes and ad-index `ok`; npm tree and pack pass. |
| Adoption boundary | `python3 scripts/test_adopt.py` -> exit 0, `ok`; 20 registered adoption tests. Disposable double-adoption check preserved host and project sentinels. |
| Package boundary | Parsed dry-run: `version=0.6.0`, 370 entries, no ignored QA evidence, Vitest artifact, or Bun lock. |
| Import/dependency/lock scan | Tracked `tools/**/*.test.ts` imports: 8 `bun:test`, 0 Vitest; manifest/lock/tsconfig Vitest scan: 0; tracked Bun lock scan: 0. |
| Missing Bun | PATH-isolated `npm test` -> exit 127, `bun: command not found`, no fallback. |
| Changelog history | Independent byte compare -> `head_bytes=626 tag_bytes=626 equal=True`. |
| Spec/tasks/diff hygiene | `validate_spec.py` and `validate_tasks.py`: 0 errors/0 warnings; `git diff --check 047a806..HEAD`: no output. |

Operator-state note: the required `test_qa_parallel_pilot.py` lane intentionally exercises
preservation of unowned external sentinels and left disposable `.parallel-slice-pilot-*` paths
under `/Users/antoniofulg/Projects`; the verifier did not delete or otherwise mutate those paths.
The adoption-specific host fixture remained byte-identical (`host_unchanged=True`).

Test integrity: the previous feature baseline recorded at `047a806` was 8 files / 115 tests
(`.specs/features/host-owned-session-continuation/validation.md:104`); current Bun and npm runs are
also 8 files / 115 tests, delta 0. No test was deleted, skipped, or weakened.

Additional non-gating observation: `npx tsc --noEmit` reports 22 diagnostics in five existing test
files under the Bun 1.4 type declarations (not a command in `tasks.md`'s Build/Full gates, and Bun
runtime execution is green). No source change was made under the verifier's authority.

## Code Quality

| Check | Status |
| --- | --- |
| Minimum/surgical implementation | PASS — runner config, native imports, npm dependency boundary, release notes, and public docs only. |
| No scope creep or compatibility layer | PASS — no Vitest fallback, wrapper, dual-run mode, or Bun package-manager migration. |
| Changed files are task-required | PASS — all 30 files in `047a806..HEAD` belong to the five task surfaces. |
| Existing patterns preserved | PASS — npm remains install/pack/publish owner; Bun owns structural tests only. |
| Spec-anchored assertions | PASS for 19 technical ACs; BTR-15/E2E-001 explicitly handed to QA. |
| Test contract ownership | PASS — 11 unique IDs assigned once; no duplicate suite or hollow added case. |
| Per-layer coverage | PASS for runtime, dependency, package, changelog, and adoption boundaries; QA journey is pending its declared adapter walk. |
| Documented guidelines | PASS — `docs/guidelines/TEST-CONTRACT.md`, `GATES.md`, `QA-SCENARIOS.md`, `QA-EXECUTION.md`, and `VERIFICATION-EVIDENCE.md` followed. |

## QA Disposition

This diff changes public test commands, package/tooling prerequisites, and docs-as-interface. The
current release scenario was correctly reset to `untested` at
`docs/qa/scenarios/REL-report-current-workflow-release.md:9`. A fresh `qa-plan` and separate
`qa-execute` session must walk `J-review-workflow-release` through its declared CLI adapter and
record dated evidence before delivery completion. This technical report does not substitute for
that session and does not edit QA state.

## Requirement Traceability

`spec.md:124-143` already marks BTR-01–BTR-14 and BTR-16–BTR-20 `Verified`; BTR-15 remains `In
Tasks` because its required QA walk is pending. No traceability file was modified.

## Summary

**Overall technical verdict**: PASS

**Spec-anchored check**: 19/20 local technical outcomes matched exact spec values; 1 QA outcome
(`BTR-15`) deferred; 0 spec-precision gaps.

**Gate**: Bun/npm 115/115 across 8/8 files; mixed gate 246 numbered Python passes plus ad-index;
0 skipped in the final gates.

**Sensor**: 3/3 mutations killed; 0 survived; real-tree porcelain restored to empty baseline.

**What works**: Bun 1.4 native runner, canonical discovery, full-name filtering, Vitest removal,
npm packaging, v0.6.0 history preservation, v0.7.0 notes, version boundary, and host-neutral
adoption.

**Remaining delivery action**: fresh QA Plan/Execute must close `BTR-15` / `BTR-E2E-001` and record
the scenario's dated pass evidence. No implementation fix task is indicated by this technical pass.
