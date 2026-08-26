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

## Coordinator-assisted Orca

When automatic Orca is `unsupported`, an operator may explicitly authorize the main agent to
coordinate direct Orca worktrees. This path is supervised through the existing Orca CLI and is not a
new executor verb or compatibility result. It must read the frozen
`roles.implementer.provider/model/effort` and always launch an explicit command, never trust an
unobservable default. The verified provider forms are `codex --model <model> -c
'model_reasoning_effort="<effort>"'`, `claude --model <model> --effort <effort>`, and `cursor agent
--model '<model>[effort=<effort>]'`; merge Cursor effort into an existing parameter block. Use the
selected executable's `--help`/availability check, wait for `tui-idle`, then read the terminal to
confirm effective model and effort before sending the task packet. An inexpressible, unavailable, or
unobservable route stops setup without editing `tasks.md`. Always use the two-step
`worktree create` plus `terminal create --command`, preserving startup policy. A fallback shell is
closed only after `terminal list` or `terminal show` proves it is unused. Deliver the packet and
later follow-ups with `terminal send` to that sole verified handle.

The coordinator starts at most one worker per ready slice. Tasks inside each slice stay sequential.
At the first unmet dependency, the worker leaves a clean checkpoint and writes this worktree
comment:

```text
slice=<id>; state=parked; completed_through=<task>; next=<task>;
blocked_on=<slice:task>; head=<sha>
```

The worker ends its turn without polling. After the producer's required completion and verification,
the coordinator reconciles the comment with `tasks.md` and Git, synchronizes the exact producer
commit into the dependent worktree, reruns the affected gate, and follows up the same terminal. A
stale handle is reacquired from that worktree; a dirty, ambiguous, conflicting, or failed lane
returns to serial recovery without automatic conflict resolution. Cleanup removes only clean,
integrated, coordinator-owned worktrees after deterministic integration and proves zero owned
residue. Before cleanup, revalidate the exact create receipt (full worktree id, instance, path,
branch, worker handle, and HEAD), Orca show/list identity, Git worktree/gitdir/path/no-symlink/HEAD/
clean/no-operation-in-progress state, and slice-head ancestry of integration HEAD. Stop the exact
worker, recheck, remove only by full id, and prove Orca/Git/path/terminal absence. Any mismatch or
missing proof retains the path and serializes; cleanup never uses a name or branch selector.
Assisted execution never records a compatibility PASS, and the automatic adapter remains serial
until its lifecycle canary passes.

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
