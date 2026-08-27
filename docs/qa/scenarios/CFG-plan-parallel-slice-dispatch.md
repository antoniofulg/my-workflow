---
id: CFG-plan-parallel-slice-dispatch
area: CFG
title: Plan parallel slices without weakening delivery
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: The read-only planner reports deterministic ready, blocked, checkpoint, or serial-fallback work from primary task Slice membership while the installed orchestration contract keeps slice tasks sequential and preserves every delivery gate.
entry_points: .agents/skills/workflow-config/scripts/parallel_plan.py; .agents/skills/autonomous/references/parallelization.md
qa_status: pass
bug_ids: BUG-20260827-parallel-plan-rejects-workflow-v2
fix_status: fixed
retest_status: pass
fix_commits: 100f963
evidence: docs/qa/evidence/2026-08-27-merge-alone-slices/retest-933b5ed/planner-validator-contract.json; docs/qa/evidence/2026-08-27-merge-alone-slices/retest-933b5ed/planner-resolver.json; docs/qa/evidence/2026-08-27-merge-alone-slices/retest-933b5ed/planner-output-initial.json; docs/qa/evidence/2026-08-27-merge-alone-slices/retest-933b5ed/planner-output-reload.json; docs/qa/evidence/2026-08-27-merge-alone-slices/retest-933b5ed/planner-independent-read.log
last_report: docs/qa/reports/2026-08-27-merge-alone-slices.md
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

The merge-alone closure table is now validated upstream of this planner. A fresh QA walk must
confirm the planner preserves primary-task Slice membership without treating closure rows as extra
tasks or slices.

QA on 2026-08-27 failed this public path before membership output. The resolver created snapshot
version 2, but the planner accepted only version 1 and exited with `parallel plan: invalid workflow
snapshot`. See `BUG-20260827-parallel-plan-rejects-workflow-v2`; a fresh post-fix Verifier must resume
this charter and its adoption canary.

Fresh QA retest at `933b5ed` passed the fixed public boundary. A resolver-created version 2 snapshot
fed the planner twice with byte-identical output; independent reload matched validator membership
for `T1` through `T4`, preserved Slice IDs `A` and `B`, excluded `T2R1`/`TDR1`, and retained the
installed sequential-task and delivery-gate contract.
