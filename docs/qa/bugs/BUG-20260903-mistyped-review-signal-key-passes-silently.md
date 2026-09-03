# BUG-20260903-mistyped-review-signal-key-passes-silently

- **Status:** open — spec-conformant, decision required
- **Severity:** minor (silent miss, no false number)
- **Scenario:** `QAS-validate-the-review-signal-trailer`
- **Expected:** AD-026 states the reason validation exists at all: *"not validating it at all would let a mistyped signal poison the metric silently."*
- **Observed:** A typo in the trailer's own key rather than in its payload defeats that reason. `Review-Singal: tier=medium slices=2 …` exits 0 with `check_commit: OK`; `SIGNAL_RE` at `.agents/skills/workflow-spec-driven/scripts/check_commit.py:50` matches only the exact literal `^Review-Signal:`. The delivery then reads as unsigned in `review-metrics.py` forever, indistinguishable from a delivery nobody reviewed.
- **Adapter:** CLI/manual, message on stdin
- **Exact path:** `printf '%s\n' "<message with Review-Singal:>" | python3 .agents/skills/workflow-spec-driven/scripts/check_commit.py`
- **Evidence:** `docs/qa/evidence/2026-09-03-review-signal-trailer/04-check-commit.log` section E

## Why this is not filed as an AC failure

`spec.md` RST-01 says a message carrying no `Review-Signal:` trailer is accepted unchanged, and by
the letter a `Review-Singal:` line is no such trailer. The validator is correct. What is at issue is
the gap between what AD-026 promises the validator protects and what it can see.

## Improvement, with its cost stated

A near-miss warning on any line matching `^Review-[A-Za-z-]+:` that is not `Review-Signal:` would
close it, at the price of a heuristic in a tool whose sibling decision (AD-027) deliberately refused
to add heuristics. The honest options are (a) accept the near-miss and say so in
`docs/guidelines/REVIEW-ROUNDS.md` beside the grammar, or (b) add the warning. This session
recommends (a): the failure is bounded — it produces an unsigned delivery, never a false reviewed
number — and `review-metrics.py`'s unsigned count is the after-the-fact catch AD-026 already names.
Recorded so the choice is made rather than inherited.
