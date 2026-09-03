---
id: QAS-report-the-reviewed-fraction-from-git
area: QAS
title: Report the reviewed fraction from git history alone
persona: Workflow operator
journey: J-measure-review-coverage
expected: The report states signalled versus unsigned deliveries, the reviewed fraction over the given range, and aggregate findings and surviving mutants, exiting 0 even when the range carries no signal
entry_points: tools/review-metrics.py; tools/review-metrics.py --json; tools/review-metrics.py <rev-range>
qa_status: pass
bug_ids: BUG-20260903-review-metrics-help-omits-the-range-caveat
fix_status: pending
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-09-03-review-signal-trailer/01-noargs.log; docs/qa/evidence/2026-09-03-review-signal-trailer/02-json.log; docs/qa/evidence/2026-09-03-review-signal-trailer/03-range.log; docs/qa/evidence/2026-09-03-review-signal-trailer/05-nextmonth.log
last_report: docs/qa/reports/2026-09-03-review-signal-trailer.md
overlaps:
---

Covers `RST-02`. Walked on this repository (67 first-parent deliveries, all unsigned, exit 0) and on
a disposable checkout-local repository carrying four signalled deliveries, three of them real
reviews that found nothing.

The zero-finding case is visible, which is the criterion that mattered most: `Findings: 0` next to
`signalled 4` and `killed 9 of 9 injected` reads as *four reviews ran and found nothing*, not as
*nobody reviewed*. The `tier=` breakdown and the reviewed-by-design line separate `direct`/`batch`
deliveries from unreviewed ones.

`bug_ids` records the usability boundary this walk found: `--help` shows only the docstring's first
line, so the range caveat AD-027 leans on never reaches the operator who does not open the source.
The headline fraction also reads 100% while a third of deliveries carry no signal at all.
