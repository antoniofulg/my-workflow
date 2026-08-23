# CH-spec-anchored-qa-contracts-2026-08-22

- **Date:** 2026-08-22
- **Time-box:** 15 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** QA contract consistency with documentation canary
- **Public entry point:** `docs/guidelines/QA-EXECUTION.md`
- **Adapter candidate:** Manual repository inspection
- **Scenarios:** `QAS-enforce-spec-anchored-qa-contracts`, `DOC-read-explicit-workflow-provenance`

## Mission

Follow the public QA planning contract and confirm that each cycle creates an immutable charter,
every planned test remains anchored to a spec acceptance criterion, and public filed-issue fixes
still trigger QA without making internal fixes do so.

## Expected observable

The workflow gives one consistent instruction across its QA skill and guidelines: create a new dated
charter per cycle, clarify the spec before adding an otherwise unmapped test case, and flag and walk
only filed-issue fixes that change a public promise.

## Planned probes

- Compare charter lifecycle wording in `docs/guidelines/QA-EXECUTION.md`,
  `docs/guidelines/QA-SCENARIOS.md`, and `.agents/skills/qa-plan/SKILL.md`.
- Confirm `docs/guidelines/TEST-CONTRACT.md` maps every case to an acceptance criterion and uses
  components, boundaries, and journeys only to reveal missing criteria.
- Confirm `docs/guidelines/REVIEW-ROUNDS.md` flags and walks user-visible filed-issue fixes while
  leaving internal fixes on technical verification only.
- Re-read `README.md` provenance as the adjacent `J-review-workflow-release` canary without changing
  its scenario promise.

End before live execution or defect remediation.
