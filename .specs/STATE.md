# Project state

## Handoff

- **Feature**: `.specs/features/host-agnostic-slice-parallelization`
- **Phase / Task**: QA Execute / halted at Retest 10 on a new Critical assisted-transport defect
- **Completed**: T1-T5; Technical Verifier PASS; Deep Review rounds 1-2; assisted Orca lifecycle hardened; QA Execute Retests 1-10; Retest 8 proved 60.694s A/B overlap, exact B parking, exact A:T7 sync, same-handle continuation, fresh per-slice Technical Verifiers, conflict-free A-then-B integration at `2051517` with fixture gate 9/9, and exact cleanup; Retest 9 closed `BUG-20260827-medium-route-contract-test-still-expects-low` through `395a691`; Retest 10 rewrote the rendered route proof for the all-Claude snapshot and proved `Claude Code` + `Sonnet 5` + `with low effort` on two consecutive `source=screen` frames for both slices, seeded the conflict-free fixture at `a86a9dd` (2 hunks, 13 immutable context lines, gate 1/1), delivered and reconciled `A_T1` packet-exactly at `61302ad`, overlapped both workers for 17.601s at concurrency 2, and cleaned up 11/11 with a 93-sample zero-residue audit
- **In-progress** (file:line): none
- **Next step**: Close `BUG-20260827-orca-terminal-send-truncates-claude-worker-packet` in the assisted contract — the contract owner picks between an acknowledging `terminal send` mode, a normative post-send rendered-packet readback that fails closed before the worker acts, or a file-based packet handoff that keeps the payload off the TUI input. Then a fresh QA Verifier re-walks `QAS-coordinate-assisted-orca-slices` end to end, proving packet delivery before each task turn, and only then reaches the newline fix loop, grouped Deep Review, final CLI persona QA, and the fixture full gate.
- **Blockers**: `BUG-20260827-orca-terminal-send-truncates-claude-worker-packet` (open, critical) blocks the assisted walk on the Claude route: `orca terminal send --text` returns `ok=true` with the full `bytesWritten` while the Claude Code TUI receives only a mangled tail fragment (measured 36 of 2081 characters), and the contract's one-send, no-replacement-worker rules make the loss unrecoverable. `BUG-20260827-assisted-pilot-batch-cli-drops-final-newline` (open, major) is still the sole open grouped Deep Review Major and stops final persona QA; it was unreachable for the second consecutive cycle because its fixture only exists inside a completed pilot run. Codex capacity remains exhausted until 2026-09-01. Retest 11 needs a live Orca session and is human-scheduled.
- **Uncommitted files**: none.
- **Branch**: `feat/host-agnostic-slice-parallelization`

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

- **Decision**: `.my-workflow.toml` is the single editable source for bundled Claude, Codex, and
  Cursor agent models and efforts. Provider packet metadata is generated through explicit sync, and
  delegated model settings freeze in each feature workflow snapshot.
- **Reason**: Provider-specific model pins duplicate one operator choice across three syntaxes and
  can silently diverge. The native runtimes still require those fields, so generated metadata keeps
  their contracts while centralizing ownership.
- **Trade-off**: Native packet files remain materialized tracked output, and an active feature needs
  explicit refresh after a deliberate model change. Provider runtimes still decide whether a model
  supports a selected effort.
- **Scope**: `.my-workflow.toml`, provider agent packets, workflow configuration and snapshots,
  adoption, tests, and public workflow documentation.
- **Date**: 2026-08-24
- **Status**: superseded by AD-010

### AD-010

- **Decision**: Track `.my-workflow.toml.example` and provider packet templates, while keeping
  `.my-workflow.toml` and generated `.claude`, `.codex`, and `.cursor` runtime agent trees local and
  ignored. Feature snapshots continue to freeze delegated model and effort settings.
- **Reason**: Provider access, quotas, profiles, models, and efforts vary by operator. Switching them
  must not create repository changes, while agent instructions still need a reviewable source.
- **Trade-off**: A fresh checkout must initialize local config and generate runtime packets before
  custom agents are available.
- **Scope**: Workflow configuration, provider templates/runtime packets, adoption, packaging, tests,
  documentation, and feature snapshots.
- **Date**: 2026-08-24
- **Status**: active

### AD-011

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

### AD-012

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
- **Status**: active

### AD-013

- **Decision**: The provider-neutral coordinator derives and validates a deterministic sibling Git worktree destination, creates that checkout with fixed argv, and gives Orca only an existing worktree to attach a worker to.
- **Reason**: Orca's public worktree-create command does not accept a destination path, while SEC-004 requires destination validation before the first writer or worker process.
- **Trade-off**: The core owns this narrow Git worktree primitive; adapter-specific worker and event effects remain behind the provider-neutral protocol.
- **Scope**: Parallel slice executor worktree creation, adapter contracts, and future worktree/worker providers.
- **Date**: 2026-08-24
- **Status**: active

### AD-014

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

### AD-015

- **Decision**: When automatic host orchestration is incompatible, explicit human authorization may
  enable coordinator-assisted inter-slice execution through the host's direct worktree and terminal
  primitives. The coordinator owns worker launch, dependency checkpoints, same-terminal follow-up,
  synchronization, integration, and cleanup; slice workers never spawn workers. This path never
  marks the automatic adapter compatible.
- **Reason**: Direct Orca worktree creation and prompt delivery work on `1.4.188`, so a supervising
  coordinator can overlap eligible slices without weakening TLC task order, verification, review,
  gates, QA, or fail-closed automatic execution.
- **Trade-off**: The coordinator must supervise and reconstruct parked workers from Orca and Git
  state. It lacks transactional `worker_done`, ack, and release receipts, so dirty, ambiguous,
  conflicting, or unrecoverable state returns to serial execution.
- **Scope**: Autonomous inter-slice coordination, Orca direct worktree/terminal handoffs, dependency
  checkpoints, follow-up, integration, and exact owned-resource cleanup.
- **Date**: 2026-08-26
- **Status**: active
