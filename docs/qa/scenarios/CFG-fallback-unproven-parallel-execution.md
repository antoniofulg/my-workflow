---
id: CFG-fallback-unproven-parallel-execution
area: CFG
title: Fall back when parallel execution is unproven
persona: Workflow adopter
journey: J-execute-parallel-slices
expected: Disabled mode, unsupported Orca capability, missing resource metadata, or a resource-bearing lane without a provider reports the decisive serial reason and creates no worktree, worker, event, Git, or resource effect.
entry_points: .my-workflow.toml; .agents/skills/workflow-config/scripts/workflow_config.py; .agents/skills/autonomous/scripts/parallel_execute.py start; .agents/skills/autonomous/scripts/parallel_execute.py status
qa_status: pass
bug_ids: BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree
fix_status: fixed
retest_status: pass
fix_commits: 0ed8b55
evidence: docs/qa/evidence/2026-08-25-parallel-slice-executor-r19/resource-plan.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r19/resource-start.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r19/resource-status.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r19/resource-effects.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r19/resource-residue.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r18/disabled-start.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r18/disabled-status.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r18/disabled-effects.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r18/unsupported-plan.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r18/unsupported-start.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r18/unsupported-status.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r18/unsupported-effects.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r18/resource-plan.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r18/resource-start.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r18/resource-status.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r18/resource-effects.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r18/resource-residue.md; docs/qa/evidence/2026-08-25-parallel-slice-executor-r18/commands.md
last_report: docs/qa/reports/2026-08-25-parallel-slice-executor-final.md
overlaps: CFG-plan-parallel-slice-dispatch; CFG-freeze-feature-workflow
---

Covers the public fallback portions of EXE-01, EXE-05, EXE-11, EXE-19, EXE-21, and SEC-007.
The canary deliberately proves zero effects; it never supplies a fake product runtime or database
provider to turn this repository's adoption limitation into an apparent pass.

Terminal status is `pass` for all three fallback legs. R18 proved disabled mode and unsupported Orca
capability return their decisive serial reasons with empty actions, fresh-process `state: null`, and
zero new worktree/runtime/Orca effects. R19 retested two ready `Resources: runtime` lanes with
frozen provider `null`: two starts returned `missing-resource-provider` with `actions: []`, two
fresh-process statuses returned `state: null`, Run inventory stayed `12 -> 12`, worker inventory
stayed `151 -> 151`, and no lane worktree, runtime receipt, Task, Dispatch, terminal, or lease was
created. Diagnostic abort and its idempotent repeat left `residual_paths: []`.

The linked worker-start bug remains open for the separate real resource-free lifecycle; its product
root causes do not invalidate this zero-effect fallback result. Evidence: R18 and R19 reports plus
the paths listed in frontmatter.
