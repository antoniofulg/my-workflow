# Gates

**Read when:** choosing which gate to run.

**Why this exists:** Running the full product gate after every atomic task is the largest avoidable
cost in the loop. Atomic tasks are cheap only if their gate is cheap: scoped while building, full
once before the pull request. Never weaken a test to go green.

The consuming project owns the commands. This pack does not ship a Makefile. If the project has
`make check`, that is the full gate; if it has a scoped selector, that is the scoped gate. Name the
actual commands the project documents.

## Which gate, when

| Moment | Gate | Why |
| --- | --- | --- |
| During a task | The task's own test command | Fast feedback while implementing |
| Closing a task | The consuming project's scoped gate | Coverage for what this diff touched |
| Closing a task with a browser surface | The consuming project's browser scoped gate, filtered by `@feature:<slug>` | Runs only that feature's browser scenarios |
| Closing a feature, before the pull request | The consuming project's full gate | The product gate, once |
| Heavy subsystem touched | The consuming project's extended gate, if it has one | Adds registered heavy checks |

**No gate reads the shape of a document.** Shape enforcement on Markdown is not a substitute for
reading product code.

A knowledge checker and a dependency inventory, if they exist, stay out of the full gate: the first
is the opening step of a knowledge harvest, the second answers a question that changes with
dependencies, not with features.

## The narrow-claim rule

**Intermediate tasks in a multi-task feature close on the scoped gate.** The honest claim is *"task
implemented, affected lanes green, full gate deferred to feature close"* — and that is a complete,
truthful claim, not a shortcut.

The full gate runs **once**, after the last mutation, before the pull request. Running every lane
once per task, for a ten-task feature, buys nothing that running them once at the end does not.

Escalate a task to the full gate when its diff touches something the selector cannot scope:
migrations and schema, runtime orchestration, dependency or build tooling, architecture boundary
configuration, or shared design tokens. Unknown or empty selection also escalates — that is the
selector working, not failing.

## Cached evidence

A gate whose result is already known for the exact tree being claimed should not run again. Re-running
a current gate proves nothing new and saturates a machine that is running several checkouts.

The rule:

- A **passing record whose fingerprint matches the current tree is fresh evidence.** Cite it — gate
  name, fingerprint, log path — instead of re-running.
- A **missing or stale record means the gate runs now.** Records key on tree content, so any edit
  invalidates one; a commit alone does not.
- **Scope still binds.** A scoped record never supports a "feature complete" claim.
- On a **failing record**, open its log and fix from there. Never re-litigate it from memory.

Produce a record: `python3 tools/gate_cache.py run --gate <scoped|full> -- <gate command>`.

## What the scenario tracker does not do

`docs/qa/scenarios/` will not reduce gate time, and expecting it to will disappoint. Two different
mechanisms:

- **Gate time** is cut by selector-scoped lanes plus a fingerprint cache, if the project has them.
- **The scenario tracker** decides which *user-visible promises* a diff invalidated, so the persona
  pass walks those and not all of them. It scopes manual verification, not automated tests.

## Concurrency

Several checkouts may share one machine. Two full gates at once collapse it and both stall.

If a gate refuses because a runtime is already bound, find the owner and stop the checkout that holds
it. Never set `reuseExistingServer: true` to get past it — that option lets a gate in one checkout
silently test a sibling's application.

## Never

- Never weaken, skip or delete a test to make a gate pass.
- Never claim a gate passed without its output.
- Never treat a warning as acceptable in a gate that reports zero-tolerance.
