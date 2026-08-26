---
id: CFG-plan-parallel-slice-dispatch
area: CFG
title: Plan parallel slices without weakening delivery
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: The read-only planner reports deterministic ready, blocked, checkpoint, or serial-fallback work while the installed orchestration contract keeps slice tasks sequential and preserves every delivery gate.
entry_points: .agents/skills/workflow-config/scripts/parallel_plan.py; .agents/skills/autonomous/references/parallelization.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-24-parallel-slice-dispatch/session.md; docs/qa/evidence/2026-08-25-parallel-slice-executor-r19/resource-plan.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r19/resource-start.json
last_report: docs/qa/reports/2026-08-25-parallel-slice-executor-final.md
overlaps: CFG-freeze-feature-workflow
---

Covers `PAR-05` through `PAR-16`: one candidate per slice, mode-specific readiness, dependency
waiting and follow-up, deterministic JSON, decisive serial fallback, checkpoint synchronization,
evidence invalidation, and preservation of TLC, Verifier, deep-review, QA, and final-gate stages.

The repository exposes no portable worker runtime. QA therefore walks the public CLI output and the
installed agent-facing policy; provider-specific worktree creation and live model behavior remain
outside this feature's public executable surface.

The planner walk passed on 2026-08-24, including deterministic ready/blocked/follow-up/checkpoint
output and preservation of sequential delivery gates. R19's public resource plan adds the current
two-ready-lane projection and confirms missing-provider serialization is decided by execution
preflight, not by planner mutation. The real worker lifecycle remains separately
`blocked-verify`.
