---
id: CFG-plan-parallel-slice-dispatch
area: CFG
title: Plan parallel slices without weakening delivery
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: The read-only planner reports deterministic ready, blocked, checkpoint, or serial-fallback work while the installed orchestration contract keeps slice tasks sequential and preserves every delivery gate.
entry_points: .agents/skills/workflow-config/scripts/parallel_plan.py; .agents/skills/autonomous/references/parallelization.md
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
overlaps: CFG-freeze-feature-workflow
---

Covers `PAR-05` through `PAR-16`: one candidate per slice, mode-specific readiness, dependency
waiting and follow-up, deterministic JSON, decisive serial fallback, checkpoint synchronization,
evidence invalidation, and preservation of TLC, Verifier, deep-review, QA, and final-gate stages.

The repository exposes no portable worker runtime. QA therefore walks the public CLI output and the
installed agent-facing policy; provider-specific worktree creation and live model behavior remain
outside this feature's public executable surface.
