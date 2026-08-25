# Parallel Slice Executor Surface Contract

## Config

```toml
[parallelization]
mode = "disabled"
# Optional repository-relative executable used only by resource-bearing lanes.
resource_provider = "tools/workflow_resources"
```

`resource_provider` is absent by default. Workflow resolution freezes its normalized repository-
relative path in `workflow.json`; an absolute path, directory, unsafe symlink, or path outside the
repository is rejected. Without it, `Resources: none` may still execute concurrently and every
resource-bearing lane falls back to serial.

## Commands

```text
python3 .agents/skills/autonomous/scripts/parallel_execute.py start \
  --root . --feature <feature-slug> --adapter auto|orca

python3 .agents/skills/autonomous/scripts/parallel_execute.py resume \
  --root . --feature <feature-slug> --adapter auto|orca --wait-seconds <1..3600> \
  --technical-verifier-receipt <receipt.json>

python3 .agents/skills/autonomous/scripts/parallel_execute.py status \
  --root . --feature <feature-slug>
```

All commands emit one JSON object to stdout, including a `command` field identifying `start`,
`resume`, or `status`. Errors use stderr and a non-zero exit. `start` performs
only actions allowed by the current frozen plan. `resume` reconciles persisted receipts, consumes at
most the available correlated events, and may block inside the adapter without model polling.
Technical verification is an explicit receipt input correlated to feature/slice/task/worktree/current_head
with `verdict: passed` and distinct `author` and `implementer`; worker completion is never inferred as verification.
`status` is read-only.

Worker-start failures preserve bounded redacted Orca JSON fields such as `code`, failed stage,
Run/Task IDs, effects, and residual resources. A pending worker action carries those partial
effects and is retryable through `resume` with the exact Run/Task selectors; the result never hides
accepted external effects behind `actions: []`.

For a real pilot, `start` is followed by bounded public `status`/`resume` calls. Cleanup is allowed
only after `python3 tools/qa_parallel_pilot.py lifecycle-check` proves exactly the two expected
lanes have terminal worker, read-before-ack, and release receipts; timeout or incomplete lifecycle
retains the fixture for diagnosis.

Normal cleanup also requires a lifecycle authorization digest bound to the owner repository/common
directory, source worktree identity, frozen heads, exact lane worktree IDs, and lifecycle version.
`cleanup --abort-incomplete` is an explicit diagnostic path; it never claims cleaned success and
refuses removal while an accepted or recoverable worker effect may still be live.

`--adapter auto` selects a proven installed adapter; the first supported adapter is `orca`. If none
qualifies, the command returns a successful serial-fallback result and creates no worktree or worker.

## Worktree destination contract

The coordinator derives a deterministic sibling destination from the repository Git common
directory ancestry, feature, slice, and task. It resolves and validates that destination before the first
Git write. The provider-neutral worktree creator creates the checkout from the frozen source HEAD;
the Orca adapter receives the existing absolute worktree path and attaches its worker there. Orca's
worktree-create command is not used as a path allocator.

## Task metadata

Parallelizable task sections add one explicit field:

```text
**Resources:** none
```

or a comma-separated consumer vocabulary such as:

```text
**Resources:** runtime, port, database
```

Missing or ambiguous resource metadata makes the lane serial. `none` means the task needs only its
isolated checkout. Other values require a configured provider accepted by the adapter.

## Resource provider protocol

The consuming project supplies an executable argv, never a shell expression. The executor sends one
JSON request on stdin:

```json
{
  "operation": "acquire|release",
  "repository": "/absolute/repository",
  "feature": "feature-slug",
  "slice": "slice-id",
  "task": "T1",
  "worktree": "/absolute/worktree",
  "idempotency_key": "opaque-key",
  "resources": ["runtime", "port", "database"]
}
```

Acquire succeeds only with a correlated JSON receipt containing `lease_id`, the same resource names,
`prepared_worktree: true`, and an `environment` object. Slice A-B persist and log only redacted
environment markers; ephemeral delivery of environment values is deferred to T7's autonomous
integration contract. Release returns the same lease ID and `released: true`; a repeated release is
idempotent.

## State

Runtime receipts live below the current repository's Git common directory. They are local machine
state, survive coordinator restart, and are never committed under `.specs/features/`.

## Failures

| Failure | Result |
| --- | --- |
| Disabled mode or unsupported adapter | Successful serial fallback; no external effect. |
| Missing resource provider for declared resources | Successful serial fallback; no worker starts. |
| Malformed, foreign, duplicated, or secret-bearing receipt | Lane halted; serial recovery reason emitted. |
| Dirty worktree or Git conflict | Operation aborted; pre-operation HEAD retained; serial recovery emitted. |
| Event wait timeout | Successful unchanged state; no polling instruction emitted. |

## Exports

The Python coordinator exposes an adapter protocol used by the bundled Orca adapter and test doubles.
Checkpoint reconciliation and final verified-slice integration are internal seams: tests may inject
deterministic Git/gate adapters, while the public CLI persists exact checkpoint, cleanup, and
integration receipts and continues to emit the same command JSON contract.

## Removals

None.
