# J-configure-feature-workflow

**Persona:** Workflow adopter
**Goal:** Configure, freeze, and inspect one feature's review, provider, and slice-dispatch policy.
**Entry point:** `.my-workflow.toml` → `workflow-config` resolver CLI

## Flow

1. Start with no config and resolve a feature using the current provider and disabled dispatch.
2. Select a supported parallelization mode and optional repository-relative resource provider, then
   explicitly refresh the feature resolution.
3. Add a cadence, partial mixed-provider profile, and role override; confirm precedence in JSON stdout and the feature snapshot.
4. Plan the versioned task state and inspect ready, blocked, checkpoint, or serial-fallback output.
5. Resume without refresh and confirm the frozen route survives config and HEAD changes.
6. Correct a named invalid input after the resolver rejects it without fallback or snapshot loss.
7. Continue to [`J-execute-parallel-slices`](J-execute-parallel-slices.md) only when the frozen mode,
   adapter capability, and declared resources permit it.

## Promises

- [`CFG-resolve-deep-review-cadence`](../scenarios/CFG-resolve-deep-review-cadence.md)
- [`CFG-route-delegated-role-providers`](../scenarios/CFG-route-delegated-role-providers.md)
- [`CFG-freeze-feature-workflow`](../scenarios/CFG-freeze-feature-workflow.md)
- [`CFG-plan-parallel-slice-dispatch`](../scenarios/CFG-plan-parallel-slice-dispatch.md)

## Adjacent canary

Walk [`J-adopt-workflow`](J-adopt-workflow.md) to confirm adoption installs the resolver while
preserving consumer-owned configuration and local-artifact boundaries.

## Terminal QA status

`CFG-freeze-feature-workflow`, `CFG-plan-parallel-slice-dispatch`, and
`CFG-fallback-unproven-parallel-execution` are `pass` in the terminal report. The safe optional
provider boundary is the repository's frozen `resource_provider: null` path; resource-bearing work
serializes before mutation. The real Orca/Codex worker journey remains separately
`blocked-verify` in [`J-execute-parallel-slices`](J-execute-parallel-slices.md).
