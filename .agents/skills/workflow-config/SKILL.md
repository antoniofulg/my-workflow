---
name: workflow-config
description: Workflow configuration resolves deep-review cadence and delegated-role providers before feature dispatch. Use when planning or resuming a feature, selecting native or mixed providers, or freezing a feature workflow. Don't use for project gates, QA policy, planning depth, or provider model selection.
---

# Workflow Configuration

Resolve the feature workflow once, then let the orchestrator dispatch the frozen route.

## First resolution

Run the bundled `mutating` resolver from the consuming project root. It writes the feature-local
`workflow.json` snapshot atomically:

```bash
python3 .agents/skills/workflow-config/scripts/workflow_config.py \
  --root . --feature <feature-slug> --slices <implementation-slice-count> \
  --native-provider <claude|codex|cursor> [--profile <name>] \
  [--override <role>=<provider>]...
```

The JSON output is `.specs/features/<feature-slug>/workflow.json` plus the resolved-now
`remediation`. The snapshot is the frozen routing state; never write the JSON output back to it.
The resolver owns config parsing, validation, balanced groups, role precedence, agent-file lookup,
and atomic persistence. Keep those rules in the resolver instead of restating them here.

Done when: the snapshot exists, contains the effective cadence and role routes, and the capable
orchestrator has accepted every selected provider.

## Remediation stall bound

`.my-workflow.toml` table `[remediation]`, single key `stall_attempts`: how many consecutive
identical failure signatures end post-cap remediation. Integer of at least `0`, default `3`, where
`0` means unbounded: never halt for a stall. The resolver reports the effective value under
`remediation` in its JSON output and deliberately keeps it out of `workflow.json`, so a changed
threshold takes effect on the next attempt instead of the next feature.

Done when: the resolved output reports the intended `stall_attempts`.

## Resume

Read the existing feature snapshot before dispatch. Use its `deep_review`, `roles`, and `git_head`
values even when `.my-workflow.toml` has changed. Do not silently re-resolve an active feature.

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
