# Legacy Adoption Resolution Surface Contract

## CLI

### `python3 scripts/adopt.py resolve TARGET --layers LIST --replace PATH [--replace PATH ...] [--json] [--skip-agents]`

- **Success:** exit `0`; every current replaceable file conflict was named exactly, selected workflow files and generated packets publish through the existing transaction, and `.my-workflow/adoption.json` publishes last.
- **Unresolved conflict:** exit `1`; output lists every remaining conflict; zero target writes.
- **Invalid or unsafe request:** exit `2`; non-Git, dirty, manifest-backed, extra, absolute, escaping, or managed-block replacement authorization; zero target writes.
- **Idempotency:** the command is a one-time bootstrap. After success, `resolve` rejects the manifest-backed target and normal `apply`/`status` own future updates.

`--replace` is repeatable and has no `--replace-all` equivalent. Resolve accepts only current
catalog-managed file conflicts. It never treats an altered `AGENTS.md` or `CLAUDE.md` managed block
as a replaceable file.

## JSON

Resolve extends the existing deterministic result with one field:

```json
{
  "command": "resolve",
  "target": "/absolute/path",
  "requested_layers": ["parallel"],
  "resolved_layers": ["core", "parallel"],
  "status": "ready",
  "actions": [{"path": "tools/resource_lock.py", "action": "replace", "layer": "parallel"}],
  "conflicts": [],
  "replacements": ["tools/resource_lock.py"]
}
```

Arrays and actions use deterministic ordering. Diagnostics never mix into JSON stdout.

## Git Boundary

Resolve executes Git with direct arguments. The target must:

- be inside a Git work tree;
- have a resolvable `HEAD`;
- return no entries from porcelain status, including untracked files;
- have no `.my-workflow/adoption.json` path.

The clean committed tree is the recovery baseline. Resolve does not create a second backup format.

## Existing Commands

`plan`, `apply`, and `status` retain their current arguments, output, exit codes, and conflict
semantics. `apply` never starts resolving unowned divergent files implicitly.

## Removals

None.
