---
id: CFG-freeze-feature-workflow
area: CFG
title: Freeze and safely resume a feature workflow
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: Resolution atomically produces matching JSON output and feature state that remains stable on resume until an explicit refresh.
entry_points: .agents/skills/workflow-config/scripts/workflow_config.py; .specs/features/<slug>/workflow.json; .agents/skills/workflow-config/SKILL.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-21-configurable-workflow/resolver-session.md
last_report: docs/qa/reports/2026-08-21-configurable-workflow.md
overlaps:
---

Covers `CWF-STATE-1` through `CWF-STATE-4`: complete snapshot fields, repeat stability, preservation
of a prior valid snapshot on atomic-write failure, and frozen resume until a human requests refresh.
