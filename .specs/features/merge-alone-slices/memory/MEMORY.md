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
- The port keeps the current `TASK_RE` (`^#{2,4}\s+(T\d+)\s*:`) instead of the old `^###` narrowing;
  `parse_tasks` now clears the current task on any heading so remediation records such as `T2R1`
  cannot donate their fields to the preceding primary task. The old heading-syntax check
  (`_task_breakdown_syntax_errors`) is out of scope — no `tests.md` ID covers it.
- Both merge-alone fixtures pass `check()` clean; the two-slice diagram is two disconnected chains
  (`T1 -> T2`, `T3 -> T4`) so slices A and B stay independent.
- Resolver tests that asserted a manual `--slices` above 1 now write a derived `tasks.md` fixture via
  `write_derived_tasks(root, feature, n)`; tests that pass `--slices 1` with no `tasks.md` are unchanged.
