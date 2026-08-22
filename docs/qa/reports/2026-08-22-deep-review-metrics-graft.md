# QA report — Deep Review metrics and Graft

- **Date:** 2026-08-22
- **Scope:** Deep Review serialized metrics, optional Graft context, artifact-hygiene canary
- **Branch:** `feat/deep-review-token-budget`
- **Head at start:** `2832503`
- **Adapter:** CLI/manual through the checkout-local Deep Review scripts and Git/filesystem inspection
- **Environment:** macOS, active isolated checkout `/Users/antoniofulg/Projects/my-workflow`
- **Automated gate before walk:** technical validation PASS at `.specs/features/deep-review-token-metrics/validation.md` (93 automated tests, 0 failed; 3/3 mutations killed)
- **Raw evidence:** `docs/qa/evidence/2026-08-22-deep-review-metrics-graft/`
- **Limitation:** no live model-execution harness; a deterministic fixture provider exercises the public runner contract. No browser, API, mobile, auth, or server surface exists.

## Matrix

| Charter | Scenario | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `CH-run-deep-review-metrics-and-graft-2026-08-22` | `QAS-observe-serialized-deep-review-metrics` | pass | Reload skipped both valid outputs; call order stayed `job-1:1, job-1:2, job-2:1, job-2:2`; ledger delta recomputed as 140 - 100 = 40. | `docs/qa/evidence/2026-08-22-deep-review-metrics-graft/session.md` |
| `CH-run-deep-review-metrics-and-graft-2026-08-22` | `QAS-use-graft-context-with-plain-fallback` | pass | Materialized prompts referenced the ready context; missing and failing pinned CLIs plus dot-directories produced explicit plain-inspection guidance. | `docs/qa/evidence/2026-08-22-deep-review-metrics-graft/session.md` |
| `CH-check-graft-artifact-hygiene-2026-08-22` | `CFG-keep-local-artifacts-out-of-git` | pass | After `b509b10`, fresh adoption ignored Graft cache/graph files, preserved consumer ignores, retained durable workflow files as reviewable, and kept cards searchable. | `docs/qa/evidence/2026-08-22-deep-review-metrics-graft/session.md`; `BUG-20260822-adoption-omits-graft-ignores` |

## Session results

Twelve probe groups covered CLI discoverability, two-job retry serialization, overlap detection,
compatible totals, content safety and file mode, reload/resume, unavailable telemetry, real pinned
Graft materialization, missing and failing Graft fallbacks, dot-directory guidance, and adoption
artifact hygiene. Metrics and Graft scenarios passed. The adjacent adoption canary found one product
defect: adoption omits the Graft Git/search-ignore contract.

Comprehension, recovery, trust, speed, language, and text-interface accessibility lenses found no
additional divergence. No browser/UI surface exists.

## Retest after `b509b10`

Fresh technical validation was PASS before QA. The affected artifact-hygiene journey passed in a
new disposable Git target: both Graft cache paths were ignored, the card remained visible to `rg`,
managed entries occurred exactly once, consumer Git/search sentinels survived, and durable
learnings/decision files stayed reviewable. The adjacent Graft canary also passed: pinned Graft
`0.10.1` produced a ready context linked from all four prompts, dot-directories retained explicit
plain-inspection guidance, and a target without the pinned CLI returned `fallback` without error.

Two adapter checks needed one clean retry. A zsh loop variable named `path` cleared command lookup;
the corrected retry passed. A JSON probe initially treated the `jobs.json` object as an array; the
corrected probe confirmed 4/4 prompts. Neither stall reached or changed product behavior.

## Final gate

PASS. Exact command:

`python3 scripts/test_adopt.py && python3 tools/test_ad_index.py && python3 tools/test_deep_review_token_metrics.py && python3 tools/test_workflow_config.py && npm test && npm run knowledge && git diff --check origin/main..HEAD`

Result: 33 Python top-level tests plus 99 Vitest tests passed (132 total), 0 failed, 0 skipped;
knowledge check reported 0 errors and 7 pre-existing harvest warnings; diff check passed.

## Cleanup and residue

All raw outputs remain under ignored `docs/qa/evidence/2026-08-22-deep-review-metrics-graft/`. The
fresh adoption target was removed after evidence capture. Source checkout residue is limited to the
planned durable QA artifacts plus ignored raw evidence; no product code was changed.

**Cycle verdict:** PASS — 3 scenarios passed, 0 failed, 0 untested, 0 blocked, 1 fixed bug with passing retest.
