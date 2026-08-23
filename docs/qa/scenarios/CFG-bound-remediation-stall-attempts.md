---
id: CFG-bound-remediation-stall-attempts
area: CFG
title: Bound post-cap remediation with a consumer-owned stall threshold
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: The resolver reports the effective stall_attempts — declared, defaulted to 3, or 0 for unbounded — and rejects a non-integer, a negative value, or an unknown [remediation] key by name without falling back.
entry_points: .my-workflow.toml; .agents/skills/workflow-config/scripts/workflow_config.py; .my-workflow.toml.example; README.md; .agents/skills/workflow-config/SKILL.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-23-stall-based-halt/resolver-session.md
last_report: docs/qa/reports/2026-08-23-stall-based-halt.md
overlaps:
---

New promise from `AD-007`. A project owner picks its own tolerance for a stalled remediation loop in
`.my-workflow.toml` instead of editing a vendored guideline. Covers `HALT-05` and the `0`-is-unbounded
assumption: a declared value, an absent file, an absent table, an empty table, a non-integer, a
negative value, and an unknown key inside `[remediation]`.

The three consumer-facing surfaces that document the key — `README.md`,
`.agents/skills/workflow-config/SKILL.md`, `.my-workflow.toml.example` — are part of this promise: a
key that resolves correctly but is documented with a retired default is still a broken promise.
