---
id: CFG-freeze-feature-workflow
area: CFG
title: Freeze and safely resume a feature workflow
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: Resolution atomically produces matching JSON output and feature state with the selected parallelization mode, which remains stable on resume until an explicit refresh.
entry_points: .my-workflow.toml; .agents/skills/workflow-config/scripts/workflow_config.py; .specs/features/<slug>/workflow.json; .agents/skills/workflow-config/SKILL.md
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-21-configurable-workflow/resolver-session.md
last_report: docs/qa/reports/2026-08-21-configurable-workflow.md
overlaps:
---

Covers `CWF-STATE-1` through `CWF-STATE-4` plus `PAR-01` through `PAR-04`: complete snapshot fields,
disabled default, supported modes, invalid-mode preservation, repeat stability, and frozen resume
until a human requests refresh. Earlier state coverage passed; parallelization coverage is untested.
