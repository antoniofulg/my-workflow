# J-measure-review-coverage

**Persona:** Workflow operator
**Goal:** Emit a delivery's review outcome as a `Review-Signal` git trailer and read back, from git history alone, what fraction of delivered work was really reviewed.
**Entry point:** `.agents/skills/workflow-spec-driven/scripts/check_commit.py` → `tools/review-metrics.py`

## Flow

1. Compose a delivery commit message carrying a `Review-Signal` trailer whose counts are reconciled
   against the feature's validation reports, and validate it with `check_commit.py`.
2. Mistype a trailer key and unbalance `findings` against `fixed + dismissed`; read the error alone
   and repair the trailer without opening the validator's source.
3. Commit an ordinary message with no trailer and confirm it is accepted unchanged.
4. Run `tools/review-metrics.py` with no argument, then `--json`, then over a narrowed range, and
   read the signalled/unsigned split, the reviewed fraction, and the aggregates.
5. Read `--help` and decide, from it alone, whether the default range is the right one to trust.
6. Read the report over a history that does carry signals and answer the operator's real question:
   is review still finding anything?

## Promises

- [`QAS-validate-the-review-signal-trailer`](../scenarios/QAS-validate-the-review-signal-trailer.md)
- [`QAS-report-the-reviewed-fraction-from-git`](../scenarios/QAS-report-the-reviewed-fraction-from-git.md)

## Adjacent canary

Inspect [`CFG-keep-local-artifacts-out-of-git`](../scenarios/CFG-keep-local-artifacts-out-of-git.md)
to confirm the QA walk's disposable repositories and evidence stay outside the tracked tree.
