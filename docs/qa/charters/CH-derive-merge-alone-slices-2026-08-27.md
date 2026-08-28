# CH-derive-merge-alone-slices-2026-08-27

- **Date:** 2026-08-27
- **Scope:** `d0dd82d..88a3eee` for `merge-alone-slices`
- **Time-box:** 40 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-configure-feature-workflow`](../journeys/J-configure-feature-workflow.md)
- **Tour:** Merge-alone derivation, failure, freeze, refresh, and downstream-planning tour
- **Public entry point:** validated `tasks.md` → `.agents/skills/workflow-config/scripts/workflow_config.py` → `.specs/features/<slug>/workflow.json`; `.agents/skills/workflow-config/scripts/parallel_plan.py`
- **Adapter candidate:** CLI/manual through the checkout-local disposable-repository path declared in [`docs/qa/README.md`](../README.md)
- **Scenarios:** [`CFG-resolve-deep-review-cadence`](../scenarios/CFG-resolve-deep-review-cadence.md); [`CFG-freeze-feature-workflow`](../scenarios/CFG-freeze-feature-workflow.md); [`CFG-plan-parallel-slice-dispatch`](../scenarios/CFG-plan-parallel-slice-dispatch.md)
- **Adjacent canary:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md) / [`ADP-adopt-workflow-safely`](../scenarios/ADP-adopt-workflow-safely.md), planned by [`CH-adopt-merge-alone-slice-contract-2026-08-27`](CH-adopt-merge-alone-slice-contract-2026-08-27.md)

## Mission

Experience slice derivation as a workflow adopter through the public resolver and planner in a
checkout-local disposable Git repository. Compare CLI output with independent snapshot and task
reads while moving from one merge-alone outcome to two, exercising fail-before-write boundaries,
then proving normal resume stays frozen and explicit refresh adopts the current contract.

## Expected observable

One merge-alone outcome produces one balanced slice, two independently mergeable outcomes produce
two, and missing Tasks produces one. Invalid closure, membership, or optional-count assertions name
the problem without creating or replacing the snapshot. Resume returns unchanged frozen state
without reading changed Tasks; refresh revalidates current Tasks; the read-only planner reports the
same primary-task Slice membership without turning closure rows into work.

## Criterion disposition ledger

| Criterion | Class | Canonical disposition |
| --- | --- | --- |
| MAS-01 | Public CLI/configuration | `J-configure-feature-workflow` → `CFG-resolve-deep-review-cadence`; one complete migration outcome derives exactly one slice. |
| MAS-02 | Public CLI/configuration | `J-configure-feature-workflow` → `CFG-resolve-deep-review-cadence`; two independently mergeable outcomes derive exactly two slices. |
| MAS-03 | Public validator CLI | `J-adopt-workflow` → `ADP-validate-generated-feature-contracts`; incomplete observable, gate, merge-alone decision, or reason is rejected with the invalid slice named. |
| MAS-04 | Public validator CLI | `J-adopt-workflow` → `ADP-validate-generated-feature-contracts`; zero/multiple task membership and empty/orphan slices are rejected with task or slice identity. |
| MAS-05 | Public CLI/state safety | `J-configure-feature-workflow` → `CFG-freeze-feature-workflow`; an optional initial/refresh count mismatch is rejected before snapshot creation or replacement. |
| MAS-06 | Public CLI/configuration | `J-configure-feature-workflow` → `CFG-resolve-deep-review-cadence`; initial resolution without Tasks uses exactly one slice. |
| MAS-07 | Public CLI/state safety | `J-configure-feature-workflow` → `CFG-freeze-feature-workflow`; malformed present Tasks fail before snapshot creation or replacement. |
| MAS-08 | Public CLI/state safety | `J-configure-feature-workflow` → `CFG-freeze-feature-workflow`; normal resume returns frozen state without re-reading current Tasks. |
| MAS-09 | Public template/adoption | `J-adopt-workflow` → `ADP-validate-generated-feature-contracts`; installed planning guidance distinguishes merge-alone slice, technical phase/cohort, and worker batch. |
| MAS-10 | Internal parser classification | No separate user promise: excluding remediation headings from the primary-task set is an internal classification rule already covered by technical PASS; users observe only the derived count covered by MAS-01/02. |
| MAS-11 | Public planner CLI | `J-configure-feature-workflow` → `CFG-plan-parallel-slice-dispatch`; downstream planning exposes the validator's primary-task Slice membership and IDs unchanged. |

## Planned probes

- In one disposable feature, resolve the valid five-primary-task/one-outcome contract; independently
  reload stdout and `workflow.json` and require one derived group.
- In another disposable feature, resolve two independently mergeable outcomes; require two slice
  IDs and a balanced group containing both.
- Resolve without `tasks.md`; require the documented one-slice default.
- Supply matching and mismatching positive `--slices` assertions during initial resolution and
  refresh, plus zero and negative values; independently confirm rejected cases create no snapshot
  or preserve prior bytes.
- Probe missing outcome, gate, merge-alone decision, and reason; non-exact `yes`; zero, multiple,
  unknown, orphan, and duplicate memberships; require the public diagnostic to identify the
  offending task or slice.
- Change valid Tasks from one to two slices, then replace them with malformed Tasks. Resume after
  each change and independently compare the returned object and snapshot bytes with the frozen
  state; explicitly refresh only the valid change and require two derived slices.
- Feed the same valid two-slice task document to the validator contract output and public read-only
  planner. Compare task-to-slice membership and slice IDs; confirm remediation records and closure
  rows never become planner tasks.
- Inspect the installed workflow-config guidance for the optional-assertion boundary and for the
  slice/phase-or-cohort/batch distinction. Do not treat source-parser structure as a QA verdict.

## Scenario state and limitations

All three mapped CFG scenarios remain `qa_status: untested`; their historical reports are prose
history, not a current verdict. No linked open bug changes this cycle's expected observable. This
repository has no browser, API, mobile, auth, server, or production runtime. Use only the profile's
CLI/manual adapter and checkout-owned disposable repositories; do not install tools, invoke the
networked external-security installer, or contact a remote. The durable technical validation file
records verified head `802aea9`, while this charter covers post-review head `88a3eee`; the QA packet
supplies the later full-gate result, but QA Execute must not present it as a new technical verdict.

## QA Execute handoff

A distinct fresh Verifier session with `phase: qa-execute` must use the canonical `qa-execute`
skill and the CLI/manual adapter from `docs/qa/README.md`. Walk this charter and
`CH-adopt-merge-alone-slice-contract-2026-08-27`, store ignored raw evidence under
`docs/qa/evidence/2026-08-27-merge-alone-slices/`, write a new dated durable report, and update the
four affected scenario verdicts only after independent observable reads. Preserve the adjacent
canary's retained verdict unless the fresh walk invalidates it. No product fix, remote action, or
release action belongs in that session.
