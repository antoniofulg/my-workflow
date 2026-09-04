# Phase Skills Validation — Slice S1

**Date**: 2026-09-03
**Spec**: `.specs/features/phase-skills/spec.md`
**Test contract**: `.specs/features/phase-skills/tests.md`
**Diff range**: `8a87dc0..85dd338` (T1–T7). Checkout HEAD is `4eadda8` (docs-only follow-up; AC5 wording — see Finding 1).
**Verifier**: independent fresh session (author ≠ verifier). Read-only; nothing fixed here.
**Verdict**: ✅ **PASS** with 3 ranked non-blocking gaps.

---

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| T1 wspecify | ✅ Done | `tasks.md:82-84` all `[x]`; skill tree present |
| T2 wdesign | ✅ Done | `tasks.md:107-108` |
| T3 wtasks | ✅ Done | `tasks.md:131-132` |
| T4 wimplement | ✅ Done | done-when checked |
| T5 wverify | ✅ Done | done-when checked |
| T6 router shrink | ✅ Done | done-when checked |
| T7 adopt + docs | ✅ Done | `tasks.md:229-230` |

16 `[x]` boxes, 0 unchecked in S1 tasks. T8–T11 are slice S2, out of scope.

---

## Spec-Anchored Acceptance Criteria

### PSK-01 — Phase skills carry their procedure

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| AC1 five SKILL.md with `name` = dir and `disable-model-invocation: true` | exact frontmatter values | `tools/test_phase_skills.py:59-63` — `assert fields.get("name") == name` and `assert fields.get("disable-model-invocation") == "true"` over `PHASES` (5 entries, `:18-24`) | ✅ PASS |
| AC2 SKILL.md carries the replaced procedure, ≤200 lines | ≤200 | `tools/test_phase_skills.py:66-69` — `assert count <= SKILL_LINE_CAP` (`:14` = 200). Measured: wspecify 118, wdesign 81, wtasks 179, wimplement 188, wverify 197 | ✅ PASS |
| AC3 template lives under the skill's `references/`, named by relative path | template resolves inside the skill | `tools/test_phase_skills.py:126-129` — `assert token.startswith("references/")` and `assert (skill / token).is_file()`. Templates present: `wspecify/references/spec-template.md`, `wdesign/references/design-template.md`, `wtasks/references/tasks-template.md`, `wimplement/references/execution-template.md`, `wverify/references/validation-template.md` | ⚠️ **Spec-precision gap** — resolution is asserted, *naming* is not (mutant M6 survived; see Finding 2) |
| AC4 validators cited as `.agents/skills/workflow-spec-driven/scripts/<name>.py` | exact prefix, file exists | `tools/test_phase_skills.py:120-122` — `assert token.startswith(VALIDATOR_PREFIX)` (`:28`) and `assert (ROOT / token).is_file()`. Live citations e.g. `wspecify/SKILL.md:101` (`validate_spec.py`), `wtasks/SKILL.md:149` (`validate_tasks.py`), `wimplement/SKILL.md:142` (`check_commit.py`), `wverify/SKILL.md:184` (`validate_state.py`) — all keep `--root`/`<feature>` argument semantics | ✅ PASS |
| AC5 five references gone from the router; per-phase totals ≤ replaced + 10 | budget per phase | `tools/test_phase_skills.py:91-97` — `assert not (ROUTER/"references"/reference).exists()` and `assert total <= budget` with budgets at `:19-23`. Measured: wspecify 397/397, wdesign 201/203, wtasks 453/453, wimplement 435/436, wverify 342/349 | ✅ PASS (under the amended AC text — see Finding 1) |
| AC6 `discuss.md` at `wspecify/references/`; five shared stay in the router | exact set | `tools/test_phase_skills.py:99-101` — `assert kept == SHARED_REFERENCES` (`:26`, exact set equality). `discuss.md` presence is asserted indirectly through the `references/discuss.md` token in `wspecify/SKILL.md` (`:35` region) via `:126-129`; mutant M5 (delete the file) was killed | ✅ PASS |

### PSK-02 — Router shrinks to dispatch

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| AC1 router keeps its five sections, ≤150 lines | ≤150 | `tools/test_phase_skills.py:72-74` — `assert count <= ROUTER_LINE_CAP` (`:15` = 150). Measured 136. Sections present: Critical Rules (`workflow-spec-driven/SKILL.md:22`), Auto-Sizing (`:44`), `.specs` Structure (`:78`), Workflow (`:98`), Knowledge Verification Chain (`:114`) | ✅ PASS |
| AC2 sizing table names the phase skill per column | `wspecify`/`wdesign`/`wtasks`/`wimplement` in the table | `tools/test_phase_skills.py:85-87` — table slice bounded by `| Scope`, `assert skill in sizing` for the four. Header at `workflow-spec-driven/SKILL.md:48` | ✅ PASS |
| AC3 no Commands table, no Context Loading Strategy, no Coordinator-assisted section; dispatch text in `references/sub-agents.md` | headings absent | `tools/test_phase_skills.py:81-83` — `assert not line.startswith(heading)` over `FORBIDDEN_ROUTER_HEADINGS` (`:34`). Dispatch text relocated to `workflow-spec-driven/references/sub-agents.md:6-28` (`## Dispatch`, +25 lines in `fdb5170`) | ✅ PASS |
| AC4 router names `w<phase>`, never links `references/<phase>.md` | zero matches | `tools/test_phase_skills.py:78-80` — `assert stale is None` against `PHASE_REFERENCE` (`:33`, covers specify/discuss/design/tasks/implement/validate) | ✅ PASS |

### PSK-04 — Skills are discoverable and adoptable

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| AC1 `.claude/skills/<name>` is a git-tracked symlink to `../../.agents/skills/<name>` | exact target string, tracked | `tools/test_phase_skills.py:104-114` — `assert link.is_symlink()`, `assert link.readlink().as_posix() == f"../../.agents/skills/{name}"`, `assert (link/"SKILL.md").is_file()`, `assert f".claude/skills/{name}" in tracked` (from `git ls-files`) | ✅ PASS |
| AC2 `CORE_PATHS` includes the five dirs; `plan --layers core` lists them managed | present in plan JSON | `scripts/adopt.py:41-42` (the five entries); `scripts/test_adopt.py:117-129` — `assert f".agents/skills/{name}/SKILL.md" in managed` and `assert f".claude/skills/{name}" in managed` off `plan --layers core --json` | ✅ PASS |
| AC3 pack table rows + roadmap states the 200-line rule | five rows; "under 200 lines" | `tools/test_phase_skills.py:131-138` — `assert any(line.startswith(f"| \`{name}\` |") ...)` and `assert "under 200 lines" in roadmap` | ✅ PASS |
| AC4 `AGENTS.md` line count not increased | ≤134 | `tools/test_phase_skills.py:139-140` — `assert agents <= AGENTS_LINE_CAP` (`:36` = 134) | ✅ PASS |

**PSK-03 is slice S2 and was not verified here.**

### Edge cases

| Edge case | Evidence | Result |
| --- | --- | --- |
| SKILL.md over 200 → move text to `references/`, never delete a rule | Independent line-level diff of each pre-slice reference (`8a87dc0`) against the new SKILL.md + its references + the router: every rule sentence is present. The 17 non-verbatim lines are all `<skill-dir>/scripts/…` → `.agents/skills/workflow-spec-driven/scripts/…` path rewrites (required by AC4) or heading removals whose body text survives — e.g. old `implement.md:9 "## Before starting any implementation"` dropped as a heading but its sentence kept at `wimplement/SKILL.md:13`; old `design.md`/`tasks.md` `"## Template: …"` headings replaced by `wdesign/SKILL.md:70` and `wtasks/SKILL.md:165` pointing at the extracted template files. **No rule text was deleted.** | ✅ PASS |
| Two templates disagree on a skill name | UT-006, slice S2 | ⏭️ out of scope |
| `.claude/skills/<name>` is a directory not a symlink → contract test fails | `tools/test_phase_skills.py:108` — `assert link.is_symlink()` fails for a directory | ✅ PASS |

---

## Gate

| Command | Status |
| --- | --- |
| `python3 tools/test_phase_skills.py` | `status=0` — 9 passed, 0 failed |
| `python3 tools/test_workflow_config.py` | `status=0` — 55 passed, 0 failed |
| `python3 scripts/test_adopt.py` | `status=0` — ok (84 tests) |
| `bun run test:python` | `status=0` — all suites OK |

**Test integrity**: purely additive. `tools/test_phase_skills.py` is new (146 lines, 9 tests).
`scripts/test_adopt.py` gained `+16 -0`: five entries appended to `FROZEN_PRE_FEATURE_PATHS`
(`:32-33`) and one new test registered (`:117`, `:1511`). **No existing assertion was removed,
loosened, or reordered** — verified with `git diff 8a87dc0..85dd338 -- scripts/test_adopt.py`
(18 insertions, 0 deletions across both adopt files).

---

## Discrimination Sensor

Run in a throwaway `git worktree` at
`…/scratchpad/wt`, removed afterward.
Baseline `git status --porcelain` md5 `9a27f37ddc06ff98dba207e6f539ad13` before and after — real
checkout untouched.

| # | Mutation | Where | Killed? |
| --- | --- | --- | --- |
| 1 | Delete `disable-model-invocation: true` | `wtasks/SKILL.md` frontmatter | ✅ Killed (exit 1) |
| 2 | Repoint symlink to the wrong skill | `.claude/skills/wverify` → `wdesign` | ✅ Killed |
| 3 | Re-add a `references/specify.md` link | router `SKILL.md` | ✅ Killed |
| 4 | Push the router past 150 lines (+20) | router `SKILL.md` | ✅ Killed |
| 5 | Delete the moved `discuss.md` | `wspecify/references/discuss.md` | ✅ Killed |
| 6 | **Remove the template citation** (`from \`references/tasks-template.md\`` → `from the tasks template`) | `wtasks/SKILL.md:165` | ❌ **Survived** |
| 7 | Rewrite a validator citation to a project-root path (`scripts/validate_state.py`) | `wverify/SKILL.md:184` | ✅ Killed |
| 8 | Drop `.agents/skills/wimplement` from `CORE_PATHS` | `scripts/adopt.py:41-42` | ✅ Killed (`AssertionError: core plan omits .agents/skills/wimplement`) |

**Sensor depth**: lightweight (8 injected, 7 killed, 1 survived).

---

## Implementer-reported deviations — adjudication

1. **UT-008 accepts two token shapes.** *Confirmed and accepted for AC4 and AC6; partial for AC3.*
   `tools/test_phase_skills.py:116-129`: a `scripts/*.py` token must start with the router prefix
   and exist (AC4, killed by M7); a `references/` token either starts with the router reference
   prefix and exists, or is bare and resolves inside the phase skill (AC3/AC6, killed by M5). The
   gap is that the rule is conditional on a token *being present* — see Finding 2.
2. **UT-002 split into `test_phase_skill_line_cap` (`:66`) and `test_router_line_cap` (`:72`).**
   *Confirmed, harmless.* Both caps are still asserted (mutants 4 and the 200-line cap constant),
   and splitting improves failure attribution. No coverage lost.
3. **Per-phase totals at or near the +10 budget.** *Confirmed with `wc -l`.* wspecify 397 ≤ 397,
   wdesign 201 ≤ 203, wtasks 453 ≤ 453, wimplement 435 ≤ 436, wverify 342 ≤ 349. Independent
   line-by-line diff of the five pre-slice references shows **no rule sentence deleted** — see the
   edge-case row above for the 17 accounted-for non-verbatim lines. See Finding 1 on the AC wording.
4. **`FROZEN_PRE_FEATURE_PATHS` grew.** *Confirmed, additive only.* `scripts/test_adopt.py:32-33`
   adds exactly the five `.agents/skills/w*` entries; the diff has zero deletions.
5. **Router cleanup.** *Confirmed.* No `references/<phase>.md` link, no `## Commands`,
   `## Context Loading Strategy`, or `## Coordinator-assisted` heading in
   `workflow-spec-driven/SKILL.md` (136 lines); the coordinator/dispatch text now lives at
   `workflow-spec-driven/references/sub-agents.md:6-28`.

---

## Ranked gaps (non-blocking)

1. **Minor — AC5's wording was loosened after the code landed.** `4eadda8` changed spec.md:82 from
   "plus its frontmatter" to "plus ten lines for frontmatter and headings". Under the pre-slice
   wording (frontmatter is 5 lines) wspecify (+10), wtasks (+10), wimplement (+9) and wdesign (+8)
   would all have failed. Mitigating: `tests.md` UT-003 already carried the `+10` budget at plan
   time (`8a87dc0`, the only commit touching that file), so the amendment reconciles spec to a
   pre-committed contract rather than to a measured result. No fix task; noted so the sequence is
   on record.
2. **Minor — PSK-01 AC3's "SHALL name it by relative path" half is not discriminated.**
   `tools/test_phase_skills.py:124-129` validates tokens that appear but never asserts that each
   phase skill names its own template, so a SKILL.md that stops citing its template still passes
   (mutant 6 survived). Fix: assert each phase skill's SKILL.md contains its own
   `references/<x>-template.md` token (and, for `wspecify`, `references/discuss.md`).
3. **Minor — validator/template citation scan covers SKILL.md only.** Same test walks
   `(skill/"SKILL.md")` and not the skill's `references/*.md`, so a broken path inside a template
   is invisible. Cheap to widen to `phase_tree(name)` (`:53-56`).

**Observation, outside the slice:** the checkout carries one uncommitted edit to
`docs/workflow/roadmap.md` (a `sentry`/`analytics` source-label addition). It predates this
session, is unrelated to S1, and was present in the sensor baseline.

---

## Code Quality

| Check | Pass? |
| --- | --- |
| No features beyond what was asked | ✅ |
| No abstractions for single-use code | ✅ — the contract test is one flat module of plain asserts |
| No unnecessary "flexibility" added | ✅ |
| Only touched files required for the tasks | ✅ — 25 files, all named in T1–T7 |
| Didn't "improve" unrelated code | ✅ |
| Matches existing patterns/style | ✅ — same runner shape as `tools/test_workflow_config.py` |
| Would a senior engineer approve? | ✅ |
| Tests map to ACs, non-shallow | ✅ — 7 of 8 mutants killed |
| Spec-anchored outcome check | ⚠️ — one spec-precision gap (AC3 naming half) |
| Every test in scope maps to a spec AC or Done-when criterion | ✅ — all 9 unit tests trace to UT-001/002/003/004/007/008/009, IT-003 to PSK-04 AC2 |
| Documented project guidelines followed | ✅ — `docs/guidelines/TEST-CONTRACT.md`, `VERIFICATION-EVIDENCE.md` |

---

## Verdict

✅ **PASS.** All in-scope acceptance criteria (PSK-01 AC1–AC6, PSK-02 AC1–AC4, PSK-04 AC1–AC4) and
both applicable edge cases carry `file:line` evidence. Gate green on all four commands. Sensor 7/8.
The single surviving mutant and the two citation-scan gaps are Minor and can ride with slice S2's
contract-test work; none of them blocks integration of S1.
