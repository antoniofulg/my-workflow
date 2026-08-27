# BUG-20260827-parallel-plan-rejects-workflow-v2

- **Status:** open
- **Severity:** major
- **Scenarios:** `CFG-plan-parallel-slice-dispatch`
- **Expected:** A workflow snapshot created by the public `workflow_config.py` resolver is accepted
  by the public `parallel_plan.py` planner, which reports the same primary-task Slice membership and
  slice IDs as `validate_tasks.py --slice-contract-json`.
- **Observed:** `workflow_config.py` creates a version 2 `workflow.json`, then `parallel_plan.py`
  exits 1 with `parallel plan: invalid workflow snapshot` because its snapshot reader accepts only
  version 1. No planner membership is returned.
- **Adapter:** CLI/manual in a checkout-owned disposable Git repository, confirmed by a read-only
  replay against the active checkout.
- **Exact path:** resolve a feature through `workflow_config.py` -> independently reload
  `workflow.json` and observe `version: 2` -> invoke `parallel_plan.py --root <repo> --feature
  <feature>` -> observe exit 1.
- **Evidence:** `docs/qa/evidence/2026-08-27-merge-alone-slices/planner-resolve.json`;
  `docs/qa/evidence/2026-08-27-merge-alone-slices/defect-reproduction.exit`;
  `docs/qa/evidence/2026-08-27-merge-alone-slices/defect-reproduction.stderr.log`;
  `docs/qa/evidence/2026-08-27-merge-alone-slices/defect-independent-read.log`

## Reproduction

1. In a disposable Git repository adopted from this checkout, create valid two-slice `tasks.md`.
2. Run the public resolver with `--slices 2`; it succeeds and writes snapshot version 2.
3. Run the public read-only planner for the same feature.
4. Observe exit 1 and `parallel plan: invalid workflow snapshot` before any membership is emitted.

## Remediation recommendation

Make the resolver and planner share one supported workflow snapshot version. Add a public-path
integration regression that feeds an actual resolver-created snapshot directly to the planner and
asserts validator/planner membership equality, rather than constructing a planner-only snapshot.
A fresh Technical Verifier must run the feature gate, then a fresh QA Execute must resume the
affected charter and adjacent adoption canary.
