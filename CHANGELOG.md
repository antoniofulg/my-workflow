# Changelog

All notable changes to this project are documented here.

## [0.3.2] - 2026-08-21

### Added

- Dedicated `deep-reviewer` agents for Claude, Codex, and Cursor.
- Dedicated deep-review pins: Claude Sonnet/high; Codex Luna/high; Cursor Luna/high.
- Agent matrix pins: Claude Opus/high planner, Opus/medium implementer and verifier, Sonnet/medium explorer; Codex Sol/high planner, Luna/high implementer, Sol/medium verifier, Luna/medium explorer; Cursor Grok/high planner, Luna/high implementer, Grok/medium verifier, Luna/medium explorer.
- Native-first deep-review dispatch with role-free Workflow fallback.
- Automatic remediation of blocking findings from round 2 without opening round 3.

### Changed

- Luna implementers use high effort across the agent matrix.
