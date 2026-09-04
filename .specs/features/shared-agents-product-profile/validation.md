# Shared Agents and Selective Product Context Validation

**Verdict:** PASS
**Date:** 2026-09-04
**Spec:** `.specs/features/shared-agents-product-profile/spec.md`
**Approved plan:** `.specs/features/shared-agents-product-profile/plan.md`
**Diff range:** `fa080e53641247573caf9f7b64a0b93e5e556481..2d564cf688fe5a330ced90a05148ace8ecfdd49c`
**Verifier:** independent final technical verifier (author != verifier)

## Acceptance evidence

| Obligation | Evidence | Result |
| --- | --- | --- |
| Neutral missing-index initialization | `scripts/test_adopt.py:714-737` asserts template bytes, absence of source-pack identity, consumer ownership, and no installed-byte hash. | PASS |
| Existing profile preservation and re-adoption | `scripts/test_adopt.py:739-744` writes two distinct consumer markers, reapplies core, and asserts byte preservation. | PASS |
| Symlink-safe profile destination | `scripts/test_adopt.py:750-760` asserts a symlinked parent aborts before target or referent mutation. | PASS |
| Shared product-neutral AGENTS entry point | `AGENTS.md:7-9` routes product-specific work through the index; `templates/adoption/agents/core.md:5-17` defines task-over-role selection. `scripts/test_adopt.py:721-727` applies core to two projects, compares AGENTS bytes, asserts the product-context pointer, and rejects the old stencil. | PASS |
| Fresh role and reviewer pointers | `tools/test_phase_skills.py:281-299` asserts every provider/role template exposes the index and role/task routing; `tools/shared/tests/qa-skills.test.ts:886-887` independently checks all generated role sources. | PASS |
| Packet pointer, unchanged schema, and budgets | `tools/test_workflow_spec_driven.py:87-114` rejects added fields and asserts the new product-context section; `tools/test_workflow_spec_driven.py:116-151` retains exact 3,072-byte role and 10,240-byte slice boundaries. | PASS |
| Designer constraints, selective references, read-only reuse, scaled alternatives, and bounded iteration | `tools/test_phase_skills.py:509-518` asserts the canonical UI procedure; `tools/test_phase_skills.py:521-565` asserts all Designer templates allow affected-component read-only inspection and carry the bounded alternatives procedure. | PASS |
| Human manual QA is never inferred | `docs/guidelines/UI-UX.md:81-85` requires human confirmation; `tools/test_phase_skills.py:518` asserts that contract. | PASS |
| Proportional doc/instruction/mixed-change validation overrides blanket gates | `docs/guidelines/GATES.md:11-16` defines the classifier. `.agents/skills/wtasks/SKILL.md:110-127`, `.agents/skills/wtasks/references/tasks-template.md:164-171`, and `docs/adoption-prompt.md:53-60` now route through it without automatic full/all-test or QA expansion. | PASS |
| Scope and authority preserved | The diff changes only workflow/adoption/spec/test assets. `.specs/features/shared-agents-product-profile/spec.md:21-28` excludes CRM/Creatista migration, remote authority, and release changes; no CRM/Creatista product checkout, release action, or remote action appears in the diff. | PASS |

## Resolved finding history

Correction commit `2d564cf688fe5a330ced90a05148ace8ecfdd49c` resolves all four prior findings:

1. **Resolved:** `.specs/features/shared-agents-product-profile/spec.md:24` now scopes only QA/review execution beyond proportional selection out, and `spec.md:81-82,111-112` adds traceable Designer and proportional-validation criteria.
2. **Resolved:** `docs/adoption-prompt.md:53-60` treats the full gate as a candidate, applies `GATES.md`, and dispatches QA only when the classifier selects a public walk.
3. **Resolved:** `.agents/skills/wtasks/SKILL.md:110-127` and `.agents/skills/wtasks/references/tasks-template.md:164-171` declare owning scoped gates and explicitly prohibit automatic all-tests expansion.
4. **Resolved:** `scripts/test_adopt.py:721-744` compares two fresh AGENTS files, asserts the pointer/no-stencil contract, and preserves distinct consumer profiles across re-adoption.

## Scoped checks

- Correction commit author evidence: `python3 scripts/test_adopt.py` -> 88 passed, 0 failed.
- Unchanged packet evidence reused: `python3 tools/test_workflow_spec_driven.py` -> 5 passed, 0 failed.
- Correction commit author evidence: `python3 tools/test_phase_skills.py` -> 19 passed, 0 failed.
- Correction commit author evidence: `bun test tools/shared/tests/qa-skills.test.ts tools/shared/tests/deep-review-installation.test.ts` -> 33 passed, 0 failed.
- Correction commit author evidence: `git diff --check` -> clean.

## Discrimination sensor

Lightweight isolated worktree mutation on pre-correction commit `a47c1b1a`: removed consumer-missing classification for `docs/product/AGENT-CONTEXT.md` at `scripts/adopt.py:316-317`. Targeted `test_product_context_is_neutral_missing_only_and_consumer_owned` failed at that commit's `scripts/test_adopt.py:724` (`record["ownership"] == "consumer"`). **1/1 mutant killed.** Real checkout status matched the clean pre-sensor baseline after cleanup.

## Limitations

Per the approved plan, no full repository gate, deep review, QA Plan/Execute, live UI/product walk, or generic validator pipeline ran. This report does not claim measured LLM context savings, live-model reliability, release readiness, or remote-delivery readiness.
