# Gates

**Read when:** choosing which gate to run.

**Why this exists:** Keep task feedback scoped and cheap; run the full product gate once before the
pull request. Never weaken a test to go green.

The consuming project owns commands. `make check`, when present, is the full gate; a documented
selector is the scoped gate. Name the actual commands.

## Which gate, when

| Moment | Gate | Why |
| --- | --- | --- |
| During a task | The task's own test command | Fast feedback while implementing |
| Closing a task | The consuming project's scoped gate | Coverage for what this diff touched |
| Closing a task with a browser surface | The consuming project's browser scoped gate, filtered by `@feature:<slug>` | Runs only that feature's browser scenarios |
| Closing a feature, before the pull request | The consuming project's full gate | The product gate, once |
| Heavy subsystem touched | The consuming project's extended gate, if it has one | Adds registered heavy checks |

**No gate reads document shape instead of product code.** Knowledge checkers and dependency
inventories stay separate: one opens a knowledge harvest; the other inventories current dependencies.

## Credential-free declarative agent-tool configuration

Eligible only when the entire diff is declarative agent configuration containing agent or
tool-server names, public URLs, and non-secret options. Executable commands, hooks, plugins,
dependencies, credential-bearing headers or environment variables, OAuth clients or scopes,
permissions, product or runtime code, CI or deploy changes, and external mutations take the
applicable normal path.

The active agent edits directly and makes one atomic commit. Create no `spec.md`, `tasks.md`, or
`workflow.json`; dispatch no agent; run no Verifier, deep-review, QA, or completion gate.

Before committing:

1. Parse every changed file with its native parser.
2. Compare every name, public URL, key, and value exactly with the request and client schema.
3. Scan keys and values for credential material.
4. Query each installed client for the relevant server, returning only `name`, `url`, `enabled`, and
   `auth_status`; remain read-only.
5. Run `git diff --check` and the project's commit-message validator.

OAuth is a separate local action requiring explicit human authorization. Credentials, OAuth clients
or scopes, permissions, authentication behaviour, and sensitive product data require full Verifier.

## The narrow-claim rule

**Intermediate tasks close on the scoped gate.** Claim *"task implemented, affected lanes green,
full gate deferred to feature close"*. Run the full gate once after the last mutation, before the
pull request.

Escalate a task to the full gate when its diff touches something the selector cannot scope:
migrations and schema, runtime orchestration, dependency or build tooling, architecture boundary
configuration, or shared design tokens. Unknown or empty selection also escalates — that is the
selector working, not failing.

## Cached evidence

A known result for the exact claimed tree need not run again. When a cache exists:

- A matching **passing record is fresh evidence.** Cite gate, fingerprint, and log path.
- A **missing or stale record means the gate runs now.** Records key on tree content, so any edit
  invalidates one; a commit alone does not.
- **Scope still binds.** A scoped record never supports a "feature complete" claim.
- A **failing record** starts diagnosis from its log.

This cache is optional tooling for the consuming project.

## What the scenario tracker does not do

Selectors and fingerprint caches reduce gate time. `docs/qa/scenarios/` scopes manual verification
to invalidated user-visible promises; it does not scope automated tests.

## Concurrency

Concurrent full gates across checkouts can stall both.

If a runtime is bound, find its owner and stop that checkout. Never set `reuseExistingServer: true`:
one checkout could silently test a sibling's application.

## Never

- Never weaken, skip or delete a test to make a gate pass.
- Never claim a gate passed without its output.
- Never treat a warning as acceptable in a gate that reports zero-tolerance.
