---
name: workflow-config
description: Workflow configuration synchronizes central agent models and efforts, then resolves deep-review cadence and delegated-role providers before feature dispatch. Use when editing model settings, syncing packets, planning or resuming a feature, selecting native or mixed providers, or freezing a feature workflow. Don't use for project gates, QA policy, or planning depth.
---

# Workflow Configuration

Synchronize native packet metadata explicitly, then resolve the feature workflow once and let the
orchestrator dispatch the frozen route.

## Synchronize agent metadata

`.my-workflow.toml` is the checkout-local single editable source for every Claude, Codex, and Cursor
model and effort across planner, implementer, verifier, explorer, and deep reviewer. The tracked
`.my-workflow.toml.example` initializes it, and tracked `templates/agents/` bodies are the source
for ignored generated runtime packets. Native packet fields are generated output; edit templates
for instruction changes.

Run:

```bash
python3 .agents/skills/workflow-config/scripts/workflow_config.py \
  --root . --sync-agents
```

The command validates the complete matrix and every template before writing, initializes a missing
local config from the example, reports `changed` and `unchanged` runtime paths, and is idempotent.
Adoption runs it after installing missing example/templates.

## Remediation stall bound

The optional `[remediation]` table has one key, `stall_attempts`: the number of consecutive
post-cap remediation attempts that fail to establish a new minimum of failing-test identifiers.
It must be an integer of at least `0`, defaults to `3`, and `0` means unbounded. The resolver
includes the effective value in its current JSON output but never writes it to `workflow.json`.
This lets an operator tune the bound between attempts without refreshing the frozen route.

## First resolution

Run the bundled `mutating` resolver from the consuming project root. When `tasks.md` exists, it
validates the vertical-slice closure contract and derives the count before writing the feature-local
`workflow.json` snapshot atomically:

```bash
python3 .agents/skills/workflow-config/scripts/workflow_config.py \
  --root . --feature <feature-slug> \
  --native-provider <claude|codex|cursor> [--profile <name>] \
  [--override <role>=<provider>]...
```

With no `tasks.md`, the resolver uses one slice. `--slices <expected-count>` remains an optional
assertion for initial resolution and refresh; it never owns the count. Normal resume returns the
frozen snapshot without reading current Tasks.

Treat the snapshot as the persisted route and cadence; the current JSON output additionally reports
the live remediation threshold. The resolver owns config parsing, validation, balanced groups, role
precedence, agent-file lookup, and atomic persistence. Keep those rules in the resolver instead of
restating them here.

Done when: the snapshot exists, contains effective parallelization, cadence, role routes, and frozen delegated
model/effort, the current output reports `remediation.stall_attempts`, and the capable orchestrator
has accepted every selected provider.

## Resume

Read the existing feature snapshot before dispatch. Use its `parallelization`, `deep_review`, `roles`, and `git_head`
values even when `.my-workflow.toml` has changed. Re-read the current `[remediation]` threshold on
every resume; it is deliberately live. Current packet metadata must match each frozen delegated
model and effort; otherwise synchronize and explicitly refresh. Do not silently re-resolve an active
feature.

Done when: resumed dispatch uses the snapshot's effective route and cadence, reports the current
remediation threshold, and records no new resolution.

## Refresh

Run the same command with `--refresh` only when the human explicitly requests a new resolution.
Review the resulting snapshot before dispatch because refresh may change review groups or providers.

Done when: the refreshed snapshot is valid and the orchestrator dispatches only its effective route.

## Provider availability

Check that the selected orchestrator can execute each provider named in `roles`. Halt with the
provider and role named when a route is unavailable. Keep provider agent definitions complete and
separate; use the `agent_file` selected by the resolver without merging definitions or silently
falling back to another provider.

Done when: every dispatched role has an available provider and its existing agent file.

## Failure recovery

Read the resolver's stderr and correct the named input before retrying:

- Parse or validation failure: fix the local config, example/template source, or CLI argument and rerun.
- Provider failure: make the named provider and role agent available; use no fallback.
- Snapshot write failure: restore write access to the feature state directory and rerun; atomic
  replacement preserves the prior valid snapshot.

Done when: the resolver exits 0 and the snapshot contains the requested effective route.
