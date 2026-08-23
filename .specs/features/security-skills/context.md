# External Security Skills Context

**Gathered:** 2026-08-22
**Spec:** `.specs/features/security-skills/spec.md`
**Status:** Approved by the user's instruction to resume the preserved security-skills plan

## Feature Boundary

Adoption installs the workflow only and prints a separate, explicit command for three reviewed external security skills.

## Implementation Decisions

- Keep external security skills outside the bundled adoption copy.
- Require `--yes` for writes; no flag means plan-only status 2.
- Pin upstream repositories, commits, paths, hashes and CLI version.
- Keep the current `main` adoption behavior, including Graft, Deep Review, workflow config and `--skip-agents`.
- Use the legacy branch only as a source for the proven implementation; do not merge its stale history.

## Deferred Ideas

- Automatic upstream updates and provider-specific security packs are separate features.
