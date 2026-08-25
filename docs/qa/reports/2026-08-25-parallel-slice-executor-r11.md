# QA report — parallel slice executor R11 retained safety and fresh start

- **Date:** 2026-08-25
- **Scope:** one retained-fixture safety replay, then a fresh current-HEAD safe two-lane pilot until the first product defect
- **Adapter:** CLI/manual through `qa_parallel_pilot.py`, public `parallel_execute.py`, and real local Orca `orchestration.contract.v1`
- **Environment:** checkout `/Users/antoniofulg/orca/workspaces/my-workflow/feat-parallel-slice-executor`, HEAD `9493f9a`; Orca `1.4.188`
- **Preflight gate:** `rtk npm run test:all` — pass; 9 Vitest files / 110 tests and all discovered Python suites passed
- **Raw evidence:** `docs/qa/evidence/2026-08-25-parallel-slice-executor-r11/`
- **Limitation:** this repository has no runtime, port, database, or configured resource provider; no such isolation claim is made

## Matrix

| Leg | Scenario | Verdict | Observable | Evidence |
| --- | --- | --- | --- | --- |
| Retained safety replay | `QAS-run-resource-free-parallel-orca-slices` | blocked-verify | Stable `release_identity_unproven` was promoted from nested aliases; Orca retained the owned resource without proving release, with no new release/retry/cleanup effect | `retained-resume.json`; `retained-status-after.json`; `retained-worker-list-after.json`; `retained-deliveries-peek-after.json` |
| Fresh start | `QAS-run-resource-free-parallel-orca-slices` | fail | `start --adapter auto` accepted only A-T1, then attempted a nonexistent UUID as the Run and returned `run_not_found`; B never started | `fresh-setup.json`; `fresh-dry-run.json`; `fresh-start.json`; `fresh-status-after-start.json`; `orca-current-run-show.json` |
| Fresh cleanup | `QAS-clean-owned-parallel-slice-pilot` | untested | Stopped at the first fresh product defect; lifecycle authorization and cleanup were not reached | `fresh-start.json`; `fresh-worktrees-after-start.txt` |
| Fallback canaries | `CFG-fallback-unproven-parallel-execution`, `CFG-plan-parallel-slice-dispatch` | untested | Stopped before disabled/unsupported/provider-absent canaries | `fresh-start.json` |
| Convergence | `QAS-bound-verifier-remediation-per-blocker` | untested | Stopped before the fingerprint walk | `fresh-start.json` |

## Retained safety replay

Exactly one public command was run against the retained fixture:

```text
rtk python3 .agents/skills/autonomous/scripts/parallel_execute.py resume --root /private/var/folders/lc/_v1mn5h560d2tsmz474y7d1c0000gn/T/parallel-slice-pilot-mdyg1hll --feature parallel-pilot --adapter auto --wait-seconds 30
```

The result was `fallback: true`, `reason: worker-failed`, with the required stable structured
`code: release_identity_unproven`, `idempotent: true`, `releaseState: retained`, and
`retainedReason: identity_unproven`. Correlated evidence preserved Run
`run_71671ad17a77`, Task `task_78fcfca161b8`, Dispatch `ctx_5f619d0f6298`, terminal
`term_2dcb9465-d91c-4260-baa3-b92859412439`, resource `wtr_2882893be650`, and the existing
release idempotency key. The nested `result.mutation` envelope was retained as evidence of the
original provider attempt; the replay reused the persisted failure and made no new release call.

Read-only post-checks found one failed Task/Dispatch, one owned retained resource, zero retry
Dispatches/workers/terminals, two unread rejected stale `worker_done` deliveries, and the same
source/A-T1 residue. This is an external-runtime block: Orca retains the resource without proving
release, so the old leg is `blocked-verify` and the exact residue remains preserved.

## Fresh walk and first defect

Setup returned fixture root
`/private/var/folders/lc/_v1mn5h560d2tsmz474y7d1c0000gn/T/parallel-slice-pilot-5spz2fp5`.
Dry-run returned `validated: true`, `mode: safe`, equal source/repository HEAD
`4e156a800a3be172a39bcc41edc121efa38f8c01`, and exactly two ready `Resources: none` lanes.

The first mutating fresh command was:

```text
rtk python3 .agents/skills/autonomous/scripts/parallel_execute.py start --root /private/var/folders/lc/_v1mn5h560d2tsmz474y7d1c0000gn/T/parallel-slice-pilot-5spz2fp5 --feature parallel-pilot --adapter auto
```

It returned `fallback: true`, `reason: worker-failed`, and partial effect
`code: run_not_found` for UUID `bbcfd7d6-288f-45de-8617-513750eefb06`. Before that failure it
accepted one Git worktree for slice A/T1 at
`/Users/antoniofulg/Projects/.parallel-slice-pilot-5spz2fp5-parallel-slices/parallel-pilot/A-T1`
with source head `4e156a8`. Slice B was never started. The read-only Orca list showed a real
Run `run_658585e3a862`, but no pilot task or worker; `run-show` confirms that Run's objective is
the current action key, while the worker attempt used the nonexistent UUID. This is a product
defect, not an external-runtime limitation.

Per the stop rule, no public `resume`, `worker_done` read/ack, release, lifecycle-check, normal
cleanup, repeat cleanup, fallback canary, or convergence walk ran after the defect.

## Residue

Old retained residue is separate and untouched: source fixture
`parallel-slice-pilot-mdyg1hll` at `dc4476af2b4bdfa577a4e8162d92d3fb3bb8d74b`, its existing A-T1
worktree, Run/Task/failed Dispatch/exited terminal, and retained owned Orca resource.

Fresh residue is intentionally retained for diagnosis because cleanup was not authorized by a
completed lifecycle: source fixture `parallel-slice-pilot-5spz2fp5`, its ownership/metadata
markers, one detached A-T1 worktree, and Orca Run `run_658585e3a862`. No fresh cleanup claim is
made. Unrelated worktrees and siblings were not touched.

## Commands, counts, and changed QA paths

- Gate: `rtk npm run test:all` — exit `0`; 9 Vitest files / 110 tests and all discovered Python suites passed.
- Retained mutation: exactly 1 public `resume`; stable structured safety result; 0 new retry, cleanup, release, terminal, or slice-B effects.
- Retained read-only counts: 1 failed Task, 1 failed Dispatch, 1 retained owned resource, 0 retry workers, 2 unread rejected stale deliveries, 1 A-T1 worktree.
- Fresh mutation: exactly 1 public `start`; 1 accepted worktree, 1 real Run, 0 pilot Tasks, 0 workers/terminals, 0 slice-B lanes; cleanup not run.
- Changed QA paths: `docs/qa/reports/2026-08-25-parallel-slice-executor-r11.md` and the evidence files under `docs/qa/evidence/2026-08-25-parallel-slice-executor-r11/`.
- No product, test, spec-validation, Git, push, merge, or broad cleanup action was performed.

**Verdict: FAIL at the first fresh product defect (`run_not_found` after accepted A-T1 worktree).**
