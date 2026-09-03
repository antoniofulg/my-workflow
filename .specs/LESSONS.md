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

### L-033 - Exercise adapter compatibility through the executor boundary before accepting a host capability proof
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `host-adapters` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: validation.md:ranked-gap-1/MAE-01 (host-adapters) (host-adapters)
- last seen: 2026-09-02T01:21:09Z

### L-034 - Test every lifecycle failure stage for no success receipt and exact retained-resource evidence
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `host-adapters` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: validation.md:ranked-gap-3/ORC-05 (host-adapters) (host-adapters)
- last seen: 2026-09-02T01:21:09Z

### L-035 - Keep canonical workflow wording synchronized with contract assertions when changing published policy
- signal: `gate_fail` · recurrence: 1 feature(s) · scope: `workflow-contracts` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: validation.md:gate-check (workflow-contracts) (workflow-contracts)
- last seen: 2026-09-02T01:21:09Z

### L-036 - Parse task status from canonical task records before reconciling expected task IDs
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `assisted-probe` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: validation.md AST-04 (assisted-probe) (assisted-probe)
- last seen: 2026-09-02T01:21:09Z

### L-037 - Cleanup tests must fail when any foreign branch reference changes
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `assisted-probe` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: validation.md M4 (assisted-probe) (assisted-probe)
- last seen: 2026-09-02T01:21:09Z

### L-038 - Treat only the documented not-found exit status as absence; every command error must fail closed
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `assisted-probe` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: .specs/features/host-agnostic-slice-parallelization/validation.md:121 (assisted-probe) (assisted-probe)
- last seen: 2026-09-02T01:21:09Z

### L-039 - Cleanup proof must audit host inventory, filesystem path, branch ref, and Git worktree registration from the same ownership receipt
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `assisted-probe` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: AST-06 (assisted-probe) (assisted-probe)
- last seen: 2026-09-02T01:21:09Z

### L-040 - Inject retained cleanup residue so tests fail when final registration proof is removed
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `assisted-cleanup` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: .specs/features/host-agnostic-slice-parallelization/validation.md:AST-06 sensor (assisted-cleanup) (assisted-cleanup)
- last seen: 2026-09-02T01:21:10Z

### L-041 - Require every task effect to prove at least one packet-declared atomic commit
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `assisted-reconciliation` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: AST-04 (assisted-reconciliation) (assisted-reconciliation)
- last seen: 2026-09-02T01:21:10Z

### L-042 - Exercise incomplete canonical task state at the effect-reconciliation boundary
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `assisted-reconciliation` · harmful: 0
- features: host-agnostic-slice-parallelization
- evidence: .specs/features/host-agnostic-slice-parallelization/validation.md:AST-04 task-state sensor (assisted-reconciliation) (assisted-reconciliation)
- last seen: 2026-09-02T01:21:10Z

### L-043 - Failure-path tests assert the offending record identity, not only the error category
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `workflow-validation` · harmful: 0
- features: merge-alone-slices
- evidence: MAS-03/MAS-04 (workflow-validation) (workflow-validation)
- last seen: 2026-09-02T01:21:10Z

### L-044 - Failure atomicity tests assert pre-existing artifact bytes remain unchanged
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `workflow-resolution` · harmful: 0
- features: merge-alone-slices
- evidence: MAS-05/MAS-07 (workflow-resolution) (workflow-resolution)
- last seen: 2026-09-02T01:21:10Z

### L-045 - Fixtures exercise every identifier shape named by the acceptance criterion
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `workflow-validation` · harmful: 0
- features: merge-alone-slices
- evidence: MAS-10 (workflow-validation) (workflow-validation)
- last seen: 2026-09-02T01:21:11Z

### L-046 - Cross-component contract tests compare producer output directly with consumer output
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `workflow-planning` · harmful: 0
- features: merge-alone-slices
- evidence: MAS-11 (workflow-planning) (workflow-planning)
- last seen: 2026-09-02T01:21:11Z

### L-047 - Boundary values named by the specification receive explicit regression assertions
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `workflow-resolution` · harmful: 0
- features: merge-alone-slices
- evidence: MAS-05 edge (workflow-resolution) (workflow-resolution)
- last seen: 2026-09-02T01:21:11Z

### L-048 - Test a rejected-input branch with a value that would pass every other check, so removing the branch changes the outcome
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `validators` · harmful: 0
- features: review-signal-trailer
- evidence: tools/test_tlc_validators.py:297 (mutant M2) (validators)
- last seen: 2026-09-03T03:33:00Z

### L-049 - When a spec validates a text format, pin where in the input it may appear and which separators are legal, or the validator's tolerance is unproven
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `validators` · harmful: 0
- features: review-signal-trailer
- evidence: .agents/skills/workflow-spec-driven/scripts/check_commit.py:50 (RST-01 trailer location) (validators)
- last seen: 2026-09-03T03:33:05Z

## Quarantined (failed when applied - ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
