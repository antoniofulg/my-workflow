# CH-check-graft-artifact-hygiene-2026-08-22

- **Date:** 2026-08-22
- **Time-box:** 10 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Generated-artifact hygiene canary
- **Public entry point:** `.gitignore`
- **Adapter candidate:** CLI/manual filesystem and Git inspection
- **Scenarios:** `CFG-keep-local-artifacts-out-of-git`

## Mission

Create representative Deep Review, feature workflow, and Graft artifacts in a disposable target,
then inspect Git eligibility and search behavior without changing durable workflow sources.

## Expected observable

Generated caches stay out of Git, durable learnings and decisions remain reviewable, Graft cards
remain searchable, and unrelated consumer ignore entries survive adoption.

## Planned probes

- `graft/` cache and `.deep-review/` run data are ignored.
- Graft cards remain visible to repository search while `.cache` and `.graph` stay excluded.
- Durable learnings, decision indexes, and consumer ignore entries remain eligible for review.

End before live defect remediation.
