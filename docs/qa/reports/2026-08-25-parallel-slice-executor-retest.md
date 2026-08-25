# QA report — parallel slice executor retest

- **Date:** 2026-08-25
- **Scope:** fresh retest of the parallel Orca lifecycle fixes, followed by planned fallback and convergence canaries
- **Adapter:** CLI/manual through `qa_parallel_pilot.py`, public `parallel_execute.py`, and real local Orca `orchestration.contract.v1`
- **Environment:** checkout-local disposable Git fixture; latest checkout HEAD `48ec1cb97ce843fa084340b9c41e3fd320416686`; product HEAD `35a49bf`; fixture source `dc4476af2b4bdfa577a4e8162d92d3fb3bb8d74b`
- **Preflight gate:** fresh independent technical verification at `2fb2f419` records
  `npm_config_offline=true npm run test:all` pass (9 Vitest files / 110 tests; 174 named Python
  tests across 12 suites passed); validation-only HEAD `3a9f3468` adds no product change. Fresh
  technical verification at product HEAD `453a8ab` records `npm run test:all` pass
  (110 Vitest + 176 Python = 286 tests) and a 2/2 killed discrimination sensor; validation-only
  HEAD `fd9fbc1` adds no product change.
  R7 preflight at checkout `48ec1cb` ran `rtk npm run test:all`: 9 Vitest files / 110 tests and
  every discovered Python suite passed.
- **Raw evidence:** `docs/qa/evidence/2026-08-25-parallel-slice-executor-retest/`
- **Limitation:** no runtime, port, database, or configured product resource provider exists; no isolation claim is made for those resources.

## Matrix

| Charter | Scenario | Verdict | Observable | Evidence |
| --- | --- | --- | --- | --- |
| `CH-execute-parallel-slices-2026-08-24` | `QAS-run-resource-free-parallel-orca-slices` | fail | R7 projected the authoritative terminal and requested release, but Orca returned `tab_not_found`; release is `unknown`, no retry exists, and slice B remains absent | `docs/qa/evidence/2026-08-25-parallel-slice-executor-retest/r7-recovery.md`; `BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree` |
| `CH-execute-parallel-slices-2026-08-24` | `QAS-clean-owned-parallel-slice-pilot` | untested | Completed lifecycle remains unreachable; fresh diagnostic abort correctly did not claim success and retained the fixture as `worker-may-be-live` | `docs/qa/evidence/2026-08-25-parallel-slice-executor-retest/r4-abort.json`; `BUG-20260824-parallel-pilot-cleanup-allows-incomplete-lifecycle` |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `CFG-freeze-feature-workflow` | untested | Not walked: QA stopped at the re-found product defect | — |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `CFG-fallback-unproven-parallel-execution` | untested | Not walked: QA stopped at the re-found product defect | — |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `CFG-plan-parallel-slice-dispatch` | untested | Not walked: QA stopped at the re-found product defect | — |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `QAS-bound-verifier-remediation-per-blocker` | untested | Not walked: QA stopped at the re-found product defect | — |

## Exact walk

1. `rtk npm run test:all` passed.
2. `rtk orca status --json` reported Orca 1.4.188 ready with `orchestration.contract.v1`.
3. `rtk python3 tools/qa_parallel_pilot.py setup` created the owned fixture.
4. Public `dry-run` returned `validated: true`, `mode: safe`, equal source/repository HEADs, and exactly two ready `Resources: none` lanes.
5. Public `start --adapter auto` returned `fallback: true`, `reason: worker-failed`, and `selector_not_found` after accepting slice A's detached worktree and creating Orca Run/Task ids.
   The Orca selector passed was `path:/Users/antoniofulg/Projects/.parallel-slice-pilot-mdyg1hll-parallel-slices/parallel-pilot/A-T1`.
6. Public `status` independently showed slice A serial, one accepted worktree action, one pending worker action, and no slice-B state.
7. Read-only Orca inspection showed one ready Task and zero workers for the returned Run.
8. Public diagnostic `cleanup --abort-incomplete` returned `cleaned: false`, `aborted: false`, and `worker-may-be-live`. No normal cleanup, manual deletion, or broad Orca reset was attempted.

## Fix-loop recovery on `3a9f346`

1. Public status confirmed the retained accepted slice-A worktree, Run
   `run_71671ad17a77`, Task `task_78fcfca161b8`, pending worker action, and absent slice B.
2. Read-only Orca inspection confirmed the Task was ready and the Run owned zero workers before
   recovery.
3. One bounded public `resume --adapter auto --wait-seconds 30` reused the same Run and Task and
   created Dispatch `ctx_5f619d0f6298`; no identity was recreated.
4. Recovery returned `fallback: true`, `reason: worker-failed`; Orca reported failed stage
   `dispatch_input` and `lastError: agent_prompt_stalled`.
5. Independent Orca reads showed the Task and worker failed, with terminal
   `term_2dcb9465-d91c-4260-baa3-b92859412439` reclaimable and release not requested.
6. Canonical lifecycle check returned `authorized: false`, `lifecycle-incomplete`. Public diagnostic
   abort again returned `cleaned: false`, `worker-may-be-live`.
7. The fixture source and slice-A worktree remain registered. No fixture was created, no normal
   cleanup ran, and no manual deletion or broad Orca reset occurred.

## Debrief

The worker-start fix does not pass the production-parity adapter. The defect is not the old hidden
`actions: []` presentation anymore—the partial ids and action are visible—but the user-visible
journey still cannot start either worker or reach concurrency. Two worktrees, branches, tasks,
dispatches, terminals, simultaneous activity, `worker_done`, read→ack→release, lifecycle
authorization, normal cleanup, repeated cleanup, and zero owned residue are therefore all absent.

The session stopped at the confirmed product defect as required. Fallback, resource-provider-absent,
and fingerprint-convergence scenarios remain `untested`; the cleanup defect remains pending a fresh
retest after worker start is repaired. The exact owned fixture was retained because the public
diagnostic cleanup refused it; unrelated pilot residue was observed but not touched.

The follow-up recovery fix removed the original worktree selector barrier but did not make the
public journey executable: worker input stalled after Dispatch acceptance. Because recovery did not
reach a worker lifecycle, this fresh Verifier stopped before creating a new fixture or walking the
remaining canaries. Retained residue is exact and owned: fixture source, slice-A worktree, Run, Task,
failed Dispatch, and one reclaimable terminal.

## Fresh recovery on product HEAD `453a8ab`

1. `rtk orca status --json` reported Orca 1.4.188 ready with
   `orchestration.contract.v1`.
2. `rtk orca orchestration check --run run_71671ad17a77` exposed the retained rejected stale
   `worker_done` Delivery without acknowledging it.
3. Public `status` confirmed the exact retained Run, Task, failed Dispatch, reclaimable terminal,
   accepted slice-A worktree, and absent slice B.
4. One bounded public `resume --adapter auto --wait-seconds 30` returned `fallback: true`,
   `reason: worker-failed`, and persisted `invalid Orca dispatch id`.
5. Independent Orca reads confirmed the old Dispatch remains failed and revoked, release remains
   `not_requested`, two rejected stale `worker_done` messages exist, and no retry Dispatch exists.
6. Canonical lifecycle check returned `authorized: false`, `lifecycle-incomplete`. Public diagnostic
   abort returned `cleaned: false`, `worker-may-be-live`.

This is the first product defect in the fresh session, so QA stopped. No new fixture, fallback
canary, convergence walk, normal cleanup, manual acknowledgement, manual release, or broad reset ran.

## Fresh recovery R5 on product HEAD `941bbc5`

1. `rtk orca status --json` reported Orca 1.4.188 ready with
   `orchestration.contract.v1`.
2. Public `status` confirmed the exact retained Run, Task, failed Dispatch, reclaimable terminal,
   accepted slice-A worktree, and absent slice B.
3. One bounded public `resume --adapter auto --wait-seconds 30` returned `fallback: true`,
   `reason: worker-failed`, and persisted `invalid Orca dispatch id` again.
   Public `status` showed the exact legacy identity only at
   `state.actions["6c23af154805041a709d55309c674e2f4548b19cc9c26ec4a035d3cf2a01e473"].partial_effect.result.dispatchId`;
   that `partial_effect` had no top-level `dispatch_id`.
4. Independent Orca reads confirmed exactly one Dispatch, still failed and capability-revoked;
   its terminal remains reclaimable, its release remains `not_requested`, exactly two stale
   rejected `worker_done` messages remain unread, and zero retry Dispatches exist.
5. Canonical lifecycle check returned `authorized: false`, `lifecycle-incomplete`. Public
   diagnostic abort returned `cleaned: false`, `worker-may-be-live`.

Evidence: `docs/qa/evidence/2026-08-25-parallel-slice-executor-retest/r5-recovery.md`.

This is the first product defect in R5. The nested Dispatch normalization fix did not reach the
persisted recovery path, so QA stopped without creating a new fixture or walking fallback and
convergence canaries. No stale Delivery was acknowledged, no Dispatch was released manually, and
no broad reset or normal cleanup ran.

## Fresh recovery R6 on product HEAD `e24228c`

1. `rtk orca status --json` reported Orca 1.4.188 ready with
   `orchestration.contract.v1`.
2. The requested `rtk orca orchestration check --run run_71671ad17a77` exposed the oldest retained
   rejected `worker_done` Delivery without acknowledgement.
3. Public `status` confirmed the exact nested `partial_effect.result.dispatchId`, accepted
   slice-A worktree, failed Run/Task/Dispatch boundary, and absent slice B.
4. One bounded public `resume --adapter auto --wait-seconds 30` normalized
   `ctx_5f619d0f6298`, then returned `fallback: true`, `reason: worker-failed`, and persisted
   `invalid Orca terminal handle`.
5. Independent Orca reads confirmed exactly one failed/revoked Dispatch and zero retries. Its exact
   terminal is live/reclaimable and owned, release remains `not_requested`, and both stale rejected
   `worker_done` messages remain unread.
6. Canonical lifecycle check returned `complete: false`. Public diagnostic abort returned
   `cleaned: false`, `worker-may-be-live`.

Evidence: `docs/qa/evidence/2026-08-25-parallel-slice-executor-retest/r6-recovery.md`.

This is the first product defect in R6. QA stopped without creating a fresh fixture or walking the
fallback and convergence canaries. No Delivery was acknowledged, no Dispatch was released manually,
and no force-delete, reset, normal cleanup, or unrelated-fixture mutation ran.

## Fresh recovery R7 on product HEAD `35a49bf`

1. The requested `rtk orca orchestration check --run run_71671ad17a77 --json` replayed one rejected
   stale `worker_done` without acknowledgement.
2. `rtk npm run test:all` passed (9 Vitest files / 110 tests and every discovered Python suite).
3. Public `status` confirmed the nested Dispatch, missing persisted terminal projection, accepted
   slice-A worktree, failed Run/Task boundary, and absent slice B.
4. Exactly one bounded public `resume --adapter auto --wait-seconds 30` projected terminal
   `term_2dcb9465-d91c-4260-baa3-b92859412439` and requested release.
5. Recovery returned `fallback: true`, `reason: worker-failed`; Orca reported `tab_not_found` and
   the public state retained the terminal but marked the action pending.
6. Independent `worker-show`, `task-list`, and `worker-list` confirmed one failed/revoked Dispatch,
   one failed Task, one owned terminal resource in `release_unknown`, no release completion, and no
   retry Dispatch.

Evidence: `docs/qa/evidence/2026-08-25-parallel-slice-executor-retest/r7-recovery.md`.

This is the first product defect in R7. QA stopped before a fresh fixture, fallback canaries,
convergence, lifecycle-check, normal cleanup, or repeated cleanup. No stale Delivery was
acknowledged and no lifecycle action, force-delete, reset, or unrelated-fixture mutation ran.
