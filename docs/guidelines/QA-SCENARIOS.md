# QA Scenarios

**Read when:** the diff changes user-visible behaviour, or you are planning a QA pass.

**Why this exists:** Feature verification dies with the feature. Without a tracker, a stale `pass`
looks like a current promise, and nothing remembers what a user can still do. A scenario holds a
verdict that survives between features and goes stale when a diff invalidates it.

`docs/qa/scenarios/` answers one question: **what does this product promise its users, and what state
is each promise in right now?**

This is not a test list. A test is checked when it runs; a scenario's verdict survives until a diff
invalidates it.

## Layout

```
docs/qa/
├── README.md                          area codes, entry points, how to reach the product
├── personas.md                        who walks the journeys
├── journeys/J-<slug>.md               journey maps and flows
├── scenarios/<AREA>-<slug>.md         the tracker — one file per promise
├── bugs/BUG-<YYYYMMDD>-<slug>.md      registry, deduplicated by symptom
├── charters/CH-<slug>.md              session missions, immutable once written
├── reports/<YYYY-MM-DD>-<scope>.md    one per run, never overwritten
└── automation-backlog/<slug>.md       exploratory findings worth automating later
```

`docs/qa/evidence/` and any generated table view are gitignored. Everything else is committed.

## Scenario file

```markdown
---
id: PUB-public-form-happy
area: PUB
title: Submit the public form end to end
persona: Visitor
journey: J-public-form
expected: Confirmation visible, row present, reload shows the submitted state
entry_points: /
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
overlaps:
---

Free prose lives here and only here.
```

**Flat frontmatter, one field per line, fixed order, enum-only values, all prose in the body.** This is
not style — it is what makes the tree greppable and merge-safe. `grep -l 'qa_status: fail'
docs/qa/scenarios/` must be the whole query, not an interpretation exercise.

## Field rules

| Field | Content |
| --- | --- |
| `id` | `<AREA>-<slug>` — equals the filename, never renamed |
| `area` | Code from the consuming project's `docs/qa/README.md` |
| `title` | Verb-first, ≤80 chars |
| `persona` | Exact name from `personas.md` |
| `journey` | A `J-<slug>` that exists in `journeys/` |
| `expected` | The observable that proves success, in user language, one sentence |
| `entry_points` | URL, route or command — semicolon-separated |
| `qa_status` | Enum only |
| `bug_ids` | Registry ids, semicolon-separated |
| `fix_status` | Enum only, meaningful when `bug_ids` is non-empty |
| `retest_status` | Enum only, meaningful when `fix_status: fixed` |
| `fix_commits` | Short SHAs, semicolon-separated |
| `evidence` | Paths backing the current verdict |
| `last_report` | Path of the report that produced the verdict |
| `overlaps` | Scenario ids covering the same behaviour, canonical owner first |

## Status enums

`qa_status` — `untested` · `pass` · `fail` · `blocked-verify` · `blocked-decision` · `skipped`

- `pass` requires the expected observable confirmed with evidence, through an independent read path,
  surviving a reload. Optimistic UI is not confirmation.
- `fail` requires `bug_ids` to be non-empty.
- `blocked-verify` is for legs only a human can complete — a real payment, a real email, a real
  third-party account. It says *no session will ever walk this*, so a missing tool, an unconnected
  browser or an absent fixture leaves the scenario `untested` instead: that gap closes on its own,
  and `untested` is the only status the next cycle picks back up.
- `blocked-decision` needs a product call before it can pass.

`fix_status` — *(empty)* · `pending` · `fixed` · `deferred`
`retest_status` — *(empty)* · `pending` · `pass` · `fail`

A scenario is done for a cycle when `qa_status` is terminal **and** any `fixed` bug has
`retest_status: pass`.

## Area codes

The consuming project owns the area table in `docs/qa/README.md`. Adding an area updates that file
first.

## Id minting

Ids are **content-addressed** — derived from the behaviour, never from a counter. `PUB-public-form-happy`,
not `PUB-003`.

This matters when several checkouts run at once. Nothing reads "the highest existing number", so
parallel branches cannot collide on minting. Two planners describing the same behaviour mint the
same id — that is deduplication working, not a conflict.

Ids are stable forever. Retiring a scenario means `qa_status: skipped` with `retired — <reason>` in
the body. The file stays as memory.

## Flag, then verify — the rule that keeps the tree honest

Before completing any task, ask: **does this diff change user-visible behaviour** — a screen, a route,
a config key, user-facing copy?

- **No** — state "no user-visible change" in the completion notes. Done.
- **New behaviour** — add scenario files with `qa_status: untested`.
- **Changed behaviour** — reset the affected files to `untested`. **A stale `pass` is worse than no
  verdict.**

Then walk them before the feature's pull request, per `docs/guidelines/QA-EXECUTION.md`. A flag
without a walk is `untested` debt that no cycle is guaranteed to clear.

**A slice walks what it flags.** A slice that puts something in front of a user flags its scenarios
and walks them before it is done — the behaviour is complete by definition, so the verdict is real
rather than provisional. A slice with no user-visible surface flags nothing and walks nothing.

The feature-closing QA session runs after the final implementation deep-review group, per
`docs/guidelines/QA-EXECUTION.md` and `docs/guidelines/REVIEW-ROUNDS.md`. It covers everything; a
scenario already walked and passing is confirmed there, not re-litigated.

## Merge behaviour

- Different scenarios → different files → never conflict.
- Same scenario, different fields → git auto-merges, because fields are one per line.
- Same scenario, same field → a small one-file conflict; keep the values whose `last_report` is newer.
- Same behaviour, two slugs → not a git conflict, so it must be hunted: fold the newer file into the
  older id, merge verdicts by report recency, update references, delete the duplicate.

## Anti-patterns

- **Prose statuses.** `qa_status: "passed after retest"` makes the tree unqueryable. The enum is
  `pass`; the story goes in the body.
- **Counter ids.** They reintroduce the shared counter that makes parallel checkouts collide.
- **A file per round.** One scenario, one file, forever. History lives in the dated reports.
- **Scenario bodies growing into narratives.** The frontmatter answers "what state is this in"; the
  why and how live in bug files and reports.
