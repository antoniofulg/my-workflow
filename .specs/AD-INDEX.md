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
| `AD-007` | active | Bound post-cap remediation by consecutive identical failure signatures, not by an open blocker. |
