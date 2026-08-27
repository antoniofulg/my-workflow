# BUG-20260826-assisted-orca-terminal-create-timeout

- **Status:** open
- **Severity:** major
- **Scenario:** `QAS-coordinate-assisted-orca-slices`
- **Expected:** After an owned worktree is created, direct `orca terminal create --worktree <full-id> --command <frozen-route> --json` returns the sole worker handle so rendered `source=screen` route proof can precede prompt delivery.
- **Observed:** Two clean attempts returned `runtime_error: Timed out waiting for terminal handle after creation`. Re-listing the exact worktree after the first attempt showed only the original unused shell and no agent terminal. No prompt or task edit occurred.
- **Adapter:** Installed Orca `1.4.190` direct CLI/manual worktree and terminal interfaces
- **Exact path:** `orca worktree create` → immutable Git/Orca receipt → `orca terminal create` with `codex --model gpt-5.6-luna -c 'model_reasoning_effort="high"'` → exact-worktree `orca terminal list`
- **Evidence:** `docs/qa/evidence/2026-08-26-assisted-orca-slices/session.md`

## Boundary

The failure occurs before rendered route proof, prompt delivery, task execution, overlap, parking,
checkpoint synchronization, integration, or final lifecycle validation. The assisted contract
therefore fails closed as required by AST-01. The automatic adapter remains `candidate` /
`canary-required`; this result creates no compatibility PASS and does not rerun its canary.

Exact owned setup cleanup removed the created slice worktree and branch and independently proved
slice path, terminal, branch-ref, and Orca slice-worktree absence. The ignored integration ground
remains only as checkout-local raw evidence.
