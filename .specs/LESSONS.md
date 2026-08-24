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

## Quarantined (failed when applied - ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
