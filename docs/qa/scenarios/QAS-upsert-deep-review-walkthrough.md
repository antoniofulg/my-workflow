---
id: QAS-upsert-deep-review-walkthrough
area: QAS
title: Upsert one Deep Review walkthrough comment
persona: Workflow operator
journey: J-run-deep-review
expected: An existing walkthrough marker causes one PATCH, an absent marker causes one POST, and neither path sends both requests or targets a null comment id.
entry_points: .agents/skills/deep-review/references/publish-github.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-22-deep-review-walkthrough-upsert/session.md
last_report: docs/qa/reports/2026-08-22-deep-review-walkthrough-upsert.md
overlaps:
---

Covers the operator-visible publication promise from issue #29. The QA adapter replaces `gh` with
a local argument logger, so both marker states are observable without GitHub access or network
mutation.
