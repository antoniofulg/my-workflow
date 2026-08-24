---
name: workflow-config
description: Workflow configuration synchronizes central agent models and efforts, then resolves deep-review cadence and delegated-role providers before feature dispatch. Use when editing model settings, syncing packets, planning or resuming a feature, selecting native or mixed providers, or freezing a feature workflow. Don't use for project gates, QA policy, or planning depth.
---

# Workflow Configuration

Synchronize native packet metadata explicitly, then resolve the feature workflow once and let the
orchestrator dispatch the frozen route.

## Synchronize agent metadata

`.my-workflow.toml` is the single editable source for every Claude, Codex, and Cursor model and
effort across planner, implementer, verifier, explorer, and deep reviewer. Native packet fields are
generated output and packet instructions remain provider-owned.

Run:

```bash
python3 .agents/skills/workflow-config/scripts/workflow_config.py \
  --root . --sync-agents
```

The command validates the complete matrix and every packet before writing, reports `changed` and
`unchanged` paths, and is idempotent. Adoption runs it after installing missing config and packets.

## First resolution

Run the bundled `mutating` resolver from the consuming project root. It writes the feature-local
`workflow.json` snapshot atomically:

```bash
python3 .agents/skills/workflow-config/scripts/workflow_config.py \
  --root . --feature <feature-slug> --slices <implementation-slice-count> \
  --native-provider <claude|codex|cursor> [--profile <name>] \
  [--override <role>=<provider>]...
```

Treat the JSON output and `.specs/features/<feature-slug>/workflow.json` as the same resolved state.
The resolver owns config parsing, validation, balanced groups, role precedence, agent-file lookup,
and atomic persistence. Keep those rules in the resolver instead of restating them here.

Done when: the snapshot exists, contains the effective cadence, role routes, and frozen delegated
model/effort, and the capable orchestrator has accepted every selected provider.

## Resume

Read the existing feature snapshot before dispatch. Use its `deep_review`, `roles`, and `git_head`
values even when `.my-workflow.toml` has changed. Current packet metadata must match each frozen
delegated model and effort; otherwise synchronize and explicitly refresh. Do not silently re-resolve
an active feature.

Done when: resumed dispatch uses the snapshot's effective route and records no new resolution.

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

- Parse or validation failure: fix `.my-workflow.toml` or the CLI argument and rerun.
- Provider failure: make the named provider and role agent available; use no fallback.
- Snapshot write failure: restore write access to the feature state directory and rerun; atomic
  replacement preserves the prior valid snapshot.

Done when: the resolver exits 0 and the snapshot contains the requested effective route.
