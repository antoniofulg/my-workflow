# Parallel Slice Executor Context

**Gathered:** 2026-08-24
**Spec:** `.specs/features/parallel-slice-executor/spec.md`
**Status:** Ready for design

## Feature Boundary

Operationalize the existing inter-slice plan through a deterministic provider-neutral coordinator,
an Orca adapter, checkpoint synchronization, resource-provider enforcement, and one real concurrency
pilot. TLC remains the sequential engine inside every slice and every existing readiness stage stays.

## Implementation Decisions

### Reliability and modes

- Parallel execution is opportunistic; any unproven capability returns to the current serial path.
- `disabled`, `safe`, and `full` retain the meanings already frozen by `AD-011`.
- Tasks stay sequential inside a slice; only another slice may advance.
- Gates, Technical Verifier, grouped deep-review, final QA, and the final full gate are not combined or skipped.

### Workers and events

- One worker owns one slice worktree.
- A waiting worker leaves a clean committed checkpoint and ends its turn.
- Dependency completion sends follow-up to the same terminal; no watchdog model polls unchanged state.
- Runtime receipts survive coordinator reboot outside versioned `.specs/` state.

### Git reconciliation

- A dependent private lane rebases onto the exact upstream task checkpoint before consuming it.
- Sync is checkpoint-driven, not per task.
- A verified slice merges into the feature integration branch so reviewed commit identities survive.
- Changed HEAD invalidates affected evidence; conflicts abort and return to serial handling.

### Provider neutrality

- The core knows actions and receipts, not Orca commands.
- Orca is the first adapter because its current CLI proves worktree, worker, event, follow-up, and cleanup capabilities.
- A future IDE implements the same protocol and conformance suite.
- Resource allocation is a consumer-owned command provider; the core accepts only a correlated lease receipt.

### Verification convergence

- Technical Verifier remediation limits belong to each blocker fingerprint, not the whole slice.
- A fingerprint is requirement, root cause, and concrete failure path; changed wording does not mint a new blocker.
- Different blockers start their own count and do not stop an unattended run that is still making progress.
- The third failed remediation of the same fingerprint halts; a reopened blocker retains its prior identity and count.

### Agent's Discretion

- Python module split, internal type names, JSON key ordering, and bounded timeout defaults.
- Exact disposable repository used by the real Orca pilot.

### Declined / Undiscussed Gray Areas → Assumptions

- The repository has no product runtime or database, so the real pilot proves Orca concurrency and lifecycle; runtime/DB allocation is proven through the provider conformance contract and must be re-walked by each consuming product.
- Multiple incomparable producer checkpoints serialize because an automatic integration order would be a code decision.

## Specific References

- Continue from `AD-011` and `.agents/skills/autonomous/references/parallelization.md`.
- Use Orca orchestration events rather than generic subagent polling for the real pilot.

## Deferred Ideas

- Additional IDE adapters after their public worktree/worker APIs are confirmed.
- Duration-aware lane packing after reliable execution telemetry exists.
