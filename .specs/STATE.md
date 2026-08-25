# Project state

## Handoff

- **Feature**: `.specs/features/parallel-slice-executor`
- **Phase / Task**: Execute / post-cap grouped C-D review remediation complete
- **Completed**: T1, T2, T2R1-T2R5, T3, T3R1, T3R2, TDR1, TDR2, T4, T4R1, T4R2, T5, T6, T7, T7R1-T7R5; grouped C-D round 1 and post-cap round 2 remediation; Slice A-C Technical Verifiers PASS; grouped deep-review A-B closed
- **In-progress** (file:line): none
- **Next step**: Fresh QA executes the disposable E2E-001 Orca handoff, then the feature-closing QA step records final evidence.
- **Blockers**: no author-run Orca pilot; fresh QA and feature closure remain pending.
- **Uncommitted files**: none
- **Branch**: `feat/parallel-slice-executor`

## Decisions

### AD-001

- **Decision**: Agent always-on is a thin `AGENTS.md` (contract + pointers). `CLAUDE.md` is
  `@AGENTS.md`. Project decisions are looked up via `.specs/AD-INDEX.md`, not by reading
  `.specs/STATE.md`. Planner, implementer and verifier are three windows with different
  packets; models live only on the agent files. The delivery loop is unchanged.
- **Reason**: A `CLAUDE.md` symlink made Cursor inject the contract twice. Design/resume paid
  for the whole decision log. Packets cut that without adding a TLC phase or a front/back split.
- **Trade-off**: Role prose is copied per provider so spawn does not follow a pointer; the
  three copies can drift. Accepted over a renderer until a packet change actually diverges.
  Adopt copies agent folders only when the destination has none, so model pins survive re-adopt.
- **Scope**: `AGENTS.md`, `CLAUDE.md`, `.cursor/agents/`, `.claude/agents/`, `.codex/agents/`,
  `.specs/AD-INDEX.md`, `tools/ad-index.py`, `scripts/adopt.py`.
- **Date**: 2026-08-19
- **Status**: active

### AD-002

- **Decision**: QA planning and QA execution are separate provider-neutral skills dispatched in fresh
  sessions by the existing Verifier. The consuming project selects its adapter through
  `docs/qa/README.md`; the workflow does not mandate or install a QA framework.
- **Reason**: Independent review must be stable across Cursor, Claude and Codex while the consuming
  product remains free to use browser, API, CLI, mobile or manual tooling.
- **Trade-off**: Each consuming project maintains a small operational profile, and a missing runner
  can leave documented manual or blocked legs instead of automatic framework installation.
- **Scope**: `.agents/skills/qa-plan/`, `.agents/skills/qa-execute/`, provider `verifier` packets,
  `docs/qa/README.md`, QA guidelines and workflow docs.
- **Date**: 2026-08-20
- **Status**: active

### AD-003

- **Decision**: `.specs/features/` is ignored local state. Durable project decisions remain tracked in
  `.specs/STATE.md` and indexed by `.specs/AD-INDEX.md`; task commits no longer include `tasks.md`.
- **Reason**: Feature specs, designs, tasks, memory and validation reports are execution scaffolding,
  not the public workflow contract.
- **Trade-off**: A fresh clone cannot resume an in-progress local feature from Git; the active
  checkout owns its planning state until durable knowledge is promoted.
- **Scope**: `.gitignore`, `AGENTS.md`, TLC workflow guidance, artifact lifecycle and commit evidence.
- **Date**: 2026-08-20
- **Status**: superseded by AD-007

### AD-004

- **Decision**: Workflow routing is consumer-configurable in `.my-workflow.toml`. The public
  hierarchy is `Feature -> Vertical Slice -> Task`; deep-review accepts `slice`, `feature`, or
  balanced `grouped.N`, defaults to `grouped.3`, and freezes its effective route in the feature
  snapshot before dispatch. Technical Verifier remains per code-changing slice; QA closes the
  feature after the final review group.
- **Reason**: Deep-review per slice repeatedly rereads shared context and wastes tokens. A single
  canonical resolver makes cadence and mixed-provider routing explicit without duplicating provider
  definitions or moving project gates and QA policy into workflow config.
- **Trade-off**: A project can choose less frequent deep-review and must inspect the frozen snapshot
  when resuming. Provider availability is an explicit orchestrator concern; the resolver never falls
  back silently.
- **Scope**: `.my-workflow.toml`, `.agents/skills/workflow-config/`, `AGENTS.md`, review guidance,
  workflow docs, and adoption.
- **Date**: 2026-08-21
- **Status**: active

### AD-005

- **Decision**: Keep the optional, checkout-local Graft `0.10.1` integration as the deep-review
  context aid. Graft failure, absence, stale output, and dot-directory coverage always fall back to
  plain repository inspection; Graphify is not adopted.
- **Reason**: The completed local trials showed Graft improved repository-map and symbol context,
  while the project requires a non-blocking review path and has no evidence to justify replacing it
  with Graphify.
- **Trade-off**: The workflow carries a pinned optional tool and its installation surface, while
  hosts without it retain full review functionality through ordinary inspection.
- **Scope**: `.agents/skills/deep-review/`, `package.json`, lockfiles, deep-review tests and
  documentation.
- **Date**: 2026-08-22
- **Status**: active

### AD-006

- **Decision**: Keep the workflow stack- and tool-agnostic while allowing optional capability
  integrations. Recommend Graft for deep-review context and OpenDesign for visual iteration; neither
  is mandatory. The repository remains authoritative for approved handoffs, with precedence
  `spec.md` → `uiux.md` → approved design artifact → tool or plugin output, then legacy mockup.
- **Reason**: Optional tools can improve context or iteration without imposing installation, provider,
  framework, or product-specific paths on consuming projects.
- **Trade-off**: Integrations may be absent or fail, so agents use honest repository fallbacks;
  external writers need explicit filesystem boundaries and non-destructive imports.
- **Scope**: `README.md`, `docs/guidelines/UI-UX.md`, `docs/guidelines/SECURITY.md`, optional
  integration skills, and feature snapshots.
- **Date**: 2026-08-23
- **Status**: active

### AD-007

- **Decision**: `.specs/features/` is versioned, durable workflow state. Completed feature state is
  retained by default, archived explicitly when needed, and never auto-deleted.
- **Reason**: Worktrees, gates, handoffs, and audit need the same specs, tasks, snapshots, and
  validation state across branches and fresh checkouts.
- **Trade-off**: The repository retains small planning artifacts and maintainers must choose when to
  archive them.
- **Scope**: `.specs/features/`, `.gitignore`, `AGENTS.md`, artifact lifecycle guidance, and TLC
  workflow state handling.
- **Date**: 2026-08-24
- **Status**: active

### AD-008

- **Decision**: Adopt upstream ai-memory `1.31.0` only as an opt-in, transient handoff transport
  between Claude Code, Codex, and Cursor. Lifecycle hooks and the sourceable Codex helper may create
  one pending baton, but MCP, briefing, routing skills, managed workstreams, LLMs, embeddings,
  consolidation, and auto-improvement remain disabled. Git, `.specs/`, tasks, architecture docs,
  and `knowledge/` remain the only project authority. Reviewer continuity is packet-defined: internal
  Verifier and Deep Reviewer subagents do not consume Implementer handoffs.
- **Reason**: Provider limits can end a session before work is finished; a bounded single-use baton
  resumes the next session without recurring startup context or a second task and decision ledger.
- **Trade-off**: The local runtime stores captured session material outside the checkout and still
  needs explicit path exclusions because free-form prompts and shell output are not a complete DLP
  boundary. Codex requires a manual `handoff` fallback when its process exits abnormally. Dropping
  subagent captures reduces storage noise but does not protect a top-level reviewer; role isolation
  remains an explicit packet rule.
- **Scope**: `scripts/ai-memory.zsh`, `scripts/test_ai_memory.py`, `docs/workflow/ai-memory.md`,
  `README.md`, `docs/guidelines/REVIEW-ROUNDS.md`, `docs/qa/`, the ai-memory feature contracts and
  threat model, and this decision record.
- **Date**: 2026-08-23
- **Status**: active

### AD-009

- **Decision**: Parallelization is an opt-in inter-slice orchestration layer above unchanged TLC;
  `disabled` is the default, `safe` consumes independent or verified cross-slice producers, and
  `full` consumes completed gated checkpoints with sync and revalidation. Uncertainty falls back to
  serial execution; waiting turns end and resume by dependency event; sync occurs at checkpoints,
  and affected evidence is revalidated after integration or remediation.
- **Reason**: Reduce wall time only when isolation and dependency evidence are proven, while keeping
  the reliable sequential task contract and every readiness stage.
- **Trade-off**: Capable orchestrators own worktree/runtime isolation and reconciliation, and full
  mode can pay rebase and repeated evidence costs; tasks inside a slice never run in parallel.
- **Scope**: `.my-workflow.toml`, frozen feature workflow snapshots, workflow-config planning,
  autonomous orchestration, and Verifier/deep-review/QA integration.
- **Date**: 2026-08-24
- **Status**: active

### AD-010

- **Decision**: Parallel execution uses a provider-neutral deterministic coordinator whose adapters
  own external effects. Orca is the first worktree/worker/event adapter; checkpoint sync rebases only
  the private dependent lane, verified slices merge without rewriting their commits, and any missing
  adapter or consumer resource-provider capability falls back to serial execution.
- **Reason**: Restart safety, event correlation, Git evidence, and isolation policy must behave the
  same across agents and IDEs, while real port/runtime/database semantics remain owned by each
  consuming project.
- **Trade-off**: Non-Orca environments stay serial until they implement the conformance protocol,
  and resource-bearing concurrency requires a small project executable plus adoption QA.
- **Scope**: Autonomous parallel execution, workflow snapshots and task resource metadata, Orca/Git
  adapters, consumer resource providers, and future IDE adapters.
- **Date**: 2026-08-24
- **Status**: superseded by AD-011

### AD-011

- **Decision**: The provider-neutral coordinator derives and validates a deterministic sibling Git worktree destination, creates that checkout with fixed argv, and gives Orca only an existing worktree to attach a worker to.
- **Reason**: Orca's public worktree-create command does not accept a destination path, while SEC-004 requires destination validation before the first writer or worker process.
- **Trade-off**: The core owns this narrow Git worktree primitive; adapter-specific worker and event effects remain behind the provider-neutral protocol.
- **Scope**: Parallel slice executor worktree creation, adapter contracts, and future worktree/worker providers.
- **Date**: 2026-08-24
- **Status**: active

### AD-012

- **Decision**: Technical Verifier remediation is bounded per blocker fingerprint, defined by the
  requirement, root cause, and concrete failure path. Distinct blockers start independent counts;
  the same fingerprint halts only after its third failed remediation, and reopening retains its
  identity and count.
- **Reason**: A slice-global round cap can stop an unattended run even while each cycle closes a
  different defect, wasting the delivery window without signalling non-convergence.
- **Trade-off**: A slice with many distinct blockers can run longer, while repeated or renamed
  versions of one blocker remain bounded and all other halt conditions still apply.
- **Scope**: Technical Verifier fix/reverify loops, autonomous halt decisions, TLC verifier guidance,
  review workflow documentation, and their contract tests.
- **Date**: 2026-08-24
- **Status**: active
