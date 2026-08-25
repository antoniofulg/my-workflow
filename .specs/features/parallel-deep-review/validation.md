# Parallel Deep Review Validation

**Date**: 2026-08-25
**Spec**: `.specs/features/parallel-deep-review/spec.md`
**Diff range**: `da5571e..ffc7c21`
**Verifier**: independent verifier (author != verifier)
**Verdict**: PASS

---

## Task Completion

No `tasks.md` or `tests.md` exists in this packet. All six requirement traceability rows in
`spec.md` are complete. This verification independently maps all 12 acceptance criteria and five
listed edge cases to exact assertions.

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| P1.1 default | Manifest concurrency is exactly `3`. | `tools/test_deep_review_contract.py:288-290` — successful build and `self.assertEqual(...["concurrency"], 3)`. | PASS |
| P1.2 repository config | Every integer from `1` through `6` is accepted and persisted. | `tools/test_deep_review_contract.py:295-299,304-308` — configured `5` and lower boundary `1` both build and persist exactly; boundary-rejection mutants for `1` and `6` are killed by the combined config/CLI case. | PASS |
| P1.3 CLI precedence | CLI overrides repository config with every integer from `1` through `6`. | `tools/test_deep_review_contract.py:300-312` — config `5` overridden to `2`, and CLI upper boundary `6` persists exactly; lower/upper boundary mutants are killed. | PASS |
| P1.4 invalid input | Boolean, below `1`, above `6`, quoted string, and non-integer values are rejected before dispatch. | `tools/test_deep_review_contract.py:314-320` — `true`, `false`, `0`, `7`, `"3"`, and `1.5` each require non-zero exit. | PASS |
| P1.5 bounded dispatch | Peak active reviewers is `min(concurrency, pending)` and real overlap occurs at bounds `3` and `6`. | `tools/test_deep_review_token_metrics.py:224-247` — overlap exists at `(3,3)` and `(6,6)`; `:251-269` — exact peak for `(3,8)`, `(6,8)`, and `(6,2)`. | PASS |
| P1.6 deterministic output | Run status, validate-only status, merge, and report remain manifest-order deterministic under inverted completion. | `tools/test_deep_review_token_metrics.py:437-451` — captures and asserts run status before validate-only, then asserts validation rows; `:456-471` — exact run equality plus distinct finding/advisory titles, source jobs, raw IDs, findings JSON, report equality, and report inclusion. | PASS |
| P2.1 retry slot | Retries stay inside one worker slot while siblings continue. | `tools/test_deep_review_token_metrics.py:273-293` — exact peak `3`, attempts `[2,1,1,1,1]`, and complete call multiset; `:577-599` — overlap, exact two-attempt calls, ordered attempts, and complete metrics. | PASS |
| P2.2 provider block | Stop scheduling, finish active attempts, exit `2`, retain first reason, and ledger every unfinished job. | `tools/test_deep_review_token_metrics.py:321-349` — exact exit, only active starts, first reason/label, full pending ledger; `:353-376` — direct no-submit assertions; `:938-947` — active sibling completion and manifest-order status. | PASS |
| P2.3 resume | Valid outputs are preserved; only missing, blocked, or invalid jobs execute. | `tools/test_deep_review_token_metrics.py:603-619` — second run leaves provider call count at one; `:949-954` — resume skips the valid active sibling and runs only unfinished jobs. | PASS |
| P2.4 source drift | Active jobs finish, then exit `3` without accepting a valid review. | `tools/test_deep_review_token_metrics.py:380-412` — exact exit `3`, drift message, both calls, and both output artifacts. | PASS |
| P2.5 metrics | Cumulative checkpoints are serialized, omit job attribution, and finalize only after full scope. | `tools/test_deep_review_token_metrics.py:224-247,473-489` — exact checkpoint order and no `job`; `:623-654` — partial scope remains `running`, full scope finalizes with exact cumulative total and checkpoints. | PASS |
| P2.6 legacy option | `--workers` is rejected. | `tools/test_deep_review_contract.py:322-328` — invocation with `--workers 2` must exit non-zero. | PASS |

**Status**: 12/12 acceptance criteria match precise spec outcomes with assertion evidence.

## Edge Cases

| Edge case | Evidence | Result |
| --- | --- | --- |
| Fewer pending jobs than concurrency | `tools/test_deep_review_token_metrics.py:251-269` includes `(6,2)` and asserts peak `2`. | PASS |
| Ordinary failure continues siblings | `tools/test_deep_review_token_metrics.py:297-317` asserts all five calls and statuses `fail, pass, pass, pass, pass`. | PASS |
| Multiple blocks preserve first reason | `tools/test_deep_review_token_metrics.py:321-349` asserts `BLOCK-A` / `job-1` despite later `BLOCK-B`. | PASS |
| `--only` retains full-scope metrics | `tools/test_deep_review_token_metrics.py:623-654` asserts partial `running`, then cumulative finalization. | PASS |
| Old valid output is not rerun | `tools/test_deep_review_token_metrics.py:603-619` asserts one provider call across two runs. | PASS |

## Discrimination Sensor

Scratch: detached temporary worktree at `ffc7c21`; removed after the run. Source files were restored
byte-for-byte before cleanup. Real checkout porcelain was
`?? .specs/features/parallel-deep-review/validation.md` before sensor work and remains the same
single path after cleanup.

| # | Behavior mutation | Focused result |
| ---: | --- | --- |
| 1 | Default concurrency `3` -> `2` | KILLED |
| 2 | Ignore repository concurrency | KILLED |
| 3 | Ignore CLI precedence | KILLED |
| 4 | Accept quoted integer config | KILLED |
| 5 | Accept boolean config | KILLED |
| 6 | Accept concurrency `0` | KILLED |
| 7 | Accept concurrency `7` | KILLED |
| 8 | Accept legacy `--workers` | KILLED |
| 9 | Force serial executor | KILLED |
| 10 | Submit only one initial job | KILLED |
| 11 | Disable ordinary refill | KILLED |
| 12 | Reverse run-mode status rows | KILLED |
| 13 | Disable configured retries | KILLED |
| 14 | Stop refill after ordinary failure | KILLED |
| 15 | Continue provider dispatch after block | KILLED |
| 16 | Overwrite first provider-block reason | KILLED |
| 17 | Rerun already-valid output | KILLED |
| 18 | Skip post-run source-freeze check | KILLED |
| 19 | Drop cumulative checkpoints | KILLED |
| 20 | Increment checkpoint count by two | KILLED |
| 21 | Finalize metrics with incomplete full scope | KILLED |
| 22 | Add per-job checkpoint attribution | KILLED |
| 23 | Reverse validate-only status rows | KILLED |
| 24 | Merge distinct outputs by completion mtime | KILLED |
| 25 | Reject valid lower boundary `1` across config/CLI | KILLED |
| 26 | Reject valid upper boundary `6` across config/CLI | KILLED |

**Sensor depth**: 26 behavior mutations, 26 killed, 0 survived. The prior three survivors — run-mode
status reversal and valid boundaries `1` / `6` — are closed. **PASS**.

## Gate Check

- `python3 tools/test_deep_review_contract.py` — 10 passed, 0 failed, 0 skipped.
- `python3 tools/test_deep_review_token_metrics.py` — canonical sequential rerun: 28 passed, 0 failed, 0 skipped.
- `npm test` — 7 files passed; 108 passed, 0 failed, 0 skipped.
- `git diff --check da5571e..ffc7c21` — exit 0.
- `python3 .../tlc-spec-driven/scripts/validate_spec.py .specs/features/parallel-deep-review/spec.md` — 0 errors, 0 warnings.
- Aggregate canonical current count: 146 passed.
- Focused baseline at `da5571e`: 8 contract + 19 runner/metrics = 27 passed.
- Focused current at `ffc7c21`: 10 contract + 28 runner/metrics = 38 passed; delta `+11`.
- Diagnostic: first non-canonical parallel invocation of both Python suites produced one missing
  retry-overlap marker. Exact sequential rerun passed 28/28, and the affected test then passed 10/10
  consecutive focused repetitions. No failure reproduced under the documented gate command.
- `npm run lint` and `npm run typecheck` do not exist in `package.json`; no result claimed.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum, surgical implementation | PASS |
| No unrelated product scope | PASS |
| Existing Python stdlib and project patterns | PASS |
| Spec-anchored outcomes, including both valid boundaries | PASS |
| Run and validation status asserted before overwrite | PASS |
| Distinct findings/advisories discriminate completion-order merge and report | PASS |
| Every in-scope test maps to an AC, edge case, or existing metrics contract | PASS |
| Guideline | `docs/guidelines/TEST-CONTRACT.md:53-55` contracted-outcome rule satisfied | PASS |

## Requirement Traceability

| Requirement | Verification |
| --- | --- |
| PDR-01 | PASS |
| PDR-02 | PASS |
| PDR-03 | PASS |
| PDR-04 | PASS |
| PDR-05 | PASS |
| PDR-06 | PASS |

## Summary

**Overall**: PASS — technically ready for the next workflow gate.

**Spec-anchored check**: 12/12 ACs matched, 0 spec-precision gaps.

**Sensor**: 26/26 mutations killed.

**Gate**: 146 canonical tests passed; 0 failed; 0 skipped.

**Ranked gaps**: none. Iteration-cap blockers: none.
