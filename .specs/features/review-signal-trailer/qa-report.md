# QA: review-signal-trailer — feature-closing session

**Verdict: READY TO DELIVER.** Both user stories walked through their real public surfaces on
`feat/review-signal-trailer` @ `0916394`. Three usability findings, none an acceptance-criteria
failure, none producing a wrong number.

Durable QA artifacts:

- `docs/qa/reports/2026-09-03-review-signal-trailer.md` — the walk, the matrix, the reconciliation.
- `docs/qa/journeys/J-measure-review-coverage.md`
- `docs/qa/scenarios/QAS-validate-the-review-signal-trailer.md` — `qa_status: pass`
- `docs/qa/scenarios/QAS-report-the-reviewed-fraction-from-git.md` — `qa_status: pass`
- `docs/qa/bugs/BUG-20260903-review-metrics-help-omits-the-range-caveat.md`
- `docs/qa/bugs/BUG-20260903-mistyped-review-signal-key-passes-silently.md`

## Reconciled trailer

```
Review-Signal: tier=medium slices=2 verified=2 sensor=10/10 rounds=2 findings=5 fixed=4 dismissed=1
```

Validated: `check_commit: OK`, exit 0. Two values differ from the packet's suggestion —
`fixed=4 dismissed=1` rather than `fixed=5 dismissed=0`, because Round 2's Finding 1 was dismissed by
AD-027 rather than fixed. `sensor=10/10` is confirmed but for a different reason than assumed: there
were four sensor passes, and 10/10 is the count of *distinct* mutations at their final verdict, M2
having survived slice 1 and been killed on re-proof after `f73fcd8`. Full derivation in the report.

## Findings, ranked

1. **Major (usability)** — `tools/review-metrics.py:116` passes `__doc__.splitlines()[0]` to
   argparse, so `--help` shows one sentence and the four paragraphs at `:6-16` defining a delivery,
   defining `unsigned`, and warning that a feature branch is the wrong range never reach the
   operator. AD-027 names the help text as the mitigation for its accepted pessimistic bias; the
   mitigation is not in the help text. Fix: `description=__doc__` with
   `formatter_class=argparse.RawDescriptionHelpFormatter`.
2. **Minor (usability)** — `tools/review-metrics.py:105-106` renders `Reviewed fraction: 4/4 slices
   verified (100.0%)` while two of six deliveries carried no signal. Unsigned deliveries contribute
   zero slices and so cannot lower the percentage. Fix: append the coverage the report already
   computes, e.g. `across 4 of 6 deliveries`.
3. **Minor (decision required)** — `check_commit.py:50` matches the literal `^Review-Signal:` only,
   so `Review-Singal:` exits 0 and the delivery is unsigned forever. Spec-conformant; it is AD-026's
   stated purpose that is dented, not an AC. Recommendation is to accept and document rather than
   add a heuristic.

## What was walked

Default range, `--json`, a narrowed range, an unreadable range, `--help` read cold, a composed
delivery message, a mistyped payload key, an unbalanced `findings`, a mistyped trailer key, and a
simulated month of signalled deliveries in a disposable checkout-local repository. Gates green:
`test_review_metrics.py` 14 OK, `test_tlc_validators.py` 35 OK. No residue beyond the
`review-fingerprints.json` modification that was already in the tree.
