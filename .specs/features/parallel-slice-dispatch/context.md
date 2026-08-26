# Parallel Slice Dispatch Context

**Gathered:** 2026-08-24
**Spec:** `.specs/features/parallel-slice-dispatch/spec.md`
**Status:** Ready for design

## Feature Boundary

Add opt-in inter-slice dispatch planning above TLC. Tasks remain sequential inside every slice. A
capable orchestrator may advance another slice only when the selected mode and dependency state
permit it; otherwise the existing serial workflow runs unchanged.

## Implementation Decisions

### Reliability

- Parallelization is applied only when the graph and executor prove it safe.
- No gate, Verifier, deep-review, QA, or final readiness evidence is removed or weakened.
- `disabled` remains the default and every inconclusive state falls back to serial.

### Modes

- `disabled` preserves current serial slice execution.
- `safe` permits independent slices and verified cross-slice producers.
- `full` permits a gated, committed task checkpoint to unlock a dependent slice before its producer slice closes.
- TLC keeps tasks and batches sequential inside each slice.

### Waiting and synchronization

- A worker that reaches an unavailable dependency reports its clean checkpoint and ends its turn.
- The Planner or deterministic scheduler sends follow-up after the dependency completion event.
- Sync occurs at dependency checkpoints, not after every task.
- A final reconciliation occurs only when the upstream base advanced.
- Any changed tree invalidates affected evidence and triggers revalidation.

### Workflow state

- `.specs/features/` is versioned durable state.
- Completed feature artifacts are retained by default and archived explicitly, never auto-deleted.

### Agent's Discretion

- Exact internal Python types and JSON field ordering.
- Conservative parsing details, provided ambiguity always falls back to serial.

### Declined / Undiscussed Gray Areas → Assumptions

- Automatic worktree and process management is deferred because the repository has no portable agent runtime.
- Per-task timing optimization is deferred until reliable timestamps exist.

## Specific References

- The feasibility study remains the user's untracked `paralelizacao.md` in the original checkout and is not part of this feature diff.

## Deferred Ideas

- Provider-specific worktree/spawn executors.
- Concurrent deep-review cohorts over a frozen commit.
- Measured duration-aware lane selection.
