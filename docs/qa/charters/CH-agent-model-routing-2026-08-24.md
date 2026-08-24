# CH-agent-model-routing-2026-08-24

- **Date:** 2026-08-24
- **Time-box:** 45 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-configure-feature-workflow`](../journeys/J-configure-feature-workflow.md)
- **Tour:** Central configuration, synchronization, frozen resume, adoption, and recovery tour
- **Public entry point:** `.my-workflow.toml` -> `workflow-config --sync-agents` -> feature resolution
- **Adapter candidate:** CLI/manual through the public resolver and adoption commands declared in
  [`docs/qa/README.md`](../README.md)
- **Scenarios:** `CFG-centralize-agent-model-routing`, `CFG-freeze-feature-workflow`,
  `CFG-resolve-deep-review-cadence`, `ADP-adopt-workflow-safely` (adjacent canary)

## Mission

Use checkout-local disposable Git repositories to change central model settings, synchronize all
provider packets, resolve and resume one feature, recover from deliberate drift, and adopt into
fresh and pre-populated targets. Confirm outcomes through CLI JSON, independently reloaded packet
and snapshot bytes, and target inspection.

## Expected observable

The adopter controls all fifteen native model and effort fields from one v2 TOML file without
instruction-byte loss, sees exact changed/unchanged paths, keeps delegated settings frozen until an
explicit refresh, and can adopt or re-adopt without losing consumer-owned configuration.

## Criterion disposition ledger

All changed acceptance criteria alter a public CLI, public configuration, generated packet,
snapshot, adoption, or documentation promise. No acceptance criterion is internal-only.

| Spec criterion | Disposition | Canonical scenario |
| --- | --- | --- |
| Configure every agent 1: complete 3-provider x 5-role model/effort matrix | Public config promise | `CFG-centralize-agent-model-routing` |
| Configure every agent 2: explicit sync renders native packet metadata | Public CLI/filesystem promise | `CFG-centralize-agent-model-routing` |
| Configure every agent 3: sync preserves non-model packet bytes | Public preservation promise | `CFG-centralize-agent-model-routing` |
| Configure every agent 4: unchanged second sync is byte-identical | Public idempotence promise | `CFG-centralize-agent-model-routing` |
| Configure every agent 5: invalid matrix, effort, or packet fails before writes | Public recovery promise | `CFG-centralize-agent-model-routing` |
| Configure every agent 6: sync reports changed and current packet paths | Public CLI-output promise | `CFG-centralize-agent-model-routing` |
| Freeze delegated settings 1: resolve/refresh stores every delegated model and effort | Public snapshot promise | `CFG-freeze-feature-workflow` |
| Freeze delegated settings 2: resume returns frozen settings despite config replacement | Public resume promise | `CFG-freeze-feature-workflow` |
| Freeze delegated settings 3: packet drift fails with sync/refresh guidance | Public recovery promise | `CFG-freeze-feature-workflow` |
| Freeze delegated settings 4: planner synchronizes but remains non-delegated | Public routing promise | `CFG-freeze-feature-workflow` |
| Adopt centralized contract 1: fresh adoption installs v2 config and synchronizes packets | Public adoption promise | `ADP-adopt-workflow-safely` |
| Adopt centralized contract 2: re-adoption preserves config and packet instructions | Public preservation promise | `ADP-adopt-workflow-safely` |
| Adopt centralized contract 3: unsynchronizable adoption fails and names the packet | Public recovery promise | `ADP-adopt-workflow-safely` |
| Adopt centralized contract 4: docs identify central source and generated fields | Public docs-as-interface promise | `CFG-centralize-agent-model-routing` |

`CFG-resolve-deep-review-cadence` is reset because the public configuration hard-cuts from optional
v1/default handling to the shipped required v2 matrix. `CFG-route-delegated-role-providers` retains
its prior `pass`: routing precedence and provider-file selection did not change. The adoption
journey is the adjacent canary and is also directly affected by the new install/sync step.

## Planned probes

- Copy the active checkout into a disposable Git target, edit one model/effort pair per provider,
  run the documented `--sync-agents` command, and compare all fifteen native fields with the config.
- Record CLI JSON and independently verify exact `changed` paths; checksum packet bodies with only
  native model metadata excluded.
- Run sync again; verify empty `changed`, complete `unchanged`, and byte-identical packet tree.
- Try a missing role, unknown matrix key, invalid effort, and malformed native metadata; require
  exit `2`, one actionable path/packet diagnostic, and zero packet changes.
- Resolve a disposable feature and independently reload `workflow.json`; verify four delegated
  roles contain provider, agent file, model, and effort while planner is absent.
- Change and synchronize one delegated model and one effort. Require ordinary resume to reject drift
  with sync plus explicit-refresh guidance; then refresh and verify the new frozen values.
- Recheck configured cadence and balanced review groups under v2 config; keep the unchanged
  provider-routing scenario as a retained verdict, not an execution target for this cycle.
- Adjacent adoption canary: adopt into fresh and pre-populated disposable targets. Verify fresh v2
  config and fifteen synchronized packets; verify existing config and non-model packet bytes remain
  byte-identical; verify malformed packet adoption fails and names it.
- Follow README and installed skill text as user-facing instructions; confirm they identify central
  ownership, generated fields, explicit sync, frozen resume, and explicit refresh.
- Remove only checkout-local disposable targets and confirm source residue is limited to planned
  `docs/qa/` artifacts and ignored raw evidence.

## QA Execute handoff

Start a fresh Verifier session with `phase: qa-execute`. Read `docs/qa/README.md`, invoke the
canonical `qa-execute` skill, and use its declared CLI/manual adapter. Exact public paths are
`.agents/skills/workflow-config/scripts/workflow_config.py` with `--sync-agents` or documented
feature-resolution arguments, and `scripts/adopt.py` against separate checkout-local disposable
targets. Store raw evidence under `docs/qa/evidence/2026-08-24-agent-model-routing/`, write a new
durable report, and update only scenario verdict fields supported by observed evidence.

Limitations: no live-model execution harness exists; model availability and model/effort
compatibility remain provider-runtime concerns. This repository has no browser, API, mobile, auth,
server, or production-health surface. Do not install tools, invoke the networked external-security
installer, contact remote services, or treat structural test results as real-user evidence.

End before product remediation. A confirmed product defect returns to an Implementer and requires a
fresh Verifier after the fix.
