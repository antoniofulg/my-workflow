# J-run-deep-review

**Persona:** Workflow operator
**Goal:** Complete a Deep Review with serial reviewers, honest metrics, and optional Graft context.
**Entry point:** `.agents/skills/deep-review/SKILL.md` → `scripts/run_jobs.py`

## Flow

1. Materialize review jobs and inspect the optional Graft context referenced by their prompts.
2. Run pending reviewer jobs serially with compatible telemetry configured.
3. Inspect preserved reviewer outputs, run status, and the content-safe metrics ledger.
4. Repeat without compatible telemetry and confirm the review result is unchanged and usage is
   reported as unavailable.
5. Make Graft unavailable and confirm prompts direct the reviewer to ordinary repository inspection.

## Promises

- [`QAS-observe-serialized-deep-review-metrics`](../scenarios/QAS-observe-serialized-deep-review-metrics.md)
- [`QAS-use-graft-context-with-plain-fallback`](../scenarios/QAS-use-graft-context-with-plain-fallback.md)

## Adjacent canary

Inspect [`CFG-keep-local-artifacts-out-of-git`](../scenarios/CFG-keep-local-artifacts-out-of-git.md)
to confirm generated Deep Review and Graft data remain local and source files remain searchable.
