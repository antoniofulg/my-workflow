# QA report — Deep Review walkthrough upsert

- **Date:** 2026-08-22
- **Scope:** issue #29 walkthrough publication and adjacent Deep Review canary
- **Branch:** `fix/idempotent-review-comment`
- **Head at start:** `8268c77`
- **Adapter:** CLI/manual through the public Markdown recipe and checkout-local fake `gh`
- **Environment:** macOS, active isolated checkout `/Users/antoniofulg/Projects/my-workflow`
- **Automated gate before walk:** targeted public-recipe contract PASS (1 test, 0 failed)
- **Raw evidence:** `docs/qa/evidence/2026-08-22-deep-review-walkthrough-upsert/`
- **Limitation:** fake `gh` records arguments without network access; GitHub rendering is not exercised.

## Matrix

| Charter | Scenario | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `CH-upsert-deep-review-walkthrough-2026-08-22` | `QAS-upsert-deep-review-walkthrough` | pass | The fake `gh` log contained one list plus one POST for no id, and one list plus one PATCH to id `42` for an existing marker; neither contained a second mutation or `/comments/null`. | `docs/qa/evidence/2026-08-22-deep-review-walkthrough-upsert/session.md` |
| `CH-upsert-deep-review-walkthrough-2026-08-22` | `QAS-observe-serialized-deep-review-metrics` | pass | The complete Deep Review contract suite passed after both publication paths. | `docs/qa/evidence/2026-08-22-deep-review-walkthrough-upsert/session.md` |

## Session results

The adapter extracted the bash block from the public Markdown entry point, placed a checkout-local
fake `gh` first on `PATH`, and walked both marker states in isolated temporary directories. The
absent-marker state issued one list and one create request. Marker id `42` issued one list and one
PATCH to that id. Exact argument-array assertions rejected a second mutation, a wrong endpoint,
or `/comments/null`.

The targeted recipe contract passed twice, including one verbose confirmation. The adjacent
Deep Review canary then passed all eight tests. No network request or remote mutation occurred.

## Final gate

PASS. Exact command:

`npm test && git diff --check`

Result: 11 Vitest files and 145 tests passed; diff check passed.

## Cleanup and residue

The adapter's temporary directories cleaned themselves after each run. Raw evidence remains under
the ignored evidence path. Checkout residue is limited to planned durable QA artifacts; no product
code changed during QA.

**Cycle verdict:** PASS — 2 scenarios passed, 0 failed, 0 untested, 0 blocked, no product defects.
