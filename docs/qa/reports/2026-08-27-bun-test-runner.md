# QA report — Bun 1.4 source pack

- **Date:** 2026-08-27
- **Charter:** [`CH-bun-test-runner-source-pack-2026-08-27`](../charters/CH-bun-test-runner-source-pack-2026-08-27.md)
- **Phase:** QA Execute — fresh source-pack and adoption walk
- **Persona:** Repository reader; adjacent adoption canary uses Workflow adopter
- **Adapter:** CLI/manual repository inspection plus checkout-local disposable Git targets and package inspection
- **Environment:** active checkout `/Users/antoniofulg/Projects/my-workflow` at `b1dd167f68576bd02f0232145bd72c82e379303b`; Bun `1.4.0`, npm `10.9.8`, Node `v22.23.1`
- **Entry path:** `README.md` → structural test gate and **Adopt the workflow**; `CHANGELOG.md`; `scripts/adopt.py`; `npm pack --dry-run --json`
- **Automated gate before walk:** PASS — Bun/npm structural commands and the first mixed-language gate exited 0 before scenario status updates
- **Current verdict:** FAIL — public release/adoption observables passed, but HSC-09 rejects the required current dated report/evidence paths; new bug filed and handed to Implementer
- **Raw evidence:** [`2026-08-27-bun-test-runner/`](../evidence/2026-08-27-bun-test-runner/)

## Matrix

| Charter | Scenario | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `CH-bun-test-runner-source-pack-2026-08-27` | `REL-report-current-workflow-release` / release walk | fail | Release observables independently reloaded; HSC-09 rejects fresh 2026-08-27 scenario evidence/report paths | [`session.md`](../evidence/2026-08-27-bun-test-runner/session.md); [`hsc09-failure.log`](../evidence/2026-08-27-bun-test-runner/hsc09-failure.log) |
| `CH-bun-test-runner-source-pack-2026-08-27` | `ADP-adopt-workflow-safely` / adjacent canary | fail | Double adoption independently reloaded and clean; HSC-09 rejects its fresh evidence path | [`adoption.json`](../evidence/2026-08-27-bun-test-runner/adoption.json); [`hsc09-failure.log`](../evidence/2026-08-27-bun-test-runner/hsc09-failure.log) |

No report row remains pending. Both rows are terminal `fail` because the public observables passed
but the canonical pass-state gate is incompatible with the mandated dated report/evidence paths.
The new defect is [`BUG-20260827-scenario-pass-report-version-gate`](../bugs/BUG-20260827-scenario-pass-report-version-gate.md).

## Scope and guardrails

This session will walk the declared CLI/manual adapter only. It will run the source-pack commands,
release and package inspections, and two separate checkout-local adoption runs. It will not install
Bun, invoke the printed external-security installer, contact remotes or registries, create tags or
releases, publish, push, merge, deploy, inspect real operator state, or touch retained parallel
residue. Existing unrelated `blocked-verify` scenario statuses remain unchanged.

## Walk results

The CLI/manual release tour passed its user-observable checks: Bun `1.4.0` ran the canonical
`8` files and `115` tests; npm delegated to Bun; the full gate ran Bun before `12` Python lanes;
the unique test-name filter selected `1` test; missing Bun failed with `127` and no fallback;
the ignored failing copy was excluded; the exact `1.4.x` guard accepted `1.4.0` and rejected
`1.5.0`; v0.6.0 changelog bytes matched the tag at `627/627`; v0.7.0 notes and 0.6.0 package
authorities matched; and the package dry-run contained `368` entries with no forbidden paths.

The adjacent adoption canary also passed its public checks. Two runs returned `0`; knowledge
source modules were source-identical; Bun tests/config/guard/lock and external skill trees were
absent; consumer config/template/profile/ignore/hook bytes, Git `HEAD`, and index tree were
unchanged; host sentinels were unchanged; and the target/host were removed after capture. The
printed external-security command was not invoked.

## Defect and handoff

When the fresh evidence was recorded in both changed scenarios and their canonical `qa_status`
was set to `pass`, HSC-09 rejected the paths because it requires a `v0.6.0` token. The targeted
contract and closing `npm run test:all` both reproduced this failure. The scenarios are therefore
marked `fail` with the new bug id; the existing fixed-bug history remains linked, while
`fix_status` and `retest_status` are `pending` for the new open defect. No product code or tests
were changed. Implementer handoff: update HSC-09 to validate fresh canonical evidence/report
paths or current-cycle identity without hard-coding a historical package version, then start a
fresh technical Verifier and fresh QA Execute retest.

## Closing gate before status normalization

`npm run test:all` with both scenarios temporarily `pass` exited `1`: Bun reported `114 pass`,
`1 fail`, `1105 expect() calls`, and `Ran 115 tests across 8 files`; Python did not start because
the npm script stopped at the failing structural lane. Exact failure is linked in
[`hsc09-failure.log`](../evidence/2026-08-27-bun-test-runner/hsc09-failure.log).

After recording the defect, scenario statuses were changed to terminal `fail` so no row remains
pending. A final full gate after that status update is recorded below.

## Final gate after defect recording

`npm run test:all` exited `0` after both affected scenarios were marked `fail`. Bun reported
`115 pass`, `0 fail`, `1107 expect() calls`, and `Ran 115 tests across 8 files`; Python then ran
all `12` discovered lanes (`246` numbered cases plus `tools/test_ad_index.py` `ok`) with zero
failures. The final technical gate is green; the QA verdict remains `FAIL` because the newly filed
HSC-09 defect prevents a valid pass-state close.

The final working-tree residue check reported only the planned durable QA files: this report, the
new bug record, and the two scenario frontmatter updates. Checkout-owned adoption targets and the
ignored failing test probe were absent; no package tarball was present. The full-gate diagnostic
parallel tests emitted retained external parallel-QA paths; this session did not inspect or clean
them per charter guardrails.

## Limitations and handoff

This repository has no browser, API, mobile, authentication, server, or production health surface.
The tagged v0.5.0 guide was verified locally with `git cat-file` but not fetched. The external
security installer remained uninvoked by authorization boundary. Existing real Orca/Codex lifecycle
and completed-pilot cleanup scenarios remain `blocked-verify` and were not reclassified. The new
bug requires an Implementer and a fresh technical Verifier/QA Execute cycle; this session made no
product, test, spec, validation, package, config, tag, release, publication, remote, deploy, or
operator-state change.
