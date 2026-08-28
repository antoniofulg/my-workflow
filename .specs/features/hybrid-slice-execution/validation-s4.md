# Hybrid Slice Execution S4 Validation

**Verdict:** FAIL
**Date:** 2026-08-28
**Phase:** Technical
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Diff range:** `2cb70ba..b13df17`
**Verifier:** independent session, author != verifier

CP-S4 remains blocked. Five high-risk mutants were killed, including duplicate successful Git and
provider effects. A sixth mutant inserted a direct mutating `git(..., "add", ...)` call outside
`MutationRunner.issue`; the structural AST contract stayed green. The test therefore does not prove
HSE-54's exclusive mutation boundary. Cleanup also lacks the required independent PATH-backed Git
and Orca ledger proof for HSE-56.

## Task completion

| Task | Status | Notes |
| --- | --- | --- |
| T5-T7 | Done, checkpoint blocked | Existing lifecycle implementation remains present. |
| T13 | Done | Generation-aware resume tests pass. |
| T14 | Needs fix | Physical issue guard works in exercised paths, but structural bypass proof is incomplete. |

## Spec-anchored acceptance criteria

| Requirement | Spec-defined outcome | `file:line` + assertion/evidence | Result |
| --- | --- | --- | --- |
| HSE-22, HSE-23 | Persist the full packet and transport only its pointer. | `tools/test_orca_assisted_probe.py:96` asserts persisted state, one send, absent body, and packet path at lines 104-112. | PASS |
| HSE-24, HSE-25 | Issue each logical mutation once; reconcile ambiguity only with bounded reads. | `tools/test_orca_assisted_probe.py:229` asserts one physical call after post-effect failure; `:274` asserts one mutation and one read; duplicate Git/provider mutants died. | PASS |
| HSE-26, HSE-27, HSE-41, HSE-47 | Prove every identity independently and reject contradictions. | `tools/test_orca_assisted_probe.py:305` rejects each observation field; `:333` rejects every receipt/state contradiction; `:348` stops public cleanup before Orca. | PASS |
| HSE-28, HSE-43 | Remove only proven owned effects and report residue zero; unsafe state has zero destructive effects. | `tools/test_orca_assisted_probe.py:186` asserts stop, release, rm, ref absence, settled effects, and all five effect IDs; `:368` asserts zero destructive effects for five unsafe states. | PASS |
| HSE-29 | Import performs zero external or filesystem mutation calls. | `tools/test_orca_assisted_probe.py:178` imports via `runpy` and asserts the fake ledger is absent at line 183. | PASS |
| HSE-39 | Paths remain repository-owned and non-symlinked before effects. | `tools/test_orca_assisted_probe.py:115` rejects outside state and symlink packet; `:409` rejects symlinked repository with zero calls/state. | PASS |
| HSE-49, HSE-50 | Authorized resume appends generation 2 without changing generation 1 or cumulative count. | `tools/test_review_convergence.py:139` asserts generation 2 open/local 0/cumulative 3 and generation 1 halted/3 with exact authorization at lines 147-157. | PASS |
| HSE-51 | Unknown, non-halted, unauthorized, reworded, replacement, and reset bypasses fail before write. | `tools/test_review_convergence.py:162` exercises all bypasses and asserts byte identity at lines 168-193. | PASS |
| HSE-52 | Only fresh independent PASS plus green gate closes the resumed generation. | `tools/test_review_convergence.py:198` keeps ordinary/red-gate results open, closes only qualified PASS, and halts generation 2 on its own third failure at lines 204-221. | PASS |
| HSE-53, HSE-57 | Persist `in_flight`, attempt 1 before sink; persistence failure performs no sink and preserves bytes. | `tools/test_orca_assisted_probe.py:433` asserts pre-sink state at lines 447-451 and unchanged durable bytes after injected write failure at lines 453-467. | PASS |
| HSE-54 | Every reachable Orca, Git, and provider mutation uses `MutationRunner.issue`; structural contract rejects alternate sinks. | `tools/test_orca_assisted_probe.py:419` rejects only direct names `raw` and `subprocess` at lines 423-430. A direct mutating `git(root, "add", "seed")` bypass left this AST test green. | FAIL |
| HSE-55 | Existing `in_flight`/`unknown` effects perform zero mutations and bounded reads only. | `tools/test_orca_assisted_probe.py:470` replays both states, then asserts unchanged physical ledgers and exactly two reads at lines 497-511; reissue mutant died. | PASS |
| HSE-56 | Happy, timeout, and cleanup paths have exactly one physical Git/provider/Orca mutation per logical effect; pointer excludes body. | `tools/test_orca_assisted_probe.py:470` proves PATH-backed dispatch ledgers at lines 473-494. Cleanup at `:186` uses in-process `raw`/Git substitutions, so no file:line assertion proves PATH-backed cleanup ledgers. | GAP |

**Spec result:** 19/21 scoped requirements match exact outcomes; HSE-54 fails and HSE-56 lacks the
required cleanup-layer evidence. There are 0 spec-precision gaps.

## Gates

- `python3 tools/test_review_convergence.py` -> exit 0, 10/10 passed.
- `python3 tools/test_orca_assisted_probe.py` -> exit 0, 18/18 passed; AST count command reports 18
  test functions and 62 assertions.
- `npm_config_offline=true npm run test:all` -> exit 0. Vitest: 8/8 files and 111/111 tests.
  Python discovery completed every suite with no failure or skip; focused probe remained 18/18.
- `git diff --check 2cb70ba..b13df17` -> exit 0.
- `git diff --shortstat 2cb70ba..b13df17` -> 23 files changed, 3,235 insertions, 120 deletions.
- No live Orca command ran.

## Discrimination sensor

All mutations ran in detached disposable worktrees at `b13df17`.

| Mutation | Fault | Result |
| --- | --- | --- |
| M1 | Issue a successful Git effect twice with the same effect ID. | KILLED: focused suite exit 1 on duplicate cleanup Git mutation. |
| M2 | Issue a successful provider effect twice. | KILLED: focused suite exit 1 on duplicate provider ledger entry. |
| M3a | Call `raw` directly from `dispatch`, bypassing `MutationRunner`. | KILLED: AST test exit 1, `direct sink in dispatch`. |
| M3b | Call mutating `git(root, "add", "seed")` directly from `dispatch`. | SURVIVED: AST test exit 0, `AST SURVIVED`. |
| M4 | Reach the sink before persisting `in_flight`. | KILLED: focused suite exit 1; isolated pre-sink test also exits 1. |
| M5 | Reissue persisted `in_flight`/`unknown` effects instead of read-only reconcile. | KILLED: focused suite exit 1 with two physical create calls. |

**Sensor result:** 5/6 killed, 1 survived. Real porcelain returned to its baseline except this report
and convergence state. Worktree count returned from 2 to 2.

## Fingerprint accounting

Fingerprint `a83ca4d68afa5e45916eae7606c22e6dd57444470bea7b13cfb916684e98bbfd`
keeps generation 1 field-for-field halted at three failures. Generation 2 is open with one local
failure and four cumulative failures. Its exact authorization reference remains unchanged. The two
other S4 fingerprints remain open and were not closed by this FAIL verdict.

## Ranked gaps

1. **Blocker, HSE-54:** the structural test permits a direct mutating Git helper call outside
   `MutationRunner.issue`. Fix the canonical AST ownership check so it distinguishes and rejects
   mutating Git verbs while allowing read-only Git observations.
2. **Major, HSE-56:** extend the canonical lifecycle suite with PATH-backed cleanup ledgers for Orca,
   Git, and provider operations. Assert exactly one physical call for stop, lease release, detach,
   branch removal, and worktree removal, with pointer body exclusion retained.

## Summary

**Overall:** FAIL. The full gate is green and the redesigned issue runner kills duplicate-success,
pre-persistence, and restart-reissue faults. CP-S4 cannot close because its structural exclusivity
sensor survived a direct Git mutation and cleanup lacks the contracted PATH-ledger evidence.
