# Hybrid Slice Execution S4 Validation

**Verdict:** FAIL
**Date:** 2026-08-28
**Phase:** Technical
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Diff range:** `2cb70ba..56cd202`
**Verifier:** independent session, author != verifier

CP-S4 remains blocked. The remediation makes the public three-command lifecycle executable and
contains state paths, but the canonical suite no longer discriminates independent identity
correlation, receipt ownership, or exactly-once Git/lease mutations. Three prior fingerprints remain
open at failed-remediation count 2.

## Scope and isolation

`git diff --shortstat 2cb70ba..56cd202` reports 11 files changed, 2,079 insertions, and 28 deletions.
`git diff --check 2cb70ba..56cd202` exits 0. The real checkout porcelain was empty before gates and
scratch work. After two disposable worktrees were removed it again contained only this report and
`review-fingerprints.json`. `git worktree list --porcelain | rg '^worktree ' | wc -l` returned 2
before and after sensors. No live Orca command ran.

## Public surface and task state

- `tools/test_orca_assisted_probe.py:53`-`55` proves the CLI has exactly `dispatch`, `inspect`, and
  `cleanup`.
- T5, T6, and T7 are marked complete in `tasks.md`; their required gate boxes are checked.
- Public dispatch state is accepted by cleanup in the happy case at
  `tools/test_orca_assisted_probe.py:153`-`187`.

## Spec-anchored acceptance criteria

| Requirement | Spec-defined outcome | `file:line` + assertion/evidence | Result |
| --- | --- | --- | --- |
| HSE-22 | Persist complete packet, then send only its pointer. | `tools/test_orca_assisted_probe.py:58`-`74` invokes public dispatch, asserts persisted state/receipt, one send, absent body, and pointer path. | PASS |
| HSE-23 | Terminal text never contains packet body. | `tools/test_orca_assisted_probe.py:71`-`74` asserts one send and excludes `SECRET_PACKET_BODY`. Pointer-body mutation was killed. | PASS |
| HSE-24 | Every Orca, Git, and lease mutation occurs at most once per logical operation. | `tools/test_orca_assisted_probe.py:115`-`129` asserts Orca ledger counts, but excludes the last lease effect from `attempts` at `:127` and counts neither Git nor provider invocations. A duplicate Git+lease mutant survived. | FAIL |
| HSE-25 | Transient mutation failure settles through bounded reads without retry. | `tools/test_orca_assisted_probe.py:132`-`142` covers only one Orca create failure. It does not induce post-effect failure for send/set/stop/rm, Git, or lease, and exercises no repeated read settlement. | FAIL |
| HSE-26 | Repository, worktree, handle, route, task, operation, commit, and lease are independently proved before acceptance. | Happy correlation is supplied at `tools/test_orca_assisted_probe.py:93`-`112`, but deleting `_observation_identity` entirely leaves 8/8 green. | FAIL |
| HSE-27 | Malformed, stale, reused, or contradictory provider/Git evidence fails closed. | No current assertion supplies a contradictory observation. `SEC-007` is present only in the combined happy test name at `tools/test_orca_assisted_probe.py:93`; the identity-check deletion survived. | FAIL |
| HSE-28 | Cleanup stops/releases/removes only owned effects and reports residue zero. | `tools/test_orca_assisted_probe.py:153`-`187` proves happy stop, release, and worktree removal, but does not assert branch/ref absence or the normalized residue object. | FAIL |
| HSE-29 | Import performs zero Orca, Git, provider, or filesystem mutations. | `tools/test_orca_assisted_probe.py:145`-`150` imports with a fake Orca on PATH and asserts no call ledger. Guard is `tools/orca_assisted_probe.py:1603`-`1604`. | PASS |
| HSE-39 | Every executable and writable/effect path is repository-owned, non-symlinked, and fixed argv. | `tools/test_orca_assisted_probe.py:77`-`90` covers outside state and a symlinked packet. It does not exercise absolute/escaping/missing/non-executable providers or unsafe cleanup targets required by `SEC-001`. | FAIL |
| HSE-41 | Persist immutable identities sufficient to reconcile the same effect. | State fields are checked at `tools/test_orca_assisted_probe.py:67`-`70`; independent reconciliation is not discriminated because `_observation_identity` can be removed with a green suite. | FAIL |
| HSE-43 | Incomplete ownership/integration/clean/stop/lease/ref proof stops before destruction and reports residue. | The current suite has no dirty, unmerged, running, live-lease, extra-ref, or foreign-state refusal. Bypassing receipt id/path/handle comparison at `tools/orca_assisted_probe.py:1305`-`1308` leaves 8/8 green. | FAIL |
| HSE-47 | Reused handle/worktree for another repository, slice, or operation is rejected before cleanup. | No current negative identity or cleanup-reuse assertion exists; both identity and receipt-ownership mutants survived. | FAIL |

**Spec result:** 3/12 scoped requirements fully matched, 9/12 have evidence gaps, 0
spec-precision gaps.

## Test integrity

The focused suite fell from 34 to 8 test functions:

- `git show 9457cf6:tools/test_orca_assisted_probe.py | rg -n '^def test_' | wc -l` -> 34.
- `rg -n '^def test_' tools/test_orca_assisted_probe.py | wc -l` -> 8.
- Assert statements fell from 97 to 22 using the same old/current `rg -n 'assert '` comparison.
- `git diff --diff-filter=D --name-only 2cb70ba..56cd202 -- 'tools/test*' | wc -l` -> 0 deleted test files.

Removing historical fixture-only commands was legitimate. The replacement also removed required
negative outcomes: `tests.md:63`-`65` requires post-effect failure for every mutation, contradictory
identity, and unsafe cleanup (`SEC-006` through `SEC-008`). `SEC-008` has no current test at all.
Combining IDs into happy-path names does not preserve those assertions. This is test weakening, not
mere fixture pruning.

## Gates

- `python3 tools/test_orca_assisted_probe.py`: exit 0; 8/8 passed.
- `npm_config_offline=true npm run test:all`: exit 0. Vitest: 8/8 files and 111/111 tests passed.
  All 14 Python suites completed; no failure or skip was reported.

## Discrimination sensor

Mutations ran only in detached disposable worktrees at `56cd202`. The focused suite was run after
each fault; scratch diffs were restored before removal.

| Mutation | Fault | Result |
| --- | --- | --- |
| M1 | Send packet body instead of pointer in `send_pointer`. | KILLED: body-exclusion assertion at `tools/test_orca_assisted_probe.py:73`; exit 1. |
| M2 | Return immediately from `_observation_identity`, disabling all independent correlation. | SURVIVED: 8/8 passed; exit 0. |
| M3 | Invoke each declared Git and lease mutation twice. | SURVIVED: 8/8 passed; exit 0. |
| M4 | Return from `_receipt_from_state` before id/path/handle ownership comparison. | SURVIVED: 8/8 passed; exit 0. |

**Sensor result:** 1/4 killed, 3/4 survived. Real porcelain and worktree count returned to their
baselines.

## Code quality

The public argparse surface is now minimal and import-safe, and the implementation remains stdlib
only. The test layer does not meet the project contract: it maps several security IDs to happy paths,
omits `SEC-008`, permits two terminal sends in `IT-007` at
`tools/test_orca_assisted_probe.py:128`, and lacks exact Git/provider ledgers. The gate is green but
cannot certify the specified failure paths.

## Ranked gaps and fingerprint accounting

1. **Blocker:** Independent effect identity can be disabled without detection. Fingerprint
   `49092771bac5f9461878129cc1518db120787ec6944d2f7d3abf81e2258fab0b` remains open at failed
   remediation 2.
2. **Blocker:** Cleanup receipt ownership and fail-closed residue cases are not discriminated.
   Fingerprint `d11da16b460c9514ef870fea56f469cb35ea657f77cdd7a9bbfd3d2eafb6b9f0` remains open at failed
   remediation 2.
3. **Major:** Exact-once assertions omit Git and lease call ledgers and their transient paths.
   Fingerprint `a83ca4d68afa5e45916eae7606c22e6dd57444470bea7b13cfb916684e98bbfd` remains open at failed
   remediation 2.

No new lesson is needed: L-021, L-022, and L-023 already describe these recurring failures.

## Fix tasks

1. Add negative table cases for every independent identity field and require zero next mutation on
   mismatch; the `_observation_identity` deletion must fail.
2. Count fake Git and provider calls exactly, induce post-effect failure for both plus every Orca
   mutator, and assert no retry; duplicate-call mutants must fail.
3. Restore spec-owned `SEC-008` cleanup refusals (foreign/reused identity, dirty/unmerged worktree,
   running process, live lease, extra ref) through public `cleanup --state`, asserting zero destructive
   effects and exact residue; receipt-ownership bypass must fail.

## Summary

**Overall:** FAIL. CP-S4 must not release to dependent slices. The implementation repairs the earlier
happy lifecycle, but the reduced canonical suite permits the exact identity, duplicate-mutation, and
unsafe-cleanup regressions that S4 exists to prevent.
