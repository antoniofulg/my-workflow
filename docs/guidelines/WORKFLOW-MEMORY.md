# Workflow Memory

**Read when:** starting any task in a multi-task feature.

Atomic tasks buy short, reliable review rounds. They cost a ramp-up: every task is a fresh agent run
that re-reads the spec, re-explores the codebase, and rebuilds its model of the system from zero
before the first edit — then throws that reasoning away at the task boundary.

Workflow memory is how the reasoning survives the boundary. It is what makes small tasks affordable.

## The two files

Both live at `.specs/features/<feature>/memory/`.

| File | Scope | Owner |
| --- | --- | --- |
| `MEMORY.md` | Durable, cross-task | Every task promotes into it |
| `task_NN.md` | Local, operational | The task that is running |

## Timing

**Read both before the first code edit. Update before any completion claim or commit.**

That order is the whole mechanism. Memory read after implementation has already failed to prevent the
rediscovery it exists to prevent.

## What goes in shared memory

A constraint, decision or risk earns promotion only when all three are true:

1. Another task needs it to avoid a mistake or a rediscovery.
2. It is durable across runs, not just this execution.
3. It is **not** already obvious from the spec, the task file, or the repository.

If any answer is no, it stays in task memory.

Belongs in `MEMORY.md`:

- A constraint discovered during implementation that affects later tasks — "the repository serializes
  writes per region; batch inserts must chunk by region"
- A cross-cutting decision made while coding, not at design time — "chose a discriminated union over
  a status enum because the public contract rejects bare strings"
- An open risk later tasks must account for — "the onboarding migration assumes the accounts backfill
  has run; it has not in this checkout"

Belongs in `task_NN.md`:

- Files touched during this task
- Debugging steps taken to resolve a task-specific failure
- This task's objective and acceptance-criteria snapshot
- A workaround scoped to this task only

## Hard rules

- **Never invent history**, decisions, or status that did not happen.
- **Never copy** code blocks, stack traces, or spec text into memory. Reference them by path.
- **Never duplicate** what the repository, the diff, the task file or the spec already says.
- **Never read another task's memory file** unless `MEMORY.md` points at it.
- When memory conflicts with the repository, **the repository wins** — then correct the memory file.

## Compaction

When a file grows noisy, compact it in place. Shared memory first, then task memory — the shared file
sets the context the task file must not duplicate.

- **Keep:** current state, durable decisions, reusable learnings, open risks, handoff notes.
- **Cut:** repetition, stale notes, command transcripts, anything derivable from the repo or spec.
- **Rewrite** what remains as short factual bullets. Never a chronological log.

## Lifecycle

Memory is scratch. It lives and dies with the feature branch and is not a durable artifact — see
`docs/guidelines/ARTIFACT-LIFECYCLE.md`. Anything that must outlive the feature is promoted to a real
home before the pull request: a project decision to `.specs/STATE.md` as `AD-NNN`, a durable lesson to
the lessons layer, a product promise to `docs/qa/scenarios/`.
