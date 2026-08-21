---
id: ADP-adopt-workflow-safely
area: ADP
title: Adopt the workflow without replacing consumer-owned state
persona: Workflow adopter
journey: J-adopt-workflow
expected: A fresh target receives the workflow and re-adoption preserves its QA profile, model pins, and unrelated ignore entries.
entry_points: README.md#adopt-the-workflow; scripts/adopt.py
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-20-workflow-0.3.0/session.md
last_report: docs/qa/reports/2026-08-20-workflow-0.3.0.md
overlaps:
---

Covers safe capability discovery, managed-path review, initial profile creation, and preservation of
consumer-owned state when the workflow is adopted again.
