---
id: REL-report-current-workflow-release
area: REL
title: Report the current workflow release consistently
persona: Repository reader
journey: J-review-workflow-release
expected: The newest changelog release matches the package manifest, while Bun 1.4's lockfile identifies the root package and dependency graph; the documented install, knowledge, full-gate, frozen-lockfile, and package commands expose the current source pack without checkout residue.
entry_points: CHANGELOG.md; README.md; package.json; bun.lock; bunfig.toml
qa_status: untested
bug_ids: BUG-20260824-release-overstates-lifecycle-qa; BUG-20260825-adoption-omits-parallel-pilot; BUG-20260829-bun-history-gate-rejects-new-qa-charters
fix_status: fixed
retest_status: pending
fix_commits: 61f2e74; 816afd6; fb4c61f
evidence: docs/qa/evidence/2026-08-29-bun-tooling-runtime-retest/opening-gate.txt; docs/qa/evidence/2026-08-29-bun-tooling-runtime-retest/release-readback.txt; docs/qa/evidence/2026-08-29-bun-tooling-runtime-retest/package-dry-run.txt; docs/qa/evidence/2026-08-29-bun-tooling-runtime-retest/adoption-summary.json; docs/qa/evidence/2026-08-29-bun-tooling-runtime-retest/security-summary.json
last_report: docs/qa/reports/2026-08-29-bun-tooling-runtime-retest.md
overlaps:
---

Version-neutral owner for public release consistency. For release `0.8.0`, the reader compares the
newest changelog heading with the package manifest, checks Bun's root package and dependency graph
metadata, and checks release claims against
the shipped public contracts. The release walk reuses the current ai-memory handoff and adoption verdicts as
canaries instead of repeating their feature-level runtime probes.

Release `0.8.0` changes this promise and resets it to `untested`. This candidate records no
execution verdict. The next independent QA Execute session must verify identity, package
membership, `bun install --frozen-lockfile`, adoption, `bun run test:all`, first-use cross-project
locking, effect-free probe import, and every 0.8.0 release-note claim. The real Orca/Codex two-lane lifecycle and
completed-pilot cleanup remain `blocked-verify`; release QA may confirm that boundary but cannot
convert it to a pass or claim a completed pilot.

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
