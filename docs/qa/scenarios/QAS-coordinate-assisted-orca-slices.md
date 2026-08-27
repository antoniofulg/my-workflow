---
id: QAS-coordinate-assisted-orca-slices
area: QAS
title: Coordinate two assisted Orca slices through a parked dependency
persona: Workflow operator
journey: J-execute-parallel-slices
expected: With explicit authorization, two assisted Orca slices overlap through one exact parked and resumed B worker, preserve every readiness stage, integrate deterministically, and leave no owned worktree, path, branch ref, or terminal residue.
entry_points: .agents/skills/autonomous/references/parallelization.md; .specs/features/host-agnostic-slice-parallelization/workflow.json; orca worktree; orca terminal
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
overlaps: QAS-run-resource-free-parallel-orca-slices; QAS-clean-owned-parallel-slice-pilot; QAS-qualify-orca-host-before-parallel-use
---

Covers E2E-001, AST-01 through AST-07, and the user-observable ownership and cleanup outcome of
SEC-008. The canonical pilot uses the frozen implementer route `codex` / `gpt-5.6-luna` / `high`,
starts B only after `A:T1` completes and verifies, and parks it at the exact later dependency
`B:T12 depends_on A:T7`.

Assisted execution is a distinct explicitly authorized path. It never writes a compatibility PASS
and cannot turn the packet-observed Orca `1.4.190` automatic canary failure into support for the
automatic adapter. A pass requires rendered `source=screen` route proof before prompt delivery, one
worker per ready slice, a clean exact parked comment, producer-commit sync, the affected gate,
same-terminal follow-up, deterministic integration, preserved TLC readiness stages, and independent
absence checks for every owned worktree, path, branch ref, and terminal.
