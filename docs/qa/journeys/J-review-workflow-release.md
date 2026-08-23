# J-review-workflow-release

**Persona:** Repository reader
**Goal:** Understand the workflow's provenance, neutral scope, optional capability boundaries,
remote-delivery authority, and published capability version.
**Entry point:** `README.md`

## Flow

1. Read the repository description, credits, adoption contract, bundled and external skills lists,
   and out-of-scope text.
2. Follow the Tech Leads Club and Pedro Nauck source links and compare them with the local authorship
   statements.
3. Confirm Graft and OpenDesign are optional recommendations, adoption installs neither, repository
   artifacts remain the fallback and approved handoff, and external filesystem writers are bounded
   and non-destructive.
4. Confirm readiness never authorizes push, pull request creation, or merge, and that each action
   requires explicit authorization in the current session.
5. Inspect the external security entries in `skills-lock.json` and confirm the docs describe them as
   separately authorized, immutable dependencies rather than bundled capabilities.
6. Inspect the package and lockfile root metadata for the published workflow version.

## Promises

- [`DOC-read-explicit-workflow-provenance`](../scenarios/DOC-read-explicit-workflow-provenance.md)
- [`DOC-use-optional-tools-with-repository-authority`](../scenarios/DOC-use-optional-tools-with-repository-authority.md)
- [`DOC-require-explicit-remote-action-approval`](../scenarios/DOC-require-explicit-remote-action-approval.md)
- [`REL-report-current-workflow-release`](../scenarios/REL-report-current-workflow-release.md)

This journey is the adjacent canary for `J-adopt-workflow`.
