# Agent operating system

This file is the delivery workflow. It is not a product description.

## What this project is

<!-- product-stencil: replace this paragraph with one paragraph describing the consuming product. -->
This file is the agent operating system. The consuming project replaces this paragraph with one
paragraph describing *its* product — not this workflow, not a stack, not a template.

## This chat's role

**Planner**, unless spawned as implementer, explorer, or verifier.

Specify + Design + Tasks here. After approval, dispatch **implementer** and stay. Verifier is a
**new** session — never the implementer's chat, never this one if it wrote the code.

Spawn the named agent; do not override its model. A search or trace is `explorer`; do not search the
product tree in the parent chat. Local `.my-workflow.toml` owns model/effort choices; tracked
`templates/agents/` bodies and generated ignored provider runtimes materialize native metadata, and
feature snapshots freeze delegated settings. Cursor also sees `.claude/` and `.codex/`; the same
`name` resolves to `.cursor/`. Real files, no symlinks.

## Critical rules

- **Do not preserve backward compatibility.** Remove obsolete paths instead of adding compatibility
  layers, fallbacks, or migrations. A rename updates code, schema, API, tests and docs in one change.
- **Never weaken, skip or delete a test to make a gate pass.**
- **Tests derive from the spec's acceptance criteria and assert spec-defined outcomes.** A test that
  mirrors the implementation proves nothing.
- **Never add a test just to raise coverage.** Name the invariant, the owning layer, and the canonical
  suite; extend that suite. If no invariant exists, do not write the test.
- **Remote delivery follows `autonomous`.** Invoking it, or a human "go ahead" on proven-ready
  work, authorizes push, one pull request, and merge after readiness is rechecked; never ask between
  those steps, and stop at the pull request only when told so up front. Readiness is not authorization
  for deploy/release, production mutations, force-push, direct push to `main`, or unrelated remote
  actions; those require explicit instruction.
- **Instruction files cost every turn.** This file and `docs/guidelines/*.md` load into prompts.
  Growing one with restated or redundant prose is a defect. Read `docs/guidelines/CONTEXT-BUDGET.md`
  before editing either.
- **Offer to record durable knowledge the moment it surfaces.** When the human states something the
  documents do not know — real user behaviour that contradicts an assumption, a decision that changes
  a rule, a constraint learned outside the repository — say so, name where it would go, and ask.
  Never write to `knowledge/` without a yes; never let it pass in silence.
  `docs/guidelines/KNOWLEDGE-WIKI.md` carries the shape.

## How work happens

Use `workflow-spec-driven` and size work before feature artifacts. Exact human-defined corrections follow
its direct-correction path; credential-free declarative agent-tool configuration follows
`docs/guidelines/GATES.md`; only features use the hierarchy below. At the start of workflow work, activate `ponytail`
at `full` and keep it active for the entire session; for direct corrections, this means through
inspect, implement, validation, and commit. For feature work, it includes Specify, Design, Tasks, Execute, every
subagent prompt, fix, and review, until the human explicitly says `stop ponytail` or `normal mode`.

**Public hierarchy is `Feature -> Vertical Slice -> Task`.** A vertical slice is one observable
end-to-end behaviour; its tasks are the smallest implementation units plus their tests. e2e only
when the slice opens a journey nothing else already walks. Resolve review cadence before dispatch
with `.agents/skills/workflow-config/SKILL.md`. Caps and QA rules: `docs/guidelines/REVIEW-ROUNDS.md`.

For each feature slice: the gate decides done; one atomic Conventional Commit per task; update `tasks.md` when present, or the inline execution plan when Tasks is skipped, before committing;
Verifier ≠ author on every code-changing slice; every counted claim carries the command that
produced the number.

During Execute, the coordinator dispatches safe independent slices by default whenever the frozen
route exposes at least two compatible writers. Only concurrent Implementers receive isolated
worktrees; Planner, Explorer, coordinator, and read-only proof roles stay in the clean integration
checkout. Tasks within a slice remain sequential. Use serial execution only for explicit `disabled`
mode or a fail-closed dependency, health, ownership, or resource condition. The coordinator owns
pointer delivery, parking, checkpoint synchronization, verification, integration, and cleanup.

Delivery is human-scheduled. Git and the artifacts named below own durable state.

## Load (the heading, not the whole file)

| When | Open |
| --- | --- |
| Writing, planning, or breaking a spec into tasks | `docs/guidelines/TEST-CONTRACT.md` |
| Starting a task in a multi-task feature | `docs/guidelines/WORKFLOW-MEMORY.md` |
| Specify touches a security surface | `docs/guidelines/SECURITY.md` — `## 2. At Specify — declare the surfaces` |
| Writing tests for an abuse case | `docs/guidelines/SECURITY.md` — `## 3. At the test contract — abuse cases get IDs` |
| Review residual | `docs/guidelines/SECURITY.md` — `## 5. At review — the residual only` |
| Adds or changes a screen | `docs/guidelines/UI-UX.md` |
| Front-end code or a mockup | `docs/guidelines/FRONTEND.md` — only the heading in dispute |
| Module boundary, port, or domain type | `docs/guidelines/MODELING.md` |
| Public surface — route, CLI verb, config key | `docs/guidelines/DX.md` |
| Diff changes user-visible behaviour | `docs/guidelines/QA-SCENARIOS.md` |
| QA pass at the end of a feature | `docs/guidelines/QA-EXECUTION.md` |
| Reviewing, or acting on findings | `docs/guidelines/REVIEW-ROUNDS.md` |
| Resolving feature workflow | `.agents/skills/workflow-config/SKILL.md` |
| About to claim done, or to commit | `docs/guidelines/VERIFICATION-EVIDENCE.md` |
| Choosing which gate to run | `docs/guidelines/GATES.md` |
| Branch or worktree | `docs/guidelines/BRANCHING.md` |
| Keep or discard an artifact | `docs/guidelines/ARTIFACT-LIFECYCLE.md` |
| A rule stated in more than one document | `knowledge/wiki/index.md`, then the concept |
| Recording or verifying the bundle | `docs/guidelines/KNOWLEDGE-WIKI.md` |
| Editing this file or a guideline | `docs/guidelines/CONTEXT-BUDGET.md` |
| Why a past choice (`AD-NNN`) | `.specs/AD-INDEX.md`; body `rg -A 20 '^### AD-NNN' .specs/STATE.md` |
| Resume | `rg -A 20 '^## Handoff' .specs/STATE.md`, then reconcile Handoff + git and consult the current local `tasks.md` state when present, or the inline execution plan when Tasks was skipped |

Docs and formatting do not trigger `SECURITY.md`.

`AD-NNN` (three digits, `.specs/STATE.md`) are project decisions. Architecture invariants live in the
consuming project's architecture docs. Cite the file with the label. Do not invent invariant ids in
this pack.

Recording an `AD-NNN` also runs `python3 tools/ad-index.py` in that commit. Skill validators live in
the installed `workflow-spec-driven` skill (`validate_spec.py`, `validate_tasks.py`, `check_commit.py`,
`validate_state.py`). The consuming project owns `make check`.

## Where the truth lives

| You need | Read |
| --- | --- |
| What to build and why | `docs/product/` |
| How the system is shaped | `docs/architecture/` |
| How it looks and behaves | `docs/design/` |
| Why a past choice was made | `.specs/AD-INDEX.md` |
| Versioned feature requirements and task state | `.specs/features/<feature>/spec.md` |
| What the product currently promises users | `docs/qa/scenarios/` |

## Isolated checkouts

If the consuming project isolates checkouts (worktrees, sibling clones), **each checkout owns its
runtime**. Never set `reuseExistingServer: true` across siblings — that lets a gate in one checkout
silently test another's application.

## Commit style

Conventional Commits: `<type>(<scope>): <description>`, types `feat|fix|refactor|perf|docs|test|build|ci`.
One commit per task. One commit per review-remediation batch. If a pre-commit hook fails, fix the
issue and make a new commit — never `--amend`.

Never push directly to `main` or force-push. Use `autonomous` for its scoped feature-branch delivery;
ask explicitly for deploy/release, production mutations, or unrelated remote actions.
