# Review Rounds

**Read when:** reviewing code, or acting on review findings.

**Why this exists:** Remediating every nitpick in one iteration is unbounded: each fix changes the
diff and the next round finds new nits. Caps, monotonic findings, and filed issues make review end.

## Why loops run away

The failure has one cause, and it is a rule that sounds responsible:

> *remediate every confirmed finding **and every nitpick** in this same iteration*

Every nitpick changes the diff, so the next round finds new nitpicks. The loop is unbounded by construction, not by bad luck.

## The review stages, and what each is for

| Stage | Asks | Cap |
| --- | --- | --- |
| **Technical Verifier** (every slice that changes code) | Do the tests actually prove the acceptance criteria? | ≤3 fix rounds, then escalate to the human |
| **QA Plan** (public slices) | Which public promises need a walk? | One fresh Verifier session |
| **QA Execute** (public slices) | Does this behaviour work through the declared adapter? | One fresh Verifier session |
| **deep-review** (resolved implementation groups) | Is the code correct, safe and maintainable? | ≤2 rounds, blocking findings only |
| **QA session** (feature closing step) | Does the finished feature work for a real user? | One `qa-plan` and one `qa-execute` session |
The provider `verifier` executes exactly one phase per packet: `technical`, `qa-plan`, or
`qa-execute`. The orchestrator dispatches a technical packet, then fresh QA Plan and QA Execute
packets for a public slice. Deep-review is a separate orchestrator stage, not a Verifier phase;
internal-only changes skip the QA packets. All QA stages read `docs/guidelines/QA-SCENARIOS.md`; it owns
fields and statuses. Each stage answers a question the others cannot, so none is redundant.

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

   `tlc-spec-driven` does not have this rule — it bounds the Verifier at 3 iterations but nothing stops
   a round re-raising what a prior round already found. The count bound alone does not converge; this
   rule is what makes it converge.
2. **Nitpicks never trigger a round.** They go to a follow-up list in the pull request. Only `FIX_BEFORE_SHIP` and `REWORK` findings justify another pass. **In an active, already-approved review loop, fix blocking findings without new human approval through the applicable review cap and run the scoped gate after each correction. Findings produced by the final deep-review round (round 2) are corrected automatically in the same loop; do not start round 3; past the cap, escalation below bounds remediation by failure signature, not by an open blocker.** Local fixes only; remote actions retain separate approval requirements.
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
8. **A documentation-only change is not an exception.** What a second reader buys is a second reading,
   and a document no tool parses can be as wrong as one that ten do — `docs/` is full of Markdown that
   agents act on.
8. **A passing verdict on a failing tree is void.** Re-run the scoped gate after remediation; a green
   review over a red gate is not a review.
9. **A new control for an unobserved failure is Major (YAGNI) unless the spec named it.** A
   killed-process shim, a test-of-the-test, or a prefix allowlist the spec did not name is overbuild.
   Filed-issue review uses the same rule. `ponytail-review` is the skill; this rule is what makes
   YAGNI blocking.

## Finding shape

Every finding states, in this order:

- **Premise** — the fact in the code that starts the argument, with `file:line`
- **Path** — the concrete sequence from that fact to a wrong outcome
- **Verdict** — severity from the taxonomy below, never inflated

A finding without a failure path is an advisory, not a defect. Advisories state
**Premise → Improvement → Fix** and never block.

Severity uses the scheme tlc's validation report already ships, so the Verifier and deep-review speak
one vocabulary:

| Severity | Meaning | Action | Blocks |
| --- | --- | --- | --- |
| `Blocker` | Data loss, security hole, or the feature does not work | Fix now | yes |
| `Major` | Behaviour deviates from the spec, or a likely crash under real input | Fix now | yes |
| `Minor` | A spec edge case is unhandled, or a real maintenance hazard | Fix if it blocks a journey, else file an issue | only if blocking |
| `Cosmetic` | Style, naming, structure — a nitpick by definition | File an issue | never |

**Any unfixed `Blocker` or `Major` means the verdict is `FIX_BEFORE_SHIP`.** Nothing else triggers a
round. `Minor` that does not block, and every `Cosmetic`, become issues filed for later work — they
never hold a pull request.

Filed issues are real work, not a disposal bin. They enter the backlog like any other item.

## Fixing a filed issue

**A filed issue does not re-enter the loop above.** It was already reviewed — that is how it came to be
filed — so a verifier, a QA pass and two review rounds would re-do work that is already done. The
whole point of filing it was to get it out of the feature's critical path, not to move the ceremony
to a later date.

Fix one, or a batch of them, as a small change:

```
implement → scoped gate → one commit for the batch
```

No spec, no tasks file, no verifier, no deep-review round. `tlc-spec-driven` already sizes this way:
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

Past a cap, remediation continues locally: run the scoped gate after every attempt and record that attempt's **failure signature** — the sorted set of failing test identifiers for the failing gate command, normalized to drop timings, absolute paths and line numbers, which shift on any edit and would make every attempt read as progress. Assertion messages stay in the halt report as diagnosis and never enter the comparison, so message churn cannot read as progress either.

An attempt makes progress only when its set of failing tests is strictly smaller than the fewest failing tests seen so far in this remediation loop; anything else — the same count, a larger one, or a different set of the same size — is a stalled attempt. That running minimum only decreases, so the loop is finite by construction: progress events are bounded by the initial failing count, and at most `stall_attempts` stalls sit between any two. Progress starts the next attempt, with no new human authorization. Halt once `stall_attempts` consecutive attempts stall, or when the gate cannot be made to run, and hand the human the repeated failure signature, the attempt count that produced it, every fix tried, and the recommended call. `stall_attempts` is `.my-workflow.toml` `[remediation]`, default `3`; `0` never halts for a stall. The accepted cost: a fix that does not push the count below the best seen so far reads as a stall, which costs a halt report to read, not a broken tree. No new review round opens past a cap — the caps stand. Local fixes only; every remote action keeps the authorization it already had.

## Requirement and contract parity

A green gate proves the code compiles, lints and passes its tests. It does not prove the code matches
the spec. Every reviewer additionally compares the deliverable against the canonical artifacts —
`spec.md` acceptance criteria, `tests.md` cases, and the `uiux.md` / `dx.md` surface contracts when
they exist — field by field, not by paraphrase.

The failure this prevents is specific: a change can pass many review rounds while contradicting the
spec's canonical contract, because every round measured engineering quality against the task file's
paraphrase and nothing ever compared it to the source.
