# QA report — parallel slice executor R12 fresh real Orca lifecycle

- **Date:** 2026-08-25
- **Scope:** R11 fresh-residue diagnostic abort, then a new current-HEAD two-lane Orca journey and serial/fingerprint canaries
- **Adapter:** CLI/manual through `qa_parallel_pilot.py`, public `parallel_execute.py`, and real local Orca `orchestration.contract.v1`
- **Environment:** checkout `/Users/antoniofulg/orca/workspaces/my-workflow/feat-parallel-slice-executor`, checkout HEAD `84ef849` (product implementation `f02b679`); Orca `1.4.188`
- **Preflight gate:** `rtk npm run test:all` — pass; Vitest and all discovered Python suites passed
- **Raw evidence:** `docs/qa/evidence/2026-08-25-parallel-slice-executor-r12/`
- **Limitation:** this repository has no runtime, port, database, or configured resource provider; no such isolation claim is made

## Matrix

| Leg | Scenario | Verdict | Observable | Evidence |
| --- | --- | --- | --- | --- |
| R11 fresh residue diagnostic | out-of-cycle residue check | recorded-safe | Safe public diagnostic abort removed the R11 source/worktree with no residual paths; external Run remained separate and untouched | `r11-abort.json`; `r11-postcheck.md` |
| Fresh real Orca lifecycle | `QAS-run-resource-free-parallel-orca-slices` | fail | `start --adapter auto` fell back at `selector_not_found` during worktree discovery after accepting only A/T1; canonical Run/Task exist, but B, workers, terminals, and lifecycle receipts do not | `start.json`; `status-after-start.json`; `orca-run.json`; `orca-tasks.json`; `orca-workers.json` |
| Fresh owned cleanup | `QAS-clean-owned-parallel-slice-pilot` | untested | Stopped at the first fresh product defect; public diagnostic abort correctly refused accepted partial state, so lifecycle authorization and normal/repeated cleanup were not reached | `abort-incomplete.json`; `residue.md` |
| Serial fallback canaries | `CFG-fallback-unproven-parallel-execution`; `CFG-plan-parallel-slice-dispatch` | untested | Stopped before disabled/unsupported/provider-absent canaries | `start.json` |
| Fingerprint convergence | `QAS-bound-verifier-remediation-per-blocker` | untested | Stopped before the fingerprint walk | `start.json` |

## R11 residue separation

The older external `identity_unproven` fixture was not touched. R11’s separate fresh residue was
`parallel-slice-pilot-5spz2fp5`: one accepted A-T1 worktree, Orca Run `run_658585e3a862`, and no
Task, worker, or terminal. The public abort preconditions were safe because the executor state had
no accepted/released worker effect or partial Run/Task/Dispatch IDs, and independent Orca reads
returned zero Tasks, workers, and terminals. Public `cleanup --abort-incomplete` returned
`aborted: true`, `cleaned: false`, and `residual_paths: []`. The source/worktree are gone; the
external Run remains as separate residue and was not manually reset.

The remainder of this report records only the new R12 fixture. It must not be conflated with the
older retained fixture or the R11 external Run.

## R12 fresh walk and first defect

Setup returned `/private/var/folders/lc/_v1mn5h560d2tsmz474y7d1c0000gn/T/parallel-slice-pilot-fa298dih`.
Dry-run returned `validated: true`, `mode: safe`, equal source/repository fixture HEAD
`a69a10716710f6fcec82edc1b1fa276eab570a28`, and exactly two ready `Resources: none` lanes.

The first mutating fresh command was public `start --adapter auto`. It exited `0` but returned
`fallback: true`, `reason: worker-failed`, with `selector_not_found` after three worktree-discovery
attempts. Before that failure, the executor accepted A/T1’s detached worktree and canonical Orca
Run `run_eaaa364b0f83` plus Task `task_0075163a8c51`; B/T2 never started. Independent reads confirm
one `ready` Task, zero workers/terminals, no Dispatch, and no lifecycle receipts. The top-level
Orca response UUIDs are not used as Run/Task identities.

Per the stop rule, no `resume`, `worker_done` read/ack, release, lifecycle-check, normal cleanup,
repeat cleanup, fallback canary, resource-provider canary, convergence walk, or manual cleanup ran
after the defect. Public diagnostic abort refused with `worker-may-be-live` because the persisted
partial effect contains canonical Run/Task IDs; the R12 source/worktree and external Run/Task remain
retained for an Implementer.

## Counts and changed QA paths

- Gate: `rtk npm run test:all` — exit `0`; 9 Vitest files / 110 tests and all discovered Python suites passed.
- R11 diagnostic cleanup: 1 public abort; source/worktree removed; 0 residual paths; external Run retained.
- R12 fresh mutation: 1 public `start`; 1 accepted A/T1 worktree; 1 canonical Run; 1 canonical Task; 0 workers; 0 terminals; 0 Dispatches; 0 B/T2 lane; 0 lifecycle receipts.
- R12 diagnostic cleanup: 1 public abort attempt; exit `1`; fail-closed `worker-may-be-live`; fresh fixture retained.
- Changed QA paths: this report plus `docs/qa/evidence/2026-08-25-parallel-slice-executor-r12/` and the linked scenario/bug retest records.

**Verdict: FAIL at the first fresh product defect (`selector_not_found` during Orca worktree discovery after accepted A/T1 partial effects).**
