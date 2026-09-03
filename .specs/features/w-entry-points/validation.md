# W Entry Points Validation

**Date**: 2026-09-03
**Spec**: `.specs/features/w-entry-points/spec.md`
**Diff range**: `origin/main..HEAD` (`c3a72f70..4f386642`)
**HEAD**: `4f3866420dd2476b237cdb35ea9099fac858c44f`
**Verifier**: independent sub-agent (author ≠ verifier). Read-only on the real tree. Mutations only in `/tmp/wep-close-sensor`, then removed.
**Verdict**: PASS

Prior evidence cited, not copied: `.specs/features/w-entry-points/validation-s1.md` (slice PASS at `5b10e1af`); `.deep-review/w-entry-points/review.md` (round 2 SHIP); `docs/qa/reports/2026-09-03-w-entry-points.md` (all six scenarios pass); coordinator probe `/private/tmp/claude-501/-Users-antoniofulg-Projects-my-workflow/56007cfc-7cef-4947-a9e8-0835b2fc4af7/scratchpad/probe-fork-preload.txt`.

---

## Task Completion

No `tasks.md` (Tasks skipped). Commits on `origin/main..HEAD` cover T1–T3, review remediations, and QA artifacts.

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1 | ✅ Done | `a24e351d` — fork keys on the five phase skills; UT-001 grown |
| T2 | ✅ Done | `d18e4699` — `wreview` / `wqa`, symlinks, `CORE_PATHS`, UT-010, IT-003 |
| T3 | ✅ Done | `5b10e1af` — pack table, roadmap slice 2 `(done)`, bug file, UT-011 |
| Review remediations | ✅ Done | `1f7c0d0d` plus fingerprint/docs commits; round 2 SHIP |
| QA plan + execute | ✅ Done | `0dc981af`, `4f386642`; report cited above |

---

## Spec-Anchored Acceptance Criteria

### WEP-01 — A phase runs in a fresh agent from one command

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| AC1 five phase skills carry `context: fork`, `agent:` per Assumptions, `background: false`, `argument-hint` | exact keys; agents `planner` / `planner` / `planner` / `implementer` / `verifier`; hint names the feature or slice | `tools/test_phase_skills.py:122` — `assert fields.get("context") == "fork"`; `:123` `assert fields.get("agent") == agent` via `PRELOADING_AGENT` `:27-33`; `:124` `assert fields.get("background") == "false"`; `:125` `assert fields.get("argument-hint") in ('"<feature-or-slice>"', "<feature-or-slice>")`; `:130-131` Bun `readFrontmatter` exit 0. Measured on HEAD: all five files carry those keys | ✅ PASS |
| AC2 `/w<phase> <args>` binds `$ARGUMENTS` and starts with no main-conversation history | first body line binds `$ARGUMENTS`; `context: fork` requests a fresh agent | `tools/test_phase_skills.py:129` — `assert "$ARGUMENTS" in first_body_line`; `:122` fork key. Live empty-history spawn was not run in this session | ⚠️ Spec-precision gap — repo contract asserted; live no-history fork not observed here (same limitation in the QA report) |
| AC3 forked agent finish returns only its final message to the main conversation | product fork return shape | no test assertion for "only the final message" | ⚠️ Spec-precision gap — host runtime; keys that request it are asserted in AC1 |
| AC4 phase skills stay listed as Claude preloads; spawned implementer still has `wimplement` and `ponytail`, no `Skill` tool | templates keep the lists; probe shows both skills and no Skill tool | `tools/test_phase_skills.py:240` — `assert fields.get("skills") == "[" + ", ".join(expected) + "]"` with `CLAUDE_PRELOAD` implementer `("wimplement", "ponytail")` at `:54`; `:244` `assert fields.get("disallowedTools") == "Skill"`. Probe file: Skill tool absent; first heading `# Execute`; ponytail first heading `# Ponytail` | ✅ PASS |
| AC5 IF fork keys stop `skills:` preload THEN switch to the fallback (`phase-<x>` + thin `w<x>`) | fallback only when preload breaks | Probe shows `wimplement` present before any tool call. IF is false; fallback not required | ✅ PASS (vacuous) |

### WEP-02 — Review and QA have entries

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| AC1 `.agents/skills/wreview/SKILL.md` and `wqa/SKILL.md` exist, each under 40 lines, fork keys, `agent:` per Assumptions | `wreview` → `planner`; `wqa` → `verifier`; `< 40` lines | `tools/test_phase_skills.py:294-302` — file exists; `context == "fork"`; `agent == agent`; `background == "false"`; `argument-hint` present; `assert count < 40`. Measured: wreview 16, wqa 14 | ✅ PASS |
| AC2 `/wreview <args>` reads `deep-review/SKILL.md` in full, follows it, publishing nothing; `--publish` refused | body names the wrap and rejects `--publish` | `.agents/skills/wreview/SKILL.md:14-16` — `When $ARGUMENTS includes `--publish`, reject it` and `never pass --publish`. Description also says `never --publish`. QA execute walked the adopted file and recorded the refuse. UT-010 still does not assert those sentences | ⚠️ Spec-precision gap — instruction present; unit suite does not lock the refuse line |
| AC3 `/wqa <flow>` runs only `qa-execute`; `/wqa plan <flow>` runs only `qa-plan`; missing tag renders report and stop | exactly one QA phase; no invented journeys | `.agents/skills/wqa/SKILL.md:14` — `Run exactly one QA phase: qa-plan when the first argument is plan, else qa-execute` and `if no journey carries the tag, report and stop`. QA execute recorded the same sentences on the adopted copy. UT-010 does not assert them | ⚠️ Spec-precision gap — instruction present; unit suite does not lock the one-phase / no-tag stop |
| AC4 both are git-tracked `.claude/skills/` symlinks and members of `CORE_PATHS` | mode `120000`, target `../../.agents/skills/<name>`, listed in core plan and frozen inventory | `tools/test_phase_skills.py:303-307` — symlink, target, resolves, `git ls-files`. `scripts/adopt.py:43` both paths in `CORE_PATHS`. `scripts/test_adopt.py:35` both in `FROZEN_PRE_FEATURE_PATHS`. `scripts/test_adopt.py:124-126` — `assert f".agents/skills/{name}/SKILL.md" in managed` and `assert f".claude/skills/{name}" in managed` for `wreview` and `wqa`. This session: `git ls-files -s` mode `120000`; `readlink` targets match; `adopt.py plan --layers core --json` lists all four paths | ✅ PASS |

### WEP-03 — The menu and docs match

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| AC1 seven `w*` skills user-invocable; each `description` starts with the phase name and states the argument | exactly those seven; not `disable-model-invocation: true`; description prefix plus argument | `tools/test_phase_skills.py:314-324` — `w_skill_dirs == set(ALL_W_SKILLS)`; `disable-model-invocation != "true"`; `description.startswith(... phase)`; `assert "Argument:" in description`. Round 2 remediations closed the S1 description-vs-hint gap | ✅ PASS |
| AC2 docs list the seven entries in `pack.md`; roadmap slice 2 marked done | seven `w*` rows; slice 2 `(done)` | `docs/workflow/pack.md:10-16` lists `wspecify` … `wqa`. `docs/workflow/roadmap.md:133` ends slice 2 with `(done)`. `tools/test_phase_skills.py:207-208` now walks `ALL_W_SKILLS`, including `wreview`/`wqa` | ✅ PASS |
| AC3 `AGENTS.md` stays at or below 134 lines | `<= 134` | `tools/test_phase_skills.py:211-212` — `assert agents <= AGENTS_LINE_CAP` (`:45` = 134). Measured 134 | ✅ PASS |

**Status**: ⚠️ Spec-precision gaps flagged (live fork history, host return shape, WEP-02 body refuse / one-phase sentences not unit-locked). No AC failed on the implementation this session could inspect.

---

## Discrimination Sensor

Scratch: `git worktree add /tmp/wep-close-sensor HEAD`. Real tree `git status --porcelain` empty before and after (0 bytes). Worktree removed with `git worktree remove --force`.

| Mutation | File:line | Description | Killed? |
| -------- | --------- | ----------- | ------- |
| 1 | `.agents/skills/wspecify/SKILL.md:5` | Dropped `context: fork` (WEP-01 AC1) | ✅ Killed — `tools/test_phase_skills.py:122` `AssertionError: wspecify: context is None` (exit 1) |
| 2 | `.agents/skills/wqa/SKILL.md:6` | `agent: verifier` → `agent: planner` (WEP-02 AC1) | ✅ Killed — `tools/test_phase_skills.py:298` `AssertionError: wqa: agent is 'planner'` (exit 1) |
| 3 | `.agents/skills/wreview/SKILL.md` | Padded to 77 lines (WEP-02 AC1) | ✅ Killed — `tools/test_phase_skills.py:302` `AssertionError: wreview/SKILL.md is 77 lines, must be < 40` (exit 1) |
| 4 | `scripts/adopt.py:43` | Removed `.agents/skills/wqa` from `CORE_PATHS` (WEP-02 AC4) | ✅ Killed — `scripts/test_adopt.py:125` `AssertionError: core plan omits .agents/skills/wqa` (exit 1) |
| 5 | `.agents/skills/wspecify/SKILL.md:3` | Removed `Argument:` from description (WEP-03 AC1) | ✅ Killed — `tools/test_phase_skills.py:324` `AssertionError: wspecify: description does not state its argument` (exit 1) |
| 6 | `docs/workflow/pack.md:16` | Removed the `wqa` pack row (WEP-03 AC2) | ✅ Killed — `tools/test_phase_skills.py:208` `AssertionError: pack.md has no row for wqa` (exit 1) |
| 7 | `templates/agents/claude/implementer.md:7` | `skills: [wimplement, ponytail]` → `[ponytail]` (WEP-01 AC4) | ✅ Killed — `tools/test_phase_skills.py:240` `AssertionError: implementer: skills are '[ponytail]'` (exit 1) |

**Sensor depth**: P0-full (7 manual behavior-level mutations across WEP-01..03)
**Result**: 7/7 killed — PASS

---

## Interactive UAT Results

| # | Test | Result | Details |
| --- | --- | --- | --- |
| — | — | ⏭️ Skip | No interactive UI. User-visible adopt/docs/slash contracts were walked in the cited QA execute report. This packet is the technical phase only. |

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ |
| Surgical changes | ✅ — entry skills, adopt inventory, contract tests, pack/roadmap, QA artifacts, one out-of-scope bug file |
| No scope creep | ✅ — Orca Cursor route left unchanged; bug filed as specified |
| Matches patterns | ✅ — same frontmatter reader, symlink layout, `CORE_PATHS` tuple |
| Spec-anchored outcome check (asserted values match spec) | ⚠️ — keys, caps, agents, `Argument:`, pack rows, symlinks, inventory match; live fork return and WEP-02 body refuse/stop are not unit-asserted |
| Per-layer Coverage Expectation met (domain 1:1 ACs; routes happy+edge+error) | ✅ — unit on skill contracts; integration on adopt core plan |
| Every test maps to a spec requirement - no unclaimed tests | ✅ — UT-001 extension → WEP-01; UT-010 → WEP-02 AC1/AC4; UT-011 → WEP-03 AC1; IT-003 extension → WEP-02 AC4; pack-row lock → WEP-03 AC2 |
| Documented guidelines followed: `docs/guidelines/TEST-CONTRACT.md`, `.agents/skills/workflow-spec-driven/references/coding-principles.md` | ✅ |

---

## Edge Cases

- [x] `/w<phase>` with no argument: five phase skills stop and ask on a slash-empty argument (`wspecify/SKILL.md:12`, same first-body pattern on `wdesign`/`wtasks`/`wimplement`/`wverify`). `wqa/SKILL.md:12` stops and asks for the flow. Bound by UT-001 `:129` (`$ARGUMENTS` on the first body line). `wreview` flags are optional; no empty-arg stop.
- [x] `/wqa` flow with no tagged journey: `wqa/SKILL.md:14` — report and stop. Instruction only; no unit lock. QA execute recorded the sentence on the adopted file.
- [x] `/wreview --publish`: `wreview/SKILL.md:14-16` — reject; publishing stays in the main session. Instruction only; no unit lock. QA execute recorded the refuse.

---

## Success Criteria

- [ ] From one terminal, `/wspecify a` then `/wspecify b`, each one summary, no stacked procedure transcript — not observed in this session. Cited QA execute report records the same live dual-`/wspecify` host return as an untested limitation, not a product defect.
- [x] Implementer probe still shows `# Execute`, `# Ponytail`, and no `Skill` tool — coordinator probe file cited above.

---

## Packet-specific file checks

| Check | Evidence | Result |
| ----- | -------- | ------ |
| Five phase SKILL.md: `context: fork`, `background: false`, `argument-hint`, `agent:` per Assumptions, strict YAML | UT-001 `:122-131`; measured agents match the Assumptions table | ✅ |
| `wreview`/`wqa` under 40 lines; agents planner/verifier; one QA phase + no-tag stop; `--publish` refused | 16 and 14 lines; UT-010; body lines cited under WEP-02 | ✅ files; ⚠️ body sentences untested |
| `.claude/skills/wreview` and `.claude/skills/wqa` git-tracked symlinks | `git ls-files -s` mode `120000`; targets `../../.agents/skills/wreview` and `.../wqa` | ✅ |
| `CORE_PATHS` and frozen inventory include both | `scripts/adopt.py:43`; `scripts/test_adopt.py:35` | ✅ |
| `pack.md` lists seven `w*` entries; roadmap slice 2 done; bug file exists and matches sibling shape | `pack.md:10-16`; `roadmap.md:133`; `docs/qa/bugs/BUG-20260903-cursor-route-bracket-effort-rejected.md` has Status, Severity, Scenario, Expected, Observed, Adapter, Exact path, Evidence | ✅ |
| `AGENTS.md` ≤ 134; every phase SKILL.md ≤ 200 | AGENTS 134; wspecify 118, wdesign 82, wtasks 177, wimplement 189, wverify 193 | ✅ |

---

## Gate Check

- **Gate command**: packet runners (no `tasks.md` Build line). First `bun run test:all` hit the known `tools/test_parallel_resource_lock.py` flake (load averages 28.06 25.66 21.47); isolated retry of that file exited 0; full `bun run test:all` retry exited 0.

| Command | Exit | Output |
| ------- | ---- | ------ |
| `bun run test:all` (1) | 1 | bun `124 pass`, `0 fail`, `1157 expect() calls`; python progressed through adopt `ok (84 tests)` and later suites; failed at `tools/test_parallel_resource_lock.py:143` `assert events.index("second-start") < events.index("first-end")` |
| `python3 tools/test_parallel_resource_lock.py` (retry) | 0 | `ok (7 tests)` |
| `bun run test:all` (2) | 0 | bun `124 pass`, `0 fail`, `1157 expect() calls`; python suites completed including `13 passed` (`test_phase_skills.py`) |
| `python3 tools/test_phase_skills.py` | 0 | `13 passed, 0 failed` |
| `python3 scripts/test_adopt.py` | 0 | `ok (84 tests)` |
| `git diff --check origin/main..HEAD` | 0 | empty |
| `python3 .agents/skills/workflow-spec-driven/scripts/validate_spec.py .specs/features/w-entry-points/spec.md` | 0 | `0 error(s), 0 warning(s)` |
| `python3 scripts/adopt.py plan <tmp> --layers core --json` | 0 | `status: ready`; lists `.agents/skills/wqa/SKILL.md`, `.agents/skills/wreview/SKILL.md`, `.claude/skills/wqa`, `.claude/skills/wreview` |
| `ls .claude/skills \| grep -E '^w(specify\|design\|tasks\|implement\|verify\|review\|qa)$' \| wc -l` | 0 | `7` |

- **Test count before feature** (`origin/main`): `tools/test_phase_skills.py` 11 functions; `scripts/test_adopt.py` 84 functions
- **Test count after feature**: 13 and 84
- **Delta**: +2 phase-skill tests (UT-010, UT-011). IT-003 and the pack-row lock grew in place. No deletions, no weakened assertions observed
- **Skipped tests**: none
- **Failures**: first full-gate flake only; not in this feature's diff. Retry green

---

## Fix Plans (if issues found)

None required to close the feature. Residual precision items (not blockers; same class as S1 follow-ups, still open after remediations):

### Follow-up 1: Lock skill-body refuse / one-phase / no-tag sentences

- **Root cause**: UT-010 asserts keys, caps, and symlinks, not the WEP-02 AC2/AC3 sentences
- **Fix task**: extend UT-010 to require `--publish` reject text in `wreview` and the one-phase / no-tag-stop sentence in `wqa`
- **Priority**: Minor

### Follow-up 2: Observe dual `/wspecify` on the host

- **Root cause**: Success Criterion 1 and WEP-01 AC2/AC3 need a live slash fork
- **Fix task**: coordinator-owned spawn, same class as the AC4 probe
- **Priority**: Minor (host limitation; QA did not treat it as a defect)

---

## Requirement Traceability Update

Recommended statuses only. `spec.md` was not edited.

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| WEP-01 | Pending | ✅ Verified (AC2/AC3 live half ⚠️) |
| WEP-02 | Pending | ✅ Verified (AC2/AC3 test-lock ⚠️) |
| WEP-03 | Pending | ✅ Verified |

---

## Summary

**Overall**: ✅ Ready
**Verdict**: PASS

**Spec-anchored check**: 8/12 ACs matched spec outcome in the unit/integration suite; 4 spec-precision gaps flagged (WEP-01 AC2 live history, WEP-01 AC3 return shape, WEP-02 AC2/AC3 body sentences)
**Sensor**: 7/7 mutations killed
**Gate**: bun 124 + phase-skills 13 + adopt 84 passed on the green full-gate retry; first `test:all` exit 1 was the known resource-lock flake

**What works**: Fork keys and agent mapping on all seven `w*` skills; preload still injects `wimplement` and `ponytail` without a Skill tool; `wreview`/`wqa` exist, stay under 40 lines, are tracked symlinks, and ship in `CORE_PATHS`; descriptions carry `Argument:`; docs list the seven entries and mark slice 2 done; line caps hold; round 2 review SHIP; QA execute passed its six scenarios.

**Issues found**: none that fail the feature. Remaining gaps are observational or unit-lock only.

**Next steps**: coordinator may treat the feature as technically verified. Do not treat this report as authorization to push or merge.
