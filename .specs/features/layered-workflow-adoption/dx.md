# Layered Workflow Adoption Surface Contract

## CLI

### `python3 scripts/adopt.py plan TARGET --layers LIST [--json] [--skip-agents]`

- **Success:** exit `0`; deterministic requested/resolved layers and per-path actions.
- **Failures:** exit `2` for invalid arguments/layers/target/manifest; concise message on stderr.
- **Idempotency:** read-only; repeated calls return the same result for unchanged source and target.

### `python3 scripts/adopt.py apply TARGET --layers LIST [--json] [--skip-agents]`

- **Success:** exit `0`; cumulative layers installed, provider packets synchronized against the fully staged target, selected files and packets published deterministically, and the manifest atomically published last as the authority marker.
- **Conflict:** exit `1`; all conflicts reported; zero target writes.
- **Failures:** exit `2` for invalid invocation, unsafe path, unsupported/malformed manifest, or synchronization precondition; zero writes.
- **Idempotency:** repeated apply with unchanged inputs is byte-stable.

### Publication order

Apply stages the complete adoption input set in a private directory and runs provider
synchronization there. Only after staging and synchronization succeed does it publish, in
deterministic buckets, selected managed and missing-only files, instruction blocks and separators,
ignore edits, local config initialization/preservation, legacy cleanup, managed Claude skill links,
and generated Claude/Codex/Cursor packets. It then atomically publishes
`.my-workflow/adoption.json` as the final live-target mutation. A staging, synchronization,
cleanup, or link failure publishes nothing and leaves the previous target and manifest unchanged.

### `python3 scripts/adopt.py status TARGET [--json]`

- **Clean:** exit `0`; installed layers plus clean/retained managed entries.
- **Drift:** exit `1`; missing/modified/conflicting entries.
- **Failures:** exit `2`; missing or invalid manifest/target. A missing manifest is invalid for
  `status`, while a fresh `apply` without one is valid.
- **Idempotency:** read-only; never synchronizes agents or invokes Orca.

## JSON

Every JSON mode emits one object on stdout:

```json
{
  "command": "plan",
  "target": "/absolute/path",
  "requested_layers": ["parallel"],
  "resolved_layers": ["core", "parallel"],
  "status": "ready",
  "actions": [{"path": "tools/orca_assisted_probe.py", "action": "add", "layer": "parallel"}],
  "conflicts": []
}
```

Arrays use deterministic layer/path ordering. Diagnostics never mix into stdout.

## Manifest

`.my-workflow/adoption.json` is workflow-owned schema version `1`:

```json
{
  "schema": 1,
  "workflow_version": "0.7.0",
  "layers": ["core", "parallel"],
  "files": {
    "tools/orca_assisted_probe.py": {
      "layer": "parallel",
      "ownership": "managed",
      "source_sha256": "<64 lowercase hex>",
      "installed_sha256": "<64 lowercase hex>"
    }
  },
  "blocks": {
    "AGENTS.md:core": {"sha256": "<64 lowercase hex>"}
  }
}
```

No timestamps. Paths are normalized repository-relative POSIX paths. Unknown keys, layers, ownership values, hashes, duplicate JSON keys, non-normalized paths, and escapes are failures.

## Managed instruction blocks

Selected blocks use exact markers:

```text
<!-- my-workflow:core:start -->
...
<!-- my-workflow:core:end -->
```

The adopter appends an absent block after existing consumer prose and replaces only a valid existing block. Duplicate, nested, incomplete, or edited-marker structure is a conflict. `CLAUDE.md` receives a managed core block containing `@AGENTS.md`; other consumer content remains unchanged.

## Removals

- Remove `python3 scripts/adopt.py TARGET`.
- Remove whole-file `AGENTS.md` replacement and whole-file `CLAUDE.md` recreation.
- Remove the monolithic `COPY_PATHS`/`COPY_MISSING_PATHS` public adoption model.
