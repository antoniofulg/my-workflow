# CH-execute-parallel-slices-2026-08-24

- **Date:** 2026-08-24
- **Time-box:** 45 minutes
- **Persona:** Workflow operator
- **Journey:** [`J-execute-parallel-slices`](../journeys/J-execute-parallel-slices.md)
- **Tour:** Real Orca concurrency, receipts, restart, and owned-cleanup tour
- **Public entry point:** `tools/qa_parallel_pilot.py setup|dry-run` → `parallel_execute.py start|status|resume` → `lifecycle-check|cleanup`
- **Declared adapter:** CLI/manual with Orca `orchestration.contract.v1`
- **Scenarios:** `QAS-run-resource-free-parallel-orca-slices`, `QAS-clean-owned-parallel-slice-pilot`
- **Adjacent canary:** `CFG-fallback-unproven-parallel-execution` and `CFG-plan-parallel-slice-dispatch`

## Mission

Use the feature's disposable two-lane fixture and the real Orca adapter to prove that two
`Resources: none` slices are active concurrently in distinct worktrees and terminals, converge
through correlated lifecycle receipts, and are cleaned only after the canonical oracle accepts
their terminal state.

## Expected observable

Dry-run identifies the exact source HEAD and two resource-free lanes; both lanes become active with
distinct owned identities; public status/resume records two correlated terminal
read-before-ack-before-release lifecycles; cleanup removes only those owned workers and worktrees,
preserves an unrelated sibling canary, and leaves no owned residue.

## Planned probes

- Create the fixture through its public setup command and retain the exact root for evidence.
- Require dry-run equality between frozen source and repository HEAD plus exactly two ready lanes.
- Start with `--adapter auto`; stop as untested if Orca capability is absent or the result serializes.
- Capture redacted run, worktree, branch, dispatch, terminal, delivery, acknowledgement, and release identities.
- Observe both lanes active before accepting terminal results; never infer verification from `worker_done`.
- Use only bounded public status/resume calls and the canonical lifecycle checker.
- Preserve an unrelated sibling through cleanup; repeat cleanup to confirm bounded idempotency.
- Inspect `git worktree list`, executor status, and checkout residue after cleanup.

No runtime, port, or database isolation claim is permitted. A product defect returns to an
Implementer; this session records it and stops before remediation.

## Terminal outcome

`QAS-run-resource-free-parallel-orca-slices` and `QAS-clean-owned-parallel-slice-pilot` are
`blocked-verify` at the external Orca/Codex boundary. Orca `1.4.188` revoked the failed Dispatch
after `agent_prompt_stalled`; Codex `0.149.1` later completed externally, while replayed
`worker-stop` returned `alreadySettled` and left the exact owned terminal live/writable. Product
correctly refused release, retry, and cleanup. R14 user-takeover residue and older
`identity_unproven` residue remain separate; no cleanup claim exists. See the
[terminal report](../reports/2026-08-25-parallel-slice-executor-final.md).
