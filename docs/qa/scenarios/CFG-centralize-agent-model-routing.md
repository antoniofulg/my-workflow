---
id: CFG-centralize-agent-model-routing
area: CFG
title: Synchronize every provider agent from central model settings
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: An explicit sync initializes local state when needed, renders all fifteen native model and effort fields from templates plus `.my-workflow.toml`, reports idempotent results, and adoption preserves local configuration.
entry_points: .my-workflow.toml.example; .my-workflow.toml; templates/agents/; .agents/skills/workflow-config/scripts/workflow_config.py; scripts/adopt.py
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
overlaps: ADP-adopt-workflow-safely
---

Covers E2E-001 and E2E-002: local model/effort editing, template-driven native packet generation,
frozen delegated settings, explicit drift rejection, fresh adoption, and runtime regeneration.
