# Project state

## Handoff

Idle.

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
- **Status**: active

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

### AD-008

- **Decision**: Adopt upstream ai-memory `1.31.0` only as an opt-in, transient handoff transport
  between Claude Code, Codex, and Cursor. Lifecycle hooks and the sourceable Codex helper may create
  one pending baton, but MCP, briefing, routing skills, managed workstreams, LLMs, embeddings,
  consolidation, and auto-improvement remain disabled. Git, `.specs/`, tasks, architecture docs,
  and `knowledge/` remain the only project authority.
- **Reason**: Provider limits can end a session before work is finished; a bounded single-use baton
  resumes the next session without recurring startup context or a second task and decision ledger.
- **Trade-off**: The local runtime stores captured session material outside the checkout and still
  needs explicit path exclusions because free-form prompts and shell output are not a complete DLP
  boundary. Codex requires a manual `handoff` fallback when its process exits abnormally.
- **Scope**: `scripts/ai-memory.zsh`, `scripts/test_ai_memory.py`, `docs/workflow/ai-memory.md`,
  `README.md`, `docs/qa/`, and this decision record.
- **Date**: 2026-08-23
- **Status**: active
