---
id: CFG-resolve-deep-review-cadence
area: CFG
title: Resolve balanced deep-review groups before QA
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: The resolver reports the configured cadence and consecutive balanced review groups, rejects invalid inputs precisely, and leaves final review before QA.
entry_points: .my-workflow.toml.example; .my-workflow.toml; .agents/skills/workflow-config/scripts/workflow_config.py; .agents/skills/workflow-config/SKILL.md; docs/guidelines/REVIEW-ROUNDS.md
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
overlaps:
---

Covers `CWF-CAD-1` through `CWF-CAD-7`: the v2 config's default `grouped.3`, `slice`, `feature`, balanced
`grouped.N`, validation failures, final implementation review before QA, and delta-only review after
QA remediation.
