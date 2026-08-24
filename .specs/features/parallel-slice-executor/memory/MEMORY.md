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
- T2R4 makes review convergence fingerprint-scoped; `REVIEW-ROUNDS.md` is canonical and bridge docs must not restate its full accounting.
- T2R5 keeps the public CLI `resume` observable while allowing a minimal entrypoint-only adapter factory seam for safe-mode reconciliation tests; persisted pending worker receipts are accepted without dispatching a second effect.
- T3 attaches Orca workers only through `worker-start --worktree path:<validated-checkout>`; run/task reuse is keyed by the core idempotency key, and worker/event receipts are redacted and correlated before release or same-terminal follow-up.
- T3R1 keeps Run Delivery (`check --run`) separate from worker-read output; resume accepts only correlated successful deliveries after redacted output validation, leaves timeout/waiting unchanged, and serializes escalation or malformed receipts without release.
- T3R2 persists only redacted waiter payloads, records `end_waiter` before `waiting`, allows restart-safe dependency follow-up on the persisted terminal, and independently rejects sparse worker receipts before `running`.
- TDR1 adds strict unknown-field/duplicate Orca boundaries, durable completion/ack/worker-release replay, bounded CLI waits, real Git worktree coverage, and stdlib review-fingerprint persistence; EXE-18–22 and C/D data fields remain planned.
- TDR2 removes supported worker envelopes before strict validation, projects/redacts complete Run Deliveries, persists a pending then accepted correlated delivery-ack action, requires dispatch-owned release receipts, bounds convergence feature paths/aliases, and makes `test:python` discover every Python suite deterministically.
- T4's Git adapter validates clean worktrees, rebases one exact producer checkpoint, restores pre-operation HEAD on conflict/undeclared paths, serializes incomparable checkpoints, invalidates gate/Technical Verifier/deep-review evidence on changed HEAD, and merges verified commits in sorted slice order without squashing.
- T4R1 makes the coordinator consume exact checkpoint receipts before worker/follow-up effects, persist `current_head` and invalidated evidence, block at `gate_required` across restart, and accept only a passed gate receipt matching lane, gate, and current head; Verifier/deep-review invalidations remain.
- T4R2 preserves the lane state that existed before checkpoint invalidation, so a waiting lane returns to `waiting` only after its exact gate passes; dependency delivery then follows up once on the persisted terminal with no pre-gate effect.
