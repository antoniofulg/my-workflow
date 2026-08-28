# Coordinator-assisted slice execution

This reference defines how the workflow dispatches independent vertical slices
without expanding a worker's context beyond its assigned slice.

## Roles

- The Planner owns the feature plan and ready-slice dependency graph.
- The coordinator owns admission, worktree creation, pointer delivery, parking,
  checkpoint synchronization, verification routing, integration, and cleanup.
- An Implementer owns one slice and runs that slice's tasks sequentially, with a
  scoped gate and atomic commit for every task.
- An Explorer and read-only reviewers use the clean integration checkout.
- A fresh Technical Verifier checks every code-changing slice before a dependent
  slice consumes its checkpoint.
- A fresh Deep Reviewer checks each resolved review group on the integrated tree.
  Fresh QA Plan and QA Execute sessions check the public result.

## Admission

The coordinator reads the frozen route and dispatches safe independent slices by
default. It creates persistent worktrees only for Implementers that write at the
same time. One ready slice runs in the integration checkout. Two or more
compatible ready slices start in isolated writer worktrees. Tasks within each
slice never run concurrently.

Automatic admission starts at two writers. After a healthy settle window the
coordinator may admit one additional writer, up to the configured ceiling of
four. Missing, malformed, stale, or unhealthy host evidence keeps the active
lanes running but denies any lane above two. An explicit positive integer is a
cap, not permission to bypass the health check. `disabled` is the explicit
serial mode.

Readiness is recomputed after every verified checkpoint and lane cleanup. The
next assignment comes from the current dependency-, path-, and resource-
compatible ready queue; no fixed odd/even assignment is used. A blocked slice
is parked with its dependency IDs and resumes only after the producer commit is
verified and synchronized.

## Worker packet

An Implementer receives only its slice task definitions, cited acceptance
criteria, assigned test IDs, gate, required design excerpt, and compact slice
memory. It does not receive the planning transcript, whole feature state,
unrelated slices, or a global task summary. The coordinator persists the packet
on disk and delivers a short pointer to the worker transport.

## Per-slice lifecycle

1. Validate the frozen snapshot, clean integration baseline, and ready-slice
   compatibility before effects.
2. Admit the slice serially or into an owned writer worktree.
3. Execute its tasks in order. Every task updates local task state, runs its
   declared gate, and creates one Conventional Commit.
4. Send the compact checkpoint to a fresh Technical Verifier. The Verifier is
   never the Implementer and does not fix the code it inspects.
5. Integrate only a verified checkpoint, then recompute the ready queue.
6. Release correlated resources and clean only proven-owned effects.

The last Implementer writes a compact handoff only. It does not perform
Technical Verification, Deep Review, or final QA.

## Failure and recovery

External mutations are issued at most once. A missing or transient mutation
response is settled with bounded read-only observations correlated to the same
operation, handle, repository, slice, and checkpoint. The coordinator never
retries a mutation. Contradictory or malformed evidence fails closed and keeps
state for safe cleanup.

Heavy gates use the configured resource-provider lease protocol. A lane waits or
parks when its lease is unavailable; unrelated light work remains eligible.

## Independent verification

The Technical Verifier derives evidence from the specification, cites exact
assertion locations, and runs the discrimination sensor in an isolated scratch.
Deep Review sees the integrated commit range, not a private writer tree. QA
Plan and QA Execute are separate fresh sessions. Review-remediation accounting
uses the immutable finding fingerprint and `docs/guidelines/REVIEW-ROUNDS.md`.

## Coordinator contract

The orchestrator must:

1. Resolve and freeze the workflow route before dispatch.
2. Build a bounded slice packet and persist it before pointer delivery.
3. Keep author, verifier, reviewer, and QA identities distinct.
4. Preserve operation, worktree, handle, lease, route, and commit identities.
5. Stop before destructive cleanup when ownership or clean-tree proof is absent.
6. Run the final full gate on the integrated tree and record exact commands and
   results.
