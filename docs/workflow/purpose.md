# Purpose

This workflow exists to **keep shipping without pretending the product is safer than it is**.

Two failure modes showed up in the same kind of work:

- **Delivery without a floor.** A green linter, a coverage number, a paraphrase of the spec. The
  feature merges. Users hit a journey nobody walked. Security is “we thought about it”.
- **Reliability without an end.** Every nitpick is remediating in the same iteration. Each fix
  changes the diff. The next round finds new nits. Thirty rounds is not thoroughness; it is a loop
  that cannot converge.

The pack is the floor plus the end condition.

## What “balance” means here

**Delivery** is: a change small enough to implement and verify by vertical slice, a gate cheap
enough to run per slice, review cadence selected by workflow config, and merge authority that stays
with the human.

**Reliability** is: tests derived from acceptance criteria, security surfaces named and given
`SEC-` cases, a Verifier that is not the author, a persona walk for anything a user can see, and a
full gate once — on the tree you actually ship.

Neither side is optional. A slice that skips the Verifier to go faster is not this workflow. A
slice that re-reviews Cosmetics until the diff stops moving is not this workflow either.

## What the caps buy

| Cap | Protects |
| --- | --- |
| Verifier fingerprint cap, then escalate | Stops a repeated blocker from eating the week |
| Deep-review ≤2, Blocker/Major only | Stops nitpick churn from being called “quality” |
| Stages do not loop into each other | Review groups bound repeated reading, then a human |
| Full gate once per feature | Stops ten-task features from paying the product gate ten times |
| Approval is local-only | Stops an agent from pushing, merging, or deploying on a spec yes |

Escalate is a result after the required post-cap remediation and gate. Shipping past a cap with a
reproducible blocker is not.

The review cap counts failed remediation per immutable finding fingerprint; see
[`REVIEW-ROUNDS.md`](../guidelines/REVIEW-ROUNDS.md) for the accounting rule.

## What this pack is not

It is not a product, a stack, or a starter app. The consuming project fills one paragraph in
`AGENTS.md` and owns `make check`. Reliability rules here are process: they do not name a
framework.
