# J-review-workflow-release

**Persona:** Repository reader
**Goal:** Understand the workflow's provenance, neutral scope, and published capability version.
**Entry point:** `README.md`

## Flow

1. Read the repository description, credits, adoption contract, bundled and external skills lists,
   and out-of-scope text.
2. Follow the Tech Leads Club and Pedro Nauck source links and compare them with the local authorship
   statements.
3. Inspect the external security entries in `skills-lock.json` and confirm the docs describe them as
   separately authorized, immutable dependencies rather than bundled capabilities.
4. Inspect the package and lockfile root metadata for the published workflow version.

## Promises

- [`DOC-read-explicit-workflow-provenance`](../scenarios/DOC-read-explicit-workflow-provenance.md)
- [`REL-report-capability-version-0-3-0`](../scenarios/REL-report-capability-version-0-3-0.md)

This journey is the adjacent canary for `J-adopt-workflow`.
