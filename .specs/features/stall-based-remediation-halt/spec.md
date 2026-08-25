# Stall-Based Remediation Halt Specification

## Problem Statement

Post-cap remediation currently lacks a measurable progress boundary. The workflow must continue
while the failing-test set reaches a new minimum and stop only after a configurable number of
consecutive attempts without that progress.

## Out of Scope

| Capability | Reason |
| --- | --- |
| A third deep-review round | Remediation happens after the existing review cap. |
| Runtime-specific test parsers | The workflow defines a normalized failure signature, not a test-framework adapter. |
| Persisting remediation thresholds in feature snapshots | Operators must be able to tune the bound between attempts. |

## Assumptions & Open Questions

| Decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Stall threshold | `3` consecutive non-progress attempts | Bounds loops without stopping on one noisy run. | yes, prior approved PR #60 |
| Unbounded mode | `0` | Gives operators an explicit opt-out without a second key. | yes, prior approved PR #60 |
| Progress | Current failing-test identifiers form a strict subset of the smallest prior set | Counts observed improvement rather than agent confidence. | yes, prior approved PR #60 |

**Open questions:** none.

## User Stories

### P1: Bound post-cap remediation by observed progress

**User Story**: As a workflow operator, I want remediation to continue while failures shrink and
halt after repeated stalls so that useful progress is not interrupted and stuck loops terminate.

**Why P1**: This is the complete behavior requested by PR #60.

**Acceptance Criteria**:

1. WHEN configuration is resolved THEN the resolver SHALL accept `[remediation].stall_attempts` as
   an integer greater than or equal to `0`, defaulting to `3` when absent.
2. WHEN `stall_attempts` is `0` THEN the workflow SHALL treat stall-based termination as unbounded.
3. WHEN configuration is resolved or resumed THEN the resolver SHALL emit the current effective
   threshold under `remediation.stall_attempts` without persisting it in `workflow.json`.
4. WHEN a post-cap remediation attempt completes THEN the workflow SHALL run its scoped gate and
   derive a stable signature from sorted failing-test identifiers with timings, absolute paths, and
   line numbers removed.
5. WHEN the current failing-test set is strictly smaller than the smallest prior set THEN the workflow SHALL reset the consecutive-stall counter and continue remediation.
6. WHEN the current failing-test set does not establish a new minimum THEN the workflow SHALL
   increment the consecutive-stall counter.
7. WHEN a nonzero configured threshold is reached THEN the workflow SHALL halt and report the
   repeated signature, attempt count, and fixes tried.
8. IF the scoped gate cannot run THEN the workflow SHALL halt immediately without opening another
   deep-review round.
9. WHEN the review cap is reached THEN the workflow SHALL keep remediation inside the existing
   review loop and SHALL NOT start review round three.

**Independent Test**: Resolve default, positive, zero, invalid, refresh, and resume configurations;
then inspect the post-cap contract against shrinking, unchanged, and unavailable-gate cases.

## Edge Cases

- IF `stall_attempts` is negative, boolean, non-integer, or accompanied by an unknown remediation
  key THEN the resolver SHALL reject the configuration before writing a snapshot.
- WHEN a failure set changes members without becoming smaller THEN the workflow SHALL count a stall.
- WHEN the threshold changes after snapshot creation THEN resume SHALL use the new threshold while
  preserving the frozen routing and cadence.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| SRH-01 | P1: remediation configuration | Implementation | verified |
| SRH-02 | P1: live threshold resolution | Implementation | verified |
| SRH-03 | P1: failure signature and progress | Implementation | verified |
| SRH-04 | P1: bounded halt report | Implementation | verified |
| SRH-05 | P1: gate and review-cap safety | Implementation | verified |

**Coverage:** 5 total, 5 mapped to P1, 0 unmapped.

## Success Criteria

- [x] Resolver validation covers default, positive, zero, invalid, and resume cases.
- [x] `workflow.json` remains free of the live remediation threshold.
- [x] Post-cap remediation continues only on a new minimum and halts at the configured stall bound.
- [x] No third deep-review round is opened.
