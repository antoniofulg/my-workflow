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
