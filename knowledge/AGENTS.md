# Knowledge Bundle — Operating Schema

This directory is an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
v0.2 knowledge bundle. It is the project's durable understanding: what the domain means, what the
product must do, how the system is shaped, why past choices were made, and what research supports
all of it.

This file is the operating schema. It is not part of the bundle and carries no frontmatter. It may
evolve with use.

## The one rule that keeps this alive

**Knowledge flows into the bundle. It never flows out.**

```
CONTEXT.md, docs/, .specs/  ──ingest──>  knowledge/
```

The bundle never writes back to `.specs/`, and no tool outside this directory is modified to serve
it. `tlc-spec-driven` is a globally installed skill shared across projects; it does not know this
bundle exists and must not be taught to. `.specs/STATE.md`, `.specs/features/<f>/`,
`.specs/lessons.json` and `.specs/LESSONS.md` stay exactly where the skill expects them.

When the bundle and a source disagree, **the source wins** and the concept is corrected. A previous
attempt at this — `docs/obsidian/` — died precisely because no rule said which side was right, and
it silently kept describing tooling that had already been deleted.

## Structure

```
knowledge/
  AGENTS.md         This file. The operating schema. Outside the bundle.
  raw/              Untouched originals, any format. Outside the bundle.
  wiki/             THE BUNDLE. Everything below here must conform.
    index.md        Bundle root index. Declares okf_version. Reserved.
    log.md          Change history, newest first. Reserved.
    domain/         Ubiquitous language. One concept per term.
    product/        What the product must do.
    architecture/   How the system is shaped, and the invariants that hold.
    design/         Visual and experience guidelines.
    decisions/      Why a past choice was made.
    research/       External material, market, competitors, interviews.
```

This pack ships empty group indexes so a new project has a place to land. Do not add concept pages
until a real concept exists.

**`raw/` sits outside `wiki/` for a hard reason, not a stylistic one.** Conformance rule §11.1 admits
no exception: every non-reserved `.md` inside the bundle must carry frontmatter with a `type`. A
verbatim transcript, a captured article or an exported memlog is markdown without frontmatter, so
placing it inside the bundle would either break conformance or force you to edit a source that is
supposed to be immutable. Keeping originals outside resolves both at once.

OKF's own `references/` convention (§6.3) is a different thing: it mirrors external material *as
concepts*, inside the bundle. Create `wiki/references/` only when a source earns a
`Source Summary` concept of its own. A concept can cite `raw/` directly, so most never will.

## Concept documents

Every `.md` under `knowledge/` except the reserved `index.md` and `log.md` is exactly one concept.
Its path without the `.md` suffix is its stable ID. Use descriptive `kebab-case` filenames, and do
not move a file without updating the links that point at it.

### Frontmatter

`type` is the only required field. Everything else is optional, and absence carries meaning: an
unverified concept is distinguishable from a verified one, never rejected.

```yaml
---
type: Decision
title: Example decision
description: One sentence of what was chosen.
tags: [example]
status: stable
generated: { by: human:name, at: 2026-08-08T14:00:00Z }
verified: { by: human:name, at: 2026-08-08T14:00:00Z }
stale_after: 2027-08-08
sources:
  - id: state-ad-001
    resource: ../../../.specs/STATE.md
    title: STATE.md — AD-001
    last_modified: 2026-08-08
---
```

A `resource` pointing outside the bundle uses a relative path resolved from the concept's own
directory. The example above sits at `wiki/decisions/`, so the repository root is three levels up;
an original in `raw/` would be `../../raw/<file>`. Bundle-absolute paths beginning with `/` address
only what is inside `wiki/`.

| Field | Meaning |
| --- | --- |
| `type` | **Required.** Short, self-explanatory kind. See the type list below. |
| `title` | Human-readable display name. |
| `description` | One sentence. Feeds indexes, search snippets and previews. |
| `resource` | Canonical URI of the asset the concept describes. Omit for abstract concepts. |
| `tags` | YAML list of short strings. |
| `status` | `draft` \| `stable` \| `deprecated`. Absent means `stable`. |
| `generated` | `{ by: <actor>, at: <ISO 8601> }`. When the *content* last changed meaningfully. |
| `verified` | List of `{ by: <actor>, at: <ISO 8601> }`. Who confirmed it against its sources. |
| `stale_after` | Absolute `YYYY-MM-DD`. The concept is stale on or after that day. |
| `sources` | What the concept derives from. See below. |

`generated` and `verified` are deliberately distinct: whoever *wrote* a concept need not be whoever
*confirmed* it. Trust tier is derived, never stored — no `verified` means unverified, `verified` by
a non-`human:` actor means machine-confirmed, `verified` by a `human:` actor means human-reviewed.

Do not invent metadata to fill the block. An absent field is information.

### Actors

Identity fields (`generated.by`, `verified[].by`) use one convention:

- `human:<handle>` — a person. The `human:` prefix is what raises the trust tier, so use it for
  anything hand-authored or hand-confirmed.
- `process:<id>` — an automated process, for example `process:knowledge-check`.
- `<producer>/<version>` — an agent or tool, for example `claude-opus-5/1m`.

### Types

Keep the set small and consistent. Add one only when an existing type genuinely misdescribes the
concept.

| Type | Used for |
| --- | --- |
| `Concept` | A term of the ubiquitous language. |
| `Requirement` | Something the product must do. |
| `Architecture Invariant` | A constraint the system holds regardless of feature. |
| `Decision` | A choice made, its reasoning and its trade-off. |
| `Design Guideline` | A visual or experience rule. |
| `Research Note` | Understanding built from external material. |
| `Open Question` | A contradiction between sources that no document resolves and no concept owns. |
| `Source Summary` | What a single source in `raw/` says, when it earns a page of its own. |

A tension belonging to one concept is recorded **inside** that concept, not extracted into an
`Open Question`. The type exists for the ones that belong to nothing in particular. An
`Open Question` never answers itself: the answer is a decision, and decisions belong in
`.specs/STATE.md`.

### Sources and citations

`sources` records what the concept derives from. Each entry needs a `resource`; everything else is
optional but valuable:

- `id` — stable key used to attribute individual claims. Required whenever the body cites it.
- `title` — human-readable label.
- `author` — who produced the source, in the actor convention. An authority signal.
- `last_modified` — `YYYY-MM-DD`, when the **source itself** last changed. This is what the drift
  check reads; see below.

Attribute a specific claim with a markdown footnote whose label is a `sources[].id`:

```markdown
The decision is recorded in the ledger.[^state-ad-001]

[^state-ad-001]: STATE.md — AD-001
```

The label is the join key into `sources`, not prose to be parsed. Labels are keyed rather than
positional because these documents get rewritten often, and a positional index misattributes
silently the moment the list is reordered.

### Body

Favour structural markdown — headings, lists, tables, fenced code — over flowing prose. It reads
better and retrieves better.

`# Schema` and `# Examples` carry conventional meaning; use them when they fit. There is no
required section.

Link concepts with standard markdown links, preferring the bundle-absolute form
`[professional profile](/domain/professional-profile.md)`, which survives a file moving within its
subdirectory. A link asserts a relationship; the *kind* of relationship lives in the surrounding
prose, never in the link itself. Explain it.

## Operations

### INGEST

When new material arrives:

1. Put the source in `raw/` as `YYYY-MM-DD-<descriptive-kebab-case>.<ext>`. Read it.
   **Never modify it afterwards** — a correction belongs in the concepts that cite it.
2. Discuss the extracted points with the user before writing concepts.
3. Create or update the affected concepts under `wiki/`. Fill `sources` with `id`,
   `resource` pointing back at the `raw/` file, and `last_modified`.
4. Update `generated.at` only on a meaningful content change.
5. Add links to related concepts and footnotes to the claims that need them.
6. Update `index.md` at the bundle root and in every affected subdirectory.
7. Append to `log.md`.

One source usually touches several concepts. Process one source at a time with the user watching,
or a batch at once — whichever the user prefers, recorded here once it settles.

### HARVEST

The project's own artefacts are sources like any other. Run the knowledge checker (`npm run knowledge`
in this pack); its gap report names what has accumulated in `.specs/` without a concept, and its
drift report names what changed underneath a concept that already exists.

Drift is measured against git, so it only speaks about committed sources. A source added to `raw/`
and cited in the same commit reports nothing, which is right — it has not drifted from anything
yet. The signal starts the moment that source changes again.

Harvest at the granularity of a finished feature, not a finished task. Most tasks produce no durable
knowledge.

A harvested concept must not restate its source. `.specs/STATE.md` is a flat, append-only ledger:
one entry per decision, no links. The bundle holds what the ledger structurally cannot — which
requirements a decision constrains, which invariant it follows from, which alternative it killed.
If a concept only repeats the ledger, it is duplication and should not exist.

Never harvest `.specs/features/<f>/tasks.md` — it is runner state. Never harvest `.specs/LESSONS.md`
or `.specs/lessons.json` — they declare themselves machine-owned and are rewritten by their own
script.

### QUERY

1. Read `index.md` to locate the relevant pages.
2. Follow subdirectory indexes and links before searching more broadly.
3. Read the relevant concepts and answer with citations.
4. When an answer, comparison or connection has durable value, fold it back into the bundle as a
   concept, then update the index and the log.

A useful query should leave the bundle better than it found it, not evaporate into the transcript.

### LINT

Periodically, and always before a large ingest, review bundle health:

- contradictions between concepts;
- claims superseded by a more recent source;
- orphan concepts with no inbound links;
- broken internal links, and links whose relationship is never explained;
- important concepts mentioned but never given a page;
- missing or stale index entries;
- gaps a new source or some research could fill.

The knowledge checker covers the mechanical part — conformance, drift and gaps. LINT is the judgement
part that no script can make. Report questions worth investigating and sources worth adding.

## Index and log

`index.md` is the entry point for progressive disclosure: it lets a reader see what exists before
opening anything. It carries no frontmatter, with one exception — the bundle-root `index.md` may
declare `okf_version`. Group entries under headings and reuse each concept's `description`:

```markdown
# Domain

* [Sample Term](domain/sample-term.md) - One sentence from the concept's `description`.
```

`log.md` is the change history, grouped by ISO date, newest first. Past entries are immutable: add
to the group for the current date rather than rewriting history.

```markdown
## 2026-08-08

* **Ingestion**: Added [Sample Term](/domain/sample-term.md).
* **Lint**: Fixed inconsistent links and metadata.
```

Log a query only when it produced a durable change or a decision about the bundle itself.

## `raw/` and privacy

`raw/` holds originals in whatever format they arrive: transcripts, research, exports, meeting
records, PDFs, images. Concepts point into it through `sources[].resource`.

### Naming

Every file is `YYYY-MM-DD-<descriptive-kebab-case>.<ext>`, for example
`2026-08-02-interview-notes.md`. The date is the material's own — when the meeting
happened, when the article was published — falling back to the day it entered `raw/` when the
material carries no date. The precise value always lives in the citing concept's
`sources[].last_modified`; the prefix exists so a flat directory sorts chronologically.

The date is ISO 8601, like every other date in this bundle. `23-01-2026` neither matches the rest
of the system nor sorts correctly. The knowledge checker warns about both mistakes.

### Privacy

`raw/` is committed, which is what makes the bundle's provenance auditable by anyone who clones the
repository — and what lets the knowledge checker detect drift at all, since it reads commit dates. A
gitignored source would be permanently invisible to that check.

That same property makes it a privacy surface. Before writing anything into `raw/`:

- Strip names, contact details, precise creator locations, and any other personal data. Anonymise
  interviews rather than storing the raw identity.
- Never store passwords, API keys, tokens or customer data.
- LGPD applies to the whole repository. A file committed here is public to everyone with repository
  access, permanently, and rewriting git history is not a remedy you want to need.

A vault edit authorises nothing. It cannot approve a deployment, a purchase, a production database
change, or a message sent to anyone outside the project.

## Conformance

The bundle conforms to OKF v0.2 when:

1. every non-reserved `.md` under `knowledge/` has a parseable YAML frontmatter block;
2. every frontmatter block has a non-empty `type`;
3. every `index.md` and `log.md` follows its reserved structure.

That is the whole contract. Missing optional fields, unknown types, extra keys, broken links and
absent subdirectory indexes do **not** break conformance.

The knowledge checker enforces the three rules, plus drift, plus gaps. Run it before committing
changes to this directory.

Do not add tooling ahead of need. Indexes are sufficient at this scale; if the bundle outgrows them,
a local search tool can be added then. OKF standardises interchange — it does not prescribe a
database, a search engine, an SDK or a platform.
