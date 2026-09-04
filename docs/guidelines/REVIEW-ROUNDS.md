# Review Rounds

**Read when:** reviewing code, or acting on review findings.

**Why this exists:** Remediating every nitpick in one iteration is unbounded: each fix changes the
diff and the next round finds new nits. Caps, monotonic findings, in-run defect batches, and filed
Cosmetics make review end.

## The review stages, and what each is for

| Stage | Asks | Cap |
| --- | --- | --- |
| **Technical Verifier** (every slice that changes code) | Do the tests actually prove the acceptance criteria? | Same-fingerprint live threshold; no final round 3 |
| **QA Plan** (public slices) | Which public promises need a walk? | One fresh Verifier session |
| **QA Execute** (public slices) | Does this behaviour work through the declared adapter? | One fresh Verifier session |
| **deep-review** (resolved implementation groups) | Is the code correct, safe and maintainable? | ≤2 rounds, blocking findings only |
| **QA session** (feature closing step) | Does the finished feature work for a real user? | One `qa-plan` and one `qa-execute` session |
The provider `verifier` executes exactly one phase per packet: `technical`, `qa-plan`, or
`qa-execute`. The orchestrator dispatches a technical packet, then fresh QA Plan and QA Execute
packets for a public slice. Deep-review is a separate orchestrator stage, not a Verifier phase;
internal-only changes skip the QA packets. All QA stages read `docs/guidelines/QA-SCENARIOS.md`; it owns
fields and statuses. Each stage answers a question the others cannot, so none is redundant. Direct corrections follow `.agents/skills/workflow-spec-driven/SKILL.md`: scoped validation closes them, with no fresh Verifier, deep-review, or QA.

Intent vocabulary is routing input, not a keyword bypass: `feature` starts at Small, `cross-feature change` at Medium, `direct correction`/`UI-only correction` use the fast path only when the repository predicate passes, and `issue` is neutral. State tier, facts, and validation before dispatch; escalation requires newly discovered named evidence, not file count or UI presence.

## Why resolved groups, not a rigid interval

Rounds do not grow with the size of a diff, they explode with it. Every round re-reads the whole
change, and every remediation moves what the next round reads, so a large diff feeds itself. Three
rounds over one behaviour is a signal about that behaviour; twenty over a finished feature is the
size talking.

Read `.agents/skills/workflow-config/SKILL.md` before dispatch; its resolver owns cadence modes,
default, and balanced groups. One pull request and one actor per role remain unchanged.

**Stages do not loop back into each other.** A deep-review finding never sends work back to
Technical Verifier. The deep-review cap ends review rounds; it does not revoke the approval for
local remediation already in progress. The post-fix gate and escalation rule below decide whether
the slice is done.

Before final QA, complete the final pending implementation deep-review group. For QA code remediation, review only `reviewed_head..HEAD`, then re-walk affected scenario rows.

## The feature closing step

A feature's closing step is the **QA session**, after the final implementation review group. It
needs the whole feature and cannot run on part of one. The `qa-plan` and `qa-execute` skills own it.

It writes no product code, so it gets no technical Verifier or deep-review. It still receives distinct
fresh packets, `qa-plan` and `qa-execute`. Per-slice QA answers *"does this behaviour work?"*; the
final session answers *"does the finished thing feel right?"* after all implementation groups close.

## Hard rules

1. **A round contains only findings not raised in a prior round.** Before writing a finding, read the
   prior rounds. A pending, accepted, or already-resolved issue is never re-raised. This is what makes
   the loop monotonic and therefore finite.

   `workflow-spec-driven` points here for remediation identity and counting; this rule prevents a renamed
   finding from resetting its history while allowing a distinct blocker to proceed.
2. **Nitpicks never trigger a round.** Fix every confirmed deep-review defect in the active feature run. Blocker and Major findings trigger the next capped round; Minor findings join that remediation batch, or close together in one Minor-only batch with one scoped gate and one commit. A Minor-only batch starts no fresh Technical Verifier, QA phase, or deep-review round. Cosmetics and advisories go to the pull request follow-up list. **In an active, already-approved review loop, fix blocking findings without new human approval through the applicable review cap and run the scoped gate after each correction. Findings produced by the final deep-review round (round 2) are corrected automatically in the same loop; do not start round 3; escalate only if the post-fix gate fails or the configured stall threshold is reached for the same fingerprint.** Local fixes only; remote actions retain separate approval requirements.
3. **Deduplicate by root cause, not by occurrence.** One missing null check repeated in six files is
   one finding that lists six files — not six findings.
4. **Verify before flagging.** Check for an adjacent comment explaining the choice, a decision in
   `.specs/STATE.md`, or a test that validates the behaviour. Unconventional is not the same as wrong.
5. **Never report what a linter already catches.** Run the consuming project's linter first and drop
   every overlapping candidate.
6. **Signal over volume.** Above 20 findings, keep all blocking ones and prune the rest to the most
   impactful. Eight precise findings are worth more than thirty that include marginal concerns.
7. **The reviewer is not the author.** A different actor, or at minimum a different model — the model
that implemented the change never solely reviews it. This is cheaper than recruiting a fresh agent
identity and buys the same independence.
   Verifier and Deep Reviewer receive fresh role packets. They do not inherit the Implementer's
   transcript or operator handoff. Their conclusions must come from the spec, diff, tests, and
   assigned evidence.
8. **Documentation and instruction changes follow the proportional classifier in `GATES.md`.** Pure maintenance and bounded instruction changes do not start deep-review or QA by default; mixed changes run canonical checks for changed executable behavior. Named concrete risk or changed public promise can select stronger review; file count and the word "feature" do not escalate them.
8. **A passing verdict on a failing tree is void.** Re-run the scoped gate after remediation; a green
   review over a red gate is not a review.
9. **A new control for an unobserved failure is Major (YAGNI) unless the spec named it.** A
   killed-process shim, a test-of-the-test, or a prefix allowlist the spec did not name is overbuild.
   Filed-issue review uses the same rule. `ponytail-review` is the skill; this rule is what makes
   YAGNI blocking.
## Fingerprinted remediation accounting
`fingerprint = requirement + root cause + failure path` is each finding's immutable identity. Maintain an independent cumulative failed-remediation counter and append-only generation history for each fingerprint; count every failed post-fix Verifier result, whether or not the build gate is green. The current generation's consecutive-stall state is separate and halts only at the live `[remediation].stall_attempts` threshold. The executable state lives in `review-fingerprints.json` through the stdlib convergence script, which delegates the pure transition to `remediation.py`.
Rewording or reopening a finding preserves its fingerprint and counter. A distinct blocker starts at count zero and does not consume another fingerprint's counter; the diagnostic cap is separate.
## The Review-Signal trailer

The delivery commit for a pull request carries one `Review-Signal:` line recording its review
outcome, so the record survives the pruning of `.specs/features/` (AD-025). `check_commit.py`
validates the line when present and never requires one (AD-026); that validator's docstring owns
the field-by-field grammar.

## Finding shape
Every finding states, in this order:

- **Premise** — the fact in the code that starts the argument, with `file:line`
- **Path** — the concrete sequence from that fact to a wrong outcome
- **Verdict** — severity from the taxonomy below, never inflated
A finding without a failure path is an advisory, not a defect. Advisories state
**Premise → Improvement → Fix** and never block.

Severity uses the scheme tlc's validation report already ships, so the Verifier and deep-review speak
one vocabulary:

| Severity | Meaning | Action | Another round | Blocks delivery |
| --- | --- | --- | --- | --- |
| `Blocker` | Data loss, security hole, or the feature does not work | Fix now | yes | yes |
| `Major` | Behaviour deviates from the spec, or a likely crash under real input | Fix now | yes | yes |
| `Minor` | A spec edge case is unhandled, or a real maintenance hazard | Fix in the active feature batch | no | until fixed |
| `Cosmetic` | Style, naming, structure — a nitpick by definition | File an issue | no | no |

Every confirmed deep-review defect is fixed before feature delivery. An unfixed `Blocker` or `Major`
means the verdict is `FIX_BEFORE_SHIP`, and only those severities trigger another round. Every
`Minor` closes in the current remediation batch; the scoped gate and one commit close it without
another proof cycle. Cosmetics and advisories become follow-ups and never hold a pull request.

Filed Cosmetic issues are real work, not a disposal bin. They enter the backlog like any other item.

## Fixing a filed issue

**A filed Cosmetic issue does not re-enter the loop above.** It was already reviewed — that is how it
came to be filed — so a verifier, a QA pass and two review rounds would re-do work that is already
done. Minor findings never enter this path; they close inside their originating feature run.

Fix one, or a batch of them, as a small change:

```
implement → scoped gate → one commit for the batch
```

No spec, no tasks file, no verifier, no deep-review round. `workflow-spec-driven` already sizes this way:
a change of a few files with an obvious outcome skips planning entirely.

Three things still apply, because they are about the change and not about the review:

- **If the fix changes user-visible behaviour**, flag its scenario per `QA-SCENARIOS.md` and walk it.
  A `Cosmetic` finding on a screen is still a change a user can see.
- **If the fix touches a security surface**, `SECURITY.md` fires as it would for any diff.
- **If the fix turns out to be large** — it needs a schema change, it spreads across a boundary, the
  "one-line fix" opens a design question — it stopped being a filed issue and became a feature. Take
  it through the full loop and say why.

Batch aggressively. One commit per remediation batch is already the commit rule, and a batch of six
`Cosmetic` findings in one area is one review's worth of attention, not six.

## Escalation

When a cap is reached, finish approved remediation and run its scoped gate after every attempt; the cap forbids another review round, does not require new approval for the round-2 fix, and the existing loop never starts round 3. Each attempt derives a stable signature from sorted failing-test identifiers after removing timings, absolute paths, and line numbers; a current failing-test set that is a strict subset of the running minimum failing-test set resets the counter, while an equal-size set, including one with different members, or a larger set increments it, and `stall_attempts = 0` is unbounded.
If the gate is unavailable, halt immediately without another deep-review round; when a nonzero threshold is reached, halt with the repeated signature, attempt count, and fixes tried. An open blocker alone does not halt while attempts establish new minima; autonomous uses the same unavailable-gate or reached-threshold halt contract.

## Requirement and contract parity

A green gate proves the code compiles, lints and passes its tests. It does not prove the code matches
the spec. Every reviewer additionally compares the deliverable against the canonical artifacts —
`spec.md` acceptance criteria, `tests.md` cases, and the `uiux.md` / `dx.md` surface contracts when
they exist — field by field, not by paraphrase.

The failure this prevents is specific: a change can pass many review rounds while contradicting the
spec's canonical contract, because every round measured engineering quality against the task file's
paraphrase and nothing ever compared it to the source.
