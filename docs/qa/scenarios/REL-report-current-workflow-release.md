---
id: REL-report-current-workflow-release
area: REL
title: Report the current workflow release consistently
persona: Repository reader
journey: J-review-workflow-release
expected: The newest changelog release matches both package authorities and shipped public contracts, while the full test command scopes discovery to canonical tests under tools.
entry_points: CHANGELOG.md; package.json; package-lock.json
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-23-release-0-3-6/session.md
last_report: docs/qa/reports/2026-08-23-release-0-3-6.md
overlaps:
---

Version-neutral owner for public release consistency. For release `0.4.0`, the reader compares the
newest changelog heading with both package authorities and checks its claims against the shipped
public contracts. The release walk reuses the current ai-memory handoff and adoption verdicts as
canaries instead of repeating their feature-level runtime probes.
