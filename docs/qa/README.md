# QA operational profile

This file is the consuming project's stack-specific QA profile. Adoption creates it as a template
only when it is absent; the consuming project owns its contents. Keep command facts in executable
manifests or CI and link to those authorities instead of copying commands here.

## Public interfaces and area codes

List each user-observable surface that QA can reach and assign the area code used by
`docs/qa/scenarios/`:

- Browser: `[area]` — `[entry point or route]` — `[authority]`
- API: `[area]` — `[endpoint or contract]` — `[authority]`
- CLI: `[area]` — `[verb or command entry point]` — `[authority]`
- Mobile: `[area]` — `[build or installed entry point]` — `[authority]`
- Manual: `[area]` — `[human entry point]` — `[authority]`

Remove surfaces that do not exist and add the product's own areas. Do not invent an interface to
fill the template.

## Runner and adapter

- Existing runner or adapter: `[name, or manual]`
- Manifest or CI authority: `[repository path and job]`
- Exact path used by `qa-execute`: `[link or repository path]`
- Installed QA tooling discovered: `[names and paths, or none]`

Prefer an existing browser, API, CLI, mobile, or manual adapter. Missing tooling is a recorded
limitation; adoption does not install a framework or invent commands.

## Build, start, and health

- Build authority: `[manifest, task, or CI job]`
- Production-parity start authority: `[manifest, task, or CI job]`
- Health signal: `[endpoint, check, or manual observation]`
- Environment and checkout isolation: `[profile or CI authority]`

## Authentication and test data

- Test identity or session setup: `[safe reference; no secrets]`
- Fixtures or seed authority: `[repository path, manifest, or CI job]`
- Cleanup and teardown authority: `[repository path, manifest, or CI job]`
- Residue check: `[query, check, or manual observation]`

## Evidence and limitations

- Raw evidence path: `[disposable, ignored path owned by this project]`
- Durable reports and statuses: `docs/qa/`
- Known limitations or unreachable surfaces: `[none, or named limitation]`
- External dependencies requiring a human: `[none, or named dependency]`

`qa-plan` reads this profile before mapping promises. `qa-execute` selects the declared adapter,
records the exact path, evidence, and limitations, and leaves product fixes to an Implementer.
