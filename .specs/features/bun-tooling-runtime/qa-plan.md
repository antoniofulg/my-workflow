# Bun Tooling Runtime QA Plan

**Date:** 2026-08-29
**Scope:** `69914e831cb8..38796e825360`
**Profile:** `docs/qa/README.md`
**Adapter:** CLI/manual in checkout-local disposable paths
**Technical prerequisite:** `.specs/features/bun-tooling-runtime/validation.md` — PASS, 18/18

## Criterion disposition

| Criterion | Disposition |
| --- | --- |
| BUN-01 | Public package/runtime metadata → `J-review-workflow-release` / `REL-report-current-workflow-release`. |
| BUN-02 | Public install and lockfile contract → `J-review-workflow-release` / `REL-report-current-workflow-release`. |
| BUN-03 | Public structural-test discovery → `J-review-workflow-release` / `REL-report-current-workflow-release`. |
| BUN-04 | Internal preload ordering guard; technical validation proves failure before test cases, with no separate user promise. |
| BUN-05 | Public source-pack dependency/runtime contract → `J-review-workflow-release` / `REL-report-current-workflow-release`. |
| BUN-06 | Public knowledge command → `J-review-workflow-release` / `REL-report-current-workflow-release`. |
| BUN-07 | Internal parser implementation; user-observable adopted CLI outcome is covered by BUN-13, while parser parity remains technical. |
| BUN-08 | Public full-gate command → `J-review-workflow-release` / `REL-report-current-workflow-release`. |
| BUN-09 | Public Bun executable contract → `J-review-workflow-release` / `REL-report-current-workflow-release`; `J-enable-external-security-skills` / `ADP-install-pinned-external-security-skills` is the unchanged installation canary. |
| BUN-10 | Public Bun refusal contract → `J-review-workflow-release` / `REL-report-current-workflow-release`; `ADP-preserve-security-install-target` is the unchanged preservation canary. |
| BUN-11 | Public package-membership command and zero-residue outcome → `J-review-workflow-release` / `REL-report-current-workflow-release`. |
| BUN-12 | Public Bun distribution contract → `J-review-workflow-release` / `REL-report-current-workflow-release`; `J-adopt-workflow` / `ADP-adopt-workflow-safely` is the unchanged adoption canary. |
| BUN-13 | Public adopted Bun CLI contract → `J-review-workflow-release` / `REL-report-current-workflow-release`; `ADP-adopt-workflow-safely` is the unchanged preservation canary. |
| BUN-14 | Internal active-authority scan supporting the mapped public commands; no distinct user promise. |
| BUN-15 | Public docs-as-interface → `J-review-workflow-release` / `REL-report-current-workflow-release`. |
| BUN-16 | Internal historical-integrity guard; dated evidence is not a current user operation and remains technically verified. |
| BUN-17 | Internal malformed-version discrimination for BUN-04; no distinct user journey. |
| BUN-18 | Public zero-residue/refusal outcome → `REL-report-current-workflow-release`; adoption and installer preservation scenarios remain adjacent canaries, while hostile-path mechanics remain technical. |

All 18 criteria have one explicit disposition: 13 map to public QA promises and 5 remain internal
with no distinct user surface.

## Test-contract disposition

| Contract | QA disposition |
| --- | --- |
| IT-001, IT-002, IT-003, IT-004, E2E-001 | Release/source-pack charter. |
| IT-005 | Release scenario through the adoption charter and its existing adoption canary. |
| UT-003, IT-007 | Release scenario through the external-security charter and its existing installer canaries. |
| UT-001, UT-002, IT-006, SEC-001, SEC-002 | Technical-only mechanics or discrimination sensors supporting mapped public outcomes. |

## Flagged scenarios

- `REL-report-current-workflow-release` remains `untested`; its Bun promise is refreshed without an
  execution claim.
- `ADP-adopt-workflow-safely`, `ADP-install-pinned-external-security-skills`, and
  `ADP-preserve-security-install-target` retain their prior verdicts as adjacent canaries. Their
  generalized preservation/install outcomes did not change; the new Bun-specific command and
  distribution promise is owned by the reset current-release scenario.
- Existing live Orca scenarios remain `blocked-verify`; this feature does not change them.

## Immutable charters

- `docs/qa/charters/CH-review-bun-tooling-runtime-2026-08-29.md`
- `docs/qa/charters/CH-adopt-bun-tooling-runtime-2026-08-29.md`
- `docs/qa/charters/CH-enable-bun-security-skills-2026-08-29.md`

## QA Execute handoff

Dispatch a fresh Verifier with `phase: qa-execute` at the final candidate HEAD. Use only the
CLI/manual adapter declared in `docs/qa/README.md`, Bun 1.4.x already present, checkout-local
disposable targets, and ignored raw evidence under
`docs/qa/evidence/2026-08-29-bun-tooling-runtime/`. Write one new durable report at
`docs/qa/reports/2026-08-29-bun-tooling-runtime.md` and update scenario verdicts only after
independent reloads confirm each observable.

Walk release and adoption charters fully. The external-security charter may walk its no-write plan
and fail-closed legs without network; its successful installation leg requires explicit
network/write authorization in the QA Execute packet. Without that authority, leave
`REL-report-current-workflow-release` untested for that Bun-specific leg rather than simulating
success; the existing generalized installer canary keeps its prior verdict unless contradicted.

Do not publish, tag, push, merge, contact a registry, invoke live Orca, install another framework,
mutate a non-disposable target, or change product code. A contradiction becomes a bug for an
Implementer and ends that QA Execute session.
