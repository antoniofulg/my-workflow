# Phase Skills Specification

Size: Large. Ticket: none (roadmap slice 1, `docs/workflow/roadmap.md`).

## Problem Statement

Every role loads the whole `workflow-spec-driven` skill (200 lines of router plus the reference it
needs) even when it runs one phase. Skills are loaded by prose ("Load skill X"), so no role can be
scoped to its own knowledge, and the main chat auto-loads the router whenever a trigger word
appears. Planning several features in one sitting stacks that context. Splitting each phase into its
own skill, preloaded per agent, is the precondition for forked entry points, a cheap qualifier role,
and per-role model choice.

## Goals

- [ ] Each phase (Specify, Design, Tasks, Implement, Verify) is one skill an agent can preload alone.
- [ ] The router shrinks to sizing, phase chain, `.specs` layout, critical rules, and resume.
- [ ] Claude agents declare their skills in frontmatter; narrow roles cannot invoke other skills.
- [ ] No instruction text is duplicated between the router and a phase skill.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Forked slash entry points (`context: fork`, `agent:`) | Roadmap slice 2; needs the skills to exist first |
| Renaming the `workflow-spec-driven` directory | About 90 references incl. lock files, adopt catalog, QA docs, history; no behaviour gain |
| Moving `scripts/*.py` out of the router | Adopted gate paths and tests already cite `.agents/skills/workflow-spec-driven/scripts/`; moving buys nothing |
| `skills:` frontmatter for Cursor and Codex packets | Provider support unverified; bodies keep the prose load line |
| Qualifier, designer, Linear, global config | Later roadmap slices |
| Changing any phase's procedure | This slice moves text; it does not rewrite rules |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Phase skill names | `wspecify`, `wdesign`, `wtasks`, `wimplement`, `wverify` | `design` collides with the global Claude Design skill; `/w` prefix lists the phases in the slash menu | y |
| What a phase SKILL.md carries | The phase procedure itself, not a pointer | Preload injects SKILL.md only; a pointer would make preload worthless | y |
| Where templates go | `references/` inside the phase skill (spec template, tasks template, validation report template) | Read on demand when writing the artifact; keeps SKILL.md under the cap | y |
| `discuss.md` home | `wspecify/references/discuss.md` | Discuss is triggered inside Specify only | y |
| Shared references | `lessons.md`, `memory.md`, `sub-agents.md`, `code-analysis.md`, `coding-principles.md` stay in the router | Used by more than one phase or by the coordinator | y |
| Which roles lose the `Skill` tool | implementer, explorer, deep-reviewer via `disallowedTools: Skill` | They receive a packet and one preloaded skill; planner pulls design on demand; verifier invokes `qa-plan` or `qa-execute` per packet | y |
| Hidden from auto-invocation | All five phase skills set `disable-model-invocation: true` | The main chat enters a phase explicitly; agents preload | y |
| Lock files | No new entries in `skills-lock.json` or `.agents/.skill-lock.json` | Those pin externally sourced skills; the new ones are workflow-owned | y |
| SKILL.md cap | 200 lines per phase skill; router under 150 | Context reduction is the goal; measured with `wc -l` | y |

**Open questions:** none - all resolved or logged above.

---

## Impact

- `.agents/skills/workflow-config/scripts/workflow_config.py`: sync copies templates verbatim except
  model and effort, so `skills:` and `disallowedTools:` pass through. Gains one check (PSK-03 AC 4).
- `scripts/adopt.py` `CORE_PATHS`: gains five skill directories; `scripts/test_adopt.py` catalog tests.
- `.agents/skills/autonomous/SKILL.md` and `references/parallelization.md` cite `workflow-spec-driven`;
  unchanged because the router keeps its name.
- `tools/test_tlc_validators.py`, `test_workflow_spec_driven.py`, `test_review_convergence.py`,
  `test_parallel_plan.py` import router scripts by path; unchanged because scripts do not move.
- `docs/workflow/pack.md` skill table, `README.md` skill mentions, `AGENTS.md` role line,
  `templates/agents/*` bodies: renamed load lines.
- `docs/qa/scenarios/ADP-*` adoption scenarios: managed path list changes; QA Plan decides.

---

## User Stories

### P1: Phase skills carry their procedure ⭐ MVP

**User Story**: As a role agent, I want the phase I run to be one skill, so that I preload exactly
that procedure and nothing else.

**Why P1**: Nothing else in the roadmap works without it.

**Acceptance Criteria**:

1. The repository SHALL contain `.agents/skills/<name>/SKILL.md` for each of `wspecify`, `wdesign`, `wtasks`, `wimplement`, `wverify`, each with frontmatter `name` equal to its directory and `disable-model-invocation: true`.
2. The phase SKILL.md SHALL contain the procedure sections of the reference it replaces (`specify.md`, `design.md`, `tasks.md`, `implement.md`, `validate.md`) and SHALL be at most 200 lines.
3. WHEN a phase writes an artifact from a template THEN the template SHALL live under that skill's `references/` and the SKILL.md SHALL name it by relative path.
4. WHEN a phase runs a validator THEN the SKILL.md SHALL cite it as `.agents/skills/workflow-spec-driven/scripts/<name>.py` with `--root` semantics unchanged.
5. The five references above SHALL no longer exist under `workflow-spec-driven/references/`, and the sum of lines across each phase skill (SKILL.md plus its references) SHALL not exceed the line count of the reference it replaced plus ten lines for frontmatter and headings.
6. The skill tree SHALL keep `discuss.md` at `wspecify/references/discuss.md`, and `lessons.md`, `memory.md`, `sub-agents.md`, `code-analysis.md`, `coding-principles.md` SHALL stay in the router.

**Independent Test**: `wc -l .agents/skills/w*/SKILL.md` shows five files at or under 200
lines; `ls .agents/skills/workflow-spec-driven/references/` lists only the five shared files.

---

### P1: Router shrinks to dispatch

**User Story**: As the planner, I want the router to tell me which skill runs which phase at which
size, so that I open one phase skill and never the whole workflow.

**Why P1**: Without it the router and the phase skills say the same thing twice.

**Acceptance Criteria**:

1. The router `workflow-spec-driven/SKILL.md` SHALL keep Critical Rules, Auto-Sizing, `.specs` Structure, Workflow (new and resume), and Knowledge Verification Chain, and SHALL be at most 150 lines.
2. The Auto-Sizing table SHALL name the phase skill for each phase column instead of a reference file.
3. The router SHALL NOT contain the Commands table, the Context Loading Strategy section, or the Coordinator-assisted dispatch section; the dispatch text SHALL live in `references/sub-agents.md` and the loading ceiling in each phase skill that uses it.
4. WHEN the router mentions a phase THEN it SHALL name the skill (`w<phase>`) and SHALL NOT link a `references/<phase>.md` path.

**Independent Test**: `grep -c 'references/specify.md\|references/implement.md' SKILL.md` returns 0
and `wc -l` is at most 150.

---

### P1: Agents preload their skills

**User Story**: As the coordinator, I want each Claude agent to declare its skills in frontmatter and
narrow roles to lack the `Skill` tool, so that a role sees only its own knowledge.

**Why P1**: This is the scoping mechanism the roadmap rests on.

**Acceptance Criteria**:

1. The template `templates/agents/claude/planner.md` SHALL declare `skills: [workflow-spec-driven, wspecify, wtasks, ponytail]` and SHALL NOT set `disallowedTools`.
2. The template `templates/agents/claude/implementer.md` SHALL declare `skills: [wimplement, ponytail]` and `disallowedTools: Skill`; `explorer.md` and `deep-reviewer.md` SHALL declare `disallowedTools: Skill` and keep their tool lists; `verifier.md` SHALL declare `skills: [wverify]` and SHALL NOT set `disallowedTools`.
3. WHEN `workflow_config.py --sync-agents` renders a Claude template THEN the generated `.claude/agents/<role>.md` SHALL contain the `skills:` and `disallowedTools:` lines byte-identical to the template, with only `model` and `effort` replaced.
4. IF a Claude template names a skill in `skills:` with no `.agents/skills/<name>/SKILL.md` THEN `--sync-agents` SHALL exit non-zero naming the template and the skill, and SHALL write nothing.
5. The Cursor and Codex templates for planner, implementer, and verifier SHALL name the phase skills in their `## Load` prose and SHALL NOT name `implement.md`, `validate.md`, or another reference file.
6. The templates SHALL name, on every "Load" or "Do not load" line, a skill or a guideline path that exists in the repository.

**Independent Test**: run sync on a temp copy of the repo; diff generated implementer against its
template shows only the model and effort lines.

---

### P2: Skills are discoverable and adoptable

**User Story**: As a consuming project, I want the phase skills to install with the core layer and
resolve for Claude, so that adoption keeps working.

**Why P2**: Adoption is exercised less often than dispatch, but it breaks silently.

**Acceptance Criteria**:

1. The checkout SHALL track `.claude/skills/<name>` as a git-tracked symlink to `../../.agents/skills/<name>` for each phase skill.
2. The adopt catalog `scripts/adopt.py` `CORE_PATHS` SHALL include the five phase skill directories, and `adopt.py plan --layers core` SHALL list them as managed.
3. The docs SHALL list the phase skills with the router in the `docs/workflow/pack.md` skill table, and state in `docs/workflow/roadmap.md` that a phase SKILL.md carries its procedure under 200 lines.
4. The file `AGENTS.md` SHALL keep its line count at or below its current count.

**Independent Test**: `python3 scripts/adopt.py plan <tmp> --layers core --json` output contains
`.agents/skills/wimplement`.

---

## Edge Cases

- IF a phase SKILL.md exceeds 200 lines after the move THEN the implementer SHALL move template or
  example text to `references/`, never delete a rule.
- IF two templates disagree on a skill name THEN the contract test SHALL fail naming both files.
- WHEN `.claude/skills/<name>` already exists as a directory instead of a symlink THEN sync SHALL
  leave it and the contract test SHALL fail.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| PSK-01 | P1: Phase skills carry their procedure | Design | Pending |
| PSK-02 | P1: Router shrinks to dispatch | Design | Pending |
| PSK-03 | P1: Agents preload their skills | Design | Pending |
| PSK-04 | P2: Skills are discoverable and adoptable | Design | Pending |

**Coverage:** 4 total, 0 mapped to tasks, 4 unmapped ⚠️

---

## Success Criteria

- [ ] An implementer dispatched with the new template has `wimplement` and `ponytail` in
      context and no `Skill` tool, verified by asking it to list its tools.
- [ ] Planner context at Specify drops from router plus reference to router plus one phase skill,
      measured by `wc -l` on the loaded files.
