# CH-adopt-bun-tooling-runtime-2026-08-29

- **Date:** 2026-08-29
- **Scope:** `69914e831cb8..38796e825360` for `bun-tooling-runtime`
- **Time-box:** 25 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Bun-native knowledge adoption and repository-test exclusion
- **Public entry point:** `README.md` → Adopt the workflow → `scripts/adopt.py`
- **Adapter candidate:** CLI/manual through [`docs/qa/README.md`](../README.md)
- **Bun contract scenario:** [`REL-report-current-workflow-release`](../scenarios/REL-report-current-workflow-release.md)
- **Journey canary:** [`ADP-adopt-workflow-safely`](../scenarios/ADP-adopt-workflow-safely.md)

## Mission

Adopt and re-adopt the workflow into a disposable consumer. Confirm the target receives Bun-native
knowledge sources but none of the repository-only TypeScript suites, and that its knowledge CLI
runs through the supplied Bun runtime without consumer Node packages or lost consumer state.

## Expected observable

Fresh adoption exits zero, installs current managed runtime bytes, contains zero `*.test.ts` files,
and runs the installed knowledge CLI with Bun; re-adoption produces the same managed bytes while
preserving consumer-owned configuration and tests byte-for-byte and leaving the source checkout
unchanged.

## Planned walk

1. Create one checkout-owned disposable target with consumer config, QA profile, and TypeScript-test
   sentinels; record their hashes before adoption.
2. Run `scripts/adopt.py`, reload its stdout and target tree, and confirm managed knowledge sources
   exist while repository test suites do not.
3. Run the installed knowledge CLI with Bun from the target without installing consumer packages;
   record its exit and independently reload its output.
4. Modify one managed file, re-adopt, and confirm managed restoration plus exact preservation of
   every consumer sentinel.
5. Import the installed assisted probe with a call-counting fake `orca` on `PATH`; require zero
   Orca calls as the adjacent adoption safety canary.
6. Remove only the disposable target and confirm source status matches preflight.

## Boundaries

Do not install packages in the consumer, invoke the printed external-security command, call live
Orca, mutate a real project, or change product code.
