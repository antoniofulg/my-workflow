# BUG-20260824-parallel-pilot-cleanup-allows-incomplete-lifecycle

- **Status:** open — live retest `blocked-verify` at external Orca/Codex boundary
- **Severity:** major
- **Scenario:** `QAS-clean-owned-parallel-slice-pilot`
- **Expected:** Public normal cleanup refuses effects until `lifecycle-check` accepts exactly two correlated terminal read-before-ack-before-release receipts.
- **Observed at discovery:** Immediately after incomplete A/T1 worker start, normal cleanup returned `cleaned: true` and removed the fixture despite zero lifecycle receipts and absent B/T2.
- **Adapter:** public `qa_parallel_pilot.py cleanup` with executor status and filesystem residue inspection
- **Exact path:** failed `parallel_execute.py start` → `parallel_execute.py status` → `qa_parallel_pilot.py cleanup --root <root>` without a passing lifecycle check
- **Initial evidence:** `docs/qa/evidence/2026-08-24-parallel-slice-executor/orca-pilot/status-after-start.json`; `cleanup-after-failure.json`; `cleanup-repeat.json`; `residue.json`

## Product fix state

Cleanup authorization and fail-closed recovery were fixed and technically validated by `d8c848e`,
`1216014`, `6b3f1f0`, `5b7a9dd`, `48e5322`, and `a736757`. R14/R15/R17 diagnostic boundaries
show the product refusing `worker-may-be-live` when an exact owned terminal remains unsafe. That
proves safety behavior, not successful normal cleanup of a completed two-lane lifecycle.

## Terminal retest

The scenario is `blocked-verify`, not `pass`, `fail`, or `untested`. The external Orca/Codex path
stalls after `agent_prompt_stalled`; the later exact recovery-stop returns `alreadySettled` while
the owned terminal remains live/writable. Product correctly refuses release, retry, and cleanup.
Because lifecycle authorization never became true, normal cleanup and repeat cleanup were not run.
No bug closure or zero-residue claim is allowed.

R19's effect-free provider fixture was diagnostically aborted with `residual_paths: []` twice, but
that fixture had no worker effect and is not evidence for this completed-pilot cleanup promise.
Evidence: [`R19 report`](../reports/2026-08-25-parallel-slice-executor-r19.md),
[`R19 residue`](../evidence/2026-08-25-parallel-slice-executor-r19/resource-residue.json).

## Historical evidence

- Initial incomplete-lifecycle cleanup: `docs/qa/evidence/2026-08-24-parallel-slice-executor/orca-pilot/`.
- Recovery and retained-resource boundaries: [`parallel-slice-executor retest`](../reports/2026-08-25-parallel-slice-executor-retest.md),
  `docs/qa/evidence/2026-08-25-parallel-slice-executor-retest/r4-abort.json`,
  `docs/qa/evidence/2026-08-25-parallel-slice-executor-r10/retained-resume.md`,
  `docs/qa/evidence/2026-08-25-parallel-slice-executor-r10/retained-orca-state.md`.
- R12 fail-closed diagnostic abort: `docs/qa/evidence/2026-08-25-parallel-slice-executor-r12/abort-incomplete.json`;
  `residue.md`.
- R14/R15/R17 external boundary: `docs/qa/evidence/2026-08-25-parallel-slice-executor-r14/lifecycle-and-abort.json`,
  `docs/qa/evidence/2026-08-25-parallel-slice-executor-r15/lifecycle-and-residue.json`,
  `docs/qa/evidence/2026-08-25-parallel-slice-executor-r17/verdict.json`.

Retained R14 prompt/user-takeover residue, R15/R17 live terminal residue, and older R8–R11
`identity_unproven` residue remain separate. No manual reset, force-delete, normal cleanup, or
broad cleanup was performed.

Canonical status: [`2026-08-25-parallel-slice-executor-final`](../reports/2026-08-25-parallel-slice-executor-final.md).

## v0.6.0 safe-mode retest reset

On 2026-08-25, the operator manually removed the historical pilot worktrees through Orca. This
operator-forced cleanup does not satisfy the normal-cleanup oracle and cannot close this bug. A
fresh fixture, lifecycle check, normal cleanup, repeated cleanup, and independent residue check are
pending in [`2026-08-25-parallel-slice-executor-v060-safe-retest`](../reports/2026-08-25-parallel-slice-executor-v060-safe-retest.md).

The fresh lifecycle checker returned `complete: false` and `lifecycle-incomplete` while the exact
A/T1 terminal remained live and writable. Normal cleanup and repeat cleanup were not attempted;
the fixture remains preserved. This confirms fail-closed behavior but leaves completed-pilot
automatic cleanup `blocked-verify`.
