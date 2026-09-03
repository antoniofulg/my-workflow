# Decisions — review-signal-trailer

Everything this unattended run chose. Read the "Handed down" section first: those were the human's,
and the rest are the run's to answer for.

## Handed down by the human

| Decision | Where it came from |
| --- | --- |
| Build the durable review signal at all, as a Small/Medium feature in two slices — emit, then read | Direct instruction, after reviewing four alternatives and rejecting three |
| Do not build infra gates (CI, branch protection) in this repository | "esse projeto serve como um aditivo para um projeto real … deve ser realmente implementado no projeto real, independente de stack" |
| Do not add red-before-green for feature tests | The spec-driven method deliberately replaced it with the coverage matrix plus the mutation sensor, at lower cost |
| Do not add a sizing auditor | "alto custo e pouco benefício" — the scopes are already clear in practice |
| Do not gate `STATE.md` freshness | Specs guide the agent; they are not the source of truth, and pruning is coming |
| Treat the `autonomous` merge-without-human-read gap as accepted for this phase | Construction phase, defined plan, safe review process |

## Decided by this run

Two decisions were weighty enough to outlive the feature and are recorded in `.specs/STATE.md`:
**AD-025** (one trailer per delivery, not per slice), **AD-026** (validated when present, never
required), **AD-027** (pre-process commits count as unsigned; no pull-request heuristic).

| Decision | Why | Rejected | Cost to change now | Cost to the user today |
| --- | --- | --- | --- | --- |
| One trailer per delivery, aggregating slices via `slices=`/`verified=` (AD-025) | No per-slice commit can carry a verdict: tasks commit before the Verifier runs, and integration may fast-forward with no commit at all. The counts still sum to the slice-level fraction | A trailer per slice; a dedicated close-out commit per slice; `git notes` (does not survive clone) | Low — grammar and reader both change, ~50 lines | A squash merge keeps its signal only if the squash message carries it |
| Validate the trailer only when present (AD-026) | Every task commit runs through the same validator; requiring it would reject all of them | Requiring it on delivery commits only — the validator cannot tell which commit is a delivery | Low | Nothing forces a delivery to carry the trailer; omission shows up only afterward, as an unsigned delivery |
| A delivery is any first-parent commit, merged or squashed (AD-027) | Excluding single-parent commits made squash-merged pull requests vanish from the report entirely — a flattering number, the exact failure this feature exists to prevent | Keeping `--merges`; a heuristic for "did this go through a pull request" | Low, one flag | Run over this repository's whole history, ~6 of 60 first-parent commits predate the process and dilute the fraction. The bias is pessimistic, and `--help` now says to pass a range |
| The grammar's one home is `check_commit.py`'s docstring, not the guideline | `REVIEW-ROUNDS.md` broke its executable 160-line cap; the validator that enforces the grammar is the honest home | Raising the cap (would have been weakening a test to pass a gate) | Trivial | Readers follow one pointer to reach the field list |
| Deleting `## Why loops run away` from `REVIEW-ROUNDS.md` to fit the cap | Its content restated the `**Why this exists:**` header two lines above; the operative Hard rule survives untouched. Independently confirmed by deep review | Pruning elsewhere; raising the cap | Trivial, `git revert` of one hunk | None found — no reference pointed at the deleted heading |
| Ruling deep-review round 2's Finding 1 not-a-defect (AD-027) | Commits that reached `main` unreviewed *are* unsigned; reporting them so is true, and the bias runs pessimistic rather than flattering | Accepting the finding and filtering history | Low | See AD-027's trade-off |
| Accepting a mistyped trailer key as a silent unsigned delivery | A near-miss heuristic is the same cleverness AD-027 refused on the sibling tool, and the failure is bounded — the delivery reads unsigned, never falsely reviewed | Fuzzy-matching the key; requiring the trailer | Low | Filed as `docs/qa/bugs/BUG-20260903-mistyped-review-signal-key-passes-silently.md` for the human to decide |
| Accepting that a repository with no refs *and* no reflogs reports zeros | Git has no in-band signal left to separate it from a never-committed repository; closing it costs an O(repo) scan on every healthy run to cover two deliberate deletions | A full object scan | Low | Documented in the code comment; unreachable in normal use |
| Not testing `--help` output | Asserting it pins prose that will churn | A brittle wording assertion | Trivial | The help text can regress without a test catching it |

## What the numbers in this delivery's own trailer mean

`tier=medium slices=2 verified=2 sensor=10/10 rounds=2 findings=5 fixed=4 dismissed=1`

Reconciled by the QA session against the evidence, correcting the coordinator's proposed
`fixed=5 dismissed=0`: round 1 raised 2 Major (both fixed), round 2 raised 3 Major (2 fixed, 1
dismissed as AD-027). The sensor counts 10 distinct mutations at their final verdict — counting
injection events would give 11/10 and report a mutant that no longer survives.

QA recorded the sharpest limitation of the whole feature: `findings=5 fixed=5 dismissed=0` would
also pass the validator, because it enforces arithmetic and never truth. The number's integrity
rests entirely on whoever composes it.

## Known limits, in plain terms

- A squash merge keeps its signal only if the squash message carries the trailer.
- A mistyped trailer key reads as an unsigned delivery, silently.
- Backfilling historical commits is out of scope, so this repository reports 0 signalled today.
- Nothing forces the trailer to be emitted. That is AD-026's deliberate trade, and the reader's
  unsigned count is what catches omission, after the fact.
