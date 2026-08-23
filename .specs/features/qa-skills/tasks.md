# QA Skills Tasks

## Test Coverage Matrix

| Requirements | Layer | Cases | Canonical suite |
| --- | --- | --- | --- |
| QA-19–QA-21, QA-12 | Integration | IT-007, IT-014–IT-016 | `tools/shared/tests/qa-skills.test.ts` |
| QA-01–QA-05, QA-09–QA-10 | Integration | IT-001, IT-002, IT-008 | `tools/shared/tests/qa-skills.test.ts` |
| QA-06–QA-07, QA-16 | Integration | IT-003, IT-004, IT-013 | `tools/shared/tests/qa-skills.test.ts` |
| QA-08, QA-11, QA-13–QA-15, QA-17–QA-18 | Integration | IT-005, IT-006, IT-010–IT-012 | `tools/shared/tests/qa-skills.test.ts` |
| QA-22 | Integration | IT-017 | `tools/shared/tests/qa-skills.test.ts` |
| All | Integration gate | IT-009 | `npm_config_offline=true npm test` |

No unit, automated end-to-end, or security cases apply. The final QA Plan and QA Execute sessions
exercise the agent-facing journey manually through the repository's public adoption surface.

## Gate Check Commands

- Scoped structural suite: `npm_config_offline=true npx vitest run tools/shared/tests/qa-skills.test.ts`
- Metadata: `python3 <writing-skills-dir>/scripts/validate-metadata.py --name <name> --description <description>`
- Spec: `python3 .agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/qa-skills/spec.md --strict`
- Tasks: `python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/qa-skills/tasks.md`
- Full gate: `npm_config_offline=true npm test`
- Decision index: `python3 tools/ad-index.py`

## Execution Plan

Run tasks in order. Each implementation task receives a fresh Implementer, closes its scoped gate,
creates one Conventional Commit, then receives a fresh Verifier and Deep Review before the next task.
Task 05 and Task 06 are fresh Verifier sessions invoking the completed QA skills. Task 06 is the last
slice and writes no product or workflow code.

## Task Breakdown

### T1: Make feature planning local

**Status:** complete

**Observable behaviour:** Feature planning and Deep Review run output stay out of Git while durable
decisions and learnings remain eligible for tracking.

**Where:** `.gitignore`, `AGENTS.md`, `.specs/STATE.md`, `.specs/AD-INDEX.md`, relevant lifecycle and
workflow guidelines, tracked `.specs/features/` cleanup, `tools/shared/tests/qa-skills.test.ts`.

**Depends on:** None.

**Tests:** IT-007, IT-014, IT-015, IT-016.

**Gate:** Run the scoped structural suite, `python3 tools/ad-index.py`, task/spec validators by explicit
path, and `git diff --check`. Commit `docs(workflow): keep feature planning local`.

### T2: Add canonical QA skills

**Status:** complete

**Observable behaviour:** Agents discover distinct, model-invoked `qa-plan` and `qa-execute` skills
with deterministic procedures, completion criteria, and explicit provenance.

**Where:** `.agents/skills/qa-plan/**`, `.agents/skills/qa-execute/**`,
`tools/shared/tests/qa-skills.test.ts`.

**Depends on:** Task 01.

**Tests:** IT-001, IT-002, IT-008.

**Gate:** Run both writing-skills metadata validations, the written writing-skills checklist audit for
each skill, the scoped structural suite, and `git diff --check`. Commit
`feat(qa): add planning and execution skills`.

### T3: Dispatch QA through the Verifier

**Status:** complete

**Evidence:** `npm_config_offline=true npx vitest run tools/shared/tests/qa-skills.test.ts` — 10 passed;
provider parity, guideline-size, and `git diff --check` checks passed.

**Observable behaviour:** Cursor, Claude, and Codex use their existing Verifier for technical review,
QA Plan, and QA Execute in independent sessions, with QA schema remaining authoritative in one place.

**Where:** provider `verifier` packets, `docs/guidelines/QA-EXECUTION.md`,
`docs/guidelines/QA-SCENARIOS.md` only where a pointer changes, `docs/guidelines/REVIEW-ROUNDS.md`,
workflow loop/review docs, `tools/shared/tests/qa-skills.test.ts`.

**Depends on:** Task 02.

**Tests:** IT-003, IT-004, IT-013.

**Gate:** Run the scoped structural suite, provider parity checks, guideline size checks, and
`git diff --check`. Commit `docs(qa): dispatch QA through verifier skills`.

### T4: Adapt setup and public prompts

**Status:** complete

**Evidence:** `npm_config_offline=true npm test` — 55 passed; `python3 scripts/test_adopt.py` — ok;
both skill metadata validators passed; spec/tasks validators passed with existing warnings; `git diff
--check` passed.

**Observable behaviour:** One safe suggested prompt discovers the consuming stack, records its QA
profile, adopts both skills, preserves product-owned material, and reports reviewable evidence; the
README is neutral and carries explicit credits.

**Where:** `README.md`, `docs/qa/README.md`, `scripts/adopt.py`, adoption/workflow docs,
`package.json`, `package-lock.json`, `tools/shared/tests/qa-skills.test.ts`.

**Depends on:** Task 03.

**Tests:** IT-005, IT-006, IT-009, IT-010, IT-011, IT-012, IT-017.

**Gate:** Run adopt-script tests or a disposable adoption smoke test, the scoped structural suite,
the full offline gate, and `git diff --check`. Commit `feat(setup): discover consuming QA stack`.

### T5: Plan the QA session

**Status:** complete

**Evidence:** `npm_config_offline=true npx vitest run tools/shared/tests/qa-skills.test.ts` — 16
passed; scenario schema check — 5 valid `untested` scenarios; `git diff --check` passed.

**Observable behaviour:** A fresh Verifier invokes `qa-plan` and records the affected adoption and QA
journeys, scenarios, and session charter under `docs/qa/`.

**Where:** Durable `docs/qa/` artifacts only.

**Depends on:** Task 04 and its closed review rounds.

**Tests:** Manual QA Plan mapping against QA-01–QA-21; no automated case is owned by this task.

**Gate:** Validate scenario/charter schema and `git diff --check`. Commit
`docs(qa): plan QA skills adoption session` if durable artifacts change.

### T6: Execute the final QA session

**Status:** complete

**Evidence:** both dated charters and all 10 probes passed through the declared CLI/manual adapter;
all 5 scenarios are `pass`; `npm_config_offline=true npm test` — 55 passed; no product defects.

**Observable behaviour:** A different fresh Verifier invokes `qa-execute`, walks the adoption and
skill-discovery journeys, records terminal statuses, and publishes a dated durable report.

**Where:** Durable `docs/qa/` statuses, bugs, and reports only; raw evidence remains ignored.

**Depends on:** Task 05.

**Tests:** Manual execution of every charter from Task 05; no automated case is owned by this task.

**Gate:** Every flagged scenario is `pass` or `blocked-verify`, the final offline gate is current for
the exact tree, and `git diff --check` passes. Commit `docs(qa): record QA skills session` if durable
artifacts change.
