# Phase Skills — Slice S2 Remediation Validation (round 2)

**Date**: 2026-09-03
**Spec**: `.specs/features/phase-skills/spec.md` — PSK-01 AC1 (amended), Assumptions row "Hidden from auto-invocation", the `disable-model-invocation` Edge Case, Success Criteria
**Test contract**: `.specs/features/phase-skills/tests.md` — UT-001 (amended), UT-002, IT-002 + new sibling case
**Diff range**: `3644d4e..2bf336f` (code: `9693e1e`, `b9d34e2`; docs: `468b9bd`, `2bf336f`)
**Checkout**: `/Users/antoniofulg/Projects/my-workflow`, branch `feat/phase-skills`, HEAD `2bf336f`, clean before and after
**Verifier**: independent fresh session (author ≠ verifier)

**Verdict**: ✅ **PASS** — 0 blocking gaps, 1 Minor precision note. Both validation-s2 items are closed.

---

## Task Completion

| Task | Commit | Status | Notes |
| --- | --- | --- | --- |
| validation-s2 gap 1 (hollow-skill sensor blindness) | `9693e1e` | ✅ Done | New sibling case + shared `assert_sync_rejects_preload_skill` helper; no production change |
| T12 Make the phase skills preloadable | `b9d34e2` | ✅ Done | Frontmatter only in all five skills; UT-001 amended |
| Doc alignment (spec, design, tests, tasks, roadmap, STATE) | `468b9bd`, `2bf336f` | ✅ Done | No code |

---

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| **PSK-01 AC1a** frontmatter `name` equals the directory | exact equality, all 5 | `tools/test_phase_skills.py:95` — `assert fields.get("name") == name` over `PHASES` (5 entries, `:18-24`) | ✅ PASS |
| **PSK-01 AC1b** no `disable-model-invocation` key | key absent, all 5 | `tools/test_phase_skills.py:97` — `assert "disable-model-invocation" not in fields`. Source: five frontmatters at `.agents/skills/w{specify,design,tasks,implement,verify}/SKILL.md:1-4`, key removed by `b9d34e2` | ✅ PASS |
| **PSK-01 AC1c** `description` names the preloading agent | agent token present, per-skill mapping | `tools/test_phase_skills.py:100` — `assert agent in description`, driven by `PRELOADING_AGENT:27-33` (`wspecify/wdesign/wtasks→planner`, `wimplement→implementer`, `wverify→verifier`) | ✅ PASS |
| **PSK-01 AC1d** `description` names the `/w<phase>` entry | literal `/w<name>` present | `tools/test_phase_skills.py:101` — `assert f"/{name}" in description`. Descriptions end `… enter with /wspecify.` / `/wdesign` / `/wtasks` / `/wimplement` / `/wverify` (`SKILL.md:3` each) | ✅ PASS |
| **PSK-01 AC2 / PSK-02 AC1** line caps | phase ≤ 200, router ≤ 150 | `tools/test_phase_skills.py:104-108` (UT-002). Measured `wc -l`: wdesign 80, wspecify 117, wtasks 178, wimplement 187, wverify 196; router `workflow-spec-driven/SKILL.md` 136 | ✅ PASS |
| **PSK-03 AC4** (re-checked, `SKILL.md` half) | exit ≠ 0 naming template + skill, nothing written, for a directory with no `SKILL.md` | `.agents/skills/workflow-config/scripts/workflow_config.py:577-581` (`(… / skill / "SKILL.md").is_file()` inside the plan loop, before any write). Asserted `tools/test_workflow_config.py:1749-1770` (`assert_sync_rejects_preload_skill`) via `test_sync_rejects_a_preload_skill_directory_without_a_skill_file:1780-1786`, which creates `<root>/.agents/skills/hollow/` with no `SKILL.md` | ✅ PASS |
| **Body-invariance** (T12 scope discipline) | only frontmatter may differ vs `e8b9e50` | `git diff e8b9e50..2bf336f -- .agents/skills/w*/SKILL.md` = 5 files, `+5 -10`, each hunk `@@ -1,7 +1,6 @@` inside frontmatter; zero body lines changed | ✅ PASS |

**Status**: ✅ 7/7 checked criteria matched their spec-defined outcome. No spec-precision gap at AC level.

---

## Discrimination Sensor

Isolated scratch: `git worktree add --detach <scratch> 2bf336f`; mutated only in the scratch;
`git worktree remove --force` afterwards. Real-tree `git status --porcelain` was empty before and
after (verified twice).

| # | Mutation | File:line | Killed? |
| --- | --- | --- | --- |
| 1 | Re-add `disable-model-invocation: true` | `.agents/skills/wimplement/SKILL.md:4` | ✅ Killed — `python3 tools/test_phase_skills.py` status=1, `AssertionError: wimplement: the flag blocks 'skills:' preload` |
| 2 | Drop the `/w` token from a description (`enter with /wverify.` → `enter via the verify phase.`) | `.agents/skills/wverify/SKILL.md:3` | ✅ Killed — status=1, `AssertionError: wverify: description does not name the /wverify entry` |
| 3 | Drop the agent name (`Preloaded by the planner agent;` → `Preloaded upstream;`) | `.agents/skills/wspecify/SKILL.md:3` | ✅ Killed — status=1, `AssertionError: wspecify: description does not name the planner agent` |
| 4 | Relax the preload check `… / skill / "SKILL.md").is_file()` → `… / skill).is_dir()` | `.agents/skills/workflow-config/scripts/workflow_config.py:577` | ✅ Killed — `test_sync_rejects_a_preload_skill_directory_without_a_skill_file` FAIL (`AssertionError: sync accepted preload skill 'hollow'`) while `test_sync_rejects_an_unknown_preload_skill_before_any_write` PASS — the exact discrimination validation-s2 gap 1 asked for |

**Sensor depth**: lightweight (4 mutations, all on the code this range introduces)
**Result**: 4/4 killed — ✅ PASS

---

## Gate Check

| Command | Status | Result |
| --- | --- | --- |
| `python3 tools/test_phase_skills.py` | `status=0` | 11 passed, 0 failed |
| `python3 tools/test_workflow_config.py` | `status=0` | 58 passed, 0 failed (was 57 before `9693e1e`; +1 = the new sibling case) |
| `python3 scripts/test_adopt.py` | `status=0` | ok (84 tests) |
| `python3 .agents/skills/workflow-config/scripts/workflow_config.py --root . --sync-agents` | `status=0` | `{"changed": [], "unchanged": [15 packets]}` — generated runtimes already match the templates |
| `git status --porcelain` (before and after sensor) | empty | tree clean |

**Test count delta**: +1 (`test_sync_rejects_a_preload_skill_directory_without_a_skill_file`). No test
deleted, skipped, or weakened; `9693e1e` refactored the existing IT-002 body into
`assert_sync_rejects_preload_skill` with every original assertion preserved
(`returncode != 0`, empty stdout, template name in stderr, skill name in stderr, no provider
directory written, `tree_state(root) == before`).

**Not run (by packet instruction)**: `bun run test:python` — box at load 40,
`tools/test_parallel_resource_lock.py` flakes above 20. The coordinator reruns it when quiet. This is
the one open evidence item for the slice; the scoped suites above cover every AC in this range.

---

## Edge Cases

- [x] `IF a phase skill sets disable-model-invocation: true THEN the contract test SHALL fail naming the skill` — proven by sensor mutation 1; the failure message names `wimplement`.
- [x] `IF a phase SKILL.md exceeds 200 lines THEN move text to references, never delete a rule` — caps hold with 4 lines of headroom at the worst file (`wverify` 196/200). No rule text was moved or deleted in this range (body-invariance row above).
- [x] `WHEN .claude/skills/<name> already exists as a directory instead of a symlink THEN sync SHALL leave it and the contract test SHALL fail` — unchanged by this range; the five symlinks remain tracked (`.claude/skills/w* -> ../../.agents/skills/w*`).

---

## Success Criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| An implementer dispatched with the new template has `wimplement` and `ponytail` in context and no `Skill` tool | Live probe by the coordinator (cited as given, not re-run here): spawned implementer reported no `Skill` tool, `wimplement` text present (`# Execute`, ~130 lines), `ponytail` present | ✅ PASS |
| Planner context at Specify drops from router plus reference to router plus one phase skill | `wc -l`: router 136 + `wspecify` 117 = 253 lines, versus the pre-split router (200) plus `references/specify.md` | ✅ PASS |

---

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum code | ✅ — T12 is a 5-line frontmatter edit; the test fix is one helper plus one 7-line case |
| Surgical changes | ✅ — no body line of any phase skill changed vs `e8b9e50` |
| No scope creep | ✅ — no production change in `9693e1e`; no product code in `b9d34e2` |
| Matches patterns | ✅ — helper follows the file's existing `make_preload_root` / `tree_state` idiom |
| Spec-anchored outcome check | ✅ — every assertion targets the amended AC1 wording |
| Per-layer Coverage Expectation | ✅ — contract text asserted at unit layer; sync behaviour asserted at integration layer through a real subprocess |
| Every test maps to a spec requirement | ✅ — UT-001→PSK-01 AC1, UT-002→PSK-01 AC2/PSK-02 AC1, IT-002 + sibling→PSK-03 AC4 |
| Documented guidelines followed | ✅ — `docs/guidelines/TEST-CONTRACT.md` consulted for the sibling case's layer; the case asserts a spec outcome, not an implementation shape |

---

## Ranked gaps

None blocking.

1. **Minor (precision note, no fix task) — the description assertions are substring checks.**
   `tools/test_phase_skills.py:100-101` assert `agent in description` and `f"/{name}" in description`.
   A description that mentioned the agent in a negation ("not for the planner") or carried `/wverify`
   inside unrelated prose would pass. This matches the spec's own wording ("names the preloading
   agent and its `/w<phase>` entry"), so it is a spec-precision limit rather than a test defect. No
   remediation recommended: tightening it would encode phrasing the spec does not define.

**validation-s2 disposition**: gap 1 (hollow-skill sensor blindness) is closed and independently
re-derived by sensor mutation 4. The validation-s2 procedural note (`wverify` uninvocable) is
resolved — this session invoked `/wverify` as a skill, which is exactly the behaviour `b9d34e2`
restores.

---

## Requirement Traceability Update

| Requirement | Previous | New |
| --- | --- | --- |
| PSK-01 | Implementing | ✅ Verified (AC1 as amended, AC2) |
| PSK-03 | Verified with 1 Minor gap | ✅ Verified (AC4 now discriminated) |

---

## Summary

**Overall**: ✅ Ready

**Spec-anchored check**: 7/7 criteria matched the spec outcome, 0 spec-precision gaps at AC level
**Sensor**: 4/4 mutations killed
**Gate**: 11 + 58 + 84 passed, 0 failed, 0 skipped; `--sync-agents` reports `changed: []`

**What works**: the five phase skills carry no preload-blocking flag, each description names its
preloading agent and its `/w<phase>` entry, no procedure text moved, caps hold with headroom, and the
sync check now fails on a half-installed skill directory as well as a missing one.

**Issues found**: none blocking; one Minor precision note recorded above.

**Next steps**: coordinator reruns `bun run test:python` when the box is quiet; then deep review
group [S1, S2] and the QA plan packet.
