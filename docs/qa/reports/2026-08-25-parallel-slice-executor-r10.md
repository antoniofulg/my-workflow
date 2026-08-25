# QA report — parallel slice executor R10 retained-fixture safety and fresh pilot

- **Date:** 2026-08-25
- **Scope:** one retained-fixture public resume safety replay on product `6975d4e`, then (only if the safety contract holds) a fresh current-HEAD Orca two-lane journey and fallback/convergence canaries
- **Adapter:** CLI/manual through `qa_parallel_pilot.py`, public `parallel_execute.py`, and real local Orca `orchestration.contract.v1`
- **Environment:** checkout-local retained or disposable Git fixture; checkout HEAD `bf1c8f2`; product recovery reference `6975d4e`
- **Preflight gate:** `rtk npm run test:all` — pass (9 Vitest files / 110 tests; all discovered Python suites passed)
- **Raw evidence:** `docs/qa/evidence/2026-08-25-parallel-slice-executor-r10/`
- **Limitation:** no runtime, port, database, or configured product resource provider exists; no isolation claim is made for those resources

## Matrix

| Charter | Scenario | Verdict | Observable | Evidence |
| --- | --- | --- | --- | --- |
| `CH-execute-parallel-slices-2026-08-24` | `QAS-run-resource-free-parallel-orca-slices` | fail | Retained safety replay returned generic `worker-failed` / `release_not_accepted` instead of stable structured `release_identity_unproven`; no fresh pilot started | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r10/retained-resume.md`; `docs/qa/evidence/2026-08-25-parallel-slice-executor-r10/retained-orca-state.md`; `BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree` |
| `CH-execute-parallel-slices-2026-08-24` | `QAS-clean-owned-parallel-slice-pilot` | untested | Fresh lifecycle authorization was not reached; old retained residue was preserved and no fresh cleanup was attempted | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r10/retained-resume.md` |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `CFG-freeze-feature-workflow` | untested | Stopped at first product defect before canary | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r10/retained-resume.md` |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `CFG-fallback-unproven-parallel-execution` | untested | Stopped at first product defect before canary | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r10/retained-resume.md` |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `CFG-plan-parallel-slice-dispatch` | untested | Stopped at first product defect before canary | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r10/retained-resume.md` |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `QAS-bound-verifier-remediation-per-blocker` | untested | Stopped at first product defect before canary | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r10/retained-resume.md` |

## Execution rule

Before creating a fixture, perform exactly one public `resume --adapter auto` against the retained
fixture. It must return stable structured `release_identity_unproven`, correlate the exact old
Run/Task/Dispatch/terminal, perform zero retry/cleanup/new-release effects, and preserve residue.
If and only if that exact contract holds, classify the old leg `blocked-verify` external-runtime and
continue with a fresh fixture. Any generic/lost evidence or new effect is a product defect and ends
this session.

## Preflight

The current checkout is `bf1c8f26f0ecae9b36a067c584bb3aa9fa87b671`; product recovery reference is
`6975d4e610662c153105e1dac4f69ce0bcee839f`. Orca `1.4.188` is ready and advertises
`orchestration.contract.v1`. The gate passed. No runtime, port, database, or configured product
resource provider exists; no isolation claim is made.

## Retained safety replay

Exactly one public `parallel_execute.py resume --adapter auto --wait-seconds 30` ran against the
retained fixture. It preserved correlated Run `run_71671ad17a77`, Task `task_78fcfca161b8`, Dispatch
`ctx_5f619d0f6298`, terminal `term_2dcb9465-d91c-4260-baa3-b92859412439`, and resource
`wtr_2882893be650`. Independent reads show the Task and Dispatch failed, the terminal exited/
disconnected/non-writable, and the resource remains owned/retained with `identity_unproven` and no
release completion. No retry Dispatch, cleanup, new terminal resource, or slice-B lane appeared;
the owned source and A-T1 worktree remain.

The expected structured safety result did not hold. Public output was `fallback: true`, top-level
`reason: worker-failed`, `code: release_not_accepted`, `lastError: tab_not_found`, and
`message: selector_not_found`; `identity_unproven` appeared only as nested detail. The partial
effect also reported `mutation.replayed: false` with a new request id, so replay stability and
zero-new-release semantics are not proven. This is a product defect, not an external-runtime
blocker. The old retained residue remains untouched.

## Stop boundary and residue

Stopped before fresh setup, dry-run, start, lifecycle-check, normal cleanup, repeat cleanup,
fallback/resource-provider canaries, and fingerprint convergence. No fresh QA pilot fixture was
created. Old retained residue: fixture source at `dc4476af2b4bdfa577a4e8162d92d3fb3bb8d74b` with
its existing `.parallel-slice-qa-fixture`, `.parallel-slice-qa-ownership.json`, and
`.specs/features/parallel-pilot/workflow.json` markers; accepted detached A-T1 worktree,
Run/Task/failed Dispatch/exited terminal, and owned retained terminal resource. Existing unrelated
worktrees/siblings were preserved. Fresh-fixture residue: none; fresh cleanup: not run.

Evidence: `docs/qa/evidence/2026-08-25-parallel-slice-executor-r10/retained-resume.md`,
`retained-resume.json`, `retained-status.json`, `retained-orca-state.md`,
`retained-worktrees.txt`, `retained-git-status.txt`, and `retained-source-head.txt`.
