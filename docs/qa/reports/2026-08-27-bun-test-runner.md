# QA report — Bun 1.4 source pack

- **Date:** 2026-08-27
- **Charter:** [`CH-bun-test-runner-source-pack-2026-08-27`](../charters/CH-bun-test-runner-source-pack-2026-08-27.md)
- **Phase:** QA Execute — fresh source-pack/adoption walk and HSC-09 retest
- **Persona:** Repository reader; adjacent adoption canary uses Workflow adopter
- **Adapter:** CLI/manual repository inspection plus checkout-local disposable Git targets and package inspection
- **Environment:** active checkout `/Users/antoniofulg/Projects/my-workflow` at `e215c809960ac8decfd8b9dfcde7d813b0134447`; Bun `1.4.0`, npm `10.9.8`, Node `v22.23.1`
- **Entry path:** `README.md` → structural test gate and **Adopt the workflow**; `CHANGELOG.md`; `scripts/adopt.py`; `npm pack --dry-run --json`
- **Automated gate before walk:** PASS — fresh Bun/npm structural commands and CLI/manual adapter probes exited 0 before status normalization
- **Current verdict:** PASS after fresh retest — HSC-09 accepts current-cycle canonical report/evidence paths without a package-version token
- **Raw evidence:** [`2026-08-27-bun-test-runner/`](../evidence/2026-08-27-bun-test-runner/)

## Matrix

| Charter | Scenario | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `CH-bun-test-runner-source-pack-2026-08-27` | `REL-report-current-workflow-release` / release walk | pass after retest | Release/package/version observables independently reloaded; HSC-09 accepts fresh 2026-08-27 paths without a version token | [`retest-session.md`](../evidence/2026-08-27-bun-test-runner/retest-session.md); [`retest-release.json`](../evidence/2026-08-27-bun-test-runner/retest-release.json); [`retest-pack-summary.json`](../evidence/2026-08-27-bun-test-runner/retest-pack-summary.json); [`retest-test-all.log`](../evidence/2026-08-27-bun-test-runner/retest-test-all.log) |
| `CH-bun-test-runner-source-pack-2026-08-27` | `ADP-adopt-workflow-safely` / adjacent canary | pass after retest | Double adoption independently reloaded; consumer/host sentinels and source-pack-only absence checks pass | [`retest-session.md`](../evidence/2026-08-27-bun-test-runner/retest-session.md); [`retest-adoption.json`](../evidence/2026-08-27-bun-test-runner/retest-adoption.json); [`retest-adoption-gate.log`](../evidence/2026-08-27-bun-test-runner/retest-adoption-gate.log); [`retest-test-all.log`](../evidence/2026-08-27-bun-test-runner/retest-test-all.log) |

No report row remains pending. Both rows are terminal `pass` after the fresh HSC-09 retest. The
current dated report/evidence paths are canonical and do not contain a historical package-version
token; the linked bug is closed after retest.

## Scope and guardrails

This session will walk the declared CLI/manual adapter only. It will run the source-pack commands,
release and package inspections, and two separate checkout-local adoption runs. It will not install
Bun, invoke the printed external-security installer, contact remotes or registries, create tags or
releases, publish, push, merge, deploy, inspect real operator state, or touch retained parallel
residue. Existing unrelated `blocked-verify` scenario statuses remain unchanged.

## Walk results

The fresh CLI/manual release tour passed its user-observable checks: Bun `1.4.0` ran the canonical
`8` files and `115` tests; npm delegated to Bun; the full gate ran Bun before `12` Python lanes;
the unique test-name filter selected `1` test; missing Bun failed with `127` and no fallback;
the ignored failing copy was excluded; the exact `1.4.x` guard accepted `1.4.0` and rejected
`1.5.0`; v0.6.0 changelog bytes matched the tag at `627/627`; v0.7.0 notes and 0.6.0 package
authorities matched; and the package dry-run contained `369` entries with no forbidden paths.

The fresh adjacent adoption canary also passed its public checks. Two runs returned `0`; knowledge
source modules were source-identical; Bun tests/config/guard/lock and external skill trees were
absent; consumer config/template/profile/hook bytes and consumer ignore rules were preserved,
the target Git index and no-preexisting-`HEAD` state were unchanged; host sentinels were unchanged;
and the target/host were removed after capture. The printed external-security command was not
invoked.

## Original defect and handoff

In the original Execute run, fresh evidence was recorded in both changed scenarios and their
canonical `qa_status` was set to `pass`; HSC-09 rejected the paths because it required a
`v0.6.0` token. The targeted
contract and closing `npm run test:all` both reproduced this failure. The scenarios are therefore
marked `fail` with the new bug id; the existing fixed-bug history remains linked, while
`fix_status` and `retest_status` are `pending` for the new open defect. No product code or tests
were changed. Implementer handoff: update HSC-09 to validate fresh canonical evidence/report
paths or current-cycle identity without hard-coding a historical package version, then start a
fresh technical Verifier and fresh QA Execute retest. That retest is recorded below.

## Fresh HSC-09 retest

After technical fix `17fd3f5`, both affected scenarios were set to canonical `qa_status: pass`
with fresh `2026-08-27` evidence and `last_report` paths. The targeted HSC-09 contract passed
with no `v0.6.0` token requirement; its exact command and output are in
[`retest-hsc09.log`](../evidence/2026-08-27-bun-test-runner/retest-hsc09.log).

## Closing gate before status normalization

`npm run test:all` with both scenarios temporarily `pass` exited `1`: Bun reported `114 pass`,
`1 fail`, `1105 expect() calls`, and `Ran 115 tests across 8 files`; Python did not start because
the npm script stopped at the failing structural lane. Exact failure is linked in
[`hsc09-failure.log`](../evidence/2026-08-27-bun-test-runner/hsc09-failure.log).

After recording the defect, scenario statuses were changed to terminal `fail` so no row remains
pending. A final full gate after that status update is recorded below.

## Original final gate after defect recording

`npm run test:all` exited `0` after both affected scenarios were marked `fail`. Bun reported
`115 pass`, `0 fail`, `1107 expect() calls`, and `Ran 115 tests across 8 files`; Python then ran
all `12` discovered lanes (`246` numbered cases plus `tools/test_ad_index.py` `ok`) with zero
failures. The final technical gate is green; the QA verdict remained `FAIL` because the newly filed
HSC-09 defect prevented a valid pass-state close at that time.

The final working-tree residue check reported only the planned durable QA files: this report, the
new bug record, and the two scenario frontmatter updates. Checkout-owned adoption targets and the
ignored failing test probe were absent; no package tarball was present. The full-gate diagnostic
parallel tests emitted retained external parallel-QA paths; this session did not inspect or clean
them per charter guardrails.

## Fresh retest gate and closure

The fresh closing gate ran after both scenarios were marked `pass`:

`npm run test:all` exited `0`. Bun reported `115 pass`, `0 fail`, `1123 expect() calls`, and
`Ran 115 tests across 8 files`; Python then ran all `12` discovered lanes (`246` numbered cases
plus `tools/test_ad_index.py` `ok`) with zero failures. The targeted HSC-09 contract also exited
`0` with `1 pass`, `27 filtered out`, and `0 fail`. Package, version, adoption, and cleanup
captures are linked in the retest evidence directory.

Closing command ledger: `bun test`/`npm test` were exercised by the source-pack and closing npm
chain; `npm run test:all` exit `0` (Bun `115/0`, `1123` expectations, `8` files; Python `12`
lanes, `246` numbered cases); `bun test ./tools/shared/tests/qa-skills.test.ts -t "HSC-09
requires current report evidence for changed QA scenarios"` exit `0` (`1` pass, `27` filtered,
`0` fail); `python3 tools/test_workflow_config.py` exit `0` (`44` passed, `0` failed);
`python3 tools/test_ad_index.py` exit `0` (`ok`); `python3 tools/ad-index.py --check` exit `0`
(`AD-INDEX.md up to date`); `npm ls --all` exit `0`; `npm ls vitest --all` exit `1` with expected
`(empty)`; `npm pack --dry-run --json` exit `0` (`my-workflow@0.6.0`, `369` entries, eight
canonical tests, empty QA-evidence/Vitest/Bun-lock lists); and `git diff --check` exit `0`.

Fresh working-tree residue remained limited to the permitted durable QA files; checkout-local
adoption targets and the ignored failing-test probe were absent, and no package tarball was
created.

## Limitations and handoff

This repository has no browser, API, mobile, authentication, server, or production health surface.
The tagged v0.5.0 guide was verified locally with `git cat-file` but not fetched. The external
security installer remained uninvoked by authorization boundary. Existing real Orca/Codex lifecycle
and completed-pilot cleanup scenarios remain `blocked-verify` and were not reclassified. This
session made no product, test, spec, validation, package, config, tag, release, publication,
remote, deploy, commit, or operator-state change.
