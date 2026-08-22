---
id: CFG-resolve-deep-review-cadence
area: CFG
title: Resolve balanced deep-review groups before QA
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: The resolver reports the configured cadence and consecutive balanced review groups, rejects invalid inputs precisely, and leaves final review before QA.
entry_points: .my-workflow.toml; .agents/skills/workflow-config/scripts/workflow_config.py; .agents/skills/workflow-config/SKILL.md; docs/guidelines/REVIEW-ROUNDS.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-21-configurable-workflow/resolver-session.md
last_report: docs/qa/reports/2026-08-21-configurable-workflow.md
overlaps:
---

Covers `CWF-CAD-1` through `CWF-CAD-7`: zero-config `grouped.3`, `slice`, `feature`, balanced
`grouped.N`, validation failures, final implementation review before QA, and delta-only review after
QA remediation.
