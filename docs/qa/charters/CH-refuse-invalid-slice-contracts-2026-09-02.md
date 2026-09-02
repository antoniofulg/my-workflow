# CH-refuse-invalid-slice-contracts-2026-09-02

- **Date:** 2026-09-02
- **Scope:** `main..5d517be` on `feat/merge-alone-slices`
- **Time-box:** 35 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-configure-feature-workflow`](../journeys/J-configure-feature-workflow.md)
- **Tour:** Refusal and fail-closed tour
- **Public entry point:** `python3 .agents/skills/workflow-config/scripts/workflow_config.py --root . --feature <slug> --native-provider <provider> [--slices N]`
- **Adapter candidate:** CLI/manual with a checkout-local disposable Git repository, as declared in [`docs/qa/README.md`](../README.md)
- **Scenario:** `CFG-derive-merge-alone-slices`
- **Adjacent canary:** `CFG-resolve-deep-review-cadence`

## Mission

Hunt the failure this promise exists to catch: a resolver that writes a snapshot it should have
refused. Every rejection must name its cause and leave the filesystem exactly as it was.

## Expected observable

A `--slices` value that disagrees with the derived count, a zero or negative value, and a malformed
closure contract each exit non-zero naming the cause. No `workflow.json` is created where none
existed, and an existing `workflow.json` is byte-for-byte unchanged. A feature directory with no
`tasks.md` resolves to exactly one slice instead of failing.

## Planned probes

- Resolve the two-slice fixture with `--slices 2`. Require success. Then, in a fresh disposable
  feature, resolve it with `--slices 1` and `--slices 3`. Require non-zero exit naming both the
  supplied and the derived count, and require no `workflow.json` to exist afterwards.
- Repeat the mismatch against a feature that already holds a valid snapshot, using `--refresh`.
  Compare the file hash before and after. Require an unchanged hash.
- Resolve with `--slices 0` and `--slices -1`. Require non-zero refusal before any snapshot effect.
- Mutate a fixture copy one defect at a time: drop the closure table entirely; blank the observable
  outcome; blank the independent gate; set the merge-alone cell to empty, `no`, `Yes`, and `true`;
  duplicate a slice id across two rows; declare a closure row no primary task references. Require
  each run to fail naming the offending slice and field, with the snapshot absent or unchanged.
- Mutate membership one defect at a time: a primary task with no `**Slice:**` field, a task with two,
  and a task pointing at an undeclared slice id. Require each failure to name the inconsistent task.
- Resolve a disposable feature directory containing no `tasks.md` at all. Require exit zero and
  exactly one slice in the review groups.
- Adjacent canary: run one invalid remediation input from `CFG-resolve-deep-review-cadence`
  read-only. Require its prior reject-before-write promise unchanged.
- Remove only checkout-owned targets and record source-checkout residue. Do not edit product code.

## QA Execute handoff

Start a fresh Verifier session with `phase: qa-execute`. Read `docs/qa/README.md`, invoke canonical
`qa-execute`, and use its CLI/manual adapter at HEAD `5d517be`. Record the hash of every
`workflow.json` before and after each refusal probe as evidence; a refusal without a before/after
hash is not proof of fail-closed behaviour. Store raw evidence under
`docs/qa/evidence/2026-09-02-merge-alone-slices/`, write into
`docs/qa/reports/2026-09-02-merge-alone-slices.md`, and leave every defect to an Implementer.
