---
id: REL-report-current-workflow-release
area: REL
title: Report the current workflow release consistently
persona: Repository reader
journey: J-review-workflow-release
expected: The newest changelog release matches the package manifest, while Bun 1.4's lockfile identifies the root package and dependency graph; the documented install, knowledge, scoped-validation, frozen-lockfile, and package commands expose the current source pack without checkout residue.
entry_points: CHANGELOG.md; README.md; package.json; bun.lock; bunfig.toml
qa_status: skipped
bug_ids: BUG-20260824-release-overstates-lifecycle-qa; BUG-20260825-adoption-omits-parallel-pilot; BUG-20260829-bun-history-gate-rejects-new-qa-charters; BUG-20260903-history-gate-forbids-resetting-baseline-scenarios; BUG-20260904-adopt-apply-requires-designer-before-migration
fix_status:
retest_status:
fix_commits:
evidence: .specs/features/shared-agents-product-profile/release.md
last_report:
overlaps:
---

QA Execute on 2026-09-04 passed release `0.9.2` at `de53cb77`. Identity, the packaged DRC-01
through DRC-04 deep-review defect closeout contract, its canonical structural assertion, private
662-file dry-run package, zero archive residue, independent reload, and the closing full gate
matched after the one permitted clean retry recovered a 5-second test timeout. The unchanged
passing 0.9.1 real 0.8.0 adoption/migration evidence was reused without rerunning adoption. No
external skill install, registry, publication, remote action, consumer write, or live Orca
operation occurred.

Release `0.10.0` preparation intentionally skips a QA Plan/Execute cycle under explicit user
direction. Scoped package and contract evidence is recorded separately by the release owner; this
scenario makes no `0.10.0` QA PASS claim. The historical `0.9.2` report and evidence remain intact.

Version-neutral owner for public release consistency. For release `0.10.0`, the reader compares the
newest changelog heading with the package manifest, checks Bun's root package and dependency graph
metadata, and checks release claims against
the shipped public contracts. The release walk reuses the current adoption verdict as a
canaries instead of repeating their feature-level runtime probes.

Release `0.10.0` changes this promise and is skipped for QA under explicit user direction. The release
owner records scoped identity, package membership, and residue evidence; no closing full gate or
deep-review claim is inferred. The historical 0.9.2 adoption and migration verdict remains the
adjacent canary.

QA Execute on 2026-09-04 passed release `0.9.1` at `7875bd9f`. Identity, 659-file private package,
real 0.8.0 skip-agents migration, seven phase skills and Claude links, strict no-write sync failure,
fresh full and incremental adoption, preserved package bytes, zero-effect probe import, installed
routing prose, independent reloads, cleanup, and the closing full gate matched. The linked migration
defect retest passed. No external skill install, registry, publication, remote action, or live Orca
operation occurred.

Release `0.9.1` changes this promise. Fresh QA Execute verified identity, package membership,
adoption including the 0.8.0 `--skip-agents` migration, `bun run test:all`, and every 0.9.1
release-note claim. The real Orca/Codex two-lane lifecycle and completed-pilot cleanup remain
`blocked-verify`; release QA did not convert those boundaries to a pass or claim a completed
pilot.

QA Execute on 2026-09-04 walked release `0.9.0` at tag `v0.9.0` (`9e391920`). Identity, frozen
install, dry-run pack, and `bun run test:all` matched. Documented Migration step 1 failed on a
real 0.8.0 adopted consumer: apply exited `2` requiring designer tables that the note adds only
in step 3. See `BUG-20260904-adopt-apply-requires-designer-before-migration`. Later migration
steps worked only after tables were added first. `scripts/install_security_skills.py` was not run.
The real Orca/Codex two-lane lifecycle and completed-pilot cleanup remain `blocked-verify`.

QA Execute on 2026-08-31 passed release `0.8.0` at `0260c8c`. Fresh reads, offline frozen install,
the full mixed-language gate, private dry-run package, layered and exact-conflict legacy adoption,
first-use cross-project machine locking, installed probe import, and final cleanup all matched the
release promise. The probe import made zero Orca calls; no live Orca run, remote action, external
skill installation, or package publication occurred. Both live-host scenarios remain
`blocked-verify` with pending retests.

The 2026-08-29 Bun tooling cycle refreshes this still-`untested` promise: Bun 1.4 now owns install,
TypeScript execution, structural tests, the mixed-language gate, knowledge parsing, executable
resolution, and package inspection. This plan records no execution verdict.

The prior `0.6.0` verdict and its evidence remain historical record below; this release reset
clears only the current metadata pointers until the independent `0.8.0` release walk completes.

The 2026-08-29 `0.7.0` release report and its raw evidence remain preserved as historical
artifacts; they do not establish the current verdict. Fresh QA must rerun the release walk before
this scenario can leave `untested`.

QA Execute on 2026-08-29 stopped at the opening documented `bun run test:all` command. The gate
misclassified the three new Bun-cycle charters as changed historical evidence, producing 121
passes and 1 failure before any adoption, package, or installer walk. See
`BUG-20260829-bun-history-gate-rejects-new-qa-charters`.

Fresh QA retest at `761d188` passed the repaired opening gate, all documented Bun 1.4 source-pack
commands, dry-run package inspection, disposable adoption and re-adoption, adopted knowledge
execution, probe import with zero Orca calls, and the authorized-boundary security preflights. The
networked external-skill success leg was not authorized and remains explicitly untested; no
publication, release, live Orca operation, or remote action occurred.

QA on 2026-08-25 failed release `0.6.0` during fresh adoption: the package contains the public
parallel-pilot helper, but `scripts/adopt.py` does not install it. The release walk stopped at the
first product defect. See `BUG-20260825-adoption-omits-parallel-pilot` and the current report.

Fresh QA after `816afd6` passed the affected adoption journey and all remaining release probes.
Release identity, package membership, adopted exact bytes, resolver modes, effect-free fallback,
claim language, authority boundaries, and English prose agreed. The real Orca/Codex lifecycle and
completed-pilot cleanup remain `blocked-verify`; they were not rerun or converted to success.

QA on 2026-08-25 confirmed release `0.5.0` across the changelog, package authorities, canonical
assertions, clean-HEAD 293-file offline package, disposable adoption/re-adoption, current resolver,
and shipped #62-#67 contracts. Current public/versioned prose is English, the package remains
private, and no publication or remote action occurred. See
`docs/qa/reports/2026-08-25-release-0-5-0.md`.

QA on 2026-08-24 found that the release changelog overstates durable runtime QA coverage for
lifecycle controls. See `BUG-20260824-release-overstates-lifecycle-qa`.

Fresh QA on 2026-08-24 retested fix `61f2e74`. Release identity, bounded evidence categories,
package dry-run contents, disposable adoption/re-adoption, lifecycle documentation and hook-only
dry-run, reviewer-isolation pointers, and final gates passed. The original defect remains linked as
fixed history; see `docs/qa/reports/2026-08-24-release-0-4-0.md`.

The 2026-09-03 `phase-skills` QA Plan registered
`BUG-20260903-history-gate-forbids-resetting-baseline-scenarios`: the documented full gate rejects
the scenario resets that `docs/guidelines/QA-SCENARIOS.md` requires, so the source pack a reader
installs currently cannot run a compliant QA cycle. Reset to `untested` pending the 2026-09-03
cycle; prior evidence remains historical.
