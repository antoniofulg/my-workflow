# J-configure-feature-workflow

**Persona:** Workflow adopter
**Goal:** Configure, freeze, and inspect one feature's models, review, provider, remediation, and slice-dispatch policy.
**Entry point:** `.my-workflow.toml.example` → local `.my-workflow.toml` → `workflow-config` resolver CLI

## Flow

1. Distinguish tracked `.my-workflow.toml.example` and packet templates from ignored local config and generated runtimes; confirm the same ownership boundary.
2. Initialize local config, select the documented profile, edit model/effort pairs, run explicit sync, and confirm generated packets are stable.
3. Exercise invalid config, template, metadata, destination, and symlink inputs; confirm each failure names its source and changes no bytes.
4. Resolve a feature with cadence, profile, and overrides; confirm delegated model/effort and route are frozen while current JSON reports live remediation without persisting it.
5. Select a supported parallelization mode and optional repository-relative resource provider, then explicitly refresh; confirm snapshot and JSON agree on frozen route, cadence, and parallelization.
6. Change only remediation threshold and resume; confirm the new live value is reported while route, cadence, models, efforts, and snapshot bytes remain frozen.
7. Plan the schema-v2 task state and inspect ready, blocked, checkpoint, or serial-fallback output; reject obsolete schema-v1 snapshots before host effects.
8. Inspect host compatibility through the public preflight command; continue to [`J-execute-parallel-slices`](J-execute-parallel-slices.md) only when the selected host has an identity-matched clean proof and declared resources permit it.
9. Confirm packet drift requires explicit synchronization and refresh, cadence grouping, provider precedence, checkout isolation, and adoption preservation.

## Promises

- [`CFG-resolve-deep-review-cadence`](../scenarios/CFG-resolve-deep-review-cadence.md)
- [`CFG-route-delegated-role-providers`](../scenarios/CFG-route-delegated-role-providers.md)
- [`CFG-freeze-feature-workflow`](../scenarios/CFG-freeze-feature-workflow.md)
- [`CFG-plan-parallel-slice-dispatch`](../scenarios/CFG-plan-parallel-slice-dispatch.md)
- [`CFG-fallback-unproven-parallel-execution`](../scenarios/CFG-fallback-unproven-parallel-execution.md)
- [`CFG-centralize-agent-model-routing`](../scenarios/CFG-centralize-agent-model-routing.md)

## Adjacent canary

Walk [`J-adopt-workflow`](J-adopt-workflow.md) to confirm adoption installs the resolver while
preserving consumer-owned configuration and local-artifact boundaries.

## Terminal QA status

`CFG-freeze-feature-workflow`, `CFG-plan-parallel-slice-dispatch`, and
`CFG-fallback-unproven-parallel-execution` are `pass`. QA on 2026-08-26 accepted schema v2, rejected
schema v1, and proved disabled/incompatible host paths had zero effect. The real Orca/Codex worker
journey remains separately `blocked-verify` in
[`J-execute-parallel-slices`](J-execute-parallel-slices.md).

Fresh fix-loop QA at `cd1886f` re-passed the affected schema, fallback, host-rejection, policy, and
full-gate legs with every measured residue delta zero.
