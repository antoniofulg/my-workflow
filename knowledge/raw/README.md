# Raw sources

Originals in whatever format they arrived: transcripts, research, captured articles, exports,
meeting records, PDFs, images. Concepts in `../wiki/` cite these files through
`sources[].resource`.

This directory is deliberately **outside** the OKF bundle. Conformance rule §11.1 requires every
`.md` inside `../wiki/` to carry frontmatter with a `type`; a verbatim source has none, and adding
it would mean editing a file that must not change.

Two rules, both detailed in [the operating schema](../AGENTS.md):

* **Immutable.** Once a file lands here it is never modified. Corrections go in the concepts that
  cite it, never in the source.
* **Committed, so it is a privacy surface.** Strip names, contact details and precise locations
  before writing anything here. Never store credentials or customer data. Applicable privacy law
  applies to the whole repository, and rewriting git history is not a remedy you want to need.

Collected so far: `2026-09-03-e2e-gate-remediation-cost.md`.
