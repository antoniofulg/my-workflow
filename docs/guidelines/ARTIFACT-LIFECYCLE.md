# Artifact Lifecycle

**Read when:** deciding whether an artifact is kept or discarded.

Every artifact costs something forever: review attention, drift risk, and context budget. The question
is never "is this useful" — it is "is this useful *after the feature ships*".

## The split

| Durable — committed, maintained | Disposable — scratch, dies with the branch |
| --- | --- |
| The code and its tests | `spec.md`, `design.md`, `tasks.md` |
| `.specs/STATE.md` decisions (`AD-NNN`) | `tests.md` once its cases are implemented |
| `docs/qa/` — scenarios, journeys, bugs, charters, reports | `memory/` workflow memory |
| `docs/` — product, architecture, engineering, design | `uiux.md`, `dx.md`, review rounds |
| Durable lessons | Validation and verification reports |

The principle behind the line: **a planning artifact's job is finished when the code exists.** After
that it is a second description of the same thing, and two descriptions drift.

A verification artifact's job is never finished, because it answers a question about the *present*
state of the product — which is why `docs/qa/` is on the other side of the line.

## Why this exists

The inverted arrangement — permanent planning artifacts gated for drift, no durable record of what
the product promises users — produces a gate policing documents nobody reads, and features
re-verified from scratch because nothing remembered the last verdict.

## Rules

1. **Planning artifacts stay out of the durable record.** They live on the branch and are not
   maintained after the merge. Git history holds them if anyone ever needs to look.
2. **Promote before the pull request.** Anything from a planning artifact that must outlive the
   feature moves to its real home first:
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
