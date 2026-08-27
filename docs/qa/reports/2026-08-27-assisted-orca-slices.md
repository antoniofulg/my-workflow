# Assisted Orca Slices QA — 2026-08-27

## Session

- **Charter:** [`CH-coordinate-assisted-orca-slices-2026-08-26`](../charters/CH-coordinate-assisted-orca-slices-2026-08-26.md)
- **Scenario:** `QAS-coordinate-assisted-orca-slices`
- **Persona:** Workflow operator
- **Adapter:** CLI/manual through installed Orca `1.4.190` direct worktree and terminal interfaces
- **Environment:** Feature checkout `31d21d2`; Orca repo `4d0d9503-7a68-4fa7-93fb-3b07cd6c0d7f`
- **Exact path:** bare Orca worktree creation → owned startup-shell promotion → rendered route proof
- **Frozen route:** `codex` / `gpt-5.6-luna` / `high`
- **Evidence:** `docs/qa/evidence/2026-08-27-assisted-orca-slices/session.md`
- **Recorded pre-execution gate:** independent Technical Verifier PASS at `4385b25`: focused `4/4`, full Vitest `112/112`, all 13 Python lanes, sensor `5/5` killed.
- **Final outer gate:** `npm_config_offline=true npm run test:all` exited `0`: Vitest `112/112`; all 13 Python test files exited `0`.
- **Limitation:** No automatic Orca canary was authorized or run. Assisted execution cannot establish automatic adapter compatibility.

## Scenario matrix

| Scenario | Charter leg | Expected | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- | --- |
| `QAS-coordinate-assisted-orca-slices` | E2E-001 / AST-01–AST-07 / SEC-008 | Two slices overlap through one exact parked/resumed B worker, integrate deterministically, and leave zero owned residue | **FAIL** at follow-up receipt/effect correlation | A_FINAL's same-handle send returned `agent_prompt_stalled`, but that handle silently executed A:T7/A:T8 and created two commits; coordinator could not safely continue | [`Retest 5`](../evidence/2026-08-27-assisted-orca-slices/retest-5/session.md); [`BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree`](../bugs/BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree.md) |
| Adjacent `QAS-qualify-orca-host-before-parallel-use` | No automatic canary | Assisted execution creates no compatibility evidence | **PASS** for this boundary; scenario status unchanged | No `preflight --canary` or compatibility receipt mutation occurred | `session.md` |
| Adjacent `QAS-clean-owned-parallel-slice-pilot` | Exact assisted ownership cleanup | Only receipt-owned fixture resources disappear | **PASS** for this run's setup cleanup; scenario status unchanged | Final prefix query found zero owned Orca/Git worktrees, refs, paths, or terminals | `session.md` |

## Fixture and execution ledger

| Item | Result |
| --- | --- |
| Ground | full id `4d0d9503-7a68-4fa7-93fb-3b07cd6c0d7f::/Users/antoniofulg/orca/workspaces/my-workflow/qa-assisted-20260827-ground`; instance `70f557fe-1cda-4cda-9142-bbc6837be194`; branch `feat/qa-assisted-20260827-ground`; seed `ed464c6`; baseline fixture gate `1/1` |
| Slice A receipt | full id `4d0d9503-7a68-4fa7-93fb-3b07cd6c0d7f::/Users/antoniofulg/orca/workspaces/my-workflow/qa-assisted-20260827-a`; instance `ce7f90de-6e13-495d-a864-acaff4a9ee2f`; branch `feat/qa-assisted-20260827-a`; `pre_head=ed464c6`; sole handle `term_0251a629-492a-4319-af1a-69896d241820` |
| A ownership proof | Exactly one newly created terminal for exact worktree; `lastOutputAt=null`, empty preview, writable shell, `agentWait=null`, no default-task or agent activity |
| A route promotion | Fixed argv sent 66-byte payload plus newline: `exec codex --model gpt-5.6-luna -c 'model_reasoning_effort="high"'`; Orca accepted 67 bytes |
| Route proof | **FAIL**: `terminal wait --for tui-idle` returned satisfied, then exact `terminal read --screen --json` returned `source=screen` with only shell prompt. Later `terminal show` exposed `gpt-5.6-luna high` only after `connected=false`, so it cannot satisfy AST-01 |
| Delayed duplicate setup | The first create invocation returned no receipt within its command session; after the clean retry, Orca later materialized exact owned worktree `qa-assisted-20260827-a-2`, instance `620e71f4-006d-4183-ba69-638949db6159`, branch `feat/qa-assisted-20260827-a-2`, handle `term_1c7a74ab-b9d4-447a-aab9-b7cd2d943410`. It was never promoted or prompted and was included in exact cleanup |
| Tasks | A:T1, A:T7, A:T8, B:T9, B:T12, B:T15: not started; zero task commits |
| B checkpoint | B was not created; no parked comment, producer sync, overlap, or follow-up |
| Per-slice Technical Verifiers | Not dispatched because no task or code-changing slice completed |
| Grouped Deep Review | Not dispatched because no slice implementation existed to integrate |
| Final fixture QA | Not run because AST-01 failed before product implementation |

## Timing

| Event | UTC |
| --- | --- |
| Ground created | `2026-08-27T04:19:24.470Z` |
| Main A created | `2026-08-27T04:22:32.613Z` |
| Delayed A-2 materialized | `2026-08-27T04:22:44.347Z` |
| Main A last route output | `2026-08-27T04:24:00.195Z` |

No slice task ran, so A/B execution windows and overlap seconds are not applicable.

## Cleanup and residue

- Main A and delayed A-2 were clean at `ed464c6`; no merge, rebase, cherry-pick, or revert was active.
- Their exact terminals were closed/disconnected; each worktree was detached at its recorded head;
  each exact branch was safely deleted with non-force `git branch --delete`; ref absence returned `1`.
- Ground was clean at seed `ed464c6`, detached, safely branch-deleted, and removed by complete Orca id.
- Every complete Orca id returned `removed: true`.
- Final structured prefix audit: owned Orca worktrees `[]`, owned terminals `[]`, owned branch refs
  `[]`, owned Git worktrees `[]`; both recorded A paths and the ground path were absent. Repository
  worktree count returned to `2`. Global terminal count changed `10 → 11` during concurrent unrelated
  activity; no terminal containing the owned prefix remained.
- No unrelated worktree, terminal, branch, source file, ignored artifact, or repo registration was removed.

## Debrief

**Verdict: FAIL.** The current startup-shell contract reached the exact promotion command, but
Orca's `tui-idle` signal preceded the required rendered-route screen. AST-01 correctly stopped the
lane before prompt delivery. `BUG-20260827-assisted-orca-tui-idle-before-route-proof` requires an
Implementer handoff and a fresh QA Execute retest. This result makes no automatic Orca compatibility
claim.

## Retest 1 — 2026-08-27T05:39:27Z

- **Fix commits:** `4858934`; `e062ca0`; `b821f87`
- **Adapter:** CLI/manual through installed Orca `1.4.190`
- **Exact repository:** `4d0d9503-7a68-4fa7-93fb-3b07cd6c0d7f`
- **Unique prefix:** `qa-assisted-20260827-r2`
- **Raw evidence:** `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-1/`
- **Preflight:** PASS — Orca ready; exact repo inventory contains only primary and feature
  worktrees; Git likewise contains exactly those two worktrees; source checkout clean at `b821f87`.
- **Status:** **INVALID / NOT EXERCISED** as scenario evidence.

### Invalidating boundary

The coordinator verified B's exact parked comment and synchronized A through `A:T8`, but sent the
B follow-up at `2026-08-27T05:52:48.545394Z` while B's preceding turn still rendered `Working`.
The input was visibly queued for delivery after the worker's next tool call. The prescribed flow
requires proof that B ended its parked turn before any follow-up. This historical ordering error
cannot be reclassified as a product result. Retest 1 therefore neither passes nor fails E2E-001,
does not close the route bug, and files no new product bug.

### Partial observations — not a verdict

| Item | Observed |
| --- | --- |
| Ground | One create invocation; missing immediate receipt reconciled after a full 60-second machine-only settle window to exact id suffix `qa-assisted-20260827-r2-ground`; seed `db6a9c4`; baseline gate 1/1. |
| A route | Exact handle `term_239199bb-b863-4cda-8cc5-44af39a20129`; frozen `exec` sent once; two consecutive connected `source=screen` frames contained Codex / `gpt-5.6-luna` / `high` before A:T1 prompt. |
| B route | Exact handle `term_2b062918-dc7f-4c6a-a84b-994a55b26984`; frozen `exec` sent once; two consecutive connected `source=screen` frames contained Codex / `gpt-5.6-luna` / `high` before B:T9 prompt. |
| A tasks | A:T1 `7573ac5`, gate 3/3; A:T7 `b19bc52`, gate 4/4; A:T8 `e4fc531`, gate 5/5. |
| B checkpoint | B:T9 `c4c2949`, gate 4/4; exact parked comment at `c4c2949867461ca2d59d8dfdae40ba940ea86547`. |
| Partial overlap | A and B follow-up/initial packets were accepted at `05:50:50.537598Z` and `05:50:50.537582Z`; A completed at `05:51:42Z`, so at least 51 seconds of task overlap was observed. It is not credited as a scenario pass. |
| Producer sync | `b19bc52` and `e4fc531` became ancestors of B; affected gate passed 6/6. |
| Queued effects | The prematurely queued follow-up later produced B:T12 `a35ca37` and B:T15 `29d5707`; fixture gate reached 10/10. These are cleanup inputs only, not readiness evidence. |
| Verifiers/review/final QA | Not dispatched. Retest invalidated before those readiness stages. |

### Cleanup

The queued effects finished cleanly and were fast-forwarded into the disposable ground only to
satisfy fail-closed cleanup ancestry. A, B, and ground were clean with no Git operation in progress.
Their exact handles were absent, each checkout was detached at its current head, each exact branch
was deleted with non-force `git branch --delete`, each ref was independently absent, and Orca
removed all three complete ids with `removed: true`.

The final machine-only late-effect audit ran for 60 seconds through 53 bounded samples and a final
deadline audit at `2026-08-27T05:58:07.895584Z`. It observed no matching late effect. Final owned
Orca worktrees, terminals, filesystem paths, branch refs, and Git worktrees were all `[]`; repository
worktree count returned to the two-resource baseline. Foreign resources were preserved.

Raw evidence: [`retest-1/`](../evidence/2026-08-27-assisted-orca-slices/retest-1/).

Prior FAIL evidence above remains unchanged.

## Retest 2 — 2026-08-27T06:05:44Z

- **Fix commits:** `4858934`; `e062ca0`; `b821f87`
- **Adapter:** CLI/manual through installed Orca `1.4.190`
- **Exact repository:** `4d0d9503-7a68-4fa7-93fb-3b07cd6c0d7f`
- **Unique prefix:** `qa-assisted-20260827-r3`
- **Raw evidence:** `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-2/`
- **Preflight:** PASS — Orca ready; exact repo and Git inventories each contained only primary and
  feature worktrees; source HEAD was `b821f87`.
- **Status:** **INVALID / NOT EXERCISED** as scenario evidence.

### Invalidating boundary

The corrected helper captured terminal stream cursor `16` before A:T1 input, then read only
post-send output at 250ms intervals. Its mandatory 60-second QA-harness deadline elapsed before the
final marker appeared. The same worker subsequently emitted the valid standalone marker
`TURN_DONE A_T1 head=d931de7c6dae4e3614ad4ade5db811c18b0cf79c` after its displayed 1m14s turn.
Because the deadline had already invalidated the attempt, the coordinator sent no further packet.

This is a harness limitation, not a product failure: neither the assisted contract nor the feature
promises that an implementation turn finishes within 60 seconds. Retest 2 therefore neither passes
nor fails E2E-001, files no new bug, and does not close the existing route-fix retest.

### Partial observations — not a verdict

| Item | Observed |
| --- | --- |
| Ground | One create; exact receipt; seed `3bc3ea5`; baseline gate 1/1. |
| A route | Handle `term_b16a9371-c7de-49af-a7fa-63ee17699790`; two consecutive connected exact route frames before input. |
| A:T1 | Packet accepted `2026-08-27T06:06:38.989967Z`; commit `d931de7`; gate 3/3; clean; marker arrived after helper deadline. |
| Unreached | B creation, overlap, parking, producer sync, same-handle B continuation, per-slice Verifiers, grouped Deep Review, final persona QA, and full fixture gate. |

### Cleanup

The late A:T1 commit was fast-forwarded into ground only for cleanup ancestry. Exact A and ground
handles were closed; both worktrees were detached at `d931de7`; both branches were deleted with
non-force `git branch --delete`; both refs were absent; both complete Orca ids returned
`removed: true`. A 60-second late-effect audit ran 97 samples plus a deadline audit at
`2026-08-27T06:12:55.899759Z` and found `[]` for owned worktrees, terminals, paths, refs, and Git
worktrees. Baseline returned to exactly two repository worktrees. Foreign resources were preserved.

Prior FAIL and Retest 1 history remain unchanged. Fresh Retest 3 must use a technical-event wait
long enough for ordinary task turns while retaining a bounded deadline and the marker + idle +
non-Working conjunction.

## Retest 3 — 2026-08-27T06:17:44Z

- **Fix commits:** `4858934`; `e062ca0`; `b821f87`
- **Adapter:** CLI/manual through installed Orca `1.4.190`
- **Exact repository:** `4d0d9503-7a68-4fa7-93fb-3b07cd6c0d7f`
- **Unique prefix:** `qa-assisted-20260827-r4`
- **Raw evidence:** `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-3/`
- **Preflight:** PASS — exact Orca/Git inventories each contained only primary and feature
  worktrees; source HEAD was `b821f87`.
- **Status:** **INVALID / NOT EXERCISED** as scenario evidence.

### Invalidating boundary

The corrected 300-second helper captured a pre-send cursor and polled only post-send output every
250ms. A:T1 completed at clean commit `78aab41` with gate 3/3 and the exact route remained ready.
However, the cursor adapter represented the rendered terminal content as escaped/nested data, so
its standalone-line regex never recognized the unique marker already visible inside the captured
value. The helper reached its deadline. Immediate exact-handle `show` and `source=screen` reads then
showed the valid marker and the worker ready for input.

This is a QA adapter mismatch, not evidence that the worker exceeded 300 seconds and not a product
defect. The causal barrier failed, so the coordinator correctly sent no follow-up and created no B
lane. Retest 3 therefore neither passes nor fails E2E-001 and files no new bug.

### Partial observations — not a verdict

| Item | Observed |
| --- | --- |
| Ground | One create; seed `8f6175e`; baseline gate 1/1. |
| A route | Same startup handle `term_0b7e16e1-b9f1-4bd6-912d-0708adb4a90c`; two consecutive connected exact `source=screen` route frames before input. |
| A:T1 | Commit `78aab41`; gate 3/3; clean; exact marker rendered; stream parser did not identify it as a standalone event. |
| Unreached | B creation, overlap, parking, producer sync, same-handle continuation, per-slice Verifiers, grouped Deep Review, final persona QA, and complete fixture integration. |

### Cleanup

A:T1 was fast-forwarded into ground only for cleanup ancestry. Exact A and ground handles were
absent after the turn / exact stop attempt; both worktrees were detached at `78aab41`; both branches
were deleted with non-force `git branch --delete`; both refs were absent; both complete Orca ids
returned `removed: true`.

The final machine-only audit ran 60 seconds through 95 samples plus its deadline audit at
`2026-08-27T06:26:22.626581Z`. It found `[]` for owned worktrees, terminals, paths, refs, and Git
worktrees. Repository worktree count returned to exactly two. Foreign resources were preserved.

Prior FAIL and Retests 1–2 remain unchanged. A fresh Retest 4 must decode the cursor API's structured
content before applying the standalone marker predicate; the product scenario remains untested.

## Retest 4 — 2026-08-27T06:33:34Z

- **Fix commits:** `4858934`; `e062ca0`; `b821f87`
- **Adapter:** CLI/manual through installed Orca `1.4.190`
- **Exact repository:** `4d0d9503-7a68-4fa7-93fb-3b07cd6c0d7f`
- **Unique prefix:** `qa-assisted-20260827-r5`
- **Raw evidence:** `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-4/`
- **Preflight:** PASS — exact Orca/Git inventories each contained only primary and feature
  worktrees; source HEAD was `b821f87`.
- **Status:** **INVALID / NOT EXERCISED** as scenario evidence.

### Invalidating boundary

The coordinator captured causal cursor `16` before A:T1 input. A:T1 then completed cleanly at
`155b4fe593f7882c7ec04859f9ede7374a3287e1`, passed 3/3 tests, and rendered the exact marker. Retest
4 inspected only `result.terminal.text`, but installed Orca returned the post-cursor stream under
`result.terminal.tail` as a JSON array and omitted `text`. The parser advanced through cursor `209`
while decoding empty values, then expired its 300-second deadline.

[`cursor-tail-sample.json`](../evidence/2026-08-27-assisted-orca-slices/retest-4/cursor-tail-sample.json)
records exact response keys, `text_present=false`, `tail_type=list`, `source=stream`, and the
post-cursor marker. This is another QA adapter mismatch, not product failure or worker timeout.
Retest 4 therefore neither passes nor fails E2E-001, files no new bug, and leaves the fixed route
bug's retest pending.

### Partial observations — not a verdict

| Item | Observed |
| --- | --- |
| Ground | One create; exact receipt; seed `04efdd1`; baseline gate 1/1. |
| A route | Handle `term_d0389798-c207-46ea-9a18-ebaff839d79f`; two consecutive connected exact route frames before input. |
| A:T1 | Commit `155b4fe`; gate 3/3; clean; exact marker rendered after causal cursor 16. |
| Unreached | B creation, overlap, parking, producer sync, same-handle continuation, per-slice Verifiers, grouped Deep Review, final persona QA, and complete fixture integration. |

### Cleanup

A:T1 was fast-forwarded into ground only for cleanup ancestry. Exact A and ground resources were
clean at `155b4fe`; A's worker was closed and the already absent ground terminal was independently
confirmed absent. Both worktrees were detached, both branches were deleted with non-force
`git branch --delete`, both refs were absent, and both complete Orca ids returned `removed: true`.

Final machine-only audit ran 78 samples across 60 seconds plus deadline audit and found `[]` for
owned worktrees, terminals, paths, refs, and Git worktrees. Repository worktree count returned to
exactly two. Foreign resources were preserved.

Prior FAIL and Retests 1–3 remain unchanged. A future fresh retest must recursively traverse the
cursor response's structured string/array values, including `tail`, before marker checks.

## Retest 5 — 2026-08-27T06:49:12Z

- **Fix commits:** `4858934`; `e062ca0`; `b821f87`
- **Adapter:** CLI/manual through installed Orca `1.4.190`
- **Exact repository:** `4d0d9503-7a68-4fa7-93fb-3b07cd6c0d7f`
- **Unique prefix:** `qa-assisted-20260827-r6`
- **Raw evidence:** `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-5/`
- **Preflight:** PASS — Orca ready; exact Orca/Git inventories each contained only primary and
  feature worktrees; source HEAD was `b821f87`.
- **Status:** **FAIL** at same-handle follow-up receipt/effect correlation.

### Valid progress before failure

| Item | Observed |
| --- | --- |
| Ground | One create; seed `ff91c3b`; baseline gate 1/1. |
| A route and T1 | Exact handle `term_78b69ea9-3496-4565-a1d9-77e8d579cd0a`; two consecutive connected exact route frames; A:T1 `94e6056`, gate 3/3, full rendered-screen barrier and ground integration. |
| B route and park | Exact handle `term_214ce460-eaac-4fb8-b7f3-69827d715867`; two exact route frames; B:T9 `87ab805`, gate 4/4; exact parked comment reconciled; marker plus second post-idle screen passed. |
| Overlap dispatch | A_FINAL and B_PARKED were issued back-to-back. B accepted at `06:52:25Z`; A's send returned the terminal error below. |

### Failing boundary

The exact A startup handle had completed A:T1, passed the full screen-marker barrier, remained the
sole connected route-matched worker, and received no early queued input. Its A_FINAL send returned
`agent_prompt_stalled`. No retry or replacement worker was started. The same handle nevertheless
executed the rejected packet, creating A:T7 `976dbc5` and A:T8 `4e07291` and rendering the requested
A_FINAL marker. The CLI receipt therefore contradicted the terminal and Git effects.

This is not an operator-ordering or parser failure. A coordinator cannot know whether a failed send
is effect-free, in progress, or complete, so it cannot safely synchronize A:T7 and resume B. The
symptom deduplicates to open
[`BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree`](../bugs/BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree.md).
The corrected startup-route defect independently passed for both workers and is now retest-passed.

### Unreached stages

B:T12/B:T15, exact A:T7 producer sync, B's same-handle continuation, per-slice Technical Verifiers,
grouped Deep Review, final persona QA, normal deterministic integration, and complete fixture gate
did not run. The coordinator stopped at the first ambiguous receipt as required.

### Cleanup

For exact cleanup ancestry, B first fast-forwarded into the disposable ground. The late A effect
then produced two expected task/test conflicts; a bounded serial cleanup reconciliation preserved
both intents and passed 6/6 fixture tests at `08f1ae7`. This does not count as successful feature
integration. Exact A/B/ground terminals were closed or already absent; all three clean checkouts
were detached; all exact branches were safely deleted with refs absent; all complete Orca ids
returned `removed: true`.

Final machine-only audit ran 60 seconds through 85 samples and found `[]` for matching Orca
worktrees, terminals, Git worktrees, paths, and refs. Repository worktree count returned to the
two-resource baseline. Foreign resources were preserved.

Closing outer gate after all durable QA mutations: `npm run test:all` exited `0`; Vitest passed
`112/112`, and every Python lane passed. `qa-skills.test.ts` passed `23/23`; spec, tasks, and state
validators reported 0 errors; `git diff --check` passed.

## Retest 6 — 2026-08-27T08:21:48Z

- **Source:** `d191025`
- **Adapter:** CLI/manual through installed Orca `1.4.190`
- **Unique prefix:** `qa-assisted-20260827-r7`
- **Worker route:** `codex` / `gpt-5.6-luna` / `low`
- **Raw evidence:** `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-6/`
- **Status:** **INVALID / NOT APPLICABLE** to the successful-parallel journey.

### Proven subpaths

A:T1 completed and integrated. A_FINAL and B_PARKED started 18 microseconds apart and overlapped
for 32.630 seconds. B parked cleanly after B:T9 at A:T7, the exact producer became its ancestor, its
affected gate passed 5/5, and the same Luna-low B handle completed B:T12 and B:T15. All six task
commits, gates, marker/HEAD/ancestry/path/status/comment checks, and max concurrency 2 were proven.

Fresh Technical Verifiers used distinct new `gpt-5.6-sol medium` sessions after implementer handles
ended. Both verifier sends returned `agent_prompt_stalled`; no resend or replacement occurred.
Same-handle bounded reconciliation accepted exactly one complete effect per verifier: A PASS at
`df0edd3`, sensor 3/3; B PASS at `39ceccb`, sensor 3/3. This passes the observed assisted
send-recovery subpath but makes no automatic compatibility claim.

### Invalidating boundary

Deterministic A-then-B integration produced a real content conflict in shared mutable
`pilot/tasks.md`. Contract correctly stopped rather than auto-resolving. Grouped Deep Review and
final CLI persona QA did not run; Retest 6 cannot close E2E-001. This is a fixture/applicability
limitation, not a new product defect. Fresh conflict-free Retest 7 remains required.

Cleanup-only ancestry reconciliation preserved both verified heads and passed 8/8; it is not
successful integration evidence. Exact A/B/ground terminals, branches, refs, paths, Git worktrees,
and Orca worktrees were removed. Final 60-second audit ran 99 samples with zero owned residue and
returned to the exact two-worktree baseline. Foreign resources were preserved.

Per coordinator direction, no new outer full gate and no durable commit ran after this invalid
fixture result; those remain for fresh Retest 7 close.

## Retest 7 — 2026-08-27T08:44:50Z

- **Source:** `d191025`
- **Adapter:** CLI/manual through installed Orca `1.4.190`
- **Unique prefix:** `qa-assisted-20260827-r8`
- **Worker route:** `codex` / `gpt-5.6-luna` / `low`
- **Raw evidence:** `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-7/`
- **Status:** **FAIL** at the worker task-integrity gate.

### Conflict-free seed and valid progress

The single versioned `pilot/tasks.md` kept Slice A lines 7–9 and Slice B lines 23–25, with 13
immutable context lines between the nearest mutable lines. A pre-launch three-line-context proof
produced exactly two independent hunks. Ground seed `fa3c552` passed 1/1.

A:T1 committed `a72eef1` and passed 4/4 before B opened. A_FINAL and B_PARKED sends occurred 56
microseconds apart at `08:47:55.391503Z` and `08:47:55.391447Z`; both effects ran concurrently until
A completed at `08:48:30.736536Z`, proving 35.345 seconds of overlap and max concurrency 2. A:T7
`92c61d0` and A:T8 `29e32d3` passed 6/6. B:T9 `44efd42` passed 6/6 and produced the exact clean
parked comment. Exact A:T7 was merged into B without conflict at `bf167fc`; producer ancestry and
the affected 7/7 gate passed. The same B handle received B_FINAL once. All four worker send receipts
were successful; no false-negative reconciliation or retry occurred.

### Failing boundary

B:T12 created `3014cc8 feat(pilot): add name validation`. During B:T15 the worker ran the canonical
gate, observed one failure, and nevertheless created `92fd6dd feat(pilot): add batch CLI`. It then
changed the CLI newline behavior and created the extra `e75f856 fix(pilot): preserve batch CLI
newline`; final gate passed 9/9. Marker, HEAD, ancestry, allowed paths, task checkboxes, clean state,
same handle, and final gate all matched, but commit count and subjects did not. Effect reconciliation
therefore stopped fail-closed. This is tracked by
`BUG-20260827-luna-low-worker-commits-before-green-gate`.

No per-slice Technical Verifier, grouped Deep Review, deterministic integration verdict, or final
CLI persona QA ran after the task-integrity failure. The run makes no automatic Orca compatibility
claim.

### Cleanup

Cleanup-only ancestry integrated A then B without conflict at `4500833` and passed 10/10; it is not
successful feature integration evidence. Exact A/B/ground terminals were already absent, all three
clean checkouts were detached, all exact branches were safely deleted, and all complete Orca ids
returned `removed: true`. The 60-second late-effect audit ran 65 samples and found `[]` for owned
worktrees, terminals, Git worktrees, paths, and refs. Orca and Git both returned to the exact two-
worktree baseline. Foreign resources were preserved.

Per coordinator direction, no outer full gate or durable commit ran after this FAIL. Accumulated QA
history remains uncommitted for the worker-route remediation and fresh retest.

## Retest 8 — 2026-08-27T09:06:16Z

- **Source:** `40f2d55`
- **Adapter:** CLI/manual through installed Orca `1.4.190`
- **Unique prefix:** `qa-assisted-20260827-r9`
- **Worker route:** `codex` / `gpt-5.6-luna` / `medium`
- **Raw evidence:** `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-8/`
- **Status:** **FAIL** at grouped Deep Review.

### Assisted flow and task integrity

The conflict-free seed retained Slice A lines 7–9 and Slice B lines 23–25 with 13 immutable lines
between them and two independent three-line-context hunks. Ground seed `16144e0` passed 1/1.

A:T1 `323e350` passed 3/3 and integrated before B opened. A_FINAL and B_PARKED were sent 8
microseconds apart at `09:09:03.702327Z` and `09:09:03.702335Z`; both ran until A completed at
`09:10:04.396181Z`, proving 60.694 seconds of overlap and maximum concurrency 2. A:T7 `68c84d5`
and A:T8 `c9670bc` passed 5/5. B:T9 `ee624da` passed 5/5 and recorded the exact parked comment.
Exact A:T7 sync produced `e3eb0c0` without conflict; producer ancestry and affected gate 6/6 passed.
The same B handle then produced B:T12 `46e6ea8` and B:T15 `9afbcfe`; final task gate passed 8/8.

All four worker sends returned success. Each of the six tasks had exactly one expected Conventional
Commit after a green gate, no extra commit, no amend, and only packet-allowed paths. This closes
`BUG-20260827-luna-low-worker-commits-before-green-gate` through fix `40f2d55`.

### Technical Verification and integration

Fresh distinct Sol-medium Verifiers authored only `pilot/validation-a.md` and
`pilot/validation-b.md`. Both sends returned `agent_prompt_stalled`; neither was resent or replaced.
Same-handle effect reconciliation proved one complete PASS each: A `b3c0e05`, sensor 3/3; B
`b1f8d55`, sensor 3/3. Deterministic A-then-B integration was conflict-free at `2051517`; intermediate
gate passed 5/5 and integrated fixture gate passed 9/9.

### Grouped Deep Review and terminal verdict

Actual full grouped Deep Review used fresh native deep-reviewers over
`16144e0..2051517`: two defect cohorts, two polish cohorts, and three sweeps. After one
contracts-sweep schema retry, all jobs validated and both lanes covered 216/216 selected hunk lines.
Verdict was `FIX_BEFORE_SHIP`: 0 Critical, 1 Major, 3 Minor, and 8 advisories. The sole Major found
that `python -m pilot.batch` removes a terminal newline from valid newline-delimited stdin.

Readiness stopped correctly. Final normal/batch/invalid/new-process/canary persona QA did not run.
The new defect is `BUG-20260827-assisted-pilot-batch-cli-drops-final-newline`. This does not reopen
the Luna-low worker-process bug and makes no automatic Orca compatibility claim.

### Cleanup

Verifier and review terminals were closed. A and B heads were ancestors of integrated ground;
all three checkouts were clean with no Git operation in progress. Each was detached at its exact
head, each exact branch was deleted non-force with ref absence proven, and each complete Orca id
returned `removed: true`. The final 60-second audit ran 63 samples and found zero owned Orca/Git
worktree, terminal, path, branch ref, or late effect. Orca returned to the exact two-worktree
baseline; foreign resources were preserved.

### Closing repository gates

- `npm_config_offline=true npm run test:all`: **FAIL**, Vitest 111/112; IT-005 still expected
  implementer effort `low` while the frozen route is `medium`. Python lanes did not start after the
  Vitest failure.
- `npm_config_offline=true npm test -- --run tools/shared/tests/qa-skills.test.ts`: PASS, 23/23.
- Spec/tasks/state validators: PASS, 0 errors and 0 warnings.
- `git diff --check`: PASS.

The route/test mismatch is tracked separately as
`BUG-20260827-medium-route-contract-test-still-expects-low`. Both open Major defects require an
Implementer and a fresh QA Verifier; this session changed no product or contract-test code.

## Retest 9 — 2026-08-27T14:48:33Z

- **Source:** `83954ec`
- **Adapter:** CLI/manual through installed Orca `1.4.190`
- **Unique prefix:** `qa-assisted-20260827-r10`
- **Worker route:** `codex` / `gpt-5.6-luna` / `medium`
- **Raw evidence:** `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-9/`
- **Status:** **invalid / not exercised** — external provider capacity exhausted at the first worker turn.

### Reachable setup

`before_inventory` recorded 2 repository worktrees and 8 terminals before the single mutating
create. Ground was created once at `pre_head=83954ec`, seeded conflict-free at `d0b91ca`, and passed
the fixture gate `1/1`. The pre-launch hunk proof produced two independent three-line-context hunks
with 13 immutable lines between Slice A lines 7–9 and Slice B lines 23–25.

Slice A was created once at `pre_head=d0b91ca` with sole startup handle
`term_47676ffb-0511-4908-9640-7f0edd748dec`; its `new`/`sole`/`unused` ownership proof passed. The
rendered route proof was ACCEPTED at sample 3 with two consecutive `source=screen` frames showing
`OpenAI Codex` and `gpt-5.6-luna medium`, with `gpt-5.6-luna low` and `gpt-5.6-luna high` both
absent. This re-confirms AST-01 on the current contract.

### Blocking boundary

The `A_T1` packet was sent exactly once and Orca returned `ok=true`, but the Codex agent rendered
`You've hit your usage limit ... try again at Sep 1st, 2026 11:14 AM` instead of starting the turn.
Effect reconciliation ran 538 samples to its 300 s deadline at `marker-count=0`. The packet was not
resent, no replacement worker was launched, and no second terminal was opened. Independent
inspection proved zero effect: both checkouts clean at `d0b91ca`, all six task checkboxes `pending`,
zero commits.

Slice B was never created, so no overlap window, producer sync, same-handle continuation, Technical
Verifier, integration, grouped Deep Review, newline fix loop, final CLI persona QA, or fixture full
gate ran. Maximum concurrency was 1.

This is an external provider-capacity limitation, not a product or contract defect, and it creates
no new bug. Because the account quota resets on its own, the scenario keeps Retest 8's terminal
`fail` on the still-open newline Major rather than becoming `blocked-verify`.

### Cleanup

Pre-cleanup revalidation passed 11/11 for both owned worktrees. Terminals were stopped and listed
empty, each checkout was detached at its exact `current_head` `d0b91ca`, each exact branch was
deleted with non-force `git branch --delete`, `git show-ref --verify --quiet` returned `1` for both,
and both complete Orca ids returned `removed: true`. The 60-second audit ran **91 samples** with
`[]` for owned worktrees, terminals, Git worktrees, paths, and refs. Orca and Git returned to the
exact two-worktree baseline; foreign resources were preserved.

### Closing repository gates

- `npm_config_offline=true npm run test:all`: **PASS**, exit `0`; Vitest `112/112` across 8 files;
  all Python lanes `OK`. This closes `BUG-20260827-medium-route-contract-test-still-expects-low`
  through fix `395a691`.

`BUG-20260827-assisted-pilot-batch-cli-drops-final-newline` remains open and unretested. No
automatic Orca compatibility claim is made and no `preflight --canary` ran.
