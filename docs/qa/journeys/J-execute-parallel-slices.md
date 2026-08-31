# J-execute-parallel-slices

**Persona:** Workflow operator
**Goal:** Advance eligible slices through the assisted workflow while preserving independent proof and safe serial fallback.
**Entry point:** `.my-workflow.toml` → `parallel_execute.py start|status|resume` → `orca_assisted_probe.py dispatch|inspect|cleanup`

## Flow

1. Resolve a v3 feature with default `assisted` mode and inspect the frozen provider and worker cap.
2. Plan ready, blocked, conflicting, and serial cases; require worktrees only for compatible concurrent writers.
3. When a gate declares a shared heavy resource, wrap only that command with `resource_lock.py` at
   project scope by default or machine scope explicitly; leave unrelated resources concurrent.
4. Exercise the public executor and assisted probe with checkout-local fake providers; persist the packet and transport only its pointer.
5. Observe correlated worktree, branch, operation, terminal, checkpoint, and lease receipts without packet bodies or absolute home paths.
6. Reconcile transient responses through bounded read-only inspections and confirm one physical mutation per logical operation.
7. Run cleanup only after ownership and lifecycle proof, then independently confirm zero owned residue and an unrelated canary remains.
8. Keep the separate real Orca/Codex lifecycle and completed-pilot cleanup legs `blocked-verify` until upstream support is verified.

## Promises

- [`QAS-run-resource-free-parallel-orca-slices`](../scenarios/QAS-run-resource-free-parallel-orca-slices.md)
- [`QAS-clean-owned-parallel-slice-pilot`](../scenarios/QAS-clean-owned-parallel-slice-pilot.md)
- [`QAS-coordinate-assisted-slices-offline`](../scenarios/QAS-coordinate-assisted-slices-offline.md)
- [`QAS-serialize-heavy-test-resources`](../scenarios/QAS-serialize-heavy-test-resources.md)
- [`CFG-fallback-unproven-parallel-execution`](../scenarios/CFG-fallback-unproven-parallel-execution.md)
- [`QAS-bound-verifier-remediation-per-blocker`](../scenarios/QAS-bound-verifier-remediation-per-blocker.md)

## Adjacent canary

Walk [`J-configure-feature-workflow`](J-configure-feature-workflow.md), especially
[`CFG-plan-parallel-slice-dispatch`](../scenarios/CFG-plan-parallel-slice-dispatch.md), to confirm
disabled or unsupported execution produces a serial plan with zero worktree, worker, Git, event, or
resource effects while tasks and delivery stages remain unchanged.

## Terminal QA status

[`QAS-run-resource-free-parallel-orca-slices`](../scenarios/QAS-run-resource-free-parallel-orca-slices.md)
and [`QAS-clean-owned-parallel-slice-pilot`](../scenarios/QAS-clean-owned-parallel-slice-pilot.md)
are `blocked-verify` at the external Orca/Codex recovery boundary. R14's user-takeover residue,
R15/R17's live owned terminal, and the older R8–R11 `identity_unproven` residue were later removed
manually by the operator; that is not automatic cleanup evidence. A fresh v0.6.0 safe-mode run then
reproduced `agent_prompt_stalled` with its exact A/T1 terminal still live/writable and B/T2 absent.
The new fixture remains preserved, so no cleanup or zero-residue claim is made. See the
[v0.6.0 safe retest](../reports/2026-08-25-parallel-slice-executor-v060-safe-retest.md).
