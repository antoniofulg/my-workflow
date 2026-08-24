# Optional ai-memory handoff

`ai-memory` is an opt-in transport for one next-session baton between Claude Code, Codex, and
Cursor. It does not replace repository workflow state.

Git, `.specs/`, `tasks.md`, architecture documentation, and `knowledge/` remain authoritative. The
ai-memory runtime and its SQLite/FTS data stay outside the checkout, under the operator's home data
directory. Do not commit `.ai-memory.toml`, hook files, handoffs, or runtime databases here.

## Enable

Enablement is operator-only: it changes agent hooks, the local ai-memory service, and the shell that
launches Codex. It does not add a repository toggle or runtime dependency. Complete the steps below,
source the helper in a new shell, and restart Claude Code, Codex, and Cursor after hook installation.

### Pinned workstation setup

Use upstream release `1.31.0`, not `main` or `latest`. On macOS/Linux, a tagged release binary or
the upstream `mise` GitHub backend is supported. Pin the exact release outside this repository:

```bash
mise use -g github:akitaonrails/ai-memory@1.31.0
ai-memory --version
```

Verify the published SHA-256 sidecar when downloading a release archive manually. The official
installation cookbook covers native archives, Docker, and source builds:
[`docs/install.md`](https://github.com/akitaonrails/ai-memory/blob/v1.31.0/docs/install.md).

Initialize a user-local server. These paths deliberately do not live in a project checkout:

```bash
mkdir -p "$HOME/.config/ai-memory" "$HOME/.local/share/ai-memory"
ai-memory \
  --data-dir "$HOME/.local/share/ai-memory" \
  --config "$HOME/.config/ai-memory/config.toml" init
```

Run the server in a separate terminal:

```bash
ai-memory \
  --data-dir "$HOME/.local/share/ai-memory" \
  --config "$HOME/.config/ai-memory/config.toml" \
  serve --transport http --bind 127.0.0.1:49374
```

`127.0.0.1` keeps the service local. Do not expose this server on a LAN or configure a remote
`AI_MEMORY_SERVER_URL` for this workflow. If a non-loopback deployment is later required, it needs
TLS, bearer authentication, and a separate security decision.

## Minimal configuration

Edit the user config created by `init` and keep the following boundaries. Omit all LLM and embedding
provider settings and do not configure API keys:

```toml
[routing]
mid_session = "sticky"

[briefing]
inject_on_session_start = false

[auto_improve]
on_session_end = false
require_approval = true

[auto_improve.scheduler]
enabled = false
```

This intentionally leaves consolidation, embeddings, auto-improvement scheduling, and recurring
briefing off. Do not run `ai-memory bootstrap`, `ai-memory embed`, `ai-memory auto-improve`, or
`ai-memory run` for this integration. `ai-memory run` is the managed-workstream mode and is outside
the contract.

There is intentionally no `.my-workflow.toml` toggle for ai-memory: that file owns workflow cadence,
role routing, and bundled agent model/effort settings, while ai-memory is an operator-local optional capability. `.ai-memory.toml` only
declares workspace/project scope and capture exclusions; its presence does not enable or disable
ai-memory.

## Install lifecycle hooks

Install only lifecycle hooks for the three supported agents. `--project-strategy repo-root` makes
subdirectories and linked worktrees resolve to the main Git repository. The server's `sticky`
mid-session routing keeps a temporary `cd` from moving one session into another project.

```bash
for agent in claude-code codex cursor; do
  ai-memory install-hooks \
    --agent "$agent" \
    --project-strategy repo-root \
    --apply
done
```

Do not run `install-mcp`, `install-instructions`, or `install-skills`. No MCP tools, routing skill,
managed skill, or instruction block is part of this handoff-only setup. The hook installer is
idempotent and changes only ai-memory-owned entries in the agent configuration.

After installing hooks, restart the three agent processes and open a new shell after sourcing
`scripts/ai-memory.zsh` so Codex uses the wrapper.

For recognized file-tool events, add a nearest, operator-owned `.ai-memory.toml` marker with
explicit exclusions, for example:

```toml
workspace = "local"
project_strategy = "repo-root"
drop_subagent_captures = "true"

[capture]
ignore_paths = [".env", ".env.*", "private/**", "~/.ssh/**", "~/personal-notes/**"]
```

Keep this marker outside the repository when possible. Exclusions are lexical and bounded. They do
not filter secrets mentioned in free-form prompts, shell output, or patches; this is not a complete
DLP boundary. Review the upstream [capture policy](https://github.com/akitaonrails/ai-memory/blob/v1.31.0/docs/marker-file.md#capture-exclusions)
before adding paths.

`drop_subagent_captures = "true"` is an optional storage and noise control: it prevents subagent
captures for this project from being stored. It does not isolate reviewer roles or protect a
top-level reviewer from consuming an Implementer handoff. Apply the reviewer packet rule in
[`REVIEW-ROUNDS.md`](../guidelines/REVIEW-ROUNDS.md).

## Codex wrapper

This repository ships a sourceable helper at [`scripts/ai-memory.zsh`](../../scripts/ai-memory.zsh).
Source it in the shell that launches Codex:

```zsh
source /path/to/my-workflow/scripts/ai-memory.zsh
codex
```

The wrapper forwards the original argument vector literally, calls `ai-memory finalize-session`
once after an interactive Codex exit, and returns Codex's original exit status. It skips automatic
finalization for known noninteractive, informational, and admin commands (`--version`, `--help`,
`exec`, `mcp`, `completion`, `login`, and `logout`) because those invocations do not create the
interactive session that the wrapper is meant to close. It does not edit `~/.zshrc`; the operator
may source it from their own shell startup file later if desired.

Codex has no reliable true SessionEnd hook. If the wrapper shell dies before cleanup, return to the
project directory and run the manual fallback:

```zsh
source /path/to/my-workflow/scripts/ai-memory.zsh
handoff
```

With multiple Codex sessions in one project, target the exact session instead:

```bash
ai-memory finalize-session --session-id <uuid>
```

## Daily handoff

1. Work normally in Claude Code, Codex, or Cursor.
2. End Codex normally; the sourced wrapper finalizes it. For an interrupted Codex process, run
   `handoff` when back in the project. Claude Code and Cursor use their installed lifecycle hooks.
3. Start another supported agent in the same project or a compatible subdirectory/worktree.
4. The startup hook consumes at most one pending handoff. With no pending handoff, it adds no
   ai-memory startup payload.

The handoff is a concise baton, not a transcript, project briefing, wiki recall, or second task
ledger. Once consumed, it is not injected again. Continue from the repository files and Git state.

## Disable without deleting data

First inspect the upstream dry-run. It changes nothing without `--apply`:

```bash
ai-memory uninstall --only hooks
```

Disable lifecycle wiring without deleting handoffs or runtime data:

```bash
ai-memory uninstall --only hooks --apply --yes
```

Stop the service separately with the manager that launched it. Generic examples:

```bash
systemctl --user stop ai-memory.service       # systemd user service
docker stop ai-memory                          # Docker deployment
```

On the current macOS LaunchAgent setup, inspect and stop the labeled service with:

```bash
launchctl print "gui/$(id -u)/com.akitaonrails.ai-memory"
launchctl bootout "gui/$(id -u)/com.akitaonrails.ai-memory"
```

Remove or comment the `source /path/to/my-workflow/scripts/ai-memory.zsh` line from the operator's
shell startup file, then restart the agent processes and open a new shell. This workflow never edits
that file automatically. The disable command removes only ai-memory-owned hooks; it does not delete
`~/.local/share/ai-memory`, `~/.config/ai-memory`, handoffs, or runtime databases.

## Re-enable

Start the same local service again, reinstall the three hooks with the enable commands above, source
the helper in a new shell, and restart the agent processes. Existing runtime data remains available;
re-enable does not require a purge or repository change.

## Upgrade

Pin upgrades explicitly. After upgrading the binary, refresh each lifecycle hook and re-check the
configuration:

```bash
mise use -g github:akitaonrails/ai-memory@<new-version>
for agent in claude-code codex cursor; do
  ai-memory install-hooks --agent "$agent" --project-strategy repo-root --apply
done
```

## Destructive data purge

Only when intentionally discarding all ai-memory runtime data, first stop the service and then run
the upstream destructive path:

```bash
ai-memory uninstall --apply --purge-data --yes
```

This removes wiring and permanently wipes `wiki/`, `db/`, and `raw/` under the configured data
directory. It is separate from disabling hooks and cannot be undone from this workflow. This
repository does not remove operator-owned files.

## Upstream references

- [ai-memory 1.31.0 release](https://github.com/akitaonrails/ai-memory/releases/tag/v1.31.0)
- [Installation cookbook](https://github.com/akitaonrails/ai-memory/blob/v1.31.0/docs/install.md)
- [Marker and capture policy](https://github.com/akitaonrails/ai-memory/blob/v1.31.0/docs/marker-file.md)
- [Handoff usage](https://github.com/akitaonrails/ai-memory/blob/v1.31.0/docs/usage.md#cross-agent-handoff)
- [Managed workstreams, intentionally excluded](https://github.com/akitaonrails/ai-memory/blob/v1.31.0/docs/managed-workstreams.md)
