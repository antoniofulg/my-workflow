# R1 — Close Technical Verifier Evidence Gaps

- Assumptions: the implementation already fails closed in the requested paths; this remediation
  strengthens contract evidence without changing production behavior. The existing validation
  report remains immutable.
- Files: canonical validator/resolver/planner tests, the two-slice fixture, this memory,
  `tasks.md`, `spec.md`, and the project handoff.
- Success: error identity, refresh byte preservation, both remediation shapes, direct validator-to-
  planner membership equality, and non-positive count assertions are all discriminating.
- Gates: `python3 tools/test_tlc_validators.py` (16 passed), `python3 tools/test_workflow_config.py`
  (54 passed), `python3 tools/test_parallel_plan.py` (19 passed), and `npm run test:all` (exit 0,
  with 116 Bun tests and 265 Python checks including the `ad-index.py` pass).
- Adequacy: `tools/test_tlc_validators.py:134-135` asserts the slice identity for each incomplete
  field; `:168-169` asserts the offending task or slice for membership defects; `:175-179` asserts
  duplicate/orphan closure identities; and `:110-114` proves both remediation headings remain out
  of primary membership/count. `tools/test_workflow_config.py:222` asserts the non-positive bound,
  `:250` and `:253` assert refresh mismatch plus byte preservation, and `:274-278` assert malformed
  refresh plus byte preservation. `tools/test_parallel_plan.py:110` compares planner membership
  directly to validator output from the same document. No production behavior changed; no QA
  reports or scenario statuses were in scope.
- Status: complete; no spec deviation. Ready for a fresh Technical Verifier.
