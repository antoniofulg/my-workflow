---
id: CFG-freeze-feature-workflow
area: CFG
title: Freeze and safely resume a feature workflow
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: Resolution derives slice count from validated task outcomes, while resume reports live remediation without re-reading Tasks and keeps model/effort routes, cadence, selected parallelization mode, and safe optional resource provider frozen until explicit refresh.
entry_points: .my-workflow.toml.example; .my-workflow.toml; .claude/agents/; .codex/agents/; .cursor/agents/; .agents/skills/workflow-config/scripts/workflow_config.py; .specs/features/<slug>/workflow.json; .agents/skills/workflow-config/SKILL.md
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
overlaps:
---

Covers `CWF-STATE-1` through `CWF-STATE-4`, `PAR-01` through `PAR-04`, and the public configuration
portion of EXE-19–EXE-21: complete snapshot fields, repeat stability, preservation of a prior valid
snapshot on atomic-write failure, and frozen resume until a human requests refresh. The 2026-08-24
resolver walk passed snapshot, mode, invalid-input, repeat, and frozen-resume checks. R19 confirmed
safe mode preserves a frozen `resource_provider: null` boundary before execution; resource-bearing
lanes serialize through the linked fallback scenario. No configured consumer provider or
resource-isolation claim is made.
`SRH-02` adds a deliberate live-state exception: `remediation.stall_attempts` appears in current CLI
JSON, never in `workflow.json`, and may change on resume without changing frozen route, cadence, or
snapshot bytes.

The 2026-08-24 evidence remains historical. The live-output and snapshot-boundary change at
`cada159` was re-walked through the CLI/manual path on 2026-08-25. Resolution reported `4`, resume
reported live `6`, and independent JSON/hash reads confirmed byte-identical frozen route, model,
effort, cadence, and snapshot with no persisted remediation key. The earlier final report remains
in `docs/qa/reports/2026-08-25-parallel-slice-executor-final.md`; the latest report is recorded above.

The merge-alone slice contract changes this current promise. A fresh QA walk must prove malformed
Tasks fail before snapshot replacement, refresh re-derives current slices, and normal resume keeps
the frozen snapshot unchanged.
