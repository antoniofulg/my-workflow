# Merge-Alone Slice Derivation Surface Contract

## CLI

### Workflow resolution

```bash
python3 .agents/skills/workflow-config/scripts/workflow_config.py \
  --root . \
  --feature <feature-slug> \
  --native-provider <claude|codex|cursor> \
  [--slices <expected-count>] \
  [--profile <name>] \
  [--override <role>=<provider>]... \
  [--refresh]
```

- **Initial resolution with `tasks.md`**: validates its vertical-slice closure contract and derives
  the count.
- **Initial resolution without `tasks.md`**: uses one slice.
- **`--slices`**: optional exact assertion during initial resolution and refresh; it never owns the
  count.
- **Resume**: returns the existing valid snapshot without reading current tasks or checking
  `--slices`.
- **Refresh**: validates current tasks and derives the count again before atomically replacing the
  snapshot.
- **Parallel consumers**: the planner accepts the resolver's snapshot and reports the validator's
  primary-task membership.

### Task validation contract output

```bash
python3 .agents/skills/workflow-spec-driven/scripts/validate_tasks.py \
  <tasks.md> --slice-contract-json
```

Success writes one JSON object to stdout:

```json
{
  "task_slices": {"T1": "A", "T2": "A"},
  "slice_ids": ["A"],
  "closures": {
    "A": {
      "outcome": "The complete migration runs on Bun and Vitest is absent.",
      "gate": "npm run test:all",
      "merge_alone": true,
      "why": "This is the requested deliverable."
    }
  }
}
```

Task IDs and slice IDs appear in document order. JSON output is deterministic.

## Task document

Every primary task heading `### T<number>:` contains exactly one field:

```markdown
**Slice:** A
```

Every used slice appears exactly once in:

```markdown
## Vertical Slice Closure

| Slice | Observable outcome | Independent gate | Merge if later slices are cancelled? | Why |
| --- | --- | --- | --- | --- |
| A | Complete user-valuable outcome | `exact gate command` | yes | Concrete delivery reason |
```

`yes` is the only accepted merge-alone value. Review remediation records do not create primary task
membership or new slices.

## Failures

| Condition | Result |
| --- | --- |
| Present `tasks.md` is invalid | Exit non-zero; name invalid task/slice; do not write snapshot |
| `--slices` differs from derived count during initial/refresh | Exit non-zero with expected and derived counts; do not replace snapshot |
| `--slices` is zero or negative | Exit non-zero; do not write snapshot |
| Existing snapshot is invalid | Preserve current validation failure; do not derive from tasks |

## Removals

Manual slice count is removed as a source of truth. No alias, fallback parser, or inferred
task-count heuristic remains.
