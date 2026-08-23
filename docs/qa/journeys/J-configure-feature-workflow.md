# J-configure-feature-workflow

**Persona:** Workflow adopter
**Goal:** Configure and freeze one feature's review cadence and delegated-provider routes.
**Entry point:** `.my-workflow.toml` → `workflow-config` resolver CLI

## Flow

1. Start with no config and resolve a feature using the current provider.
2. Add a cadence and partial mixed-provider profile, then explicitly refresh the feature resolution.
3. Add one role override and confirm precedence in JSON stdout and the feature snapshot.
4. Resume without refresh and confirm the frozen route survives config and HEAD changes.
5. Correct a named invalid input after the resolver rejects it without fallback or snapshot loss.
6. Declare `[remediation] stall_attempts`, confirm the resolver reports it while leaving it out of the
   frozen snapshot, and confirm a changed threshold reaches a resumed feature.

## Promises

- [`CFG-resolve-deep-review-cadence`](../scenarios/CFG-resolve-deep-review-cadence.md)
- [`CFG-route-delegated-role-providers`](../scenarios/CFG-route-delegated-role-providers.md)
- [`CFG-freeze-feature-workflow`](../scenarios/CFG-freeze-feature-workflow.md)
- [`CFG-bound-remediation-stall-attempts`](../scenarios/CFG-bound-remediation-stall-attempts.md)

## Adjacent canary

Walk [`J-adopt-workflow`](J-adopt-workflow.md) to confirm adoption installs the resolver while
preserving consumer-owned configuration and local-artifact boundaries.
