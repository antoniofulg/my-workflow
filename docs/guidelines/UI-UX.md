# UI/UX Surface Map

**Read when:** the feature adds or changes a screen.

Optional by design. A feature with no new or changed screen skips this entirely.

## Why it exists

Two reasons, and the second one is the reason it earns its cost:

1. Internals designed before the surface is settled get redesigned when the surface moves.
2. **This document is the input a design agent reads.** Handed a filled `uiux.md`, a design agent
   produces every component and state in one pass instead of guessing. That is where the time comes
   back.

## The artifact

`.specs/features/<feature>/uiux.md`, written in Design, **before** internal design begins.

```markdown
# <Feature> UI Change Map

## Screens

### <Screen name> — `<route>`
- **New or changed:** changed
- **Story:** links the user story it serves
- **Entry points:** how a user reaches it
- **States:** empty · loading · populated · error · submitting · success
- **Breakpoints:** mobile, desktop — and what differs

## Components

| Component | New or existing | States and variants | Source |
| --- | --- | --- | --- |
| `PublicForm` | new | idle, validating, submitting, error, success | composed from existing primitives |
| `RegionPicker` | existing | unchanged | the project's design docs |

## Copy

Every user-visible string this feature introduces, in the product's language, with its context.

## Out of scope

Screens and components this feature deliberately does not touch.
```

## Rules

1. **Enumerate states. Never write "all states".** A component with an unlisted error state ships
   without one. `empty · loading · populated · error` is a list a design agent can execute; "all
   states" is not.
2. **Reuse before create.** Check the project's design docs and the existing component inventory
   before proposing anything new. A new generic primitive needs a reason; a domain variant takes a
   domain-prefixed name.
3. **Every value comes from the design system.** Colour, type, radius, spacing and motion come from
   the token source. Never invent a value in a feature.
4. **Truthful UI over plausible UI.** Never render a control or a metric the backend does not support.
   On conflict, runtime truth wins.
5. **The surface freezes before internals.** Once this document is settled, internals are designed to
   serve it — never the reverse. Changing the surface afterwards means reopening this document
   explicitly, not quietly adapting it to what got built.
6. **Its existence marks the feature UI-bearing** for the QA pass. A feature with a `uiux.md` gets
   browser scenarios in `docs/qa/scenarios/`.

## Working with a design agent

The intended flow, in order:

1. Write `uiux.md` from the spec and its user stories.
2. Hand `spec.md` + `uiux.md` to the design agent; ask for every component and every listed state.
3. Review what came back **against `uiux.md`**, not against taste. Anything that does not match goes
   into `uiux-review.md` as a list of concrete corrections and goes back.
4. Repeat until the review file is empty, then design internals.

Step 3 is the one that gets skipped and the one that matters. A mockup reviewed against taste produces
another round of taste; a mockup reviewed against an enumerated state list converges.

## Verifying the built screen

When the spec names a visual reference, the completion claim needs a comparison, not a screenshot.
Required for each state and breakpoint: the rendered reference, the implementation, and a stated
verdict on the differences.

An implementation-only capture is not parity evidence. Differences in content, data, copy, brand marks
and host chrome are judged against their real owners — runtime truth and the design system — not
against the mockup. The mockup owns visual language only.
