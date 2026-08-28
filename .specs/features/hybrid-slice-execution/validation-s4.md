# Hybrid Slice Execution S4 Validation

**Verdict:** FAIL
**Date:** 2026-08-28
**Phase:** Technical
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Diff range:** `2cb70ba..91b185a`
**Verifier:** independent session, author != verifier

CP-S4 remains blocked. The focused and full gates are green, PATH-backed cleanup proves each
physical mutation once, and nine high-risk mutants die. One structural mutant calls
`MutationRunner._sink` directly from public `dispatch`; the HSE-54 test stays green. The canonical
suite therefore still permits an alternate mutation path around `MutationRunner.issue`.

## Task completion

| Task | Status | Notes |
| --- | --- | --- |
| T5-T7 | Done, checkpoint blocked | Pointer, identity, reconciliation, and cleanup behavior remain present. |
| T13 | Done | Generation-aware resume contract is green. |
| T14 | Needs fix | Physical ledgers pass; structural exclusivity still permits direct private-sink entry. |

## Spec-anchored acceptance criteria

| Requirement | Spec-defined outcome | `file:line` + assertion/evidence | Result |
| --- | --- | --- | --- |
| HSE-22, HSE-23 | Persist the full packet and transport only its pointer. | `tools/test_orca_assisted_probe.py:96` asserts persisted state, one send, packet path, and absent body at `:104`-`:112`. | PASS |
| HSE-24, HSE-25 | Issue each logical mutation once; reconcile ambiguity only with bounded reads. | `tools/test_orca_assisted_probe.py:325` asserts one physical call after repeated post-effect failure; `:370` asserts one mutation and bounded reads. Duplicate Git/provider mutants die. | PASS |
| HSE-26, HSE-27, HSE-41, HSE-47 | Prove every persisted identity independently and reject contradictions before cleanup. | `tools/test_orca_assisted_probe.py:389` rejects every observation field; `:429` rejects every receipt/state contradiction; `:444` stops public cleanup before Orca. Both identity-bypass mutants die. | PASS |
| HSE-28, HSE-43 | Remove only proven owned effects, stop before unsafe destruction, and report residue zero. | `tools/test_orca_assisted_probe.py:186` asserts the public cleanup lifecycle; `:229` asserts PATH-backed cleanup and `residue == []`; `:464` asserts zero destructive effects for five unsafe states. | PASS |
| HSE-29 | Import performs zero external or filesystem mutation calls. | `tools/test_orca_assisted_probe.py:178` imports with fake executables and asserts no ledger at `:183`. | PASS |
| HSE-39 | Writable and executable paths remain repository-owned and non-symlinked before effects. | `tools/test_orca_assisted_probe.py:115` rejects outside state and symlinked packet paths; `:505` rejects a symlinked repository with zero calls/state. | PASS |
| HSE-49, HSE-50 | Authorized resume appends generation 2 while preserving generation 1 and cumulative history. | `tools/test_review_convergence.py:139` asserts generation 2 open/local 0, cumulative 3, generation 1 halted/3, and exact authorization. | PASS |
| HSE-51 | Unknown, non-halted, unauthorized, reworded, replacement, and reset bypasses fail before write. | `tools/test_review_convergence.py:162` exercises every bypass and asserts original bytes unchanged. | PASS |
| HSE-52 | Only fresh independent PASS plus green gate closes the current generation. | `tools/test_review_convergence.py:198` rejects non-qualifying results, closes qualifying PASS, and proves generation-local halt accounting. | PASS |
| HSE-53, HSE-57 | Persist `in_flight`, immutable identity, and attempt 1 before sink; persistence failure performs no sink and preserves bytes. | `tools/test_orca_assisted_probe.py:625` asserts the pre-sink record and unchanged bytes after injected atomic-write failure. The sink-before-ledger mutant dies. | PASS |
| HSE-54 | Every reachable Orca, Git, and provider mutation uses `MutationRunner.issue`; structural checks reject every alternate sink. | `tools/test_orca_assisted_probe.py:548` walks public lifecycle helpers and rejects direct raw, subprocess, and mutating Git calls. A direct `runner._sink({...})` call inserted after `tools/orca_assisted_probe.py:1711` leaves `test_UT020_public_lifecycle_has_one_mutation_issuer` green. | FAIL |
| HSE-55 | Existing `in_flight` or `unknown` effects perform zero mutations and use bounded same-identity reads. | `tools/test_orca_assisted_probe.py:662` replays both states and asserts unchanged external ledgers plus exactly two reads at `:697`-`:703`. The reissue mutant dies. | PASS |
| HSE-56 | Happy, timeout, and cleanup paths record one physical mutation per logical effect; transport excludes packet body. | `tools/test_orca_assisted_probe.py:229` asserts PATH ledgers: stop 1, release 1, detach 1, branch-delete 1, worktree-remove 1, rm 1, no send/body, and `residue == []` at `:302`-`:322`; `:662` proves dispatch ledgers. | PASS |

**Spec result:** 20/21 scoped requirements match exact outcomes. HSE-54 fails. There are 0
spec-precision gaps.

## Gates

- `python3 tools/test_review_convergence.py` -> exit 0, 10/10 passed.
- `python3 tools/test_orca_assisted_probe.py` -> exit 0, 19/19 passed; AST count command reports 19
  test functions and 76 assertions.
- `npm_config_offline=true npm run test:all` -> exit 0. Vitest reports 8/8 files and 111/111 tests;
  Python discovery completes every suite with no reported failure or skip; focused probe remains
  19/19.
- `git diff --check 2cb70ba..91b185a` -> exit 0.
- `git diff --shortstat 2cb70ba..91b185a` -> 23 files changed, 3,464 insertions, 120 deletions.
- No live Orca command ran.

## PATH-backed cleanup inspection

The independent disposable run prints these normalized physical results before its temporary files
are deleted:

- Orca mutation ledger: `stop`, `rm`, each exactly once.
- Provider ledger: `release` once, followed by read-only `inspect` once.
- Git mutation ledger: `switch --detach`, `branch --delete lane`, and `worktree remove --force`, each
  exactly once. Other Git rows are read-only inspection verbs.
- First cleanup returns fail-closed after the stop post-effect timeout. The second cleanup reconciles
  the same stopped handle by reads and does not issue stop again.
- Result has `residue: []`; terminal ledger contains neither `terminal send` nor packet body.

## Discrimination sensor

All mutations ran at `91b185a` in detached disposable worktrees.

| Mutation | Fault | Result |
| --- | --- | --- |
| M1 | Duplicate a successful Git sink call. | KILLED: focused suite exits 1 on duplicate cleanup Git mutation. |
| M2 | Duplicate a provider sink call. | KILLED: focused suite exits 1 with two lease ledger rows. |
| M3 | Call `raw` directly from public `dispatch`. | KILLED: structural test rejects the direct sink. |
| M4 | Call `subprocess.run` directly from public `dispatch`. | KILLED: structural test rejects the direct subprocess sink. |
| M5 | Call mutating `git(..., "add", ...)` directly from public `dispatch`. | KILLED: focused and isolated structural checks both exit 1. |
| M6 | Invoke the sink before persisting the `in_flight` record. | KILLED: focused suite observes duplicate physical create after restart. |
| M7 | Reissue existing `in_flight` and `unknown` records. | KILLED: focused suite records two physical create calls. |
| M8 | Bypass cleanup receipt/state identity conjunction. | KILLED: public cleanup accepts a forged repository and the focused suite exits 1. |
| M9 | Call `MutationRunner._sink` directly from public `dispatch`. | SURVIVED: isolated HSE-54 structural test exits 0 and prints `AST_SURVIVED_DIRECT_PRIVATE_SINK`. |
| M10 | Disable independent provider observation identity validation. | KILLED: contradictory repository observation is accepted and the focused suite exits 1. |

**Sensor result:** 9/10 killed, 1 survived. Real porcelain returned to its empty baseline. Worktree
count returned from 2 to 2.

## Fingerprint accounting

- `a83ca4d68afa5e45916eae7606c22e6dd57444470bea7b13cfb916684e98bbfd` keeps generation 1
  field-for-field halted at 3. Generation 2 records failure 2 and remains open; cumulative failures
  become 5. The authorization reference remains unchanged.
- `49092771bac5f9461878129cc1518db120787ec6944d2f7d3abf81e2258fab0b`
  closes after the current independent identity proof and green gate.
- `d11da16b460c9514ef870fea56f469cb35ea657f77cdd7a9bbfd3d2eafb6b9f0` closes after the current
  public cleanup, correlated release, physical ledger, and residue-zero proof.

## Ranked gaps

1. **Blocker, HSE-54:** `tools/test_orca_assisted_probe.py:593` rejects direct helper names and
   subprocess attributes, but permits a reachable direct call to `MutationRunner._sink`. Reject any
   `_sink` call whose owner is outside `MutationRunner.issue`, while retaining required read-only Git
   and provider inspections.

## Code quality

The module stays stdlib-only, import-safe, and uses explicit Git verb semantics that permit required
reads. The physical lifecycle proof is now complete. Structural ownership is still hollow at the
private sink boundary, so the checkpoint is not releasable.

No new lesson was added. The surviving structural-boundary mutant is the same grounded guidance
already tracked by L-024; duplicating it would split one lesson into two exact-match candidates.

## Summary

**Overall:** FAIL. CP-S4 cannot close. Generation 2 is not halted, so one targeted remediation may
continue autonomously. The next verifier must kill a direct `MutationRunner._sink` bypass without
banning the read-only reconciliation paths.
