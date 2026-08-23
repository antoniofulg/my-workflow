---
id: REL-report-current-workflow-release
area: REL
title: Report the current workflow release consistently
persona: Repository reader
journey: J-review-workflow-release
expected: The newest changelog release matches both package authorities and shipped public contracts, while the full test command scopes discovery to canonical tests under tools.
entry_points: CHANGELOG.md; package.json; package-lock.json
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-23-release-0-3-6/session.md
last_report: docs/qa/reports/2026-08-23-release-0-3-6.md
overlaps:
---

Version-neutral owner for public release consistency. For release `0.3.6`, the reader compares the
newest changelog heading with both package authorities, checks its claims against their public
contracts, and confirms the documented full gate cannot discover copied tests outside `tools`.
