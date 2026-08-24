# Parallel Slice Dispatch Surface Contract

## Config

| Key | Type | Default | Effect |
| --- | --- | --- | --- |
| `parallelization.mode` | enum: `disabled`, `safe`, `full` | `disabled` | Selects serial execution or a conservative/full inter-slice dispatch plan. |

Invalid values make workflow resolution fail before replacing an existing snapshot. Existing feature
snapshots retain their frozen mode until an explicit refresh.

## Commands

```text
python3 .agents/skills/workflow-config/scripts/parallel_plan.py \
  --root . --feature <feature-slug> [--verified-slice <slice-id>]...
```

The command writes deterministic JSON to stdout and mutates no file, branch, worktree, or process.
Exit is non-zero only when the feature snapshot or tasks file cannot be read. Unsafe or inconclusive
graphs return a successful serial-fallback plan with reasons.

## Exports

None.
## Removals

None.
