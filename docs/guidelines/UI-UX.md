# UI/UX Surface Map

**Read when:** the feature adds or changes a screen.

**Why this exists:** Internals designed first get redesigned when the screen moves. `uiux.md` freezes
states so a design agent can execute in one pass, and so QA knows the feature is UI-bearing. Features
with no new or changed screen skip this.

## The artifact

`.specs/features/<feature>/uiux.md`, written in Specify, **before** internal design begins.

## Optional design tooling

OpenDesign or another design tool may support visual iteration when available. It is optional: the
repository stores only the approved handoff, and tool absence or failure falls back to the normal
repository artifacts. Resolve disagreements in this order: `spec.md` → `uiux.md` → approved design
artifact → tool or plugin output, then legacy mockup.

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

Use this bounded procedure for UI-bearing work:

1. State constraints first: user goal, required states and actions, hierarchy, accessibility,
   responsive behavior, runtime/data limits, brand principles, and existing components.
2. Read only the selected product/design references and inspect affected existing components read-only.
   Use the existing pattern for a bounded composition or exact correction.
3. For a genuinely new screen or meaningful redesign, provide three distinct directions. A fourth
   is allowed only for a named additional tradeoff. Do not make variants a requirement for button,
   copy, token, or existing-component corrections.
4. Prototype in an available design tool, isolated HTML, or component playground when useful. Tool
   absence is not a blocker, and exploratory variants stay out of production routes.
5. Subtract labels, icons, borders, controls, and decoration that have no purpose, while retaining
   discoverability, accessibility, required actions, and useful feedback.
6. Review the selected direction against `uiux.md` for contract conformance and against coherent
   visual quality. Perform one exploration pass and one refinement by default, then name any
   remaining design choice instead of repeating indefinitely.
7. Record the chosen direction, reused components, states, breakpoints, copy, and tradeoffs in the
   existing feature UI contract. Human local QA is recorded only after human confirmation.

No new showcase, preview deployment, design integration, or split frontend/backend delivery is
mandatory. Keep the vertical slice and reuse existing catalogues when available.

## Verifying the built screen

When the spec names a visual reference, the completion claim needs a comparison, not a screenshot.
Required for each state and breakpoint: the rendered reference, the implementation, and a stated
verdict on the differences.

An implementation-only capture is not parity evidence. Differences in content, data, copy, brand marks
and host chrome are judged against their real owners — runtime truth and the design system — not
against the mockup. The mockup owns visual language only.
