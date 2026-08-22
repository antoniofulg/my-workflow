---
id: REL-report-capability-version-0-3-0
area: REL
title: Report capability version 0.3.0 consistently
persona: Repository reader
journey: J-review-workflow-release
expected: The package manifest and lockfile root both identify the workflow release as version 0.3.0.
entry_points: package.json; package-lock.json
qa_status: skipped
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-22-external-security-skills/session.md
last_report: docs/qa/reports/2026-08-22-external-security-skills.md
overlaps:
---

Adjacent canary for the adoption journey: the distributed package metadata still identifies the
capability release consistently after setup changes.

Retired — the literal `0.3.0` promise became stale when later releases advanced the package. The
2026-08-22 canary independently confirmed that all three current metadata locations agree on
`0.3.4`; a future QA Plan may mint a version-neutral release-consistency scenario.
