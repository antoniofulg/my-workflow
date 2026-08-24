---
id: CFG-centralize-agent-model-routing
area: CFG
title: Synchronize every provider agent from central model settings
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: An explicit sync renders all fifteen native model and effort fields from `.my-workflow.toml`, preserves packet instructions, reports idempotent results, and adoption preserves existing configuration.
entry_points: .my-workflow.toml; .agents/skills/workflow-config/scripts/workflow_config.py; scripts/adopt.py
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits: 1d3d832; e3f7150; 8d841b8
evidence:
last_report:
overlaps: ADP-adopt-workflow-safely
---

Covers E2E-001 and E2E-002: central model/effort editing, native packet materialization, frozen
delegated settings, explicit drift rejection, fresh adoption, and byte-preserving re-adoption.
