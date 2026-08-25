# J-configure-feature-workflow

**Persona:** Workflow adopter
**Goal:** Configure central provider model/effort and remediation settings, then freeze one feature's review cadence and delegated-provider routes while keeping its remediation bound live.
**Entry point:** `.my-workflow.toml.example` → local `.my-workflow.toml` → `workflow-config` resolver CLI

## Flow

1. Distinguish tracked `.my-workflow.toml.example` and packet templates from ignored local config and generated runtimes; confirm the same ownership boundary in package output and a clean clone.
2. Initialize the local config, select the documented `mixed` profile, edit one model/effort pair per provider, and run explicit sync; inspect all fifteen generated native packets.
3. Run sync again and confirm no runtime packet bytes change; confirm tracked templates remain unchanged.
4. Exercise invalid config, template, metadata, destination, and symlink inputs; confirm each failure names its source and changes no local or outside bytes.
5. Resolve a feature and confirm delegated model/effort values are frozen while planner remains top-level; confirm current JSON reports the default, positive, or unbounded remediation threshold without persisting it.
6. Change only the remediation threshold and resume; confirm the new live value is reported while route, cadence, and snapshot bytes remain frozen.
7. Replace unsynchronized model values, then synchronize deliberate model/effort drift; confirm frozen resume first remains stable, then rejects packet drift until explicit refresh.
8. Confirm cadence grouping, provider precedence, checkout isolation, and adoption preservation as adjacent paths.

## Promises

- [`CFG-resolve-deep-review-cadence`](../scenarios/CFG-resolve-deep-review-cadence.md)
- [`CFG-route-delegated-role-providers`](../scenarios/CFG-route-delegated-role-providers.md)
- [`CFG-freeze-feature-workflow`](../scenarios/CFG-freeze-feature-workflow.md)
- [`CFG-centralize-agent-model-routing`](../scenarios/CFG-centralize-agent-model-routing.md)

## Adjacent canary

Walk [`J-adopt-workflow`](J-adopt-workflow.md) to confirm adoption installs the resolver while
preserving consumer-owned configuration and local-artifact boundaries.
