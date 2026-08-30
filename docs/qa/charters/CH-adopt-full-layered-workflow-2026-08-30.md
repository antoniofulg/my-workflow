# CH-adopt-full-layered-workflow-2026-08-30

- **Date:** 2026-08-30
- **Scope:** `48cfd971f199..d4633c9` for `layered-workflow-adoption`
- **Time-box:** 25 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Complete Bun-native profile and effect-free probe import
- **Public entry point:** `README.md` → Adopt the workflow → `scripts/adopt.py apply --layers full`
- **Adapter candidate:** CLI/manual through [`docs/qa/README.md`](../README.md)
- **Scenario:** [`ADP-layered-workflow-adoption`](../scenarios/ADP-layered-workflow-adoption.md)
- **Adjacent canary:** [`REL-report-current-workflow-release`](../scenarios/REL-report-current-workflow-release.md)

## Mission

Confirm `full` preserves the complete shipped capability set in a Bun consumer while keeping
consumer package ownership and avoiding any Orca effect during installed-probe import.

## Expected observable

Full adoption resolves all four layers, publishes synchronized provider packets and the manifest,
retains consumer `package.json` and `bun.lock` byte-for-byte, runs the installed knowledge CLI with
Bun, and imports the assisted probe with a call-counting fake `orca` recording zero calls. Public
Bun and package metadata remain consistent as the adjacent release canary.

## Planned walk

1. Create one checkout-owned Bun target with consumer package and lock sentinels; record hashes.
2. Plan and apply `full`; reload the manifest, expected capability inventory, managed blocks,
   missing-only ownership, Claude links, and all generated provider packets.
3. Run the installed knowledge CLI through Bun without installing consumer packages; independently
   reload its exit and output, then require unchanged consumer package hashes.
4. Put a call-counting fake `orca` first on `PATH`, import the installed assisted probe, and require
   zero recorded calls and a successful import.
5. Read `README.md`, `package.json`, and `bun.lock` as the adjacent release canary; require the
   documented Bun 1.4 and adoption commands to agree with the shipped metadata.
6. Remove only disposable paths and confirm source checkout status matches preflight.

## Boundaries

No live Orca call, package installation, external-skill installation, registry contact, release,
publication, mutation of a real project, or product-code change.
