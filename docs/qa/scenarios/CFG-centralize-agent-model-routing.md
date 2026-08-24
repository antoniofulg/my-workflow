---
id: CFG-centralize-agent-model-routing
area: CFG
title: Synchronize every provider agent from central model settings
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: An explicit sync renders all fifteen native model and effort fields from `.my-workflow.toml`, preserves packet instructions, reports idempotent results, and adoption preserves existing configuration.
entry_points: .my-workflow.toml; .agents/skills/workflow-config/scripts/workflow_config.py; scripts/adopt.py
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-24-agent-model-routing/qa-execute-session.md
last_report: docs/qa/reports/2026-08-24-agent-model-routing.md
overlaps: ADP-adopt-workflow-safely
---

Covers E2E-001 and E2E-002: central model/effort editing, native packet materialization, frozen
delegated settings, explicit drift rejection, fresh adoption, and byte-preserving re-adoption.
