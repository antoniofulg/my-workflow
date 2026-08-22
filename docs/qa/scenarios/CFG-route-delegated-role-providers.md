---
id: CFG-route-delegated-role-providers
area: CFG
title: Route delegated roles without changing provider definitions
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: The resolver reports override-over-profile-over-native routes to existing provider agent files and rejects every invalid route without fallback.
entry_points: .my-workflow.toml; .agents/skills/workflow-config/scripts/workflow_config.py
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-21-configurable-workflow/resolver-session.md
last_report: docs/qa/reports/2026-08-21-configurable-workflow.md
overlaps:
---

Covers `CWF-ROUTE-1` through `CWF-ROUTE-5`: native routing, partial profiles, explicit overrides,
provider-owned agent files, and precise failures for invalid profiles, roles, providers, or paths.
