# CH-consume-derived-slice-membership-2026-09-02

- **Date:** 2026-09-02
- **Scope:** `main..5d517be` on `feat/merge-alone-slices`
- **Time-box:** 30 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-configure-feature-workflow`](../journeys/J-configure-feature-workflow.md)
- **Tour:** Downstream-consumer agreement tour
- **Public entry point:** `python3 .agents/skills/workflow-config/scripts/parallel_plan.py` over a snapshot produced by `workflow_config.py`
- **Adapter candidate:** CLI/manual with a checkout-local disposable Git repository, as declared in [`docs/qa/README.md`](../README.md)
- **Scenario:** `CFG-derive-merge-alone-slices`
- **Adjacent canary:** `CFG-plan-parallel-slice-dispatch`

## Mission

Close the loop the derived count opens: the planner must consume the resolver's snapshot and report
exactly the membership the validator derived — over every heading shape the validator accepts, and
with remediation records contributing nothing.

## Expected observable

For the two-slice fixture, the union of planned lanes and blocked tasks equals the validator's
`task_slices` mapping, slice ids included. A `### T2R1:` record following `T2` changes nothing about
`T2`'s plan: same lane or blocked placement, resources `none`, dependencies unchanged. Primary tasks
written with `##`, `####`, or lowercase `t` headings are seen by both tools alike.

## Planned probes

- Resolve the two-slice fixture, then plan from the resulting snapshot. Compare the planner's lane
  plus blocked membership against `--slice-contract-json` output field by field. Require equality.
- Plan the same feature twice. Require identical JSON.
- Insert a `### T2R1:` record after `T2` carrying `**Status:** complete`, `**Resources:** db`, and
  `**Depends on:** T3`. Plan again and diff against the record-free run. Require a zero diff for
  `T2` — status, resources, and dependency edges all unmoved — and no extra candidate for `T2R1`.
- Rewrite the fixture's primary task headings as `## T1:`, `#### T2:`, `### t3:`, and `### T4:`.
  Require the validator to see four tasks and the planner's membership to match it, with no
  `fallback` and empty `reasons`.
- Add a phase heading listing `#### T1:` above the task's own `### T1:` definition. Require the
  planner to merge the listing with the definition rather than double-count or fall back.
- Adjacent canary: read `CFG-plan-parallel-slice-dispatch`'s prior promise and confirm the planner
  still emits deterministic ready/blocked/checkpoint/serial-fallback output and preserves every
  delivery gate. Do not launch a worker, contact Orca, or touch a live terminal.
- Remove only checkout-owned targets and record source-checkout residue. Do not edit product code.

## QA Execute handoff

Start a fresh Verifier session with `phase: qa-execute`. Read `docs/qa/README.md`, invoke canonical
`qa-execute`, and use its CLI/manual adapter at HEAD `5d517be`. This is a read-only planning tour:
no worker dispatch, no worktree creation, no network. Store raw evidence under
`docs/qa/evidence/2026-09-02-merge-alone-slices/`, write into
`docs/qa/reports/2026-09-02-merge-alone-slices.md`, and hand any planner defect to an Implementer.
If a planner disagreement is found, report it against `CFG-derive-merge-alone-slices` and state in
the report that `CFG-plan-parallel-slice-dispatch` is affected; do not edit that frozen scenario.
