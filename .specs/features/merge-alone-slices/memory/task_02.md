# Task 02 — Derive Initial Workflow Slice Count

- Assumptions: initial resolution and explicit refresh may read the validated closure contract;
  normal resume remains snapshot-first. Missing `tasks.md` means one slice.
- Files: workflow resolver, resolver contract tests/fixtures, this memory, `tasks.md`, and `spec.md`
  traceability.
- Success: valid one- and two-slice tasks derive counts; malformed tasks and invalid/mismatched
  assertions fail before snapshot replacement; absent Tasks derives one slice.
- Gate: `python3 tools/test_workflow_config.py` passed with 49 tests.
- Adequacy: resolver assertions cover one derived slice (tools/test_workflow_config.py:174-179),
  two derived slices (184-189), mismatch-before-write (194-204), no-Tasks default (209-213), and
  malformed Tasks-before-write (218-229); derivation is implemented at workflow_config.py:621-643
  and applied before snapshot writing at 788-796.
- Status: complete; no spec deviation.
