# QA report — Deep Review learnings adoption retest

- **Date:** 2026-08-22
- **Scope:** Issue #28 — trackable Deep Review learnings under a consumer parent ignore
- **Branch:** `fix/track-deep-review-learnings`
- **Head at start:** `0413862`
- **Adapter:** CLI/manual through `scripts/adopt.py`, Git, and filesystem inspection
- **Environment:** macOS, isolated disposable Git target owned by this checkout
- **Automated gate before walk:** `python3 scripts/test_adopt.py && npm test` — PASS; adoption smoke passed and 145/145 Vitest tests passed
- **Raw evidence:** `docs/qa/evidence/2026-08-22-deep-review-learnings-retest/`
- **Limitation:** no browser, API, mobile, auth, server, or live agent-execution surface exists; the public adoption CLI and generated filesystem are fully reachable.

## Matrix

| Charter | Scenario | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `CH-retest-deep-review-learnings-2026-08-22` | `ADP-adopt-workflow-safely` | pass | Fresh Git reads before and after re-adoption exposed `learnings.md`, ignored `review.json`, preserved consumer lines, and retained an identical complete `.gitignore` hash. | `docs/qa/evidence/2026-08-22-deep-review-learnings-retest/session.md` |
| `CH-retest-deep-review-learnings-2026-08-22` | `CFG-keep-local-artifacts-out-of-git` | pass | Generated feature and Graft cache artifacts remained ignored; the Graft card remained searchable. | `docs/qa/evidence/2026-08-22-deep-review-learnings-retest/session.md` |

## Session results

The public adoption script ran twice against a disposable Git repository whose consumer-owned
`.gitignore` already ignored `.deep-review/`. Git returned `1` for
`.deep-review/learnings.md` and exposed it in status, while returning `0` for generated
`.deep-review/review.json`. All consumer and managed lines occurred once.

Re-adoption preserved the complete `.gitignore` SHA-256 byte-for-byte. Independent reload checks
returned the same visibility. Adjacent probes confirmed local feature state and Graft cache remain
ignored while a Graft card remains visible to repository search. No retries, defects, or additional
limitations occurred.

## Final gate

PASS. Exact command:

`python3 scripts/test_adopt.py && python3 tools/test_ad_index.py && python3 tools/test_deep_review_token_metrics.py && python3 tools/test_workflow_config.py && npm test && npm run knowledge && git diff --check origin/main..HEAD && git diff --check`

All four Python authorities passed; Deep Review reported 19/19 and workflow configuration reported
11/11. Vitest passed 145/145 across 11 files. Knowledge validation reported 0 errors and 11
pre-existing harvest warnings. Both committed-range and working-tree diff checks passed.

## Cleanup and residue

The disposable Git target and temporary command captures were removed. Raw evidence remains only at
the ignored `docs/qa/evidence/2026-08-22-deep-review-learnings-retest/session.md`. Checkout residue
is limited to the planned durable charter, report, bug, and scenario updates; no product code was
changed by QA.

**Cycle verdict:** PASS — 2 scenarios passed, 0 failed, 0 untested, 0 blocked, and the fixed issue
#28 bug has a passing public-interface retest.
