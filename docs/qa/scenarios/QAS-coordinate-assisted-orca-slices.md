---
id: QAS-coordinate-assisted-orca-slices
area: QAS
title: Coordinate two assisted Orca slices through a parked dependency
persona: Workflow operator
journey: J-execute-parallel-slices
expected: With explicit authorization, two assisted Orca slices overlap through one exact parked and resumed B worker, preserve every readiness stage, integrate deterministically, and leave no owned worktree, path, branch ref, or terminal residue.
entry_points: .agents/skills/autonomous/references/parallelization.md; .specs/features/host-agnostic-slice-parallelization/workflow.json; orca worktree; orca terminal
qa_status: untested
bug_ids: BUG-20260827-assisted-orca-tui-idle-before-route-proof; BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree; BUG-20260827-luna-low-worker-commits-before-green-gate; BUG-20260827-assisted-pilot-batch-cli-drops-final-newline; BUG-20260827-medium-route-contract-test-still-expects-low; BUG-20260827-orca-terminal-send-truncates-claude-worker-packet
fix_status: pending
retest_status: fail
fix_commits: 40f2d55; 395a691
evidence: docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-8/session.md; docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-8/deep-review-result.md; docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-10/session.md
last_report: docs/qa/reports/2026-08-27-assisted-orca-slices.md
overlaps: QAS-run-resource-free-parallel-orca-slices; QAS-clean-owned-parallel-slice-pilot; QAS-qualify-orca-host-before-parallel-use
---

Covers E2E-001, AST-01 through AST-07, and the user-observable ownership and cleanup outcome of
SEC-008. The canonical pilot uses the frozen implementer route `claude` / `sonnet` / `low`,
starts B only after `A:T1` completes and verifies, and parks it at the exact later dependency
`B:T12 depends_on A:T7`.

Assisted execution is a distinct explicitly authorized path. It never writes a compatibility PASS
and cannot establish automatic support without a separately authorized, durable candidate canary.
A pass requires rendered `source=screen` route proof before prompt delivery, one
worker per ready slice, a clean exact parked comment, producer-commit sync, the affected gate,
same-terminal follow-up, deterministic integration, preserved TLC readiness stages, and independent
absence checks for every owned worktree, path, branch ref, and terminal. Every logical packet body is
written to a coordinator-owned file outside every slice worktree and delivered as a short fixed-shape
pointer through exactly one send; an ambiguous receipt is reconciled only on the same handle through
one bounded machine-only marker/state proof and never by retry or replacement.

The pointer-delivery contract has never been walked: every retest through Retest 10 exercised the
superseded inline-payload transport, so this scenario is reset to `untested` and Retest 11 must
walk the pointer contract end to end.

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

Retest 8 proved the Luna-medium route's task integrity, 60.694 seconds of A/B overlap, exact B
parking, exact A:T7 sync, affected gate, same-handle continuation, fresh per-slice Technical
Verifiers, and conflict-free deterministic A-then-B integration. Grouped Deep Review then returned
`FIX_BEFORE_SHIP` with one open Major because the mini CLI removes a terminal newline. Final persona
QA did not run. The scenario is `fail` on that new defect; exact cleanup and a 60-second 63-sample
audit returned to the exact two-worktree baseline with zero owned residue.

The closing outer full gate also failed IT-005 because the canonical test still asserts Luna low
after fix `40f2d55` froze Luna medium. QA skills and structural validators remained green. This is a
separate tracked defect and keeps the feature tree unready.

Retest 9 started at `2026-08-27T14:48:33Z` against `83954ec` with prefix `qa-assisted-20260827-r10`.
It is invalid/not exercised. Ground and Slice A were each created once, the conflict-free seed
`d0b91ca` passed 1/1 with two independent hunks and 13 immutable context lines, A's ownership proof
passed, and A's rendered `source=screen` route again proved `gpt-5.6-luna medium` while rejecting
low and high. The single `A_T1` send then returned `ok=true` but the Codex agent reported an
exhausted account quota resetting on Sep 1st, so the turn never started; 538 effect samples reached
the 300-second deadline at zero marker, nothing was resent, and both checkouts stayed clean at the
seed with zero commits. Slice B, overlap, producer sync, Technical Verification, integration, the
resumed grouped Deep Review, the newline fix loop, and final persona QA did not run. This external
capacity gap closes on its own and creates no bug, so the scenario keeps Retest 8's `fail` on the
still-open newline Major. Exact cleanup revalidated 11/11, deleted both branches non-force with ref
absence proven, removed both complete Orca ids, and a 60-second 91-sample audit returned to the
exact two-worktree baseline with zero owned residue. The closing outer full gate
`npm_config_offline=true npm run test:all` exited `0` with Vitest `112/112`, closing
`BUG-20260827-medium-route-contract-test-still-expects-low` through `395a691`.

The next current-contract retest uses `claude` / `sonnet` / `low` after the Codex account exhausted
its weekly plan limit during Retest 9. The human explicitly scoped the move to the implementer role;
`verifier` and `deep_reviewer` stay on Codex, so a retest run before that quota restores is expected
to halt at Technical Verification or grouped Deep Review rather than at the first worker turn. The
route is refreshed in the feature snapshot with `--override implementer=claude`; cadence
`grouped.3` and its `[[1,2],[3,4]]` groups are unchanged. Retest 7 already failed task integrity
with a low-effort worker, so the next walk must observe gate-before-commit and one-atomic-commit-per-task
on this route before any field is updated.

Retest 10 started at `2026-08-27T15:19:33Z` against `30e828b` with prefix `qa-assisted-20260827-r11`
and the refreshed all-Claude snapshot, worker route `claude` / `sonnet` / `low`. The Codex-shaped
route matcher was replaced: the ground worktree's startup shell was promoted first and its rendering
read empirically before any slice existed. Claude Code renders provider, model and effort together
(`Claude Code v2.1.247`, `Sonnet 5 with low effort · Claude Max`), so the two-consecutive-frame
`source=screen` proof holds unweakened on this provider and both slices accepted it at sample 4.
Ground seeded conflict-free at `a86a9dd` with the identical two-hunk, 13-immutable-line layout, and
the single `A_T1` packet was delivered intact and honoured exactly: green gate before the commit,
one atomic packet-exact commit at `61302ad`, allowlisted paths, clean tree. Slice B then started on
that verified head and both workers ran concurrently for 17.601 seconds at concurrency 2.

The walk then failed on a new Critical transport defect. `A_FINAL` and `B_PARKED` were each sent
once with `ok=true`, and the Claude Code TUI received only a mangled tail fragment of each: `A_FINAL`
reconciled a complete zero-work effect that was rejected on commit count, subjects and task status,
and `B_PARKED` reached its 300 s deadline at `marker-count=0`. Neither was resent and no replacement
worker or second terminal was created. A bounded characterization probe on the coordinator's
non-slice ground shell measured the loss: `bytesWritten` 2082 with `ok=true`, 36 of 2081 characters
received. Because the contract mandates one send with no retry and no replacement worker, a
truncation that reports success burns the lane irrecoverably. The scenario is `fail` on
[`BUG-20260827-orca-terminal-send-truncates-claude-worker-packet`](../bugs/BUG-20260827-orca-terminal-send-truncates-claude-worker-packet.md);
the still-open newline Major was unreachable for the second consecutive cycle. Exact cleanup
revalidated 11/11 on all three owned worktrees, deleted all three branches non-force with ref
absence proven, removed all three complete Orca ids, and a 60-second 93-sample audit returned to the
exact two-worktree baseline with zero owned residue. The closing outer full gate
`npm_config_offline=true npm run test:all` exited `0` with Vitest `112/112`.
