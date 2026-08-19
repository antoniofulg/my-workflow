# Agent operating system

This file is the delivery workflow. It is not a product description.

## What this project is

<!-- product-stencil: replace this paragraph with one paragraph describing the consuming product. -->
This file is the agent operating system. The consuming project replaces this paragraph with one
paragraph describing *its* product — not this workflow, not a stack, not a template.

## Critical rules

- **Do not preserve backward compatibility.** Remove obsolete paths instead of adding compatibility
  layers, fallbacks, or migrations. A rename updates code, schema, API, tests and docs in one change.
- **Never weaken, skip or delete a test to make a gate pass.**
- **Tests derive from the spec's acceptance criteria and assert spec-defined outcomes.** A test that
  mirrors the implementation proves nothing.
- **Never add a test just to raise coverage.** Name the invariant, the owning layer, and the canonical
  suite; extend that suite. If no invariant exists, do not write the test.
- **Approval authorizes local work only.** A spec or task approval covers scoped local changes and
  atomic local commits. Push, pull request, merge, deploy and production database changes each need an
  explicit go-ahead in the prompt.
- **Instruction files cost every turn.** This file and `docs/guidelines/*.md` load into prompts.
  Growing one with restated or redundant prose is a defect. Read `docs/guidelines/CONTEXT-BUDGET.md`
  before editing either.
- **Offer to record durable knowledge the moment it surfaces.** When the human states something the
  documents do not know — real user behaviour that contradicts an assumption, a decision that changes
  a rule, a constraint learned outside the repository — say so, name where it would go, and ask.
  Never write to `knowledge/` without a yes; never let it pass in silence.
  `docs/guidelines/KNOWLEDGE-WIKI.md` carries the shape.

## How work happens

Use the `tlc-spec-driven` skill. It auto-sizes: a one-line change gets no spec, a multi-component
feature gets full planning. The guidelines below increment it — they never replace its four phases.

**Activate `ponytail` at `full` intensity before writing, refactoring, fixing or reviewing any code,
and keep it active through completion.** It asks whether the task needs to exist, reaches for the
standard library before custom code and a native platform feature before a dependency, and prefers
one line to fifty. This workflow already says to delete rather than bridge and to add no test
without an invariant; `ponytail` is the same instinct applied to the code itself.

**Tasks are atomic vertical slices.** One task delivers one observable behaviour — a user or an API
caller can see the difference — together with the tests that prove it, at the cheapest layer that
discriminates it. Unit for domain rules and error paths, integration for anything crossing a
boundary, and an e2e **only when the slice opens a journey nothing else already walks**. A second
slice inside an existing journey proves itself at the integration layer, not the browser. Tests are
never separate tasks, and a slice that is not observable or not complete is not a slice.

The loop, with its caps:

```
per slice    implement → scoped gate → atomic commit          (Conventional Commits)
             Verifier — spec-anchored check + mutation sensor  ≤3 fix rounds, then escalate
             QA — walk this slice's scenarios                  only if it has a user-visible surface
             deep-review                                       ≤2 rounds, blocking findings only

last slice   the QA session — charters, tours, lenses, paper cuts, the dated report
then         full gate → pull request
```

**Review is scoped to the slice, deliberately.** Rounds do not grow with a diff, they explode with
it: every round re-reads the whole change and every remediation moves what the next round reads.
Three rounds over one behaviour is a signal; twenty over a finished feature is the size talking. The
slice is small so the review can be.

Every slice gets a Verifier and a deep-review, including a documentation-only one. QA fires only when
the slice puts something in front of a user; a backend slice has no journey to walk.

The **last slice is the QA session** — the holistic pass that needs the whole feature and cannot run
on part of it. It gets no Verifier and no deep-review of its own: it writes no product code.

**That loop is for a feature.** A filed issue from an earlier review was already read once, so fixing
it is `implement → scoped gate → one commit for the batch` — no verifier, no QA pass, no review
round. `docs/guidelines/REVIEW-ROUNDS.md` carries the three exceptions.

Rules that hold at every size:

1. The gate decides a task is done, not self-assessment.
2. One atomic commit per task. Mark the task complete in `tasks.md` in that same commit.
3. The Verifier is a different actor than the author and runs automatically on every slice that
   changes code. It re-derives coverage independently and injects behavioural mutants to prove the
   tests kill them.
4. Every round of any reviewer contains only findings not already raised in a prior round.
5. Only `Blocker` and `Major` findings trigger another round. `Minor` that does not block, and every
   `Cosmetic`, become filed issues.
6. The stages never loop back into each other. Worst case is six passes for one slice — three
   Verifier rounds, one QA walk, two deep-review rounds — then it escalates to the human regardless
   of what remains.
7. Every claim that counts or measures something carries the command that produced the number.

## Read before you act

Load a guideline when its condition fires. Do not load them speculatively.

| When | Read |
| --- | --- |
| Writing or planning any test | `docs/guidelines/TEST-CONTRACT.md` |
| Starting any task in a multi-task feature | `docs/guidelines/WORKFLOW-MEMORY.md` |
| The change touches runtime code, config, dependencies, schemas, deployment, data flows or public behaviour | `docs/guidelines/SECURITY.md` |
| The feature adds or changes a screen | `docs/guidelines/UI-UX.md` |
| Writing or reorganizing front-end code, or a mockup | `docs/guidelines/FRONTEND.md` |
| Changing a module boundary, a port, or modelling a domain type | `docs/guidelines/MODELING.md` |
| The feature adds or changes a public surface — route, CLI verb, config key | `docs/guidelines/DX.md` |
| The diff changes user-visible behaviour | `docs/guidelines/QA-SCENARIOS.md` |
| Running the QA pass at the end of a feature | `docs/guidelines/QA-EXECUTION.md` |
| Reviewing code, or acting on review findings | `docs/guidelines/REVIEW-ROUNDS.md` |
| About to claim anything is done, or to commit | `docs/guidelines/VERIFICATION-EVIDENCE.md` |
| Choosing which gate to run | `docs/guidelines/GATES.md` |
| Creating a branch or a worktree | `docs/guidelines/BRANCHING.md` |
| Deciding whether an artifact is kept or discarded | `docs/guidelines/ARTIFACT-LIFECYCLE.md` |
| Planning against a rule stated in more than one document — a domain term, an invariant, a product rule | `knowledge/wiki/index.md`, then the concept |
| Recording knowledge in, or verifying, the bundle | `docs/guidelines/KNOWLEDGE-WIKI.md` |
| Editing this file or any guideline | `docs/guidelines/CONTEXT-BUDGET.md` |

## Where the truth lives

| You need | Read |
| --- | --- |
| What to build and why | `docs/product/` |
| How the system is shaped | `docs/architecture/` |
| How it looks and behaves | `docs/design/` |
| Why a past choice was made | `.specs/STATE.md` — `AD-NNN`, append-only |
| What a feature must do | `.specs/features/<feature>/spec.md` |
| What the product currently promises users | `docs/qa/scenarios/` |

Two decision namespaces exist and they are not the same. `AD-NNN` with three digits, in
`.specs/STATE.md`, are project decisions. Architecture invariants live in the consuming project's
architecture docs. Always cite the file with the label. Do not invent invariant ids in this pack.

## Isolated checkouts

If the consuming project isolates checkouts (worktrees, sibling clones), **each checkout owns its
runtime**. Never set `reuseExistingServer: true` across siblings — that lets a gate in one checkout
silently test another's application.

## Commit style

Conventional Commits: `<type>(<scope>): <description>`, types `feat|fix|refactor|perf|docs|test|build|ci`.
One commit per task. One commit per review-remediation batch. If a pre-commit hook fails, fix the
issue and make a new commit — never `--amend`.

Never push to `main`, force-push, or merge without an explicit instruction.

## History

Delivery is human-scheduled. Git and the artifacts named above own durable state.
