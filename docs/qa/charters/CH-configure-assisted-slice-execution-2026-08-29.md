# CH-configure-assisted-slice-execution-2026-08-29

- **Date:** 2026-08-29
- **Time-box:** 45 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-configure-feature-workflow`](../journeys/J-configure-feature-workflow.md)
- **Tour:** v3 defaults, adaptive planning, serial fallback, role separation, and residue canary
- **Public entry point:** `.my-workflow.toml` → `workflow_config.py` → `parallel_plan.py` → `parallel_execute.py start|status`
- **Adapter candidate:** CLI/manual with checkout-local fake health and resource providers
- **Scenarios:** `CFG-freeze-feature-workflow`, `CFG-plan-parallel-slice-dispatch`, `CFG-fallback-unproven-parallel-execution`
- **Adjacent canary:** `ADP-adopt-workflow-safely`

## Mission

Configure a disposable v3 feature through public CLIs and observe assisted-by-default planning,
dynamic writer admission, sequential tasks within each slice, and zero-effect serial fallback when
dependency, health, ownership, or resource proof is missing.

## Expected observable

Configuration and frozen snapshot agree on schema v3, default `assisted`/`auto`, baseline two,
automatic ceiling four, routes and cadence. Ready compatible slices receive bounded writer lanes;
one ready slice and `disabled` mode use the clean integration checkout; invalid or unproven inputs
produce decisive JSON and no external effect or residue.

## Criterion disposition

| Criterion | Disposition |
| --- | --- |
| HSE-07 | Public configuration. Map to `CFG-freeze-feature-workflow`; compare resolver JSON and reloaded snapshot schema `3`. |
| HSE-08 | Public configuration. Observe default `assisted`, explicit `disabled`, and rejection of every other mode. |
| HSE-09 | Public configuration. Observe default `auto`, valid positive integers, and rejection of booleans, zero, negatives, and strings other than `auto`. |
| HSE-10 | Public frozen-state promise. Reload mode, cap, baseline, ceiling, provider, routes, and cadence from the feature snapshot. |
| HSE-11 | Public fail-closed result. Use disposable v1/v2 config and snapshot copies; require refresh guidance and zero executor effects. |
| HSE-12 | User-visible fallback. Walk `CFG-fallback-unproven-parallel-execution`; `disabled` must use the integration checkout with zero concurrent-writer worktree effects. |
| HSE-13 | Public planner output. A blocked DAG reports dependency IDs and no writer action. |
| HSE-14 | Public scheduler output. Exactly one ready slice runs serially in the integration checkout and leaves no extra worktree. |
| HSE-15 | Public scheduler output. Two compatible ready slices start no more than two writer lanes. |
| HSE-16 | Public adaptive behavior. Fake healthy settle windows admit one lane at a time and never exceed four in `auto`. |
| HSE-17 | Public fail-closed behavior. Missing, malformed, stale, or unhealthy evidence admits no lane above two while active work remains represented. |
| HSE-18 | Public explicit cap. Integer caps bound concurrency and health still gates every lane above two. |
| HSE-19 | Public scheduling behavior. A released lane receives the next compatible ready slice, independent of odd/even numbering. |
| HSE-20 | Docs/CLI workflow promise. Inspect lane records and installed instructions: only concurrent implementer writers own persistent worktrees. |
| HSE-21 | Public provider boundary. Fake exclusive leases serialize competing heavy gates, release after use, and do not block unrelated light work. |
| HSE-30 | Docs-as-interface. Inspect installed implementer route for sequential slice tasks, scoped gates, and atomic Conventional Commits. |
| HSE-31 | Docs-as-interface with observable trace. A dependent slice remains parked until a fresh slice-keyed Technical Verifier checkpoint exists. |
| HSE-32 | Docs-as-interface. Integrated review routing names a fresh Deep Reviewer over the frozen commit range, not a writer tree. |
| HSE-33 | Public workflow routing. Installed roles require fresh QA Plan and QA Execute after final implementation review. This session supplies only QA Plan. |
| HSE-34 | Docs-as-interface. The last implementer packet ends with compact handoff and excludes verification, review, and final QA duties. |
| HSE-44 | Public conflict result. Overlapping write paths serialize and report the conflicting paths without creating a second writer lane. |
| HSE-45 | Public parked-state result. A moved checkpoint keeps the consumer parked until synchronization and fresh verification. |
| HSE-46 | Public refusal. A dirty integration checkout causes no writer, worktree, Orca, Git, or provider mutation. |
| HSE-48 | Public provider failure. A denied lease waits or fails closed while an unrelated light task remains eligible. |

## Planned probes

1. Create a disposable Git feature, resolve defaults, and independently reload stdout and snapshot.
2. Exercise valid `assisted`/`disabled` modes, `auto` and integer caps, plus old-version and malformed
   inputs; compare state and effect logs after every refusal.
3. Plan zero-ready, one-ready, two-compatible, path-conflicting, dependency-moving, and lane-reuse
   DAGs; reload deterministic JSON from a fresh process.
4. Feed fake health sequences for healthy, stale, malformed, unhealthy, and non-finite/count-invalid
   evidence; observe baseline and incremental admission.
5. Feed fake lease acquire/release receipts for heavy/light contention and refusal; independently
   inspect correlation and effect counts.
6. Walk `disabled` and dirty-checkout cases and require zero worktree/provider/worker effects plus
   zero disposable residue.
7. Inspect installed role and orchestration instructions for author/verifier/reviewer/QA separation.
8. Re-adopt one target as the adjacent canary and require consumer-owned config preservation.

## QA Execute handoff

Use a fresh Verifier with `qa-execute` and the existing CLI/manual adapter. Use public resolver,
planner, executor, and fake-provider paths only. Record current evidence in
`docs/qa/evidence/2026-08-29-hybrid-slice-execution/`, write one durable report, and update the three
named CFG scenarios. Do not substitute structural test output for public CLI observations and do
not use live Orca.
