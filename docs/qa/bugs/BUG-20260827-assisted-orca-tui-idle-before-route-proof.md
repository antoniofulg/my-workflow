# BUG-20260827-assisted-orca-tui-idle-before-route-proof

- **Status:** open
- **Severity:** major
- **Scenario:** `QAS-coordinate-assisted-orca-slices`
- **Expected:** After the exact owned startup shell receives the frozen `exec codex` route and
  `terminal wait --for tui-idle` succeeds, the immediate `terminal read --screen --json` exposes
  `source=screen` with `codex` / `gpt-5.6-luna` / `high` before any task prompt.
- **Observed:** Orca accepted the complete payload and returned `tui-idle: satisfied`, but the
  immediate screen contained only the startup shell prompt. A later exact-handle inspection exposed
  `gpt-5.6-luna high` only after the terminal had disconnected. No task prompt or task edit occurred.
- **Adapter:** Installed Orca `1.4.190` direct CLI/manual worktree and terminal interfaces
- **Exact path:** bare `orca worktree create` → one exact unused startup handle → fixed-argv
  `terminal send` of frozen `exec` payload → `terminal wait --for tui-idle` → exact
  `terminal read --screen --json`
- **Evidence:** `docs/qa/evidence/2026-08-27-assisted-orca-slices/session.md`

## Impact

The coordinator cannot distinguish "agent route rendered and idle" from "startup shell idle before
agent render" using the prescribed single wait/read sequence. AST-01 must fail closed, so A:T1 never
starts and no inter-slice overlap can be exercised.

The run also observed one delayed duplicate setup worktree from a create invocation that returned no
receipt before a clean retry. Both exact resources were discovered and removed. That observation is
recorded for lifecycle diagnosis but is not needed to reproduce the route-proof blocker.

## Retest

Pending Implementer remediation. A fresh QA Execute Verifier must repeat the affected journey plus
the zero-residue adjacent canary. No automatic `preflight --canary` is implied or authorized.
