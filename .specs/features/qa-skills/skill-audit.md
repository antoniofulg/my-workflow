# T2 skill audit

Audit date: 2026-08-20

The `writing-skills` checklist was applied independently to
`.agents/skills/qa-plan/` and `.agents/skills/qa-execute/`. Every item is marked Pass. The
`skill-creator` quick validator was attempted but could not start because the environment lacks its
optional `yaml` Python module; the required writing-skills metadata validator passed for both skills.

## `qa-plan`

### Part A — Doctrine

- [Pass] Invocation earned: model invocation is required for Verifier discovery and provider routing.
- [Pass] Leading word front-loaded: the description opens with `Plan`.
- [Pass] One trigger per branch: changed user-facing surface/adoption is one planning branch; live walks, fixes, and framework selection are distinct exclusions.
- [Pass] Triggers only: the description contains capability and routing triggers, not body identity.
- [Pass] Content typed: the entrypoint contains ordered planning steps and reference sections; profile detail is disclosed.
- [Pass] Completion criteria: every numbered step ends with a checkable `Done when:` bound covering all affected promises or records.
- [Pass] Disclosure by branch: profile discovery is disclosed because it applies only when the operational profile is missing or incomplete.
- [Pass] Pointers worded for when: profile pointers explicitly say when to read the reference and when to read it in full.
- [Pass] Co-location: scope, QA context, mapping, flagging, charters, and handoff rules stay with their respective steps.
- [Pass] Single source of truth: scenario schema and status rules point to `QA-SCENARIOS.md`; the skill does not reproduce that schema.
- [Pass] Relevance: every entrypoint and profile-reference line changes planning behaviour or points to an owned authority.
- [Pass] No-op hunt: generic advice was removed; remaining instructions constrain discovery, mapping, reset, charter, and handoff decisions.
- [Pass] Negation: boundaries are paired with the positive owner (`qa-execute`, the next Verifier, or the Implementer).
- [Pass] Leading words: `scope`, `profile`, `promise`, `flag`, `charter`, and `handoff` anchor the procedure without repeated quality prose.

### Part B — agentskills.io

- [Pass] Naming: `name: qa-plan` is valid and matches the directory.
- [Pass] Description length: the description is below 1,024 characters.
- [Pass] Trigger coverage: the description includes `Use when` and `Don't use for` branches.
- [Pass] Third-person tone: metadata has no first- or second-person pronouns.
- [Pass] Standard folders, flat: only `references/` is used, one level deep.
- [Pass] No human docs: the package contains `SKILL.md` and agent-facing references only.
- [Pass] Forward slashes: all referenced paths use `/`.
- [Pass] Explicit helper paths: no bundled helpers exist; no helper path is needed.
- [Pass] No orphans: `references/profile.md` is linked from the entrypoint at each applicable branch.
- [Pass] Lean body: `SKILL.md` is 98 lines, below the 500-line ceiling.
- [Pass] Imperative mood: procedure steps use imperative actions (`Read`, `Map`, `Create`, `Summarize`).
- [Pass] Domain-native terms: the skill uses the repository's QA, Verifier, scenario, journey, charter, and adapter vocabulary.
- [Pass] CLI design: no scripts are bundled, so no CLI contract is needed.
- [Pass] Helper roles: no helpers are bundled or referenced.
- [Pass] Failure states: no visible surface, missing profile, duplicate coverage, and incomplete handoff each have recovery or stop behaviour.

## `qa-execute`

### Part A — Doctrine

- [Pass] Invocation earned: model invocation is required for independent Verifier discovery and provider routing.
- [Pass] Leading word front-loaded: the description opens with `Execute`.
- [Pass] One trigger per branch: walking a current plan is the positive branch; planning, product fixes, and framework installation are distinct exclusions.
- [Pass] Triggers only: the description contains capability and routing triggers, not body identity.
- [Pass] Content typed: the entrypoint contains ordered execution steps and disclosed protocol/fix references.
- [Pass] Completion criteria: every numbered step ends with a checkable `Done when:` bound covering all charters, surfaces, findings, and report rows.
- [Pass] Disclosure by branch: session protocol is required before any walk; fix-loop detail is disclosed only when a product defect appears.
- [Pass] Pointers worded for when: both pointers name their trigger and explicitly require reading the session protocol or fix loop in full.
- [Pass] Co-location: preflight, adapter, report, walk, probes, findings, and close rules remain grouped by execution stage.
- [Pass] Single source of truth: scenario schema/status rules point to `QA-SCENARIOS.md`; adapter facts point to `docs/qa/README.md`.
- [Pass] Relevance: every line constrains adapter choice, evidence, status, defect handoff, or report closure.
- [Pass] No-op hunt: generic QA encouragement was removed; instructions retain independent confirmation, evidence, cleanup, and fresh verification.
- [Pass] Negation: product-fix and tooling boundaries are paired with the positive Implementer, Verifier, profile, and existing-adapter paths.
- [Pass] Leading words: `preflight`, `adapter`, `report`, `walk`, `probe`, `finding`, and `resume` anchor the procedure.

### Part B — agentskills.io

- [Pass] Naming: `name: qa-execute` is valid and matches the directory.
- [Pass] Description length: the description is below 1,024 characters.
- [Pass] Trigger coverage: the description includes `Use when` and `Don't use for` branches.
- [Pass] Third-person tone: metadata has no first- or second-person pronouns.
- [Pass] Standard folders, flat: only `references/` is used, one level deep.
- [Pass] No human docs: the package contains `SKILL.md` and agent-facing references only.
- [Pass] Forward slashes: all referenced paths use `/`.
- [Pass] Explicit helper paths: no bundled helpers exist; no helper path is needed.
- [Pass] No orphans: `references/session-protocol.md` and `references/fix-loop.md` are linked from the entrypoint at their trigger points.
- [Pass] Lean body: `SKILL.md` is 105 lines, below the 500-line ceiling.
- [Pass] Imperative mood: procedure steps use imperative actions (`Read`, `Confirm`, `Choose`, `Create`, `Adopt`, `Run`, `Deduplicate`).
- [Pass] Domain-native terms: the skill uses the repository's QA, Verifier, scenario, journey, charter, adapter, evidence, and status vocabulary.
- [Pass] CLI design: no scripts are bundled, so no CLI contract is needed.
- [Pass] Helper roles: no helpers are bundled or referenced.
- [Pass] Failure states: missing runners, human-only legs, stalled flows, product defects, and pending rows have explicit status or recovery paths.

## Command evidence

| Check | Result |
| --- | --- |
| `validate-metadata.py --name qa-plan ...` | Pass; exit 0 |
| `validate-metadata.py --name qa-execute ...` | Pass; exit 0 |
| `npm_config_offline=true npx vitest run tools/shared/tests/qa-skills.test.ts` | Pass; 7 tests passed, 0 failed |
| `git diff --check` | Pass; exit 0 |

## T2 remediation evidence

- No-runner fallback: the skill selects the closest reachable public interface or manual adapter;
  only an unreachable product leg is `untested`.
- Execution boundary: the skill routes product defects to the Implementer, closes the current QA
  session, and requires a fresh Verifier to retest and resume the affected journey.
- Test sensors: IT-001 checks both corresponding Pedro Nauck links and provenance sections; IT-002
  checks adapter fallback, exact adapter/path/evidence/limitation reporting, tooling boundaries,
  defect handoff, fresh-Verifier resumption, and plan/execute separation; IT-008 rejects metadata
  outside initial frontmatter.
- Full offline gate: `npm_config_offline=true npm test` — 46 tests passed, 0 failed.
- Final T2 remediation: mixed-feature criterion dispositions are explicit, and durable QA outputs
  name `docs/qa/journeys/`, `docs/qa/scenarios/`, and `docs/qa/charters/`.
