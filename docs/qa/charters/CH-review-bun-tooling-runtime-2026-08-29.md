# CH-review-bun-tooling-runtime-2026-08-29

- **Date:** 2026-08-29
- **Scope:** `69914e831cb8..38796e825360` for `bun-tooling-runtime`
- **Time-box:** 30 minutes
- **Persona:** Repository reader
- **Journey:** [`J-review-workflow-release`](../journeys/J-review-workflow-release.md)
- **Tour:** Bun 1.4 source-pack command and package boundary
- **Public entry point:** `README.md` → Knowledge checker; `package.json`
- **Adapter candidate:** CLI/manual through [`docs/qa/README.md`](../README.md)
- **Scenario:** [`REL-report-current-workflow-release`](../scenarios/REL-report-current-workflow-release.md)
- **Adjacent canary:** [`ADP-adopt-workflow-safely`](../scenarios/ADP-adopt-workflow-safely.md)

## Mission

Validate the source pack as a repository reader through its documented Bun commands. Confirm Bun
1.4 owns dependency installation, TypeScript execution, structural tests, the mixed-language gate,
knowledge checking, and package inspection without reintroducing npm-family authority or leaving
checkout residue.

## Expected observable

The manifest and lockfile name Bun 1.4 consistently; documented commands match manifest scripts;
frozen install, knowledge, structural, and full-gate commands exit successfully; structural
discovery stays under `tools/`; disposable `bun pm pack` includes required public files and leaves
no tarball or source change; historical command evidence remains untouched.

## Planned walk

1. Independently reload `README.md`, `package.json`, `bun.lock`, and `bunfig.toml`; compare every
   documented Bun command with the manifest and supported 1.4.x range.
2. Run the public frozen install, structural test, knowledge, and full-gate commands. Record exact
   exits and reported suite counts; do not substitute technical validation for this public walk.
3. Run package inspection into a checkout-owned disposable destination with `bun pm pack`; reload
   membership independently and confirm no checkout tarball or status change.
4. Confirm active public authority contains no npm/npx/Vitest/tsx/external-yaml command and that
   dated historical records were not rewritten.
5. Walk the adjacent adoption charter in its separate target before assigning the release verdict.

## Boundaries

No publication, registry contact, tag, release, push, merge, live Orca call, dependency upgrade, or
product-code change. Raw evidence belongs only under the cycle's ignored evidence directory.
