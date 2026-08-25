---
id: REL-report-current-workflow-release
area: REL
title: Report the current workflow release consistently
persona: Repository reader
journey: J-review-workflow-release
expected: The newest changelog release matches both package authorities and shipped public contracts, while the full test command scopes discovery to canonical tests under tools.
entry_points: CHANGELOG.md; package.json; package-lock.json
qa_status: untested
bug_ids: BUG-20260824-release-overstates-lifecycle-qa
fix_status: fixed
retest_status: pass
fix_commits: 61f2e74
evidence: docs/qa/evidence/2026-08-25-release-0-5-0/session.md
last_report: docs/qa/reports/2026-08-25-release-0-5-0.md
overlaps:
---

For the v0.6.0 removal, the next fresh QA walk must inspect the host-owned README/workflow rule and
reviewer packets, clean and repeated adoption, package dry-run membership, release-version parity,
protected historical files against the v0.5.0 tag, and the explicit final reference-scan allowlist.
This scenario is untested until the fresh QA Plan and QA Execute packets record those observables.

Version-neutral owner for public release consistency. For release `0.5.0`, the reader compares the
newest changelog heading with both package authorities and checks its claims against the shipped
public contracts. The release walk reuses the adoption verdict as a canary instead of repeating its
feature-level probes.

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
