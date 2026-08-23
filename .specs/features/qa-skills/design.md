# QA Skills Design

## Overview

Create two provider-neutral, model-invoked skills. The existing Verifier dispatches each skill in a
fresh session. The consuming project supplies its operational adapter through `docs/qa/README.md`;
the skills never assume a framework.

## Ownership

| Concern | Authority |
| --- | --- |
| Scenario tree, frontmatter, status, flag/reset | `docs/guidelines/QA-SCENARIOS.md` |
| QA planning procedure | `.agents/skills/qa-plan/` |
| Real-user QA procedure and governed fix loop | `.agents/skills/qa-execute/` |
| Project-specific interfaces, runner, setup and limits | `docs/qa/README.md` in the consuming project |
| When QA runs | `docs/guidelines/QA-EXECUTION.md` |
| Independent reviewer dispatch | Provider `verifier` packets |
| Adoption and public provenance | `README.md` |

Guidelines carry triggers and dispatch only. Skills point to canonical schemas instead of copying
them. Provider packets share the same behaviour but retain their native formats and model pins.

## Skill packages

### `qa-plan`

`SKILL.md` contains the ordered planning path: load the feature contract and operational profile,
identify affected public journeys, update durable scenarios, reset affected rows, create charters,
and stop before live execution. A small disclosed reference defines how to interpret the operational
profile without duplicating scenario fields.

Completion requires every affected acceptance criterion to map to a journey/scenario or carry an
explicit reason that no user-visible promise changed.

### `qa-execute`

`SKILL.md` contains the session sequence: load the plan/profile, select the existing adapter, prepare
the environment, execute public journeys, record evidence and statuses, run exploratory lenses, and
close the report. Disclosed references own session protocol, evidence/reporting, and the fix loop.

When a product defect appears, the Verifier records it and returns the fix to an Implementer. A fresh
Verifier validates the fix; QA resumes from the affected journey. The QA Verifier never writes
product code.

Both skills use original repository wording and structure. Each names Antonio Fulgêncio as author
and links the corresponding Pedro Nauck skill as inspiration.

## Stack adaptation

The adoption prompt creates or updates `docs/qa/README.md` with:

- public interfaces: browser, API, CLI, mobile, or manual;
- runner/adapter, as a reference to an existing manifest, CI job, or documented path;
- production-parity start/build path and health signal;
- authentication/session setup;
- fixtures or seed path;
- cleanup and residue check;
- known limitations and unavailable surfaces.

Executable manifests and CI own command strings already declared there. The profile links to those
authorities. When the project has no runner, QA Execute selects the closest public interface and
records the limitation. Adding a framework is a separate, planned implementation task.

## Workflow sequence

```text
Implementer closes product slice
  -> fresh Verifier: technical contract and mutation sensor
  -> fresh Verifier: qa-plan when user-visible
  -> fresh Verifier: qa-execute with project adapter
       -> finding: Implementer fixes -> fresh Verifier -> resume affected journey
  -> deep-review according to REVIEW-ROUNDS
```

The final QA session remains non-authoring. QA evidence does not replace automated gates or
acceptance-criterion verification.

## Suggested adoption prompt

Replace the two mostly duplicated prompts with one prompt containing new-project and existing-project
branches. Its shared preflight performs read-only discovery, reports managed paths that adoption can
replace, and requires a clean-state check. Its closeout reports the diff and exact gate evidence.

The prompt points to the skills and operational profile. It does not embed their full procedures.

## Artifact lifecycle

Ignore `.specs/features/` as local planning state. Remove historical tracked feature artifacts from
the current tree. Keep `.specs/STATE.md` and `.specs/AD-INDEX.md` tracked. Validators continue to
receive explicit local paths; commit validation does not require `tasks.md` in the commit.

Ignore `.deep-review/*` and re-include `.deep-review/learnings.md`. Durable QA documents under
`docs/qa/` remain tracked; existing raw evidence/state ignores remain unchanged.

## Adoption integration

`scripts/adopt.py` copies both canonical skill directories through its explicit allowlist. Claude's
existing link step discovers them automatically. The prompt states that managed instruction trees
and `CLAUDE.md` can be replaced and requires post-adoption diff review.

## Verification strategy

Extend the canonical Vitest suite with semantic structural checks for metadata, responsibility
boundaries, provider parity, provenance links, prompt preflight/closeout, adapter selection, adopt
allowlisting, and selective ignores. Run the writing-skills metadata validator for both skills.
Finish with `npm_config_offline=true npm test`, independent Verifier mutation probes, Deep Review,
and a documentation QA session.

## Failure semantics

- Missing operational profile: discover capabilities read-only, create the profile, then plan QA.
- Missing runner: use the closest public interface and record `untested` only for unreachable legs.
- Missing credentials or external dependency: record `blocked-verify`; never fabricate evidence.
- Product defect: hand off to Implementer and require a fresh Verifier before resuming.
- Unclean adoption target: report overlapping changes and halt before replacement.
