# Changelog

All notable changes to this project are documented here.

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
