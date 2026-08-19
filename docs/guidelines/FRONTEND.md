# Front-End Engineering

**Read when:** writing or reorganizing front-end application code, or working on a mockup under
`docs/design/`.

This document owns front-end *code organization*. It does not own appearance or behaviour. The
consuming project's design docs win on appearance and behaviour. Link to those instead of restating
them here.

## Feature folders vs shared UI

Routes compose. A route selects a shell, loads route state and composes feature and shared
components. It does not own reusable layout and does not draw raw landmarks (`header`, `nav`,
`main`) that a shell already owns.

Feature-specific browser and transport logic lives in a feature folder named for the capability:

- a client adapter for the browser-facing surface;
- a server-side forwarder only when this app is not itself the product boundary;
- an explicit marker (suffix, package, or bundler boundary) for modules that must not enter the
  browser bundle.

Shared folders have narrower roles: generic primitives, compositions used by more than one route,
feature-neutral helpers. Do not move feature-specific policy into a shared folder to avoid creating
a feature folder.

Tests stay grouped by execution layer, not by feature folder, unless the consuming project already
colocate them.

## Component script

Follow this order before writing any application UI:

1. Identify the shell. Exactly one component owns each shell. Select it; do not improvise an
   equivalent header, navigation or main layout in the route.
2. If the needed primitive exists, use it without a wrapper whose only purpose is spacing or styling.
3. If a shared composition exists, use it.
4. If a generic primitive is missing, add it at the project's primitive layer — follow that layer's
   generation rules; do not hand-edit generated files.
5. Express a primitive variation as a variant of that primitive. Do not copy or fork it.
6. If a product composition is missing, add it with closed props. Use a free slot only when the
   surface genuinely varies. Consistency-critical content belongs in named, constrained props.
7. Never add a stylesheet outside the project's canonical style root.

## Mockups

Standalone mockups are implementation references when the project treats them that way, not
disposable sketches. Reuse the same shell family, component treatment and state vocabulary the
implementation will use. If the existing pattern cannot express the surface, change the shared
reference deliberately and extend its conformity test in the same task.

## Browser permanence

Use the cheapest layer that discriminates the outcome. Keep an application e2e permanently only for a
browser-only or real-stack property, a session/cookie/origin/authorization/checkout boundary, a named
minimum smoke capability, or a regression that lower layers demonstrably miss. Permanent scenarios
carry stable `@feature:<slug>` and `@journey:<slug>` tags, own every account/IP/session/resource they
create, and clean exact resources in `finally` with zero-residue assertions. Temporary probes are
removed before commit.

Durable regression is a deterministic spec with no model call. Exploratory scripts and agent sessions
are disposable. Neither their transcript nor a successful session is evidence.

## Vendored skill scope

Vendored skills are advisory. Canonical project documents, installed source and installed dependency
declarations win when guidance conflicts. Do not edit a vendored skill to record a project exception:
that changes its lockfile hash and the next upstream refresh can overwrite the edit. Record the
exception in the consuming project's front-end guideline.
