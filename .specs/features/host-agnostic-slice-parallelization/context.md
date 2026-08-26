# Host-Agnostic Slice Parallelization Context

**Gathered:** 2026-08-26
**Spec:** `.specs/features/host-agnostic-slice-parallelization/spec.md`
**Status:** Approved input for design

## Feature Boundary

Keep the existing deterministic slice scheduler and make its execution-host boundary explicit.
Orca and Maestri are selected through adapters, but neither may run parallel work until its installed
runtime proves the required lifecycle and cleanup capabilities.

## Implementation Decisions

### Reliability

- TLC tasks remain sequential inside each slice.
- Technical Verifier, grouped deep-review, gates, and final QA remain unchanged.
- Any unknown host state or incomplete cleanup capability falls back to serial execution.

### Orca

- Orca `1.4.188` is known incompatible with the required argv worker lifecycle.
- A new installed version is only a candidate; an explicit lifecycle canary proves actual support.
- A successful canary is cached locally by installed runtime identity and invalidated by an update.

### Maestri

- Floors are the only allowed isolation boundary; the adapter never creates a manual Git worktree.
- Human-readable output is not accepted as a lifecycle receipt.
- The current CLI remains unsupported because it lacks structured floor/lifecycle receipts and floor deletion.

### Cleanup

- A canary must release its worker and remove its disposable checkout before recording PASS.
- Missing cleanup proof blocks the adapter and reports the exact retained resource.

### Agent's Discretion

- Local receipt filename and compact JSON field names.
- Exact bounded canary timeout and reusable canary objective text.

## Specific References

- Orca PR `stablyai/orca#16548` is the candidate upstream fix.
- The Maestri SAFE pilot proved concurrent floors but failed its operational contract after a manual
  sensor worktree and unavoidable UI-only floor cleanup.

## Deferred Ideas

- Full Maestri execution support after the CLI exposes structured lifecycle receipts and floor deletion.
- Runtime, port, and database allocation beyond the existing consumer resource-provider protocol.
