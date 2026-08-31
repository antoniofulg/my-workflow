# Release 0.8.0 — QA Plan

**Date:** 2026-08-31
**Phase:** QA Plan
**Spec:** `.specs/features/release-0-8-0/spec.md`
**Candidate:** `9751bd79acd52aaeb97ffff461d11fb4b06ccff6`
**Diff range:** `origin/main...9751bd7`
**Profile:** `docs/qa/README.md`
**Adapter:** Checkout-local CLI/manual with disposable Git targets; no browser, server, live Orca,
network, or real consumer repository

## Prerequisites

- Technical revalidation: `PASS` for `RLS-01`, `RLS-02`, and `RLS-04` in
  `.specs/features/release-0-8-0/validation-s2-r4.md`; its three discrimination mutants were killed.
- Deep Review round 2: `FIX_BEFORE_SHIP` with three Major and two Minor defects in
  `.deep-review/release-0-8-0/review.md`. Commit `9751bd7` closes the final listed defects after
  `a11729d`; QA must assess the post-fix candidate, not treat the round-2 verdict as release QA.
- `REL-report-current-workflow-release` is already reset to `untested`. Historical 0.7.0 evidence
  does not establish a 0.8.0 verdict.

## Criterion disposition

| Requirement | Disposition | Canonical QA coverage |
| --- | --- | --- |
| `RLS-01` | Public release consistency | `J-review-workflow-release` -> `REL-report-current-workflow-release`; fresh reads compare manifest, newest changelog heading, scenario, Bun root package/dependency graph, and frozen install. |
| `RLS-02` | Public private-source-pack promise | Same journey/scenario; inspect Bun dry-run membership and zero package residue. Adjacent adoption canaries prove the shipped members remain consumable. |
| `RLS-03` | Public release QA, owned by the next fresh Verifier | Same journey/scenario through `CH-review-release-0-8-0-2026-08-31`; run the full gate, layered and legacy adoption, first-use machine locking, and effect-free installed probe import. |
| `RLS-04` | Public limitation | Same release scenario plus `QAS-run-resource-free-parallel-orca-slices` and `QAS-clean-owned-parallel-slice-pilot`; confirm both remain `blocked-verify` and make no live-success claim. |
| `RLS-05` | Remote delivery only; excluded from pre-release QA | Verify only after the authorized PR merge, tag, and GitHub Release exist. This QA cycle must not push, merge, tag, publish, or contact GitHub. |

All five requirements have one explicit disposition: four public pre-release mappings and one
post-merge remote-delivery check. `RLS-03` remains incomplete until a fresh QA Execute session
records current evidence and updates the release scenario.

## QA context and outputs

- Persona: `Repository reader` from `docs/qa/personas.md`.
- Canonical journey: `docs/qa/journeys/J-review-workflow-release.md`.
- Canonical scenario: `docs/qa/scenarios/REL-report-current-workflow-release.md`.
- New immutable charter:
  `docs/qa/charters/CH-review-release-0-8-0-2026-08-31.md`.
- Adoption canaries: `ADP-layered-workflow-adoption` and
  `ADP-resolve-legacy-adoption-conflicts`.
- Lock canary: `QAS-serialize-heavy-test-resources`, including the deferred public first-use
  cross-project probe for `CTL-10`.
- Offline coordination canary: `QAS-coordinate-assisted-slices-offline`.
- Preserved external boundary: `QAS-run-resource-free-parallel-orca-slices` and
  `QAS-clean-owned-parallel-slice-pilot` remain `blocked-verify`.

The existing journey and scenario already describe the 0.8.0 route, expected observable, reset,
and historical-evidence boundary. No journey or scenario schema change is needed during planning.

## QA Execute handoff

Dispatch a fresh Verifier with `phase: qa-execute` and the canonical `qa-execute` skill. It must
read `docs/qa/README.md`, this plan, and
`docs/qa/charters/CH-review-release-0-8-0-2026-08-31.md`, then use only the declared CLI/manual
adapter in this clean candidate checkout. Store raw evidence under
`docs/qa/evidence/2026-08-31-release-0-8-0/`, write the immutable report
`docs/qa/reports/2026-08-31-release-0-8-0.md`, and update
`REL-report-current-workflow-release` only from observed current evidence.

Do not touch active CRM or Creatista checkouts, use network access, invoke live Orca, install an
external skill, modify product code, publish a package, push or merge, create a tag or GitHub
Release, or clean historical host evidence. A product contradiction becomes a bug and ends that QA
Execute session for Implementer remediation.
