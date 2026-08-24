# Agent Model Routing Surface Contract

## Config

`.my-workflow.toml` uses schema version 2. It contains exactly one `model` and `effort` pair for each
provider and role:

```toml
version = 2

[models.codex.planner]
model = "gpt-5.6-sol"
effort = "high"
```

Providers: `claude`, `codex`, `cursor`.

Roles: `planner`, `implementer`, `verifier`, `explorer`, `deep_reviewer`.

Model identifiers are provider-native strings. Effort accepts the workflow vocabulary supported by
the selected provider adapter; the provider runtime remains authoritative for model compatibility.

## CLI

```bash
python3 .agents/skills/workflow-config/scripts/workflow_config.py \
  --root . --sync-agents
```

- **Success:** exits `0` and prints JSON arrays named `changed` and `unchanged` with project-relative packet paths.
- **Idempotent success:** exits `0`, prints an empty `changed` array, and changes no bytes.
- **Invalid config:** exits `2`, writes one actionable `workflow-config:` error to stderr, and changes no packets.
- **Invalid packet:** exits `2`, names the packet and invalid metadata condition, and changes no packets.
- **Argument conflict:** exits `2` when `--sync-agents` is combined with feature-resolution arguments.

Ordinary resolve and resume commands remain unchanged. New and refreshed snapshots expose `model`
and `effort` beside `provider` and `agent_file` for every delegated role.

## Removals

- Remove `.my-workflow.toml.example`; `.my-workflow.toml` becomes the shipped configuration.
- Remove schema version 1 acceptance.
- Remove documentation that model pins are manually owned by provider packets.
- Remove silent resume when synchronized packet metadata differs from frozen snapshot metadata.
