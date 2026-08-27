---
id: QAS-coordinate-assisted-orca-slices
area: QAS
title: Coordinate two assisted Orca slices through a parked dependency
persona: Workflow operator
journey: J-execute-parallel-slices
expected: With explicit authorization, two assisted Orca slices overlap through one exact parked and resumed B worker, preserve every readiness stage, integrate deterministically, and leave no owned worktree, path, branch ref, or terminal residue.
entry_points: .agents/skills/autonomous/references/parallelization.md; .specs/features/host-agnostic-slice-parallelization/workflow.json; orca worktree; orca terminal
qa_status: fail
bug_ids: BUG-20260827-assisted-orca-tui-idle-before-route-proof; BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree
fix_status: pending
retest_status:
fix_commits: 4858934; e062ca0; b821f87
evidence: docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-5/session.md
last_report: docs/qa/reports/2026-08-27-assisted-orca-slices.md
overlaps: QAS-run-resource-free-parallel-orca-slices; QAS-clean-owned-parallel-slice-pilot; QAS-qualify-orca-host-before-parallel-use
---

Covers E2E-001, AST-01 through AST-07, and the user-observable ownership and cleanup outcome of
SEC-008. The canonical pilot uses the frozen implementer route `codex` / `gpt-5.6-luna` / `high`,
starts B only after `A:T1` completes and verifies, and parks it at the exact later dependency
`B:T12 depends_on A:T7`.

Assisted execution is a distinct explicitly authorized path. It never writes a compatibility PASS
and cannot establish automatic support without a separately authorized, durable candidate canary.
A pass requires rendered `source=screen` route proof before prompt delivery, one
worker per ready slice, a clean exact parked comment, producer-commit sync, the affected gate,
same-terminal follow-up, deterministic integration, preserved TLC readiness stages, and independent
absence checks for every owned worktree, path, branch ref, and terminal.

The 2026-08-26 assisted walk is retained as historical pre-remediation evidence: both clean,
out-of-contract attempts to create a separate frozen-route terminal timed out, so no rendered route
proof or worker handle existed. The owned setup worktree was cleanly removed with zero slice residue;
the attempt did not exercise the current startup-shell promotion contract. See the [historical QA
report](../reports/2026-08-26-assisted-orca-slices.md) and [reclassified bug
record](../bugs/BUG-20260826-assisted-orca-terminal-create-timeout.md).

The 2026-08-27 current-contract retest failed before prompt delivery. Orca accepted the exact frozen
`exec` payload and reported `tui-idle`, but the immediate `source=screen` read still showed the
startup shell instead of the required route tuple. A later handle inspection showed the requested
route only after the handle had disconnected. See the [current report](../reports/2026-08-27-assisted-orca-slices.md)
and [`BUG-20260827-assisted-orca-tui-idle-before-route-proof`](../bugs/BUG-20260827-assisted-orca-tui-idle-before-route-proof.md).

Retest 1 started at `2026-08-27T05:39:27Z` against fixes `4858934`, `e062ca0`, and `b821f87`.
It is invalid/not exercised as scenario evidence: the coordinator queued B's follow-up while B's
prior turn still reported `Working`, before proving the required end-turn boundary. The route fix
and full scenario retest remain pending. Exact cleanup passed with zero owned residue.

Retest 2 started at `2026-08-27T06:05:44Z` and is also invalid/not exercised. A's exact route and
A:T1 succeeded, but the QA helper's 60-second turn deadline elapsed before the valid final marker
arrived at the worker's reported 1m14s boundary. No follow-up or B effect occurred. This harness
limitation created no product bug. Exact cleanup and a 60-second late-effect audit left zero owned
residue; the scenario remains `untested` with the fixed route bug's retest still pending.

Retest 3 started at `2026-08-27T06:17:44Z` with the corrected 300-second turn window. A's exact
route and A:T1 succeeded at clean commit `78aab41`, but the cursor adapter exposed the rendered
marker as escaped/nested data rather than a standalone stream line. Its predicate timed out even
though immediate exact-handle screen inspection showed the unique marker and a ready worker. This
QA adapter mismatch is invalid/not exercised, creates no product bug, and leaves the scenario
`untested`. Exact cleanup and the final 60-second audit returned to the two-worktree baseline with
zero owned residue.

Retest 4 started at `2026-08-27T06:33:34Z` and is invalid/not exercised. A's route and A:T1 again
succeeded at clean commit `155b4fe` with gate 3/3 and an exact post-cursor marker. The helper read
only `result.terminal.text`, while Orca `1.4.190` omitted that key and returned the structured stream
as a `result.terminal.tail` array. Its 300-second deadline therefore expired without recognizing the
already rendered event. No follow-up or B effect occurred. This harness mismatch creates no product
bug; the scenario stays `untested` and the fixed route bug remains retest-pending. Exact cleanup and
a 60-second 78-sample audit returned to the two-worktree baseline with zero owned residue.

Retest 5 started at `2026-08-27T06:49:12Z` and is the current terminal verdict. Both A and B proved
the corrected rendered route, A:T1 completed and integrated, and B:T9 parked with its exact clean
comment. During intentional overlap, A_FINAL's exact same-handle send returned
`agent_prompt_stalled`, yet that handle silently executed A:T7/A:T8 and created two commits. The
receipt therefore contradicted the observed effect, so the coordinator could not safely correlate
or continue to producer sync and B follow-up. The scenario is `fail`, deduplicated to the existing
external lifecycle bug. Exact cleanup and a 60-second 85-sample audit returned to two worktrees with
zero owned residue.
