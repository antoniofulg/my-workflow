# QA Skills Test Contract

## Unit

No unit cases. The feature changes agent-facing skill and workflow contracts rather than pure runtime
logic.

## Integration

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| IT-001 | Canonical QA skills are discoverable | Inspect `.agents/skills/qa-plan` and `.agents/skills/qa-execute` from the repository root | Both directories contain valid model-invoked `SKILL.md` metadata whose names match their directories |
| IT-002 | QA skill responsibilities remain separated | Inspect each skill's declared inputs, outputs, and completion criteria | QA Plan owns journeys, scenarios, and charters without live execution; QA Execute consumes that plan and owns live walks, reports, status, and defect hand-off |
| IT-003 | Every provider uses its existing Verifier | Inspect Cursor, Claude, and Codex verifier packets and workflow dispatch | All three dispatch the canonical QA skills; no additional reviewer role exists |
| IT-004 | QA schema has one durable authority | Inspect QA guidelines and skill context pointers | Skills and integration guidance point to `QA-SCENARIOS.md`; schema and status rules are not duplicated elsewhere |
| IT-005 | Repository provenance is explicit | Inspect `README.md` and both QA skills | README credits TLC and Pedro Nauck with source links; each QA skill identifies Antonio Fulgêncio as author and links its corresponding inspiration |
| IT-006 | Public scope is product-neutral | Inspect the README's project and scope sections | The reusable workflow is described without personal project names or product-specific stack choices |
| IT-007 | Deep Review output follows artifact policy | Evaluate `.gitignore` against generated and durable Deep Review paths | Generated `.deep-review/` contents are ignored and `.deep-review/learnings.md` is not ignored |
| IT-008 | Skill metadata passes the authoring contract | Run the writing-skills metadata validator for both skill names and descriptions | Both validations exit 0 |
| IT-009 | Repository gate remains green offline | Run `npm_config_offline=true npm test` from the repository root | The canonical suite exits 0 with no failed or skipped tests |
| IT-010 | Setup prompts discover stack capabilities safely | Inspect both suggested adoption prompts | Each requires read-only discovery, names every operational capability, preserves product-owned docs, exposes managed-path replacement, and requests diff plus gate evidence |
| IT-011 | Operational profile is canonical | Inspect the QA skills, QA guidance, and `docs/qa/README.md` template | Stack-specific QA capabilities have one durable home and command facts point to executable manifests or CI rather than being copied |
| IT-012 | Tool selection remains stack-agnostic | Inspect QA Execute's adapter-selection contract | Existing project tooling is preferred; browser, API, CLI, mobile, and manual paths are supported; missing tooling does not trigger automatic installation or invented commands |
| IT-013 | Verifier evidence identifies the adapter | Inspect all provider Verifier packets and QA Execute's completion criteria | QA output includes the selected interface/runner, exact execution path, evidence, and limitations without replacing the technical gate |
| IT-014 | Feature planning state is ignored selectively | Evaluate Git ignore behaviour for feature specs and durable `.specs` files | `.specs/features/qa-skills/spec.md` is ignored while `.specs/STATE.md` and `.specs/AD-INDEX.md` remain eligible for tracking |
| IT-015 | Task commits no longer depend on tracked specs | Inspect workflow instructions and commit validation against a current local `tasks.md` absent from the commit tree | The task gate can validate current local state without requiring disposable planning files in the commit |
| IT-016 | Historical disposable specs leave the tree | Inspect tracked files under `.specs/features/` after implementation | No disposable feature planning or validation artifact remains tracked |
| IT-017 | Package version is consistent | Inspect `package.json`, the lockfile root package, and installed package metadata when present | Every package-owned version reports `0.3.0` |

## End-to-end

No automated end-to-end case. The repository has no deterministic agent-execution harness; the
Verifier performs the documented QA sessions through the consuming product's public interfaces.

## Security

No security cases. This feature changes documentation and agent instructions without adding a
security surface.
