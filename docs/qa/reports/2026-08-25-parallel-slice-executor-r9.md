# QA report — parallel slice executor R9 recovery and fresh walk

- **Date:** 2026-08-25
- **Scope:** fresh independent retained-fixture recovery on current product HEAD `cb919c1`, followed by the current-HEAD two-lane pilot and fallback canaries only if recovery completes
- **Adapter:** CLI/manual through `qa_parallel_pilot.py`, public `parallel_execute.py`, and real local Orca `orchestration.contract.v1`
- **Environment:** checkout-local retained Git fixture; source fixture `/private/var/folders/lc/_v1mn5h560d2tsmz474y7d1c0000gn/T/parallel-slice-pilot-mdyg1hll`; checkout HEAD `cb919c1`; product recovery proof reference `7edfaf5`
- **Preflight gate:** `rtk npm run test:all` — pass (110 Vitest tests; all discovered Python suites passed)
- **Raw evidence:** `docs/qa/evidence/2026-08-25-parallel-slice-executor-r9/`
- **Limitation:** no runtime, port, database, or configured product resource provider exists; no isolation claim is made for those resources

## Matrix

| Charter | Scenario | Verdict | Observable | Evidence |
| --- | --- | --- | --- | --- |
| `CH-execute-parallel-slices-2026-08-24` | `QAS-run-resource-free-parallel-orca-slices` | fail | One public recovery repeated the release key but stopped with `worker-failed`/release-not-accepted; no explicit reconciliation, retry, or slice B | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r9/r9-recovery.md`; `docs/qa/evidence/2026-08-25-parallel-slice-executor-r9/r9-postcheck.md`; `BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree` |
| `CH-execute-parallel-slices-2026-08-24` | `QAS-clean-owned-parallel-slice-pilot` | untested | Recovery failed before lifecycle authorization, so normal cleanup and repeat cleanup were not run | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r9/r9-postcheck.md` |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `CFG-freeze-feature-workflow` | untested | Stopped at the first product defect before the canary | — |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `CFG-fallback-unproven-parallel-execution` | untested | Stopped at the first product defect before the canary | — |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `CFG-plan-parallel-slice-dispatch` | untested | Stopped at the first product defect before the canary | — |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `QAS-bound-verifier-remediation-per-blocker` | untested | Stopped at the first product defect before the canary | — |

## Preflight

At the start of this fresh verifier session, read-only public inspection confirmed the retained
ownership boundary from R8. The exact Run, Task, failed Dispatch, exited terminal, and owned
`release_unknown` terminal resource are still present. The two rejected stale `worker_done`
messages remain unread and are not completion evidence. The fixture source is unchanged at
`dc4476a`; the accepted A-T1 worktree remains the only derived lane.

## Execution rule

Run exactly one public recovery `resume --adapter auto --wait-seconds 30` against the retained
Run/Task. The recovery must repeat the same release request key, post-check the exact Dispatch and
exited/disconnected/non-writable terminal, persist explicit reconciled release and revocation
evidence, create exactly one retry-of the same selectors with an explicit timeout, reject stale
deliveries, and continue. A failure at that boundary is the first product defect and ends this
verifier session; the lifecycle oracle, cleanup, fresh pilot, and fallback canaries remain pending.

## R9 recovery and verdict

The single public `resume --adapter auto --wait-seconds 30` exited `0` but returned
`fallback: true`, `reason: worker-failed`, and `Orca worker release was not accepted`. It repeated
request `5b67b016-a78e-43ec-9044-1a87c3905475` for Dispatch `ctx_5f619d0f6298`, Run
`run_71671ad17a77`, Task `task_78fcfca161b8`, and terminal
`term_2dcb9465-d91c-4260-baa3-b92859412439`.

Read-only post-check shows the Run/Task/failed revoked Dispatch are unchanged; the terminal remains
exited, disconnected, and non-writable; the owned resource is `retained` with
`retainedReason: identity_unproven`, no release completion, and no explicit reconciled
release/revocation receipt. Exactly two stale rejected `worker_done` messages remain unread, no
retry Dispatch exists, and only the accepted A-T1 worktree remains.

**Verdict: FAIL at the first product defect.** Recovery still does not reconcile the exact release,
create one bounded retry-of the same Run/Task, or continue to the two-lane lifecycle. The lifecycle
oracle, normal cleanup/repeat, fresh two-lane pilot, disabled/unsupported/resource-provider-absent
fallbacks, and fingerprint convergence were not run.

## Commands and counts

- Gate: `rtk npm run test:all` — exit `0`; 110 Vitest tests and all discovered Python suites passed.
- Recovery mutation: exactly one public `parallel_execute.py resume --adapter auto --wait-seconds 30`; exit `0`, public `fallback: true`, `reason: worker-failed`.
- Read-only post-check: executor status, Run, Task, worker, worker list, delivery peek, and Git worktree list; all completed after the failed recovery.
- Receipt counts: 1 old failed/revoked Dispatch; 0 retry Dispatches; 1 owned `retained` terminal resource with `identity_unproven`; 2 rejected stale `worker_done` deliveries unread; 0 acknowledged completions.
- Lane counts: 1 accepted A-T1 worktree in serial fallback; 0 B-T2 lane/worktree/task/worker.

## QA paths changed

- `docs/qa/reports/2026-08-25-parallel-slice-executor-r9.md`
- `docs/qa/evidence/2026-08-25-parallel-slice-executor-r9/preflight.md`
- `docs/qa/evidence/2026-08-25-parallel-slice-executor-r9/r9-recovery.md`
- `docs/qa/evidence/2026-08-25-parallel-slice-executor-r9/r9-postcheck.md`
- `docs/qa/scenarios/QAS-run-resource-free-parallel-orca-slices.md`
- `docs/qa/bugs/BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree.md`
