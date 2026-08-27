# Assisted Orca Slices QA — 2026-08-26

## Session

- **Charter:** [`CH-coordinate-assisted-orca-slices-2026-08-26`](../charters/CH-coordinate-assisted-orca-slices-2026-08-26.md)
- **Scenario:** `QAS-coordinate-assisted-orca-slices`
- **Persona:** Workflow operator
- **Adapter:** CLI/manual through installed Orca direct worktree and terminal interfaces
- **Environment:** Feature checkout `55fdbc6`; Orca `1.4.190`; ignored checkout-local Git fixture at base `16fdb64`
- **Exact path:** `orca worktree create` → `orca terminal create` → rendered screen proof → direct terminal prompts/follow-up → Git integration → ownership-checked Orca cleanup
- **Frozen route:** `codex` / `gpt-5.6-luna` / `high`, from the feature `workflow.json`
- **Evidence:** `docs/qa/evidence/2026-08-26-assisted-orca-slices/`
- **Recorded pre-execution gate:** PASS at `d28cbf1`: Vitest `112/112` and all Python lanes passed.
- **Final gate:** PASS at cycle close: `npm_config_offline=true npm run test:all` exited `0` with Vitest `112/112` and all package-discovered Python lanes passing; strict spec/tasks validators, state validator, and `git diff --check` also passed.
- **Limitations:** No product server/browser/API/mobile surface exists. No automatic `preflight --canary` is authorized. The recorded `1.4.190` automatic-canary failure is inspected read-only and cannot become a compatibility PASS through this assisted walk.

## Scenario matrix

| Scenario | Charter leg | Expected | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- | --- |
| `QAS-coordinate-assisted-orca-slices` | E2E-001 / AST-01–AST-07 / SEC-008 | Two slices overlap through one exact parked/resumed B worker, integrate deterministically, and leave zero owned residue | fail | Two direct terminal-create attempts failed before route proof or prompt; exact setup residue is zero | `session.md`; `BUG-20260826-assisted-orca-terminal-create-timeout` |
| Adjacent `QAS-qualify-orca-host-before-parallel-use` | Recorded automatic-canary state, read-only | Automatic execution remains unsupported and no PASS receipt is written | pass for inspected boundary; scenario status unchanged | Read-only public preflight returned `candidate`, `canary-required`, `cached=false`, `cleanup=not-run`; no canary ran | `session.md` |
| Adjacent `QAS-clean-owned-parallel-slice-pilot` | Assisted ownership cleanup only | Exact assisted resources are removed without changing the automatic-cleanup scenario | pass for setup cleanup; scenario status unchanged | Full-id slice worktree removal plus independent Git/path/ref/terminal checks | `session.md` |

## Checkpoint and task ledger

| Item | Result |
| --- | --- |
| Fixture base | `16fdb64a34f95965f5778d0c566da78717fe14e4` |
| Slice A immutable receipt | repo `fcea29fd-5864-4f36-9733-55b85537852c`; instance `e918bc9a-fdca-4ba6-a432-262a51f9e1ff`; full id and path recorded in raw evidence; branch `feat/qa-assisted-a-20260826`; `pre_head=16fdb64` |
| Slice A worker | not created; both direct terminal-create attempts timed out |
| A:T1 through A:T7 | not started; zero task commits |
| Slice B / B:T8 through B:T12 | not started because the exact `A:T1` start dependency was never reached |
| Parked checkpoint | none; no worktree comment written |
| Overlap | not achieved; overlap seconds not calculable |
| Integration | no slice commit existed; integration remained at `16fdb64` |

## Probe results

- Frozen route was read from `workflow.json` as `codex` / `gpt-5.6-luna` / `high`; local `codex --help` proved `--model` and `-c` are expressible.
- Read-only automatic preflight returned `status=candidate`, `reason=canary-required`, `cached=false`, and `cleanup=not-run`; no automatic canary or PASS receipt was created.
- A direct worktree was created through the required two-step path. Its complete Orca/Git ownership receipt matched and its path was not a symlink.
- First `terminal create` attempt at `2026-08-26T21:58:51-0300` returned `Timed out waiting for terminal handle after creation`; exact-worktree terminal inspection showed only the original unused shell.
- One clean retry at `2026-08-26T21:59:31-0300` returned the same error. Per session protocol and AST-01 fail-closed behavior, no prompt, task edit, polling, second worker, checkpoint, or integration followed.
- Defect: [`BUG-20260826-assisted-orca-terminal-create-timeout`](../bugs/BUG-20260826-assisted-orca-terminal-create-timeout.md).

## Cleanup and residue

- Before deletion, Orca and Git revalidated repo id, complete worktree id, instance, path, gitdir, branch, and `pre_head/current_head=16fdb64`; status was clean, no Git operation was active, the path was not a symlink, branch tip matched current head, and the tip was an ancestor of integration.
- The unused shell handle `term_bf9c6976-99d9-4d57-8c16-fdbd8bee23fe` disappeared during the failed-create boundary; exact-worktree re-list returned zero terminals and `terminal stop` confirmed `stopped: 0`.
- `orca worktree rm` targeted the complete id and returned `removed: true`. Orca subsequently listed no slice worktree; Git listed only the integration ground; the exact slice path and branch ref were absent; global terminal count returned to `18` and fixture-owned terminals returned to zero.
- No unrelated worktree, terminal, branch, or source-checkout file was removed. The ignored integration ground remains as the raw-evidence fixture, not a live slice resource.
- Final snapshot at `2026-08-26T22:07:09-0300`: Orca fixture repo had one integration ground and zero slice worktrees; fixture-owned terminals were `0`; global terminals were `18`, matching the pre-slice baseline; exact Orca selector returned `selector_not_found`; exact Git ref and slice path were absent. Slice worktree, terminal, path, and branch deltas were all `0 → 0`.
- Residual audit: the clean terminal-free integration ground at base `16fdb64` remains below the ignored evidence path. An exact-id removal attempt at `2026-08-26T22:11:56-0300` was refused with `Refusing to delete protected worktree path`; no force or manual deletion followed. This retained raw-evidence repository is not a slice lane and contains no pilot task commit.

## Debrief

**Verdict: FAIL.** E2E-001 cannot enter A:T1 because installed Orca fails to return an explicit
worker terminal handle. AST-01 correctly stops the lane before route proof and prompt delivery, but
the public assisted journey is not usable. Fix `BUG-20260826-assisted-orca-terminal-create-timeout`,
then use a fresh Verifier to resume from this charter and its adjacent canaries.
