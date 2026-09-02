# Task 03 — Preserve Resume and Refresh Semantics

- Assumptions: an existing valid snapshot is authoritative on normal resume; only explicit
  `refresh=True` revalidates current Tasks and replaces the snapshot.
- Files: resolver lifecycle tests, this memory, `tasks.md`, and `spec.md` traceability; production
  code changes only if the lifecycle gate identifies a gap.
- Success: resume returns the frozen v2 snapshot despite changed/malformed Tasks and count input;
  refresh derives current closure slices and preserves the existing snapshot schema.
- Gate: `python3 tools/test_workflow_config.py` passed with 51 tests.
- Adequacy: resume invariance and byte preservation are asserted at
  `tools/test_workflow_config.py:234-253`; refresh re-derivation and v2 schema preservation are
  asserted at `:256-277`. Existing atomic replacement coverage remains in the resolver suite.
- Status: complete; no production lifecycle change was needed because the current resume branch
  already precedes task derivation and refresh uses the same atomic writer.
