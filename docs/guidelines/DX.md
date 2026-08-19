# Public Surface Contract

**Read when:** the feature adds or changes a public surface — an HTTP route, a config key, a CLI verb,
a package export.

**Why this exists:** A surface designed after its internals inherits the internals' shape instead of
the caller's needs. Writing the contract first — as if it already shipped, failures enumerated —
surfaces ergonomic problems while they are still free to fix. Internals-only features skip this.

## The artifact

`.specs/features/<feature>/dx.md`, written in Design, before internal design.

```markdown
# <Feature> Surface Contract

## Routes

### `POST /api/records`
- **Auth:** none
- **Request:** `{ name, email, region }`
- **Success:** `201 { id, createdAt }`
- **Failures:** `422` validation, field-level detail · `429` rate limited · `500` no detail
- **Idempotency:** none — duplicate submissions create duplicate rows by design

## Config

| Key | Type | Default | Effect |
| --- | --- | --- | --- |
| `PUBLIC_RATE_LIMIT_PER_MINUTE` | integer | 10 | Requests per IP before 429 |

## Exports

What this feature adds to a package's public interface, and what now depends on it.

## Removals

What this feature deletes. Hard cuts, no aliases, no dual fields.
```

## Rules

1. **Write it as if it shipped.** Present tense, no hedging, no "we could". A surface described in
   conditionals has not been decided.
2. **Every failure is enumerated with its status and its body shape.** An unlisted failure ships as a
   500.
3. **Error copy is part of the surface.** What the caller reads on failure is designed here, not
   improvised in a catch block.
4. **The surface freezes before internals.** Internals are designed to serve it. Reopening it later is
   an explicit decision, not a quiet adaptation.
5. **Removals are listed.** This workflow does not preserve backward compatibility — so a change that
   removes something states exactly what goes, and the same change updates every caller.
6. **It respects the project's boundary.** The consuming project's architecture docs name the product
   boundary. A surface that would violate that boundary is wrong at design time, not at build time.

## What to grill before freezing

The questions worth asking about a surface, once the draft exists:

- Does the name say what it does to someone who has not read the spec?
- Is the failure a caller is most likely to hit the one with the clearest message?
- What happens on the second call with the same input?
- What does this look like from a client that cannot retry?
- Which field will someone want that is not here, and is leaving it out deliberate?

The draft is the question. Rework it between rounds rather than discussing it in the abstract.
