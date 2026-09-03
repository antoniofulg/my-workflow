# Project state

## Handoff

- **Feature**: `phase-skills` (branch `feat/phase-skills`, roadmap slice 1 of `docs/workflow/roadmap.md`)
- **Phase / Task**: complete; awaiting human go-ahead to push and open the pull request
- **Completed**: S1, S2, T12 remediation; deep review rounds 1 (FIX_BEFORE_SHIP) and 2 (SHIP); QA plan and QA execute 10/10 pass; feature `validation.md` PASS, sensor 10/10; `validate_state.py` exit 0; `bun run test:all` exit 0 at load 17
- **In-progress** (file:line): none
- **Next step**: push `feat/phase-skills`, open one PR to `main`; merge commit carries
  `Review-Signal: tier=large slices=2 verified=2 sensor=29/31 rounds=2 findings=7 fixed=7 dismissed=0`.
  Then roadmap slice 2 (`/w*` fork entry points, `wreview`, `wqa`).
- **Blockers**: none for this feature. Live Orca transport stays `blocked-verify`
  (`BUG-20260827-orca-terminal-send-truncates-claude-worker-packet`).

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
- **Status**: superseded by AD-019

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
- **Status**: superseded by AD-015

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
- **Date**: 2026-08-28
- **Status**: superseded by AD-016

### AD-015

- **Decision**: Replace the vendored TLC phase-batch delegation with a workflow-owned,
  CC-BY-4.0-attributed spec-driven skill that dispatches vertical slices through hybrid assisted
  execution. Only concurrent writers receive worktrees; tasks within a slice remain sequential;
  fresh Verifier, Deep Review, and QA sessions remain independent. Adaptive concurrency starts at
  two workers and may scale one lane at a time to a default ceiling of four when a machine-only
  health proof and resource leases permit it. Context cleanup and slice-scoped packets are part of
  the foundation, not a later optimization. This decision supersedes AD-011's opt-in modes,
  unchanged-TLC premise, and default-disabled policy; AD-012 through AD-014 remain active.
- **Reason**: The current TLC skill teaches sequential phase batches, while the approved workflow
  uses safe vertical slices as the unit of concurrent delivery. A single, lean contract removes
  contradictory scheduling instructions and reduces repeated context.
- **Trade-off**: The workflow owns a maintained adaptation and additional scheduler/resource
  machinery. Independent proof still consumes tokens, and unavailable health evidence prevents
  scaling above the safe baseline.
- **Scope**: Agent instructions, spec-driven skill and references, role packets, workflow snapshot
  schema, planner/executor scheduling, resource provider and health probe, worktree lifecycle,
  adoption, verification, QA, and context-budget evidence.
- **Date**: 2026-08-28
- **Status**: active

### AD-016

- **Decision**: A halted blocker fingerprint may resume only after explicit human authorization
  creates a new audit generation under that same fingerprint. The prior generation, cumulative
  failure count, halt event, and authorization reference remain immutable; only the new
  generation-local failure count starts at zero, and only a fresh independent PASS may close it.
- **Reason**: A human must be able to authorize a redesigned remediation after a legitimate halt
  without erasing why the autonomous run stopped or bypassing convergence by rewording the finding.
- **Trade-off**: Convergence state gains generation history and an explicit resume operation; a
  halted path cannot continue through JSON edits, a replacement fingerprint, or an ordinary result
  record.
- **Scope**: Technical Verifier convergence state, autonomous halt/resume decisions, review
  guidance, and their contract tests. Supersedes AD-014.
- **Date**: 2026-08-28
- **Status**: active

### AD-017

- **Decision**: Heavy test commands use an explicit named kernel lock separate from lane-wide
  resource-provider leases. The default scope coordinates linked worktrees of one project; an
  explicit machine scope coordinates projects using the same resource name. Adoption installs the
  dormant wrapper with the `parallel` layer and never rewrites consumer-owned test commands.
- **Reason**: A lane lease serializes implementation and light tests along with the contested gate,
  while a command lock preserves concurrency until the exact browser, database, container, or media
  command begins.
- **Trade-off**: Consumers must classify and wrap their heavy commands. Incorrectly unwrapped gates
  remain concurrent, while overly broad resource names reduce useful parallelism.
- **Scope**: Parallel adoption inventory, heavy-gate execution, project test commands, and local
  process-isolation guidance.
- **Date**: 2026-08-30
- **Status**: active

### AD-018

- **Decision**: The gate fingerprint is `sha256` over the gate label, the exact command argv, and
  the Git tree object written from a temporary index seeded with the checkout index and refreshed
  with every non-ignored worktree file. Records live in checkout-local ignored `.gate-cache/`.
- **Reason**: One `git write-tree` names the exact content the gate could read, honours `.gitignore`,
  changes on any edit, and does not change on a commit alone — which is the invalidation rule
  `docs/guidelines/GATES.md` already states. Hand-rolled file walks restate Git badly.
- **Trade-off**: Interpreter, dependency-binary, and environment versions are outside the key, so a
  toolchain upgrade needs the cache directory deleted. A document-only edit also invalidates code
  gates; that is conservative in the safe direction.
- **Scope**: The gate cache tool. Whether a cached record may be cited as readiness evidence is a
  separate decision, deferred with the wiring; `.agents/skills/autonomous/SKILL.md` still refuses
  cached results and this delivery does not change it.
- **Date**: 2026-09-01
- **Status**: active

### AD-019

- **Decision**: Cross-provider session continuation is owned by the host. Repository files, Git
  state, feature artifacts, and explicit handoff prompts remain the durable semantic context.
- **Reason**: Host-native continuation now covers provider unavailability, instability, and token
  exhaustion; Praxis CRM proved the approach with Orca's `Continue in New Session`, selectable
  destination agents, focused handoffs, older transcript access, and unchanged original sessions.
- **Trade-off**: Host capabilities vary, so the repository provides no replacement runtime,
  wrapper, database, hook, protocol, or compatibility layer; operators use the host UI to continue.
- **Scope**: Cross-provider continuation guidance, reviewer packets, adoption, QA, and release
  contracts in this workflow pack.
- **Date**: 2026-08-25
- **Status**: active

### AD-020

- **Decision**: Vertical slice count is derived from validated task outcomes that remain worth
  merging if all later slices are cancelled. Technical phases, cohorts, directories, runners, and
  worker batches do not create slices without an independently mergeable outcome.
- **Reason**: A manual count froze technical organization as delivery structure and multiplied
  Verifier, gate, and review cost before Tasks proved the cut.
- **Trade-off**: Every planned primary task must declare slice membership and every slice needs an
  explicit closure row; old task documents require the new contract before refresh, while normal
  resume keeps its frozen snapshot.
- **Scope**: TLC task templates and validation, workflow configuration, parallel task planning,
  feature snapshots, adoption, tests, and workflow documentation.
- **Date**: 2026-08-27
- **Status**: active

### AD-021

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
- **Status**: superseded by AD-015

### AD-022

- **Decision**: The assisted coordinator writes each complete slice packet to a coordinator-owned
  file outside every slice worktree and sends only a short fixed-shape pointer to that file through
  the host's one mandated `terminal send`. The inline-packet transport is removed, not retained as a
  fallback or length-threshold alternative. `exec_payload` and the pre-packet recording obligations
  are unchanged.
- **Reason**: `BUG-20260827-orca-terminal-send-truncates-claude-worker-packet` proves
  `orca terminal send --text` reports a complete write while the receiving TUI gets a mangled
  fragment. Loss is timing-dependent, `--text` is the only expressible transport, and the one-send
  and no-replacement-worker rules make the loss unrecoverable. A pointer keeps the mandated payload
  at a size the observed loss did not reach.
- **Trade-off**: This does not make the host transport reliable; it only shrinks the mandated
  payload. The coordinator owns packet-file lifecycle outside every worktree, and the worker must
  read a file before acting. A truncated pointer cannot produce a valid marker, so truncation still
  fails closed rather than half-executing.
- **Scope**: Assisted Orca packet delivery, the `parallelization.md` contract, AST-04, IT-005, and
  the assisted QA charter and scenario.
- **Date**: 2026-08-27
- **Status**: active

### AD-023

- **Decision**: `assisted` is the default inter-slice execution mode whenever the frozen task DAG
  exposes independent safe slices. The main agent owns direct worktree and terminal creation,
  pointer-only packet delivery, dependency parking, producer verification, exact commit sync,
  affected-gate rerun, same-handle continuation, deterministic integration, and cleanup. `disabled`
  is the explicit sequential override; `safe` and `full` retain their automatic-adapter semantics.
  Fewer than two ready slices or any isolation, resource, ownership, or reconciliation uncertainty
  falls back to sequential execution. AD-022 remains active until upstream transport is proven.
- **Reason**: Retest 12 proved useful overlap and exact cleanup under supervised coordination, while
  the upstream Orca transport and lifecycle gaps still prevent trustworthy automatic orchestration.
- **Trade-off**: Default development can consume more local CPU and memory, and the main coordinator
  must supervise fail-closed mechanics until upstream support replaces the workaround. Operators who
  need lower machine use must select `disabled` explicitly.
- **Scope**: Workflow mode resolution, feature snapshots, assisted planning and dispatch, adopted
  agent instructions and probe tooling, pointer delivery, checkpoint continuation, integration, and
  exact owned-resource cleanup.
- **Date**: 2026-08-27
- **Status**: superseded by AD-015

### AD-024

- **Decision**: Merge the workflow-side assisted-parallelization remediation with the affected live
  QA scenario truthfully left `untested`; defer live Orca QA until the upstream `orca terminal send
  --text` transport support is corrected. The pointer-only workaround and all technical fake-Orca
  evidence remain required, and no live run is claimed by this waiver.
- **Reason**: The human authorized commit and merge without publishing while explicitly choosing to
  wait for the Orca team to fix the host transport. Holding the workflow-side fail-closed and
  pointer-only delivery improvements would delay usable intermediate parallelization without making
  live QA possible in this repository.
- **Trade-off**: Autonomous readiness accepts technical/fake-host evidence for this merge, while
  the changed user journey remains visibly untested and must be walked after upstream support lands.
- **Scope**: This feature merge only: assisted default dispatch, adopted probe, pointer delivery,
  direct capability/resource proof, same-handle reconciliation, and cleanup.
- **Date**: 2026-08-28
- **Status**: active

### AD-025

- **Decision**: One `Review-Signal` trailer per delivered pull request, carried on its merge commit,
  aggregating the feature through `slices=<n> verified=<m>` counts. Not one trailer per slice.
- **Reason**: No per-slice commit can carry the verdict. The per-slice lifecycle commits each task
  before the fresh Verifier runs (`references/sub-agents.md:50-57`), and integration may be a
  fast-forward with no commit of its own, so a slice has no commit that exists after its verdict is
  known. A merge commit always exists and is the unit principle 9 names. `slices`/`verified` sum
  across deliveries to the same slice-level fraction a per-slice trailer would give.
- **Trade-off**: A pull request squashed or merged outside the documented command loses its signal.
  The reader counts a missing signal as unproven rather than as reviewed, which is the honest
  reading, but it makes the metric sensitive to how a human merges.
- **Scope**: The trailer grammar, `check_commit.py` validation, and `tools/review-metrics.py`.
- **Date**: 2026-09-03
- **Status**: active

### AD-026

- **Decision**: `check_commit.py` validates the `Review-Signal` trailer only when present; it never
  requires one. A malformed trailer is exit 1, an absent trailer is exit 0.
- **Reason**: Every task commit inside a feature runs through the same validator, and only the
  delivery commit carries a verdict. Requiring the trailer would reject every ordinary commit; not
  validating it at all would let a mistyped signal poison the metric silently.
- **Trade-off**: Nothing forces a delivery to carry the trailer, so the emitting step stays an
  instruction rather than a gate. `review-metrics.py` reporting unsigned deliveries is what catches
  omission, after the fact.
- **Scope**: `check_commit.py` only.
- **Date**: 2026-09-03
- **Status**: active

### AD-027

- **Decision**: Round 2's Finding 1 is resolved as documentation, not code. `review-metrics.py` keeps
  counting every first-parent commit as a delivery, including commits that reached `main` before the
  pull-request process existed. The operator narrows the range; the tool adds no heuristic for
  whether a commit "went through a pull request".
- **Reason**: Those commits did reach `main` and were not reviewed, so reporting them as unsigned is
  the true reading, and the bias runs pessimistic - it understates review coverage rather than
  flattering it, which is the opposite of the failure this feature exists to prevent. Any rule that
  guessed which historical commits count would be exactly the cleverness the reviewer would flag
  next, and it would decide from the tool what is properly the operator's question.
- **Trade-off**: Run over this repository's whole history today, 6 of 60 first-parent commits predate
  the process and dilute the fraction by roughly a tenth. That noise decays as history grows, and a
  reader who wants the post-adoption number passes a range. A reader who does not pass one, and does
  not read the help text, will read a number lower than the truth.
- **Scope**: `tools/review-metrics.py` delivery enumeration only. Findings 2 and 3 of the same round
  are accepted as defects and remediated in code.
- **Date**: 2026-09-03
- **Status**: active

### AD-028

- **Decision**: Each workflow phase (Specify, Design, Tasks, Implement, Verify) is its own skill
  (`wspecify`, `wdesign`, `wtasks`, `wimplement`, `wverify`) whose `SKILL.md` carries the phase
  procedure under 200 lines, with templates under `references/`. `workflow-spec-driven` remains
  the router (sizing, phase-to-skill map, `.specs` layout, resume) and keeps `scripts/`. Claude agent
  templates preload their phase skill through frontmatter `skills:`; implementer, explorer, and
  deep-reviewer carry `disallowedTools: Skill`.
- **Reason**: Preload injects only `SKILL.md`, so a phase skill that merely pointed at a reference
  would scope nothing. A role that preloads one phase and cannot invoke others reads exactly its
  own procedure, which is what makes a cheap qualifier, a forked `/w<phase>` entry point, and
  per-role model choice possible.
- **Trade-off**: Six skills instead of one directory; the router name stays because about ninety
  references and the adopted gate path cite it. Cursor and Codex keep prose load lines until their
  preload support is verified.
- **Scope**: `.agents/skills/w*`, `workflow-spec-driven/SKILL.md`, `templates/agents/claude/*`,
  `scripts/adopt.py` core catalog.
- **Date**: 2026-09-03
- **Status**: active
