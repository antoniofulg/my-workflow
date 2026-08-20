---
name: qa-plan
description: Plan user-visible QA coverage by mapping feature intent to durable journeys, scenarios, and session charters. Use when a Verifier prepares QA for a changed user-facing surface or adoption. Don't use for live product walks, defect fixes, or selecting a test framework.
metadata:
  author: Antonio Fulgêncio
---

# QA Plan

Plan a reviewable QA cycle for a user-visible change. Keep the plan stack-agnostic: the consuming
project's operational profile chooses the public interface and adapter later.

## Provenance

Author: Antonio Fulgêncio.

This is an original project-owned adaptation for this workflow, inspired by Pedro Nauck's
[`qa-report` skill](https://github.com/pedronauck/skills/tree/main/skills/mine/qa-report).

## Inputs and boundaries

Read the feature contract or Verifier packet, the current diff, `docs/qa/README.md`, and the
affected QA records. Read `docs/guidelines/QA-SCENARIOS.md` in full before creating or changing a
scenario. It owns the scenario tree, fields, ids, statuses, and flag/reset rules.

Plan journeys, scenarios, and charters. Leave live walks, evidence capture, defect remediation,
and framework selection to `qa-execute` or the next independent Verifier session.

When the profile is missing or incomplete, read
[`references/profile.md`](references/profile.md) in full before discovering capabilities or writing
`docs/qa/README.md`.

## Procedure

### 1. Resolve scope

Read the feature contract, acceptance criteria, current diff, and existing QA records. Classify each
changed surface as user-visible or internal. Include routes, screens, public configuration, CLI
commands, API responses, mobile surfaces, and user-facing copy when their observable behaviour
changed.

If no user-visible promise changed, record `no user-visible change` in the task handoff and stop.

**Done when:** every changed acceptance criterion has a user-visible/internal classification and the
no-surface case has a written handoff.

### 2. Load the QA context

Read `docs/qa/README.md`, the relevant personas, journeys, scenarios, open bugs, and current
charters. If the operational profile is absent or lacks a capability needed to plan the scope,
follow [`references/profile.md`](references/profile.md) in full and record discovered facts with
links to executable manifests or CI. Keep product-owned documentation intact while updating the
profile.

**Done when:** the plan names the profile path, every in-scope persona, and every existing journey or
scenario that can cover the changed surface.

### 3. Map the promises

Map every affected acceptance criterion to an existing journey and scenario. Mint a stable,
content-addressed scenario for a new promise. Fold duplicate coverage into the canonical scenario
and record overlaps there. Include one adjacent canary journey when the feature has a user-visible
surface.

Use the schema and status vocabulary from `QA-SCENARIOS.md`; keep field definitions in that file.
Describe the expected observable in user language and preserve scenario ids once published.

**Done when:** every user-visible acceptance criterion maps to one canonical scenario and journey,
or the handoff names the criterion and explains why no user promise changed.

### 4. Flag the cycle

Create a scenario with `qa_status: untested` when the promise is new. Reset an affected existing
scenario to `untested` when the diff changes its promise. Link open bugs and preserve the latest
report path and evidence according to the schema. Update journey maps when the route through the
product changed.

**Done when:** every affected scenario is new or reset to `untested`, and its journey, bug links,
and report references are internally consistent.

### 5. Write session charters

Create or update one charter per meaningful persona × journey × tour × time-box for this cycle.
Point each charter at its scenario and journey, state the public entry point, and define the
observable that proves success. Include the adjacent canary and prioritize changed or risky paths.

**Done when:** every affected scenario is covered by a dated, bounded charter with a persona,
journey, entry point, tour, time-box, and expected observable.

### 6. Hand off for execution

Summarize the scenario ids, charters, profile path, adapter candidates, and any missing prerequisite
for the next fresh Verifier. State that execution must use `qa-execute`, the project's existing
public interface, and the profile's declared adapter. End this skill before launching the product or
changing product code.

**Done when:** the handoff lists every affected scenario and charter, names the next Verifier
session, and contains no live execution result or product fix.
