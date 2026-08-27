# CH-adopt-merge-alone-slice-contract-2026-08-27

- **Date:** 2026-08-27
- **Scope:** `d0dd82d..88a3eee` for `merge-alone-slices`
- **Time-box:** 25 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Adopted merge-alone template and validator contract tour
- **Public entry point:** `README.md` → `scripts/adopt.py` → adopted `.agents/skills/tlc-spec-driven/references/tasks.md` and `.agents/skills/tlc-spec-driven/scripts/validate_tasks.py`
- **Adapter candidate:** CLI/manual adoption into a separate checkout-local disposable Git target, as declared in [`docs/qa/README.md`](../README.md)
- **Scenario:** [`ADP-validate-generated-feature-contracts`](../scenarios/ADP-validate-generated-feature-contracts.md)
- **Adjacent canary:** [`ADP-adopt-workflow-safely`](../scenarios/ADP-adopt-workflow-safely.md), retaining its current verdict unless fresh evidence invalidates it

## Mission

Confirm a workflow adopter receives the public merge-alone planning vocabulary and validator CLI,
can validate generated one- and two-slice task contracts without hand edits, and receives named
failures for incomplete closures or inconsistent membership. Re-adopt once to confirm this changed
managed surface still preserves consumer-owned state.

## Expected observable

The adopted task template requires one Slice per primary task and one complete merge-alone closure
per used slice, while distinguishing slices from technical phases/cohorts and worker batches. The
adopted validator accepts generated one- and two-slice contracts, rejects incomplete closure and
membership shapes with task/slice identity, and re-adoption leaves consumer-owned sentinels
unchanged.

## Planned probes

- Adopt into a separate checkout-owned disposable Git target and independently compare the adopted
  task template and validator with the source-managed files.
- From the adopted template, form one-outcome and two-outcome task documents and invoke the adopted
  validator's public JSON contract; reload its stdout and require stable ordered Slice membership.
- Remove each required closure value in turn and probe non-exact merge-alone decisions; require a
  non-zero result naming the invalid slice and field.
- Probe a primary task with zero, multiple, or unknown Slice membership plus an empty, orphan, or
  duplicate closure; require a non-zero result naming the inconsistent task or slice.
- Inspect the adopted wording for the merge-alone slice, technical phase/cohort, and worker batch
  distinction. Keep remediation-heading classification as technical context, not a new scenario.
- Add a consumer-owned config sentinel, re-adopt, and independently require unchanged sentinel
  bytes. Confirm adoption only prints the external-security installer command; never invoke it.

## Scenario state and limitations

`ADP-validate-generated-feature-contracts` remains `qa_status: untested` because this feature
changes its current validator promise. `ADP-adopt-workflow-safely` remains a retained adjacent
canary and is not reset by planning. No browser, server, API, auth, or external account is involved;
network access and host configuration are outside this charter.

## QA Execute handoff

Execute this charter in the same fresh `qa-execute` session as
`CH-derive-merge-alone-slices-2026-08-27`, using a distinct disposable adoption target. Record raw
evidence under `docs/qa/evidence/2026-08-27-merge-alone-slices/` and the result in that cycle's new
dated report. Update only the affected scenario and any canary whose observable actually changed.
