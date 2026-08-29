# Knowledge Wiki

**Read when:** discussing a product rule, domain term, or architecture invariant stated in more than
one document — which is most of planning — or when durable knowledge surfaces in conversation and
needs recording.

**Why this exists:** Source documents cannot see each other. The wiki holds the graph and the
contradictions; it is not a summary of `docs/`. When bundle and source disagree, the source wins.
Silence when durable knowledge surfaces leaves an existing concept confidently wrong.

`knowledge/wiki/` is an Open Knowledge Format bundle holding what no single source document can: the
graph between them, and the contradictions no document resolves.

It is not a summary of `docs/`. Its pages synthesize several sources into one answer and cite each
claim back. A concept that reconciles four product files into a single table and names the failure
mode in both directions is doing work no source document could, because none of them can see the
other three.

This pack ships the machinery empty. The consuming project fills concepts as they are earned.

## Reading is automatic and cheap

No permission needed, no schema to load first.

1. Read `knowledge/wiki/index.md` — it is the router, and it lists what exists before you open
   anything.
2. Follow the subdirectory index, then the concept.
3. Answer with its citations, and follow them to the source when the answer must be exact.

Read it when the conversation is about:

- A product rule stated in several places
- A domain term whose meaning might differ between documents
- An architecture invariant and what it constrains
- Why a past decision went the way it did, including the reversals

**Planning a feature that touches those areas is exactly when to read it**, not a reason to skip it.

**The source always wins.** When bundle and source disagree, the source is right and the concept is
wrong. Say so and note it — never quietly follow the concept.

## Writing: never silently, but never miss it either

Two write paths, and they have different rules because the knowledge comes from different places.

### From the human, in conversation — offer it, every time

When something durable surfaces while talking, **say so and offer to record it**. The schema requires
this: *"a useful query should leave the bundle better than it found it, not evaporate into the
transcript."*

The stakes are asymmetric. An observation that contradicts a founding assumption does not merely leave
the bundle incomplete — it leaves an existing concept confidently wrong. Silence is the expensive
option.

Offer when any of these appear:

- An observation about real user behaviour that differs from a documented assumption
- A decision made in conversation that changes a documented rule
- A contradiction between two sources that the human points out
- An outside constraint learned from the market, a competitor, or a platform
- An answer derived at real cost that would cost the same to derive again

Do not offer for: anything a source document already states, implementation detail, or transient
status.

The offer names the target and waits:

> Users treating the catalogue as a directory rather than a search tool contradicts
> `product/<concept>.md`, which assumes intent-driven reads. I would write
> `raw/YYYY-MM-DD-<slug>.md` with the observation, then amend that concept to cite it. Record it?

Then INGEST as the schema defines it: the observation lands in `knowledge/raw/` as
`YYYY-MM-DD-<slug>` and is **never modified afterwards** — a correction belongs in the concepts citing
it. Concepts cite sources, so an observation with no `raw/` entry is a claim with no provenance.

**The human always decides. Never write without a yes, and never skip the offer because a feature is
in progress.**

### From shipped artifacts — explicit request only

HARVEST reads the project's own `.specs/`, commits and docs. Never run it as part of a feature: an
agent harvesting what it just wrote produces restatements, and the schema bans exactly that — a
harvested concept must not restate its source.

**At the granularity of a finished feature, never a finished task.** Most tasks produce nothing
durable. Never harvest `tasks.md` (runner state) or `LESSONS.md` / `lessons.json` (machine-owned).

### Either path loads the schema first

Writing means reading `knowledge/AGENTS.md` in full — it owns frontmatter, citation shape, index and
log rules. That load is justified for writing and wasted for reading.

## Verifying happens with the write, not with the ship

The knowledge checker (`bun run knowledge` in this pack) runs as the **first step of a harvest**, not
as part of the consuming project's full gate.

Its conformance, gap and drift reports are useful input when you are about to write to the bundle.
They are noise when you are trying to merge a bug fix — and the drift check is file-granular against
entry-granular sources, so an unrelated append to `.specs/STATE.md` restales every concept citing that
file. Gating a feature on that is gating on bookkeeping.

LINT is the judgment half no script performs — contradictions between concepts, claims superseded by a
newer source, orphan pages, missing index entries. It runs with the harvest, periodically, and always
before a large ingest.

## No overlap with the QA tree

Sometimes confused. They ask unrelated questions:

| | Asks | Built from |
| --- | --- | --- |
| `knowledge/wiki/` | How do these documents connect, and where do they contradict? | Reading documents |
| `docs/qa/scenarios/` | What does the product promise users, and what state is each promise in? | Walking the product |

Neither substitutes for the other.

## Summary

| Operation | Trigger | Who decides | Loads |
| --- | --- | --- | --- |
| **Read** (QUERY) | Automatic, whenever the topic spans documents | Agent | `index.md` + the concept |
| **Offer** (INGEST) | Automatic, whenever durable knowledge surfaces in conversation | **Human approves, agent writes** | `AGENTS.md` after the yes |
| **Harvest** (HARVEST) | Explicit request only, per finished feature | Human | `AGENTS.md` in full |
| **Verify** (knowledge checker + LINT) | With any write | Agent | — |

Reading and offering are the agent's job without being asked. Deciding is always the human's.
