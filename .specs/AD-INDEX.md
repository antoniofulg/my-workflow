# Project decision index

One line per `AD-NNN`. The append-only body lives in `.specs/STATE.md`.

Body: `rg -A 20 '^### AD-NNN' .specs/STATE.md`. Resume: `rg -A 20 '^## Handoff' .specs/STATE.md`.
When recording an `AD-NNN`, run `python3 tools/ad-index.py` in the same commit.

| ID | Status | Decision |
| --- | --- | --- |
| `AD-001` | active | Agent always-on is a thin `AGENTS.md` (contract + pointers). |
| `AD-002` | active | QA planning and QA execution are separate provider-neutral skills dispatched in fresh sessions by the existing Verifier. |
| `AD-003` | active | `.specs/features/` is ignored local state. |
| `AD-004` | active | Workflow routing is consumer-configurable in `.my-workflow.toml`. |
| `AD-005` | active | Keep the optional, checkout-local Graft `0.10.1` integration as the deep-review context aid. |
| `AD-006` | active | Keep the workflow stack- and tool-agnostic while allowing optional capability integrations. |
| `AD-008` | superseded by AD-011 | Adopt upstream ai-memory `1.31.0` only as an opt-in, transient handoff transport between Claude Code, Codex, and Cursor. |
| `AD-009` | superseded by AD-010 | `.my-workflow.toml` is the single editable source for bundled Claude, Codex, and Cursor agent models and efforts. |
| `AD-010` | active | Track `.my-workflow.toml.example` and provider packet templates, while keeping `.my-workflow.toml` and generated `.claude`, `.codex`, and `… |
| `AD-011` | active | Cross-provider session continuation is owned by the host. |
