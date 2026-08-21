---
id: REL-report-capability-version-0-3-0
area: REL
title: Report capability version 0.3.0 consistently
persona: Repository reader
journey: J-review-workflow-release
expected: The package manifest and lockfile root both identify the workflow release as version 0.3.0.
entry_points: package.json; package-lock.json
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-20-workflow-0.3.0/session.md
last_report: docs/qa/reports/2026-08-20-workflow-0.3.0.md
overlaps:
---

Adjacent canary for the adoption journey: the distributed package metadata still identifies the
capability release consistently after setup changes.
