---
id: CFG-freeze-feature-workflow
area: CFG
title: Freeze and safely resume a feature workflow
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: Resolution atomically produces matching JSON output and feature state with the selected parallelization mode, which remains stable on resume until an explicit refresh.
entry_points: .my-workflow.toml; .agents/skills/workflow-config/scripts/workflow_config.py; .specs/features/<slug>/workflow.json; .agents/skills/workflow-config/SKILL.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-21-configurable-workflow/resolver-session.md; docs/qa/evidence/2026-08-24-parallel-slice-dispatch/session.md
last_report: docs/qa/reports/2026-08-24-parallel-slice-dispatch.md
overlaps:
---

Covers `CWF-STATE-1` through `CWF-STATE-4` plus `PAR-01` through `PAR-04`: complete snapshot fields,
disabled default, supported modes, invalid-mode preservation, repeat stability, and frozen resume
until a human requests refresh. Parallelization coverage passed through the public resolver CLI on
2026-08-24.
