# Merge-Alone Slice Memory

- The validator owns the closure contract; resolver and downstream planning consume its validated
  primary-task membership.
- Snapshot schema stays at the resolver's current version (3); this feature adds no field. Resume returns the frozen snapshot before reading current task
  files; refresh is the explicit re-derivation path.
- No new dependency or compatibility parser is in scope.
- `parallel_plan.py` reads bold-colon fields (`**Slice:**`, `**Status:**`, `**Resources:**`,
  `**Depends on:**`); the validator must accept exactly `**Slice:**` so both readers agree.
- Existing `docs/qa/scenarios/*` are frozen by `IT-006` (`historicalQaBaseline`); new promises get a
  new scenario file, never an edit.
- The 2026-08-27 implementation lives at `3ce7a2e` (`git show 3ce7a2e:<path>`); port its rules, not
  its `tlc-spec-driven` paths or schema-v2 checks.
