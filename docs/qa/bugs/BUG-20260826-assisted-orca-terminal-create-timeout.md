# BUG-20260826-assisted-orca-terminal-create-timeout

- **Status:** closed — historical out-of-contract attempt; no current product defect established
- **Severity:** major
- **Scenario:** `QAS-coordinate-assisted-orca-slices`
- **Expected:** The current assisted contract promotes the exact `startupTerminal.handle` returned by
  `orca worktree create`; it does not create a second terminal.
- **Observed:** Two clean attempts returned `runtime_error: Timed out waiting for terminal handle after creation`. Re-listing the exact worktree after the first attempt showed only the original unused shell and no agent terminal. No prompt or task edit occurred.
- **Adapter:** Installed Orca `1.4.190` direct CLI/manual worktree and terminal interfaces
- **Historical exact path:** `orca worktree create` → immutable Git/Orca receipt → out-of-contract
  `orca terminal create` with the frozen route → exact-worktree `orca terminal list`
- **Evidence:** `docs/qa/evidence/2026-08-26-assisted-orca-slices/session.md`

## Boundary

This historical attempt occurred before the startup-shell promotion contract was adopted. It failed
before rendered route proof, prompt delivery, task execution, overlap, parking, checkpoint
synchronization, integration, or final lifecycle validation; it is not evidence that the current
assisted contract fails. A fresh QA walk must exercise the exact startup handle promotion. The
automatic adapter remains `candidate` / `canary-required`; this record creates no compatibility PASS
and does not rerun its canary.

Exact owned setup cleanup removed the created slice worktree and branch and independently proved
slice path, terminal, branch-ref, and Orca slice-worktree absence. The ignored integration ground
remains only as checkout-local raw evidence.
