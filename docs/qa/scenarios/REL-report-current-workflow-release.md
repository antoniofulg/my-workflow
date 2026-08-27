---
id: REL-report-current-workflow-release
area: REL
title: Report the current workflow release consistently
persona: Repository reader
journey: J-review-workflow-release
expected: Unreleased v0.7.0 notes identify Bun 1.4 structural tests rooted at tools, package and lock metadata remain 0.6.0, adoption does not install Bun or mutate host settings, and no bun.lock is created.
entry_points: CHANGELOG.md; package.json; package-lock.json; README.md; docs/workflow/README.md
qa_status: pass
bug_ids: BUG-20260824-release-overstates-lifecycle-qa; BUG-20260825-scenario-pass-report-field; BUG-20260825-adoption-omits-parallel-pilot; BUG-20260827-scenario-pass-report-version-gate
fix_status: fixed
retest_status: pass
fix_commits: 61f2e74; 816afd6; 1593299; 17fd3f5
evidence: docs/qa/evidence/2026-08-25-release-0-6-0/session.md; docs/qa/evidence/2026-08-25-release-0-6-0/retest-package-summary.json; docs/qa/evidence/2026-08-25-release-0-6-0/retest-version-parity.json; docs/qa/evidence/2026-08-25-release-0-6-0/retest-protected-history.json; docs/qa/evidence/2026-08-25-release-0-6-0/retest-reference-scan.json; docs/qa/evidence/2026-08-25-release-0-6-0/retest-migration.json; docs/qa/evidence/2026-08-25-release-0-6-0/retest-locality.json; docs/qa/evidence/2026-08-25-release-0-6-0/retest-adoption.json; docs/qa/evidence/2026-08-27-bun-test-runner/retest-session.md; docs/qa/evidence/2026-08-27-bun-test-runner/retest-bun-test.log; docs/qa/evidence/2026-08-27-bun-test-runner/retest-npm-test.log; docs/qa/evidence/2026-08-27-bun-test-runner/retest-release-filter.log; docs/qa/evidence/2026-08-27-bun-test-runner/retest-version-guard.md; docs/qa/evidence/2026-08-27-bun-test-runner/retest-source-boundary.md; docs/qa/evidence/2026-08-27-bun-test-runner/retest-pack-summary.json; docs/qa/evidence/2026-08-27-bun-test-runner/retest-release.json; docs/qa/evidence/2026-08-27-bun-test-runner/retest-ignored-discovery.log; docs/qa/evidence/2026-08-27-bun-test-runner/retest-adoption.json; docs/qa/evidence/2026-08-27-bun-test-runner/retest-adoption-gate.log; docs/qa/evidence/2026-08-27-bun-test-runner/retest-test-all.log; docs/qa/evidence/2026-08-27-bun-test-runner/retest-hsc09.log
last_report: docs/qa/reports/2026-08-27-bun-test-runner.md
overlaps: ADP-adopt-workflow-safely
---

The current release walk covers the v0.7.0 Unreleased notes, Bun 1.4 structural test discovery
under `tools`, unchanged 0.6.0 package authorities, npm package membership, the absence of
`bun.lock`, and the host-neutral adoption boundary. It must verify these public contracts through the declared CLI adapter before
the feature closes; this scenario is intentionally `untested` until that fresh walk completes.

Version owner for public release consistency. While v0.7.0 is Unreleased, the reader compares the
pending changelog notes with both 0.6.0 package authorities and checks their claims against the
shipped public contracts. The release walk reuses the adoption verdict as a canary instead of
repeating its feature-level probes.

The v0.7.0 runner and documentation changes reset this promise to `untested`. The next independent
QA Execute session must verify identity, package membership, adoption, the Bun and full test
commands, and every parallel-executor release-note claim. The real Orca/Codex two-lane lifecycle
and completed-pilot cleanup remain `blocked-verify`; release QA may confirm that boundary but cannot
convert it to a pass or claim a completed pilot.

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
