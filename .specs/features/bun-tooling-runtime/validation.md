# Bun Tooling Runtime Validation

**Date**: 2026-08-29
**Spec**: `.specs/features/bun-tooling-runtime/spec.md`
**Diff range**: `69914e831cb8..30b17f3e2be5`
**Verifier**: independent Verifier (author != verifier)
**Verdict**: PASS

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| T1 | ✅ Done | Bun manifest, lock, discovery, guard, and test runner verified. |
| T2 | ✅ Done | Knowledge CLI and YAML parsing use native Bun. |
| T3 | ✅ Done | Security installer uses pinned, fail-closed `bunx`. |
| T4 | ✅ Done | Package and adoption boundaries verified without checkout residue. |
| T5 | ✅ Done | Active command authority is Bun-only; historical QA remains unchanged. |

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| BUN-01 | Bun 1.4.0 package manager; 1.4.x engine | `tools/shared/tests/deep-review-installation.test.ts:67` - version is `0.7.0`; `:68` - package manager equals `bun@1.4.0`; `tools/shared/tests/qa-skills.test.ts:1085` - engine equals `>=1.4.0 <1.5.0` | ✅ PASS |
| BUN-02 | committed stable `bun.lock`; no `package-lock.json` | `tools/shared/tests/deep-review-installation.test.ts:69` - `bun.lock` exists; `:70` - `package-lock.json` absent; frozen install kept SHA-256 `2017e1f780055f755fa145636d98b8f54a7dfc4fcbc89bf982f0ed42dc22cfb5` unchanged | ✅ PASS |
| BUN-03 | structural discovery only under `tools/` | `tools/shared/tests/qa-skills.test.ts:1086`-`:1089` - `[test]`, root `./tools`, preload, and `bun test` asserted; runtime reported 8 files under `tools/` | ✅ PASS |
| BUN-04 | unsupported Bun fails before cases | `tools/shared/tests/qa-skills.test.ts:52`-`:73` - injected unsupported version exits non-zero, marker remains absent, required range is named; invocation at `:1189`-`:1193` | ✅ PASS |
| BUN-05 | every TS suite imports `bun:test`; no Vitest | `tools/shared/tests/qa-skills.test.ts:1095`-`:1111` - every discovered suite matches `bun:test`; manifest rejects Vitest/tsx/yaml dependencies | ✅ PASS |
| BUN-06 | knowledge entrypoint runs directly with Bun | `tools/knowledge/tests/cli.test.ts:21`-`:25` - command runs through Bun; `:43`-`:45` - manifest knowledge script equals `bun tools/knowledge/src/cli.ts` | ✅ PASS |
| BUN-07 | frontmatter uses `Bun.YAML.parse`; no external yaml | `tools/shared/src/frontmatter.ts:31`-`:43` - native parser and exact failure shapes; `tools/shared/tests/frontmatter.test.ts:13`-`:54` - mapping, empty, malformed, scalar, and CRLF outcomes asserted; `tools/shared/tests/qa-skills.test.ts:1109`-`:1111` rejects external yaml | ✅ PASS |
| BUN-08 | full gate runs Bun then every Python suite | `tools/shared/tests/qa-skills.test.ts:1089`-`:1092` - exact `test:all` chain and 17-file Python inventory asserted; final `bun run test:all` exited 0 | ✅ PASS |
| BUN-09 | locked CLI uses exact `bunx --bun --no-install` argv | `tools/shared/tests/security-skills-installation.test.ts:291`-`:298` - dry plan exact argv; `:425`-`:437` - one preflight plus one add per each of three locked skills | ✅ PASS |
| BUN-10 | missing/wrong CLI fails closed without fallback | `tools/shared/tests/security-skills-installation.test.ts:306`-`:317` - no standalone `skills` on PATH and version `1.5.23`; `:320`-`:339` - non-zero/wrong-version preflight preserves target before mutation | ✅ PASS |
| BUN-11 | package membership inspected through disposable `bun pm pack`; no checkout tarball | `tools/shared/tests/workflow-config.test.ts:29`-`:53` - pack destination is temp, command is `bun pm pack`, tar is read there, temp is removed, porcelain equals baseline | ✅ PASS |
| BUN-12 | adoption omits repository-only TS suites | `scripts/test_adopt.py:191`-`:194` - fresh adoption asserts zero `*.test.ts`; `:504`-`:543` - legacy owned tests removed while consumer suite survives | ✅ PASS |
| BUN-13 | adopted knowledge CLI runs with Bun and no consumer packages | `scripts/test_adopt.py:195`-`:203` - adopted TS CLI invoked by Bun, exits 0, returns knowledge result; real fresh adoption reproduced this with zero adopted TS tests | ✅ PASS |
| BUN-14 | active authority has zero npm/npx/Vitest/tsx/external-yaml commands | `tools/shared/tests/qa-skills.test.ts:1114`-`:1124` - active roots scanned and violations equal `[]`; `:1134`-`:1146` catches `npm run forbidden`, `npm start`, and `npx foo` mutants | ✅ PASS |
| BUN-15 | public Bun commands map to manifest scripts | `tools/shared/tests/qa-skills.test.ts:1159`-`:1166` - every documented `bun run` name belongs to `package.json`; `README.md:267`-`:269` exposes frozen install, full gate, and knowledge commands | ✅ PASS |
| BUN-16 | historical evidence command text stays unchanged | `tools/shared/tests/qa-skills.test.ts:1167` - historical changes equal `[]`; `:1170`-`:1183` proves the local-baseline detector catches a changed report; `git diff --name-only origin/main...HEAD -- docs/qa/evidence docs/qa/reports` returned 0 paths | ✅ PASS |
| BUN-17 | malformed Bun version fails with required range | `tools/shared/tests/qa-skills.test.ts:52`-`:73` and `:1189`-`:1194` - malformed `not-a-version` exits non-zero before marker and names Bun 1.4.x | ✅ PASS |
| BUN-18 | package/adoption state stays inside disposable boundaries | `tools/shared/tests/workflow-config.test.ts:36`-`:53` - package tarball is temp and checkout porcelain is invariant; `scripts/test_adopt.py:580`-`:599` - symlinked managed target rejects with byte-identical destination; real boundary run also preserved external sentinel | ✅ PASS |

**Status**: 18/18 acceptance criteria match spec-defined outcomes; 0 precision gaps.

## Discrimination Sensor

Sensors ran in detached scratch worktree `/var/tmp/bun-final-sensor.iPGGmi`; real checkout porcelain was empty before and after cleanup.

| Mutation | Assertion exercised | Result |
| --- | --- | --- |
| Bun guard accepted `1.5.x` instead of `1.4.x` | `bun test tools/shared/tests/frontmatter.test.ts` | ✅ Killed: exit 1 before any case; Bun 1.4.0 rejected |
| Legacy cleanup never removed a hash-owned suite | direct `test_legacy_cleanup_removes_owned_tests_and_preserves_consumer_files()` | ✅ Killed: assertion failed on `tools/knowledge/tests/check.test.ts` |
| Security installer executed every mutating add twice | targeted pinned-add Bun test | ✅ Killed: expected 4 commands, received 7 |

**Sensor depth**: lightweight, three highest-risk boundary mutations.
**Result**: 3/3 killed - PASS.

## Gate and Boundary Evidence

- `bun install --frozen-lockfile`: exit 0; 49 installs checked; lock SHA-256 unchanged.
- `bun run test:all`: exit 0. Bun: 122 passed, 0 failed, 1113 assertions, 8 suites. Python: 17 tracked suites executed, 0 failed.
- Python inventory command: `git ls-files -- 'scripts/test_*.py' 'tools/test_*.py' | sort`; 17 paths. Independent loop reported every path `rc=0`.
- Test inventory comparison: `git ls-tree`/`git ls-files` reported 8 TypeScript suites before and after, 17 Python suites before and after. Static test definitions increased from 108 to 115 TypeScript and 345 to 348 Python; none decreased.
- `bun run knowledge`: exit 0; 0 errors and 32 pre-existing harvest-gap warnings.
- Real `bun pm pack --filename <temp>/workflow.tgz --ignore-scripts`: exit 0; final dry-run reported 426 members after adding this validation record; 0 tarballs in checkout; source porcelain unchanged.
- Fresh adoption and re-adoption: both exit 0; snapshots byte-identical; 0 adopted TypeScript tests; adopted knowledge exit 0.
- Adopted probe import with fake `orca` first on PATH: import exit 0; Orca call count 0.
- Legacy re-adoption: 8/8 exact v0.7.0 owned suites removed; corrected rerun confirmed consumer-owned suite remains byte-identical.
- Symlink containment: adoption exit 1 before mutation; target snapshot and external sentinel unchanged.
- Security focused checks: no-standalone-skills PATH 1/1 pass; wrong/non-zero preflight 2/2 pass; pinned exactly-once transaction 1/1 pass.
- Current release scenario: `docs/qa/scenarios/REL-report-current-workflow-release.md:9` remains `qa_status: untested`; `:24`-`:35` requires fresh QA Execute and preserves prior evidence as history.
- Historical evidence: 0 changed paths under `docs/qa/evidence` and `docs/qa/reports` versus `origin/main`.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum native implementation; no new runtime dependency | ✅ |
| Surgical migration; no unrelated product behavior | ✅ |
| Tests assert spec-defined outcomes at owning layers | ✅ |
| Active command scan discriminates real command forms, including `npm start` and `npx foo` | ✅ |
| Security and filesystem mutations fail before target writes | ✅ |
| Guidelines followed: `docs/guidelines/TEST-CONTRACT.md`, feature `tests.md`, TLC `validate.md` | ✅ |

## Requirement Traceability Update

All BUN-01 through BUN-18 moved from task checkpoint attribution to `Validate / ✅ Verified` in `spec.md`. All five tasks are complete. Goals and success criteria are checked. No validation signal requires a reusable lesson.

## Summary

**Overall**: ✅ Ready for separate QA Plan/QA Execute and subsequent delivery decision.

**Spec-anchored check**: 18/18 matched, 0 gaps.
**Sensor**: 3/3 mutants killed.
**Gate**: 122 Bun tests plus all 17 Python suites passed; 0 failures.
**Limit**: technical verification does not upgrade the current release scenario from `untested`; public command/adoption changes require fresh QA.
