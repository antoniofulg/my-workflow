# Hybrid Slice Execution S4 Validation

**Verdict:** PASS
**Date:** 2026-08-28
**Phase:** Technical
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Diff range:** `2cb70ba..d75a188`
**Verifier:** independent session, author != verifier

## PASS

CP-S4 is releasable. All 21 scoped requirements match exact spec outcomes. The focused probe,
convergence suite, full offline gate, and ten historical discrimination mutants pass. No live Orca
command ran.

## Task completion

| Task | Status | Notes |
| --- | --- | --- |
| T5-T7 | Done | Pointer delivery, effect identity, bounded reconciliation, and owned cleanup pass. |
| T13 | Done | Append-only audit generation and bypass rejection pass. |
| T14 | Done | `MutationRunner.issue` is the sole reachable mutation boundary. |

## Spec-anchored acceptance criteria

| Requirement | Spec-defined outcome | `file:line` + assertion/evidence | Result |
| --- | --- | --- | --- |
| HSE-22, HSE-23 | Persist the packet and send only its pointer. | `tools/test_orca_assisted_probe.py:96` dispatches through fake Orca; `:104`-`:112` assert success, full state, exactly one send, absent body, and exact packet path. | PASS |
| HSE-24, HSE-25 | Issue each logical mutation once and reconcile ambiguity only through bounded reads. | `tools/test_orca_assisted_probe.py:148` asserts attempts `1` and exact create/send/set/stop/rm counts at `:160`-`:162`; `:165`-`:175` assert one create after two failed dispatches; `:370` proves read-only settle. | PASS |
| HSE-26, HSE-27, HSE-41, HSE-47 | Prove all persisted identities and reject contradictions before destructive cleanup. | `tools/test_orca_assisted_probe.py:401` rejects every independent observation mismatch; `:429` rejects every receipt/state mismatch; `:444` asserts zero Orca calls for public cleanup contradictions. | PASS |
| HSE-28, HSE-43 | Remove only correlated owned effects and report residue zero. | `tools/test_orca_assisted_probe.py:229` executes PATH-backed cleanup; `:308` asserts `residue == []`; `:310`-`:322` assert exact Orca/provider/Git mutations and absent worktree/ref. `:464` rejects unsafe cleanup states. | PASS |
| HSE-29 | Import performs zero external or filesystem-mutation calls. | `tools/test_orca_assisted_probe.py:178` imports under call-counting PATH fakes and asserts no ledger at `:183`. | PASS |
| HSE-39 | Control paths remain repository-owned and non-symlinked before effects. | `tools/test_orca_assisted_probe.py:115` asserts outside/symlinked paths fail with zero calls; `:505` asserts a symlinked repository fails before state or calls. | PASS |
| HSE-49, HSE-50 | Authorized resume appends generation 2 without rewriting generation 1 or cumulative history. | `tools/test_review_convergence.py:139` asserts generation 2, cumulative `3`, generation 1 halted at `3`, local `0`, and the exact authorization at `:147`-`:157`. | PASS |
| HSE-51 | Resume bypasses and manual counter resets fail before write. | `tools/test_review_convergence.py:162` exercises unauthorized, unknown, ordinary-record, reworded, replacement, and reset attempts; `:182` and `:193` assert unchanged bytes. | PASS |
| HSE-52 | Only a fresh independent PASS with a green gate closes generation 2. | `tools/test_review_convergence.py:198` leaves non-independent/red-gate results open and asserts qualified closure while generation 1 stays halted at `:204`-`:212`. | PASS |
| HSE-53, HSE-57 | Persist immutable `in_flight`, attempt `1` before the sink; atomic failure calls no sink and preserves bytes. | `tools/test_orca_assisted_probe.py:639` asserts pre-sink state at `:652`-`:654`, duplicate suppression at `:656`-`:657`, and unchanged prior bytes after injected write failure at `:659`-`:673`. | PASS |
| HSE-54 | Every reachable mutation uses `MutationRunner.issue`; alternate raw, subprocess, Git, and private sinks are rejected. | `tools/test_orca_assisted_probe.py:548` traverses public lifecycle reachability; `:593` classifies sinks; `:600` rejects private sinks; `:608` validates the real source; `:626`-`:636` inject and kill exact `runner._sink(...)`. Source inspection finds no `_sink` or `_physical_sink` method. | PASS |
| HSE-55 | Existing `in_flight` and `unknown` effects perform zero mutations and use bounded same-identity reads. | `tools/test_orca_assisted_probe.py:676` replays both states; `:710`-`:717` assert unchanged Orca/Git ledgers and exactly two reads. | PASS |
| HSE-56 | Independent physical Orca, Git, and provider ledgers each record one mutation; terminal receives pointer, never body. | `tools/test_orca_assisted_probe.py:676` dispatches PATH fakes; `:693`-`:702` assert one create, one send, one Git row, one provider row, absent body, settled state. Cleanup exact counts and residue are asserted at `:308`-`:322`. | PASS |

**Spec result:** 21/21 scoped requirements match exact outcomes. There are 0 spec-precision gaps.

## Gates

- `python3 tools/test_orca_assisted_probe.py` -> exit 0, 19/19 passed. AST count command reports
  19 test functions and 77 assertions.
- `python3 tools/test_review_convergence.py` -> exit 0, 10/10 passed. AST count command reports
  10 test functions and 39 assertions.
- `npm_config_offline=true npm run test:all` -> exit 0. Vitest reports 8/8 files and 111/111 tests;
  Python discovery runs 14 suites with no failure or skip; the probe remains 19/19.
- `python3 -m compileall -q tools/orca_assisted_probe.py tools/test_orca_assisted_probe.py .agents/skills/workflow-spec-driven/scripts/review_convergence.py tools/test_review_convergence.py` -> exit 0.
- `git diff --check 2cb70ba..d75a188` -> exit 0.
- `git diff --shortstat 2cb70ba..d75a188` -> 23 files changed, 3,509 insertions, 120 deletions.
- No live Orca command ran.

## PATH-backed lifecycle proof

- Dispatch physical ledgers record Orca create `1`, pointer send `1`, Git mutation `1`, provider
  mutation `1`; packet body marker is absent.
- Cleanup physical ledgers record Orca stop `1`, Orca rm `1`, provider release `1`, Git detach `1`,
  branch delete `1`, and worktree remove `1`; read-only observations may repeat.
- Restart from `unknown` and `in_flight` records zero new mutations and exactly two bounded reads.
- Cleanup returns `residue: []`; owned worktree and branch are absent.
- Import with call-counting executables records zero calls.

## Discrimination sensor

All mutations ran at `d75a188` in one detached disposable worktree. The real checkout remained clean.

| Mutation | Fault | Result |
| --- | --- | --- |
| M1 | Duplicate a successful Git sink call. | KILLED: focused suite exits 1 on the second cleanup Git mutation. |
| M2 | Duplicate a provider sink call. | KILLED: focused suite exits 1 with `['lease', 'lease']`. |
| M3 | Call `raw` directly from public `dispatch`. | KILLED: structural sensor reports `direct mutable sink`. |
| M4 | Call `subprocess.run` directly from public `dispatch`. | KILLED: structural sensor reports `direct provider/orca subprocess`. |
| M5 | Call mutating `git(..., "add", ...)` directly from public `dispatch`. | KILLED: structural sensor reports `direct mutating git call`. |
| M6 | Invoke the sink before persisting `in_flight`. | KILLED: focused suite detects duplicate terminal send. |
| M7 | Reissue persisted `in_flight`/`unknown` effects. | KILLED: focused suite records two physical create calls. |
| M8 | Bypass cleanup receipt/state identity conjunction. | KILLED: focused suite accepts contradictory repository and exits 1. |
| M9 | Insert exact `runner._sink({...})` after public dispatch constructs its runner. | KILLED: structural sensor reports `private mutation sink bypass`. |
| M10 | Disable independent observation identity validation. | KILLED: focused suite accepts contradictory repository observation and exits 1. |

The same structural sensor permits direct read-only `git(..., "rev-parse", "HEAD")`. Baseline PATH
tests permit repeated read-only Orca/provider/Git inspections while keeping mutation counts at one.

**Sensor result:** 10/10 historical mutants killed, 0 survived. Worktree count returned from 2 to 2.

## Fingerprint accounting

- Fingerprint `a83ca4d68afa5e45916eae7606c22e6dd57444470bea7b13cfb916684e98bbfd`
  retains generation 1 halted at 3 and generation 2's two failed remediations. Qualified independent
  PASS closes generation 2 and the fingerprint; cumulative failures remain 5.
- Fingerprint `49092771bac5f9461878129cc1518db120787ec6944d2f7d3abf81e2258fab0b`
  remains closed.
- Fingerprint `d11da16b460c9514ef870fea56f469cb35ea657f77cdd7a9bbfd3d2eafb6b9f0`
  remains closed.

## Code quality

The probe remains stdlib-only, import-safe, and guarded by `if __name__ == "__main__"`. The final
change deletes the alternate private sink instead of adding another control layer. Mutating Git,
provider, and Orca operations share one durable issuer; required read-only inspections remain legal.
No scope creep or unrelated refactor was found.

No new lesson is recorded. This clean PASS adds no new failure signal; the prior structural lesson
L-024 remains the grounded reusable guidance.

## Summary

**Overall:** PASS. CP-S4 may release S3 and S6.
