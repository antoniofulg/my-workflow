# CH-freeze-and-refresh-derived-slices-2026-09-02

- **Date:** 2026-09-02
- **Scope:** `main..5d517be` on `feat/merge-alone-slices`
- **Time-box:** 25 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-configure-feature-workflow`](../journeys/J-configure-feature-workflow.md)
- **Tour:** Resume-versus-refresh tour
- **Public entry point:** `python3 .agents/skills/workflow-config/scripts/workflow_config.py --root . --feature <slug> --native-provider <provider> [--refresh]`
- **Adapter candidate:** CLI/manual with a checkout-local disposable Git repository, as declared in [`docs/qa/README.md`](../README.md)
- **Scenario:** `CFG-derive-merge-alone-slices`
- **Adjacent canary:** `CFG-freeze-feature-workflow`

## Mission

Prove an in-flight feature cannot have its cadence moved by editing `tasks.md`. Resume must not read
current tasks at all; only an explicit refresh may re-derive.

## Expected observable

After a one-slice snapshot is frozen, changing `tasks.md` to declare two slices — or corrupting it
outright — leaves resume returning the byte-for-byte frozen snapshot with exit zero. Running the same
state with `--refresh` re-derives two slices and replaces the snapshot atomically on the same schema
version.

## Planned probes

- Resolve the one-slice fixture in a disposable feature. Record the `workflow.json` hash and its
  review groups.
- Replace `tasks.md` with the two-slice fixture. Resume without `--refresh`. Require exit zero, the
  recorded hash unchanged, and review groups still covering exactly slice `1`.
- Resume again with `--slices 2` supplied. Require the frozen snapshot returned unchanged and the
  assertion not applied, per the resume contract.
- Corrupt `tasks.md` (remove the closure table). Resume without `--refresh`. Require exit zero and
  the same unchanged hash — a malformed document after the freeze must not fail an in-flight resume.
- Restore the valid two-slice `tasks.md` and run `--refresh`. Require exit zero, review groups
  covering slices `1` and `2`, a changed hash, and an unchanged snapshot schema version.
- Corrupt `tasks.md` again and run `--refresh`. Require non-zero refusal and the previous refreshed
  snapshot byte-for-byte intact.
- Adjacent canary: confirm `CFG-freeze-feature-workflow`'s live-remediation exception still holds in
  the same target — `remediation.stall_attempts` appears in current CLI JSON and never in
  `workflow.json`, and changing it on resume moves no frozen field.
- Remove only checkout-owned targets and record source-checkout residue. Do not edit product code.

## QA Execute handoff

Start a fresh Verifier session with `phase: qa-execute`. Read `docs/qa/README.md`, invoke canonical
`qa-execute`, and use its CLI/manual adapter at HEAD `5d517be`. Every freeze claim needs a hash
recorded on both sides of the probe. Store raw evidence under
`docs/qa/evidence/2026-09-02-merge-alone-slices/`, write into
`docs/qa/reports/2026-09-02-merge-alone-slices.md`, and hand any defect to an Implementer.
