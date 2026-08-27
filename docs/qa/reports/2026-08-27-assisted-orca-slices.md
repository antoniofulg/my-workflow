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

## Retest 10 — 2026-08-27T15:19:33Z

- **Source:** `30e828b`
- **Adapter:** CLI/manual through installed Orca direct worktree and terminal interfaces
- **Unique prefix:** `qa-assisted-20260827-r11` (collision-checked against Orca and Git before the first create; both `0`)
- **Worker route:** `claude` / `sonnet` / `low` (frozen `workflow.json`, all four roles moved off the exhausted Codex quota)
- **Raw evidence:** `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-10/`
- **Status:** **FAIL** — new Critical transport defect, `BUG-20260827-orca-terminal-send-truncates-claude-worker-packet`.

### Route proof rewritten for the Claude provider — PASS

The retest-8/9 matcher targeted Codex TUI text and is wrong for this snapshot. Per the packet, the
ground worktree was created first, its startup shell promoted with
`exec claude --model sonnet --effort low`, and the rendering read empirically over 42 samples
(`retest-10/route-discover.jsonl`) before any slice worktree existed.

Claude Code renders all three required facts on the rendered `source=screen` frame —
`Claude Code v2.1.247` and `Sonnet 5 with low effort · Claude Max`. **Effort is directly observable
on this provider, so no proof was weakened.** The retest-10 matcher requires `Claude Code`,
`Sonnet 5` and `with low effort` on two consecutive connected `source=screen` frames, with
`with medium effort` and `with high effort` both absent. Slice A accepted at sample 4; Slice B
accepted at sample 4. AST-01 is re-confirmed on a second provider.

### Reachable setup

`before_inventory` was snapshotted before each of the three single mutating creates. Ground was
created once at `pre_head=30e828b`, seeded conflict-free at `a86a9dd`, and passed the fixture gate
`Ran 1 test … OK`. `hunk-proof.json` reproduced retest 8's layout byte for byte: two independent
hunks `@@ -4,9 +4,9 @@` and `@@ -20,8 +20,8 @@`, `unified_context=3`, 13 immutable context lines
between Slice A lines 7–9 and Slice B lines 23–25, `status=PASS`.

Slice A was created once at `pre_head=a86a9dd`; ownership `new`/`sole`/`unused` passed. The `A_T1`
packet (1225 chars) was sent exactly once with `ok=true` and reconciled **complete and
packet-exact**: head `61302ad`, one commit `feat(pilot): add basic name normalization`, changed
paths inside the allowlist, `A:T1` complete, scoped gate green, clean tree, same handle, agreeing
second frame. Only then was Slice B created at `pre_head=61302ad` and routed. Both workers ran
concurrently.

### Blocking boundary — the receipt reports a write the agent never receives

`A_FINAL` (1354 chars) and `B_PARKED` (1677 chars) were each sent exactly once with `ok=true`. Both
failed closed.

`A_FINAL` reconciled a complete, unambiguous, **non-conforming** effect: `commit_count`,
`commit_subjects` and `tasks` all false with zero commits and a marker head equal to `pre_head`,
while `clean`, `gate`, `head`, `descends`, `paths`, `idle`, `second_frame`, `same_handle` and
`comment` were all true. The rendered transcript starts mid-word at
`n end your turn with exactly one final standalone marker line …` — the worker received only the
packet's tail and answered that fragment alone.

`B_PARKED` produced no effect across **297** samples to the 300 s deadline. Its worker stated the
cause unprompted: *"This message got cut off / garbled — I only see a fragment ending
mid-instruction … Can you resend the full message?"*

Neither packet was resent, no replacement worker was launched, and no second terminal was opened for
either slice.

A bounded characterization probe on the **ground** shell (a coordinator-owned non-slice terminal, so
no slice lane's one-send rule was touched) quantified it: a 2081-character payload of position
markers returned `{"ok": true, "accepted": true, "bytesWritten": 2082}` while the agent received
**36 of 2081 characters**. Loss is timing-dependent rather than a fixed cap — 39 chars and 1225
chars arrived intact, 1354 and 1677 did not, 2081 lost 98.3 %. `orca terminal send --help` exposes
no chunking, paste or stdin mode, so `--text` is the only expressible transport.

This is Critical against the assisted contract: exactly one send per packet is mandated, retry after
a success receipt is forbidden, and a replacement worker is forbidden — so a silent truncation that
still reports success burns the lane irrecoverably.

### Task-integrity watch on the sonnet/low route

The one packet that was delivered intact was honoured exactly: green gate before the commit, one
atomic commit, packet-exact subject, allowlisted paths, clean tree. No gate-before-commit or
extra-commit violation was observed on this route. The two rejected turns were rejected for
non-delivery, not for worker misbehaviour, so retest 7's low-effort failure mode is **not**
reproduced and also **not** cleared — one delivered packet is not enough evidence either way.

### Stages that did not run

Slice B parking, the exact `A:T7` producer sync, the affected gate, same-handle continuation,
per-slice Technical Verifiers, deterministic A-then-B integration, grouped Deep Review, the newline
fix loop, final CLI persona QA, and the fixture full gate.

### Timing

- Overlap window: `2026-08-27T15:26:05.657381Z` → `2026-08-27T15:26:23.258715Z`
- Overlap duration: **17.601 s**
- Maximum concurrency: **2**

### Cleanup

Pre-cleanup revalidation passed **11/11** for all three owned worktrees. Terminals were stopped
(`rc 0`, `connected: false`, ground `[]`), each checkout was detached at its exact `current_head`
with the head unchanged, each exact branch was deleted with non-force `git branch --delete` at
`rc 0`, `git show-ref --verify --quiet` failed for all three proving ref absence, and all three
complete Orca ids returned `removed: true` with the path absent. The 60-second audit ran
**93 samples** with `[]` for owned worktrees, terminals, Git worktrees, paths, and refs.
`git worktree list` returned the exact two-worktree baseline. Foreign resources were preserved and
nothing foreign was adopted or cleaned.

### Closing repository gates

- `npm_config_offline=true npm run test:all` on the final tree: **PASS**, exit `0`; Vitest
  `112/112` across 8 files; all Python lanes `OK`.
- Fixture full gate: **not run** — no integrated fixture ever existed.

`BUG-20260827-assisted-pilot-batch-cli-drops-final-newline` remains open and unretested for the
second consecutive cycle: the fixture it lives in only exists inside a completed pilot run. No
automatic Orca compatibility claim is made and no `preflight --canary` ran.

## Retest 11 — aborted by human direction, 2026-08-27

- **Source:** `94ab954`; prefix `qa-assisted-20260827-r12` (collision-checked to `0` before any create)
- **Adapter:** CLI/manual through the installed Orca direct worktree and terminal interfaces
- **Routes (frozen `workflow.json`, schema v2):** implementer `claude`/`sonnet`/`low`; verifier
  `claude`/`sonnet`/`medium`; deep_reviewer `claude`/`sonnet`/`high`; cadence `grouped.3`
- **Window:** `2026-08-27T16:39:44.389708Z` → `2026-08-27T17:38:33.882863Z`
- **Evidence:** [`retest-11/session.md`](../evidence/2026-08-27-assisted-orca-slices/retest-11/session.md)

### Disposition

**Invalid / not exercised — no verdict.** Mid-run the human directed that the frozen implementer
effort be raised from `sonnet`/`low` to `sonnet`/`medium`. `workflow.json` is being re-frozen and
Retest 12 will walk the new route, so this walk's observations belong to a route that no longer
exists and cannot close the scenario. The abort is a direction, not a failure. This run creates no
bug, changes no bug record, and leaves `QAS-coordinate-assisted-orca-slices` at `qa_status:
untested`. No compatibility PASS was written and no `preflight --canary` ran.

The abort arrived after the walk and its full cleanup lifecycle had already completed, so no worker
turn was in flight and nothing had to be torn down mid-turn.

### Findings that survive the route change

**Pointer packet delivery works, measured.** On the ground worktree's promoted startup shell — a
coordinator-owned non-slice terminal, so no slice lane's one-send rule was spent — before any slice
worktree existed:

| Fact | Value |
| --- | --- |
| Packet body written to the coordinator-owned file, outside every slice worktree | **2418 chars** |
| What crossed `orca terminal send` | the **188-char** pointer only |
| Receipt | `ok: true`, `accepted: true`, `bytesWritten: 189` |
| Worker action / reply | `Read 1 file` → `TRANSPORT_PROOF token=TRPF-e4c160800f5b3157 first=P000 last=P299` |
| Samples to delivery | 2 |

The embedded random token plus the first and last positional filler markers all returned, so the
**complete** body reached the worker, read from a path outside its own worktree. The body exceeds
both packets Retest 10 lost (1354, 1677) and is comparable to its 2081-char payload that lost 98.3 %.
Every later packet matched: bodies of 1226, 1355, 1678 and 1635 chars plus three review packets, all
delivered as 177-185 char pointers, one send each, all honoured packet-exactly — including `A_FINAL`
and `B_PARKED`, the two packets Retest 10 lost. This does not fix the host; it shows no loss occurs
at ~180 characters.

**Sonnet-low task integrity was clean while observed.** All four task packets honoured
packet-exactly: six task commits, packet-exact subjects and counts, changed paths inside every
allowlist, a green gate before every commit, a clean tree after every turn, **zero corrective commits
and zero amends**. Retest 7's low-effort violation did not recur. One clean observation of the route
the effort raise supersedes — not a durable verdict, which is why it closes nothing.

### What ran before the abort

Rendered route proof on 6/6 terminals; conflict-free seed at `2bd1e76` with the byte-identical
2-hunk / 13-immutable-line layout; 159.487 s A/B overlap at concurrency 2; exact B parking with the
normative comment; exact `A:T7` sync `fb7217b` conflict-free with the affected gate 7/7; same-handle
B continuation; fresh per-slice Technical Verifiers PASS on their own terminals; conflict-free
deterministic A-then-B integration at `0e2fd5b` with the fixture gate `12/12`; grouped Deep Review
`SHIP` (0 Critical, 0 Major, 1 Minor, 5 advisories, 265/265 hunk lines both lanes) read back from
the generated artifacts; final CLI persona QA 10/10 edge probes.

### Coordinator error, recorded so it is not repeated

Slice A's first `orca worktree create` exceeded the harness's 15 s client timeout and the probe
crashed inside its own SETTLE WINDOW; the command was then re-run to read its stderr, issuing the
second create the contract forbids. Both landed. Neither was ever routed or sent a packet, and both
were cleaned exactly with ownership reconstructed from the first attempt's logged `before` inventory
(10/10 checks each). Slice A was then created once under the fresh name `…-r12-a3`. The harness now
survives a transient failure inside the settle window and tolerates concurrent read-only Orca
inspections; `create`, `send`, `rm`, `set` and `stop` are never retried. Harness fault, not a product
defect.

### Cleanup on abort — the full lifecycle, no shortcut

Revalidation passed **13/13** for all three owned worktrees: Orca repo/id/instance/path/branch,
gitdir, no symlink, clean, no operation in progress, branch tip equals `current_head`, recorded
handles only, startup handle present, and `git merge-base --is-ancestor <slice-head> 0e2fd5b` for A
and B. Terminals stopped at `rc 0`; each checkout detached at its exact `current_head` unchanged;
each exact branch deleted with non-force `git branch --delete` at `rc 0`;
`git show-ref --verify --quiet` failed for all three, proving ref absence; all three complete Orca
ids removed with the path absent. Plus the two erroneous `-a` worktrees, cleaned the same way.

60-second sampled audit: **65 samples**, zero residue in every sample and at the deadline —
`{"worktrees": [], "terminals": [], "git": [], "refs": [], "paths": [], "pilot_residue": []}`,
`repo_worktrees: 2`. Re-verified live after the abort: `git worktree list` → the exact two
repository worktrees; `orca worktree list` → `2`; `git branch --list '*r12*'` → `0`;
`ls -d ~/Projects/.parallel-slice-pilot-*` → no matches. Nothing foreign was adopted or cleaned.

### Gates

- Fixture full gate on the integrated tree `0e2fd5b`, clean:
  `python3 -m unittest discover -s pilot/tests -p 'test_*.py'` → `Ran 12 tests … OK`, exit `0`.
- Outer full gate on the abort commit's tree, clean working tree:
  `npm_config_offline=true npm run test:all` → exit `0`; Vitest `Test Files 8 passed (8)`,
  `Tests 112 passed (112)`; all Python lanes passed (`9`, `5`, `67`, `53`, `18`, `14`, `6`, `44`
  passed with `0 failed`). Log: `/tmp/r12-abort-gate.log`.

## Retest 12 — 2026-08-27T18:08:00Z — **PASS**

- **Source:** `b6bdcad` (`feat/host-agnostic-slice-parallelization`)
- **Adapter:** CLI/manual through installed Orca `1.4.190` direct worktree and terminal interfaces
- **Exact repository:** `4d0d9503-7a68-4fa7-93fb-3b07cd6c0d7f`
- **Unique prefix:** `qa-assisted-20260827-r13` (Retest 11 consumed `r12`); collision check before
  any create returned `0` for Orca worktrees, Git branches, and terminals
- **Frozen route:** implementer `claude`/`sonnet`/**`medium`**, verifier `claude`/`sonnet`/`medium`,
  deep_reviewer `claude`/`sonnet`/`high`, cadence `grouped.3`, groups `[[1,2],[3,4]]`. Nothing ran
  on Codex.
- **Raw evidence:** `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-12/`
- **Duration:** `18:08:00.260486Z` → `18:55:25.707676Z`, **2845.447 s** (47 min 25 s)

### Verdict

**PASS.** Every stage of the assisted E2E completed with evidence: pointer transport proof, rendered
medium-route proof on all six terminals, one create per slice, four packet-exact worker turns,
58.536 s of A/B overlap at concurrency 2, exact parking, exact producer sync with the affected gate,
same-handle continuation, fresh per-slice Technical Verifiers, conflict-free deterministic
integration, grouped Deep Review `SHIP` with zero open Critical or Major, final persona QA 10/10,
fixture full gate `12/12`, and exact cleanup returning the two-worktree baseline with zero residue.

### Scenario matrix

| Scenario | Charter leg | Expected | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- | --- |
| `QAS-coordinate-assisted-orca-slices` | E2E-001 / AST-01–AST-07 / SEC-008 | Two slices overlap through one exact parked/resumed B worker, integrate deterministically, leave zero owned residue | **PASS** | Deep Review verdict read back from generated artifacts, not the agent's claim; canonical suite re-run by the coordinator on `07540bc` (`Ran 12 tests … OK`); cleanup audited over 39 samples plus independent `git`/`orca` baseline queries | `retest-12/session.md` |
| Adjacent `QAS-qualify-orca-host-before-parallel-use` | No automatic canary | Assisted execution creates no compatibility evidence | **PASS** for this boundary; status unchanged | No `preflight --canary` ran; `workflow.json` keeps `parallelization.mode: disabled` | `retest-12/session.md` |
| Adjacent `QAS-clean-owned-parallel-slice-pilot` | Exact assisted ownership cleanup | Only receipt-owned resources disappear | **PASS** for this run; status unchanged | 13/13 revalidation each, 39-sample audit clean, two foreign artifacts explicitly left untouched | `retest-12/cleanup.jsonl`, `retest-12/cleanup-audit.jsonl` |

### Coordinator fault — a second `orca worktree create`

Recorded prominently because it is the rule that invalidated Retest 11. Retest 11's probe dispatches
its subcommand at module scope with no `__name__` guard, so importing it to inherit its hardening
executed the `create`, and this run's own dispatcher executed it again — two creates ~3 s apart for
the ground worktree's logical name. The harness was fixed before any further Orca call and the fix
was **proved with a fake `orca` on `PATH`** (exactly 1 `worktree create` across 421 recorded calls)
before being trusted. Both erroneous worktrees were cleaned exactly, 10/10 reconstructed ownership
each, and ground was recreated once as `…-r13-ground3`.

The ground stage therefore does not certify the one-create rule. Slices A and B do, and it is
checkable: `create_result=1` in each of `ground-create.jsonl`, `a-create.jsonl`, `b-create.jsonl`.

Two smaller coordinator observations are recorded in `session.md` §7 and §9: a permission dialog on
Slice B's verifier that the coordinator declined (the keystroke was read as an interrupt, ending that
turn cleanly with no partial commit, and one same-handle follow-up completed it unchanged), and the
`deep-review` skill's `disable-model-invocation` guard, which the review agent correctly refused to
work around and which the coordinator satisfied with the explicit slash invocation.

### Execution ledger

| Item | Result |
| --- | --- |
| Ground | `…-r13-ground3`, branch `feat/…-r13-ground3`, `pre_head=b6bdcad`; seed `d9d3921`, fixture gate `Ran 1 test … OK` |
| Hunk proof | 2 independent hunks, 13 immutable context lines, `status=PASS` — byte-identical to retests 8, 10, 11 |
| Slice A | `…-r13-a`, `pre_head=d9d3921`, sole handle `term_3d4b64b7-…`, ownership `new`/`sole`/`unused` all true |
| Slice B | `…-r13-b`, `pre_head=d42d2ce`, created only after `A:T1` reconciled 12/12, sole handle `term_0993c20f-…` |
| Route proof | `Claude Code v2.1.247` + `Sonnet 5 with medium effort · Claude Max` on two consecutive `source=screen` frames, other two efforts absent, on all six terminals |
| Packets | 8 logical packets, bodies 1226-2077 chars, all delivered as 177-190 char pointers, **one send each**, all `ok=true`, all honoured |
| Task commits | **6**, packet-exact subjects and counts, green gate before every commit, zero corrective commits, zero amends |
| Overlap | `18:16:52.510990Z` → `18:17:51.046586Z`, **58.536 s**, max concurrency **2** |
| Parked comment | exact: `slice=B; state=parked; completed_through=B:T9; next=B:T12; blocked_on=A:T7; head=6835d9e…` |
| Producer sync | exact `A:T7` `2c1b1ab` merged into B, no conflict, affected gate `Ran 7 tests … OK`, synced head `7331235` |
| Continuation | `B_FINAL` on the same handle, no reacquisition, no dual-send, no replacement worker |
| Technical Verifiers | fresh agents on their own terminals, author ≠ verifier, both 10/10, `verdict=PASS` |
| Integration | A fast-forward, B `ort` merge with no conflict, head `07540bc`, both slice heads ancestors, all six checkboxes `[x]` |

### Sonnet-medium task integrity

Retest 7 failed because a low-effort worker committed over a red gate and added a corrective commit;
Retest 11 saw the low route clean but is `invalid / not exercised`. This run is the first observation
of the **medium** route across all four task packets:

- `A_T1` → 1 commit `feat(pilot): add basic name normalization` (`d42d2ce`), gate `4 tests OK`
- `A_FINAL` → 2 commits `feat(pilot): normalize apostrophes` (`2c1b1ab`), `feat(pilot): normalize ordered lines` (`196d82d`), gate `6 tests OK`
- `B_PARKED` → 1 commit `feat(pilot): add batch normalization` (`6835d9e`), gate `6 tests OK`
- `B_FINAL` → 2 commits `feat(pilot): add name validation` (`2a11198`), `feat(pilot): add batch CLI` (`6db92f3`), gate `11 tests OK`

All twelve reconciliation checks true on every turn. Six task commits, packet-exact, green gate
before every commit, allowlisted paths, clean tree after every turn, zero corrective commits, zero
amends. Retest 7's failure mode did not recur.

### Grouped Deep Review — SHIP

Frozen `deep_reviewer` route `sonnet`/`high`, canonical skill with its native fresh `deep-reviewer`
subagents at bounded concurrency 3, `--full`, no publish, scope `d9d3921…..07540bc…`. Verdict read
back from `state.json` / `review-stats.json` / `findings.json`, not from the agent:

| Fact | Value |
| --- | --- |
| Rounds | 1 |
| Verdict | **SHIP** |
| Critical / Major | **0 / 0** |
| Minor (defects) | 3, all open, none blocking a journey |
| Advisories | 6 |
| Candidates / reported / suppressed | 17 / 9 / 8 |
| Hunk coverage | defect 359/359 complete; polish 359/359 complete |
| Rule accounting | R01–R14 all accounted |
| Duration | 18 m 59 s |

Under `REVIEW-ROUNDS.md` only a `Blocker` or `Major` triggers a round, so round 2 was not required
and no fix loop ran. The three Minors are fixture-local: a missing case-sensitivity test for
`is_normalized`, and two accuracy gaps in `pilot/validation-b.md`. The fixture is disposable and was
destroyed at cleanup, so they are recorded here rather than filed.

### The expected newline Major did not reproduce — established independently

`BUG-20260827-assisted-pilot-batch-cli-drops-final-newline` was filed against Retest 8's fixture.
`pilot/` is regenerated by the workers every run, so that artifact no longer exists. Retest 11
reached the same conclusion but is `invalid / not exercised`, so this run re-derived it from scratch
on a copy proven byte-identical to the reviewed tree:

- `printf 'Ada Lovelace\nGrace Hopper\n' | python3 -m pilot.batch` → `b'ada-lovelace\ngrace-hopper\n'`,
  ends with a newline. `pilot/batch.py:15-17` prints one record at a time and never writes a bare
  `"\n".join(...)`, which is the recorded root cause.
- The required focused subprocess assertion exists: `pilot/tests/test_batch.py:34-43`.
- That assertion **discriminates**: injecting the exact recorded symptom into the copy gives
  `b'ada-lovelace\ngrace-hopper'` and `Ran 12 tests … FAILED (failures=1)`; restoring gives `OK`.
- Grouped Deep Review over the same tree returned zero open Major.

Both halves of the required fix are satisfied. **No remediation batch was manufactured.**

### Host transport defect — measured, still open

One bounded characterization on the ground (non-slice) shell: a **2012-char** inline payload,
`ok=true`, `bytesWritten: 2013`, worker replied `TRUNC first=Q000 last=Q339 total=340` — the complete
payload, no loss. Retest 10's comparable 2081-char payload lost 98.3 %.

This does **not** clear `BUG-20260827-orca-terminal-send-truncates-claude-worker-packet`. The loss is
timing-dependent by the record's own description; one clean sample no more disproves an intermittent
defect than one dirty sample proves it, nothing in Orca changed, and `orca terminal send --text`
still exposes no acknowledgement mode. The bug stays open; this run did not reproduce it and, under
AD-016, never depended on the answer.

### Final CLI persona QA — persona Workflow operator

Charter tour walked in full. Ten edge probes against a copy byte-identical to `07540bc`, all exit `0`
with zero stderr bytes: newline-terminated and unterminated stdin, empty stdin, an interior blank
line, collapsed whitespace, ASCII apostrophes, CRLF, a Unicode curly apostrophe, a single unterminated
line, and 500 records. Lenses comprehension / recovery / trust / speed all pass; accessibility and
language are not applicable to a plain stdout token stream.

One recorded observation, not a defect: this run's worker filters interior blank lines
(`pilot/batch.py:7`) and covers that with `test_skips_blank_lines`, where Retest 11's independently
written fixture preserved them. The fixture task specifies neither, so both conform.

### Cleanup and residue

Pre-cleanup revalidation **13/13** on each of the three owned worktrees. Terminals stopped `rc 0`
with zero terminals remaining; each checkout detached at its exact `current_head` unchanged; each
exact branch deleted with non-force `git branch --delete` `rc 0`; `git show-ref --verify --quiet`
failed for all three, proving ref absence; all three complete Orca ids removed with paths absent.
Plus the two erroneous ground worktrees, cleaned the same way.

60-second sampled audit: **39 samples**, zero residue in every sample and at the deadline,
`repo_worktrees: 2`, `git_worktrees: 2`, `observed_dirty_samples: 0`. Independent confirmation:
`git worktree list` → exactly 2; `orca worktree list --repo id:4d0d9503-…` → `2`;
`git branch -a | grep -c r13` → `0`; owned terminals `0`; no `qa-assisted-*` workspace path;
no `~/Projects/.parallel-slice-pilot-*`.

Two pre-existing foreign artifacts were identified and deliberately left untouched: the empty
`~/orca/workspaces/my-workflow/src/main` tree, and Orca repo `fcea29fd-…` registered at
`docs/qa/evidence/2026-08-26-assisted-orca-slices/fixture-integration`.

### Gates

- Fixture full gate on the final integrated tree `07540bc`:
  `python3 -m unittest discover -s pilot/tests -p 'test_*.py'` → `Ran 12 tests … OK`, exit `0`.
- Outer full gate on the final tree `a777a9f`, clean working tree:
  `npm_config_offline=true npm run test:all` → exit `0`; Vitest `Test Files 8 passed (8)`,
  `Tests 112 passed (112)`; all Python lanes `0 failed` (`9`, `5`, `67`, `53`, `18`, `14`, `6`,
  `44` passed). Log: `/tmp/r13-final-gate-committed.log`.
- Structural gate: `python3 .agents/skills/tlc-spec-driven/scripts/validate_state.py
  host-agnostic-slice-parallelization` → `0 error(s)`, exit `0`.

### Bug dispositions after this cycle

| Bug | Disposition |
| --- | --- |
| `BUG-20260827-assisted-pilot-batch-cli-drops-final-newline` | **closed** — re-derived from scratch, not inherited; symptom absent, required assertion present and proven discriminating |
| `BUG-20260827-orca-terminal-send-truncates-claude-worker-packet` | **open** against the host — AD-016 route-around retested and passed; the host defect is unfixed and did not reproduce in one characterization, which clears nothing |
| `BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree` | **open** against the automatic executor; not reachable through the assisted path, untouched by this cycle |
