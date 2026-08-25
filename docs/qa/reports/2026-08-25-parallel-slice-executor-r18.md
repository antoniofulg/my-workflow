# QA report — parallel slice executor R18 non-worker fallback canaries

- **Date:** 2026-08-25
- **Scope:** disabled, unsupported-adapter, and missing-resource-provider serial canaries; fingerprint convergence was planned but not reached
- **Adapter:** CLI/manual through public `parallel_plan.py`, public `parallel_execute.py`, disposable `qa_parallel_pilot.py setup`, and read-only Git/Orca inspection
- **Environment:** checkout `/Users/antoniofulg/orca/workspaces/my-workflow/feat-parallel-slice-executor`, HEAD `6fba686a4f66698dd9bd35c81454fca2c59389be`; product implementation `a736757`; Orca `1.4.188` advertising `orchestration.contract.v1`
- **Preflight gate:** `rtk npm run test:all` — exit `0`; 9 Vitest files / 110 tests and all discovered Python suites passed
- **Raw evidence:** `docs/qa/evidence/2026-08-25-parallel-slice-executor-r18/`
- **Limitation:** this repository has no configured runtime, port, or database provider; no isolation claim is made. The real two-lane worker journey and historical retained fixtures were not touched.

## Matrix

| Leg | Scenario | Verdict | Observable | Evidence |
| --- | --- | --- | --- |
| Disabled mode | `CFG-fallback-unproven-parallel-execution` | pass (leg) | `start` returned `disabled-mode` with empty actions; fresh `status` had no state; fixture lane-worktree count and Orca Run inventory were unchanged | `disabled-start.json`; `disabled-status.json`; `disabled-effects.json` |
| Unsupported/unproven adapter | `CFG-fallback-unproven-parallel-execution` | pass (leg) | with `PATH=/usr/bin:/bin`, `command -v orca` returned no path; the valid two-lane plan returned `unsupported-adapter` with empty actions and no state/effects | `unsupported-plan.json`; `unsupported-start.json`; `unsupported-status.json`; `unsupported-effects.json` |
| Resource-bearing lane without provider | `CFG-fallback-unproven-parallel-execution` | **fail** | `start` returned `missing-resource-provider`, but accepted A/T1 worktree and persisted runtime state before returning serial; no Run/Task/Dispatch/terminal/lease appeared | `resource-plan.json`; `resource-start.json`; `resource-status.json`; `resource-effects.json`; `BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree` |
| Fingerprint convergence | `QAS-bound-verifier-remediation-per-blocker` | untested | session stopped at the first product defect; no convergence ledger command ran | none; stop at resource canary |
| Planner adjacent canary | `CFG-plan-parallel-slice-dispatch` | untested | only the resource canary's two-lane plan projection ran; the full planner/policy walk was not claimed | `unsupported-plan.json`; `resource-plan.json` |

## Disabled and unsupported legs

The fresh fixture source worktree was the only fixture path before the fallback calls. Disabled mode
returned exactly one serial lane (`reason: disabled-mode`); unsupported mode received a valid plan
with exactly two ready resource-free lanes, then returned `reason: unsupported-adapter` after the
hidden-`orca` capability probe. Both fresh `status` calls came from separate processes and reported
`state: null`. No lane worktree was added, no runtime state receipt was written, and the read-only
Orca Run inventory remained 12 total with the same seven historical `parallel-slice:parallel-pilot`
Run ids.

## Resource-provider defect and stop

The fresh disposable fixture's frozen snapshot retained `parallelization.resource_provider: null`.
Both tasks were given explicit `Resources: runtime`; the public planner returned two ready lanes with
that resource. The first mutating command was the public executor `start --adapter auto`. It exited
`0` with `fallback: true`, `reason: missing-resource-provider`, and `actions: []`. A fresh-process
`status` independently showed lane A serial with fallback reason `missing-resource-provider`, but
also showed an accepted Git worktree action for A/T1 and persisted runtime state. Read-only Git and
Orca checks found two matching worktrees (fixture source plus A/T1), no new Orca Run, no pilot Task,
Dispatch, terminal, or resource lease, and an unchanged 12-Run inventory.

This violates the scenario's zero-effect fallback promise. It is linked to the existing open
`BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree`; the smallest remediation is
to preflight the provider before creating any lane worktree and then retest this exact path. Per the
QA fix loop, this session ended immediately. The fresh fixture and A/T1 worktree are retained for
the Implementer; no cleanup or broad reset was attempted.

## Counts and command record

- `rtk npm run test:all`: exit `0`; 9 Vitest files / 110 tests; all discovered Python suites passed.
- `rtk python3 tools/qa_parallel_pilot.py setup`: 1 fresh source fixture created; no workers started.
- Disabled: 1 public `start` + 1 fresh `status`; 0 new lane worktrees; 0 runtime state files; 0 new Runs/Tasks/Dispatches/terminals.
- Unsupported: 1 public `parallel_plan` + 1 hidden-capability `start` + 1 fresh `status`; 0 new lane worktrees; 0 runtime state files; 0 new Runs/Tasks/Dispatches/terminals.
- Resource-bearing/no provider: 1 public `parallel_plan` + 1 public `start` + 1 fresh `status`; 1 accepted A/T1 lane worktree; 1 persisted runtime state; 0 new Orca Runs/Tasks/Dispatches/terminals/leases.
- Fingerprint convergence: 0 calls; not reached.
- Worker-start/lifecycle/cleanup interfaces: 0 calls; blocked real two-lane and historical fixtures untouched.
- Historical fixture mutations: 0. Product, test, and spec-validation files: 0. Commits/pushes/merges: 0.

**Verdict: FAIL at the resource-provider fallback canary; stop before convergence.**
