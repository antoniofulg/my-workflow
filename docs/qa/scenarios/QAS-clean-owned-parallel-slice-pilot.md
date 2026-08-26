---
id: QAS-clean-owned-parallel-slice-pilot
area: QAS
title: Clean only the completed parallel pilot
persona: Workflow operator
journey: J-execute-parallel-slices
expected: Cleanup removes exactly the attested completed pilot workers and worktrees, preserves unrelated siblings, and reports idempotent success with no owned residue.
entry_points: tools/qa_parallel_pilot.py lifecycle-check; tools/qa_parallel_pilot.py cleanup; git worktree list
qa_status: blocked-verify
bug_ids: BUG-20260824-parallel-pilot-cleanup-allows-incomplete-lifecycle
fix_status: fixed
retest_status: pending
fix_commits: d8c848e; 1216014; 6b3f1f0; 5b7a9dd; 48e5322; a736757
evidence: docs/qa/evidence/2026-08-25-parallel-slice-executor-v060-safe-retest/pilot-identities.md; docs/qa/reports/2026-08-25-parallel-slice-executor-v060-safe-retest.md
last_report: docs/qa/reports/2026-08-25-parallel-slice-executor-v060-safe-retest.md
overlaps: QAS-run-resource-free-parallel-orca-slices
---

Covers the user-observable cleanup portion of EXE-22 and SEC-008. Cleanup may run only after the
canonical lifecycle oracle accepts exactly two terminal read-before-ack-before-release receipts.
An incomplete lifecycle retains the fixture for diagnosis rather than claiming cleanup.

This scenario is terminal `blocked-verify`: no completed two-lane lifecycle was reached, so normal
cleanup and repeat cleanup were not invoked. The product-side cleanup authorization and recovery
fences are technically fixed, but the external Orca/Codex stop boundary leaves an exact owned live
terminal. Public diagnostic abort correctly refuses with `worker-may-be-live`; this is evidence of
fail-closed safety, not cleanup success.

R14, R15, and R17 preserve separate live/prompt and recovery residues. R19's effect-free fallback
fixture is the only cleanup call with zero residue; it is not a completed-pilot cleanup and must not
close this scenario. No normal cleanup, repeated cleanup, or no-owned-residue claim exists.

The operator manually removed the retained historical pilot worktrees before the v0.6.0 safe-mode
retest. That operator-forced cleanup is not product cleanup evidence. The fresh run's lifecycle
oracle returned `complete: false` / `lifecycle-incomplete` while A/T1's exact terminal remained live
and writable. Normal cleanup and repeated cleanup were correctly not attempted. The scenario
remains `blocked-verify`; automatic cleanup is still unproven.
