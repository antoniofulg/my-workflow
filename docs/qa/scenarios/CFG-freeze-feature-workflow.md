---
id: CFG-freeze-feature-workflow
area: CFG
title: Freeze and safely resume a feature workflow
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: Resolution atomically produces matching JSON output and feature state with the selected parallelization mode and safe optional resource provider, which remain stable on resume until an explicit refresh.
entry_points: .my-workflow.toml; .agents/skills/workflow-config/scripts/workflow_config.py; .specs/features/<slug>/workflow.json; .agents/skills/workflow-config/SKILL.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-24-parallel-slice-dispatch/session.md; docs/qa/evidence/2026-08-25-parallel-slice-executor-r19/setup.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r19/resource-plan.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r19/resource-status.json
last_report: docs/qa/reports/2026-08-25-parallel-slice-executor-final.md
overlaps:
---

Covers `CWF-STATE-1` through `CWF-STATE-4`, `PAR-01` through `PAR-04`, and the public configuration
portion of EXE-19–EXE-21. The 2026-08-24 resolver walk passed the snapshot, mode, invalid-input,
repeat, and frozen-resume contract. R19 independently confirmed safe mode preserves a frozen
`resource_provider: null` boundary before execution; resource-bearing lanes correctly serialize
through the linked fallback scenario. No configured consumer provider or resource-isolation claim
is made.
