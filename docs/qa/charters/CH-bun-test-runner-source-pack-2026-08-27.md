# CH-bun-test-runner-source-pack-2026-08-27

- **Date:** 2026-08-27
- **Scope:** `047a806..f041a4b` for `bun-test-runner`
- **Time-box:** 45 minutes
- **Persona:** Repository reader
- **Journey:** [`J-review-workflow-release`](../journeys/J-review-workflow-release.md)
- **Tour:** Bun 1.4 source-pack, release metadata, and adoption-boundary tour
- **Public entry point:** `README.md` → structural test gate and **Adopt the workflow**; `CHANGELOG.md`
- **Adapter candidate:** CLI/manual through the adapter and authorities in [`docs/qa/README.md`](../README.md)
- **Scenarios:** [`REL-report-current-workflow-release`](../scenarios/REL-report-current-workflow-release.md)
- **Adjacent adoption canary:** [`ADP-adopt-workflow-safely`](../scenarios/ADP-adopt-workflow-safely.md) through [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)

## Mission

Review the Bun 1.4 migration as a repository reader using the source pack's public CLI and package
boundaries. Walk the structural and full gates, release notes, package dry-run, and a separate
checkout-local adoption target. Confirm that Bun owns structural TypeScript tests while npm remains
the install/lock/package authority, and that adoption does not install or configure Bun. Keep the
release scenario and adoption canary tied to one fresh Execute session; do not publish, contact a
remote service, or inspect real operator state.

## Expected observable

The source pack names Bun 1.4 and `./tools` discovery; `npm test`, root `bun test`, targeted Bun
filtering, and `npm run test:all` expose the documented exit/count behavior; v0.6.0 history remains
unchanged while v0.7.0 is Unreleased and package authorities remain 0.6.0; the package contains
the canonical source-pack tests but no ignored QA evidence, Vitest artifact, or `bun.lock`; and two
public adoption runs preserve consumer-owned bytes while leaving Bun-only target paths absent. The
next Execute session must record dated evidence and update the flagged scenarios; this plan records
no live QA result.

## Criterion disposition ledger

All 20 acceptance criteria are accounted for: 17 are public CLI, adoption, or release promises and
3 are internal implementation/regression guards. Public criteria map to the existing canonical
journey/scenario records; internal criteria remain covered by the technical PASS and do not mint or
reset a scenario.

| Criterion | Class | Canonical mapping or internal disposition |
| --- | --- | --- |
| BTR-01 | Public release/CLI | `J-review-workflow-release` → `REL-report-current-workflow-release`; inspect the Bun 1.4 prerequisite and current README/profile/package authorities. |
| BTR-02 | Public CLI | `J-review-workflow-release` → `REL-report-current-workflow-release`; next Execute runs `npm test` and records exactly 8 files / 115 tests / 0 failures. |
| BTR-03 | Public CLI | `J-review-workflow-release` → `REL-report-current-workflow-release`; root `bun test` must match npm and exclude ignored QA evidence. |
| BTR-04 | Internal source contract | Technical-only `bun:test` import scan; implementation detail with no distinct user promise, already PASS in validation. |
| BTR-05 | Public release/package | `J-review-workflow-release` → `REL-report-current-workflow-release`; inspect manifest/lock dependency state and the npm tree for absent Vitest packages. |
| BTR-06 | Public CLI | `J-review-workflow-release` → `REL-report-current-workflow-release`; run the documented mixed Bun/Python gate and observe ordered zero exit. |
| BTR-07 | Public CLI | `J-review-workflow-release` → `REL-report-current-workflow-release`; use the documented Bun `-t` full-name filter and record one matching test. |
| BTR-08 | Public CLI/prerequisite | `J-review-workflow-release` → `REL-report-current-workflow-release`; isolate Bun from `PATH` and confirm non-zero failure with no compatibility runner. |
| BTR-09 | Public release history | `J-review-workflow-release` → `REL-report-current-workflow-release`; compare the v0.6.0 section with `git show v0.6.0:CHANGELOG.md` byte-for-byte. |
| BTR-10 | Public release notes | `J-review-workflow-release` → `REL-report-current-workflow-release`; inspect the v0.7.0 Unreleased `Changed` note for Bun 1.4. |
| BTR-11 | Public release notes | `J-review-workflow-release` → `REL-report-current-workflow-release`; inspect the v0.7.0 `Removed` notes for the retired integration and bounded ownership rules. |
| BTR-12 | Public release/migration | `J-review-workflow-release` → `REL-report-current-workflow-release`; reload the tagged v0.5.0 guide link and confirm no cleanup command is invented or run. |
| BTR-13 | Public release boundary | `J-review-workflow-release` → `REL-report-current-workflow-release`; compare package/lock versions and record no tag, publication, or release action. |
| BTR-14 | Public docs-as-interface | `J-review-workflow-release` → `REL-report-current-workflow-release`; read current testing docs for Bun 1.4 and the `tools` root. |
| BTR-15 | Public QA workflow | `J-review-workflow-release` → `REL-report-current-workflow-release`; it is the pending scenario reset and must receive a fresh CLI/manual walk and dated report. |
| BTR-16 | Public adoption | `J-adopt-workflow` → `ADP-adopt-workflow-safely` (canonical), with `REL-report-current-workflow-release` as release canary; inspect two disposable adoption runs for no Bun install, host edit, or `bun.lock`. |
| BTR-17 | Public CLI discovery | `J-review-workflow-release` → `REL-report-current-workflow-release`; place a failing copied test in ignored evidence and confirm root Bun discovery remains 8/115. |
| BTR-18 | Internal migration guard | Technical-only rejection contract for a tracked Vitest import; validation already proves the clean source tree and discriminating guard, with no separate user journey. |
| BTR-19 | Internal release regression guard | Technical-only mutation contract that protects the public BTR-09 history promise; release QA verifies the preserved section but does not need a second scenario. |
| BTR-20 | Public release/package | `J-review-workflow-release` → `REL-report-current-workflow-release`; parse `npm pack --dry-run --json` and inspect forbidden evidence/runtime paths. |

## Test-contract disposition

All 11 test-contract IDs are assigned once: 10 public CLI/adoption/release contracts map to the
existing records, and one source-level import contract remains technical-only.

| Contract ID | Class | Canonical mapping or internal disposition |
| --- | --- | --- |
| BTR-IT-001 | Public CLI | `J-review-workflow-release` → `REL-report-current-workflow-release`; root Bun discovery excludes copied ignored evidence. |
| BTR-IT-002 | Public CLI | `J-review-workflow-release` → `REL-report-current-workflow-release`; npm delegates to Bun and reports 115/8 with zero failures. |
| BTR-IT-003 | Internal source contract | Technical-only scan of tracked runner imports; no distinct user-visible promise or scenario reset. |
| BTR-IT-004 | Public CLI | `J-review-workflow-release` → `REL-report-current-workflow-release`; targeted `-t` selects only the matching full nested name. |
| BTR-IT-005 | Public release/package | `J-review-workflow-release` → `REL-report-current-workflow-release`; npm dependency tree contains no direct/transitive Vitest package. |
| BTR-IT-006 | Public CLI | `J-review-workflow-release` → `REL-report-current-workflow-release`; full mixed-language gate runs Bun before registered Python suites. |
| BTR-IT-007 | Public release history | `J-review-workflow-release` → `REL-report-current-workflow-release`; v0.6.0 section matches the tag byte-for-byte. |
| BTR-IT-008 | Public release metadata | `J-review-workflow-release` → `REL-report-current-workflow-release`; v0.7.0 notes and 0.6.0 package/lock authorities agree. |
| BTR-IT-009 | Public adoption | `J-adopt-workflow` → `ADP-adopt-workflow-safely` (canonical), with the release scenario reusing its result as an adjacent canary; run fresh and repeated adoption in disposable targets. |
| BTR-IT-010 | Public release/package | `J-review-workflow-release` → `REL-report-current-workflow-release`; pack dry-run excludes ignored QA evidence and Vitest artifacts. |
| BTR-E2E-001 | Public release journey | `J-review-workflow-release` → `REL-report-current-workflow-release`, with `ADP-adopt-workflow-safely` adjacent; this remains pending until the fresh walk produces dated evidence. |

## Scenario state

- `REL-report-current-workflow-release` remains `qa_status: untested`, already reset by the feature
  for this changed release promise. Keep its historical `evidence`, `last_report`, bug links, and
  fixed-bug retest fields; do not convert technical PASS into a QA verdict.
- `ADP-adopt-workflow-safely` is reset from `pass` to `untested` because `scripts/adopt.py` now
  changes the public generated-tree boundary for the Bun source pack. Preserve its historical
  evidence, bug links, `fix_status: fixed`, and `retest_status: pass` fields.
- `REL-report-current-workflow-release` records the adoption overlap with canonical owner
  `ADP-adopt-workflow-safely`; no duplicate scenario is minted.
- All other scenarios retain their existing statuses. In particular, the unrelated real
  Orca/Codex lifecycle and completed-pilot cleanup scenarios remain `blocked-verify` and are not
  reclassified by this Bun source-pack walk.

## Planned probes for the next Execute session

1. Read `docs/qa/README.md`, `J-review-workflow-release`, `J-adopt-workflow`, both mapped scenarios,
   and the feature's `spec.md`, `tests.md`, `dx.md`, and `validation.md`. Record the profile's
   CLI/manual adapter and Bun 1.4 prerequisite; do not discover or install another adapter.
2. From the active checkout, run the public `npm test`, root `bun test`, a unique `bun test -t`
   filter, and `npm run test:all` under the already supplied Bun 1.4. Capture exit codes, counts,
   ordering, and the missing-Bun non-zero boundary in checkout-owned raw evidence.
3. Put a deliberately failing `*.test.ts` copy under ignored `docs/qa/evidence/` in a disposable
   probe, reload the command output, and confirm `bunfig.toml` keeps discovery at `./tools`; remove
   only that checkout-owned probe afterward.
4. Independently read tracked `tools/**/*.test.ts` imports, `package.json`, `package-lock.json`,
   and `npm ls --all`/`npm ls vitest --all` output. Keep source-level import assertions as
   technical context, not a new QA scenario.
5. Compare the v0.6.0 changelog section with `git show v0.6.0:CHANGELOG.md`; inspect the v0.7.0
   `Changed`, `Removed`, and `Migration` notes, version fields, private-package state, and tags.
   No tag, release, publication, push, pull request, merge, deploy, or cleanup command is allowed.
6. Run `npm pack --dry-run --json`, reload its JSON, and confirm the source pack includes canonical
   Bun test/configuration authorities while excluding ignored QA evidence, Vitest artifacts, and
   `bun.lock`. Do not publish the private package or contact a registry.
7. Use a separate checkout-owned disposable Git target for `python3 scripts/adopt.py <target>`;
   inspect the managed tree and printed external-security command, then repeat adoption. Confirm
   knowledge source modules arrive, Bun test/config/preload paths and `bun.lock` stay absent, the
   target's consumer-owned config/template/ignore sentinels survive, and no host setting or Bun
   installation is touched. Never invoke the printed networked installer.
8. Independently reload target bytes and checkout status after cleanup. Record only raw evidence in
   the ignored cycle directory; the fresh Execute Verifier writes the durable report and scenario
   verdicts after the observables are confirmed.

## QA Execute handoff

Dispatch a distinct fresh Verifier session with `phase: qa-execute` at branch
`build/bun-test-runner`, HEAD `f041a4b`. It must read the canonical `qa-execute` skill and use the
CLI/manual adapter declared in [`docs/qa/README.md`](../README.md), with Bun 1.4 already supplied
and npm retained as the package authority. Walk `J-review-workflow-release` and its
`REL-report-current-workflow-release` scenario, then the adjacent `J-adopt-workflow` /
`ADP-adopt-workflow-safely` canary in separate checkout-local disposable targets.

Store ignored raw evidence under `docs/qa/evidence/2026-08-27-bun-test-runner/` and write a new
durable report at `docs/qa/reports/2026-08-27-bun-test-runner.md`. Update scenario verdict fields
only after independent reloads support the expected observable. A clean walk should close
BTR-15 and BTR-E2E-001 and may pass the reset adoption canary; a contradiction becomes a bug for
an Implementer and requires a fresh technical Verifier after the fix.

Do not modify product code, tests, specs, validation, package metadata, or historical reports;
install Bun; invoke external security installation; contact remote services; inspect or mutate real
operator state; create a tag/release; publish; push; merge; deploy; or clean retained parallel
residue. Preserve the existing `blocked-verify` lifecycle statuses.

## Status

QA Plan complete. New charter is immutable. No live QA walk, report, raw evidence, product change,
release action, operator-state action, or remote action occurred in this plan phase. Technical PASS
stands; BTR-15 and BTR-E2E-001 remain pending the distinct fresh `qa-execute` session.
