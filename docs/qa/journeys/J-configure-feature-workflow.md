# J-configure-feature-workflow

**Persona:** Workflow adopter
**Goal:** Configure central provider model/effort settings, then freeze one feature's review cadence and delegated-provider routes.
**Entry point:** `.my-workflow.toml.example` → local `.my-workflow.toml` → `workflow-config` resolver CLI

## Flow

1. Initialize the local config from the tracked example, edit its complete v2 model matrix, and run explicit sync; inspect all fifteen generated native packets.
2. Run sync again and confirm no runtime packet bytes change; confirm tracked templates remain unchanged.
3. Resolve a feature and confirm delegated model/effort values are frozen while planner remains top-level.
4. Synchronize a deliberate delegated model change, confirm ordinary resume rejects drift, then explicitly refresh.
5. Add a cadence and partial mixed-provider profile, then confirm route precedence and adoption preservation.

## Promises

- [`CFG-resolve-deep-review-cadence`](../scenarios/CFG-resolve-deep-review-cadence.md)
- [`CFG-route-delegated-role-providers`](../scenarios/CFG-route-delegated-role-providers.md)
- [`CFG-freeze-feature-workflow`](../scenarios/CFG-freeze-feature-workflow.md)
- [`CFG-centralize-agent-model-routing`](../scenarios/CFG-centralize-agent-model-routing.md)

## Adjacent canary

Walk [`J-adopt-workflow`](J-adopt-workflow.md) to confirm adoption installs the resolver while
preserving consumer-owned configuration and local-artifact boundaries.
