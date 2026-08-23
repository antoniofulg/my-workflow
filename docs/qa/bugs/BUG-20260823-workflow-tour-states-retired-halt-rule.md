# BUG-20260823-workflow-tour-states-retired-halt-rule

- **Status:** fixed
- **Severity:** major
- **Scenario:** `DOC-halt-remediation-only-on-a-stall`
- **Expected:** Every surface an operator reads states one halt rule — remediation continues while an attempt reaches a new minimum failing-test set and halts only after `stall_attempts` consecutive stalls or an unrunnable gate — and none still halts on an open blocker alone.
- **Observed:** `docs/workflow/reviews.md:67` still reads "Escalate only when the post-fix gate fails or a blocker remains reproducible at the cap." That is the retired formulation this feature removed from `docs/guidelines/REVIEW-ROUNDS.md`, and the word "only" positively excludes the stall rule. The file names neither `stall_attempts` nor the failure signature. `scripts/adopt.py` `COPY_PATHS` installs `docs/workflow/reviews.md` into every consuming project, so an operator reading the pack tour is told the run halts on a reproducible blocker while the guideline says it halts on consecutive stalls.
- **Adapter:** manual repository inspection
- **Exact path:** `git ls-files -z | xargs -0 grep -n -i -e 'blocker remains reproducible' -e 'leaves a blocker open' -e 'reproducible blocker'`
- **Evidence:** `docs/qa/evidence/2026-08-23-stall-based-halt/halt-rule-session.md`
- **Fix commit:** `3dee592` — `docs(workflow): point the tour at the canonical halt rule`
- **Retest:** 2026-08-23, fresh Verifier, `qa-execute` retest over `c841207..a27543c` — **pass**. `docs/qa/evidence/2026-08-23-stall-based-halt/retest-session.md`; report section `docs/qa/reports/2026-08-23-stall-based-halt.md` `## Retest — 2026-08-23`.

## Reproduction

1. Run the grep above from the repository root on branch `feat/stall-based-halt`.
2. Read `docs/workflow/reviews.md:67` and `docs/guidelines/REVIEW-ROUNDS.md` `## Escalation`.
3. The two surfaces state different halt conditions for the same event.

`git diff --stat main...HEAD` shows `docs/guidelines/REVIEW-ROUNDS.md` changed in this branch and
`docs/workflow/reviews.md` did not.

## Why the gate did not catch it

`tools/shared/tests/qa-skills.test.ts:805` forbids "blocker remains reproducible" in
`docs/guidelines/REVIEW-ROUNDS.md`, and `:839` forbids "leaves a blocker open" in the `autonomous`
halt-conditions block. Neither guard reads `docs/workflow/*`, which is an installed consumer surface.

## Smallest remediation

Restate `docs/workflow/reviews.md:67` as a pointer to `docs/guidelines/REVIEW-ROUNDS.md`
`## Escalation` — the tour's own convention elsewhere in the file — rather than a second copy of the
condition, and extend the existing negative guard to cover the installed `docs/workflow/` documents
so the next rule change cannot drift the same way.

## Adjacent, not filed as a defect

`docs/workflow/purpose.md:38-39` ("Shipping past a cap with a reproducible blocker is not") is a
readiness statement, not a halt condition, and matches `.agents/skills/autonomous/SKILL.md:181`. It
is left as observed; whoever fixes `reviews.md` should confirm it still reads correctly beside the
new rule.
