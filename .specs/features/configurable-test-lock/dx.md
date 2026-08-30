# Configurable Test Lock Surface Contract

## CLI

### `python3 tools/resource_lock.py run`

```text
python3 tools/resource_lock.py run \
  --resource <name> \
  [--scope project|machine] \
  [--timeout-seconds <number>] \
  -- <command> [argument ...]
```

| Input | Type | Default | Effect |
| --- | --- | --- | --- |
| `--resource` | lowercase identifier, 1-64 characters | required | Names the exclusive resource lane. |
| `--scope` | `project` or `machine` | `project` | Chooses linked-worktree or cross-project coordination. |
| `--timeout-seconds` | non-negative number | `2700` | Bounds acquisition wait; `0` is a single immediate attempt. |
| command after `--` | argv | required | Executes directly after acquisition without a shell. |

### Results

- The wrapper inherits the command's stdin, stdout, and stderr.
- A completed command returns its exact exit status.
- Invalid CLI input returns `2` before command execution.
- Acquisition timeout returns `75` before command execution.
- An unavailable executable returns `127` after acquisition.
- Waiting diagnostics are JSON lines on stderr: one `wait` line is emitted immediately, then at most
  one additional line per 60-second interval. Each line is at most 2,048 characters and contains the
  event, scope, resource, holder PID, opaque project identifier, and holder start time. They contain
  no command arguments or environment values.

## Adoption

`scripts/adopt.py apply <target> --layers parallel` installs `tools/resource_lock.py` and
records it in `.my-workflow/adoption.json`. `core` alone omits the file. Installation changes no
consumer-owned command; maintainers opt in by wrapping chosen heavy gates.

## Removals

None.
