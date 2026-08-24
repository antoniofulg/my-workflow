# Parallel Slice Executor Memory

## Durable

- Runtime coordinator state belongs under the Git common directory and must not be written into versioned feature artifacts.
- T1 establishes state/effect primitives; T2 builds coordinator and provider reconciliation on those primitives.
- State receipts use strict version 1 objects, lane transition validation, and SHA-256 action keys.

## Open risks

- Adapter effects are intentionally absent from T1; disabled or unsupported execution must return serial fallback before adapter construction.
- T2 persists action receipts before effects, redacts provider environment values, and rejects cross-lane lease cleanup.
- T2R1 requires lazy disabled-mode startup, pending receipt reconciliation, preflight path/provider checks, and terminal lease cleanup evidence.
- T2R2 derives and validates sibling Git worktree destinations before writes; Orca adapters attach workers to existing checkouts rather than allocating paths.
- T2R3 removes adapter worktree allocation entirely, validates recovered leases through the fresh-receipt normalizer, and exposes CLI resume as a distinct command result.
