# Layered Workflow Adoption QA Plan

**Date:** 2026-08-30
**Scope:** `48cfd971f199..d4633c9`
**Profile:** `docs/qa/README.md`
**Adapter:** CLI/manual in checkout-local disposable paths
**Technical prerequisite:** `.specs/features/layered-workflow-adoption/validation.md` — PASS, 18/18

## Criterion disposition

| Criterion | Disposition |
| --- | --- |
| LAY-01 | Public fixed-layer catalog and `full` profile → `J-adopt-workflow` / `ADP-layered-workflow-adoption`; plan and full-profile charters. |
| LAY-02 | Public read-only deterministic plan → adoption journey/scenario; plan charter. |
| LAY-03 | Public JSON stdout/stderr contract → adoption journey/scenario; plan charter. |
| LAY-04 | Public unknown-layer refusal → plan charter. Invalid in-memory DAG mechanics remain technical because users cannot configure the graph. |
| LAY-05 | Public transitive, cumulative apply → adoption journey/scenario; incremental charter. |
| LAY-06 | Public installed ownership manifest → adoption journey/scenario; incremental charter. |
| LAY-07 | Public update/conflict and zero-write outcome → adoption journey/scenario; incremental charter. Hash-classification mechanics remain technical. |
| LAY-08 | Public consumer-prose and `--skip-agents` preservation → adoption journey/scenario; incremental charter. |
| LAY-09 | Public unsafe-target refusal and no external mutation → adoption journey/scenario; incremental charter. Exhaustive containment variants remain technical. |
| LAY-10 | Public preserved config, synchronized packets, and no partial apply → adoption journey/scenario; incremental and full-profile charters. Staging internals remain technical. |
| LAY-11 | Public status vocabulary → adoption journey/scenario; incremental charter. |
| LAY-12 | Public clean/drift exit codes and read-only status → adoption journey/scenario; incremental charter. |
| LAY-13 | Public missing/invalid-manifest refusal and fresh-apply distinction → adoption journey/scenario; incremental charter. Exhaustive schema mutations remain technical. |
| LAY-14 | Public complete capability inventory → adoption journey/scenario; full-profile charter. |
| LAY-15 | Public dependency-first install → adoption journey/scenario; plan and incremental charters. |
| LAY-16 | Public atomic publication outcome → adoption journey/scenario; full-profile charter. Exact bucket/manifest-last ordering remains technical. |
| LAY-17 | Public Bun knowledge, unchanged package metadata, and effect-free probe import → adoption journey/scenario; full-profile charter. |
| LAY-18 | Public legacy-command rejection → adoption journey/scenario; plan charter. |

All 18 criteria have explicit dispositions. Every user-observable promise maps to the canonical
adoption journey and scenario; inaccessible graph mutations, exhaustive hostile variants, and exact
publication mechanics remain technical while their public refusal/atomicity outcomes are walked.

## Flagged scenarios

- `ADP-layered-workflow-adoption` remains `untested`; QA Plan records no execution claim.
- `ADP-adopt-workflow-safely` retains its previous verdict as the overlap canary for consumer-state
  preservation; the new command and ownership promise belongs to the feature-specific scenario.
- `REL-report-current-workflow-release` retains its previous verdict as the adjacent Bun/package
  canary. This feature changes no release identity or Bun package authority.
- Live Orca scenarios keep their existing status; the planned probe check uses only a fake binary.

## Immutable charters

- `docs/qa/charters/CH-plan-layered-workflow-adoption-2026-08-30.md`
- `docs/qa/charters/CH-apply-layered-workflow-adoption-2026-08-30.md`
- `docs/qa/charters/CH-adopt-full-layered-workflow-2026-08-30.md`

## QA Execute handoff

Dispatch a fresh Verifier with `phase: qa-execute` at the final candidate HEAD. Use the CLI/manual
adapter in `docs/qa/README.md`, Bun 1.4.x already present, disposable targets owned by this checkout,
and ignored raw evidence under `docs/qa/evidence/2026-08-30-layered-workflow-adoption/`. Write one
new durable report at `docs/qa/reports/2026-08-30-layered-workflow-adoption.md` and update the
feature scenario only after independent readback confirms each observable.

Walk the plan charter first, then the incremental and full-profile charters. Include the existing
adoption overlap canary and current-release adjacent canary. Use a fake `orca`; do not run a live
Orca pilot. Do not publish, tag, push, merge, contact a registry, install external skills, mutate a
non-disposable project, or change product code. A product contradiction becomes a bug for an
Implementer and ends that QA Execute session.
