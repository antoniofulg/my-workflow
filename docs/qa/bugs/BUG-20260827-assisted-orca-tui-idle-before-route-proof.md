# BUG-20260827-assisted-orca-tui-idle-before-route-proof

- **Status:** fixed — retest passed
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

Implementer fixes `4858934`, `e062ca0`, and `b821f87` still await a valid retest. Retest 1, started
at `2026-08-27T05:39:27Z`, was invalidated by coordinator sequencing after both rendered routes had
materialized: B's follow-up was queued before its prior turn was proven ended. This does not pass or
fail the product fix and created no new product bug. Exact cleanup left zero owned residue. No
automatic `preflight --canary` is implied or authorized.

Retest 2 at `2026-08-27T06:05:44Z` proved A's corrected two-frame rendered route before task input,
but did not produce a valid product retest: the QA helper's 60-second worker-turn deadline expired
before A:T1's valid marker arrived after a reported 1m14s. No new product bug was filed. Status stays
fixed / retest pending until a complete fresh E2E walk closes the whole affected journey.

Retest 3 at `2026-08-27T06:17:44Z` again proved the corrected route and completed A:T1 at clean
commit `78aab41` with gate 3/3. Its 300-second cursor helper failed to decode escaped/nested rendered
TUI content before testing the standalone marker, while immediate exact-handle screen inspection
showed the valid marker and ready worker. This is an invalid QA adapter attempt, not a product
defect or worker-timeout result. Status remains fixed / retest pending; exact cleanup left zero
owned residue.

Retest 4 at `2026-08-27T06:33:34Z` proved the corrected route and completed A:T1 at clean commit
`155b4fe` with gate 3/3. The causal cursor response omitted `result.terminal.text` and exposed its
structured stream through `result.terminal.tail` as a JSON array. The helper read only the missing
field and timed out despite the exact marker in that post-cursor array. This is an invalid QA
adapter attempt, creates no product bug, and leaves this bug fixed / retest pending. Exact cleanup
plus a 60-second 78-sample audit returned to the two-worktree baseline with zero owned residue.

Retest 5 at `2026-08-27T06:49:12Z` passed this bug's affected route boundary independently for both
A and B: each same startup handle remained connected and produced two consecutive exact rendered
`source=screen` route frames before its first task packet. The full scenario later failed at the
separate deduplicated `agent_prompt_stalled` receipt/effect contradiction tracked by
`BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree`; that does not reopen this
route-materialization defect.
