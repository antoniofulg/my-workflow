---
id: REL-report-current-workflow-release
area: REL
title: Report the current workflow release consistently
persona: Repository reader
journey: J-review-workflow-release
expected: The newest changelog release matches the package manifest and Bun lockfile, while `bun run test:all` scopes discovery to canonical tests under scripts and tools.
entry_points: CHANGELOG.md; package.json; bun.lock
qa_status: untested
bug_ids: BUG-20260824-release-overstates-lifecycle-qa; BUG-20260825-adoption-omits-parallel-pilot
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
overlaps:
---

Version-neutral owner for public release consistency. For release `0.7.0`, the reader compares the
newest changelog heading with the package manifest and Bun lockfile and checks its claims against
the shipped public contracts. The release walk reuses the current ai-memory handoff and adoption verdicts as
canaries instead of repeating their feature-level runtime probes.

Release `0.7.0` changes this promise and resets it to `untested`. The next independent QA Execute
session must verify identity, package membership, adoption, `bun run test:all`, and every
hybrid-slice release-note claim. The real Orca/Codex two-lane lifecycle and completed-pilot cleanup
remain `blocked-verify`; release QA may confirm that boundary but cannot convert it to a pass or
claim a completed pilot.

The prior `0.6.0` verdict and its evidence remain historical record below; this release reset
clears only the current metadata pointers until the independent `0.7.0` release walk completes.

The 2026-08-29 `0.7.0` release report and its raw evidence remain preserved as historical
artifacts; they do not establish the current verdict. Fresh QA must rerun the release walk before
this scenario can leave `untested`.

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
