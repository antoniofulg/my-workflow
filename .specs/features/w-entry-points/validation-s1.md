# W Entry Points Validation — Slice S1

**Date**: 2026-09-03
**Spec**: `.specs/features/w-entry-points/spec.md`
**Decisions**: `.specs/features/w-entry-points/decisions.md`
**Diff range**: `03e57240..5b10e1af` (`a24e351d`, `d18e4699`, `5b10e1af`). Checkout HEAD `5b10e1afa1dbfb9bf0bad4a0288fdc51a877a49c`, clean tree.
**Verifier**: independent sub-agent (author ≠ verifier). Read-only over the real tree. Mutations only in `/tmp/wep-s1-sensor`, then removed.
**Verdict**: PASS

---

## Task Completion

No `tasks.md` (Tasks skipped). Three commits match T1–T3.

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1 | ✅ Done | `a24e351d` — fork keys on the five phase skills; UT-001 grown |
| T2 | ✅ Done | `d18e4699` — `wreview` / `wqa`, symlinks, `CORE_PATHS`, UT-010, IT-003 |
| T3 | ✅ Done | `5b10e1af` — pack table, roadmap slice 2 `(done)`, bug file, UT-011 |

---

## Spec-Anchored Acceptance Criteria

### WEP-01 — A phase runs in a fresh agent from one command

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| AC1 five phase skills carry `context: fork`, `agent:` per Assumptions, `background: false`, `argument-hint` | exact keys; agents `planner`/`planner`/`planner`/`implementer`/`verifier`; hint names the feature or slice | `tools/test_phase_skills.py:122` `assert fields.get("context") == "fork"`; `:123` `assert fields.get("agent") == agent` via `PRELOADING_AGENT` `:27-33`; `:124` `assert fields.get("background") == "false"`; `:125` `assert fields.get("argument-hint") in ('"<feature-or-slice>"', "<feature-or-slice>")`; `:130-131` Bun `readFrontmatter` exit 0 | ✅ PASS |
| AC2 `/w<phase> <args>` binds `$ARGUMENTS` and starts with no main-conversation history | first body line binds `$ARGUMENTS`; `context: fork` requests a fresh agent | `tools/test_phase_skills.py:129` — `assert "$ARGUMENTS" in first_body_line`; `:122` fork key. Live no-history spawn was not in this packet | ⚠️ Spec-precision gap — repo contract asserted; live empty-history fork not observed here |
| AC3 forked agent finish returns only its final message to the main conversation | product fork return shape | no test assertion for "only the final message" | ⚠️ Spec-precision gap — host runtime; keys that request it are asserted in AC1 |
| AC4 phase skills stay listed as Claude preloads; spawned implementer still has `wimplement` and `ponytail`, no `Skill` tool | templates keep the lists; probe shows both skills and no Skill tool | `tools/test_phase_skills.py:240` — `assert fields.get("skills") == "[" + ", ".join(expected) + "]"` with `CLAUDE_PRELOAD` implementer `("wimplement", "ponytail")` at `:54`; `:244` `assert fields.get("disallowedTools") == "Skill"`. Probe file cited below | ✅ PASS |
| AC5 IF fork keys stop `skills:` preload THEN switch to the fallback (`phase-<x>` + thin `w<x>`) | fallback only when preload breaks | Probe shows `wimplement` present. IF is false; fallback not required | ✅ PASS (vacuous) |

**AC4 probe** (coordinator Claude spawn), path
`/private/tmp/claude-501/-Users-antoniofulg-Projects-my-workflow/56007cfc-7cef-4947-a9e8-0835b2fc4af7/scratchpad/probe-fork-preload.txt`, cited verbatim:

```
1. Skill tool present: no. (Tools: Agent, Artifact, Bash, Edit, Read, ToolSearch, Write + deferred list; no `Skill`.)
2. wimplement skill text: present before any tool call. First markdown heading: "# Execute". Literal `$ARGUMENTS` token in body: no — the line reads "Run this phase for: . If empty, stop and ask for the feature or slice.", i.e. already substituted with an empty value.
3. ponytail skill text: present. First heading: "# Ponytail".
```

`wimplement` is present. Fallback in spec Assumptions is not triggered.

### WEP-02 — Review and QA have entries

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| AC1 `.agents/skills/wreview/SKILL.md` and `wqa/SKILL.md` exist, each under 40 lines, fork keys, `agent:` per Assumptions | `wreview` → `planner`; `wqa` → `verifier`; `< 40` lines | `tools/test_phase_skills.py:294-302` — file exists; `context == "fork"`; `agent == agent`; `background == "false"`; `argument-hint` present; `assert count < 40`. Measured: wreview 16, wqa 14 | ✅ PASS |
| AC2 `/wreview <args>` reads `deep-review/SKILL.md` in full, follows it, publishing nothing; `--publish` refused | body names the wrap and rejects `--publish` | `.agents/skills/wreview/SKILL.md:14-16` — `When $ARGUMENTS includes `--publish`, reject it` and `never pass --publish`. No test locks those sentences | ⚠️ Spec-precision gap — instruction present; UT-010 does not assert the refuse line |
| AC3 `/wqa <flow>` runs only `qa-execute`; `/wqa plan <flow>` runs only `qa-plan`; missing tag → report and stop | exactly one QA phase; no invented journeys | `.agents/skills/wqa/SKILL.md:14` — `Run exactly one QA phase: qa-plan when the first argument is plan, else qa-execute` and `if no journey carries the tag, report and stop`. No test locks that sentence | ⚠️ Spec-precision gap — instruction present; UT-010 does not assert the one-phase / no-tag stop |
| AC4 both are git-tracked `.claude/skills/` symlinks and members of `CORE_PATHS` | mode `120000`, target `../../.agents/skills/<name>`, listed in core plan and frozen inventory | `tools/test_phase_skills.py:303-307` — symlink, target, resolves, `git ls-files`. `scripts/adopt.py:43` both paths in `CORE_PATHS`. `scripts/test_adopt.py:35` both in `FROZEN_PRE_FEATURE_PATHS`. `scripts/test_adopt.py:124-126` — `assert f".agents/skills/{name}/SKILL.md" in managed` and `assert f".claude/skills/{name}" in managed` for `wreview` and `wqa` | ✅ PASS |

### WEP-03 — The menu and docs match

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| AC1 seven `w*` skills user-invocable; each `description` starts with the phase name and states the argument | exactly those seven; not `disable-model-invocation: true`; description prefix | `tools/test_phase_skills.py:314-322` — `w_skill_dirs == set(ALL_W_SKILLS)`; `disable-model-invocation != "true"`; `description.startswith(f"{phase_prefix} phase")`. Argument text lives in `argument-hint` (UT-001 `:125`, UT-010 `:300`), not in the description string | ⚠️ Spec-precision gap — phase-name prefix asserted; "states the argument" is the hint, not the description |
| AC2 docs list the seven entries in `pack.md`; roadmap slice 2 marked done | seven `w*` rows; slice 2 `(done)` | `docs/workflow/pack.md:10-16` lists `wspecify` … `wqa`. `docs/workflow/roadmap.md:133` ends slice 2 with `(done)`. `tools/test_phase_skills.py:207-208` asserts pack rows only for the five `PHASES`, not `wreview`/`wqa` | ✅ PASS on the files; pack-row test does not cover the two new entries |
| AC3 `AGENTS.md` stays at or below 134 lines | `<= 134` | `tools/test_phase_skills.py:211-212` — `assert agents <= AGENTS_LINE_CAP` (`:45` = 134). Measured 134 | ✅ PASS |

**Status**: ⚠️ Spec-precision gaps flagged (runtime fork return shape, description-vs-hint, skill-body refuse/stop not test-locked). No AC failed on the implementation that this packet could inspect.

---

## Discrimination Sensor

Scratch: `git worktree add /tmp/wep-s1-sensor HEAD`. Real tree `git status --porcelain` empty before and after. Worktree removed with `git worktree remove --force`.

| Mutation | File:line | Description | Killed? |
| -------- | --------- | ----------- | ------- |
| 1 | `.agents/skills/wspecify/SKILL.md:5` | Dropped `context: fork` | ✅ Killed — `tools/test_phase_skills.py:122` `AssertionError: wspecify: context is None` (exit 1) |
| 2 | `.agents/skills/wqa/SKILL.md:6` | `agent: verifier` → `agent: planner` | ✅ Killed — `tools/test_phase_skills.py:298` `AssertionError: wqa: agent is 'planner'` (exit 1) |
| 3 | `.agents/skills/wreview/SKILL.md` | Padded to 76 lines | ✅ Killed — `tools/test_phase_skills.py:302` `AssertionError: wreview/SKILL.md is 76 lines, must be < 40` (exit 1) |
| 4 | `scripts/adopt.py:43` | Removed `.agents/skills/wqa` from `CORE_PATHS` | ✅ Killed — `scripts/test_adopt.py:125` `AssertionError: core plan omits .agents/skills/wqa` (exit 1) |
| 5 | `.claude/skills/wqa` | Symlink retargeted to `../../.agents/skills/wreview` | ✅ Killed — `tools/test_phase_skills.py:305` `AssertionError: wqa: wrong link target` (exit 1) |

**Sensor depth**: P0-full (5 manual behavior-level mutations, one per assigned AC surface)
**Result**: 5/5 killed — PASS

---

## Interactive UAT Results

| # | Test | Result | Details |
| --- | --- | --- | --- |
| — | — | ⏭️ Skip | No interactive UI. Slash/docs/adoption surface covered by structural tests and the assigned preload probe. |

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ |
| Surgical changes | ✅ — 15 files, +168/−42, only entry skills, adopt inventory, tests, pack/roadmap, one bug file |
| No scope creep | ✅ — Orca Cursor route left unchanged; bug filed as specified |
| Matches patterns | ✅ — same frontmatter reader, symlink layout, `CORE_PATHS` tuple |
| Spec-anchored outcome check (asserted values match spec) | ⚠️ — keys, caps, agents, symlinks, inventory match; body refuse/stop and live fork return are not asserted |
| Per-layer Coverage Expectation met (domain 1:1 ACs; routes happy+edge+error) | ✅ — unit on skill contracts; integration on adopt core plan |
| Every test maps to a spec requirement - no unclaimed tests | ✅ — UT-001 extension → WEP-01; UT-010 → WEP-02 AC1/AC4; UT-011 → WEP-03 AC1; IT-003 extension → WEP-02 AC4 |
| Documented guidelines followed: `docs/guidelines/TEST-CONTRACT.md`, `.agents/skills/workflow-spec-driven/references/coding-principles.md` | ✅ |

---

## Edge Cases

- [x] `/w<phase>` with no argument: five phase skills and `wqa` stop and ask (`wspecify/SKILL.md:12`, same first-body pattern on `wdesign`/`wtasks`/`wimplement`/`wverify`, `wqa/SKILL.md:12`). Bound by UT-001 `:129`. `wreview` flags are optional; no empty-arg stop (argument-hint is flag list).
- [x] `/wqa` flow with no tagged journey: `wqa/SKILL.md:14` — report and stop. Instruction only; no test lock.
- [x] `/wreview --publish`: `wreview/SKILL.md:14-16` — reject; publishing stays in the main session. Instruction only; no test lock.

---

## Success Criteria

- [ ] From one terminal, `/wspecify a` then `/wspecify b`, each one summary, no stacked procedure transcript — not observed in this Cursor verifier session (no Claude main-chat slash run assigned).
- [x] Implementer probe still shows `# Execute`, `# Ponytail`, and no `Skill` tool — probe file above.

---

## Packet-specific file checks

| Check | Evidence | Result |
| ----- | -------- | ------ |
| Five phase SKILL.md: `context: fork`, `background: false`, `argument-hint`, `agent:` per Assumptions, strict YAML | UT-001 `:122-131`; measured agents match the Assumptions table | ✅ |
| `wreview`/`wqa` under 40 lines; agents planner/verifier; one QA phase + no-tag stop; `--publish` refused | 16 and 14 lines; UT-010; body lines cited under WEP-02 | ✅ files; ⚠️ body sentences untested |
| `.claude/skills/wreview` and `.claude/skills/wqa` git-tracked symlinks | `git ls-files -s` mode `120000`; targets `../../.agents/skills/wreview` and `.../wqa` | ✅ |
| `CORE_PATHS` and frozen inventory include both | `scripts/adopt.py:43`; `scripts/test_adopt.py:35` | ✅ |
| `pack.md` lists seven `w*` entries; roadmap slice 2 done; bug file exists and matches sibling shape | `pack.md:10-16`; `roadmap.md:133`; `docs/qa/bugs/BUG-20260903-cursor-route-bracket-effort-rejected.md` has Status, Severity, Scenario (`CFG-centralize-agent-model-routing`), Expected, Observed, Adapter, Exact path, Evidence | ✅ |
| `AGENTS.md` ≤ 134; every phase SKILL.md ≤ 200 | AGENTS 134; wspecify 118, wdesign 82, wtasks 177, wimplement 189, wverify 193 | ✅ |

---

## Gate Check

- **Gate command**: packet runners (no `tasks.md` Build line)

| Command | Exit | Output |
| ------- | ---- | ------ |
| `python3 tools/test_phase_skills.py` | 0 | `13 passed, 0 failed` |
| `python3 scripts/test_adopt.py` | 0 | `ok (84 tests)` |
| `bun test` | 0 | `124 pass`, `0 fail`, `1157 expect() calls`, 8 files |
| `git diff --check 03e57240..5b10e1af` | 0 | empty |
| `python3 .agents/skills/workflow-config/scripts/workflow_config.py --root . --sync-agents` (1) | 0 | `"changed": []` |
| same command (2) | 0 | `"changed": []` |

- **Test count before feature** (`a24e351d^`): `tools/test_phase_skills.py` 11 functions; `scripts/test_adopt.py` 84 functions
- **Test count after feature**: 13 and 84
- **Delta**: +2 phase-skill tests (UT-010, UT-011). IT-003 grew in place (no new function). No deletions, no weakened assertions observed
- **Skipped tests**: none
- **Failures**: none

Independent Test extras: `python3 scripts/adopt.py plan <tmp> --layers core --json` exit 0 lists `.agents/skills/wqa/SKILL.md`, `.agents/skills/wreview/SKILL.md`, `.claude/skills/wqa`, `.claude/skills/wreview`. `ls .claude/skills/w*` also matches `workflow-config` and `workflow-spec-driven` (nine names); the seven entry skills are present. UT-011 excludes `workflow-*`.

---

## Fix Plans (if issues found)

None required to land this slice. Optional follow-ups (not blockers):

### Follow-up 1: Lock skill-body refuse / one-phase / no-tag sentences

- **Root cause**: UT-010 asserts keys, caps, and symlinks, not the WEP-02 AC2/AC3 sentences
- **Fix task**: extend UT-010 to require `--publish` reject text in `wreview` and the one-phase / no-tag-stop sentence in `wqa`
- **Priority**: Minor

### Follow-up 2: Observe dual `/wspecify` at feature close

- **Root cause**: Success Criterion 1 and WEP-01 AC2/AC3 need a live Claude slash fork
- **Fix task**: coordinator-owned spawn, same class as the AC4 probe
- **Priority**: Minor (packet only assigned the preload probe)

---

## Requirement Traceability Update

Recommended statuses only. `spec.md` was not edited.

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| WEP-01 | Pending | ✅ Verified (AC2/AC3 live half ⚠️) |
| WEP-02 | Pending | ✅ Verified (AC2/AC3 test-lock ⚠️) |
| WEP-03 | Pending | ✅ Verified (description-vs-hint ⚠️) |

---

## Summary

**Overall**: ✅ Ready

**Spec-anchored check**: 7/12 ACs matched on asserted outcomes; 5 spec-precision gaps flagged (WEP-01 AC2 live history, WEP-01 AC3 return shape, WEP-02 AC2/AC3 body sentences, WEP-03 AC1 argument-in-description)
**Sensor**: 5/5 mutations killed
**Gate**: 13 + 84 + 124 passed, 0 failed

**What works**: Fork keys and agent mapping on all seven `w*` skills; preload still injects `wimplement` and `ponytail` without a Skill tool; `wreview`/`wqa` exist, stay under 40 lines, are tracked symlinks, and ship in `CORE_PATHS`; docs list the seven entries and mark slice 2 done; bug file is present and shaped like its siblings; line caps hold.

**Issues found**: none that fail the slice. Precision gaps are observational or test-lock only.

**Next steps**: coordinator may treat S1 as verified and continue. Feature-close Verifier still writes `validation.md` after remaining slices integrate.
