# Agent Model Routing Decisions

## Human Decisions

| Decision | Source |
| --- | --- |
| Use `.my-workflow.toml` instead of manual model and effort edits in provider packet trees. | User request, 2026-08-24 |
| Retain generated native metadata because each runtime needs it to create configured agents. | User confirmation, 2026-08-24 |
| Run the feature unattended through `$autonomous`. | User request, 2026-08-24 |
| Keep `.my-workflow.toml` and generated runtime packets local and unversioned. | User decision, 2026-08-24 |

## Autonomous Decisions

### Explicit synchronization

- **Chosen**: Add `--sync-agents`; adoption invokes the same operation after installing assets.
- **Why**: Model changes remain visible and reviewable during development while adoption leaves a ready target.
- **Rejected**: Automatic sync on every resolve or resume because it creates hidden tracked-file writes.
- **Change cost now**: Low before implementation; high after CLI and adoption contracts ship.
- **User cost today**: One explicit command after changing model settings outside adoption.

### Strict version 2 hard cut (superseded)

- **Chosen**: Track `.my-workflow.toml`, remove `.my-workflow.toml.example`, and reject version 1.
- **Why**: The requested central source should be immediately editable and project policy forbids compatibility layers.
- **Rejected**: Optional model tables with native-file fallback because they preserve two sources of truth.
- **Change cost now**: Medium because resolver, adoption, docs, and fixtures change together.
- **User cost today**: Existing consumers must adopt or replace their version 1 config before resolving work.

This packaging choice is superseded by the human decision below; schema version 2 remains a hard cut.

### Local operator state

- **Chosen**: Track `.my-workflow.toml.example` and `templates/agents/`; ignore local `.my-workflow.toml` and generated runtime packet directories.
- **Why**: Provider access, limits, profiles, model choices, and efforts vary per operator and should not create repository diffs.
- **Rejected**: Tracking the active config and generated packets because every quota-driven switch becomes a project change.
- **Change cost now**: Medium; generation, adoption, tests, docs, and packaging change before merge.
- **User cost today**: A fresh checkout runs one sync/setup step before custom agents become available.

### Freeze only requested execution metadata

- **Chosen**: Snapshot and compare delegated `model` and `effort` values.
- **Why**: This extends the existing frozen route without making instruction-only packet edits block resume.
- **Rejected**: Full packet hashing because it expands the feature beyond model routing.
- **Change cost now**: Low; snapshot schema changes are already required.
- **User cost today**: A deliberate model change to an active feature requires explicit refresh.

### Provider-native identifiers

- **Chosen**: Store separate provider-native model strings for all five roles.
- **Why**: Claude, Codex, and Cursor model names and effort compatibility differ.
- **Rejected**: Cross-provider aliases because they require a model catalog and migration policy not requested.
- **Change cost now**: Low.
- **User cost today**: The central file contains fifteen explicit settings instead of a smaller lossy abstraction.

## Project Decision

`AD-010` supersedes `AD-009` for repository ownership while retaining frozen delegated settings.
