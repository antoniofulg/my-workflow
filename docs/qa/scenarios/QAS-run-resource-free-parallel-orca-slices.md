---
id: QAS-run-resource-free-parallel-orca-slices
area: QAS
title: Run two resource-free Orca slices concurrently
persona: Workflow operator
journey: J-execute-parallel-slices
expected: Two resource-free slices become active in distinct owned worktrees and terminals, then finish through correlated read, acknowledgement, release, and status receipts without changing TLC task or verification order.
entry_points: tools/orca_assisted_probe.py dispatch|inspect|cleanup; tools/qa_parallel_pilot.py; .agents/skills/autonomous/scripts/parallel_execute.py start; .agents/skills/autonomous/scripts/parallel_execute.py status; .agents/skills/autonomous/scripts/parallel_execute.py resume
qa_status: blocked-verify
bug_ids: BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree
fix_status: fixed
retest_status: pending
fix_commits: f7a1f36; 1216014; 6b3f1f0; 2fb2f41; 8675c6d; 6419d24; 453a8ab; 941bbc5; e24228c; 35a49bf; a1a49a2; 1e40171; f02b679; 5b7a9dd; 48e5322; a736757; 0ed8b55
evidence: docs/qa/evidence/2026-08-25-parallel-slice-executor-v060-safe-retest/pilot-identities.md; docs/qa/reports/2026-08-25-parallel-slice-executor-v060-safe-retest.md
last_report: docs/qa/reports/2026-08-25-parallel-slice-executor-v060-safe-retest.md
overlaps: CFG-plan-parallel-slice-dispatch
---

Covers the public E2E-001 resource-free path and observable portions of EXE-02, EXE-04,
EXE-06–EXE-10, EXE-18, and EXE-22. The independent live walk must use the real Orca capability and
public executor commands; a serial fallback or missing terminal receipt is not a pass.

This scenario is terminal `blocked-verify`, not `pass`, `fail`, or `untested`. Offline fake-provider
probe and adoption checks do not convert this live-host status. The limitation is the upstream
Orca/Codex transport boundary. Product-side parsing,
identity, terminal-ownership, recovery, and provider-preflight fixes are independently recorded by
the fix commits above. The remaining live walk is blocked at an external Orca/Codex boundary.

R14 recorded the separate user-takeover/prompt residue: Orca `1.4.188` stopped at
`agent_prompt_blocked` while the Codex terminal showed `codex-update-prompt`; diagnostic cleanup
refused with `worker-may-be-live`. R15 observed Orca `agent_prompt_stalled` and a live, writable
Codex `0.149.1` terminal after the Dispatch was revoked. The later Codex completion is external
runtime behavior, not a product success receipt. R17 issued the exact public recovery-stop; Orca
replied `alreadySettled: true` for the failed Dispatch and left the exact owned terminal
live/writable. A replay made no progress, so the product correctly refuses release, retry, and
cleanup. No lifecycle receipt, two-lane completion, or cleanup claim exists.

The older R8–R11 `identity_unproven` fixture and its retained resource remain separate historical
residue. None of these retained fixtures may be treated as cleanup evidence.

Historical evidence remains in the R8, R9, R10, R11, R12, R14, R15, R16, and R17 reports/evidence;
the terminal consolidation is [`2026-08-25-parallel-slice-executor-final`](../reports/2026-08-25-parallel-slice-executor-final.md).

The operator manually removed the retained historical pilot worktrees before the v0.6.0 safe-mode
retest. That operator-forced cleanup reset physical state only; it is not evidence for worker
lifecycle completion or automatic cleanup. The fresh run reproduced the external boundary: Orca
failed A/T1 at `agent_prompt_stalled` while the exact terminal remained live, connected, and
writable; B/T2 never started. Product fallback exposed and fenced the effect. This scenario remains
`blocked-verify` with `retest_status: pending` until a fresh run completes both lanes.
