# Artifact Lifecycle

**Read when:** deciding whether an artifact is kept or discarded.

**Why this exists:** Planning artifacts kept forever become a second, drifting description of the
code. The inverted arrangement gated drift on documents nobody read, while nothing remembered what
the product currently promises users. Keep what is still true after the feature ships; discard the
rest.

Every artifact costs something forever: review attention, drift risk, and context budget. The question
is never "is this useful" — it is "is this useful *after the feature ships*".

## The split

| Durable — committed, maintained | Disposable — scratch, dies with the branch |
| --- | --- |
| The code and its tests | `memory/` workflow memory |
| `.specs/features/<feature>/` workflow state | `uiux.md`, `dx.md`, review rounds |
| `.specs/STATE.md` decisions (`AD-NNN`) | |
| `docs/qa/` — scenarios, journeys, bugs, charters, reports | |
| `docs/` — product, architecture, engineering, design | |
| Durable lessons | |

The principle behind the line: **feature workflow state travels with the work.** Specs, tasks, and
verification state keep worktrees, gates, and reviewers aligned.

A verification artifact's job is never finished, because it answers a question about the *present*
state of the product — which is why `docs/qa/` is on the other side of the line.

## Why this exists

Product promises still belong in `docs/qa/scenarios/`; feature workflow state belongs under
`.specs/features/`.

## Rules

1. **`.specs/features/` is versioned workflow state.** Specs, tasks, test contracts, workflow
   snapshots, and validation reports travel with the feature through worktrees, gates, and CI.
   Adoption removes only the exact legacy managed `.specs/features/` ignore line, including
   duplicates, while preserving consumer-owned lines and comments; it never stages or commits files.
2. **Promote before the pull request.** Anything that must outlive the feature moves to its real home:
   - A project decision → `.specs/STATE.md` as `AD-NNN`
   - A durable lesson → the lessons layer
   - A product promise → `docs/qa/scenarios/`
   - An architecture invariant → the consuming project's architecture docs
   - A rule agents must follow → this guidelines directory
3. **Nothing gates a disposable artifact for drift.** A document nobody reads after the merge cannot
   be stale in a way that matters.
4. **One home per fact.** A fact recorded in two durable places will disagree with itself. If it
   belongs in `docs/`, it is referenced from a guideline — never copied into one.

## Cleanup cadence follows read frequency, not size

The three stores need three different policies, and the sizes mislead:

| Store | Loaded when | Policy |
| --- | --- | --- |
| `.specs/archive/features/` | never | **No recurring job.** The rule above stops the directory regrowing |
| `.specs/lessons.json` | every Specify and Design | **Nothing to do.** It prunes itself — a candidate that has not recurred within `window_days` drops on every `add` or `list` |
| `.specs/STATE.md` | every Design and every resume | **The one recurring job.** Split by status when superseded entries pass ~15, or annually |

The largest store is the one that needs no maintenance, because nothing reads it. The smallest is the
one that does, because everything does.

**Never delete a decision.** Superseding is already the mechanism, and the record of why something
changed is the value — moving a superseded entry to `DECISIONS-ARCHIVE.md` keeps its id and full
text. Ids are never reused.

**Never hand-edit the lessons store.** It is machine-owned; `LESSONS.md` is rendered from it.

## Archived planning trees

If a consuming project archives old feature directories under `.specs/archive/features/`, treat them
as history, not context: never loaded as implementation context, never maintained. Keep them only
while something still cites them as a `resource`.

## Scheduling follow-ons

Work identified but not done becomes ordinary features with ordinary specs. It is not carried as an
ambient intention in an instruction file. A model that counts is a model that miscounts — scripts
that audit `tests.md` ids, validate QA frontmatter, or cache gate fingerprints belong as features of
the consuming project, not as extra guidelines here.
