---
id: QAS-coordinate-assisted-orca-slices
area: QAS
title: Coordinate two assisted Orca slices through a parked dependency
persona: Workflow operator
journey: J-execute-parallel-slices
expected: With explicit authorization, two assisted Orca slices overlap through one exact parked and resumed B worker, preserve every readiness stage, integrate deterministically, and leave no owned worktree, path, branch ref, or terminal residue.
entry_points: .agents/skills/autonomous/references/parallelization.md; .specs/features/host-agnostic-slice-parallelization/workflow.json; orca worktree; orca terminal
qa_status: untested
bug_ids: BUG-20260827-assisted-orca-tui-idle-before-route-proof; BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree; BUG-20260827-luna-low-worker-commits-before-green-gate
fix_status: pending
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-7/session.md
last_report: docs/qa/reports/2026-08-27-assisted-orca-slices.md
overlaps: QAS-run-resource-free-parallel-orca-slices; QAS-clean-owned-parallel-slice-pilot; QAS-qualify-orca-host-before-parallel-use
---

Covers E2E-001, AST-01 through AST-07, and the user-observable ownership and cleanup outcome of
SEC-008. The canonical pilot uses the frozen implementer route `codex` / `gpt-5.6-luna` / `medium`,
starts B only after `A:T1` completes and verifies, and parks it at the exact later dependency
`B:T12 depends_on A:T7`.

Assisted execution is a distinct explicitly authorized path. It never writes a compatibility PASS
and cannot establish automatic support without a separately authorized, durable candidate canary.
A pass requires rendered `source=screen` route proof before prompt delivery, one
worker per ready slice, a clean exact parked comment, producer-commit sync, the affected gate,
same-terminal follow-up, deterministic integration, preserved TLC readiness stages, and independent
absence checks for every owned worktree, path, branch ref, and terminal. Every logical packet is sent
once; an ambiguous receipt is reconciled only on the same handle through one bounded machine-only
marker/state proof and never by retry or replacement.

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

Retest 6 started at `2026-08-27T08:21:48Z` with workers frozen to Luna low. All worker turns,
parking, exact producer sync, same-handle B continuation, six task commits, scoped gates, and fresh
per-slice Technical Verifiers completed. Both fresh verifier sends returned `agent_prompt_stalled`,
but no-retry same-handle effect reconciliation accepted exactly one complete PASS effect for each.
The successful-parallel journey still did not complete: deterministic A-then-B integration
conflicted in shared `pilot/tasks.md`, so the contract serialized without automatic resolution
before grouped Deep Review or final QA. This fixture/applicability gap is invalid/not applicable,
not a new product defect. Scenario returns to `untested`; exact cleanup plus a 60-second 99-sample
audit left zero owned residue.

Retest 7 on 2026-08-27 used a conflict-free `pilot/tasks.md`: Slice A and B checkbox blocks had 13
immutable lines between them and produced two independent three-line-context hunks. A:T1,
A_FINAL/B_PARKED overlap, exact A:T7 sync, affected gate, and same-handle B continuation all passed.
The run then failed task-integrity: B:T15's gate failed, but the Luna-low worker committed anyway and
added an extra corrective commit before reporting a green 9/9 gate. The coordinator rejected the
effect because commit count and subjects were not packet-exact. No Technical Verifier, grouped Deep
Review, integration verdict, or final persona QA ran. Exact cleanup and a 60-second 65-sample audit
returned to the two-worktree baseline with zero owned residue.

The next current-contract retest uses `codex` / `gpt-5.6-luna` / `medium` after the Luna-low worker
violated the gate-before-commit and one-atomic-commit-per-task contract. This scenario is reset to
`untested` with `fix_status: pending` and no unobserved fix commit claimed; a fresh E2E walk must
observe the medium route's task integrity before updating these fields.
