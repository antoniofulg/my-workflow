# Project decision index

One line per `AD-NNN`. The append-only body lives in `.specs/STATE.md`.

Body: `rg -A 20 '^### AD-NNN' .specs/STATE.md`. Resume: `rg -A 20 '^## Handoff' .specs/STATE.md`.
When recording an `AD-NNN`, run `python3 tools/ad-index.py` in the same commit.

| ID | Status | Decision |
| --- | --- | --- |
| `AD-001` | active | Agent always-on is a thin `AGENTS.md` (contract + pointers). |
| `AD-002` | active | QA planning and QA execution are separate provider-neutral skills dispatched in fresh sessions by the existing Verifier. |
| `AD-003` | superseded by AD-007 | `.specs/features/` is ignored local state. |
| `AD-004` | active | Workflow routing is consumer-configurable in `.my-workflow.toml`. |
| `AD-005` | active | Keep the optional, checkout-local Graft `0.10.1` integration as the deep-review context aid. |
| `AD-006` | active | Keep the workflow stack- and tool-agnostic while allowing optional capability integrations. |
| `AD-007` | active | `.specs/features/` is versioned, durable workflow state. |
| `AD-008` | superseded by AD-019 | Adopt upstream ai-memory `1.31.0` only as an opt-in, transient handoff transport between Claude Code, Codex, and Cursor. |
| `AD-009` | superseded by AD-010 | `.my-workflow.toml` is the single editable source for bundled Claude, Codex, and Cursor agent models and efforts. |
| `AD-010` | active | Track `.my-workflow.toml.example` and provider packet templates, while keeping `.my-workflow.toml` and generated `.claude`, `.codex`, and `… |
| `AD-011` | superseded by AD-015 | Parallelization is an opt-in inter-slice orchestration layer above unchanged TLC; `disabled` is the default, `safe` consumes independent or… |
| `AD-012` | active | Parallel execution uses a provider-neutral deterministic coordinator whose adapters own external effects. |
| `AD-013` | active | The provider-neutral coordinator derives and validates a deterministic sibling Git worktree destination, creates that checkout with fixed a… |
| `AD-014` | superseded by AD-016 | Technical Verifier remediation is bounded per blocker fingerprint, defined by the requirement, root cause, and concrete failure path. |
| `AD-015` | active | Replace the vendored TLC phase-batch delegation with a workflow-owned, CC-BY-4.0-attributed spec-driven skill that dispatches vertical slic… |
| `AD-016` | active | A halted blocker fingerprint may resume only after explicit human authorization creates a new audit generation under that same fingerprint. |
| `AD-017` | active | Heavy test commands use an explicit named kernel lock separate from lane-wide resource-provider leases. |
| `AD-018` | active | The gate fingerprint is `sha256` over the gate label, the exact command argv, and the Git tree object written from a temporary index seeded… |
| `AD-019` | active | Cross-provider session continuation is owned by the host. |
| `AD-020` | active | Vertical slice count is derived from validated task outcomes that remain worth merging if all later slices are cancelled. |
| `AD-021` | superseded by AD-015 | When automatic host orchestration is incompatible, explicit human authorization may enable coordinator-assisted inter-slice execution throu… |
| `AD-022` | active | The assisted coordinator writes each complete slice packet to a coordinator-owned file outside every slice worktree and sends only a short… |
| `AD-023` | superseded by AD-015 | `assisted` is the default inter-slice execution mode whenever the frozen task DAG exposes independent safe slices. |
| `AD-024` | active | Merge the workflow-side assisted-parallelization remediation with the affected live QA scenario truthfully left `untested`; defer live Orca… |
| `AD-025` | active | One `Review-Signal` trailer per delivered pull request, carried on its merge commit, aggregating the feature through `slices=<n> verified=<… |
| `AD-026` | active | `check_commit.py` validates the `Review-Signal` trailer only when present; it never requires one. |
| `AD-027` | active | Round 2's Finding 1 is resolved as documentation, not code. |
