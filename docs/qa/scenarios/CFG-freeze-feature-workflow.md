---
id: CFG-freeze-feature-workflow
area: CFG
title: Freeze and safely resume a feature workflow
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: Resolution atomically produces matching JSON output with frozen delegated model and effort, and resume rejects packet drift until an explicit refresh.
entry_points: .my-workflow.toml; .claude/agents/; .codex/agents/; .cursor/agents/; .agents/skills/workflow-config/scripts/workflow_config.py; .specs/features/<slug>/workflow.json; .agents/skills/workflow-config/SKILL.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-24-agent-model-routing-local-state/session.log
last_report: docs/qa/reports/2026-08-24-agent-model-routing-local-state.md
overlaps:
---

Covers `CWF-STATE-1` through `CWF-STATE-4`: complete snapshot fields, repeat stability, preservation
of a prior valid snapshot on atomic-write failure, and frozen resume until a human requests refresh.
