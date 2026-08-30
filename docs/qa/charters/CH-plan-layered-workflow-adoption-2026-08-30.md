# CH-plan-layered-workflow-adoption-2026-08-30

- **Date:** 2026-08-30
- **Scope:** `48cfd971f199..d4633c9` for `layered-workflow-adoption`
- **Time-box:** 15 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Plan-first adoption of an existing project
- **Public entry point:** `README.md` → Adopt the workflow → `scripts/adopt.py plan`
- **Adapter candidate:** CLI/manual through [`docs/qa/README.md`](../README.md)
- **Scenario:** [`ADP-layered-workflow-adoption`](../scenarios/ADP-layered-workflow-adoption.md)

## Mission

Review a selected adoption before changing an existing disposable project. Confirm the fixed layer
catalog, dependency resolution, deterministic text and JSON plans, and invalid-command refusals.

## Expected observable

Repeated plans report the same resolved layers and unique per-path actions while the target remains
byte-identical. JSON stdout is one parseable object, diagnostics stay on stderr, and unknown layers
or the removed positional command exit `2` without touching target content.

## Planned walk

1. Create one checkout-owned target containing consumer prose and package sentinels; record a tree
   snapshot.
2. Run text and JSON plans for `parallel,quality`; reload both outputs and require `core` first,
   stable layer order, unique paths, and the same target snapshot.
3. Run a duplicate/whitespace selection and `full`; require deterministic normalization and exactly
   `core`, `parallel`, `quality`, and `extras` for `full`.
4. Run one unknown layer and the old positional command; require exit `2`, actionable diagnostics,
   and the original target snapshot.
5. Remove only the disposable target and confirm source checkout status matches preflight.

## Boundaries

Plan only in this charter. Do not apply files, invoke live Orca, install packages, mutate a real
project, publish, or change product code.
