# T7 task memory

- Cleanup validates exact repository/worktree/instance/path/branch/HEAD/Git registration ownership,
  clean and integrated state, stopped terminal, branch/ref removal, and foreign-resource invariance
  before reporting residue zero.
- Any missing, dirty, moved, live, unmerged, foreign, or contradictory proof stops before the next
  destructive effect and retains the unresolved residue.
- Dispatch and cleanup now share schema-2 state plus a normalized receipt; cleanup releases a
  repository-contained owned lease before deleting the branch/worktree and returns `residue: []`.
- Inspect requires repository, slice, task, operation, handle, route, commit, worktree, and lease
  correlation from independent terminal/worktree/Git observations. Mutations have stable effect ids,
  are persisted before issue, and an unknown effect is never reissued on replay.
- The public argparse surface is exactly `dispatch`, `inspect`, and `cleanup`; focused probe contract
  is 15/15 after final remediation; the full offline gate remains required before commit.
- Final remediation extends receipt identity to the full state conjunction, persists cleanup effects
  through pending/issued/unknown/settled records, and covers independent observation contradictions,
  post-effect no-retry ledgers, and fail-closed cleanup unsafe-state tables.
