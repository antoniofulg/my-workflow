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
evidence: docs/qa/evidence/2026-08-24-agent-model-routing-local-state/summary.json
last_report: docs/qa/reports/2026-08-24-agent-model-routing-local-state.md
overlaps: ADP-adopt-workflow-safely
---

Covers E2E-001 and E2E-002: local model/effort editing, template-driven native packet generation,
idempotent reporting, invalid-source and symlink containment, frozen delegated settings, explicit
drift rejection, fresh adoption, and runtime regeneration.

The `phase-skills` feature makes Claude templates carry `skills:` and `disallowedTools:` and gives `--sync-agents` a new fail-closed preflight, so the rendering promise now covers lines this scenario never walked; reset to `untested` pending the 2026-09-03 cycle. Prior evidence remains historical.
