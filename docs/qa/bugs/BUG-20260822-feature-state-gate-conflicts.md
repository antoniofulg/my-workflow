# BUG-20260822-feature-state-gate-conflicts

- **Status:** fixed — retest passed
- **Severity:** major
- **Scenario:** `CFG-keep-local-artifacts-out-of-git`; `ADP-adopt-workflow-safely`
- **Expected:** The full gate accepts `.specs/features/` as versioned workflow state so public QA can
  verify adoption, Git handoff, and atomic task-status commits.
- **Observed:** `npm test` fails because `IT-015` still asserts that
  `.specs/features/qa-skills/tasks.md` is absent from Git.
- **Adapter:** repository-declared Vitest preflight
- **Exact path:** `npm test`
- **Evidence:** `docs/qa/evidence/2026-08-22-version-feature-state-by-default/session.md`
- **Fix commit:** `5b5474e`
- **Retest:** passed on 2026-08-22; `npm test` reported 11 files and 144 tests passed before the
  resumed public charter

## Reproduction

1. Check out `fix/version-feature-state` at `a3fc718`.
2. Run `npm test`.
3. Observe the lone failure in `IT-015 treats the local task state as the commit precondition`.

## Smallest remediation

Replace the retired untracked-state assertion and its stale test-contract wording with the issue
#31 invariant: feature task state is versioned, and its status change can share the atomic task
commit. Keep the existing ordering assertions that require task state to close before commit.

## Fix and retest

`5b5474e` replaced the retired assertion. Fresh QA confirmed the full gate, then proved a completed
`tasks.md` status and its observable task output travel in the same commit to a sibling worktree and
clean clone.
