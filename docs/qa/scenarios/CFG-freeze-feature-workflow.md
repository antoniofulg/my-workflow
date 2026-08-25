---
id: CFG-freeze-feature-workflow
area: CFG
title: Freeze and safely resume a feature workflow
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: Resolution and resume report the current remediation stall bound without persisting it, while route and cadence remain frozen and packet drift still requires an explicit refresh.
entry_points: .my-workflow.toml; .claude/agents/; .codex/agents/; .cursor/agents/; .agents/skills/workflow-config/scripts/workflow_config.py; .specs/features/<slug>/workflow.json; .agents/skills/workflow-config/SKILL.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-25-remediation-stall-bound/summary.json; docs/qa/evidence/2026-08-25-remediation-stall-bound/session.log
last_report: docs/qa/reports/2026-08-25-remediation-stall-bound.md
overlaps:
---

Covers `CWF-STATE-1` through `CWF-STATE-4`: complete snapshot fields, repeat stability, preservation
of a prior valid snapshot on atomic-write failure, and frozen resume until a human requests refresh.
`SRH-02` adds a deliberate live-state exception: `remediation.stall_attempts` appears in current CLI
JSON, never in `workflow.json`, and may change on resume without changing frozen route, cadence, or
snapshot bytes.

The 2026-08-24 evidence remains historical. The live-output and snapshot-boundary change at
`cada159` was re-walked through the CLI/manual path on 2026-08-25. Resolution reported `4`, resume
reported live `6`, and independent JSON/hash reads confirmed byte-identical frozen route, model,
effort, cadence, and snapshot with no persisted remediation key.
