# Branch Naming

**Read when:** creating a branch or a worktree.

**Why this exists:** A branch named for the implementation (`add-users-table`) or for a checkout
slot hides what the user gets. Work on `main`, leftover merged branches, and two checkouts sharing
a runtime are how a gate silently verifies the wrong tree.

## Shape

```
<type>/<slug>
```

`<type>` is the Conventional Commits type the branch's work will mostly carry. `<slug>` is 2–5
kebab-case words naming the behaviour, not the implementation.

```
feat/account-onboarding
fix/duplicate-submission
docs/guidelines-rebuild
refactor/repository-boundaries
```

## Types

| Type | For |
| --- | --- |
| `feat` | New user-visible behaviour |
| `fix` | A defect in behaviour that already shipped |
| `refactor` | Structure changes, no behaviour change |
| `perf` | Behaviour unchanged, measurably faster |
| `docs` | Documentation and guidelines only |
| `test` | Test-only work — rare, since tests ship with their behaviour |
| `build` | Tooling, dependencies, CI |
| `chore` | Nothing. Do not use it — name the real type |

## Rules

1. **The slug names the behaviour.** `feat/account-onboarding`, not `feat/add-users-table`. A reader
   should know what the user gets, not what the diff touches.
2. **One branch, one feature.** The branch matches the `.specs/features/<slug>/` directory name when
   the feature has one. Same slug on both sides — no translation step.
3. **Never work on `main`.** Never push to it, never force-push anywhere, never merge without an
   explicit instruction.
4. **Worktree branches are named for their work, not their checkout.** The branch name says what is
   being built.
5. **No personal namespace.** New branches do not use `username/` prefixes.
6. **Delete after merge.** After a PR merges, confirm the merge and a clean tracked worktree, then
   remove every worktree the agent created for that feature or task. Inspect ignored residue before
   using force removal. Keep the primary, active, and unmerged worktrees untouched.

## Backups

A branch created only to preserve state before a risky rebase is prefixed `backup/` and names what it
protects plus why:

```
backup/account-onboarding-pre-rebase
```

These are disposable. Delete them once the operation they protected has succeeded and been verified —
an accumulated wall of `backup/` branches hides the one that still matters.

## Isolated checkouts

If the consuming project isolates checkouts, each checkout owns its runtime. Never share a branch
between two checkouts. Two checkouts of one branch is how a gate in one silently verifies the other's
tree.

Never set `reuseExistingServer: true` across siblings.

A gate refusing because a runtime is already bound is isolation working. Identify the owner before
touching anything (`lsof` / process list). Another checkout of this repository: stop it there.
Another project entirely: leave it alone and move this checkout instead.
