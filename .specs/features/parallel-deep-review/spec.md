# Parallel Deep Review Specification

## Problem Statement

Deep-review jobs are independent and write isolated artifacts, but the current runner executes them
one at a time. This preserves deterministic checkpoints while making wall time the sum of every
reviewer. The workflow needs bounded concurrency without changing coverage, retries, blocking,
resume, freeze, or total-metrics guarantees.

## Out of Scope

| Capability | Reason |
| --- | --- |
| Automatic provider-capacity detection | IDE providers do not expose reliable shared quota or burst capacity. |
| Per-job token attribution | Provider telemetry is cumulative and cannot assign overlapping deltas honestly. |
| Cross-provider load balancing | The frozen deep-reviewer route selects one provider for the feature. |
| Cancelling active reviewer processes | A provider block stops new scheduling; already-active jobs finish safely. |

## Assumptions & Open Questions

| Decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Default concurrency | `3` | Cuts wall time while limiting provider burst. | yes, human |
| Maximum concurrency | `6` | Supports deliberate full fan-out without unbounded dispatch. | yes, human |
| Selection | Explicit config or CLI override | Provider capacity cannot be inferred safely. | yes, human |
| Metrics | Cumulative round totals and serialized checkpoints | Honest under overlapping jobs; no fabricated attribution. | yes, human |

**Open questions:** none.

## User Stories

### P1: Run independent review jobs concurrently

**User Story**: As a workflow operator, I want bounded parallel reviewers so that deep-review
finishes faster without weakening coverage or deterministic reporting.

**Why P1**: Serial execution is the dominant wall-time cost once jobs are materialized.

**Acceptance Criteria**:

1. WHEN a review manifest is built without an override or repository setting THEN the workflow SHALL resolve concurrency to `3`.
2. WHEN `.deep-review.yaml` defines `concurrency` THEN the workflow SHALL accept an integer from `1` through `6` and persist the resolved value in the manifest.
3. WHEN the CLI supplies `--concurrency` THEN the workflow SHALL override repository configuration with an integer from `1` through `6`.
4. IF concurrency is non-integer, boolean, below `1`, or above `6` THEN the workflow SHALL reject it before dispatch.
5. WHEN jobs are dispatched THEN every supported engine SHALL run at most `min(resolved concurrency, pending jobs)` reviewers simultaneously.
6. WHEN concurrent jobs finish in any order THEN the workflow SHALL preserve deterministic manifest-order status, validation, merge, and report output.

**Independent Test**: Materialize delayed jobs, prove true overlap at `3` and `6`, and compare final
status ordering across inverted completion schedules.

### P2: Preserve failure, resume, freeze, and metrics semantics

**User Story**: As a workflow operator, I want parallel dispatch to retain existing safety and
recovery guarantees so that speed cannot corrupt review state or token reporting.

**Why P2**: Concurrency is valuable only when interrupted runs remain resumable and auditable.

**Acceptance Criteria**:

1. WHEN a job retries THEN the workflow SHALL keep its attempts within one worker slot while sibling jobs continue independently.
2. WHEN a provider block is detected THEN the workflow SHALL stop scheduling new jobs, allow already-active attempts to finish, exit `2`, and list every unfinished job in `run-blocker.json`.
3. WHEN a blocked or interrupted run resumes THEN the workflow SHALL preserve valid outputs and execute only missing, blocked, or invalid jobs.
4. IF source drift occurs during concurrent execution THEN the workflow SHALL let active jobs finish and exit `3` without rendering a valid review.
5. WHEN metrics are enabled THEN the workflow SHALL serialize cumulative checkpoints, omit per-job token attribution, and finalize totals only after the full scope completes.
6. WHEN the legacy no-op `--workers` option is used THEN the workflow SHALL reject it instead of silently ignoring it.

**Independent Test**: Run blocking, retry, invalid-output, resume, drift, and metrics fixtures under
overlap and verify exit codes, artifacts, preserved outputs, and cumulative totals.

## Edge Cases

- WHEN fewer jobs are pending than the configured concurrency THEN the workflow SHALL start only the pending count.
- WHEN one job fails without a provider block THEN the workflow SHALL continue independent siblings and retain the failed result.
- WHEN multiple jobs detect a provider block THEN the workflow SHALL preserve the first block reason and produce one coherent blocker ledger.
- WHEN `--only` narrows the job set THEN the workflow SHALL apply concurrency to that pending subset while preserving full-scope metrics semantics.
- WHEN an old valid output exists THEN the workflow SHALL not rerun it merely because concurrency changed.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| PDR-01 | P1: configuration and precedence | Execute | complete |
| PDR-02 | P1: bounded concurrent dispatch | Execute | complete |
| PDR-03 | P1: deterministic output | Execute | complete |
| PDR-04 | P2: retry and provider block | Execute | complete |
| PDR-05 | P2: resume and freeze | Execute | complete |
| PDR-06 | P2: cumulative metrics | Execute | complete |

**Coverage:** 6 total, 6 mapped to stories, 0 unmapped.

## Success Criteria

- [x] Default `3` and explicit maximum `6` are enforced across engines.
- [x] Concurrency produces actual overlap without changing deterministic final artifacts.
- [x] Provider block, retry, resume, and freeze contracts remain correct.
- [x] Metrics remain honest cumulative round totals.
