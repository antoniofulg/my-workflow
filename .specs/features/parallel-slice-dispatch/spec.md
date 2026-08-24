# Parallel Slice Dispatch Specification

## Problem Statement

The workflow serializes every vertical slice even when the task graph exposes independent work.
This leaves implementers idle during long slices and reviews. The workflow needs an opt-in dispatch
plan that exposes safe inter-slice concurrency without changing TLC task execution or weakening any
gate, Verifier, deep-review, or QA contract.

## Goals

- [ ] Freeze one of `disabled`, `safe`, or `full` in each feature workflow snapshot.
- [ ] Produce a deterministic point-in-time plan from the versioned `tasks.md` state.
- [ ] Preserve sequential tasks within each slice and serial fallback whenever safety is unproven.
- [ ] Define worker turn-end, follow-up, checkpoint sync, and evidence invalidation for capable orchestrators.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Changes to `tlc-spec-driven` task, batch, commit, or Verifier semantics | TLC remains the sequential execution engine inside each slice. |
| A provider-independent agent spawn API | No such local runtime exists; capable orchestrators consume the plan. |
| Automatic worktree creation, rebase, process, port, or database management | These are mutating executor responsibilities and need a later implementation slice. |
| Parallel deep-review cohorts | Review cadence and source-freeze rules remain unchanged. |
| Timing-based lane optimization | Reliable per-task duration data does not exist yet. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Default behavior | `disabled` | Existing features keep the proven serial workflow. | yes |
| Safe eligibility | Only independent slices or slices whose cross-slice producers are verified | Safe mode never consumes an unverified checkpoint. | yes |
| Full eligibility | A completed, gated, committed upstream task may unlock a downstream slice | Full mode accepts later sync and revalidation cost. | yes |
| Intra-slice execution | Sequential | The user explicitly chose to keep TLC unchanged. | yes |
| Waiting worker | End the turn and receive a follow-up event | Polling wastes tokens and an idle model adds no evidence. | yes |
| Sync cadence | Dependency checkpoints plus final reconciliation when needed | Rebasing every task creates churn without added safety. | yes |
| Feature workflow state | `.specs/features/` remains versioned and durable | Worktrees, gates, handoffs, and audit require shared state. | yes |
| Executor capability | Missing or inconclusive capability forces serial fallback | Parallelism is opportunistic and never a readiness requirement. | yes |

**Open questions:** none - all resolved or logged above.

## User Stories

### P1: Freeze the dispatch policy

**User Story:** As a workflow maintainer, I want each feature to freeze its dispatch mode so that
resume and delegated roles use the same policy.

**Acceptance Criteria:**

1. **PAR-01:** WHEN `[parallelization]` is absent THEN the resolver SHALL freeze `mode = "disabled"` in `workflow.json`.
2. **PAR-02:** WHEN `mode` is `disabled`, `safe`, or `full` THEN the resolver SHALL accept and freeze that exact value.
3. **PAR-03:** IF `mode` has any other value THEN the resolver SHALL exit non-zero and SHALL NOT replace an existing valid snapshot.
4. **PAR-04:** WHEN an existing feature snapshot is resumed THEN the workflow SHALL use its frozen parallelization mode without re-resolving current configuration.

**Independent Test:** Resolve fresh and resumed feature snapshots from valid, absent, and invalid configuration.

### P1: Plan ready work without changing TLC

**User Story:** As a Planner, I want a deterministic projection of ready and blocked slice tasks so
that a capable orchestrator can dispatch concurrency while every slice remains sequential.

**Acceptance Criteria:**

1. **PAR-05:** WHEN planning any mode THEN the planner SHALL expose no more than the first incomplete task of each slice as a dispatch candidate.
2. **PAR-06:** WHEN mode is `disabled` THEN the planner SHALL return one serial lane in declared task order.
3. **PAR-07:** WHEN mode is `safe` THEN the planner SHALL expose concurrent candidates only when their cross-slice producers are absent or verified.
4. **PAR-08:** WHEN mode is `full` and a declared upstream task is complete THEN the planner SHALL expose the dependent slice candidate with that task recorded as a required sync checkpoint.
5. **PAR-09:** WHILE a declared dependency is incomplete the planner SHALL mark its consumer blocked and SHALL NOT dispatch a later task from that slice.
6. **PAR-10:** IF slice metadata is missing, the dependency graph is cyclic, a write target is ambiguous, or ready candidates conflict THEN the planner SHALL return a serial fallback and identify every decisive reason.
7. **PAR-11:** WHEN the same feature state and Git head are planned twice THEN the planner SHALL emit byte-equivalent JSON.

**Independent Test:** Run fixtures covering serial, independent, cross-slice, waiting, conflict, cycle, and missing-metadata graphs.

### Planner task statuses

The planner SHALL treat task status as a dispatch state, not as evidence that a worker can be
started again:

| Task status | Planner result |
| --- | --- |
| `pending` | Candidate when slice order and dependencies allow it. |
| `in_progress` | Blocked with `in-progress:<task-id>`; never emitted as a fresh worker. |
| `waiting` | Emits `follow_up` only when every declared dependency is complete; otherwise remains blocked with `waiting-on-dependency:<task-id>`. |
| `complete` | Not a candidate; may unlock dependent tasks and full-mode checkpoints. |

### P1: Preserve workflow evidence under concurrency

**User Story:** As a delivery owner, I want parallel dispatch to preserve all existing evidence so
that reduced wall time never weakens readiness.

**Acceptance Criteria:**

1. **PAR-12:** IF no capable isolated executor accepts the plan THEN the workflow SHALL execute the existing serial path without creating a worker or worktree.
2. **PAR-13:** WHEN a worker reaches a task whose dependency is unavailable THEN the worker SHALL report its clean committed checkpoint, end its turn, and receive follow-up only after the dependency event.
3. **PAR-14:** WHEN a downstream slice consumes a newer upstream checkpoint THEN the orchestrator SHALL synchronize before the dependent task and SHALL rerun the affected gate.
4. **PAR-15:** IF synchronization, integration, or remediation changes a reviewed tree THEN the workflow SHALL invalidate and repeat every affected gate, Verifier, or deep-review verdict.
5. **PAR-16:** The workflow SHALL preserve one atomic commit and scoped gate per task, one technical Verifier per code-changing slice, deep-review at the frozen groups, final QA, and one full gate on the final tree.

**Independent Test:** Inspect the autonomous contract and run its shared contract suite against the configured planner behavior.

## Implicit Requirement Dimensions

| Dimension | Resolution |
| --- | --- |
| Input validation & bounds | Mode enum, task IDs, slice IDs, statuses, dependencies, and exact write paths are validated. |
| Failure / partial-failure states | Invalid or inconclusive plans fail closed to the serial path with reasons. |
| Idempotency / retry | Planning the same state and Git head is byte deterministic. |
| Auth boundaries & rate limits | N/A because all inputs are local versioned workflow files. |
| Concurrency / ordering | One candidate per slice; declared dependencies and sync checkpoints gate dispatch. |
| Data lifecycle / expiry | `workflow.json` and feature specs remain versioned; plans are ephemeral projections. |
| Observability | The JSON plan names ready tasks, blocked tasks, fallback state, and decisive reasons. |
| External-dependency failure | Missing executor or isolation capability preserves serial execution. |
| State-transition integrity | Pending, ready, waiting, complete, needs-sync, and invalidated transitions are guarded by events. |

## Edge Cases

- IF two candidates declare the same exact write path THEN the planner SHALL select serial fallback.
- IF a task depends on an unknown task ID THEN the planner SHALL select serial fallback and name the unknown ID.
- IF a worker stops while its worktree is dirty THEN the orchestrator SHALL refuse waiting status and select serial recovery.
- WHEN the last consumed dependency checkpoint already equals the final upstream base THEN final reconciliation SHALL be a no-op.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| PAR-01 | Freeze the dispatch policy | Design | Complete |
| PAR-02 | Freeze the dispatch policy | Design | Complete |
| PAR-03 | Freeze the dispatch policy | Design | Complete |
| PAR-04 | Freeze the dispatch policy | Design | Complete |
| PAR-05 | Plan ready work | Design | Complete |
| PAR-06 | Plan ready work | Design | Complete |
| PAR-07 | Plan ready work | Design | Complete |
| PAR-08 | Plan ready work | Design | Complete |
| PAR-09 | Plan ready work | Design | Complete |
| PAR-10 | Plan ready work | Design | Complete |
| PAR-11 | Plan ready work | Design | Complete |
| PAR-12 | Preserve workflow evidence | Design | Pending |
| PAR-13 | Preserve workflow evidence | Design | Pending |
| PAR-14 | Preserve workflow evidence | Design | Pending |
| PAR-15 | Preserve workflow evidence | Design | Pending |
| PAR-16 | Preserve workflow evidence | Design | Pending |

**Coverage:** 16 total, 16 mapped to design, 0 unmapped.

## Success Criteria

- [ ] Omitted configuration produces the same serial execution policy as today.
- [ ] All planner fixtures produce deterministic ready, blocked, checkpoint, or fallback output.
- [ ] No file under `.agents/skills/tlc-spec-driven/` changes.
- [ ] Existing workflow, review, QA, and full-gate suites remain green.
