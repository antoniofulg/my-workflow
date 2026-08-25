# J-run-deep-review

**Persona:** Workflow operator
**Goal:** Complete and publish a Deep Review with bounded parallel reviewers, deterministic output, honest metrics, and optional Graft context.
**Entry point:** `.agents/skills/deep-review/SKILL.md` → `scripts/run_jobs.py`

## Flow

1. Materialize review jobs with default, repository, or CLI concurrency and inspect the resolved
   value frozen in the manifest.
2. Reject invalid concurrency before dispatch, then run pending jobs with at most the resolved
   number of active reviewers.
3. Inspect manifest-ordered status, validation, merge, and report output after reviewers finish in a
   different order.
4. Trigger retry and provider-block paths, allow active attempts to finish, and resume only
   unfinished jobs while preserving valid outputs.
5. Inspect serialized cumulative metrics checkpoints and confirm totals finalize only for a complete
   scope, without per-job token attribution.
6. Repeat without compatible telemetry and confirm the review result is unchanged and usage is
   reported as unavailable.
7. Make Graft unavailable and confirm prompts direct the reviewer to ordinary repository inspection.
8. Publish the walkthrough and confirm the marker selects exactly one create-or-edit action.

## Promises

- [`QAS-run-bounded-parallel-deep-review`](../scenarios/QAS-run-bounded-parallel-deep-review.md)
- [`QAS-observe-serialized-deep-review-metrics`](../scenarios/QAS-observe-serialized-deep-review-metrics.md)
- [`QAS-use-graft-context-with-plain-fallback`](../scenarios/QAS-use-graft-context-with-plain-fallback.md)
- [`QAS-upsert-deep-review-walkthrough`](../scenarios/QAS-upsert-deep-review-walkthrough.md)

## Adjacent canary

Inspect [`CFG-keep-local-artifacts-out-of-git`](../scenarios/CFG-keep-local-artifacts-out-of-git.md)
to confirm generated Deep Review and Graft data remain local and source files remain searchable.
