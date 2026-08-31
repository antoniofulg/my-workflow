# Legacy Adoption Resolution Threat Model

## Scope

This model covers `scripts/adopt.py resolve`, which publishes workflow files into a local Git
worktree and creates `.my-workflow/adoption.json`. It covers only the local Git and filesystem
design. There is no network service, authentication flow, or deployment surface in this feature.

## Assets

- Consumer-owned files and instruction prose in the target worktree.
- Workflow source bytes and generated agent packets from this checkout.
- Git `HEAD` as the recoverable clean baseline.
- The staged adoption transaction and manifest ownership records.
- Files outside the target that could be reached through symlinks or shell interpretation.

## Actors and trust boundaries

| Actor | Boundary / capability |
| --- | --- |
| Maintainer | Chooses target, layers, and reviewed `--replace` paths; expects explicit ownership transfer. |
| Consumer project | Supplies existing target files, Git state, symlinks, and instruction prose. Its bytes are not workflow-owned unless authorized. |
| Local filesystem | Holds source checkout, target worktree, temporary staging files, and possible external referents. |
| Git process | Reports worktree identity, `HEAD`, and porcelain status through direct argument vectors. |

The target filesystem is the publication boundary. Source files are read from this checkout, while
target paths are untrusted filesystem inputs. A target symlink, parent symlink, or shell metacharacter
must not redirect writes or execute another command.

## Controls

- Resolve requires the target to be the root of a Git worktree with resolvable `HEAD` and standard
  porcelain status empty, while ignored files remain outside the dirty check.
- Replacement values must be normalized relative paths and members of the current replaceable file
  conflict set. Duplicate, escaping, absolute, separator-trick, and managed-block values are
  rejected before publication.
- `_safe_path` follows every destination component without following symlinks and rejects
  non-directory parents and non-file leaves.
- Synchronization executes only the source checkout's workflow-config script; target resolver trees
  and module/package shadows remain data and are never imported.
- `_preflight_tree` validates every path component of `.claude/skills`, including the `.claude`
  parent, before any managed skill link is created; existing managed pointers are then checked for
  their expected relative targets.
- Git and helper calls use argument vectors, never shell interpolation.
- Publication snapshots target bytes, entry kinds, and regular-file mode bits. Failure restores the
  snapshot, including executable bits, before reporting failure.
- Workflow entries publish before `.my-workflow/adoption.json`; the manifest is the ownership
  authority and is written last.
- `--skip-agents` leaves `AGENTS.md` and `CLAUDE.md` outside the transaction.

## Residuals

- A maintainer can still authorize an obsolete file deliberately; explicit path review is the
  control for that decision, not automatic content merging.
- A failure after a filesystem operation but before rollback completes may leave the target
  unrecovered; the command reports rollback failure rather than claiming success.
- Git cleanliness protects the committed baseline, but external copies and backups remain the
  maintainer's responsibility outside this local one-shot command.
