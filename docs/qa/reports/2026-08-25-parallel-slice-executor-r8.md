# QA report — parallel slice executor R8 recovery

- **Date:** 2026-08-25
- **Scope:** fresh independent retained-fixture recovery on product HEAD `a1a49a2`, followed by the current-HEAD two-lane pilot and fallback canaries only if recovery completes
- **Adapter:** CLI/manual through `qa_parallel_pilot.py`, public `parallel_execute.py`, and real local Orca `orchestration.contract.v1`
- **Environment:** checkout-local retained Git fixture; source fixture `/private/var/folders/lc/_v1mn5h560d2tsmz474y7d1c0000gn/T/parallel-slice-pilot-mdyg1hll`; product HEAD `a1a49a2a07954e46e30408496c4ba85ba79220b9`
- **Preflight gate:** `rtk npm run test:all` — pass (110 Vitest tests; 185 named Python tests across all discovered suites)
- **Raw evidence:** `docs/qa/evidence/2026-08-25-parallel-slice-executor-r8/`
- **Limitation:** no runtime, port, database, or configured product resource provider exists; no isolation claim is made for those resources

## Matrix

| Charter | Scenario | Verdict | Observable | Evidence |
| --- | --- | --- | --- | --- |
| `CH-execute-parallel-slices-2026-08-24` | `QAS-run-resource-free-parallel-orca-slices` | fail | One public recovery stopped with `worker-failed`/`invalid Orca run id`; no explicit reconciliation, retry, or slice B | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r8/r8-recovery.md`; `r8-postcheck.md`; `BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree` |
| `CH-execute-parallel-slices-2026-08-24` | `QAS-clean-owned-parallel-slice-pilot` | untested | Recovery failed before lifecycle authorization, so normal cleanup and repeat cleanup were not run | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r8/r8-postcheck.md` |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `CFG-freeze-feature-workflow` | untested | Stopped at the first product defect before the canary | — |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `CFG-fallback-unproven-parallel-execution` | untested | Stopped at the first product defect before the canary | — |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `CFG-plan-parallel-slice-dispatch` | untested | Stopped at the first product defect before the canary | — |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `QAS-bound-verifier-remediation-per-blocker` | untested | Stopped at the first product defect before the canary | — |

## Preflight

At `2026-08-25T08:11:07Z`, read-only public inspection confirmed the retained ownership boundary:

- Run `run_71671ad17a77`
- Task `task_78fcfca161b8`
- failed/revoked Dispatch `ctx_5f619d0f6298`
- exited, disconnected, non-writable terminal `term_2dcb9465-d91c-4260-baa3-b92859412439`
- terminal resource `wtr_2882893be650` in `release_unknown` with `tab_not_found`
- persisted release request already present; no release completion and no retry Dispatch
- exactly two rejected stale `worker_done` messages remain unread and cannot count as completion

The retained fixture is owned and remains unmodified pending one public `resume`. No manual
acknowledgement, release, force-delete, reset, or broad cleanup is authorized.

## Execution rule

Run exactly one public recovery `resume` with the retained Run/Task state. The recovery must repeat
the same release request key, post-check the exact Dispatch and terminal, persist an explicit
reconciled receipt, revoke the stale Dispatch, create exactly one retry-of the same Run/Task with
an explicit timeout, and then continue. A failure at that boundary is the first product defect and
ends this verifier session; remaining canaries and cleanup stay pending and the exact residue is
retained for the Implementer.

## R8 exact walk and verdict

1. One public `resume --adapter auto --wait-seconds 30` ran against the retained fixture. It exited
   `0` but returned `fallback: true`, `reason: worker-failed`, and one worker action for slice A.
2. The partial effect preserved the exact old Dispatch/Run/Task/terminal and the same release
   request key, but persisted `invalid Orca run id` rather than an explicit reconciled receipt.
3. Read-only post-checks confirmed the exact Dispatch stayed failed/revoked, its exited terminal
   stayed owned in `release_unknown` after `tab_not_found`, the Task remained failed, and no retry
   Dispatch existed.
4. Read-only `check --peek` showed exactly two rejected stale `worker_done` messages, both unread;
   neither was counted as completion.
5. Git residue remains the retained fixture source and the accepted A-T1 worktree; B-T2 is absent.

**Verdict:** fail at the first product defect. The public recovery does not perform the required
exact-once release reconciliation, stale Dispatch revocation, one bounded retry-of, or continuation.
The lifecycle oracle, normal cleanup/repeat, fresh two-lane pilot, disabled/unsupported/resource-
provider-absent fallbacks, and fingerprint convergence were not run. No product files changed.

## Commands and counts

- Gate: `rtk npm run test:all` — exit `0`; 110 Vitest tests and 185 named Python tests passed.
- Read-only preflight: current HEAD, Orca status, executor status, Run, Task, worker, worker list,
  and delivery peek; all completed without lifecycle mutation.
- Recovery mutation: exactly one public `parallel_execute.py resume --adapter auto --wait-seconds 30`;
  no direct acknowledgement, release, revoke, retry, force-delete, reset, or cleanup command ran.
- Read-only post-check: executor status, Run, Task, worker, worker list, delivery peek, and Git
  worktree list; all completed after the failed recovery.
- Receipt counts: 1 old failed/revoked Dispatch; 0 retry Dispatches; 1 owned `release_unknown`
  terminal resource; 2 rejected stale `worker_done` deliveries unread; 0 acknowledged completions.
- Lane counts: 1 accepted A-T1 worktree in serial fallback; 0 B-T2 lane/worktree/task/worker.

## QA paths changed

- `docs/qa/reports/2026-08-25-parallel-slice-executor-r8.md`
- `docs/qa/evidence/2026-08-25-parallel-slice-executor-r8/preflight.md`
- `docs/qa/evidence/2026-08-25-parallel-slice-executor-r8/r8-recovery.md`
- `docs/qa/evidence/2026-08-25-parallel-slice-executor-r8/r8-postcheck.md`
- `docs/qa/scenarios/QAS-run-resource-free-parallel-orca-slices.md`
- `docs/qa/bugs/BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree.md`
