# CH-agent-model-routing-adoption-boundary-2026-08-24

- **Date:** 2026-08-24
- **Scope:** `059cbd0..255be33` on `feat/agent-model-routing`
- **Time-box:** 45 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Fresh adoption, preservation, failure, package, and clean-clone tour
- **Public entry point:** `README.md` → `scripts/adopt.py` → generated target files
- **Adapter:** CLI/manual through the adoption command declared in [`docs/qa/README.md`](../README.md)
- **Scenarios:** `ADP-adopt-workflow-safely`, `CFG-keep-local-artifacts-out-of-git`

## Mission

Adopt into fresh and pre-populated checkout-local targets. Prove tracked example/templates install,
ignored local state generates, existing operator/consumer bytes survive, invalid sources fail before
partial writes, and tracked source/package state can travel to a clean clone and regenerate its own
local runtimes. Retain unrelated adoption and release promises as adjacent canaries.

## Expected observable

Fresh and existing consumers receive usable local agent configuration without losing owned files;
tracked sources travel through Git/package boundaries while each checkout owns its ignored runtime.

## Planned probes

- Fresh target: run documented adoption, inspect tracked example/templates, initialized local config,
  fifteen native runtimes, Git-ignore ownership, workflow tour, and absence of unapproved external
  security skills or ai-memory runtime state.
- Existing target: seed custom local model/effort values, consumer template/profile sentinels,
  unrelated ignore lines, `tools/ad-index.py`, and feature state. Re-adopt; require byte preservation
  for consumer-owned/local inputs and regenerated native metadata/non-model instructions.
- Failure recovery: use malformed local config and malformed/missing/linked template sources;
  require non-zero exit naming the invalid source and no partial source/runtime changes.
- Package/clone: inspect declared package output for all tracked sources and zero local config/runtime
  entries, materialize a clean checkout from tracked state, adopt or sync there, and confirm its
  local outputs do not inherit another checkout's operator choices.
- Adjacent canaries: keep feature state Git-visible, preserve managed/unrelated ignore rules,
  preserve the existing QA profile, omit source-only pack material, keep external security skills
  separately authorized, and compare release/package identity without resetting their retained
  scenario verdicts unless observation invalidates them.
- Cleanup only checkout-local disposable targets; source residue must be limited to planned
  `docs/qa/` records and ignored raw evidence.

## QA Execute handoff

Execute together with `CH-agent-model-routing-local-state-2026-08-24` in one fresh `qa-execute`
Verifier session. Use `scripts/adopt.py` against separate checkout-local disposable targets and the
profile's filesystem/Git/package read paths. Store raw evidence under
`docs/qa/evidence/2026-08-24-agent-model-routing-local-state/`; write one new durable report at
`docs/qa/reports/2026-08-24-agent-model-routing-local-state.md` and update only verdict fields
supported by observed evidence.

Limitations: adoption is local and deterministic; no networked external-skill installer is
authorized. No browser, API, mobile, auth, server, production health path, or live-model harness
exists. End before product remediation; any confirmed defect returns to an Implementer and requires
a fresh Verifier after the fix.
