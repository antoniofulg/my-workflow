# Task 04 — Publish the Slice Planning Contract

- Assumptions: the validated closure table is the planning authority; `--slices` remains an
  optional assertion, while phase/cohort and batch describe downstream organization/capacity.
- Files: TLC task template, workflow-config skill, README contract examples, structural tests,
  this memory, `tasks.md`, and `spec.md` traceability.
- Success: agents can declare one `Slice` per primary task plus a closure row, resolver docs show
  validated derivation, public examples omit manual ownership, and structural/adoption gates pass.
- Gate: `npm test && python3 scripts/test_adopt.py` passed; Bun/npm reported 116 tests across 8
  files and the adoption suite exited 0.
- Adequacy: the structural contract asserts template vocabulary and public docs at
  `tools/shared/tests/workflow-config.test.ts:42-63`; the template, resolver skill, and README
  carry the same derived-count boundary without adding a new dependency.
- Status: complete; no instruction word-budget deviation was introduced.
