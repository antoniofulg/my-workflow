# Hybrid Slice Execution S4 Validation

**Verdict:** FAIL
**Date:** 2026-08-28
**Phase:** Technical
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Diff range:** `2cb70ba..9457cf6`
**Verifier:** independent session, author != verifier

CP-S4 is not releasable. Pointer transport, import safety, Orca mutation retry protection, and
private receipt cleanup have useful coverage. The three public commands do not form one usable
lifecycle: `dispatch` writes a state that `cleanup --state` cannot consume, `inspect` settles on a
matching handle without correlating the other required identities, and no lease release exists.

## Scope and isolation

`git diff --shortstat 2cb70ba..9457cf6` reports 7 files changed, 2,693 insertions, and 23 deletions.
`git diff --check 2cb70ba..9457cf6` exits 0. Real checkout porcelain was empty before verification.
It remained unchanged through gates and scratch mutation cleanup, before this report and the
required fingerprint state were written. `git worktree list --porcelain` reported exactly 2
legitimate worktrees before and after sensor cleanup. No live Orca command ran.

## Task completion

| Task | Recorded state | Verification result |
| --- | --- | --- |
| T5 | Implementation boxes checked; task gate box still unchecked | FAIL: HSE-22 lacks a public-dispatch assertion |
| T6 | Implementation boxes checked; task gate box still unchecked | FAIL: HSE-24 through HSE-27 and HSE-41 are only partially implemented or asserted |
| T7 | Implementation boxes checked; task gate box still unchecked | FAIL: public cleanup state, lease release, containment, and normalized residue are incomplete |

The current focused and full gates pass. Their current success does not prove that the same gates ran
before each author commit, because `.specs/features/hybrid-slice-execution/tasks.md:198`, `:223`, and
`:247` remain unchecked.

## Spec-anchored acceptance criteria

| Requirement | Spec-defined outcome | `file:line` + assertion/evidence | Result |
| --- | --- | --- | --- |
| HSE-22 | Persist the complete packet, then send only its pointer. | `tools/orca_assisted_probe.py:1269`-`1274` has the intended ordering. The assigned test prewrites a packet at `tools/test_orca_assisted_probe.py:83`-`87` and invokes `send-pointer` at `:90`-`93`; it never invokes public `dispatch`. Evidence-or-zero leaves the public outcome unproved. | FAIL |
| HSE-23 | Terminal text never contains packet body. | `tools/test_orca_assisted_probe.py:95`-`101` asserts one send, exact pointer, absent body marker, and shorter pointer. `:1176`-`1179` repeats the exact pointer/body exclusion in the lifecycle check. | PASS |
| HSE-24 | Every Orca, Git, and lease mutation is issued at most once per logical operation. | `tools/test_orca_assisted_probe.py:41`-`59` asserts one `create`, `send`, `set`, `stop`, and `rm`. It plans and asserts no Git or lease mutation, despite IT-007 requiring both. | FAIL |
| HSE-25 | A missing/transient mutation response settles through bounded reads without mutation retry. | `tools/test_orca_assisted_probe.py:24`-`59`, `:126`-`163`, and `:221`-`245` prove bounded reads and one-shot Orca effects. No equivalent assertion covers Git or lease effects, and public `inspect` performs only one semantic `terminal show` at `tools/orca_assisted_probe.py:1295`. | FAIL |
| HSE-26 | Accept an effect only after repository, worktree, handle, route, task, operation, commit, and lease correlation. | `tools/orca_assisted_probe.py:1287`-`1302` checks field presence and terminal handle only. A fake diagnostic supplied foreign route/task/operation/commit/lease values plus the expected handle; `inspect` wrote `status=settled`. No assertion proves the full identity tuple. | FAIL |
| HSE-27 | Malformed, stale, reused, or contradictory provider/Git evidence fails closed and remains cleanable. | `tools/test_orca_assisted_probe.py:349`-`401` covers route tokens and part of receipt shape. It does not contradict route, task, operation, commit, and lease in one accepted effect. The diagnostic above demonstrates acceptance instead of fail-closed behavior. | FAIL |
| HSE-28 | Cleanup stops only the proven worker, releases only correlated leases, removes owned clean worktree/ref, and reports residue zero. | Private-receipt cleanup checks at `tools/test_orca_assisted_probe.py:480`-`559` and `:1003`-`1181` prove owned stop/rm/ref behavior. `tools/orca_assisted_probe.py` contains no provider release operation. Public `cleanup --state` routes the dispatch state into `_receipt` at `:1305`-`1315`; a fake run fails `receipt missing id` because dispatch state lacks cleanup receipt fields. | FAIL |
| HSE-29 | Import performs zero Orca, Git, provider, or filesystem-mutation calls. | `tools/test_orca_assisted_probe.py:114`-`123` asserts importing adds no fake call. Independent fake-PATH import exited 0 with `orca_calls=0`. Guard is `tools/orca_assisted_probe.py:1440`-`1441`. | PASS |
| HSE-39 | Every executable, packet, state, worktree, and cleanup path is repository-owned, non-symlinked where required, and fixed argv. | `_owned_path` contains packet/log at `tools/orca_assisted_probe.py:1203`-`1216`, but `dispatch` resolves `state_path` without repository containment at `:1228`-`1231`. A fake diagnostic used a repository-owned request and sibling state path; output was `outside_state_written=True`. | FAIL |
| HSE-41 | Persist immutable identities sufficient to reconcile the same external effect. | Dispatch stores the identity tuple at `tools/orca_assisted_probe.py:1246`-`1260` and rejects changed replay identity at `:1261`-`1268`. No assigned assertion exercises this, and `inspect` does not use most identities to reconcile observations. | FAIL |
| HSE-43 | Missing ownership, integration, clean tree, stop, lease release, branch/ref removal proof stops before destruction and reports residue. | `tools/test_orca_assisted_probe.py:661`-`796` proves several private cleanup refusals and residue checks. There is no lease-release proof, and public failures exit as `FAIL_CLOSED` text at `tools/orca_assisted_probe.py:1432`-`1437`, not the normalized residue object promised by the CLI contract. | FAIL |
| HSE-47 | Reused handle or worktree path for another repository/slice/operation is rejected before cleanup. | `tools/test_orca_assisted_probe.py:687`-`700` asserts moved handle and wrong instance cause zero mutations. No assertion supplies a reused worktree path for a different slice/operation, and the public state-to-cleanup path cannot reach this proof. | FAIL |

**Spec result:** 2/12 scoped requirements fully matched, 10/12 have evidence or implementation gaps,
0 spec-precision gaps.

## Exact public state and cleanup outcome

The fake diagnostic called public `dispatch` with a repository-owned request and an outside sibling
state path. It emitted this persisted field set:

```text
commit_id,lease_id,log_path,operation_id,packet_path,repository,repository_root,route,
schema_version,send_ok,slice_id,status,task_id,terminal_handle
```

`cleanup --state` needs `_receipt` fields `id`, `instance`, `path`, `branch`, `pre_head`, `gitdir`,
`worktree_gitdir`, `startupTerminal`, and `before`. None are produced by `dispatch`. Observed outcome:

```text
outside_state_written= True
cleanup_state_result= ProbeError: receipt missing id
```

The separate inspect diagnostic persisted `settled` for arbitrary `FOREIGN` route, slice, task,
operation, commit, and lease values when the terminal handle matched.

## Gates

- `python3 tools/test_orca_assisted_probe.py`: exit 0; 34/34 checks passed.
- `npm_config_offline=true npm run test:all`: exit 0. Vitest reported 8/8 files and 111/111 tests
  passed. All 14 discovered Python suites exited 0. No failure or skip was reported.
- `rg -n '^[[:space:]]*def test_' tools -g 'test_*.py' | wc -l`: 295 current definitions.
- `git grep -nE '^[[:space:]]*def test_' 2cb70ba -- tools | wc -l`: 261 base definitions; delta +34.
- `git diff --diff-filter=D --name-only 2cb70ba..9457cf6 -- 'tools/test*' | wc -l`: 0 deleted test files.

## Discrimination sensor

All mutations ran in one detached disposable worktree at `9457cf6`, one at a time. The focused suite
failed for every fault. The scratch diff was clean before removal.

| Mutation | Fault | Result |
| --- | --- | --- |
| M1 | Replaced pointer text in `terminal send --text` with full packet body. | KILLED: exact-pointer assertion at `tools/test_orca_assisted_probe.py:1178` failed; exit 1. |
| M2 | Disabled the mutation short-circuit so transient post-effect failures retried each Orca mutation. | KILLED: expected mutation count 5 at `tools/test_orca_assisted_probe.py:57` failed; exit 1. |
| M3 | Bypassed immutable cleanup ownership comparison. | KILLED: wrong-instance case unexpectedly completed cleanup at `tools/test_orca_assisted_probe.py:695`-`700`; exit 1. |

**Sensor result:** 3/3 killed, 0 survived. Real porcelain remained unchanged. Worktree count returned
to exactly 2.

## Code quality and test ownership

The stdlib-only choice and guarded import match project conventions. The implementation is not yet
minimal relative to its frozen public surface:

- `tools/orca_assisted_probe.py` is 1,441 lines with 59 top-level symbols and 18 CLI subcommands.
- `.specs/features/hybrid-slice-execution/dx.md:90`-`92` defines only 3 public subcommands.
- `rg -l 'orca_assisted_probe\.py' --glob '!tools/orca_assisted_probe.py' --glob '!tools/test_orca_assisted_probe.py' --glob '!*.md' . | wc -l` reports 0 runtime consumers outside its own suite.
- Tests such as `tools/test_orca_assisted_probe.py:979`-`1000` and `:1003`-`1181` pre-implement
  dependency synchronization and a fixture-shaped `A_FINAL`/`B_FINAL` journey assigned to later
  slices, rather than only T5-T7's assigned test IDs.

Large lifecycle code can remain when each command is wired to the public state machine and claimed
by a requirement. Until then, the extra 15 subcommands and fixture-shaped checks are unclaimed
surface, not proof of CP-S4.

## Ranked gaps and fingerprints

1. **Blocker:** Public dispatch state cannot drive cleanup; cleanup has no correlated lease release
   or normalized zero-residue result. Fingerprint
   `d11da16b460c9514ef870fea56f469cb35ea657f77cdd7a9bbfd3d2eafb6b9f0` is open at failed-remediation count 1.
2. **Blocker:** `inspect` accepts an effect from a matching handle without independently correlating
   route, task, operation, commit, lease, repository, and worktree identity. Fingerprint
   `49092771bac5f9461878129cc1518db120787ec6944d2f7d3abf81e2258fab0b` is open at count 1.
3. **Major:** State containment and the complete exact-once ledger are unproved: state can escape the
   repository, and Git/lease mutations are absent from IT-007/SEC-006 assertions. Fingerprint
   `a83ca4d68afa5e45916eae7606c22e6dd57444470bea7b13cfb916684e98bbfd` is open at count 1.

Fingerprint state now contains 15 total entries: 12 closed and these 3 open.

## Fix tasks

1. Make `dispatch`, `inspect`, and `cleanup` share one strict persisted schema containing exact
   repository/worktree/handle/route/task/operation/commit/lease ownership and receipt paths. Exercise
   the three public commands as one fake-provider lifecycle.
2. Reconcile every identity against independent bounded Orca, Git, and provider observations before
   `settled`; reject malformed, stale, reused, moved, or contradictory observations.
3. Add correlated lease acquire/release and residue reporting, contain request/state/receipt/log/
   packet paths, and extend IT-007/IT-008/IT-010 plus SEC-001/SEC-006/SEC-008 with exact Git and lease
   mutation counts. Remove or defer CLI paths not used by that lifecycle.

## Distilled lessons

The grounded AC gaps produced candidate lessons L-021 through L-023: exercise public lifecycle
commands through one state artifact, correlate persisted external identities independently, and
assert repository containment for every writable control path.

## Summary

**Overall:** FAIL. CP-S4 must not release to S3 or S6. Gates are green and all three mutants were
killed, but the canonical suite proves private helpers and historical fixture mechanics instead of
the complete public lifecycle promised by HSE-22 through HSE-28.
