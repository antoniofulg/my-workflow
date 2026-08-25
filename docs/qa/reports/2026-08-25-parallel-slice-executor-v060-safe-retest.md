# QA report — v0.6.0 safe parallel-slice retest

- **Date:** 2026-08-25
- **Release under test:** `v0.6.0` / `2177564d1f16597ed566afb8f3b28f388e6aa5ce`
- **Adapter:** CLI/manual through `tools/qa_parallel_pilot.py`, public
  `parallel_execute.py start|status|resume`, and Orca `orchestration.contract.v1`
- **Execution path:** fresh two-lane resource-free fixture; safe mode only
- **Raw evidence:** `docs/qa/evidence/2026-08-25-parallel-slice-executor-v060-safe-retest/`
- **Automated gate:** `npm run test:all` PASS after checkout-local `npm ci`; 8 Vitest files /
  110 tests and all Python suites passed
- **Environment:** macOS; Orca `1.4.188` runtime/graph ready with
  `orchestration.contract.v1`; Codex `0.149.1`

## Baseline and operator cleanup boundary

Before this cycle, the operator manually removed the historical pilot worktrees through Orca.
Read-only baseline inspection then found only the principal checkout and this QA coordinator
checkout, with no `parallel-slice-pilot`, `A-T1`, or `B-T2` physical worktrees and no pilot worker
terminals. Historical orchestration records remain and will not be reused.

This was **operator-forced cleanup**. It resets the physical test environment but does not prove the
product's automatic cleanup, lifecycle authorization, idempotency, or zero-residue contract. This
cycle uses a fresh fixture and a fresh Orca run.

## Matrix

| Charter | Scenario | Verdict | Evidence / limitation |
| --- | --- | --- | --- |
| `CH-execute-parallel-slices-2026-08-24` | `QAS-run-resource-free-parallel-orca-slices` | `blocked-verify` | Fresh A/T1 Dispatch failed at external `agent_prompt_stalled`; exact terminal remained live/writable; B/T2 never started |
| `CH-execute-parallel-slices-2026-08-24` | `QAS-clean-owned-parallel-slice-pilot` | `blocked-verify` | Lifecycle oracle returned incomplete; normal cleanup correctly not attempted while worker may be live |

## Preflight

The first `npm run test:all` attempt exited 127 because this fresh checkout had no local `vitest`.
`npm ci` installed the 95 packages already pinned by the tracked lockfile with 0 vulnerabilities.
The repeated gate passed: 8 Vitest files / 110 tests and every Python suite passed, including Orca
adapter 59, executor 45, planner 18, workflow config 44, and pilot 13.

Orca `1.4.188` reported runtime and graph `ready` plus `orchestration.contract.v1`. Codex reported
`0.149.1`. Setup created a new fixture rooted at
`/private/var/folders/lc/_v1mn5h560d2tsmz474y7d1c0000gn/T/parallel-slice-pilot-lmv8bsn2`.
Dry-run returned `validated: true`, `mode: safe`, equal repository/source HEAD
`11603908b4fe0c93021e98898ad3cb02de1e14fb`, and exactly two independent ready lanes with
`Resources: none`.

## Walk

Public `start --adapter auto` returned after 22.78 seconds with safe fallback
`reason: worker-failed`. A/T1's worktree was accepted, then Orca failed the Dispatch at
`dispatch_input` with `agent_prompt_stalled`. Read-only correlation found:

- Run `run_942877dd689c`;
- Task `task_d42864b08ad0`;
- Dispatch `ctx_59b69c5baa01`;
- terminal `term_f44a259c-fa87-43f5-8629-be06d063f49d`;
- terminal resource `wtr_cbddc1533e31`;
- detached worktree
  `/Users/antoniofulg/Projects/.parallel-slice-pilot-lmv8bsn2-parallel-slices/parallel-pilot/A-T1`.

The failed Dispatch's exact worker observation was still `live`; its terminal remained connected,
writable, owned, and `not_requested` for release. Executor fell back safely and did not start B/T2.
No concurrency window, `worker_done`, read, acknowledgement, release, same-terminal follow-up,
checkpoint, gate, or no-op receipt was reached.

After Orca revoked the Dispatch, the exact worker terminal sent three `worker_done` messages and one
escalation/status message across deliveries `delivery_f540...` and `delivery_15e...`. All four were
rejected because the capability was already revoked. The coordinator processed and acknowledged
the two mailbox deliveries, returning its inbox to empty; those transport acknowledgements do not
constitute accepted worker lifecycle acknowledgements. Accepted `worker_done` remained zero.

Public status reported no new actions. The status lifecycle checker returned `complete: false`; the
root checker returned `authorized: false`, `reason: lifecycle-incomplete`. Because an exact owned
worker may still be live, this session did not call `resume`, stop, acknowledgement, release,
normal cleanup, diagnostic abort, or manual deletion. The fresh fixture remains intact.

## Probes and lenses

- **Capability and release identity:** PASS — public capability present; v0.6.0 HEAD matched.
- **Two resource-free lanes:** PASS at dry-run; both independent and ready.
- **Concurrent activation:** BLOCKED — A/T1 failed before B/T2 launch.
- **Lifecycle correlation:** BLOCKED — zero terminal completion receipts.
- **Recovery/trust:** PASS for fail-closed product behavior; executor exposed the partial effect and
  refused unsafe progress. This does not satisfy the end-to-end scenario.
- **Cleanup and idempotency:** BLOCKED — lifecycle authorization never became true.
- **Independent reload/read:** PASS for the blocked state through fresh `status`, Orca Run/Task/
  Dispatch/worker reads, worktree inspection, and lifecycle check.
- **Accessibility/language:** not applicable to this CLI-only worker lifecycle.

## Debrief and terminal verdict

**BLOCKED-VERIFY.** The v0.6.0 product exposed and fenced the partial effect correctly, but Orca
again revoked a Dispatch for `agent_prompt_stalled` while its exact Codex terminal remained live and
writable. This reproduces the existing external Orca/Codex lifecycle boundary; it is not a new
product symptom and was deduplicated into the two existing bug records.

Recovery condition: Orca must either preserve the Dispatch until the exact worker can deliver
`worker_done`, or return an authoritative stop that also proves the exact terminal is no longer
live. Then a fresh QA session must repeat safe mode from a new fixture through two concurrent lanes,
read→ack→release, normal cleanup, repeated cleanup, and zero owned residue. Full mode remains out of
scope until safe mode passes.

## Evidence

- `docs/qa/evidence/2026-08-25-parallel-slice-executor-v060-safe-retest/commands.md`
- `docs/qa/evidence/2026-08-25-parallel-slice-executor-v060-safe-retest/preflight.md`
- `docs/qa/evidence/2026-08-25-parallel-slice-executor-v060-safe-retest/pilot-identities.md`
- `docs/qa/evidence/2026-08-25-parallel-slice-executor-v060-safe-retest/rejected-lifecycle-deliveries.md`

## Final gate

`npm run test:all` rerun after report/status changes: PASS. Vitest: 8 files / 110 tests. Every
Python suite passed, including Orca adapter 59, executor 45, planner 18, workflow config 44, and
pilot 13.
