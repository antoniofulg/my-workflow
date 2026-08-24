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
- T5 freezes `parallelization.resource_provider` as `null` or a normalized repository-relative executable, rejects unsafe paths before atomic replacement, and resumes from the frozen snapshot regardless of later config edits; old v1 snapshots normalize absent provider to `null` in memory.
- T6 makes planner task metadata explicit: `Resources: none` becomes `resources: []`, valid names are lowercased/sorted, and missing/mixed/duplicate/malformed declarations produce deterministic serial fallback before execution.
- T7 binds the CLI to a proven Orca `orchestration.contract.v1` capability gate, keeps unsupported auto mode serial with zero effects, consumes frozen Git/provider seams through the Coordinator, and hands E2E-001 to fresh QA as untested without a real author pilot.
- T7R1 moves E2E-001 off the disabled/completed feature into a disposable `parallel-pilot` fixture with frozen safe mode, two explicit resource-free lanes, planner dry-run validation, public executor interface, and exact cleanup; Orca start remains fresh-QA-only.
- T7R2 makes the pilot dry-run prove frozen source HEAD equality and returns both heads, while cleanup uses a bounded attestation for explicit repeat-safe no-op and rejects unmarked roots; no Orca pilot is run by the author.
- T7R3 binds cleanup to the setup ownership manifest's exact `A-T1`/`B-T2` worktree paths, removes only valid Git worktrees, preserves unowned siblings as residual errors, and never uses broad recursive sibling deletion.
- T7R4 requires cleanup to independently match repository HEAD, frozen workflow HEAD, and ownership source HEAD before deletion; an external tombstone records exact residual paths and retries remain false until the bounded sibling is empty.
- T7R5 proves through the public cleanup boundary that root, feature, and every exact worktree-list shape (missing, extra, duplicate, outside, reordered) reject before Git/filesystem effects or tombstone creation.
