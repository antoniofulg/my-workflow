# J-configure-feature-workflow

**Persona:** Workflow adopter
**Goal:** Configure, freeze, and inspect one feature's models, review, provider, remediation, and slice-dispatch policy.
**Entry point:** `.my-workflow.toml.example` → local `.my-workflow.toml` → `workflow-config` resolver CLI

## Flow

1. Distinguish tracked `.my-workflow.toml.example` and packet templates from ignored local config and generated runtimes; confirm the same ownership boundary.
2. Initialize local config, select the documented profile, edit model/effort pairs, run explicit sync, and confirm generated packets are stable, carrying each Claude role's `skills:` preload and `disallowedTools:` scope byte-identical to its template; confirm a template preloading a skill with no `SKILL.md` fails the sync by name and writes nothing.
3. Exercise invalid config, template, metadata, destination, and symlink inputs; confirm each failure names its source and changes no bytes.
4. Author `tasks.md` from the installed task template, declaring one `**Slice:**` field per primary task and one `## Vertical Slice Closure` row per used slice; confirm the template names the slice/phase/batch distinction and that `validate_tasks.py --slice-contract-json` reports the same membership the document declares.
5. Resolve a feature with cadence, profile, and overrides; confirm the slice count is derived from the validated closure contract (one slice when `tasks.md` is absent), that `--slices` acts only as an assertion, and that delegated model/effort and route are frozen while current JSON reports live remediation without persisting it.
6. Select a supported parallelization mode and optional repository-relative resource provider, then explicitly refresh; confirm snapshot and JSON agree on frozen route, cadence, and parallelization, and that refresh re-derives the count from current tasks.
7. Change only remediation threshold and resume; confirm the new live value is reported while route, cadence, models, efforts, derived slice count, and snapshot bytes remain frozen even when `tasks.md` changed or became malformed.
8. Plan the versioned task state and inspect ready, blocked, checkpoint, or serial-fallback output; confirm planner membership equals the validator's primary-task membership and that review remediation records are ignored; continue to [`J-execute-parallel-slices`](J-execute-parallel-slices.md) only when capability and declared resources permit it.
9. Confirm packet drift requires explicit synchronization and refresh, cadence grouping, provider precedence, checkout isolation, and adoption preservation.

## Promises

- [`CFG-resolve-deep-review-cadence`](../scenarios/CFG-resolve-deep-review-cadence.md)
- [`CFG-route-delegated-role-providers`](../scenarios/CFG-route-delegated-role-providers.md)
- [`CFG-freeze-feature-workflow`](../scenarios/CFG-freeze-feature-workflow.md)
- [`CFG-plan-parallel-slice-dispatch`](../scenarios/CFG-plan-parallel-slice-dispatch.md)
- [`CFG-centralize-agent-model-routing`](../scenarios/CFG-centralize-agent-model-routing.md)
- [`CFG-derive-merge-alone-slices`](../scenarios/CFG-derive-merge-alone-slices.md)
- [`CFG-preload-agent-skills-in-packets`](../scenarios/CFG-preload-agent-skills-in-packets.md)

## Adjacent canary

Walk [`J-adopt-workflow`](J-adopt-workflow.md) to confirm adoption installs the resolver while
preserving consumer-owned configuration and local-artifact boundaries.

## Terminal QA status

`CFG-freeze-feature-workflow`, `CFG-plan-parallel-slice-dispatch`, and
`CFG-fallback-unproven-parallel-execution` are `pass` in the terminal report. The safe optional
provider boundary is the repository's frozen `resource_provider: null` path; resource-bearing work
serializes before mutation. The real Orca/Codex worker journey remains separately
`blocked-verify` in [`J-execute-parallel-slices`](J-execute-parallel-slices.md).

The v3 assisted and planner promises are reset to `untested` for the 2026-08-29 offline QA cycle;
the passing zero-effect fallback remains an adjacent canary and will be reconfirmed in that cycle.

The 2026-09-03 `phase-skills` cycle resets `CFG-centralize-agent-model-routing` and
`CFG-derive-merge-alone-slices` to `untested` and adds `CFG-preload-agent-skills-in-packets`; see
[`CH-adopt-phase-skills-2026-09-03`](../charters/CH-adopt-phase-skills-2026-09-03.md).
