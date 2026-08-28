# Hybrid Slice Execution S5 Validation

**Verdict:** FAIL
**Date:** 2026-08-28
**Phase:** Technical
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Diff range:** `6f184f3..b7c1c92`
**Verifier:** independent session, author != verifier

## FAIL

The provider packets state the intended author, tree, and phase boundaries, but CP-S5 is not
releasable. IT-012 constructs the expected two-slice trace as a literal inside the test instead of
deriving it from the shipped coordinator policy or an executable route. A mutation that changed the
shipped policy to author self-verification plus private-tree Deep Review and QA survived the focused
suite. This violates the non-hollow assertion rule in `docs/guidelines/TEST-CONTRACT.md`.

## Task completion

| Task | Recorded state | Verification result |
| --- | --- | --- |
| T8 | Done | FAIL: static provider packets pass, but the assigned integration proof is hollow |

## Spec-anchored acceptance criteria

| Requirement | Spec-defined outcome | `file:line` + assertion/evidence | Result |
| --- | --- | --- | --- |
| HSE-30 | One slice's tasks run sequentially; each task ends with scoped gate and atomic commit. | `templates/agents/codex/implementer.toml:25`-`:30` carries the boundary. `tools/shared/tests/autonomous-parallelization.test.ts:28`-`:39` asserts the same contract for Claude, Codex, and Cursor and rejects global ownership, `Batch complete`, and final QA. | PASS |
| HSE-31 | A fresh Technical Verifier reads the private writer checkpoint before a dependent slice consumes it. | `templates/agents/codex/verifier.toml:25`-`:29` states fresh identity and private checkpoint. `tools/shared/tests/autonomous-parallelization.test.ts:42`-`:51` asserts the packet wording, but no test derives checkpoint ordering from the shipped coordinator policy. | GAP |
| HSE-32 | Fresh Deep Review reads the integrated commit range, never a writer's private tree. | `templates/agents/codex/deep-reviewer.toml:16`-`:21` states the correct boundary. `tools/shared/tests/autonomous-parallelization.test.ts:53`-`:59` asserts all provider packets, but IT-012 supplies its own integrated tree constant. | GAP |
| HSE-33 | Fresh QA Plan and QA Execute sessions read the final integrated tree after implementation review. | `templates/agents/codex/verifier.toml:30`-`:31` and `:39`-`:54` state separate QA phases and final integrated tree. `tools/shared/tests/autonomous-parallelization.test.ts:69`-`:71` hard-codes the desired actors/tree rather than observing the shipped route. | GAP |
| HSE-34 | Last implementer emits only compact handoff and performs no proof phase. | `templates/agents/codex/implementer.toml:30`-`:38` limits the final report to handoff. `tools/shared/tests/autonomous-parallelization.test.ts:72` and `:91`-`:95` hard-code the desired final trace row rather than deriving it from the role contract. | GAP |

**Spec result:** 1/5 scoped requirements has discriminating end-to-end contract evidence; 4/5 retain
correct static packet text but lack the assigned non-hollow integration proof. There are 0
spec-precision gaps.

## Provider and generated packet parity

- `python3 .agents/skills/workflow-config/scripts/workflow_config.py --root . --sync-agents` exited
  0 with `changed: []` and all 15 generated role packets listed under `unchanged`.
- Direct byte comparisons found no drift for Implementer, Verifier, or Deep Reviewer across Claude,
  Codex, and Cursor.
- The packets contain no `one implementer at a time`, `one implementer globally`, `Batch complete`,
  or implementer-owned final QA contract.

## Gates

- `npm_config_offline=true npx vitest run tools/shared/tests/autonomous-parallelization.test.ts`:
  exit 0; 1/1 file and 5/5 tests passed.
- `npm_config_offline=true npm run test:all`: exit 0. Vitest reported 8/8 files and 114/114 tests;
  every discovered Python suite exited 0. No skip or failure was reported.
- `git diff --numstat 6f184f3..b7c1c92 -- tools/shared/tests/autonomous-parallelization.test.ts`:
  92 additions, 0 deletions; no prior assertion was weakened or removed.
- `git diff --check 6f184f3..b7c1c92`: exit 0.

## Discrimination sensor

Every mutation ran in a detached disposable worktree at `b7c1c92`. The first three mutate all three
provider templates. The fourth targets the shipped coordinator policy that IT-012 claims to cover.

| Mutation | Fault | Focused result |
| --- | --- | --- |
| M1 | Reuse the slice author as Technical Verifier and read the integrated tree instead of the private checkpoint in Claude, Codex, and Cursor packets. | KILLED: UT-016 failed at `autonomous-parallelization.test.ts:46`; exit 1. |
| M2 | Give each Implementer Deep Review and final QA ownership in Claude, Codex, and Cursor packets. | KILLED: UT-015 failed at `autonomous-parallelization.test.ts:38`; exit 1. |
| M3 | Make each Deep Reviewer inspect a private writer tree instead of the integrated tree. | KILLED: UT-016 failed at `autonomous-parallelization.test.ts:57`; exit 1. |
| M4 | Replace the coordinator policy's independent private-checkpoint verification and integrated Review/QA route with author self-verification and private-tree Review/QA. | **SURVIVED:** focused suite remained 5/5 green; exit 0. |

**Sensor result:** 3/4 killed, 1/4 survived. After cleanup,
`git worktree list --porcelain | rg '^worktree' | wc -l` returned `2`, matching the baseline, and
`git status --porcelain` was empty before this report.

## Ranked gap

1. **Major — IT-012 is a self-fulfilling trace, not integration evidence.**
   `tools/shared/tests/autonomous-parallelization.test.ts:62`-`:102` creates the desired actors,
   trees, ordering, and handoff inside the test and then asserts those same constants. It never reads
   `.agents/skills/autonomous/references/parallelization.md`, materializes role packets through the
   sync route, or executes a route function. Consequently, the shipped coordinator policy can assign
   Technical Verification, Deep Review, and QA to the author/private tree while IT-012 remains green.
   Fix task: make the canonical suite derive a two-slice route from one shipped source of truth and
   assert exact actor identity, checkpoint ordering, integrated head, final QA sessions, and
   handoff-only termination. The new test must kill M4 without weakening UT-015 or UT-016.

**Immutable fingerprint:**
`7d9532f88245a6eda11122ed91fa5e910eb20ccaa69016b49177a71e015b993f`, generation 1, failed
remediations 1, status `open`.

## Code quality and isolation

The template changes are small, provider-aligned, and synchronized. No unnecessary dependency or
abstraction was added. The failure is test integrity, not packet wording. No live Orca command ran.
No source, test, or configuration fix was made by this Verifier.

## Summary

**Overall:** FAIL. CP-S5 must not release to dependent delivery work until the shipped routing source
drives IT-012 and the surviving policy mutation is killed.
