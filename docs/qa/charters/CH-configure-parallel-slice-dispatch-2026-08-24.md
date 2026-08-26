# CH-configure-parallel-slice-dispatch-2026-08-24

- **Date:** 2026-08-24
- **Time-box:** 30 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-configure-feature-workflow`](../journeys/J-configure-feature-workflow.md)
- **Tour:** Parallelization defaults, planning, failure, and preservation tour
- **Public entry point:** `.my-workflow.toml` → `workflow_config.py` → `parallel_plan.py`
- **Adapter candidate:** CLI/manual through the commands documented by the `workflow-config` and autonomous skills
- **Scenarios:** `CFG-freeze-feature-workflow`, `CFG-plan-parallel-slice-dispatch`
- **Adjacent canary:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md) confirms adoption carries the planner and policy without changing consumer configuration.

## Mission

Use a checkout-local disposable Git repository to configure and freeze each dispatch mode, then
plan representative versioned task states through the public CLI. Inspect the installed
agent-facing policy to confirm unsafe or unsupported concurrency returns to the serial workflow
without removing any delivery stage.

## Expected observable

The adopter sees `disabled` by default, exact supported-mode persistence, stable resume, deterministic
ready/blocked/checkpoint output, decisive serial fallback, and an orchestration contract that keeps
tasks sequential and every gate, Verifier, deep-review group, final QA, and final-tree gate intact.

## Planned probes

- Resolve with no `[parallelization]`, then with `disabled`, `safe`, and `full`; compare stdout with the reloaded snapshot.
- Reject one unsupported mode while preserving the prior valid snapshot; resume after config and HEAD changes without refresh.
- Plan independent slices, verified safe dependencies, completed full-mode checkpoints, and a waiting task that becomes `follow_up` only after its dependency completes.
- Repeat one unchanged plan and compare stdout bytes.
- Exercise incomplete dependencies, ambiguous metadata, a cycle, and a ready write collision; inspect exact blocked or serial-fallback reasons.
- Inspect policy ordering for clean turn end, event-only follow-up, checkpoint sync before consumption, affected-gate rerun, evidence invalidation, and conditional final reconciliation.
- Adjacent canary: adopt into a disposable target and confirm the planner/policy arrive while target-owned `.my-workflow.toml` stays unchanged.

End before product remediation. A confirmed defect returns to an Implementer.

## Terminal outcome

The resolver/planner tour passed in the 2026-08-24 report. R18/R19 add the executor-facing
zero-effect fallback evidence; the configured consumer resource-provider path remains unavailable
in this repository. The adjacent provider-free fallback is therefore the authoritative current
configuration boundary. See the [terminal report](../reports/2026-08-25-parallel-slice-executor-final.md).
