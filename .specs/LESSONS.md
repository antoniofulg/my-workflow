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

### L-021 - Exercise every public lifecycle command through the state artifact produced by its preceding command.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `lifecycle` · harmful: 0
- features: hybrid-slice-execution
- evidence: .specs/features/hybrid-slice-execution/validation-s4.md:45 (lifecycle)
- last seen: 2026-08-28T18:16:50Z

### L-022 - Correlate every persisted external-effect identity against independent provider and Git observations before advancing state.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `lifecycle` · harmful: 0
- features: hybrid-slice-execution
- evidence: .specs/features/hybrid-slice-execution/validation-s4.md:43 (lifecycle)
- last seen: 2026-08-28T18:16:50Z

### L-023 - Assert repository containment for every writable control path, including state and log outputs.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `security` · harmful: 0
- features: hybrid-slice-execution
- evidence: .specs/features/hybrid-slice-execution/validation-s4.md:47 (security)
- last seen: 2026-08-28T18:16:51Z

### L-024 - Structural mutation-boundary checks must classify mutating helper verbs, not only direct subprocess sinks.
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `lifecycle` · harmful: 0
- features: hybrid-slice-execution
- evidence: .specs/features/hybrid-slice-execution/validation-s4.md:M3b (lifecycle)
- last seen: 2026-08-28T21:01:28Z

### L-025 - Prove cleanup exactly-once behavior with independent executable ledgers for every destructive sink.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `lifecycle` · harmful: 0
- features: hybrid-slice-execution
- evidence: .specs/features/hybrid-slice-execution/validation-s4.md:HSE-56 (lifecycle)
- last seen: 2026-08-28T21:01:28Z

### L-026 - Derive role-routing traces from the shipped routing source; never assert a trace literal constructed inside the test.
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `role-routing` · harmful: 0
- features: hybrid-slice-execution
- evidence: validation-s5.md#M4 (role-routing)
- last seen: 2026-08-28T22:13:06Z

### L-027 - Clamp restored runtime limits against current resolved policy before scheduling effects.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `scheduler` · harmful: 0
- features: hybrid-slice-execution
- evidence: validation-s3.md:HSE-18 (scheduler)
- last seen: 2026-08-28T22:58:24Z

### L-028 - Validate persisted external-resource ownership against its originating action before authorization or release.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `resource-leases` · harmful: 0
- features: hybrid-slice-execution
- evidence: validation-s3.md:HSE-40,HSE-48 (resource-leases)
- last seen: 2026-08-28T22:58:24Z

### L-029 - Preflight every adoption write target, including merge-generated files, before the first mutation.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `adoption` · harmful: 0
- features: hybrid-slice-execution
- evidence: .specs/features/hybrid-slice-execution/validation-s6.md:32 (adoption)
- last seen: 2026-08-28T23:43:48Z

### L-030 - The canonical full gate must execute the owner suite for every shipped adoption surface.
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `adoption` · harmful: 0
- features: hybrid-slice-execution
- evidence: .specs/features/hybrid-slice-execution/validation-s6.md:30 (adoption)
- last seen: 2026-08-28T23:43:48Z

### L-031 - Assert normalized path aliases separately from ordinary path normalization rejection.
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `adoption-manifest` · harmful: 0
- features: layered-workflow-adoption
- evidence: validation-s1.md:70 (adoption-manifest) (+1 more)
- last seen: 2026-08-30T04:28:35Z

### L-032 - Instrument every live publication mutation and assert the authority manifest is last.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `adoption` · harmful: 0
- features: layered-workflow-adoption
- evidence: validation-s1.md:125 (adoption) (+1 more)
- last seen: 2026-08-30T04:28:36Z

## Quarantined (failed when applied - ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
