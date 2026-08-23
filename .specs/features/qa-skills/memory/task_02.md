# Task 02 memory

- Added canonical `.agents/skills/qa-plan/` and `.agents/skills/qa-execute/` packages with only
  `SKILL.md` plus flat disclosed references.
- Both skills are model-invoked, authored by Antonio Fulgêncio, and carry one direct Pedro Nauck
  inspiration link each.
- `docs/guidelines/QA-SCENARIOS.md` remains the authority for scenario fields, ids, and statuses;
  the skills point to it instead of copying its schema.
- QA Execute records adapter/path/evidence/limitations and routes product defects to an Implementer
  followed by a fresh Verifier.
- Required metadata validator passed for both skills. The optional `skill-creator` quick validator
  could not run because Python `yaml` is unavailable.
- T2 remediation strengthens the no-runner fallback, evidence contract, Implementer/fresh-Verifier
  fix loop, provenance checks, and initial-frontmatter parsing in the scoped test.
- Final T2 remediation requires a disposition for every changed criterion and places journey,
  scenario, and charter outputs explicitly under `docs/qa/`.
