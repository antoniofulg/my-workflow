# QA Skills Specification

## Problem Statement

QA planning and real-user QA execution currently live as detailed guideline prose. They are not
independently discoverable skills, their boundaries are easy to blur, and their relationship with
the provider-specific Verifier is implicit. The workflow needs two project-owned skills with one
responsibility each, durable QA artifacts, explicit reviewer hand-offs, and visible credit to the
Pedro Nauck skills that inspired them.

## Out of Scope

- Adding a new reviewer or QA agent role.
- Changing the canonical scenario schema or status vocabulary in `docs/guidelines/QA-SCENARIOS.md`.
- Copying the upstream skills, templates, scripts, or prose verbatim.
- Installing the project-owned skills through `skills-lock.json`.
- Changing product runtime behaviour or introducing a security surface.

## Assumptions & Open Questions

- The canonical skill names are `qa-plan` and `qa-execute`.
- Antonio Fulgêncio is the author; Pedro Nauck is credited as the author of the inspiring
  `qa-report` and `qa-execution` skills.
- The existing `verifier` role executes technical verification, QA Plan, and QA Execute in separate
  sessions; author and verifier remain different agents.
- `docs/qa/` remains durable. Raw QA evidence and generated run state remain disposable.
- Each consuming project records its stack-specific QA capability profile in `docs/qa/README.md`;
  executable manifests and CI remain authoritative for commands already declared there.
- Feature workflow trees under `.specs/features/` are versioned state alongside `.specs/STATE.md`
  and `.specs/AD-INDEX.md`; raw QA evidence and generated run state remain disposable.

Open questions: None.

## User Stories

### US-01 — Plan durable QA coverage

As the workflow author, I want a QA Plan skill that converts feature intent into durable journeys,
scenarios, and session charters so user-visible promises can be reviewed and reused.

Acceptance criteria:

- **QA-01:** WHEN agent discovery scans `.agents/skills` THEN the system SHALL expose a valid, model-invoked `qa-plan` skill from the provider-neutral canonical directory.
- **QA-02:** WHEN a user-visible feature reaches QA planning THEN the Verifier SHALL use `qa-plan` to create or update journeys, scenarios, and charters under `docs/qa/` without executing the product or changing product code.

### US-02 — Execute real-user QA independently

As the workflow author, I want a separate QA Execute skill so a Verifier can walk the planned
journeys through public interfaces and report observable results without becoming the implementer.

Acceptance criteria:

- **QA-03:** WHEN agent discovery scans `.agents/skills` THEN the system SHALL expose a valid, model-invoked `qa-execute` skill from the provider-neutral canonical directory.
- **QA-04:** WHEN QA execution begins THEN the Verifier SHALL consume the current QA plan, exercise public interfaces, update durable QA status and reports, and keep raw evidence in disposable paths.
- **QA-05:** WHEN QA Execute finds a product defect THEN the Verifier SHALL record the finding, return remediation to an Implementer, require a fresh Verifier after the fix, and resume QA from the affected journey.

### US-03 — Use one QA contract across providers

As a workflow user, I want Cursor, Claude, and Codex to dispatch the same canonical skills so provider
choice does not change the QA process.

Acceptance criteria:

- **QA-06:** WHEN any supported provider assigns QA Plan or QA Execute THEN its existing `verifier` SHALL dispatch the matching canonical skill without introducing a separate reviewer role.
- **QA-07:** WHEN QA guidance is loaded THEN the system SHALL keep scenario schema and status rules authoritative in `docs/guidelines/QA-SCENARIOS.md` while other guidelines contain only dispatch and workflow integration.

### US-04 — Make authorship and inspiration explicit

As a repository reader, I want clear provenance so I can distinguish Antonio's adaptations from
Pedro Nauck's original skills.

Acceptance criteria:

- **QA-08:** WHEN a reader opens the repository README THEN the system SHALL explicitly credit Tech Leads Club for `tlc-spec-driven` and Pedro Nauck for `deep-review`, `qa-report`, and `qa-execution`, with direct source links.
- **QA-09:** WHEN a reader opens either QA skill THEN the system SHALL identify Antonio Fulgêncio as author and credit Pedro Nauck with a direct link to the corresponding inspiring skill.
- **QA-10:** WHEN the QA skills are authored THEN the system SHALL use project-owned wording and structure adapted to this workflow rather than reproduce unlicensed upstream content.

### US-05 — Keep the public repository product-neutral

As the workflow author, I want the README to describe only the reusable workflow so personal product
names and stack choices do not leak into the public package.

Acceptance criteria:

- **QA-11:** WHEN a reader opens the README THEN the system SHALL describe the repository as stack-agnostic without naming Creatista, antclips, or product-specific technology choices.

### US-06 — Keep Deep Review output out of Git

As a maintainer, I want generated Deep Review runs ignored while durable learnings remain available
for review.

Acceptance criteria:

- **QA-12:** WHEN Deep Review generates `.deep-review/` artifacts THEN Git SHALL ignore all generated contents except `.deep-review/learnings.md`.

### US-07 — Adapt QA to the consuming stack

As a developer adopting the workflow, I want setup to discover the project's actual operational
capabilities so QA can use its existing stack without hard-coded framework choices.

Acceptance criteria:

- **QA-13:** WHEN the workflow is adopted into a project THEN the setup prompt SHALL first discover the package/build system, declared gates, production-parity start path, public interfaces, authentication, fixtures, cleanup, and installed QA tooling through read-only inspection.
- **QA-14:** WHEN setup finishes capability discovery THEN the system SHALL record the project-specific QA interface, runner, authentication setup, fixtures, cleanup, and known limitations in `docs/qa/README.md`, referencing executable manifests or CI as the authority for commands already declared there.
- **QA-15:** WHEN no QA runner is already adopted THEN setup and QA Execute SHALL use the closest available public interface and record the limitation without installing a framework automatically or inventing commands.
- **QA-16:** WHEN the Verifier executes QA THEN it SHALL read the operational profile, choose the project's declared browser, API, CLI, mobile, or manual adapter, and report the exact path, evidence, and limitations used.

### US-08 — Make suggested setup prompts safe and actionable

As an adopter, I want copy-paste prompts that expose setup effects and produce a reviewable adaptation
instead of silently assuming repository conventions.

Acceptance criteria:

- **QA-17:** WHEN a reader uses either suggested adoption prompt THEN the prompt SHALL require a clean-state check, read-only capability discovery, preservation of product-owned documentation, explicit review of overwritten managed paths, and final diff plus gate evidence.
- **QA-18:** WHEN the workflow documents its suggested prompts THEN the system SHALL point QA work to `qa-plan`, `qa-execute`, and the existing provider Verifier without duplicating their operational instructions in the README.

### US-09 — Keep feature workflow state durable

As the workflow author, I want feature specifications and task state versioned so worktrees, gates,
and reviewers share the same contract and progress.

Acceptance criteria:

- **QA-19:** WHEN feature planning creates files under `.specs/features/` THEN Git SHALL keep that tree eligible for tracking as versioned workflow state alongside `.specs/STATE.md` and `.specs/AD-INDEX.md`.
- **QA-20:** WHEN task commits are created THEN the workflow SHALL require the current versioned `tasks.md` state to be closed before the commit, and its task/status update MAY be included in the same atomic commit.
- **QA-21:** WHEN adoption finds exact legacy `.specs/features/` ignore entries THEN it SHALL remove those entries, including duplicates, preserve unrelated consumer lines and comments, and SHALL NOT stage or commit files automatically.

### US-10 — Publish the new capability version

As a package consumer, I want the manifest version to communicate that this delivery adds compatible
new workflow capabilities.

Acceptance criteria:

- **QA-22:** WHEN the QA skills feature is delivered THEN the package and lockfile SHALL report version `0.3.0` consistently.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| QA-01 | US-01 | Specify | Complete |
| QA-02 | US-01 | Specify | Complete |
| QA-03 | US-02 | Specify | Complete |
| QA-04 | US-02 | Specify | Complete |
| QA-05 | US-02 | Specify | Complete |
| QA-06 | US-03 | Specify | Complete |
| QA-07 | US-03 | Specify | Complete |
| QA-08 | US-04 | Specify | Complete |
| QA-09 | US-04 | Specify | Complete |
| QA-10 | US-04 | Specify | Complete |
| QA-11 | US-05 | Specify | Complete |
| QA-12 | US-06 | Specify | Complete |
| QA-13 | US-07 | Specify | Complete |
| QA-14 | US-07 | Specify | Complete |
| QA-15 | US-07 | Specify | Complete |
| QA-16 | US-07 | Specify | Complete |
| QA-17 | US-08 | Specify | Complete |
| QA-18 | US-08 | Specify | Complete |
| QA-19 | US-09 | Specify | Complete |
| QA-20 | US-09 | Specify | Complete |
| QA-21 | US-09 | Specify | Complete |
| QA-22 | US-10 | Specify | Complete |
