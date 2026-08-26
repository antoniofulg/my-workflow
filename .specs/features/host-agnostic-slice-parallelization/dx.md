# Host-Agnostic Slice Parallelization Surface Contract

## Commands

```text
python3 .agents/skills/autonomous/scripts/parallel_execute.py preflight \
  --root . --feature <feature-slug> --adapter auto|orca|maestri [--canary]

python3 .agents/skills/autonomous/scripts/parallel_execute.py start|resume \
  --root . --feature <feature-slug> --adapter auto|orca|maestri
```

`preflight` emits one JSON object and never changes feature code. Without `--canary`, it is read-only.
`--canary` is an explicit operator action: it may create one disposable Orca checkout and worker,
must clean both, and records PASS only after proving zero residue. Maestri rejects `--canary` while
its CLI lacks the structured lifecycle and cleanup contract.

## Result

```json
{
  "adapter": "orca",
  "status": "compatible",
  "runtime": {"app_version": "1.4.189", "capabilities": ["orchestration.contract.v1"]},
  "proof": {"source": "canary", "cached": false, "cleanup": "clean"},
  "missing_capabilities": [],
  "reason": null
}
```

`status` is `compatible`, `candidate`, or `unsupported`. `compatible` is the only result that can
enable safe/full execution. `candidate` requires explicit `--canary`. `unsupported` names one stable
reason and produces no scheduler effect.

The frozen `.specs/features/<feature>/workflow.json` consumed by the executor is schema version `2`.
Version `1` snapshots are obsolete and are rejected; the planner output's own `version` field is a
separate plan schema.

## Adapter selection

- `auto` inside Maestri evaluates only Maestri.
- `auto` outside Maestri evaluates Orca when its executable exists.
- `auto` never crosses from one detected host into another.
- `start` and `resume` in `disabled` mode return before adapter selection. Explicit `preflight` still
  selects and probes the requested host so an operator can discover an Orca update.
- `start` and `resume` accept only an identity-matching cached PASS; they never run a canary implicitly.

## Local compatibility state

PASS receipts live below Git common state, outside `.specs/`. Identity includes repository, adapter,
installed app version, declared capabilities, and executable identity. Any mismatch invalidates the
receipt. Receipts contain no worker transcript, environment value, token, or credential.

## Failures

| Failure | Result |
| --- | --- |
| Known-bad Orca version | `unsupported`; zero mutations. |
| New Orca version without PASS receipt | `candidate`; `start`/`resume` serialize. |
| Canary lifecycle or cleanup failure | `unsupported`; failed stage and retained IDs, no PASS receipt. |
| Current Maestri machine contract | `unsupported`; missing structured lifecycle and floor deletion. |
| Missing explicit adapter | `unsupported`; serial fallback. |

## Exports

The executor recognizes `auto`, `orca`, and `maestri`. Adapter modules expose a read-only
compatibility probe; only a compatible adapter exposes execution effects.

## Removals

Capability-name-only Orca enablement is removed. `orchestration.contract.v1` remains necessary but
is no longer sufficient.
