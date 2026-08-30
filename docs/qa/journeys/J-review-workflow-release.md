# J-review-workflow-release

**Persona:** Repository reader
**Goal:** Understand the workflow's provenance, neutral scope, optional capability boundaries,
remote-delivery authority, published capability version, and honestly bounded parallel execution.
**Entry point:** `README.md`

## Flow

1. Read the repository description, credits, adoption contract, bundled and external skills lists,
   and out-of-scope text.
2. Follow the Tech Leads Club and Pedro Nauck source links and compare them with the local authorship
   statements.
3. Confirm Graft and OpenDesign are optional recommendations, adoption installs neither, repository
   artifacts remain the fallback and approved handoff, and external filesystem writers are bounded
   and non-destructive.
4. Confirm invoking `autonomous` authorizes only its scoped feature-branch push, one pull request,
   and merge after readiness; release, deploy, production mutation, force-push, direct `main` push,
   and unrelated remote actions remain separately authorized.
5. Inspect the external security entries in `skills-lock.json` and confirm the docs describe them as
   separately authorized, immutable dependencies rather than bundled capabilities.
6. Inspect the assisted-by-default hybrid slice contract: `assisted` and `disabled`, sequential
   tasks within each slice, dynamic writer admission, checkpoint synchronization, resource preflight,
   and zero-effect serial fallback when dependency, health, ownership, or isolation proof is missing.
7. Reconcile the parallel release claims with durable QA status. Keep the real Orca/Codex two-lane
   lifecycle and completed-pilot cleanup as `blocked-verify`, never as completed-pilot evidence.
8. Inspect the Bun 1.4 package and lockfile root metadata, Bun-native knowledge and full-test
   commands, and disposable `bun pm pack` membership for the published workflow version.

## Promises

- [`DOC-read-explicit-workflow-provenance`](../scenarios/DOC-read-explicit-workflow-provenance.md)
- [`DOC-use-optional-tools-with-repository-authority`](../scenarios/DOC-use-optional-tools-with-repository-authority.md)
- [`DOC-require-explicit-remote-action-approval`](../scenarios/DOC-require-explicit-remote-action-approval.md)
- [`REL-report-current-workflow-release`](../scenarios/REL-report-current-workflow-release.md)

This journey is the adjacent canary for `J-adopt-workflow`.
For the parallel release contract, its adjacent journeys are
[`J-configure-feature-workflow`](J-configure-feature-workflow.md) and
[`J-execute-parallel-slices`](J-execute-parallel-slices.md).
