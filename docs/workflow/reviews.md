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

A documentation-only slice still gets a Technical Verifier and joins the next resolved deep-review
group. Public docs also get both QA phases. The only exception is a diff classified as
credential-free declarative agent-tool configuration by [GATES.md](../guidelines/GATES.md).

Technical Verifier reads the slice's private writer checkpoint. Deep-review reads the integrated
commit range, and fresh QA Plan/Execute read the integrated final tree. The coordinator records
distinct author and proof identities; the last implementer supplies a handoff and never certifies
the integrated result.

They do not send work back to each other. A deep-review finding never restarts the Verifier. A
round-2 blocker is fixed under the approved loop and its scoped gate; the cap does not open round 3.
Post-cap remediation follows the stall bound: each attempt runs the scoped gate, a smaller failing
test set resets the counter, and an equal-size or larger set increments it. An unavailable gate
halts immediately; a reached nonzero threshold halts with the normalized signature, attempt count,
and fixes tried. If a deep-review fix changes user-visible behaviour, re-walk **the affected scenario
rows only**.

## What blocks, what files

| Severity | Another round? | Feature delivery |
| --- | --- | --- |
| `Blocker` | Yes | Fix now |
| `Major` | Yes | Fix now |
| `Minor` | No | Fix in one current-run batch, scoped gate, one commit |
| `Cosmetic` | No | File an issue |

Minor fixes stay inside the feature context and start no new proof round. Filed Cosmetic issues are
real backlog, not a disposal bin; they do **not** re-enter Verifier + QA + deep-review because that
ceremony already happened.

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
