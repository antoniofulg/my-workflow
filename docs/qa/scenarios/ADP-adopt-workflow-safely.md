---
id: ADP-adopt-workflow-safely
area: ADP
title: Adopt the workflow without replacing consumer-owned state
persona: Workflow adopter
journey: J-adopt-workflow
expected: A fresh target receives the workflow resolver, and re-adoption preserves its workflow config, QA profile, model pins, and unrelated ignore entries byte-for-byte.
entry_points: README.md#adopt-the-workflow; scripts/adopt.py; .my-workflow.toml
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-21-configurable-workflow/adoption-session.md
last_report: docs/qa/reports/2026-08-21-configurable-workflow.md
overlaps:
---

Covers `CWF-ADOPT-1` through `CWF-ADOPT-3`: resolver installation, safe capability discovery,
managed-path review, initial profile creation, preservation of `.my-workflow.toml`, and the installed
hierarchy/resolution instructions when the workflow is adopted again.
