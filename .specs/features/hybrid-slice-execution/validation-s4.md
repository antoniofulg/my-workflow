# Hybrid Slice Execution S4 Validation

**Verdict:** FAIL — AUTONOMOUS HALT
**Date:** 2026-08-28
**Phase:** Technical
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Diff range:** `2cb70ba..4001592`
**Verifier:** independent session, author != verifier

CP-S4 remains blocked. The focused and full gates are green, but a duplicate successful Git
mutation still leaves all 15 focused tests green. This is the third failed remediation of fingerprint
`a83ca4d68afa5e45916eae7606c22e6dd57444470bea7b13cfb916684e98bbfd`; its status is now `halted`.
The autonomous run must stop. No dependent checkpoint, push, PR, or merge is authorized.

## Scope and isolation

- `git diff --shortstat 2cb70ba..4001592` reports 11 files changed, 2,510 insertions, and 28 deletions.
- `git diff --check 2cb70ba..4001592` exits 0.
- `python3 tools/test_orca_assisted_probe.py` exits 0 with 15/15 checks passed.
- AST counting reports 15 test functions and 43 `assert` nodes in the focused suite.
- The real checkout porcelain was empty before gates and sensor work. After both disposable
  worktrees were removed, porcelain was empty again until this report and fingerprint state changed.
- `git worktree list --porcelain | rg '^worktree ' | wc -l` returned 2 before and after sensors.
- No live Orca command ran. All Orca traffic came from the focused suite's fakes.

## Public surface and effect ledgers

- The CLI has exactly `dispatch`, `inspect`, and `cleanup` at
  `tools/test_orca_assisted_probe.py:90`-`92`.
- Pointer persistence and transport are asserted at `tools/test_orca_assisted_probe.py:95`-`111`:
  one terminal send, packet body absent, packet path present.
- Import safety is asserted at `tools/test_orca_assisted_probe.py:177`-`182`.
- Orca create/send/set/stop/rm counts are asserted at
  `tools/test_orca_assisted_probe.py:147`-`161`.
- Public cleanup asserts stop/rm, provider release/inspect, branch absence, and settled cleanup
  effects at `tools/test_orca_assisted_probe.py:185`-`225`.
- Post-effect ledgers cover Orca, Git, and provider failure paths at
  `tools/test_orca_assisted_probe.py:228`-`270`, and read-only settlement at
  `tools/test_orca_assisted_probe.py:273`-`299`.
- The successful declared-effect path does not count Git or provider invocations. It checks only
  Orca calls, while `data["effects"][:-1]` omits the final lease record at
  `tools/test_orca_assisted_probe.py:159`-`161`.

## Spec-anchored acceptance criteria

| Requirement | Spec-defined outcome | `file:line` + assertion/evidence | Result |
| --- | --- | --- | --- |
| HSE-22 | Persist complete packet and send only its pointer. | `tools/test_orca_assisted_probe.py:103`-`111` asserts persisted state, receipt identity, one send, absent body, and pointer path. | PASS |
| HSE-23 | Terminal text never contains packet body. | `tools/test_orca_assisted_probe.py:109`-`111` asserts one send, excludes `SECRET_PACKET_BODY`, and includes only the packet path. | PASS |
| HSE-24 | Every Orca, Git, and lease mutation occurs at most once per logical operation. | `tools/test_orca_assisted_probe.py:159`-`161` has no successful Git/provider call ledger. A second Git call at `tools/orca_assisted_probe.py:1575` survived with 15/15 green. | FAIL |
| HSE-25 | Transient mutation failure settles by bounded reads without mutation retry. | `tools/test_orca_assisted_probe.py:228`-`299` covers first-call failures and read settlement, but does not discriminate a duplicate successful Git mutation after the first succeeds. | FAIL |
| HSE-26 | Repository, worktree, handle, route, task, operation, commit, and lease identities are independently proved. | `tools/test_orca_assisted_probe.py:304`-`329` rejects each independently forged identity; deleting `_observation_identity` was killed. | PASS |
| HSE-27 | Malformed, reused, stale, or contradictory observations fail closed. | `tools/test_orca_assisted_probe.py:304`-`348` rejects every observation and receipt identity contradiction. | PASS |
| HSE-28 | Cleanup removes only owned effects and reports residue zero. | `tools/test_orca_assisted_probe.py:185`-`225` asserts stop/release/rm, removed branch, and settled cleanup effects; public output reports `residue: []`. | PASS |
| HSE-29 | Import performs zero Orca, Git, provider, or filesystem mutation. | `tools/test_orca_assisted_probe.py:177`-`182` imports through `runpy` with a fake Orca and asserts the ledger does not exist. | PASS |
| HSE-39 | External and writable paths are repository-owned, non-symlinked, and fixed argv. | `tools/test_orca_assisted_probe.py:114`-`127` rejects outside state and symlinked packet paths; `:408`-`:415` rejects a symlinked repository before effects. | PASS |
| HSE-41 | Persist immutable identities sufficient to reconcile the same effect. | `tools/test_orca_assisted_probe.py:304`-`329` checks all 16 persisted identity fields, and the identity-removal mutant died. | PASS |
| HSE-43 | Incomplete ownership/cleanliness/stop/lease/ref proof stops before destruction. | `tools/test_orca_assisted_probe.py:367`-`405` covers dirty, unmerged, running, live-lease, and extra-ref states and asserts zero destructive effects. | PASS |
| HSE-47 | Reused handle/worktree identity is rejected before cleanup. | `tools/test_orca_assisted_probe.py:332`-`364` rejects receipt/state contradictions and proves id/path/handle failures occur before Orca inventory or mutation. | PASS |

**Spec result:** 10/12 scoped requirements match their asserted outcomes. HSE-24 and HSE-25 fail.
There are 0 spec-precision gaps.

## Gates

- `python3 tools/test_orca_assisted_probe.py`: exit 0; 15/15 passed.
- `npm_config_offline=true npm run test:all`: exit 0. Vitest reports 8/8 files and 111/111
  tests passed. All 14 Python suites completed with no reported failure or skip.

## Discrimination sensor

Mutations ran only in detached disposable worktrees at `4001592`.

| Mutation | Fault | Result |
| --- | --- | --- |
| M1 | Return immediately from `_observation_identity`, disabling independent correlation. | KILLED: contradictory repository observation was accepted; focused suite exit 1. |
| M2 | Invoke the declared Git mutation twice after the first successful call. | SURVIVED: focused suite exit 0; 15/15 passed. |
| M3 | Duplicate the lease/provider mutation. | NOT RUN: third identical fingerprint failure required immediate halt. |
| M4 | Bypass receipt id/path/handle cleanup conjunction. | NOT RUN: third identical fingerprint failure required immediate halt. |

**Sensor result:** 1/2 executed mutants killed, 1/2 survived. The required four-mutant run stopped at
M2 because the same fingerprint reached its third failed remediation. Real porcelain and worktree
count returned to baseline.

## Root cause and fingerprint accounting

The new failure-path table does count one Git/provider call when the first call raises. That cannot
detect a second call placed after a successful first call because the injected failure prevents the
second statement from executing. The happy-path test neither records Git/provider calls nor includes
the final lease effect in its aggregate assertion. Therefore a duplicate successful Git mutation is
invisible to the canonical suite.

1. **HALTED / Blocker:** `a83ca4d68afa5e45916eae7606c22e6dd57444470bea7b13cfb916684e98bbfd`
   moved from failed remediation 2 / `open` to failed remediation 3 / `halted`.
2. **Open / Blocker:** `49092771bac5f9461878129cc1518db120787ec6944d2f7d3abf81e2258fab0b`
   remains at failed remediation 2 because PASS-only closure was not reached.
3. **Open / Blocker:** `d11da16b460c9514ef870fea56f469cb35ea657f77cdd7a9bbfd3d2eafb6b9f0`
   remains at failed remediation 2 because PASS-only closure was not reached.

## Code quality and lessons

The module is stdlib-only, import-safe, and its public CLI remains minimal. The suite has recovered
the requested size, correlation, unsafe-cleanup, and failure-path cases, but still does not protect
the successful Git/provider exactly-once path. That gap violates the canonical test contract despite
a green gate.

No new lesson was recorded. This is the same already-grounded lifecycle/external-effect failure
tracked by the existing S4 validation, L-021 through L-023, and the immutable fingerprint above;
duplicating it as a new lesson would not add guidance.

## Summary

**Overall:** FAIL — autonomous halt. CP-S4 is not releasable. The full gate is green, but the tests
still allow a duplicate successful Git mutation. Human direction is required before another
remediation attempt because the immutable fingerprint has now failed three times.
