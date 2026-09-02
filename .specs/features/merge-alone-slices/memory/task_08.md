# DR1 — Align Canonical Slice Task Syntax

- Assumptions: planner syntax is authoritative for primary tasks; nested `#### T<number>:` phase
  outlines remain supported only as planning annotations before the canonical Task Breakdown.
- Files: validator, TLC task template, canonical validator/structural tests and fixtures, this
  memory, feature task/spec/STATE bookkeeping.
- Success: validator and planner accept the same canonical task shape, reject malformed primary
  headings and unbolded Slice fields, reject backtick-only gates, and template examples carry one
  Slice field each.
- Gates: `python3 tools/test_tlc_validators.py` (17 passed), `python3 tools/test_parallel_plan.py`
  (19 passed), structural Bun test (6 passed), adoption (exit 0), and `npm run test:all` (exit 0,
  116 Bun tests plus the Python lanes).
- Adequacy: `tools/test_tlc_validators.py:61-66` validates nested phase outlines with canonical
  Task Breakdown definitions; `:69-81` rejects planner-incompatible headings and unbolded Slice;
  `:132-155` rejects normalized-empty gates with slice identity. The structural assertions at
  `tools/shared/tests/workflow-config.test.ts:64-72` require exactly one Slice field in every
  template task example. No QA artifacts, technical validation report, review fingerprints, or
  unrelated files changed.
- Status: complete; no spec deviation. Ready for final Deep Review.
