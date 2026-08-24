# Parallel Slice Executor Specification

## Problem Statement

The workflow can now freeze `disabled`, `safe`, or `full` and calculate deterministic slice lanes,
but nothing executes those lanes. Autonomous still cannot create isolated worktrees, supervise one
worker per slice, resume a waiter from a dependency event, synchronize a checkpoint, or prove
runtime-resource isolation. The missing executor must be operational without moving task execution,
Technical Verifier, deep-review, or QA responsibilities out of their current TLC stages.

## Goals

- [ ] Execute eligible slice lanes through a provider-neutral deterministic coordinator.
- [ ] Ship Orca as the first worktree, worker, and event adapter without coupling the core to Orca.
- [ ] Persist enough local receipts to resume safely after a coordinator restart.
- [ ] Synchronize exact dependency checkpoints and invalidate evidence whenever a reviewed HEAD changes.
- [ ] Require explicit resource declarations and a proven provider before parallel runtime, port, or database use.
- [ ] Exercise two real Orca-managed worktrees concurrently and record the observable result.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Parallel tasks inside one slice | TLC task order remains unchanged. |
| Automatic conflict resolution | Choosing a side is a code decision; the executor aborts and serializes. |
| A universal port, runtime, or database allocator | Resource semantics belong to each consuming project; this feature defines and enforces the provider contract. |
| Provider adapters other than Orca | The core protocol and conformance tests make them possible without speculating about unavailable IDE APIs. |
| Parallel Technical Verifier, deep-review, or final QA sessions | Their existing source-freeze and cadence contracts remain authoritative. |
| Timing-based scheduling | The deterministic task graph remains the only scheduling input. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Core boundary | Provider-neutral state machine plus small action/receipt protocol | Deterministic policy can be tested without an IDE or agent runtime. | yes |
| First adapter | Orca CLI 1.4.188 contract | It exposes worktree, worker, event, follow-up, and cleanup operations today. | yes |
| Unsupported environment | Serial fallback | Parallelism remains optional and never reduces reliability. | yes |
| Worker ownership | One worker and one worktree per slice | Tasks remain sequential and a waiter can reuse its exact terminal. | yes |
| Waiting | Clean committed checkpoint, end turn, event-driven follow-up | A watchdog model turn would spend tokens without new state. | yes |
| Checkpoint synchronization | Rebase only the dependent slice onto the exact producer commit | The private consumer lane can absorb the dependency before using it. | yes |
| Slice integration | Merge the verified slice into the feature integration branch | Commit identities used by verification remain intact. | yes |
| Runtime state | Atomic local file under the Git common directory | Host-specific terminal, worktree, and lease IDs must survive reboot but never enter versioned specs. | yes |
| Resource isolation | Explicit task metadata and consumer-owned provider receipt | Orca advertises `workspace-ports.v1` but exposes no proven public port/DB reservation command. | yes |
| Real pilot boundary | Prove concurrent Orca worktrees, worker events, follow-up, and cleanup; report runtime/DB limitations honestly | This repository has no product server or database to isolate. | yes |

**Open questions:** none - unavailable resource allocation is handled by the specified capability fallback.

## User Stories

### P1: Decide and persist safe executor actions

**User Story:** As an autonomous coordinator, I want deterministic actions and durable local receipts
so that a restart never duplicates a worker, worktree, or resource lease.

**Acceptance Criteria:**

1. **EXE-01:** WHEN mode is `disabled` THEN the coordinator SHALL return the serial action and SHALL NOT call any worktree, worker, event, Git, or resource adapter.
2. **EXE-02:** WHEN a safe or full plan is valid THEN the coordinator SHALL expose at most one active worker receipt per slice and SHALL preserve declared task order inside that slice.
3. **EXE-03:** BEFORE performing an external action the coordinator SHALL persist an idempotency key derived from feature, slice, task, action, and source checkpoint.
4. **EXE-04:** WHEN the coordinator restarts THEN it SHALL reconcile persisted receipts with the adapter and SHALL NOT recreate an accepted worktree, worker, or lease.
5. **EXE-05:** IF runtime state is malformed, belongs to another repository or feature, or cannot be reconciled THEN the coordinator SHALL select serial recovery and name the decisive reason.

**Independent Test:** Drive the same plan twice through a fake adapter, restart from persisted state, and assert identical actions with one effect per idempotency key.

### P1: Operate Orca worktrees and worker events

**User Story:** As a workflow maintainer, I want Orca to execute the provider-neutral actions so that
eligible slices can advance concurrently without agent polling.

**Acceptance Criteria:**

1. **EXE-06:** WHEN a lane becomes ready THEN the coordinator SHALL derive and validate one child Git worktree destination from the recorded base before creating it, and the Orca adapter SHALL attach its worker only to that existing worktree.
2. **EXE-07:** WHEN worktree creation succeeds THEN the coordinator and adapter SHALL validate and return the exact worktree, branch, run, task, dispatch, terminal, and source-HEAD receipt before the lane becomes running.
3. **EXE-08:** WHEN Orca reports `worker_done` THEN the adapter SHALL read the worker result, correlate it to the declared task, and release the worker only after the coordinator accepts the receipt.
4. **EXE-09:** WHEN a worker reports a clean waiter THEN the coordinator SHALL mark the lane waiting, end that worker turn, and SHALL send follow-up to the same terminal only after the declared dependency event.
5. **EXE-10:** WHEN no dependency event is available THEN the adapter SHALL use Orca's blocking event wait and SHALL NOT poll through model turns.
6. **EXE-11:** IF a receipt is missing, mismatched, dirty, duplicated, escalated, or failed THEN the coordinator SHALL halt that lane and select serial recovery without starting a replacement worker.

**Independent Test:** Exercise every command and receipt branch against a recording Orca CLI double, then run a real two-worktree Orca pilot.

### P1: Synchronize checkpoints without stale evidence

**User Story:** As a delivery owner, I want dependent slices synchronized at declared checkpoints so
that no task consumes missing upstream work and no review verdict survives a changed tree.

**Acceptance Criteria:**

1. **EXE-12:** BEFORE a full-mode consumer starts a task with `sync_after` THEN the Git adapter SHALL verify a clean consumer worktree and rebase it onto the exact recorded producer commit.
2. **EXE-13:** WHEN the producer commit is already an ancestor of the consumer HEAD THEN checkpoint synchronization SHALL be a no-op.
3. **EXE-14:** IF checkpoint rebase conflicts or changes an undeclared path THEN the adapter SHALL abort the rebase, restore the pre-sync HEAD, and halt the lane with a serial-recovery receipt.
4. **EXE-15:** WHEN checkpoint synchronization changes HEAD THEN the coordinator SHALL invalidate the affected gate, Technical Verifier, and deep-review receipts and SHALL require the affected gate before follow-up.
5. **EXE-16:** WHEN a slice is technically verified THEN the Git adapter SHALL merge its preserved commits into the feature integration branch in deterministic slice order.
6. **EXE-17:** IF final slice integration conflicts THEN the Git adapter SHALL abort the merge and SHALL leave conflict resolution to the serial workflow.

**Independent Test:** Use disposable Git repositories to cover exact-commit rebase, ancestor no-op, conflict abort, evidence invalidation, deterministic merge, and unchanged pre-operation trees after failures.

### P1: Prove resource isolation before concurrency

**User Story:** As a consuming project owner, I want each lane to declare and acquire its resources
so that one checkout cannot silently test another checkout's runtime or data.

**Acceptance Criteria:**

1. **EXE-18:** WHEN a lane declares `Resources: none` THEN the coordinator SHALL permit worktree concurrency without acquiring a runtime lease.
2. **EXE-19:** BEFORE starting a lane that declares runtime, port, or database resources THEN the coordinator SHALL call the configured provider with an argv-only request containing repository, feature, slice, task, worktree, and idempotency key.
3. **EXE-20:** WHEN the provider succeeds THEN the coordinator SHALL accept only a correlated JSON receipt with a unique lease ID, declared resource names, prepared-worktree confirmation, and redacted environment keys.
4. **EXE-21:** IF the provider is absent, unsupported, times out, emits malformed data, reuses a live lease, or fails cleanup THEN the coordinator SHALL refuse parallel dispatch and SHALL report serial fallback.
5. **EXE-22:** WHEN a worker is accepted, halted, or abandoned THEN the coordinator SHALL release its lease exactly once and SHALL retain cleanup evidence.

**Independent Test:** Run a command-provider double for success, duplication, malformed data, timeout, and cleanup, and prove resource-bearing lanes never start without an accepted lease.

### P1: Continue unattended while verification converges

**User Story:** As an operator leaving an autonomous run unattended, I want verification limits
scoped to the blocker that is not converging so unrelated findings do not waste the delivery window.

**Acceptance Criteria:**

1. **EXE-23:** WHEN a Technical Verifier reports a blocking finding THEN the workflow SHALL fingerprint it by requirement, root cause, and concrete failure path and SHALL persist its failed-remediation count.
2. **EXE-24:** WHEN a different blocker fingerprint appears after another closes THEN its count SHALL start at one and the autonomous run SHALL continue through the approved local remediation loop.
3. **EXE-25:** IF the same blocker fingerprint fails three remediation attempts THEN the workflow SHALL halt for human direction; wording changes or reopening the same requirement, root cause, and failure path SHALL retain that fingerprint and count.

**Independent Test:** Inspect the canonical review rule, every TLC/autonomous pointer, and the public workflow documentation for one blocker-scoped convergence contract with no global three-round wording.

## Security Surfaces

| ID | Surface | Control | Requirements |
| --- | --- | --- | --- |
| S1 | Local workflow configuration and executor state | Strict schema, atomic state, fail-closed recovery | SEC-001, SEC-002 |
| S6 | Git, subprocess, and filesystem sinks | Fixed executable allowlist, argv execution without shell, validated repository/worktree paths | SEC-003, SEC-004 |
| S9 | Orca and consumer resource providers | Correlated receipts, idempotency keys, timeout, explicit cleanup | SEC-005, SEC-006 |
| S11 | Worktrees, workers, runtimes, ports, and databases | One isolated lease per lane; serial fallback when isolation is unproven | SEC-007, SEC-008 |

## Implicit Requirement Dimensions

| Dimension | Resolution |
| --- | --- |
| Input validation & bounds | Enum, repository identity, paths, IDs, events, receipts, resource names, and argv are validated before effects. |
| Failure / partial-failure states | Every uncorrelated, dirty, conflicting, or unsupported state halts its lane and returns serial recovery. |
| Idempotency / retry | Persisted keys make worktree, worker, follow-up, sync, acquire, and release effects at-most-once across restart. |
| Auth boundaries & rate limits | Local adapters inherit the operator's authority; the executor grants no remote authority and applies bounded waits/timeouts. |
| Concurrency / ordering | One worker per slice; TLC tasks remain ordered; dependency events and exact checkpoints gate follow-up. |
| Data lifecycle / expiry | Host-specific runtime state stays under Git common state; terminal cleanup retains a bounded receipt, not worker transcripts or secrets. |
| Observability | Every transition records action, correlation IDs, prior/new state, head, fallback reason, and redacted lease evidence. |
| External-dependency failure | Orca or resource-provider failure serializes; no replacement effect is guessed. |
| State-transition integrity | Only declared transitions among ready, running, waiting, needs_sync, invalidated, complete, failed, and serial are accepted. |

## Edge Cases

- IF two lanes return the same worktree, branch, terminal, dispatch, or live lease ID THEN both receipts SHALL be rejected and execution SHALL serialize.
- IF an external path resolves outside the declared repository/worktree roots or through an unsafe symlink THEN the action SHALL fail before the first write.
- IF a worker result names a task other than its dispatched task THEN the lane SHALL halt without updating `tasks.md`.
- IF more than one incomparable producer checkpoint must be synchronized into one consumer THEN the executor SHALL select serial integration rather than invent a rebase order.
- WHEN a blocking event wait times out with no new event THEN state SHALL remain unchanged and no model polling instruction SHALL be emitted.
- WHEN resource cleanup is retried after an accepted release THEN the provider SHALL return the existing release receipt without a second destructive effect.
- IF an adapter command exposes a credential-shaped value THEN logs and persisted receipts SHALL contain only the key name and redaction marker.

## Security Requirements

1. **SEC-001:** Malformed or foreign runtime state is rejected before any adapter effect.
2. **SEC-002:** Runtime-state replacement is atomic and remains outside versioned feature artifacts.
3. **SEC-003:** External commands execute as validated argv arrays with `shell=False` and bounded timeouts.
4. **SEC-004:** A deterministic Git worktree destination is resolved, bounded, and checked for unsafe symlinks before the first worktree writer or worker process; adapters receive only that validated checkout.
5. **SEC-005:** Every provider response is correlated to the current idempotency key and declared lane.
6. **SEC-006:** Logs, errors, and state redact environment values and worker transcript bodies.
7. **SEC-007:** A resource-bearing lane cannot start until its unique lease and prepared worktree are proven.
8. **SEC-008:** Cleanup is idempotent and targets only receipts owned by the current feature and lane.

## Requirement Traceability

| Requirement ID | Design component | Planned slice | Status |
| --- | --- | --- | --- |
| EXE-01 | Coordinator state and receipts | A | Complete |
| EXE-02 | Coordinator state and receipts | A | Complete |
| EXE-03 | Coordinator state and receipts | A | Complete |
| EXE-04 | Coordinator state and receipts | A | Complete |
| EXE-05 | Coordinator state and receipts | A | Complete |
| EXE-06 | Orca adapter | B | Complete |
| EXE-07 | Orca adapter | B | Complete |
| EXE-08 | Orca adapter | B | Complete |
| EXE-09 | Orca adapter | B | Complete |
| EXE-10 | Orca adapter | B | Complete |
| EXE-11 | Orca adapter | B | Complete |
| EXE-12 | Git checkpoint and integration adapter | C | Planned |
| EXE-13 | Git checkpoint and integration adapter | C | Planned |
| EXE-14 | Git checkpoint and integration adapter | C | Planned |
| EXE-15 | Git checkpoint and integration adapter | C | Planned |
| EXE-16 | Git checkpoint and integration adapter | C | Planned |
| EXE-17 | Git checkpoint and integration adapter | C | Planned |
| EXE-18 | Resource provider and autonomous integration | D | Planned |
| EXE-19 | Resource provider and autonomous integration | D | Planned |
| EXE-20 | Resource provider and autonomous integration | D | Planned |
| EXE-21 | Resource provider and autonomous integration | D | Planned |
| EXE-22 | Resource provider and autonomous integration | D | Planned |
| SEC-001 | Coordinator state and receipts | A | Complete |
| SEC-002 | Coordinator state and receipts | A | Complete |
| SEC-003 | Safe process and path boundary | A | Complete |
| SEC-004 | Safe process and path boundary | A | Complete |
| SEC-005 | Orca adapter | B | Complete |
| SEC-006 | Orca adapter | B | Complete |
| SEC-007 | Resource provider | D | Complete |
| SEC-008 | Resource provider | D | Complete |
| EXE-23 | Review convergence policy | A | Complete |
| EXE-24 | Review convergence policy | A | Complete |
| EXE-25 | Review convergence policy | A | Complete |

**Coverage:** 33 total requirements, 33 mapped, 0 unmapped.

## Success Criteria

- [ ] `disabled` and every unsupported or unsafe state create no parallel worker or worktree.
- [ ] Fake-adapter tests cover every transition, failure, restart, and at-most-once effect.
- [ ] Orca adapter command tests cover worktree, worker, event, follow-up, release, and recovery receipts.
- [ ] Disposable Git tests prove checkpoint rebase, conflict abort, evidence invalidation, and slice merge.
- [ ] Resource-bearing lanes cannot run without a conforming provider; `Resources: none` remains usable.
- [ ] A real Orca pilot records two concurrent isolated worktrees and terminal event cleanup.
- [ ] Distinct Technical Verifier blockers no longer consume one global remediation cap.
- [ ] TLC implementation, commit, Verifier, deep-review, and QA semantics remain unchanged.
