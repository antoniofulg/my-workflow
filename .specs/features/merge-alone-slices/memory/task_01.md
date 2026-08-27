# Task 01 — Validate Merge-Alone Slice Closures

- Assumptions: primary `T<number>` tasks are the only slice-count inputs; remediation records stay
  outside the primary membership contract.
- Files: validator, canonical validator fixtures/tests, parallel-plan regression, this memory,
  `tasks.md`, and `spec.md` traceability.
- Success: valid one- and two-slice contracts emit deterministic JSON; malformed closure and
  membership inputs fail with named evidence; downstream `Slice` membership remains unchanged.
- Gate: `python3 tools/test_tlc_validators.py && python3 tools/test_parallel_plan.py` passed with
  16 validator tests and 19 planner tests.
- Adequacy: validator assertions cover one slice (lines 98-105), two slices/remediation exclusion
  (107-110), closure fields and exact `yes` (112-131), membership (133-144), duplicate/orphan rows
  (146-154), deterministic JSON (156-165), and planner preservation (tools/test_parallel_plan.py:
  87-99).
- Status: complete; no spec deviation.
