# QA1 — Consume the Active Workflow Snapshot Version

- Assumptions: workflow configuration's version-2 snapshot is the current interface; planner,
  executor, and pilot reject version 1 without migration. Runtime, plan, result, and lifecycle
  schemas remain version 1.
- Files: parallel planner/executor/pilot, their canonical tests/reference, this memory, QA1 feature
  bookkeeping, and the implementation validation note.
- Success: resolver output reaches the planner with unchanged membership, all parallel consumers
  accept v2 and reject v1, and the disposable pilot uses v2. This is implementation evidence, not a
  QA pass.
- Gates: targeted planner/executor/resolver suites and adoption passed; pilot/full gates run after
  the atomic commit so the disposable fixture checks out the committed v2 code.
- Closure is pending the post-commit gates and fresh independent verification.
