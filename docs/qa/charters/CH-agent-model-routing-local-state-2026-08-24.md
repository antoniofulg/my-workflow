# CH-agent-model-routing-local-state-2026-08-24

- **Date:** 2026-08-24
- **Scope:** `059cbd0..255be33` on `feat/agent-model-routing`
- **Time-box:** 60 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-configure-feature-workflow`](../journeys/J-configure-feature-workflow.md)
- **Tour:** Local-source ownership, mixed routing, synchronization, containment, snapshot, and resume tour
- **Public entry point:** `.my-workflow.toml.example` → local `.my-workflow.toml` → `workflow-config --sync-agents` → feature resolve/resume/refresh
- **Adapter:** CLI/manual through the public resolver declared in [`docs/qa/README.md`](../README.md)
- **Scenarios:** `CFG-centralize-agent-model-routing`, `CFG-freeze-feature-workflow`,
  `CFG-route-delegated-role-providers`, `CFG-resolve-deep-review-cadence`,
  `CFG-keep-local-artifacts-out-of-git`

## Mission

Use checkout-local disposable Git repositories to prove that tracked example/templates generate
ignored checkout-local runtimes from one local config, including the documented `mixed` profile.
Walk synchronization, idempotence, pre-write failures, symlink containment, checkout isolation,
snapshot/resume/refresh, package contents, and clean-clone regeneration through public commands and
independent byte, Git, package, JSON, and filesystem reads.

## Expected observable

The adopter can configure every provider-role pair locally without dirtying tracked sources,
generate deterministic contained runtimes, freeze delegated settings, detect drift, and reproduce
the same ownership contract from tracked package/clone state.

## Requirement disposition

| Requirement | Public disposition | Canonical scenario |
| --- | --- | --- |
| AMR-01 | Complete provider-role settings and documented `mixed` profile are public configuration. | `CFG-centralize-agent-model-routing`; `CFG-route-delegated-role-providers` |
| AMR-02 | Missing-config initialization and fifteen native runtimes are public CLI/filesystem behavior. | `CFG-centralize-agent-model-routing` |
| AMR-03 | Template and non-model instruction preservation is a public source-ownership promise. | `CFG-centralize-agent-model-routing` |
| AMR-04 | Repeated sync byte stability is a public idempotence promise. | `CFG-centralize-agent-model-routing` |
| AMR-05 | Frozen model/effort snapshot state is public resume behavior. | `CFG-freeze-feature-workflow` |
| AMR-06 | Drift rejection and explicit refresh are public recovery behavior. | `CFG-freeze-feature-workflow` |
| AMR-07 | Fresh and existing-project generation is public adoption behavior. | `ADP-adopt-workflow-safely` |
| AMR-08 | Tracked-source versus ignored-state guidance is docs-as-interface. | `CFG-centralize-agent-model-routing`; `CFG-keep-local-artifacts-out-of-git` |
| AMR-09 | Git/package/clean-clone ownership is public distribution behavior. | `CFG-keep-local-artifacts-out-of-git` |

All nine requirements alter CLI, configuration, generated files, snapshots, adoption,
documentation, or package/Git observables. None is internal-only.

## Acceptance-criterion disposition

| Spec criterion | Public disposition | Canonical scenario |
| --- | --- | --- |
| Configure 1: tracked complete matrix and `mixed` profile | Config/package promise | `CFG-centralize-agent-model-routing`; `CFG-route-delegated-role-providers` |
| Configure 2: missing local config initializes and sync renders native packets | CLI/filesystem promise | `CFG-centralize-agent-model-routing` |
| Configure 3: sync leaves tracked templates byte-identical | Preservation promise | `CFG-centralize-agent-model-routing` |
| Configure 4: unchanged second sync is byte-identical | Idempotence promise | `CFG-centralize-agent-model-routing` |
| Configure 5: invalid config, matrix, effort, or template fails before writes | Recovery/containment promise | `CFG-centralize-agent-model-routing` |
| Configure 6: sync reports changed and current packet paths | CLI-output promise | `CFG-centralize-agent-model-routing` |
| Freeze 1: resolve/refresh stores every delegated model and effort | Snapshot promise | `CFG-freeze-feature-workflow` |
| Freeze 2: resume returns frozen values without reading replacements | Resume promise | `CFG-freeze-feature-workflow` |
| Freeze 3: packet drift fails with sync/refresh guidance | Recovery promise | `CFG-freeze-feature-workflow` |
| Freeze 4: planner synchronizes but remains non-delegated | Routing promise | `CFG-freeze-feature-workflow` |
| Adopt 1: fresh adoption installs sources/local state and generates runtimes | Adoption promise | `ADP-adopt-workflow-safely` |
| Adopt 2: existing local config is byte-preserved and drives regeneration | Preservation promise | `ADP-adopt-workflow-safely` |
| Adopt 3: invalid local config/template fails and names its source | Recovery promise | `ADP-adopt-workflow-safely` |
| Adopt 4: docs distinguish tracked sources from ignored operator state | Docs-as-interface promise | `CFG-centralize-agent-model-routing`; `CFG-keep-local-artifacts-out-of-git` |

## Planned probes

- From a disposable clone missing local state, inspect tracked example/templates, Git-ignore results,
  and package contents; require no tracked runtime/config entries. Run documented sync and confirm
  local config initialization plus exactly fifteen native runtimes without template-byte changes.
- Select the exact `mixed` profile, change one model/effort pair per provider, resolve a disposable
  feature, and compare CLI JSON with independently reloaded native packets and `workflow.json`.
- Run unchanged sync twice; require exact changed/unchanged path sets and a byte-identical runtime
  tree on the second run.
- Before every failure probe, hash local and outside targets. Exercise missing/unknown matrix keys,
  invalid effort, missing/duplicate native metadata, existing/dangling destination links, linked
  runtime parents, linked config/example/template sources, and existing/dangling `--root` links.
  Require non-zero exit, named source/path, empty success output, and unchanged local/outside bytes.
- Resolve four delegated roles and confirm provider, file, model, and effort are frozen while planner
  is absent. Replace unsynchronized config and require identical resume output. After sync creates
  model and effort drift, require ordinary resume failure and explicit-refresh guidance; refresh
  and independently reload the new snapshot.
- Use two disposable checkouts with distinct local configs; require each sync to touch only its own
  runtimes. Clone tracked state into a third clean checkout and regenerate local state without
  copying source-checkout config/runtime bytes.
- Adjacent canaries: confirm v2 cadence still produces balanced consecutive groups; confirm mixed
  provider precedence still resolves override over profile over native without fallback; inspect
  release package metadata without changing `REL-report-current-workflow-release` from its retained
  `pass` unless an observed canary failure invalidates it.

## QA Execute handoff

Fresh Verifier: invoke `qa-execute`, read `docs/qa/README.md`, and use its declared CLI/manual
adapter against `255be33`. The technical validation artifact names `059cbd0..a9bb322`; the later
`255be33` commit revises that validation artifact only, so QA must report its actual execution HEAD
without treating the older range label as live-user evidence. Exact resolver path:
`.agents/skills/workflow-config/scripts/workflow_config.py`; use documented `--sync-agents`, feature
resolution, resume, and `--refresh` forms only. Store raw evidence under
`docs/qa/evidence/2026-08-24-agent-model-routing-local-state/` and write a new durable report at
`docs/qa/reports/2026-08-24-agent-model-routing-local-state.md`.

Limitations: no live-model harness exists, so provider model availability and model/effort
compatibility remain provider-runtime concerns. No browser, API, mobile, auth, server, or production
health surface exists. Do not install tools, contact remote services, or treat structural tests as
real-user evidence.
