# Project state

### AD-007

- **Decision**: Bound post-cap remediation by consecutive stalled attempts, not by an open blocker.
  The failure signature is the sorted set of failing test identifiers; progress is a strictly smaller
  set, and the assertion message is reported but never compared. A run halts once `stall_attempts`
  consecutive attempts fail to shrink that set. The threshold is consumer-owned in
  `.my-workflow.toml` (`[remediation] stall_attempts`), defaults to `3`, and `0` means unbounded.
- **Reason**: The review caps bound how often a reviewer produces new findings, which already
  converges. The halt they fed bounded the wrong quantity: a blocker with a diagnosed root cause and
  a named next fix ended an unattended run that the operator would always have told to continue.
- **Trade-off**: A fix that changes which tests fail without reducing the count reads as a stall and
  costs a halt report to read. That is accepted: requiring consecutive *identical* signatures was
  insufficient, because one flaky test or one unnormalized PID, port or object address in a message
  keeps the signature changing forever and the bound never fires. Shrinking is the only progress a
  cosmetic change cannot fake.
- **Scope**: `docs/guidelines/REVIEW-ROUNDS.md`, `.agents/skills/autonomous/SKILL.md`,
  `.agents/skills/workflow-config/` and its resolver, `.my-workflow.toml.example`, `README.md`.
- **Date**: 2026-08-23
- **Status**: active

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
