---
name: autonomous
description: Ship work unattended through a proven-ready tree. Classifies the request as a feature or an issue batch and runs the matching loop; after readiness, the run may push its feature branch, create one pull request, and merge it. Other remote actions remain separately authorized.
disable-model-invocation: true
argument-hint: "[the work, in your own words]"
---

# Autonomous

Run the local work end to end while nobody is watching, prove the tree ready, then deliver the
feature branch within this skill's remote scope.

`AGENTS.md` owns the process. Run it. This skill owns only what an **unattended** run needs on top:
what to settle before starting, when to **halt**, and how to report remote-delivery readiness.

## Run to the end

Nobody is reading. A run that finishes Specify and reports for acknowledgement has stopped, and it
stays stopped until someone happens to look — which is the whole cost the human was avoiding. A run
that proves readiness continues through the scoped remote delivery below.

For feature runs, carry straight through Specify, Design, Tasks and Execute. Announcing what just
finished is fine; waiting after announcing it is not. A run ends **merged only after readiness and
the scoped delivery steps are complete**, or **halted** on the conditions listed at the end of this
file.

Ambiguity that does not change what gets built is a decision to make, record in `decisions.md`, and
move past — not a reason to pause. Only the halt conditions stop the run, and hitting one ends it
rather than pausing it: write the report and stop for good.

A phase boundary is not a checkpoint. The run reaches the end of the work or it reaches a halt.

## Classify the run first

The human describes the work in their own words. Decide which of two paths it takes, state the
choice in one line with the reason, and proceed — this is a judgment to make, not a flag to be given.

| The work is | Path |
| --- | --- |
| **A direct correction** — an exact human-defined single invariant with no product ambiguity or implicit-requirement surface | The direct-correction path in `workflow-spec-driven` |
| **A feature** — a capability or behaviour the product lacks | The full loop in `AGENTS.md` |
| **An issue batch** — work already filed and reviewed | The filed-issue path in `docs/guidelines/REVIEW-ROUNDS.md` |

The test is whether the work was already read by a reviewer. A filed issue was — that is how it came
to be filed — so it does not re-enter the feature loop. Running a verifier and two review rounds over
a one-line fix re-does work already done, which is the ceremony this workflow exists to remove.

Two cases that look ambiguous and are not:

- **A defect nobody filed** takes the direct-correction path when it meets that predicate; otherwise
  it takes the feature path at its auto-sized depth.
- **A request spanning both** — "fix the P2s and add the new capability" — splits into separate runs
  with separate pull requests. One run, one path; a batch that grows a feature inside it stops being
  a batch.

## 1. Ground

**A feature:** name it in one sentence, then find the seam — the exact place the product stops. A
hardcoded constant, an enum nothing writes, a table with no reader. With no feature named, take the
next one: read the consuming project's product spec against the code that exists.

**An issue batch:** read every candidate issue in full with `gh issue view`. Labels here are sparse —
most issues carry none — so select by reading, not by filtering, and say which issues you selected
and which you left. Map the human's severity words onto the taxonomy: P0 is `Blocker`, P1 `Major`,
P2 `Minor`, P3 `Cosmetic`.

Before taking an issue, ask whether we would write it if the ticket did not exist. If not: skip it,
comment why, and do not dispatch.

Group by what a single reading covers: issues in one area, sharing a cause, or touching one file.
Issues that depend on each other belong in one batch even when that makes it larger.

**Done when:** for a feature, you can cite `file:line` for the code that stops it being true today;
for a batch, every selected issue is read and grouped, with the ones you skipped named.

## 2. Settle every decision, or halt now

For feature runs, list the decisions the work needs that the documents do not already answer. Either decide from
evidence in the repository and record it as an `AD-NNN` in `.specs/STATE.md`, or mark it as needing
the human.

A decision recorded with its reasoning is reversible in the morning. A decision made silently inside
an implementation is found months later.

**Halt here** if any remaining decision would change what gets built.

**Done when:** every decision is either an `AD-NNN` or a named blocker in the halt report.

## 3. Do the work

**A feature:** follow `AGENTS.md`'s `Feature -> Vertical Slice -> Task` hierarchy and resolve the
feature workflow with `.agents/skills/workflow-config` before dispatch. Three rules an
unattended run gets wrong:

When the frozen workflow is resolved, read
`.agents/skills/autonomous/references/parallelization.md` after workflow resolution and before
planning. Assisted dispatch is the default. Independent compatible slices may open together;
serial execution is used when exactly one ready slice exists, explicit `disabled` mode, or any
fail-closed condition; concurrent isolated writer worktrees require at least two compatible ready
slices.

- **Every implementation slice closes its technical review before any dependent slice consumes its
  checkpoint** — implement, scoped gate, commit, and a fresh Verifier on the private writer
  checkpoint. A single ready slice runs serially in the clean integration checkout; only two or
  more compatible ready slices may open concurrent writer worktrees. Deep-review runs at the resolved
  groups on the integrated tree, before fresh final QA. Author and proof identities stay distinct.
- **One pull request for the feature**, with the slices as atomic commits inside it.
- **The feature-closing step is the QA session** and writes no product code, so it takes no Verifier
  and no deep-review.

**A direct correction:** follow the direct-correction path in `workflow-spec-driven`: inspect, implement,
run the scoped validation, and commit. Create no feature artifacts and skip fresh Verifier,
deep-review, and QA.

**An issue batch:** `implement → scoped gate → one commit per batch`. No spec, no verifier, no
deep-review round. Three things still fire, because they are about the change rather than the review:
a user-visible fix flags and walks its scenario, a fix touching a security surface reads
`docs/guidelines/SECURITY.md`, and a fix that grows — a schema change, a boundary crossed, a design
question opened — stopped being a filed issue and takes the feature path instead. Say so when that
happens.

Close each issue in the commit that fixes it (`Closes #NN`), and leave open any you could not finish
with a comment saying why.

**Done when:** for a feature, every implementation slice has its Verifier result, every resolved
deep-review group is complete, any flagged scenario is walked, and the final QA session is complete; for a batch, every
selected issue is fixed and closed or explicitly left open with a reason.

## 4. Prove readiness, then deliver within scope

The following conditions prove that a remote delivery would be safe to consider:

| | |
| --- | --- |
| The applicable gate exits 0 | The full gate for feature work, or the scoped gate for a direct correction, on the final tree after the last commit. A cached or partial result is not evidence. `make check` when the project has it |
| No blocking findings remain | `Blocker` and `Major` per `docs/guidelines/REVIEW-ROUNDS.md` |
| `main` has not moved underneath | If it has: integrate it, re-run the full gate, then re-prove readiness |
| Every flagged scenario is terminal | See the three cases below. Only when the change is user-visible |

What each verdict does to readiness:

- **`pass`** — readiness may proceed to the scoped delivery steps.
- **`untested`** — **blocks.** It was flagged and never walked, which is a promise nobody checked and
  the one failure a green gate cannot catch. Walk it, or get an explicit waiver and record the waiver
  as an `AD-NNN` so remote delivery does not rest on silence.
- **`blocked-verify`** — does not block readiness, and the eventual pull request names it. Some legs
  only a human can complete; a feature touching one of them would otherwise never be deliverable.

Invoking `$autonomous` authorizes this run to push its feature branch, create at most one pull
request, and merge that pull request after readiness is rechecked immediately before the merge.
A human "go ahead", "proceed", or "ship it" on proven-ready work carries the same authorization.
**Do not ask for confirmation between push, pull request, and merge**: readiness is the check, and
asking is the stall this skill exists to remove. The only stop short of merge is the human saying
so up front, for example `$autonomous, stop when the PR is ready`; then halt after the pull request
with readiness restated. Re-check readiness and repository state after each delivery step before
starting the next one.

This authority excludes deploy or release, production mutations, force-push, direct push to `main`,
and unrelated remote actions; those require explicit instruction. Readiness is evidence, not
authorization for those actions.

The merge commit carries one `Review-Signal` trailer for the pull request, aggregating its
slices through `slices` and `verified`, so the review record survives the pruning of
`.specs/features/`. Grammar and keys: the `check_commit.py` docstring.

One pull request per run — a batch of issues ships together, the same way a feature's slices do.

**Done when:** readiness is proven and the scoped feature-branch push, one pull request, and merge
are complete, or the run halted with the reason and the out-of-scope action awaiting instruction.

## 5. Report

For feature work, write `.specs/features/<slug>/decisions.md` — everything the run chose while
nobody was watching, in a form a stakeholder can review and reverse. It is the deliverable that
makes an unattended run accountable, so it is written even when the run halts. Direct corrections
have no feature artifact to report.

Each decision carries: **what was chosen**, **why**, **the alternatives rejected and why**, **what it
would cost to change now**, and **what it costs the user today**. Decisions weighty enough to outlive
the feature also go to `.specs/STATE.md` as an `AD-NNN` and are named here; the rest are a table.

Separate the decisions the human handed down from the ones the run made — a reviewer reading in the
morning needs to know which are theirs.

Then leave, in the pull request and in the final message: what shipped, the full-gate evidence, and
— for a batch — which issues closed and which were left, with why.

**Done when:** every choice the run made that the documents did not dictate appears in
`decisions.md`, including the ones that felt too small to mention, which are the ones a reader most
needs to see.

Post-cap remediation records through `.agents/skills/workflow-spec-driven/scripts/review_convergence.py`,
which delegates pure transitions to `.agents/skills/autonomous/remediation.py`; the review cap remains
owned by `docs/guidelines/REVIEW-ROUNDS.md`.

## Halt conditions

Stop, write up what exists, and do not continue delivery:

- A decision from step 2 would change what gets built
- The post-cap scoped gate is unavailable, or the configured remediation stall threshold is reached
  under `docs/guidelines/REVIEW-ROUNDS.md`; an open blocker alone does not halt while attempts are
  establishing new failure-set minima. Count attempts by the same immutable blocker fingerprint,
  persist each failed Verifier result with `review_convergence.py`, and halt at that configured
  threshold; the final deep-review round has no round 3.
- The work turns out to need a capability that does not exist yet
- The full gate cannot be made to run
- A required action is outside the scoped delivery authority and lacks explicit instruction

A halt report naming what stopped the run is a result. Shipping past a blocker to have something
merged by morning is not.

## Isolated checkouts

A gate refusing because a runtime is already bound means another process holds this checkout's
runtime. Identify the owner, then:

- Another checkout of this repository: stop it there.
- A process from **another project** keeps running — move this checkout instead.

Never set `reuseExistingServer: true` across siblings. See `docs/guidelines/BRANCHING.md`.
