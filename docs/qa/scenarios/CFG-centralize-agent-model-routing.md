---
id: CFG-centralize-agent-model-routing
area: CFG
title: Synchronize every provider agent from central model settings
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: An explicit sync initializes local state when needed, renders all fifteen native model and effort fields from templates plus `.my-workflow.toml`, reports idempotent results, and adoption preserves local configuration.
entry_points: .my-workflow.toml.example; .my-workflow.toml; templates/agents/; .agents/skills/workflow-config/scripts/workflow_config.py; scripts/adopt.py
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-09-03-phase-skills/30-sync-agents.log; docs/qa/evidence/2026-09-03-phase-skills/33-sync-perturbed.log; docs/qa/evidence/2026-09-03-phase-skills/34-perturbed-diff.txt; docs/qa/evidence/2026-09-03-phase-skills/35-skills-lines.txt
last_report: docs/qa/reports/2026-09-03-phase-skills.md
overlaps: ADP-adopt-workflow-safely
---

Covers E2E-001 and E2E-002: local model/effort editing, template-driven native packet generation,
idempotent reporting, invalid-source and symlink containment, frozen delegated settings, explicit
drift rejection, fresh adoption, and runtime regeneration.

The `phase-skills` feature makes Claude templates carry `skills:` and `disallowedTools:` and gives `--sync-agents` a new fail-closed preflight, so the rendering promise now covers lines this scenario never walked; walked on 2026-09-03 and confirmed `pass`: a perturbed `.my-workflow.toml` changed only the `model` and `effort` lines of the affected packets, while `skills:` and `disallowedTools:` were carried through byte for byte. Prior evidence remains historical.
