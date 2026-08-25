# QA report — parallel slice executor R19 provider preflight and convergence

- **Date:** 2026-08-25
- **Scope:** fresh resource-bearing fallback canary after the R18 fix, deterministic replay, residue
  check, and public fingerprint convergence ledger walk
- **Adapter:** CLI/manual through public `qa_parallel_pilot.py`, `parallel_plan.py`,
  `parallel_execute.py`, `review_convergence.py`, and read-only Git/Orca inspection
- **Environment:** checkout `/Users/antoniofulg/orca/workspaces/my-workflow/feat-parallel-slice-executor`,
  HEAD `cdfa6c0`; product implementation `0ed8b55`; Orca executable discoverable at
  `/usr/local/bin/orca`
- **Preflight gate:** `rtk npm run test:all` — exit `0`; 9 Vitest files / 110 tests and all
  discovered Python suites passed
- **Raw evidence:** `docs/qa/evidence/2026-08-25-parallel-slice-executor-r19/`
- **Limitation:** this repository has no configured runtime, port, database, or resource provider;
  no isolation claim is made. The real resource-free worker lifecycle and historical retained
  fixtures were not touched.

## Matrix

| Leg | Scenario | Verdict | Observable | Evidence |
| --- | --- | --- | --- | --- |
| Missing provider, resource-free-first ordering | `CFG-fallback-unproven-parallel-execution` | **pass** | Two ready runtime-bearing lanes returned `missing-resource-provider` twice with `actions: []`; fresh status was `state: null`; no worktree, adapter, lease, action, runtime, Run, Task, Dispatch, terminal, or worker effect appeared | `resource-plan.json`; `resource-start.json`; `resource-status.json`; `resource-effects.json`; `resource-residue.json` |
| Fingerprint convergence | `QAS-bound-verifier-remediation-per-blocker` | **pass** | Checkout ledger stayed at 21 closed fingerprints, `open=0`, max count 2; two closed-fingerprint replays did not increment; disposable ledger halted a distinct fingerprint exactly at failed remediation 3, with no later increment | `convergence-replays.json`; `convergence-threshold.json`; `ledger-bounds.json` |
| Disabled and unsupported-adapter adjacent legs | `CFG-fallback-unproven-parallel-execution` | pass (R18 retained) | R18 already proved both zero-effect legs; R19 did not repeat an unaffected adapter mutation | `../2026-08-25-parallel-slice-executor-r18/disabled-effects.json`; `../2026-08-25-parallel-slice-executor-r18/unsupported-effects.json` |
| Resource-free Orca worker lifecycle | `QAS-run-resource-free-parallel-orca-slices` | fail (existing; not rerun) | Prior fresh worker-start defect remains open; R19 stopped at scoped fallback/convergence and did not create workers or touch retained fixtures | prior R12/R18 reports and linked bug |
| Owned completed cleanup | `QAS-clean-owned-parallel-slice-pilot` | untested (not rerun) | No completed lifecycle existed in R19; diagnostic cleanup of the effect-free fixture removed only its source and left no residual paths | `resource-residue.json` |
| Planner policy adjacent walk | `CFG-plan-parallel-slice-dispatch` | untested (partial projection only) | The resource plan was read and deterministic, but the full policy/stage walk was outside this retest | `resource-plan.json` |

## Resource-provider canary

Fresh setup created a disposable safe-mode fixture with source head
`519c72a2a02ee44d0b3a8369d3c5201905c5da31`. Both pending lanes were changed inside that fixture
only to `Resources: runtime`; the frozen provider stayed `null`. The public planner returned two
ready lanes without fallback.

The first mutating public command was `parallel_execute.py start --adapter auto`. It returned
serial fallback reason `missing-resource-provider` and an empty action list. A fresh-process
`status` returned `state: null`. A second start/status replay returned the identical result.
The repeat baseline/post read-only inventory stayed at 12 Orca Runs with the same 7 pilot Run ids
and 151 workers. Git showed only the source fixture worktree; no derived A/T1 or B/T2 worktree
appeared. No fixture runtime-state receipt matched the root. With no Run or worker action, no Task,
Dispatch, terminal, or lease effect was present; the provider preflight therefore won before
adapter construction or lane mutation.

Diagnostic abort was used only after the public status was independently `state: null`. It
removed the exact disposable source, returned `residual_paths: []`, and a repeat returned
idempotent `residual_paths: []`. The cleanup tombstone is expected idempotency evidence; no
historical fixture, source checkout, or unrelated sibling was touched.

## Fingerprint convergence

The checkout ledger was read before and after the walk, not mutated: 21 total, 21 `closed`, 0
`open`, 0 `halted`, maximum failed-remediation count 2. A disposable copy seeded two existing
closed fingerprints. Public successful replay with `--gate-passed` preserved counts 1 and 2,
proving independent closed-fingerprint counters do not increment on successful remediation/replay.

A third disposable fingerprint walked failures 1 and 2 (`open`), a successful replay at count 2,
the third failed remediation (`halted`, count 3), then a fourth failure and successful replay,
both remaining at count 3/`halted`. The checkout ledger remained unchanged and `open=0`.

## Counts and stop boundary

- Gate: `rtk npm run test:all` — exit `0`; 9 Vitest files / 110 tests; all discovered Python
  suites passed.
- Resource canary: 1 setup, 1 plan, 2 starts, 2 fresh-process statuses; 0 new lane worktrees,
  0 runtime receipts, 0 Orca Runs/Tasks/Dispatches/terminals/workers/leases.
- Repeat inventory: Orca Runs `12 -> 12`; worker count `151 -> 151`; same 7 pilot Run ids.
- Cleanup: 2 diagnostic-abort calls; 0 residual paths; second call idempotent.
- Convergence: 2 successful closed-fingerprint replays; 1 disposable threshold sequence; checkout
  ledger unchanged at 21 closed / 0 open / 0 halted.
- Disabled/unsupported canaries: 0 R19 calls; R18 zero-effect evidence retained.
- Worker lifecycle, resume, lifecycle-check, normal cleanup, or targeted historical-fixture
  commands: 0 calls; aggregate Orca/Git inventories were read-only.
- Product, test, spec-validation, commit, push, and merge changes: 0.

**Verdict: PASS for R19's fixed resource-provider preflight and convergence scope. The existing
resource-free worker-start defect remains open and was not re-run or conflated with this pass.**
