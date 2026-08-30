# CH-apply-layered-workflow-adoption-2026-08-30

- **Date:** 2026-08-30
- **Scope:** `48cfd971f199..d4633c9` for `layered-workflow-adoption`
- **Time-box:** 30 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Incremental layers, ownership conflicts, and status drift
- **Public entry point:** `README.md` → Adopt the workflow → `scripts/adopt.py apply/status`
- **Adapter candidate:** CLI/manual through [`docs/qa/README.md`](../README.md)
- **Scenario:** [`ADP-layered-workflow-adoption`](../scenarios/ADP-layered-workflow-adoption.md)
- **Overlap canary:** [`ADP-adopt-workflow-safely`](../scenarios/ADP-adopt-workflow-safely.md)

## Mission

Adopt `core` into an existing disposable project, add capabilities incrementally, and observe clean
and drifted state without losing consumer-owned bytes or partially publishing a conflicting apply.

## Expected observable

Core installs transitively; later applies retain omitted layers and grow a deterministic schema-1
manifest. Consumer prose, package metadata, local config, missing-only files, and skipped agent
instructions survive. Re-apply is byte-stable; status exits `0` when clean, `1` after drift, and `2`
for missing or invalid state, with every read-only or rejected operation leaving the target unchanged.

## Planned walk

1. Create one checkout-owned existing-project target with consumer `AGENTS.md`/`CLAUDE.md` prose,
   package metadata, local config, QA profile, unrelated files, and recorded hashes.
2. Apply `core`, independently reload `.my-workflow/adoption.json`, instruction blocks, generated
   packets, and consumer sentinels; require clean `status` exit `0`.
3. Apply `parallel`, then `quality,extras`; require cumulative layers, retained prior files, and
   dependency-first ordering. Reapply unchanged inputs and require byte identity.
4. Repeat the relevant apply with `--skip-agents`; require both instruction files byte-identical.
5. Drift one managed file, reload `status` exit `1`, then attempt a multi-layer apply; require the
   complete conflict list and a byte-identical pre-apply snapshot. Restore the file afterwards.
6. Probe missing and malformed manifest status, plus one checkout-contained unsafe symlink target;
   require exit `2`, no external write, and no target mutation.
7. Remove only disposable paths and confirm source checkout status matches preflight.

## Boundaries

Use disposable paths only. Do not remove installed layers, follow symlinks, invoke live Orca,
install external skills, mutate a real project, publish, or change product code.
