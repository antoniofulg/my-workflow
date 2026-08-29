# Hybrid Slice Execution Surface Contract

**Status:** Approved

## Config

`.my-workflow.toml` uses schema version `3`:

```toml
version = 3

[parallelization]
mode = "assisted"
max_workers = "auto"
# Optional repository-relative executable that grants existing workflow resource leases.
# resource_provider = "tools/workflow_resources"
```

| Key | Type | Default | Effect |
| --- | --- | --- | --- |
| `parallelization.mode` | `"assisted" \| "disabled"` | `"assisted"` | Enables hybrid dispatch or explicit serial execution. |
| `parallelization.max_workers` | `"auto" \| integer >= 1` | `"auto"` | Caps active implementer writers. `auto` starts at 2 and admits one healthy lane at a time to 4. |
| `parallelization.resource_provider` | repository-relative executable path or absent | absent | Uses the existing JSON lease protocol for declared resources and heavy gates. |

Failures are exact and effect-free:

| Input | Error |
| --- | --- |
| Config version other than `3` | `workflow-config: version must be integer 3; refresh the project configuration` |
| Mode other than `assisted` or `disabled` | `workflow-config: parallelization.mode must be 'assisted' or 'disabled'` |
| `max_workers` other than `"auto"` or integer >= 1 | `workflow-config: parallelization.max_workers must be 'auto' or an integer of at least 1` |
| Absolute, escaping, symlinked, missing, or non-executable provider | Existing repository-containment error with no dispatch effect |

## Frozen Feature Snapshot

`workflow.json` uses version `3` and freezes policy, not a momentary health result:

```json
{
  "version": 3,
  "parallelization": {
    "mode": "assisted",
    "max_workers": "auto",
    "automatic_baseline": 2,
    "automatic_ceiling": 4,
    "resource_provider": null
  }
}
```

The snapshot also retains the existing branch/head identity, delegated role routes, model/effort
packets, review cadence, and remediation policy. Version-1 and version-2 active snapshots fail with:

```text
workflow-config: workflow snapshot version is stale; rerun resolution with --refresh
```

No dispatch effect occurs before refresh. No snapshot migration or compatibility reader exists.

## Packet Budget CLI

```text
python3 .agents/skills/workflow-spec-driven/scripts/slice_packet.py \
  build --input <slice-packet.json> --output <packet.md> --telemetry <telemetry.json>
```

Success writes the packet and JSON telemetry to explicit checkout-local paths. Failure exits non-zero,
writes only redacted telemetry, and performs no provider dispatch. The JSON contract is:

```json
{
  "schema_version": 1,
  "role_bytes": 0,
  "slice_bytes": 0,
  "slice_budget_bytes": 10240,
  "role_budget_bytes": 3072,
  "within_budget": true,
  "components": {}
}
```

Telemetry contains counts and logical component names only. It never contains packet bodies, secrets,
environment values, terminal text, or absolute home-directory prefixes.

## Assisted Probe CLI

The shipped stdlib module exposes JSON-on-stdout subcommands and imports without dispatch:

```text
python3 tools/orca_assisted_probe.py dispatch --request <request.json> --state <state.json>
python3 tools/orca_assisted_probe.py inspect --state <state.json>
python3 tools/orca_assisted_probe.py cleanup --state <state.json>
```

- `dispatch` validates identity and paths, persists the full packet, performs each planned mutation
  once, and sends only the pointer.
- `inspect` performs bounded read-only settle/reconciliation and never mutates.
- `cleanup` removes only effects proven by the persisted ownership record.
- Every subcommand returns one normalized, redacted JSON object on stdout and uses non-zero exit for a
  failed proof.
- Dispatch occurs only under `if __name__ == "__main__":`.

## Review Convergence Resume CLI

The existing convergence recorder gains one explicit halt-resume operation:

```text
python3 .agents/skills/workflow-spec-driven/scripts/review_convergence.py \
  --root . \
  --feature <feature-slug> \
  --resume-fingerprint <64-hex-fingerprint> \
  --authorization-ref <repository-relative-decisions-anchor>
```

- Resume accepts only an existing halted fingerprint and a non-empty repository-relative
  authorization reference.
- Success appends the next generation, preserves cumulative failures and prior generations, and
  prints the current normalized entry as JSON.
- Unknown/non-halted fingerprints, missing authorization, inconsistent history, and same-requirement
  replacement fingerprints exit non-zero without changing the file.
- A closing PASS through the existing result recorder also requires a repository-relative fresh
  Verifier evidence reference; a green gate alone never closes a resumed generation.
- No reset, delete, rename, or replacement-fingerprint command exists.

## Machine Health

Health is internal, machine-only JSON. It has no public provider or config key. The scheduler consumes:

```json
{
  "schema_version": 1,
  "observed_at_monotonic": 0.0,
  "cpu": "healthy",
  "memory": "healthy",
  "disk": "healthy",
  "heavy_gates_active": 0,
  "admit_one": true
}
```

Only normalized enums, counts, and monotonic age leave the helper. Raw process lists, command lines,
environment, usernames, and absolute paths never do. Missing, stale, malformed, or unhealthy evidence
means `admit_one: false` and cannot reduce already running healthy work.

## Removals

- `.agents/skills/tlc-spec-driven`
- Every `tlc-spec-driven` instruction, adoption entry, template reference, lock entry, and canonical
  test expectation
- Modes `safe` and `full`
- Config and feature snapshot schema version `2`
- Phase-batch worker packets and feature-only Technical Verifier wording

No aliases, dual fields, fallback readers, or migration command ship.
