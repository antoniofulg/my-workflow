# Bun Test Runner Validation

## Validation: Bun Test Runner - PASS

**Date**: 2026-08-27
**Spec**: `.specs/features/bun-test-runner/spec.md`
**Diff range**: `047a806..17fd3f5` (QA defect fix delta: `836997e..17fd3f5`)
**Verifier**: independent Technical Verifier (author != verifier)
**Scope**: fresh technical verification of the Bun migration and HSC-09 fix; no product, test,
QA, spec, task, Git, remote, release, publication, deploy, or operator-state writes. Only this
validation report is updated.
**Verdict**: PASS
**Technical scope**: PASS; QA remains pending.
**Delivery status**: BTR-15 / BTR-E2E-001 pending fresh QA retest.

Runtime: Bun `1.4.0`; npm `10.9.8`; Node.js `v22.23.1`.

## Task Completion

| Task | Status | Evidence |
| --- | --- | --- |
| T1 | Done | `tasks.md:50-72`; `bunfig.toml:1-3`; canonical discovery passes. |
| T2 | Done | `tasks.md:74-96`; all eight suites use `bun:test`; Bun/npm gates pass. |
| T3 | Done | `tasks.md:98-120`; npm tree and pack checks pass with no Vitest graph. |
| T4 | Done | `tasks.md:122-144`; tagged history and v0.7.0 assertions pass. |
| T5 | Done for technical scope | `tasks.md:146-168`; adoption/docs checks pass; BTR-15 remains QA-pending. |

All five task definitions are complete (`tasks.md:63-168`). No task is partial or blocked.

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined exact outcome | `file:line` + assertion/command evidence | Result |
| --- | --- | --- | --- |
| BTR-01 | Bun 1.4.x is supported structural TypeScript runtime. | `README.md:262-270`, `docs/qa/README.md:48-56`; `bun --version` -> `1.4.0`. | PASS |
| BTR-02 | `npm test` executes 8 canonical files / 115 tests / 0 failures. | `package.json:10`; fresh Build output: `115 pass`, `0 fail`, `Ran 115 tests across 8 files`. | PASS |
| BTR-03 | Root `bun test` excludes ignored QA evidence and matches npm. | `bunfig.toml:1-3`; current/future ignored-copy probes stayed at 115/8. | PASS |
| BTR-04 | Canonical suites import `bun:test`; no active Vitest imports. | `tools/shared/tests/qa-skills.test.ts:1-5`; tracked scan: 8 Bun imports, 0 Vitest. | PASS |
| BTR-05 | Manifest/lock contain no direct or transitive Vitest dependency. | `package.json:14-21`, `package-lock.json:10-17`; `npm ls --all` passed and Vitest query was `(empty)`. | PASS |
| BTR-06 | `npm run test:all` runs Bun then all registered Python suites with 0 failures. | `package.json:10-12`; Build chain exit 0: Bun 115/8, 12 Python lanes, 246 numbered cases plus AD index `ok`. | PASS |
| BTR-07 | Bun `-t` filters by full nested test name. | `dx.md:13-19`; release filter exit 0: 1 pass, 27 filtered, 0 fail. | PASS |
| BTR-08 | Missing Bun fails non-zero with no fallback runner. | `dx.md:5-11`, `package.json:10`; documented no-fallback contract remains present and full suite passes. | PASS |
| BTR-09 | v0.6.0 changelog section equals tag byte-for-byte. | `tools/shared/tests/qa-skills.test.ts:1075-1083`; release contract and independent section comparison pass. | PASS |
| BTR-10 | v0.7.0 Unreleased records Bun migration under Changed. | `CHANGELOG.md:5-10`; release contract passes. | PASS |
| BTR-11 | v0.7.0 Removed records retired integration and bounded ownership rules. | `CHANGELOG.md:12-17`; release contract passes. | PASS |
| BTR-12 | Migration note links tagged v0.5.0 guide and invents no cleanup command. | `CHANGELOG.md:19-24`; URL assertions pass; no cleanup command executed. | PASS |
| BTR-13 | Package/lock remain 0.6.0; no tag/publication is created while unreleased. | `package.json:2-3`, `package-lock.json:3,9`; pack is 0.6.0 and `git tag --points-at HEAD` is empty. | PASS |
| BTR-14 | Current testing docs name Bun 1.4 and `tools` discovery root. | `README.md:262-267`, `docs/qa/README.md:48-56`, `dx.md:7-10`; assertions pass. | PASS |
| BTR-15 | Invalidated release scenario is walked through CLI adapter before completion. | `docs/qa/scenarios/REL-report-current-workflow-release.md:9-15`; fresh QA Execute not run in this technical packet. | PENDING QA |
| BTR-16 | Adoption installs no Bun, edits no host settings, creates no Bun lockfile. | `scripts/adopt.py:43-73`, `scripts/test_adopt.py:187-214`; adoption exit 0 with double-run checks. | PASS |
| BTR-17 | Ignored copied tests are not discovered. | `bunfig.toml:2`; isolated failing-copy probes remained undiscovered at 115/8. | PASS |
| BTR-18 | Tracked Vitest import is rejected by migration contract. | `tools/shared/tests/qa-skills.test.ts:1-5`; tracked scan has 0 Vitest imports and native suite passes. | PASS |
| BTR-19 | Changelog drift from v0.6.0 tag is rejected. | `tools/shared/tests/qa-skills.test.ts:1075-1095`; release contract passes and history mutant is covered. | PASS |
| BTR-20 | npm pack excludes ignored QA evidence and Vitest artifacts. | `scripts/test_adopt.py:205-214`; parsed pack has `qaEvidence=[]`, `vitestArtifacts=[]`, `bunLocks=[]`. | PASS |

**Spec-anchored status**: 19/20 local technical outcomes pass; BTR-15 is explicitly deferred to
QA Execute. Zero spec-precision gaps. `spec.md:124-143` was not modified; BTR-15 remains `In Tasks`.

## HSC-09 Original Symptom and Path Checks

The fixed test is `tools/shared/tests/qa-skills.test.ts:225-296`. Its original targeted command
passes on the real tree with scenarios still in their recorded non-pass state:

```text
bun test ./tools/shared/tests/qa-skills.test.ts -t "HSC-09 requires current report evidence for changed QA scenarios"
exit 0 — 1 pass, 27 filtered, 0 fail
```

In disposable Git worktrees, both changed scenarios were temporarily made `qa_status: pass` with
canonical report/evidence paths containing no package-version token. A current-dated report/evidence
fixture (`2026-08-27`) passed (`1 pass`, `20 expect() calls`), and a future-dated fixture
(`2099-01-01`) also passed with the same result. The real scenarios and QA report were never edited.

Negative disposable fixtures all failed the intended guard:

| Fixture | Expected failure | Result |
| --- | --- | --- |
| Missing canonical evidence file | `pass references missing evidence` at `qa-skills.test.ts:257` | exit 1 |
| Noncanonical evidence path | `requires canonical evidence paths` at `qa-skills.test.ts:253` | exit 1 |
| Stale `last_report` while a newer scenario report exists | `must point to the latest report` at `qa-skills.test.ts:283` | exit 1 |
| Report/evidence dates differ | `requires evidence from the current report cycle` at `qa-skills.test.ts:291` | exit 1 |
| Current report has no scenario pass row | `requires its current report to record a pass verdict` at `qa-skills.test.ts:269` | exit 1 |
| Report row does not cite scenario evidence | `requires its report verdict to cite evidence` at `qa-skills.test.ts:273` | exit 1 |
| Canonical `last_report` file is missing | `pass references missing report` at `qa-skills.test.ts:259` | exit 1 |

These probes confirm the defect path is fixed without weakening freshness, canonicality, existence,
report-row, latest-report, date-match, or evidence-citation checks.

## Discrimination Sensor

**Sensor depth**: lightweight, one behavior-level mutation; no `git stash`.

| Mutation | Scratch fault | Directed result | Killed? |
| --- | --- | --- | --- |
| 1 | In a disposable worktree, changed `qa-skills.test.ts:231` from an ISO-dated canonical report regex to a v0.6-only report regex. | Current-dated no-version pass fixture failed at the canonical report assertion (`exit 1`). | PASS |

The sensor worktree was removed with `git worktree remove --force`; real-tree
`git status --porcelain=v1` matched the empty pre-sensor baseline. No real code, tests, scenarios,
evidence, reports, specs, tasks, config, history, tags, remotes, or release files changed.

## Gate Check

| Check | Command/result |
| --- | --- |
| Runtime | `bun --version` -> 1.4.0; `npm --version` -> 10.9.8; `node --version` -> v22.23.1. |
| Structural Bun | `bun test` -> exit 0; 115 pass, 0 fail, 1107 expect calls, 8 files. |
| Structural npm | Included in Build chain -> exit 0; 115 pass, 0 fail, 8 files. |
| Targeted HSC-09 | Current real state -> exit 0; 1 pass, 27 filtered, 0 fail. |
| Targeted release/history/version | `bun test ... -t "CT-003 / BTR-IT-007 / BTR-IT-008 ..."` -> exit 0; 1 pass, 27 filtered, 0 fail. |
| Build gate | `npm run test:all && python3 tools/test_workflow_config.py && python3 tools/test_ad_index.py && python3 tools/ad-index.py --check && npm ls --all && npm pack --dry-run --json && git diff --check` -> exit 0. |
| Build counts | Bun 115/8; 12 Python lanes, 246 numbered cases, zero failures/skips; AD index `ok`; workflow config 44/0. |
| Adoption | `python3 scripts/test_adopt.py` -> exit 0; double adoption/idempotence and host-neutral checks pass; external security installer only printed, not invoked. |
| Package | `npm pack --dry-run --json` -> version 0.6.0, 369 entries, all 8 canonical tests, Bun config/version guard included, no QA evidence/Vitest/Bun-lock paths. |
| Dependencies/imports | 8 tracked `bun:test` imports, 0 tracked Vitest imports; `npm ls vitest --all` prints `(empty)` (npm exits 1 for empty query); no tracked `bun.lock`. |
| Version/history | package, lock, and root lock versions all 0.6.0; `git tag --points-at HEAD` empty; v0.6.0 section equals tag; v0.7.0 Unreleased notes pass. |
| Spec/task validators | `validate_spec.py`: 0 errors/0 warnings; `validate_tasks.py`: 0 errors/0 warnings. |

The full feature-range whitespace scan `git diff --check 047a806..HEAD` reports one pre-existing
blank line at EOF in `docs/qa/bugs/BUG-20260827-scenario-pass-report-version-gate.md:27` (present
at `836997e`). The fix delta scan `git diff --check 836997e..HEAD` is clean, and the Build gate's
working-tree `git diff --check` passed. No change was made because this verifier owns only
`validation.md`.

## TypeScript Diagnostic Baseline

`npx tsc --noEmit` was run in current HEAD and a clean `047a806` worktree with dependencies installed
from each commit's lockfile. Both exited 2 with exactly 15 diagnostics. Normalizing each diagnostic
to `(file, TS code, message)` produced:

```text
currentCount=15
baselineCount=15
normalizedEqual=true
currentMinusBaseline=[]
baselineMinusCurrent=[]
```

The line-number shifts are expected from the HSC-09 expansion; there are zero migration/fix
diagnostics.

## Test Integrity

Clean pre-migration `047a806` Vitest gate: `8 passed (8)`, `115 passed (115)`. Current Bun gate:
`115 pass`, `0 fail`, `Ran 115 tests across 8 files`. The fix delta is one modified existing suite
(`git diff --numstat 836997e..HEAD` -> `56` additions, `6` deletions in
`tools/shared/tests/qa-skills.test.ts`); no test file was deleted, skipped, or weakened. Existing
runtime assertions remain intact; HSC-09 now adds exact state-path assertions.

## Edge Cases

| Edge case | Result | Evidence |
| --- | --- | --- |
| BTR-17: ignored copied tests | PASS | `bunfig.toml:2`; isolated failing-copy probe stays 115/8. |
| BTR-18: tracked Vitest import | PASS | tracked source scan: 0 matches; native imports at `tools/shared/tests/qa-skills.test.ts:1-5`. |
| BTR-19: v0.6.0 changelog drift | PASS | `qa-skills.test.ts:1075-1095`; byte comparison and release contract pass. |
| BTR-20: forbidden pack paths | PASS | `scripts/test_adopt.py:205-214`; parsed dry-run forbidden lists empty. |
| HSC-09 missing/noncanonical/stale/date/row/citation paths | PASS | Disposable negative fixtures above all exit 1 at intended assertions. |

## Code Quality

| Check | Status |
| --- | --- |
| Minimum/surgical implementation | PASS — fix touches only the HSC-09 contract test. |
| No scope creep or compatibility layer | PASS — no Vitest fallback, wrapper, dual-run mode, or Bun package-manager migration. |
| Changed files task-required | PASS — fix delta contains only `tools/shared/tests/qa-skills.test.ts`. |
| Existing patterns preserved | PASS — `last_report` schema, canonical evidence conventions, and npm ownership remain. |
| Spec-anchored assertions | PASS for 19 technical ACs; BTR-15/E2E-001 explicitly handed to QA. |
| Per-layer coverage | PASS for runtime, discovery, dependency, package, release, adoption, and HSC-09 state boundaries. |
| Test integrity | PASS — baseline and current counts both 8/115; no test weakening/deletion. |
| Documented guidelines | PASS — `docs/guidelines/TEST-CONTRACT.md`, `GATES.md`, `QA-SCENARIOS.md`, `QA-EXECUTION.md`, `REVIEW-ROUNDS.md`, and `VERIFICATION-EVIDENCE.md` followed. |

## QA Disposition

This feature changes public test commands, package/tooling prerequisites, adoption behavior, and
docs-as-interface. The release and adoption scenarios remain in their recorded `qa_status: fail`
state with pending retest fields; this technical verifier did not alter QA state or the durable QA
report. A fresh QA Plan/Execute session must retest `J-review-workflow-release` and its adjacent
`J-adopt-workflow` canary through the declared CLI/manual adapter before BTR-15 / BTR-E2E-001 can
close. Existing unrelated `blocked-verify` lifecycle scenarios remain unchanged.

## Requirement Traceability

`spec.md:124-143` remains unchanged: BTR-01–BTR-14 and BTR-16–BTR-20 are `Verified`; BTR-15 remains
`In Tasks` pending the separate QA walk. No traceability file was modified.

## Summary

**Overall technical verdict**: PASS
**Spec-anchored check**: 19/20 local technical outcomes matched exact spec values; BTR-15/E2E-001
pending QA; 0 spec-precision gaps.
**Gate**: Bun/npm 115/115 across 8/8 files; 246 numbered Python cases across 12 lanes plus AD
index `ok`; 0 failures and 0 skips.
**Sensor**: 1/1 mutation killed; 0 survived; real-tree porcelain restored to empty baseline.
**HSC-09**: current and future no-version canonical pass fixtures pass; missing, noncanonical,
stale, mismatched-date, report-row, uncited-evidence, and missing-report fixtures fail.
**TypeScript**: 15 current diagnostics exactly equal 15 baseline diagnostics; zero migration/fix
diagnostics.
**Remaining delivery action**: Fresh QA Plan/Execute must close BTR-15 / BTR-E2E-001 and record
dated pass evidence. No implementation fix task is indicated by this technical PASS.
