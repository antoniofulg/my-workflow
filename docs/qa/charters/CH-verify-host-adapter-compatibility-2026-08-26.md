# CH-verify-host-adapter-compatibility-2026-08-26

- **Date:** 2026-08-26
- **Time-box:** 35 minutes
- **Persona:** Workflow operator
- **Journey:** [`J-configure-feature-workflow`](../journeys/J-configure-feature-workflow.md) → [`J-execute-parallel-slices`](../journeys/J-execute-parallel-slices.md)
- **Tour:** Host selection, read-only compatibility, and zero-effect fallback
- **Public entry point:** `parallel_plan.py` → `parallel_execute.py preflight|start|resume|status --adapter auto|orca|maestri`
- **Declared adapter:** Checkout-local CLI/manual using public planner and executor JSON; installed Orca `1.4.188` and current Maestri CLI
- **Scenarios:** `CFG-plan-parallel-slice-dispatch`, `CFG-fallback-unproven-parallel-execution`, `QAS-qualify-orca-host-before-parallel-use`, `QAS-reject-unverifiable-maestri-host`
- **Adjacent canary:** `QAS-run-resource-free-parallel-orca-slices` by read-only status and policy inspection only

## Mission

Confirm that the public executor selects only the current requested host, reports installed Orca
`1.4.188` and current Maestri as unsupported, and reaches serial fallback before any host or Git
effect while schema-v2 planning and all existing delivery stages remain intact.

## Expected observable

Each preflight emits one structured JSON object with the selected backend, status, decisive reason,
runtime/proof fields, and missing capabilities where applicable. Disabled `start`/`resume` skips host
selection, explicit diagnostic preflight remains read-only, obsolete workflow schema v1 is rejected,
and incompatible selection leaves Run, Task, worker, floor, agent, terminal, worktree, runtime-state,
and compatibility-cache deltas at zero.

## Planned probes

- In a checkout-local disposable Git fixture, compare schema-v2 planning with an obsolete schema-v1 copy and require rejection before host effects.
- Run disabled `start` and `resume`; independently inspect that no adapter probe, runtime state, compatibility cache, or host/Git object appeared.
- Run explicit and automatic read-only Orca preflight against installed `1.4.188`; require `unsupported`, the known-incompatible reason, and zero Run/Task/worker/worktree delta.
- Run explicit Maestri preflight and `auto` from a Maestri terminal context; require Maestri-only evaluation, an unsupported missing/unimplemented contract, and zero floor/agent/Git-worktree delta.
- Inspect the installed parallelization policy and planner output for unchanged scheduler, checkpoint, Technical Verifier, deep-review, gate, QA, and serial-fallback stages.
- Inspect emitted and local compatibility data for credential-shaped values; only redaction markers may appear.
- Re-read public status and Git/host inventories from an independent process; record exact commands, disposable root, result JSON, and before/after residue in checkout-local evidence.

Do not run `preflight --canary`. Installed Orca `1.4.188` is known incompatible, and no candidate
runtime is authorized for this cycle. Do not launch a real two-slice worker journey, create or delete
a Maestri floor, recruit or dismiss an agent, or treat a capability claim as compatibility.

## Criterion disposition

- `HST-01` — public CLI: `CFG-plan-parallel-slice-dispatch` and `CFG-fallback-unproven-parallel-execution`.
- `HST-02`, `HST-03` — public CLI: `CFG-fallback-unproven-parallel-execution` and `QAS-reject-unverifiable-maestri-host`.
- `HST-04` — public installed policy with unchanged execution semantics: `CFG-plan-parallel-slice-dispatch` adjacent canary.
- `ORC-01`, `ORC-02`, `ORC-06`, `ORC-07` — public CLI: `QAS-qualify-orca-host-before-parallel-use`; current cycle walks the installed known-bad and cache-rejection surface.
- `ORC-03` through `ORC-05` — public CLI: `QAS-qualify-orca-host-before-parallel-use`; live execution waits for a later candidate Orca packet.
- `MAE-01` through `MAE-04` — public CLI and installed policy: `QAS-reject-unverifiable-maestri-host`.
- `SEC-001` — public CLI consequence: `CFG-fallback-unproven-parallel-execution`.
- `SEC-005` — public CLI diagnostics: `QAS-qualify-orca-host-before-parallel-use`.
- `SEC-006` — public CLI canary outcome: `QAS-qualify-orca-host-before-parallel-use`; positive cleanup proof waits for a candidate runtime.
- `SEC-002`, `SEC-003`, `SEC-004`, and `SEC-007` — internal implementation controls already covered by technical verification. QA observes only their public cache invalidation, structured-result, fixed-host, retained-ID, and zero-effect consequences in the mapped scenarios.

## QA Execute handoff

Fresh Verifier must invoke canonical `qa-execute`, read `docs/qa/README.md`, and use its existing
CLI/manual adapter in one checkout-local disposable Git repository. Execute only the schema,
disabled-mode, installed Orca `1.4.188`, current Maestri, unchanged-policy, redaction, and independent
residue probes above. Save disposable evidence below
`docs/qa/evidence/2026-08-26-host-adapter-compatibility/`, write a new durable report under
`docs/qa/reports/`, and update the four listed scenario statuses from observed results.

Limitation: do not invoke `--canary`; therefore the candidate Orca success/cleanup leg remains
`untested` unless a separate future packet supplies a candidate version and authorization. Preserve
the existing `blocked-verify` states for real two-slice Orca execution and completed-pilot cleanup.
