# T8 task memory

- Provider templates share one boundary: one implementer owns one private slice worktree and runs
  its tasks sequentially, with the scoped gate and atomic commit before the next task.
- Technical verification reads the exact private writer checkpoint in a fresh session; Deep Review
  reads the integrated commit range; fresh QA Plan and Execute read the integrated final tree.
- Author, verifier, reviewer, and QA identities are distinct. The final implementer emits only a
  compact handoff and does not certify downstream proof.
- Contract coverage is in `tools/shared/tests/autonomous-parallelization.test.ts` as UT-015,
  UT-016, and IT-012; active guidance is aligned in autonomous and workflow review references.
- IT-012 derives its trace from the delimited role-route table in
  `.agents/skills/autonomous/references/parallelization.md`; packets remain consumers of that
  single route source, not a second route authority.
- CP-S5 remediation keeps `validation-s5.md` and lesson history immutable; the canonical route
  proof now rejects a changed owner, author relation, tree boundary, or stage order.
