# Changelog

All notable changes to this project are documented here.

## [Unreleased]

## [0.9.1] - 2026-09-04

### Changed

- Planner routing now recognizes `direct correction`, `UI-only correction`, `feature`, and
  `cross-feature change` as intent signals. Behavior-preserving, bounded UI substitutions and
  reference-driven refactors use one targeted integration validation; named behavior, data,
  security, dependency, shared-token, build, architecture, and unresolved-choice evidence keeps
  the applicable feature workflow. `issue` remains neutral.

### Fixed

- `adopt.py apply --layers full --skip-agents` no longer runs packet synchronization, so a 0.8.0
  adopted consumer without designer tables can install the seven phase skills before completing
  the documented configuration and sync steps. Explicit packet sync still validates its config.

## [0.9.0] - 2026-09-04

### Added

- Phase skills `wspecify`, `wdesign`, `wtasks`, `wimplement`, `wverify`: each phase procedure is one
  skill an agent preloads alone; `workflow-spec-driven` is now the router (sizing, phase map,
  `.specs` layout, resume) and keeps the validators. Claude agent packets preload their phase
  skill through `skills:` and narrow roles carry `disallowedTools: Skill`; `--sync-agents` rejects a
  packet that preloads a missing or hollow skill.
- `/w` entry points: `/wspecify`, `/wdesign`, `/wtasks`, `/wimplement`, `/wverify` fork the phase
  into a fresh agent of its role and return only its summary; `/wreview` wraps `deep-review`;
  `/wqa [plan] <flow>` runs one QA phase over journeys tagged with the flow (`**Tags:**` line).
- Specify writes an `## Impact` section from two explorer traces with one no-regression acceptance
  criterion per affected feature, writes `uiux.md` for screen-bearing features, and offers a gap
  hunt at plan approval sized by scope; `validate_spec.py` requires `## Impact` for Large and
  Complex specs; `wverify` reruns the impacted QA scenarios.
- `designer` matrix role for Claude, Codex, and Cursor (AD-029): preloads `wdesign`, owns mockups
  under `docs/design/` and `uiux-review.md`; `wdesign` dispatches it before internal design.
- `Review-Signal` trailer on each delivery's merge commit (AD-025, AD-026) and
  `tools/review-metrics.py` reporting the reviewed fraction from git history.
- `tools/gate_cache.py` runs a gate once per tree and caches the passing result by tree hash.

### Changed

- `autonomous` merges by default once readiness is proven; a human go-ahead on ready work carries
  the same authorization, and the opt-out is stated up front (`stop when the PR is ready`).
- The QA history gate freezes evidence, reports, charters, and bugs only; scenario files are living
  status records and reset to `untested` when behaviour changes.
- `VERIFICATION-EVIDENCE.md` names the gate remediation loop and its cost; the raw knowledge note
  `2026-09-03-e2e-gate-remediation-cost.md` records the observation behind it.
- Router and reference prose trimmed after a prompt audit; the retired `context-limits.md` reference
  is removed.
- Live Orca transport stays `blocked-verify`; Cursor headless dispatch uses full Cursor model ids
  (`BUG-20260903-cursor-route-bracket-effort-rejected`).
- `docs/workflow/roadmap.md` records the modular workflow programme (Linear intake, qualifier,
  global config, mockup fidelity, telemetry intake, deterministic installer).
### Changed

- Workflow resolution derives its slice count from the validated `## Vertical Slice Closure`
  contract in `tasks.md` instead of a manually supplied number. A feature without `tasks.md`
  resolves to one slice, `--slices` is now an optional exact assertion on initial resolution and
  refresh only, and normal resume still returns the frozen snapshot without reading current tasks.
- Local `main` is reconciled onto the published 0.8.0 base. The local assisted-Orca executor and
  Bun test-runner variants are superseded by the released hybrid slice execution and Bun tooling;
  merge-alone slice derivation is scheduled for a re-port onto `workflow-spec-driven`.

### Removed

- Removed the optional ai-memory integration, including its repository scripts, guide,
  feature-specific test, and active QA promise. Session continuation is now a host responsibility.
- my-workflow keeps versioned repository artifacts and explicit prompts as the durable semantic
  context; adoption never removes external operator state.

### Migration

- Upgrading an adopted project from 0.8.0, in order:
  1. `adopt.py apply . --layers <installed layers> --skip-agents` installs the seven `w*` skills, the
     router, and the `.claude/skills/` links. Apply never removes files: delete nothing by hand.
  2. Templates are installed only when missing, so an adopted project keeps its 0.8.0
     `templates/agents/`. Copy the 0.9.0 `templates/agents/` over it (Claude packets gain `skills:`
     and `disallowedTools:`; every provider gains `designer`), then re-apply any product-specific
     lines you had added to a template.
  3. Add `[models.<provider>.designer]` tables for claude, codex, and cursor to the local
     `.my-workflow.toml`, copying from `.my-workflow.toml.example`. Sync fails naming a missing
     table.
  4. Run `workflow_config.py --root . --sync-agents` and confirm the three `designer` packets and
     the `skills:` lines in `.claude/agents/`.
  5. `--skip-agents` leaves `AGENTS.md` untouched; merge the 0.9.0 managed-block changes by hand:
     the remote-delivery bullet (merge by default, opt-out up front) and the designer in the roles
     line.
  6. Specs sized Large or Complex now need an `## Impact` section; add one to any in-flight spec
     before its next `validate_spec.py` run.
- Phase skills must not set `disable-model-invocation: true`; it blocks `skills:` preload.
- Cursor headless dispatch takes full model ids (`gpt-5.6-luna-high`); the `[effort=]` form the Orca
  route builds is rejected (`BUG-20260903-cursor-route-bracket-effort-rejected`).

- Operators who previously enabled ai-memory must follow the exact lifecycle commands in the
  [v0.5.0 tagged guide](https://github.com/antoniofulg/my-workflow/blob/v0.5.0/docs/workflow/ai-memory.md).
  This release does not execute or invent cleanup commands, and adoption never removes external
  operator state.

## [0.8.0] - 2026-08-31

### Added

- Bun 1.4 is the supported runtime, with modular `workflow-spec-driven` layers for incremental adoption.
- Assisted slice execution is the default: independent slices can run concurrently in isolated worktrees, while a single ready slice integrates serially in the checkout.
- Configurable project-scoped and machine-scoped test locks coordinate concurrent test runs.
- Legacy consumers can use `adopt.py resolve` with an exact, reviewable list of files to take over.

### Changed

- Remediation now reports real progress through the convergence ledger and preserves bounded stall decisions.

### Fixed

- First-use lock creation is serialized safely under concurrent adoption.
- Adoption resolution rejects target-controlled code and unsafe `.claude` parent symlinks at the trust boundary.
- Live Orca transport remains `blocked-verify` because the upstream `orca terminal send --text` limitation is not verified in this release.

## [0.7.0] - 2026-08-29

### Added

- PR #70's QA evidence and PR #73's hybrid slice execution establish the release's assisted-by-default workflow contract.
- Assisted slice execution is the default: independent slices can run concurrently in isolated worktrees, while a single ready slice integrates serially in the checkout.
- `workflow-spec-driven` replaces the legacy TLC path, with bounded slice context, independent proof, adaptive machine health, and exclusive-resource leases.

### Changed

- Tasks within each slice remain sequential; the coordinator owns dependency release, parking, continuation, integration, and cleanup. Adoption installs the pointer-only assisted probe with exactly-once mutations and read-only failure reconciliation.

### Fixed

- Safe cleanup and bounded ownership/effect checks prevent cross-slice residue and duplicate mutations. Live Orca remains `blocked-verify` because host terminal transport validation was not performed.

## [0.6.0] - 2026-08-25

### Added

- An opt-in parallel slice executor with `disabled`, `safe`, and `full` modes, deterministic worktree/worker follow-ups, checkpoint rebase/integration, and resource preflight.

### Changed

- Slice execution now preserves TLC task order while coordinating provider-neutral worker lifecycle, checkpoint evidence, and serial fallback for unproven capabilities.

### Fixed

- Lifecycle cleanup, recovery, and blocker convergence fail closed on uncorrelated ownership or external receipts; the real Orca/Codex two-lane journey remains `BLOCKED-VERIFY` and is not reported as a completed pilot.

## [0.5.0] - 2026-08-25

### Added

- Bounded parallel Deep Review with a default concurrency of 3, configurable from 1 through 6, frozen source inputs, resumable runs, bounded retries, provider-block state, deterministic reporting, and cumulative content-safe metrics.
- A configurable remediation stall bound of 3 consecutive stalls by default, with `0` selecting unbounded remediation.
- A direct-correction workflow for exact human-defined changes, centralized local provider runtime configuration, and model/effort routing across Claude, Codex, and Cursor.
- A refreshed adoption guide, autonomous scoped branch push, one pull request, and merge after readiness, and cleanup of merged feature worktrees.

### Changed

- Adoption now generates ignored provider runtime packets from the centralized local configuration while tracked templates remain the source of truth.
- Deep Review replaces the legacy `--workers` option with bounded `--concurrency` selection and preserves manifest-order status when refilling reviewer slots.

### Fixed

- Provider fallback and block state now survive interrupted or resumed review runs without refilling work after a provider block.
- Remediation edge cases now preserve deterministic progress and stall decisions across reordered or equal-size failing-test sets.

## [0.4.0] - 2026-08-24

### Added

- Opt-in ai-memory handoff across Claude Code, Codex, and Cursor with loopback-only, single-use continuity; adoption does not install it.
- Explicit reviewer isolation for internal Verifier and Deep Reviewer packets, with subagent capture dropping documented only as storage/noise control.
- Enable, reversible disable, re-enable, and separately destructive purge procedures for the operator-managed ai-memory lifecycle.

### Changed

- Codex handoff wrapper now finalizes only interactive launch modes and preserves the original child argv and exit status.

### Fixed

- Noninteractive and informational Codex commands no longer finalize an unrelated open session.
- QA runtime walks cover handoff delivery, single-use/no replay, the Codex wrapper/fallback/noninteractive fix, and the adoption canary. Lifecycle controls are documented and command-checked/dry-run only; reviewer isolation remains technical validation unless a later release QA session covers its documentation contract.

## [0.3.6] - 2026-08-23

### Added

- Optional Graft and OpenDesign integrations with repository-approved handoffs, source precedence, and safe writer boundaries.
- Versioned feature workflow state with safe migration of legacy ignore rules.
- Trackable Deep Review learnings and immutable QA charters with acceptance-criteria-mapped test cases.

### Changed

- Remote actions now require explicit authorization separate from local autonomous readiness.
- TLC validation honors the explicit `Verdict`; Deep Review uses the effective base and freezes source inputs before acceptance.
- Knowledge checks reject duplicate decision identities, record author dates, and run outside the repository bundle's full gate.

### Fixed

- Walkthrough comment publishing is idempotent, using PATCH for an existing comment and POST for a missing one.
- The full test gate now runs only canonical tests under `tools` via Vitest's scoped directory, so copied QA evidence cannot be discovered.

## [0.3.5] - 2026-08-22

### Added

- Authorized installation and onboarding for pinned external security skills.
- Scoped browser gate tags for feature-specific checks.
- Consumer-owned ad-index preservation during adoption.
- Source-only pack guide and versioned feature-spec guidance for worktree and gate consumers.
- TLC validator compatibility with generated feature layouts.
- Ponytail `full` activation across the complete workflow cycle.
- Deep Review manifests now handle symlink entries safely.
- Adoption supports opt-in preservation of existing `AGENTS.md` and `CLAUDE.md` files.

## [0.3.4] - 2026-08-22

### Changed

- Onboarding now relies on the bundled TLC, Ponytail, and Deep Review skills instead of external installers.
- Documentation now states that the consuming project must have a Git HEAD before resolving workflow configuration.

### Fixed

- Adoption installs the bundled Deep Review skill and excludes Python cache files.
- Adoption rejects HOME-relative Claude TLC paths before writing and directs consumers to the project-local vendored TLC path.
- Configuration follow-ups strengthen schema validation and make cadence authority explicit.

## [0.3.3] - 2026-08-22

### Added

- Configurable deep-review cadence (`slice`, `feature`, or `grouped.N`), provider profiles and overrides, frozen workflow snapshots, and a default config example.
- Optional pinned Graft 0.10.1 context with plain-inspection fallback.
- Serialized reviewers and retries, plus observational content-safe token metrics with no usage cap.

### Fixed

- Adoption now installs the Graft ignores needed to keep generated artifacts out of Git.

## [0.3.2] - 2026-08-21

### Added

- Dedicated `deep-reviewer` agents for Claude, Codex, and Cursor.
- Dedicated deep-review pins: Claude Sonnet/high; Codex Luna/high; Cursor Luna/high.
- Agent matrix pins: Claude Opus/high planner, Opus/medium implementer and verifier, Sonnet/medium explorer; Codex Sol/high planner, Luna/high implementer, Sol/medium verifier, Luna/medium explorer; Cursor Grok/high planner, Luna/high implementer, Grok/medium verifier, Luna/medium explorer.
- Native-first deep-review dispatch with role-free Workflow fallback.
- Automatic remediation of blocking findings from round 2 without opening round 3.

### Changed

- Luna implementers use high effort across the agent matrix.
