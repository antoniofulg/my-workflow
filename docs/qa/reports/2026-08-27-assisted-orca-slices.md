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
| `QAS-coordinate-assisted-orca-slices` | E2E-001 / AST-01–AST-07 / SEC-008 | Two slices overlap through one exact parked/resumed B worker, integrate deterministically, and leave zero owned residue | **FAIL** at AST-01 route proof | `tui-idle` returned true, but the immediate `source=screen` read contained only the shell; later exact-handle inspection showed the requested route after disconnect | [`session.md`](../evidence/2026-08-27-assisted-orca-slices/session.md); [`BUG-20260827-assisted-orca-tui-idle-before-route-proof`](../bugs/BUG-20260827-assisted-orca-tui-idle-before-route-proof.md) |
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
