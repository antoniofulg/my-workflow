# J-run-deep-review

**Persona:** Workflow operator
**Goal:** Complete and publish a Deep Review with serial reviewers, honest metrics, and optional Graft
context, and know when remediation past the review cap continues and when it halts.
**Entry point:** `.agents/skills/deep-review/SKILL.md` → `scripts/run_jobs.py`

## Flow

1. Materialize review jobs and inspect the optional Graft context referenced by their prompts.
2. Run pending reviewer jobs serially with compatible telemetry configured.
3. Inspect preserved reviewer outputs, run status, and the content-safe metrics ledger.
4. Repeat without compatible telemetry and confirm the review result is unchanged and usage is
   reported as unavailable.
5. Make Graft unavailable and confirm prompts direct the reviewer to ordinary repository inspection.
6. Publish the walkthrough and confirm the marker selects exactly one create-or-edit action.
7. Read the escalation rule that governs remediation past the review cap and confirm every surface
   that states or cites it agrees on when the run continues and when it halts.

## Promises

- [`QAS-observe-serialized-deep-review-metrics`](../scenarios/QAS-observe-serialized-deep-review-metrics.md)
- [`QAS-use-graft-context-with-plain-fallback`](../scenarios/QAS-use-graft-context-with-plain-fallback.md)
- [`QAS-upsert-deep-review-walkthrough`](../scenarios/QAS-upsert-deep-review-walkthrough.md)
- [`DOC-halt-remediation-only-on-a-stall`](../scenarios/DOC-halt-remediation-only-on-a-stall.md)

## Adjacent canary

Inspect [`CFG-keep-local-artifacts-out-of-git`](../scenarios/CFG-keep-local-artifacts-out-of-git.md)
to confirm generated Deep Review and Graft data remain local and source files remain searchable.
