# J-execute-parallel-slices

**Persona:** Workflow operator
**Goal:** Advance eligible slices concurrently without weakening the sequential TLC workflow.
**Entry point:** `.my-workflow.toml` → `parallel_execute.py start|status|resume`

## Flow

1. Resolve a feature with a supported parallelization mode and inspect the frozen provider choice.
2. Preflight a disposable safe-mode fixture with exactly two ready `Resources: none` slices.
3. Start through `--adapter auto`; require a proven Orca capability or an explicit zero-effect serial fallback.
4. Observe distinct worktree, branch, dispatch, and terminal receipts for both active lanes.
5. Resume through correlated events until both workers have terminal read-before-ack-before-release receipts.
6. Run the lifecycle oracle, then clean only the attested fixture, workers, and worktrees.
7. Inspect status and Git residue to confirm no owned checkout or worker remains.

## Promises

- [`QAS-run-resource-free-parallel-orca-slices`](../scenarios/QAS-run-resource-free-parallel-orca-slices.md)
- [`QAS-clean-owned-parallel-slice-pilot`](../scenarios/QAS-clean-owned-parallel-slice-pilot.md)
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
