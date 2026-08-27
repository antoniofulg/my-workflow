# Host-Agnostic Slice Parallelization Context

**Gathered:** 2026-08-26
**Spec:** `.specs/features/host-agnostic-slice-parallelization/spec.md`
**Status:** Approved input for design

## Feature Boundary

Keep the existing deterministic slice scheduler and make its execution-host boundary explicit.
Automatic Orca and Maestri adapters remain capability-gated. Coordinator-assisted Orca becomes the
default whenever the task DAG exposes safe independent slices.

## Implementation Decisions

### Reliability

- TLC tasks remain sequential inside each slice.
- Technical Verifier, grouped deep-review, gates, and final QA remain unchanged.
- `assisted` is the default mode. `disabled` is the operator's explicit sequential override.
- `safe` and `full` keep their existing automatic-adapter meaning.
- Fewer than two ready slices, write/resource conflicts, unavailable isolation, or any uncertifiable
  assisted mechanic falls back to serial execution.

### Orca

- Orca `1.4.188` is known incompatible with the required argv worker lifecycle.
- A new installed version is only a candidate; an explicit lifecycle canary proves actual support.
- A successful canary is cached locally by installed runtime identity and invalidated by an update.
- Until that update, the main agent coordinates eligible slices through direct Orca worktree and
  terminal commands by default. The automatic adapter remains unsupported.
- The coordinator owns every worker and checkpoint. A parked worker ends its turn and resumes in the
  same terminal only after the declared dependency is completed and verified.
- Complete packets live in coordinator-owned files outside slice worktrees. Only short fixed-shape
  pointers cross `terminal send`; mutation failures reconcile through read-only inspection, never retry.

### Maestri

- Floors are the only allowed isolation boundary; the adapter never creates a manual Git worktree.
- Human-readable output is not accepted as a lifecycle receipt.
- The current CLI remains unsupported because it lacks structured floor/lifecycle receipts and floor deletion.

### Cleanup

- A canary must release its worker and remove its disposable checkout before recording PASS.
- Missing cleanup proof blocks the adapter and reports the exact retained resource.
- Assisted cleanup removes only clean coordinator-owned worktrees after their commits are integrated;
  ambiguity retains the resource and returns the lane to serial recovery.

### Agent's Discretion

- Parameter names and compact JSON field names for the shipped assisted probe.
- Exact bounded canary timeout and reusable canary objective text.

## Specific References

- Orca PR `stablyai/orca#16548` is the candidate upstream fix.
- `BUG-20260827-orca-terminal-send-truncates-claude-worker-packet` remains owned by Orca; this
  workflow does not remediate it.
- The Maestri SAFE pilot proved concurrent floors but failed its operational contract after a manual
  sensor worktree and unavoidable UI-only floor cleanup.

## Deferred Ideas

- Full Maestri execution support after the CLI exposes structured lifecycle receipts and floor deletion.
- Runtime, port, and database allocation beyond the existing consumer resource-provider protocol.
