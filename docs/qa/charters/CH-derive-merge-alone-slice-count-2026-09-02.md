# CH-derive-merge-alone-slice-count-2026-09-02

- **Date:** 2026-09-02
- **Scope:** `main..5d517be` on `feat/merge-alone-slices`
- **Time-box:** 30 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-configure-feature-workflow`](../journeys/J-configure-feature-workflow.md)
- **Tour:** Derived-count and authoring-surface tour
- **Public entry point:** `python3 .agents/skills/workflow-spec-driven/scripts/validate_tasks.py <tasks.md> --slice-contract-json` -> `python3 .agents/skills/workflow-config/scripts/workflow_config.py --root . --feature <slug> --native-provider <provider>`
- **Adapter candidate:** CLI/manual with a checkout-local disposable Git repository, as declared in [`docs/qa/README.md`](../README.md)
- **Scenario:** `CFG-derive-merge-alone-slices`
- **Adjacent canary:** `CFG-resolve-deep-review-cadence`

## Mission

Experience the count as an adopter would: write no `--slices`, let the closure table decide, and
require that technical organization never inflates the number. Confirm the documents an adopter
copies from say the same thing the resolver does.

## Expected observable

The Praxis one-slice fixture resolves to review groups covering exactly slice `1` even though it
carries five primary tasks across three technical cohorts; the two-capability fixture resolves to
slice ordinals `1` and `2` exactly once. `--slice-contract-json` reports the same membership the
document declares, in document order, identically on a repeated run. A review remediation record
never raises either count.

## Planned probes

- Copy [`tools/fixtures/tlc-validator/merge-alone-one-slice.md`](../../tools/fixtures/tlc-validator/merge-alone-one-slice.md)
  into a disposable feature directory as `tasks.md`; resolve without `--slices`. Require exactly one
  slice in the snapshot's review groups.
- Repeat with [`merge-alone-two-slices.md`](../../tools/fixtures/tlc-validator/merge-alone-two-slices.md)
  in a second disposable feature. Require slice ordinals `1` and `2`, each once.
- Run `--slice-contract-json` on both fixtures twice. Require byte-identical stdout, task and slice
  ids in document order, and membership matching each `**Slice:**` field.
- Append a `### T2R1:` remediation record carrying its own `**Slice:**` field to the two-slice
  fixture copy. Require the contract, derived count, and review groups unchanged.
- Read [`.agents/skills/workflow-spec-driven/references/tasks.md`](../../.agents/skills/workflow-spec-driven/references/tasks.md)
  as an adopter authoring a plan. Require it to name vertical slice, phase/cohort, and batch apart,
  show `**Slice:**` on each task stub, and show the closure table with `yes` as the only value.
- Copy each resolver invocation printed in `README.md` and
  [`.agents/skills/workflow-config/SKILL.md`](../../.agents/skills/workflow-config/SKILL.md)
  verbatim and run it against a disposable target. Require every published example to succeed and
  none to present `--slices` as the source of truth.
- Adjacent canary: resolve cadence through `CFG-resolve-deep-review-cadence` read-only in the same
  disposable target. Require its prior balanced-group and remediation-bound promise unchanged.
- Remove only checkout-owned targets and record source-checkout residue. Do not edit product code.

## QA Execute handoff

Start a fresh Verifier session with `phase: qa-execute`. Read `docs/qa/README.md`, invoke canonical
`qa-execute`, and use its CLI/manual adapter at HEAD `5d517be`. Keep every fixture under a
disposable directory owned by the active checkout; never resolve against `.specs/` in the source
checkout. Store raw evidence under `docs/qa/evidence/2026-09-02-merge-alone-slices/`, write a new
report at `docs/qa/reports/2026-09-02-merge-alone-slices.md`, and update
`CFG-derive-merge-alone-slices` verdict fields only from observed public-interface evidence. End
before any product remediation.
