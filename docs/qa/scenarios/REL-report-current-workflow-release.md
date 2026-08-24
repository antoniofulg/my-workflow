---
id: REL-report-current-workflow-release
area: REL
title: Report the current workflow release consistently
persona: Repository reader
journey: J-review-workflow-release
expected: The newest changelog release matches both package authorities and shipped public contracts, while the full test command scopes discovery to canonical tests under tools.
entry_points: CHANGELOG.md; package.json; package-lock.json
qa_status: fail
bug_ids: BUG-20260824-release-overstates-lifecycle-qa
fix_status: pending
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-24-release-0-4-0/session.md
last_report: docs/qa/reports/2026-08-24-release-0-4-0.md
overlaps:
---

Version-neutral owner for public release consistency. For release `0.4.0`, the reader compares the
newest changelog heading with both package authorities and checks its claims against the shipped
public contracts. The release walk reuses the current ai-memory handoff and adoption verdicts as
canaries instead of repeating their feature-level runtime probes.

QA on 2026-08-24 found that the release changelog overstates durable runtime QA coverage for
lifecycle controls. See `BUG-20260824-release-overstates-lifecycle-qa`.
