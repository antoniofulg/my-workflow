---
id: QAS-validate-the-review-signal-trailer
area: QAS
title: Validate a Review-Signal trailer at commit time
persona: Workflow operator
journey: J-measure-review-coverage
expected: A well-formed trailer is accepted, a malformed one is rejected with an error that names the exact key or arithmetic to fix, and a message with no trailer is accepted unchanged
entry_points: .agents/skills/workflow-spec-driven/scripts/check_commit.py
qa_status: pass
bug_ids: BUG-20260903-mistyped-review-signal-key-passes-silently
fix_status: pending
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-09-03-review-signal-trailer/04-check-commit.log
last_report: docs/qa/reports/2026-09-03-review-signal-trailer.md
overlaps:
---

Covers `RST-01`. Walked with a real delivery message for this feature carrying
`tier=medium slices=2 verified=2 sensor=10/10 rounds=2 findings=5 fixed=4 dismissed=1`, reconciled
against `validation-s1.md`, `validation-s2.md` and `validation-postcap.md`.

The two plausible human mistakes were both repairable from the error text alone. A mistyped key
produced `key 'fidnings' is unknown; allowed: …` plus `tier 'medium' requires key 'findings'`, which
names both halves of the repair. An unbalanced count produced `findings=5 but fixed+dismissed=6`,
which shows the arithmetic rather than restating the rule.

The verdict is `pass` for the promise as the spec states it. `bug_ids` records a separate silent-miss
boundary: a typo in the trailer's own key (`Review-Singal:`) is not a `Review-Signal` trailer by the
letter of the spec, so it exits 0 and the delivery reads as unsigned forever. The AC is met; the
promise's usefulness is what the bug is about.
