# W Entry Points Specification

Size: Medium. Ticket: none (roadmap slice 2, `docs/workflow/roadmap.md`). Delegated roles run on Cursor.

## Problem Statement

The phase skills exist and preload into their agents, but a human still enters a phase by talking to
the main chat, which then carries every phase's transcript. There is no way to run Specify for
feature A, then feature B, each in a fresh agent, from one terminal. Deep review and QA have no
`/w` entry at all, so `/w` does not yet list the workflow.

## Goals

- [ ] `/wspecify`, `/wdesign`, `/wtasks`, `/wimplement`, `/wverify` each run their phase inside a fresh agent of the right role and return only that agent's summary.
- [ ] `/wreview` and `/wqa` wrap the existing `deep-review` and QA skills the same way.
- [ ] Preload keeps working: a spawned implementer still has `wimplement` and `ponytail`, no `Skill` tool.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Renaming `deep-review`, `qa-plan`, `qa-execute` | Entry points wrap them; renames touch the adopt catalog, three suites, and QA docs |
| `wqualify` and the qualifier role | Roadmap slice 6 |
| Fixing the Orca route's `--model "<m>[effort=<e>]"` for Cursor | Filed as a QA bug in this slice; the Orca transport is `blocked-verify` |
| Cursor or Codex slash equivalents | Cursor reads `.cursor/` commands differently; unverified |
| Background forks | `background: true` narrows the tool set; phases need the full set |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Where the fork lives | On the phase skill itself: `context: fork`, `agent: <role>`, `argument-hint`, `background: false`; body gains one leading line that binds `$ARGUMENTS` to the feature or slice | Fewest files; one name per phase in the `/w` menu | y |
| Fallback if fork breaks preload | Rename phase skills to `phase-<x>` with `user-invocable: false`, and create thin `w<x>` entry skills | Docs do not state whether `context: fork` and `skills:` preload coexist; a probe after the first task decides | y |
| Agent per entry | `wspecify`, `wdesign`, `wtasks` → `planner`; `wimplement` → `implementer`; `wverify`, `wqa` → `verifier`; `wreview` → `planner` (needs the Agent tool to dispatch `deep-reviewer` jobs) | Matches the roles that preload each phase | y |
| `wreview` and `wqa` bodies | Short: name the wrapped skill, pass `$ARGUMENTS`, state "read `<skill>/SKILL.md` in full and follow it"; `wqa` takes `[plan] <flow>` and runs exactly one QA phase | Subagents may lack the Skill tool; reading the file always works | y |
| `/w` menu | Exactly seven user-invocable entries; phase skills stay model-invocable for preload | The user types `/w` to see the workflow | y |
| Cursor model ids for dispatch | `<toml model>-<toml effort>` (`gpt-5.6-luna-high`, `cursor-grok-4.6-high`) | `cursor-agent --list-models` shows effort inside the id and rejects `[effort=]` | y |

**Open questions:** none - all resolved or logged above.

---

## Impact

- `.agents/skills/w*/SKILL.md` frontmatter: five files gain fork keys; UT-001 in `tools/test_phase_skills.py` grows.
- `tools/test_phase_skills.py` `PHASES` may gain `wreview` and `wqa` as entry-only skills with a different contract (no 200-line procedure, no references).
- `scripts/adopt.py` `CORE_PATHS`: two new skill directories; `scripts/test_adopt.py` frozen inventory.
- `docs/workflow/pack.md` skill table, `docs/workflow/roadmap.md` slice 2 line.
- `tools/orca_assisted_probe.py:377` Cursor route string: not changed; bug filed under `docs/qa/bugs/`.
- QA scenarios `QAS-resolve-phase-skill-procedures` and `ADP-install-phase-skills` cover changed promises; QA Plan decides resets.

---

## User Stories

### P1: A phase runs in a fresh agent from one command ⭐ MVP

**User Story**: As the human at the terminal, I want `/wspecify <feature>` to run Specify inside a fresh planner and hand me only its summary, so that I can plan several features in a row without stacking their transcripts.

**Why P1**: The birthday-afternoon use case rests on it.

**Acceptance Criteria**:

1. The five phase skills SHALL carry `context: fork`, `agent:` set per the Assumptions table, `background: false`, and an `argument-hint` naming the feature or slice argument.
2. WHEN a user invokes `/w<phase> <args>` THEN the forked agent SHALL receive the skill body with `$ARGUMENTS` bound and SHALL start with no main-conversation history.
3. WHEN the forked agent finishes THEN the main conversation SHALL receive only its final message.
4. The phase skills SHALL stay listed as preloads in the Claude templates, and a spawned implementer SHALL still have `wimplement` and `ponytail` in context with no `Skill` tool.
5. IF the fork keys stop `skills:` preload from injecting a phase skill THEN the implementer SHALL switch to the fallback layout in the Assumptions table before continuing.

**Independent Test**: run `/wimplement` with a trivial argument and observe one summary in the main chat; spawn an implementer probe and see `# Execute` present.

---

### P1: Review and QA have entries

**User Story**: As the human, I want `/wreview` and `/wqa <flow>` in the same menu, so that a review or a QA walk of one flow is one command.

**Why P1**: The `/w` menu is incomplete without them, and `/wqa auth` is a stated need.

**Acceptance Criteria**:

1. The repository SHALL contain `.agents/skills/wreview/SKILL.md` and `.agents/skills/wqa/SKILL.md`, each under 40 lines, with `context: fork`, `background: false`, an `argument-hint`, and `agent:` per the Assumptions table.
2. WHEN `/wreview <args>` runs THEN the forked agent SHALL read `.agents/skills/deep-review/SKILL.md` in full and follow it with `<args>` as the review flags, publishing nothing.
3. WHEN `/wqa <flow>` runs THEN the forked verifier SHALL run exactly the `qa-execute` phase over the journeys tagged `<flow>`; WHEN `/wqa plan <flow>` runs THEN it SHALL run exactly the `qa-plan` phase.
4. The two entry skills SHALL be git-tracked symlinks under `.claude/skills/` and members of `CORE_PATHS`.

**Independent Test**: `python3 scripts/adopt.py plan <tmp> --layers core --json` lists both; `ls .claude/skills | grep -E '^w(specify|design|tasks|implement|verify|review|qa)$' | wc -l` shows 7.

---

### P2: The menu and docs match

**User Story**: As the human, I want `/w` to show exactly the seven workflow entries with one-line hints, so that the menu is the map.

**Why P2**: Usability, not correctness.

**Acceptance Criteria**:

1. The seven `w*` skills SHALL be user-invocable and SHALL each carry a `description` that starts with the phase name and states the argument.
2. The docs SHALL list the seven entries in `docs/workflow/pack.md` and mark roadmap slice 2 done in `docs/workflow/roadmap.md`.
3. The file `AGENTS.md` SHALL stay at or below 134 lines.

**Independent Test**: `grep -c '^description' .agents/skills/w*/SKILL.md` returns 7.

---

## Edge Cases

- IF `/w<phase>` is invoked with no argument THEN the forked agent SHALL stop and name the missing argument instead of guessing a feature.
- IF `/wqa` names a flow with no tagged journey THEN the verifier SHALL report that and stop instead of inventing scenarios.
- WHEN `/wreview` receives `--publish` THEN the forked agent SHALL refuse; publishing needs the user's explicit go-ahead in the main session.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| WEP-01 | P1: A phase runs in a fresh agent from one command | Execute | Pending |
| WEP-02 | P1: Review and QA have entries | Execute | Pending |
| WEP-03 | P2: The menu and docs match | Execute | Pending |

**Coverage:** 3 total, 0 mapped to tasks, 3 unmapped ⚠️

---

## Success Criteria

- [ ] From one terminal, `/wspecify a`, then `/wspecify b`, each return one summary and the main chat holds neither procedure transcript.
- [ ] The implementer probe after the change still shows `# Execute`, `# Ponytail`, and no `Skill` tool.
