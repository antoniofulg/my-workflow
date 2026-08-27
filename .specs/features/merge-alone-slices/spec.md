# Merge-Alone Slice Derivation Specification

## Problem Statement

Workflow resolution currently accepts a manually chosen slice count before task planning proves the
delivery boundaries. This makes technical cohorts look like vertical slices, freezes an inflated
review cadence, and adds verification cost even when only the final combined state is worth merging.

## Goals

- [x] Derive slice count from validated merge-alone outcomes in `tasks.md`.
- [x] Keep initial resolution, refresh, resume, templates, and parallel planning consistent with one
      declared slice contract.
- [x] Preserve one-slice resolution when Tasks is correctly skipped.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Inferring product value from task names or file paths | Product value remains a Planner decision materialized in the closure table. |
| Prohibiting incremental migrations | An intermediate state remains a valid slice when it has independent value and would ship alone. |
| Re-resolving existing snapshots during resume | Frozen workflow state remains authoritative until explicit refresh. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| A present `tasks.md` without a closure table | Validation error | Silent one-slice fallback would preserve the same unrecorded judgment this feature removes. | yes — issue contract |
| Planned task identity | Primary `T\d+` tasks only | Review remediation records are not mergeable product slices and must not inflate delivery count. | yes — existing task model |
| Optional `--slices` during normal resume | Ignore for derivation; return the frozen snapshot | Resume must not read changed tasks or re-resolve cadence. | yes — acceptance criterion 6 |
| Optional `--slices` during initial resolution or refresh | Exact assertion against derived count | It can catch an operator expectation mismatch without owning the count. | yes — acceptance criterion 4 |
| Missing `tasks.md` | Exactly one slice | Tasks was auto-sized away, so no multi-slice plan exists to derive. | yes — acceptance criterion 5 |
| Active workflow snapshot version | Version 2 only; reject version 1 | Workflow resolution already writes version 2, and the prior routing decision removed fallback compatibility. Historical snapshots remain evidence and are not rewritten. | yes — AD-014 |

**Open questions:** none — all resolved by issue #71 and existing snapshot semantics.

## Implicit Requirement Dimensions

| Dimension | Resolution |
| --- | --- |
| Input validation & bounds | Slice IDs, membership, outcomes, gates, merge-alone decisions, and optional count assertions are exact and non-empty. |
| Failure / partial failure | Invalid task contracts and count mismatches fail before replacing a workflow snapshot. |
| Idempotency / retry | Repeated initial inputs derive the same count; normal resume returns the frozen snapshot. |
| Auth boundaries & rate limits | N/A — local repository files and CLI only. |
| Concurrency / ordering | N/A — resolution is an atomic local operation; parallel execution remains downstream. |
| Data lifecycle / expiry | Existing snapshots persist unchanged until explicit refresh. |
| Observability | Validation and mismatch errors name the failed closure or count. |
| External-dependency failure | N/A — standard-library parsing and repository files only. |
| State-transition integrity | Initial resolution and refresh validate current tasks; resume does not re-resolve them. |

## User Stories

### P1: Freeze Only Mergeable Delivery Units ⭐ MVP

**User Story**: As a workflow Planner, I want slice count derived from explicit merge-alone outcomes
so that review cadence follows deliverable behaviour instead of technical organization.

**Why P1**: Incorrect slice count multiplies Verifier handoffs, gates, and review cost before any
implementation begins.

**Acceptance Criteria**:

1. WHEN a validated task document contains five primary tasks, three technical cohorts, and one complete migration outcome THEN the workflow SHALL derive exactly one vertical slice.
2. WHEN a validated task document contains two outcomes that each would be merged if later work were cancelled THEN the workflow SHALL derive exactly two vertical slices.
3. IF a declared slice lacks a non-empty observable outcome, independent gate, exact `yes` merge-alone decision, or concrete reason THEN task validation SHALL fail and name the invalid slice.
4. IF a primary task belongs to zero or multiple declared slices, or a declared slice has no primary tasks, THEN task validation SHALL fail and name the inconsistent task or slice.
5. WHEN initial resolution or explicit refresh receives `--slices` THEN the resolver SHALL reject a value different from the validated derived count before replacing `workflow.json`.
6. WHEN initial resolution has no `tasks.md` THEN the resolver SHALL use exactly one slice.
7. IF `tasks.md` exists but its closure contract is malformed THEN the resolver SHALL fail without
   writing or replacing `workflow.json`.
8. WHILE a valid workflow snapshot exists and refresh is not requested, the resolver SHALL return that frozen snapshot without reading current tasks or deriving a new slice count.
9. WHEN the task template describes planning units THEN it SHALL distinguish a vertical slice as a merge-alone outcome, a phase or cohort as technical ordering, and a batch as worker capacity.
10. WHEN review remediation records such as `T2R1` appear in a task document THEN validation SHALL keep them outside the primary task slice count.
11. WHEN the validated closure contract feeds downstream planning THEN workflow configuration and parallel planning SHALL use the same primary-task membership and slice IDs.
12. WHEN workflow configuration writes a version-2 snapshot THEN the parallel planner and executor SHALL accept it while preserving feature, mode, and Git-head validation.
13. IF an active parallel planner or executor receives a version-1 workflow snapshot THEN it SHALL reject it without fallback or migration.

**Independent Test**: Run the Praxis/Bun regression fixture through task validation and workflow
resolution; it produces one slice and a one-slice review plan. Run the two-capability fixture; it
preserves two independently mergeable slices. Feed the resulting version-2 snapshot to the parallel
planner and executor; both accept it, while a version-1 fixture is rejected.

## Edge Cases

- IF a closure row uses `no`, an empty cell, or a value other than exact `yes` THEN validation SHALL
  reject it.
- IF two closure rows reuse one slice ID THEN validation SHALL reject the duplicate.
- IF `--slices` is zero or negative THEN resolution SHALL reject it as an invalid assertion.
- WHEN tasks change after a snapshot is frozen THEN normal resume SHALL keep the prior snapshot and
  explicit refresh SHALL validate and derive the new closure contract.
- IF a parallel consumer receives a version-1 workflow snapshot THEN it SHALL fail instead of
  silently interpreting or upgrading it.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| MAS-01 | P1: Praxis regression derives one slice | Tasks | Verified |
| MAS-02 | P1: Independent outcomes derive two slices | Tasks | Verified |
| MAS-03 | P1: Closure fields validate | DR2 | Verified |
| MAS-04 | P1: Task membership validates | R1 | Verified |
| MAS-05 | P1: Optional count asserts derived value | R1 | Verified |
| MAS-06 | P1: Missing tasks defaults to one slice | Tasks | Verified |
| MAS-07 | P1: Malformed tasks fail closed | R1 | Verified |
| MAS-08 | P1: Resume preserves frozen snapshot | Tasks | Verified |
| MAS-09 | P1: Template distinguishes planning units | DR1 | Verified |
| MAS-10 | P1: Remediation does not inflate slices | DR2 | Verified |
| MAS-11 | P1: Downstream planners share membership | DR2 | Verified |
| MAS-12 | P1: Parallel consumers accept workflow snapshot v2 | QA1 | Verified |
| MAS-13 | P1: Parallel consumers reject workflow snapshot v1 | QA1 | Verified |

**Coverage:** 13 total, 13 mapped to tasks, 0 unmapped.

## Success Criteria

- [x] The Praxis/Bun five-task migration resolves to one slice.
- [x] Two independently mergeable capabilities resolve to two slices.
- [x] Invalid closure contracts and count mismatches fail before snapshot replacement.
- [x] Resume and no-Tasks behaviour preserve their declared semantics.
- [x] All repository gates pass without adding dependencies or compatibility parsers.
- [x] Parallel planning and execution consume the resolver's version-2 snapshot and reject version 1.
