# LESSONS - auto-maintained by scripts/lessons.py

> Machine-owned. Do NOT hand-edit. Changes are overwritten on the next `lessons.py` write.
> Canonical state lives in `.specs/lessons.json`. Edit lessons only via the script.
> promote_threshold=2 distinct features · window_days=45 · quarantine_threshold=2

## Confirmed (load these at Specify/Design)

Corroborated across multiple features. Safe to apply as guidance.

_none_

## Candidates (under observation - do NOT load as guidance yet)

Seen once or not yet corroborated. Tracked, not trusted.

### L-001 - Scope canonical test discovery so ignored QA evidence cannot change the gate.
- signal: `gate_fail` · recurrence: 1 feature(s) · scope: `release` · harmful: 0
- features: release-0.3.6
- evidence: .specs/features/release-0.3.6/validation.md:65 (release)
- last seen: 2026-08-23T06:43:47Z

### L-002 - Run diff hygiene across the full release range after previously ignored artifacts become tracked.
- signal: `gate_fail` · recurrence: 1 feature(s) · scope: `release` · harmful: 0
- features: release-0.3.6
- evidence: .specs/features/release-0.3.6/validation.md:66 (release)
- last seen: 2026-08-23T06:43:47Z

### L-003 - Evaluate dependency eligibility before write conflicts so blocked consumers cannot become dispatch candidates.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `planner` · harmful: 0
- features: parallel-slice-dispatch
- evidence: .specs/features/parallel-slice-dispatch/validation.md:103 (PAR-09) (planner)
- last seen: 2026-08-24T05:56:15Z

### L-004 - Assert the complete ordered fallback reason set for malformed task graphs.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `planner` · harmful: 0
- features: parallel-slice-dispatch
- evidence: .specs/features/parallel-slice-dispatch/validation.md:104 (PAR-10) (planner)
- last seen: 2026-08-24T05:56:15Z

### L-005 - Define and assert dispatch behavior for every accepted task status.
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `planner` · harmful: 0
- features: parallel-slice-dispatch
- evidence: .specs/features/parallel-slice-dispatch/validation.md:152 (planner)
- last seen: 2026-08-24T05:56:15Z

### L-006 - Pin every waiting-worker checkpoint and event precondition with an exact contract assertion.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `orchestration` · harmful: 0
- features: parallel-slice-dispatch
- evidence: .specs/features/parallel-slice-dispatch/validation.md:274 (PAR-13) (orchestration)
- last seen: 2026-08-24T05:56:15Z

### L-007 - Assert checkpoint synchronization ordering and the affected gate rerun before continuation.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `orchestration` · harmful: 0
- features: parallel-slice-dispatch
- evidence: .specs/features/parallel-slice-dispatch/validation.md:275 (PAR-14) (orchestration)
- last seen: 2026-08-24T05:56:15Z

### L-008 - Assert reviewed-tree invalidation and repeated evidence before the next workflow stage.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `orchestration` · harmful: 0
- features: parallel-slice-dispatch
- evidence: .specs/features/parallel-slice-dispatch/validation.md:276 (PAR-15) (orchestration)
- last seen: 2026-08-24T05:56:16Z

### L-009 - Assert conditional reconciliation no-ops so unconditional rebases fail the contract suite.
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `orchestration` · harmful: 0
- features: parallel-slice-dispatch
- evidence: .specs/features/parallel-slice-dispatch/validation.md:310 (orchestration)
- last seen: 2026-08-24T05:56:16Z

### L-010 - Use an otherwise valid snapshot when testing feature identity rejection.
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `planner` · harmful: 0
- features: parallel-slice-dispatch
- evidence: .specs/features/parallel-slice-dispatch/validation.md:518 (planner)
- last seen: 2026-08-24T05:56:16Z

### L-011 - Use an otherwise valid snapshot when testing schema version rejection.
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `planner` · harmful: 0
- features: parallel-slice-dispatch
- evidence: .specs/features/parallel-slice-dispatch/validation.md:519 (planner)
- last seen: 2026-08-24T05:56:16Z

### L-012 - Assert persisted intent at every external-effect boundary, not only one representative boundary
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `workflow-executor` · harmful: 0
- features: parallel-slice-executor
- evidence: validation.md:M2 (workflow-executor)
- last seen: 2026-08-24T12:17:07Z

### L-013 - Exercise pending-receipt reconciliation for every effect type before claiming restart safety
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `workflow-executor` · harmful: 0
- features: parallel-slice-executor
- evidence: validation.md:M3 (workflow-executor)
- last seen: 2026-08-24T12:17:07Z

### L-014 - Validate and redact recovered provider receipts through the same boundary as fresh receipts
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `workflow-executor` · harmful: 0
- features: parallel-slice-executor
- evidence: validation.md:pending-acquire-recovery (workflow-executor)
- last seen: 2026-08-24T12:41:41Z

### L-015 - Exercise every public CLI verb through its observable state transition
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `workflow-executor` · harmful: 0
- features: parallel-slice-executor
- evidence: validation.md:cli-resume (workflow-executor)
- last seen: 2026-08-24T12:41:41Z

### L-016 - Assert acceptance validation precedes destructive cleanup with a negative zero-effect case
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `workflow-executor` · harmful: 0
- features: parallel-slice-executor
- evidence: validation.md:Slice-B-M1 (workflow-executor)
- last seen: 2026-08-24T15:34:19Z

### L-017 - Model provider inbox deliveries and worker output as distinct schemas at integration boundaries
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `workflow-executor` · harmful: 0
- features: parallel-slice-executor
- evidence: validation.md:Slice-B-live-delivery (workflow-executor)
- last seen: 2026-08-24T15:34:19Z

### L-018 - Use missing-field negative fixtures to prove provider receipts cannot inherit local expected values
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `workflow-executor` · harmful: 0
- features: parallel-slice-executor
- evidence: validation.md:Slice-B-R1-M2 (workflow-executor)
- last seen: 2026-08-24T15:54:47Z

### L-019 - Redact nested provider payloads before returning or persisting boundary data
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `workflow-executor` · harmful: 0
- features: parallel-slice-executor
- evidence: validation.md:Slice-B-waiter-secret (workflow-executor)
- last seen: 2026-08-24T15:54:47Z

### L-020 - Exercise every persisted lane state through checkpoint revalidation before permitting follow-up
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `workflow-executor` · harmful: 0
- features: parallel-slice-executor
- evidence: validation.md:Slice-C-R1-waiting-follow-up (workflow-executor)
- last seen: 2026-08-24T18:42:24Z

<<<<<<< HEAD
### L-021 - Exercise adapter compatibility through the executor boundary before accepting a host capability proof
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `host-adapters` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: validation.md:ranked-gap-1/MAE-01 (host-adapters)
- last seen: 2026-08-26T16:20:33Z

### L-022 - Test every lifecycle failure stage for no success receipt and exact retained-resource evidence
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `host-adapters` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: validation.md:ranked-gap-3/ORC-05 (host-adapters)
- last seen: 2026-08-26T16:20:33Z

### L-023 - Keep canonical workflow wording synchronized with contract assertions when changing published policy
- signal: `gate_fail` · recurrence: 1 feature(s) · scope: `workflow-contracts` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: validation.md:gate-check (workflow-contracts)
- last seen: 2026-08-26T16:20:33Z

### L-024 - Parse task status from canonical task records before reconciling expected task IDs
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `assisted-probe` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: validation.md AST-04 (assisted-probe)
- last seen: 2026-08-28T01:38:26Z

### L-025 - Cleanup tests must fail when any foreign branch reference changes
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `assisted-probe` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: validation.md M4 (assisted-probe)
- last seen: 2026-08-28T01:38:26Z

### L-026 - Treat only the documented not-found exit status as absence; every command error must fail closed
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `assisted-probe` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: .specs/features/host-agnostic-slice-parallelization/validation.md:121 (assisted-probe)
- last seen: 2026-08-28T02:25:41Z

### L-027 - Cleanup proof must audit host inventory, filesystem path, branch ref, and Git worktree registration from the same ownership receipt
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `assisted-probe` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: AST-06 (assisted-probe)
- last seen: 2026-08-28T02:25:41Z

### L-028 - Inject retained cleanup residue so tests fail when final registration proof is removed
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `assisted-cleanup` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: .specs/features/host-agnostic-slice-parallelization/validation.md:AST-06 sensor (assisted-cleanup)
- last seen: 2026-08-28T02:52:19Z

### L-029 - Require every task effect to prove at least one packet-declared atomic commit
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `assisted-reconciliation` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: AST-04 (assisted-reconciliation)
- last seen: 2026-08-28T02:52:19Z

### L-030 - Exercise incomplete canonical task state at the effect-reconciliation boundary
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `assisted-reconciliation` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: .specs/features/host-agnostic-slice-parallelization/validation.md:AST-04 task-state sensor (assisted-reconciliation)
- last seen: 2026-08-28T02:52:19Z
### L-031 - Failure-path tests assert the offending record identity, not only the error category
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `workflow-validation` · harmful: 0
- features: merge-alone-slices
- evidence: MAS-03/MAS-04 (workflow-validation)
- last seen: 2026-08-27T09:08:50Z

### L-032 - Failure atomicity tests assert pre-existing artifact bytes remain unchanged
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `workflow-resolution` · harmful: 0
- features: merge-alone-slices
- evidence: MAS-05/MAS-07 (workflow-resolution)
- last seen: 2026-08-27T09:08:50Z

### L-033 - Fixtures exercise every identifier shape named by the acceptance criterion
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `workflow-validation` · harmful: 0
- features: merge-alone-slices
- evidence: MAS-10 (workflow-validation)
- last seen: 2026-08-27T09:08:50Z

### L-034 - Cross-component contract tests compare producer output directly with consumer output
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `workflow-planning` · harmful: 0
- features: merge-alone-slices
- evidence: MAS-11 (workflow-planning)
- last seen: 2026-08-27T09:08:50Z

### L-035 - Boundary values named by the specification receive explicit regression assertions
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `workflow-resolution` · harmful: 0
- features: merge-alone-slices
- evidence: MAS-05 edge (workflow-resolution)
- last seen: 2026-08-27T09:08:50Z

## Quarantined (failed when applied - ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
