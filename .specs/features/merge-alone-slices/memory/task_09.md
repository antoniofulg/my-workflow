# DR2 — Reject Malformed and Leaking Task Headings

- Assumptions: canonical `### T<number>:` definitions are the only primary task inputs; canonical
  remediation headings can carry their own fields but never belong to primary membership/count.
- Files: validator, merge-alone validator fixture/tests, this memory, feature task/spec/STATE
  bookkeeping.
- Success: remediation headings reset primary parsing context, and a missing-colon primary-looking
  heading fails explicitly even when later valid tasks remain.
- Gates: `python3 tools/test_tlc_validators.py` (17 passed), `python3 tools/test_parallel_plan.py`
  (19 passed), `python3 tools/test_workflow_config.py` (54 passed), and `npm run test:all` (exit 0,
  116 Bun tests plus all Python lanes).
- Adequacy: `tools/test_tlc_validators.py:124-131` exercises both remediation headings with their
  own Slice fields while asserting only primary membership/count; `:69-82` includes `### T1`
  without a colon alongside later valid tasks and requires the explicit syntax error. The parser
  reset is at `validate_tasks.py:111-113`, and missing-colon detection is at `:152-157`.
- Status: complete; no spec deviation. Final QA Plan and Execute are next. The technical validation
  report, fingerprints, lessons, and QA records remain immutable.
