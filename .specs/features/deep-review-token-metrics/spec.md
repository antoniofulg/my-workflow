# Deep Review Token Metrics Specification

## Problem Statement

Deep-review token consumption is invisible, so workflow changes cannot be compared with evidence.
Measurement must observe the review flow without limiting tokens or blocking work when provider
telemetry is unavailable. Reviewer jobs themselves run serially so only one reviewer thread is
active at a time.

## Goals

- [ ] Record trustworthy token totals and deltas for providers with compatible telemetry.
- [ ] Dispatch reviewer jobs and retries serially with exactly one active reviewer thread.
- [ ] Keep persisted metrics free of prompt, response, and reviewed source content.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Token budgets or enforcement | The human explicitly requested numbers without a limit. |
| Invented Claude or Cursor usage adapters | No stable telemetry source is established in this repository. |
| Reusing the Antclips baseline | Its diff and job composition are not comparable. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Measurement effect | Observational only | The human requested numbers without control. | yes, human |
| Granularity | Round total plus cumulative checkpoints | Provider-global counters do not support honest per-job attribution. | yes, evidence |
| Compatible provider | Codex adapter first | It is the only durable telemetry contract currently implemented. | yes, repository evidence |
| Unsupported providers | Record `unavailable`, preserve normal execution | Unknown usage must not be invented or block review. | yes, human intent |
| Reviewer execution | Serialize jobs and retries; no worker-concurrency flag | One active reviewer prevents overlapping threads and simplifies deterministic resume. | yes, human intent |
| Repository map | Use pinned Graft when available, with plain inspection fallback | The Antclips trial established a small, optional context-map integration. | yes, human intent |

**Open questions:** none - all resolved or logged above.

## User Stories

### P1: Observe review token usage

**User Story**: As a workflow operator, I want token totals for deep-review rounds so that I can
compare changes using measured consumption.

**Why P1**: Numbers, not enforcement, are the requested outcome.

**Acceptance Criteria**:

1. WHERE compatible provider telemetry is configured, WHEN a round starts and completes THEN the system SHALL persist the start snapshot, cumulative checkpoints, a content-safe final per-thread snapshot, aggregate final provider totals, and a round delta recomputable from the start and final snapshots.
2. WHEN a job completes THEN the system SHALL preserve its valid output and MAY record a cumulative usage checkpoint before starting the next serial job.
3. IF telemetry or persisted metric state is unavailable, invalid, regressing, or incomplete THEN the system SHALL record measurement status `unavailable` and preserve the review's existing dispatch and exit behavior.
4. WHILE metrics are enabled, the system SHALL leave retry outcomes unchanged while the reviewer runner executes jobs serially with exactly one active reviewer thread.
5. The persisted metrics SHALL contain usage metadata and identifiers but no prompt, response, or reviewed source content.
6. The shared orchestration contract SHALL describe provider-neutral measurement hooks; provider-specific telemetry commands SHALL live only in provider runtime guidance. Before prompt materialization, the pipeline SHALL attempt optional Graft map, symbol, and blast-radius context and expose its artifact to prompts; missing, stale, failed, or dot-directory coverage SHALL fall back to plain inspection without blocking review.
7. WHERE Codex telemetry is configured, the Codex adapter SHALL read only the allowlisted telemetry fields for the configured reviewer path.
8. WHERE compatible telemetry is unavailable, the system SHALL avoid claiming token totals or enforcement.

**Independent Test**: Run two fixture jobs with metrics enabled, observe both outputs, prove no
overlap, cumulative/final token totals, and unchanged success status. Run the
optional Graft build and verify the plain-inspection fallback when it is unavailable.

## Edge Cases

- IF a telemetry counter decreases or a baseline thread disappears THEN the system SHALL mark metrics unavailable and continue the review.
- IF persisted metric state contains an extra content field THEN the system SHALL reject that state for measurement and continue the review without loading it.
- WHEN a completed round is inspected again THEN the system SHALL return its recorded metrics without rerunning valid jobs.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| DRM-01 | P1: snapshots and totals | Execute | PASS |
| DRM-02 | P1: non-blocking checkpoints | Execute | PASS |
| DRM-03 | P1: unavailable fallback | Execute | PASS |
| DRM-04 | P1: serialized reviewer execution | Execute | PASS |
| DRM-05 | P1: content safety | Execute | PASS |
| DRM-06 | P1: provider-neutral policy | Execute | PASS |
| DRM-07 | P1: Codex adapter | Execute | PASS |
| DRM-08 | P1: honest absence | Execute | PASS |

**Coverage:** 8 total, 8 mapped to the inline execution slice, 0 unmapped.

## Success Criteria

- [x] Tests prove metrics never change a review result and reviewer jobs remain serial.
- [x] Compatible telemetry produces round totals and deltas.
- [x] Unsupported or invalid telemetry produces `unavailable`, not fabricated numbers or a blocked review.
- [x] Prompt materialization executes optional Graft context preparation with visible-code context and honest dot-directory fallback.
