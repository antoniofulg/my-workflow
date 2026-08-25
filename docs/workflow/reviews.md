# Reviews

Review is how reliability gets a **second reader** without getting an infinite loop.

An unbounded loop was measured at 30 rounds on one feature. The rule that caused it sounded
responsible: remediate every confirmed finding **and every nitpick** in the same iteration. Each
nit changes the diff; the next round finds new nits. The loop is unbounded by construction.

[REVIEW-ROUNDS.md](../guidelines/REVIEW-ROUNDS.md) is the protocol. This page is the choice.

The public hierarchy is `Feature -> Vertical Slice -> Task`. Before dispatch, read
`.agents/skills/workflow-config/SKILL.md`; it resolves the feature's review groups.

## One Verifier role, several phases

The provider `verifier` executes one phase per packet. Deep-review is a separate stage, not a Verifier phase.
Remediation identity, independent counters, and halt behavior follow `REVIEW-ROUNDS.md`; the fingerprint is requirement + root cause + failure path.

| Reviewer | Question only it can answer | Cap |
| --- | --- | --- |
| **Technical Verifier** | Do the tests actually prove the spec? | Fingerprint-scoped; halt on third failed remediation |
| **QA Plan** | Which public promises need a walk? | One fresh Verifier session |
| **QA Execute** | Does this behaviour work through the declared adapter? | One fresh Verifier session |
| **Deep-review** (resolved groups) | Is the code correct, safe, maintainable? | ≤2 rounds, Blocker/Major only |
| **QA session** (feature closing step) | Does the finished feature feel right? | One `qa-plan` and one `qa-execute` session |

A documentation-only slice still gets a Technical Verifier and is included in the next resolved
deep-review group. If its docs are an interface users or adopters consume, it also gets the two QA
phases. `docs/` is full of Markdown agents act on; no compiler catches a shipped plan that says work
has not started.

They do not send work back to each other. A deep-review finding never restarts the Verifier. A
round-2 blocker is fixed under the approved loop and its scoped gate; the cap does not open round 3.
Post-cap remediation follows the stall bound: each attempt runs the scoped gate, a smaller failing
test set resets the counter, and an equal-size or larger set increments it. An unavailable gate
halts immediately; a reached nonzero threshold halts with the normalized signature, attempt count,
and fixes tried. If a deep-review fix changes user-visible behaviour, re-walk **the affected scenario
rows only**.

## What blocks, what files

| Severity | Blocks another round? | Otherwise |
| --- | --- | --- |
| `Blocker` | Yes | Fix now |
| `Major` | Yes | Fix now |
| `Minor` | Only if it blocks a journey | Else file an issue |
| `Cosmetic` | Never | File an issue |

Filed issues are real backlog, not a disposal bin. They do **not** re-enter Verifier + QA +
deep-review. That ceremony already happened; filing them was how they left the feature’s critical
path.

A user-visible fix still flags and walks its scenario. A fix that grows into a design or schema
change is a feature.

## Why the Verifier is not the author

A model that implemented the change will defend it. The Verifier re-derives coverage from the spec
and injects behavioural mutants. Enumerated cases in `tests.md` prove coverage *exists*; mutants
prove it is *real*.

A green gate is not a met requirement. Reviewers compare the deliverable to `spec.md`, `tests.md`,
and `uiux.md` / `dx.md` field by field. Paraphrase is not parity.

## Evidence

[VERIFICATION-EVIDENCE.md](../guidelines/VERIFICATION-EVIDENCE.md): no completion claim without a
fresh command. Scope binds — unit tests do not justify “feature complete”. A passing review over a
red gate is void.

Escalate when the post-cap gate is unavailable or the configured stall threshold is reached. An
open blocker alone does not halt while remediation is making measurable progress. A halt report is
a result.
