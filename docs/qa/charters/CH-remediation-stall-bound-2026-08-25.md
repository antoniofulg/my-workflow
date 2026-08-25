# CH-remediation-stall-bound-2026-08-25

- **Date:** 2026-08-25
- **Scope:** `origin/main..cada159` on `fix/stall-based-remediation-halt`
- **Time-box:** 30 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-configure-feature-workflow`](../journeys/J-configure-feature-workflow.md)
- **Tour:** Default, boundary, live-resume, invalid-input, and adoption-canary tour
- **Public entry point:** `.my-workflow.toml.example` -> local `.my-workflow.toml` -> `workflow-config` resolver CLI
- **Adapter candidate:** CLI/manual through the public resolver command declared in [`docs/qa/README.md`](../README.md)
- **Scenarios:** `CFG-resolve-deep-review-cadence`, `CFG-freeze-feature-workflow`; `ADP-adopt-workflow-safely` (retained adjacent canary)

## Mission

Use a checkout-local disposable Git repository to experience the remediation stall bound through
the documented resolver CLI. Prove its accepted values, current JSON output, snapshot exclusion, and
live resume behavior through independent TOML and JSON reads. Keep adoption as a narrow canary for
the changed tracked example; do not reset its retained verdict unless observation invalidates it.

## Expected observable

The adopter can set a nonnegative integer stall bound, sees default `3` and explicit `0` in current
CLI JSON, receives precise rejection for invalid values before feature state is written, and can
change the bound between resumes without changing frozen route, cadence, or snapshot bytes.

## Criterion disposition ledger

| Requirement | Disposition | Canonical QA coverage |
| --- | --- | --- |
| `SRH-01` | Public configuration and CLI promise | `J-configure-feature-workflow` -> `CFG-resolve-deep-review-cadence` |
| `SRH-02` | Public CLI output and snapshot-boundary promise | `J-configure-feature-workflow` -> `CFG-freeze-feature-workflow` |
| `SRH-03` | Internal agent-loop policy: scoped-gate normalization and minimum-set accounting have no executable public adapter in the project profile | Technical validation only; no QA scenario reset |
| `SRH-04` | Internal agent-loop policy: autonomous halt-report construction has no live-model execution harness | Technical validation only; no QA scenario reset |
| `SRH-05` | Internal orchestration safety: unavailable-gate and review-cap behavior are not exposed by the resolver CLI | Technical validation only; no QA scenario reset |

## Planned probes

- Copy the active checkout into a checkout-owned disposable Git repository and initialize local
  config from `.my-workflow.toml.example`.
- Resolve a disposable feature with the documented resolver command. Independently parse stdout and
  `.specs/features/<slug>/workflow.json`; require `remediation.stall_attempts: 3` only in stdout.
- Repeat with positive `5` and zero `0`; require exact JSON values and no persisted remediation key.
- Try negative, boolean, TOML float, string, and unknown remediation-key inputs against fresh feature
  slugs; require nonzero exit, a remediation-specific diagnostic, and no snapshot creation.
- Resolve with one threshold, hash the snapshot, edit only `stall_attempts`, and resume without
  `--refresh`; require the changed live value, unchanged route/cadence, and byte-identical snapshot.
- Reconfirm one balanced cadence result as a same-resolver canary.
- Adjacent adoption canary: use `scripts/adopt.py` against a separate checkout-local disposable
  target and confirm its tracked example contains the remediation table while a pre-existing
  consumer-owned `.my-workflow.toml` remains byte-identical on re-adoption.
- Remove only checkout-owned disposable targets. Source residue must be limited to planned durable
  QA records and ignored raw evidence.

## QA Execute handoff

Start a fresh Verifier session with `phase: qa-execute`. Read `docs/qa/README.md`, invoke canonical
`qa-execute`, and use its declared CLI/manual adapter at HEAD `cada159`. Exact resolver path:
`.agents/skills/workflow-config/scripts/workflow_config.py`; use the feature-resolution and resume
form documented by `.agents/skills/workflow-config/SKILL.md` inside a checkout-local disposable Git
repository:

```bash
python3 .agents/skills/workflow-config/scripts/workflow_config.py \
  --root . --feature remediation-stall-qa --slices 1 --native-provider codex
```

Run the same command after changing only `[remediation].stall_attempts` to exercise resume. Use
`python3 scripts/adopt.py <separate-disposable-target>` only for the adoption canary. Store raw
evidence under
`docs/qa/evidence/2026-08-25-remediation-stall-bound/`, write a new durable report at
`docs/qa/reports/2026-08-25-remediation-stall-bound.md`, then update only scenario verdict fields
supported by observed public-interface evidence.

Limitation: the profile has no live-model or agent-execution harness. Do not claim QA execution of
`SRH-03`, `SRH-04`, or `SRH-05` from documentation inspection or structural tests; retain their
technical-validation disposition. This repository has no browser, API, mobile, auth, server, or
production-health surface. Do not install tools, contact remote services, or run the networked
external-security installer.

End before product remediation. A confirmed product defect returns to an Implementer and requires a
fresh Verifier after the fix.
