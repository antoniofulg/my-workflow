# BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree

- **Status:** open — live retest `blocked-verify` at external Orca/Codex boundary
- **Severity:** major
- **Scenario:** `QAS-run-resource-free-parallel-orca-slices`; `CFG-fallback-unproven-parallel-execution`; `QAS-coordinate-assisted-orca-slices`
- **Expected:** With proven Orca `orchestration.contract.v1`, public `start --adapter auto` starts both validated resource-free lanes; if worker start fails, fallback reports and reconciles every accepted partial effect without hiding a worktree, Run, Task, Dispatch, terminal, or resource behind `actions: []`.
- **Observed at discovery:** A validated two-lane fixture accepted A/T1's worktree and Orca state, then returned `worker-failed`; B/T2 never started. Earlier responses hid accepted effects behind `actions: []`.
- **Adapter:** public `parallel_execute.py` plus read-only Orca and Git inspection
- **Exact path:** `qa_parallel_pilot.py setup|dry-run` → `parallel_execute.py start|status|resume` → read-only Orca/Git inspection
- **Initial evidence:** `docs/qa/evidence/2026-08-24-parallel-slice-executor/orca-pilot/start.json`; `status-after-start.json`; `orca-runs.json`; `orca-tasks.json`; `orca-workers.json`; `git-worktrees-after-failure.txt`

## Product fix state

The following product root causes have independent technical fixes and validation records; they do
not close this bug's live two-lane promise:

- contextual worktree receipts — `1e40171`;
- canonical Run/Task identity correlation — `f02b679`;
- persisted Dispatch and terminal recovery — `e24228c`, `35a49bf`, `a736757`;
- live failed-worker fencing and recovery-stop safety — `5b7a9dd`, `48e5322`;
- provider preflight before lane mutation — `0ed8b55`.

R19 independently passes the provider-preflight subpath. Two starts of two runtime-bearing lanes
returned `missing-resource-provider` with `actions: []`; two fresh-process statuses returned
`state: null`; Orca Run inventory stayed `12 -> 12`, worker inventory `151 -> 151`, and no lane
worktree, runtime receipt, Task, Dispatch, terminal, or lease appeared. R19 diagnostic abort and
its repeat returned `residual_paths: []`. Evidence: [`R19 report`](../reports/2026-08-25-parallel-slice-executor-r19.md),
[`R19 commands`](../evidence/2026-08-25-parallel-slice-executor-r19/commands.md), and the
`resource-*.json` files in that evidence directory.

## Terminal live retest

The real positive Orca/Codex journey is `blocked-verify`, not a product `fail`, `pass`, or
`untested` result. R14 recorded a separate user-takeover/prompt residue: Orca `1.4.188` returned
`agent_prompt_blocked` while the terminal watchdog saw `codex-update-prompt`; diagnostic cleanup
refused with `worker-may-be-live`. R15 observed `agent_prompt_stalled` with Codex `0.149.1`; Orca
revoked the Dispatch while Codex later completed externally. R17's exact public recovery-stop then
returned `alreadySettled: true` / `state: failed` and left the exact owned terminal live and
writable. A replay made no progress. The product correctly refuses release, retry, and cleanup at
that boundary; this is external verification debt, not a new product root cause.

No completed two-lane lifecycle, accepted `worker_done`, read→ack→release chain, normal cleanup,
repeat cleanup, or zero-owned-residue claim exists. This bug therefore remains open. Do not change
its status to fixed until a durable real-contract result satisfies its defined two-lane/recovery
condition.

## Historical retest ledger

The links below preserve prior evidence while removing repeated interim narratives.

| Retest | Outcome | Durable evidence |
| --- | --- | --- |
| 2026-08-24 initial walk | Product failure: hidden partial A/T1 effect and no B/T2 worker | `docs/qa/evidence/2026-08-24-parallel-slice-executor/orca-pilot/` |
| R8 | Retained recovery stopped at invalid Run identity | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r8/r8-recovery.md`; `r8-postcheck.md`; [`R8 report`](../reports/2026-08-25-parallel-slice-executor-r8.md) |
| R9 | Retained release remained `identity_unproven` | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r9/r9-recovery.md`; `r9-postcheck.md`; [`R9 report`](../reports/2026-08-25-parallel-slice-executor-r9.md) |
| R10 | Generic release evidence; replay/no-new-release semantics unproven | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r10/retained-resume.md`; `retained-resume.json`; `retained-orca-state.md`; [`R10 report`](../reports/2026-08-25-parallel-slice-executor-r10.md) |
| R11 | Fresh start stopped at invalid Run identity; retained safety replay structured | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r11/fresh-start.json`; `fresh-status-after-start.json`; `retained-resume.json`; [`R11 report`](../reports/2026-08-25-parallel-slice-executor-r11.md) |
| R12 | Fresh start stopped at `selector_not_found` after A/T1 Run/Task acceptance | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r12/start.json`; `status-after-start.json`; `orca-run.json`; `orca-tasks.json`; `orca-workers.json`; [`R12 report`](../reports/2026-08-25-parallel-slice-executor-r12.md) |
| R13 | Fresh start stopped at malformed worktree receipt; residue retained | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r13/commands.md`; `residue.md` |
| R14 | External prompt/user-takeover boundary; diagnostic cleanup refused | [`R14 session`](../evidence/2026-08-25-parallel-slice-executor-r14/session.md); `worker-show-summary.json`; `lifecycle-and-abort.json` |
| R15 | Orca `agent_prompt_stalled`; one live owned Codex terminal; B/T2 absent | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r15/start.json`; `terminal-watchdog.json`; `orca-identities.json`; `lifecycle-and-residue.json` |
| R16 | Ownership projection fix independently verified; recovery stopped safely before release/retry | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r16/r15-resume.json`; `r15-orca-reads.json`; `verdict.json` |
| R17 | Exact stop replayed `alreadySettled`; live terminal remained; release/retry/cleanup correctly refused | `docs/qa/evidence/2026-08-25-parallel-slice-executor-r17/r15-resume-1.json`; `r15-resume-2.json`; `r15-orca-reads.json`; `verdict.json`; [`R17 commands`](../evidence/2026-08-25-parallel-slice-executor-r17/commands.md) |
| R18 | Provider canary exposed preflight side effect; fixed in `0ed8b55` | [`R18 report`](../reports/2026-08-25-parallel-slice-executor-r18.md); `docs/qa/evidence/2026-08-25-parallel-slice-executor-r18/resource-*.json` |
| R19 | Provider-preflight subpath passed; real worker lifecycle intentionally not rerun | [`R19 report`](../reports/2026-08-25-parallel-slice-executor-r19.md); `docs/qa/evidence/2026-08-25-parallel-slice-executor-r19/` |
| v0.6.0 safe retest | External boundary reproduced: A/T1 `agent_prompt_stalled`, exact owned terminal remained live/writable, B/T2 absent; product exposed/fenced partial effect | [`v0.6.0 safe retest`](../reports/2026-08-25-parallel-slice-executor-v060-safe-retest.md); `docs/qa/evidence/2026-08-25-parallel-slice-executor-v060-safe-retest/` |
| Assisted Retest 5 | Exact A follow-up returned `agent_prompt_stalled`, but the same handle silently executed A:T7/A:T8 and created two commits; B parked correctly; coordinator stopped before sync/follow-up | [`assisted report`](../reports/2026-08-27-assisted-orca-slices.md); `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-5/` |
| Assisted Retest 6 | Two fresh verifier sends returned `agent_prompt_stalled`; no resend/replacement occurred, and same-handle bounded reconciliation accepted exactly one complete expected PASS effect for each. Worker sends were normal. Later shared-task-file conflict invalidated the happy-path fixture. Broader automatic lifecycle bug remains open. | [`assisted report`](../reports/2026-08-27-assisted-orca-slices.md); `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-6/` |

## Residue boundary

Retained fixtures are evidence, not cleanup claims. R14's prompt/user-takeover fixture, R15/R17's
live owned terminal fixture, and the older R8–R11 `identity_unproven` fixture remain separate and
must not be reset, force-deleted, or conflated. The canonical terminal QA report records each
boundary: [`2026-08-25-parallel-slice-executor-final`](../reports/2026-08-25-parallel-slice-executor-final.md).

## v0.6.0 safe-mode retest reset

On 2026-08-25, the operator manually removed the historical pilot worktrees through Orca. This
operator-forced cleanup cleared physical test residue but does not prove automatic reconciliation,
worker lifecycle completion, or product cleanup. The fresh retest is tracked in
[`2026-08-25-parallel-slice-executor-v060-safe-retest`](../reports/2026-08-25-parallel-slice-executor-v060-safe-retest.md);
the bug remains open with retest pending until that independent run reaches its terminal condition.

The fresh run reached the same external boundary and no new product symptom. Run
`run_942877dd689c`, Task `task_d42864b08ad0`, Dispatch `ctx_59b69c5baa01`, and terminal
`term_f44a259c-fa87-43f5-8629-be06d063f49d` remain correlated in the preserved fixture. Product
fallback exposed the accepted effect and did not start B/T2. Retest remains `blocked-verify`.
After capability revocation, the exact terminal sent three rejected `worker_done` messages and one
rejected escalation/status message across two coordinator deliveries. This proves the external
completion raced behind Orca's revocation; accepted lifecycle completion remained zero.
