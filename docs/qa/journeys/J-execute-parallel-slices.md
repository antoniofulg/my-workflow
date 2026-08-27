# J-execute-parallel-slices

**Persona:** Workflow operator
**Goal:** Advance eligible slices concurrently without weakening the sequential TLC workflow.
**Entry point:** `.my-workflow.toml` → `parallel_execute.py preflight|start|status|resume`, or the
explicitly authorized direct Orca path in `.agents/skills/autonomous/references/parallelization.md`

## Flow

1. Resolve a feature with a supported parallelization mode and inspect the frozen provider choice.
2. Run read-only host preflight. In Maestri, evaluate only Maestri; outside Maestri, evaluate the requested host without cross-fallback.
3. Require a compatible identity-matched host proof before effects. Installed Orca `1.4.188`, current Maestri, and any unproven candidate return explicit zero-effect serial fallback.
4. Only after compatibility, preflight a disposable safe-mode fixture with exactly two ready `Resources: none` slices.
5. Observe distinct worktree, branch, dispatch, and terminal receipts for both active lanes.
6. Resume through correlated events until both workers have terminal read-before-ack-before-release receipts.
7. Run the lifecycle oracle, then clean only the attested fixture, workers, and worktrees.
8. Inspect status and Git residue to confirm no owned checkout or worker remains.

## Assisted flow

1. Require explicit human authorization while automatic Orca remains unsupported; inspect the
   frozen implementer route in the feature `workflow.json`.
2. Create one direct Orca worktree per ready slice, record and inspect its exact
   `startupTerminal.handle`, prove that it is new, uniquely owned, unused, and free of agent/default
   task activity, then promote that same handle with the shell-quoted frozen command. Wait for
   `tui-idle`, read `source=screen`, and accept the worker only when provider/model/effort match.
3. After `A:T1` completes and verifies, start B once. Let B complete its sequential ready work and
   park at `B:T12 depends_on A:T7` with the exact clean checkpoint comment, then end without polling.
4. After `A:T7` completes and verifies, synchronize its exact producer commit into B, rerun B's
   affected gate, and follow up the same terminal or its sole reacquired handle.
5. Integrate verified slice commits in deterministic order while preserving task commits, scoped
   gates, per-slice Technical Verification, frozen review cadence, final QA, and the final full gate.
6. Revalidate immutable ownership separately from mutable head/handle state; stop exact workers,
   remove only clean integrated owned worktrees, safely delete exact owned branches, and prove
   worktree, path, branch-ref, and terminal absence.

## Promises

- [`QAS-run-resource-free-parallel-orca-slices`](../scenarios/QAS-run-resource-free-parallel-orca-slices.md)
- [`QAS-clean-owned-parallel-slice-pilot`](../scenarios/QAS-clean-owned-parallel-slice-pilot.md)
- [`CFG-fallback-unproven-parallel-execution`](../scenarios/CFG-fallback-unproven-parallel-execution.md)
- [`QAS-qualify-orca-host-before-parallel-use`](../scenarios/QAS-qualify-orca-host-before-parallel-use.md)
- [`QAS-reject-unverifiable-maestri-host`](../scenarios/QAS-reject-unverifiable-maestri-host.md)
- [`QAS-bound-verifier-remediation-per-blocker`](../scenarios/QAS-bound-verifier-remediation-per-blocker.md)
- [`QAS-coordinate-assisted-orca-slices`](../scenarios/QAS-coordinate-assisted-orca-slices.md)

## Adjacent canary

Walk [`J-configure-feature-workflow`](J-configure-feature-workflow.md), especially
[`CFG-plan-parallel-slice-dispatch`](../scenarios/CFG-plan-parallel-slice-dispatch.md), to confirm
disabled or unsupported execution produces a serial plan with zero worktree, worker, Git, event, or
resource effects while tasks and delivery stages remain unchanged.

## Terminal QA status

Read-only QA on 2026-08-26 confirmed installed Orca `1.4.188` and unavailable Maestri remain
unsupported with zero effects. `QAS-reject-unverifiable-maestri-host` is `pass`.
`QAS-qualify-orca-host-before-parallel-use` remains `untested` overall because its installed-runtime
leg passed but a candidate canary is deferred until a later packet supplies an updated runtime and
explicit authorization.

Fresh fix-loop QA at `cd1886f` re-passed both read-only host-rejection legs and the adjacent bounded
Deep Review canary. Candidate Orca qualification remains `untested`; no candidate or canary ran.

The current QA packet contains no durable candidate-canary evidence for a later Orca version, so no
automatic compatibility result is inferred from an installed version. This observation does not
exercise the separate assisted flow. The 2026-08-26 assisted E2E-001 walk is retained as a
historical pre-remediation record: two clean out-of-contract `terminal create` attempts timed out
without returning an agent handle. Exact setup cleanup left zero slice residue. See the
[`assisted Orca report`](../reports/2026-08-26-assisted-orca-slices.md) and
[`BUG-20260826-assisted-orca-terminal-create-timeout`](../bugs/BUG-20260826-assisted-orca-terminal-create-timeout.md).

[`QAS-run-resource-free-parallel-orca-slices`](../scenarios/QAS-run-resource-free-parallel-orca-slices.md)
and [`QAS-clean-owned-parallel-slice-pilot`](../scenarios/QAS-clean-owned-parallel-slice-pilot.md)
are `blocked-verify` at the external Orca/Codex recovery boundary. R14's user-takeover residue,
R15/R17's live owned terminal, and the older R8–R11 `identity_unproven` residue were later removed
manually by the operator; that is not automatic cleanup evidence. A fresh v0.6.0 safe-mode run then
reproduced `agent_prompt_stalled` with its exact A/T1 terminal still live/writable and B/T2 absent.
The new fixture remains preserved, so no cleanup or zero-residue claim is made. See the
[v0.6.0 safe retest](../reports/2026-08-25-parallel-slice-executor-v060-safe-retest.md).
