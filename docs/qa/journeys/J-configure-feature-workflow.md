# J-configure-feature-workflow

**Persona:** Workflow adopter
**Goal:** Configure, derive, freeze, and inspect one feature's models, review, provider, remediation, and slice-dispatch policy.
**Entry point:** `.my-workflow.toml.example` → local `.my-workflow.toml` → `workflow-config` resolver CLI

## Flow

1. Distinguish tracked `.my-workflow.toml.example` and packet templates from ignored local config and generated runtimes; confirm the same ownership boundary.
2. Initialize local config, select the documented profile, edit model/effort pairs, run explicit sync, and confirm generated packets are stable.
3. Exercise invalid config, template, metadata, destination, and symlink inputs; confirm each failure names its source and changes no bytes.
4. Define each primary task's `Slice` and the vertical-slice closure table; confirm every outcome is merge-alone, observable, independently gated, and justified.
5. Resolve a feature with validated Tasks, cadence, profile, and overrides; confirm the resolver derives slice count from the closure contract and freezes delegated model/effort and route while current JSON reports live remediation without persisting it.
6. Select a supported parallelization mode and optional repository-relative resource provider, then explicitly refresh; confirm snapshot and JSON agree on frozen route, derived cadence, and parallelization. A feature without Tasks resolves as one slice.
7. Change only remediation threshold and resume; confirm the new live value is reported while route, cadence, models, efforts, and snapshot bytes remain frozen without re-reading Tasks.
8. Plan the versioned task state and inspect ready, blocked, checkpoint, or serial-fallback output; confirm planner membership follows primary task `Slice` fields and continue to [`J-execute-parallel-slices`](J-execute-parallel-slices.md) only when capability and declared resources permit it.
9. Confirm packet drift requires explicit synchronization and refresh, cadence grouping, provider precedence, checkout isolation, and adoption preservation.

## Promises

- [`CFG-resolve-deep-review-cadence`](../scenarios/CFG-resolve-deep-review-cadence.md)
- [`CFG-route-delegated-role-providers`](../scenarios/CFG-route-delegated-role-providers.md)
- [`CFG-freeze-feature-workflow`](../scenarios/CFG-freeze-feature-workflow.md)
- [`CFG-plan-parallel-slice-dispatch`](../scenarios/CFG-plan-parallel-slice-dispatch.md)
- [`CFG-centralize-agent-model-routing`](../scenarios/CFG-centralize-agent-model-routing.md)

## Adjacent canary

Walk [`J-adopt-workflow`](J-adopt-workflow.md) to confirm adoption installs the resolver while
preserving consumer-owned configuration and local-artifact boundaries.

## Terminal QA status

`CFG-resolve-deep-review-cadence`, `CFG-freeze-feature-workflow`, and
`CFG-plan-parallel-slice-dispatch` are `untested` pending a fresh walk of the merge-alone slice
contract. The safe optional provider boundary is the repository's frozen `resource_provider: null`
path; resource-bearing work serializes before mutation. The real Orca/Codex worker journey remains
separately `blocked-verify` in [`J-execute-parallel-slices`](J-execute-parallel-slices.md).
