# Phase Skills Validation

**Date**: 2026-09-03
**Spec**: `.specs/features/phase-skills/spec.md`
**Diff range**: `origin/main..HEAD` (merge-base `b5dc370`, HEAD `a4e76d3`), 26 commits, 71 files
**Verifier**: independent sub-agent (author ≠ verifier), fresh session, integrated final tree
**Scope**: feature-level close. Slice evidence in `validation-s1.md`, `validation-s2.md`,
`validation-s2-r2.md`; Deep Review round 2 SHIP; QA execute report
`docs/qa/reports/2026-09-03-phase-skills.md` (10/10 pass). Re-derived here from scratch.

---

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| T1–T5 | ✅ Done | Five phase skills exist, all Done-when boxes checked (`tasks.md:66-181`) |
| T6 | ✅ Done | Router 136 lines |
| T7 | ✅ Done | Adopt catalog + docs |
| T8–T10 | ✅ Done | Claude / Codex / Cursor templates |
| T11 | ✅ Done | Sync rejects unknown preload skill |
| T12 | ✅ Done | `disable-model-invocation` removed; skills preloadable |

No task is blocked or partial. `validate_tasks.py` exit 0.

---

## Spec-Anchored Acceptance Criteria

Evidence-or-zero: every row cites a `file:line` assertion re-read in this session, plus the
independently measured value where the spec states a number.

### PSK-01 — Phase skills carry their procedure

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| AC1 five SKILL.md with `name` = dir, no `disable-model-invocation`, description naming the preloading agent and `/w<phase>` | exact key/value contract | `tools/test_phase_skills.py:116` `assert fields.get("name") == name`; `:117` `assert "disable-model-invocation" not in fields`; `:120` `assert agent in description`; `:121` `assert f"/{name}" in description`; `:123` strict-YAML parse via `tools/shared/src/frontmatter.ts` | ✅ PASS (see ⚠️ SP-1) |
| AC2 procedure sections present, ≤200 lines | ≤200 each | `tools/test_phase_skills.py:129` `assert count <= SKILL_LINE_CAP`. Measured: wspecify 117, wdesign 80, wtasks 178, wimplement 187, wverify 196 | ✅ PASS |
| AC3 templates under the skill's `references/`, named by relative path | every local reference named in SKILL.md | `tools/test_phase_skills.py:182` `assert token in entry, f"{name}/SKILL.md does not name {token}"`; `:193` `assert (skill / token).is_file()` | ✅ PASS |
| AC4 validators cited as `.agents/skills/workflow-spec-driven/scripts/<name>.py` | exact prefix, file exists | `tools/test_phase_skills.py:186` `assert token.startswith(VALIDATOR_PREFIX)`; `:187` `assert (ROOT / token).is_file()` | ✅ PASS |
| AC5 five references gone from the router; per-phase total ≤ replaced + 10 | numeric budgets | `tools/test_phase_skills.py:154` `assert not (ROUTER / "references" / reference).exists()`; `:156` `assert total <= budget`. Measured: wspecify 396≤397, wdesign 200≤203, wtasks 452≤453, wimplement 434≤436, wverify 341≤349. Baselines re-derived from `b5dc370` (`specify.md` 228, `discuss.md` 159, `design.md` 193, `tasks.md` 443, `implement.md` 426, `validate.md` 339) — they match the test constants at `tools/test_phase_skills.py:19-23` | ✅ PASS |
| AC6 `discuss.md` under `wspecify/references/`; five shared references stay in the router | exact set | `tools/test_phase_skills.py:161` `assert kept == SHARED_REFERENCES`. `ls` confirms router `references/` = `code-analysis.md`, `coding-principles.md`, `lessons.md`, `memory.md`, `sub-agents.md`; `discuss.md` at `.agents/skills/wspecify/references/discuss.md`, cited from `.agents/skills/wspecify/SKILL.md:10` | ✅ PASS |

### PSK-02 — Router shrinks to dispatch

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| AC1 router keeps Critical Rules, Auto-Sizing, `.specs` Structure, Workflow, Knowledge Verification Chain; ≤150 lines | ≤150 | `tools/test_phase_skills.py:134` `assert count <= ROUTER_LINE_CAP`. Measured 136. Headings present at `.agents/skills/workflow-spec-driven/SKILL.md:23,50,78,96,114` | ✅ PASS |
| AC2 sizing table names the phase skill per column | cells contain `wspecify`/`wdesign`/`wtasks`/`wimplement` | `tools/test_phase_skills.py:148` `assert skill in sizing`; row at `.agents/skills/workflow-spec-driven/SKILL.md:54` | ✅ PASS |
| AC3 no Commands table, no Context Loading Strategy, no Coordinator-assisted section; dispatch in `sub-agents.md`, ceiling in phase skills | headings absent | `tools/test_phase_skills.py:143` `assert not line.startswith(heading)` over `FORBIDDEN_ROUTER_HEADINGS`. Dispatch text at `.agents/skills/workflow-spec-driven/references/sub-agents.md:1` (`# Coordinator-assisted slice execution`); loading ceiling at `wspecify/SKILL.md:103`, `wtasks/SKILL.md:160`, `wdesign/SKILL.md:65` | ✅ PASS |
| AC4 router names `w<phase>`, never links `references/<phase>.md` | zero matches | `tools/test_phase_skills.py:140` `assert stale is None` over `PHASE_REFERENCE`; independent grep of the router returns only `references/memory.md`, `references/coding-principles.md`, `references/code-analysis.md` | ✅ PASS |

### PSK-03 — Agents preload their skills

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| AC1 planner `skills: [workflow-spec-driven, wspecify, wtasks, ponytail]`, no `disallowedTools` | exact list | `tools/test_phase_skills.py:232` `assert fields.get("skills") == "[" + ", ".join(expected) + "]"`; `:238` `assert "disallowedTools" not in fields`. Value at `templates/agents/claude/planner.md:7` | ✅ PASS |
| AC2 implementer `[wimplement, ponytail]` + `disallowedTools: Skill`; explorer/deep-reviewer `disallowedTools: Skill` with unchanged tools; verifier `[wverify]`, no `disallowedTools` | exact | `tools/test_phase_skills.py:232`, `:236` `assert fields.get("disallowedTools") == "Skill"`, `:241` `assert fields.get("tools") == READ_ONLY_TOOLS`. Values at `templates/agents/claude/implementer.md:7-8`, `verifier.md:7`, `explorer.md:9-10`, `deep-reviewer.md:8-9` | ✅ PASS |
| AC3 sync output byte-identical to the template except `model`/`effort` | byte equality | `tools/test_workflow_config.py:1740` `assert generated == template.replace("model: opus\neffort: medium\n", ...)`; `:1744` `assert key in template and key in generated` for `skills: [wimplement, ponytail]` and `disallowedTools: Skill` | ✅ PASS |
| AC4 unknown preload skill → non-zero exit naming template and skill, nothing written | exit ≠ 0, stderr names both, no writes | `tools/test_workflow_config.py:1764` `assert completed.returncode != 0`; `:1766-1767` stderr contains `templates/agents/claude/implementer.md` and the skill name; `:1770` `assert not directory.exists()` for every provider; `:1771` `assert tree_state(root) == before`. Production check at `.agents/skills/workflow-config/scripts/workflow_config.py:577-580` (raises before `render_agent_packet`) | ✅ PASS |
| AC5 Cursor/Codex planner, implementer, verifier name the phase skills and no reference file | no `implement.md`/`validate.md`/`specify.md` token; phase skill named | `tools/test_phase_skills.py:251` `assert removed not in text`; `:253` `assert name in text`. Values at `templates/agents/codex/planner.toml:12`, `codex/implementer.toml:26`, `codex/verifier.toml:18`, `cursor/planner.md:13`, `cursor/implementer.md:28`, `cursor/verifier.md:20` | ✅ PASS |
| AC6 every Load / Do-not-load line names an existing skill or guideline path | resolves on disk | `tools/test_phase_skills.py:256` `assert token not in REFERENCE_FILENAMES`; `:258` `assert (ROOT / token).exists()`; `:260` `assert (SKILLS / name / "SKILL.md").is_file()`, over 15 templates | ✅ PASS |

### PSK-04 — Skills are discoverable and adoptable

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| AC1 `.claude/skills/<name>` is a tracked symlink to `../../.agents/skills/<name>` | exact target, git-tracked | `tools/test_phase_skills.py:170` `assert link.is_symlink()`; `:171` `assert link.readlink().as_posix() == f"../../.agents/skills/{name}"`; `:172` resolves to a SKILL.md; `:173` `assert f".claude/skills/{name}" in tracked`. `git ls-files .claude/skills` lists all five | ✅ PASS |
| AC2 `CORE_PATHS` includes the five dirs; `plan --layers core` lists them managed | present in plan JSON | `scripts/test_adopt.py:124` `assert f".agents/skills/{name}/SKILL.md" in managed`; `:125` `assert f".claude/skills/{name}" in managed`. Catalog at `scripts/adopt.py:41-42` | ✅ PASS |
| AC3 `pack.md` table rows for all five; roadmap states the 200-line cap | rows + literal string | `tools/test_phase_skills.py:200` `assert any(line.startswith(f"| \`{name}\` |"))`; `:202` `assert "under 200 lines" in roadmap`. Rows at `docs/workflow/pack.md:10-14`; cap at `docs/workflow/roadmap.md:15-16` | ✅ PASS |
| AC4 `AGENTS.md` line count at or below current | ≤134 | `tools/test_phase_skills.py:204` `assert agents <= AGENTS_LINE_CAP`. Measured 134 at HEAD and 134 at `b5dc370` — no growth | ✅ PASS |

**Status**: ✅ 20/20 ACs covered by a `file:line` assertion; 2 spec-precision gaps flagged below.

### Spec-precision gaps (flagged, not failures)

- **SP-1 (PSK-01 AC1, `wdesign`)** — the AC says the description names "the preloading agent", but no
  agent preloads `wdesign`: PSK-03 AC1 gives the planner `[workflow-spec-driven, wspecify, wtasks,
  ponytail]`. The shipped description says "Pulled on demand by the planner agent"
  (`.agents/skills/wdesign/SKILL.md:3`) — honest, and the test only requires the substring `planner`
  (`tools/test_phase_skills.py:120`). The implementation is right; the AC's wording is imprecise.
- **SP-2 (Edge Case 3)** — "IF two templates disagree on a skill name THEN the contract test SHALL
  fail **naming both files**." The shipped assertion names one file per failure
  (`tools/test_phase_skills.py:253`). Sensor mutant M8 confirmed the disagreement is caught, with one
  file in the message. Detection is correct; the message is less precise than the spec states.

---

## Discrimination Sensor

Isolated `git worktree` at `HEAD`; real tree baseline `git status --porcelain` empty before and after.
Worktrees removed with `git worktree remove --force`. No `git stash` used.

| # | Mutation | File | Description | Killed? |
| --- | --- | --- | --- | --- |
| M1 | PSK-04 AC1 | `.claude/skills/wverify` | Removed the phase-skill symlink | ✅ Killed — `test_claude_symlinks_resolve`, exit 1, `.claude/skills/wverify is not a symlink` |
| M2 | PSK-01 AC1 | `.agents/skills/wimplement/SKILL.md:2` | Re-added `disable-model-invocation: true` | ✅ Killed — exit 1, `wimplement: the flag blocks \`skills:\` preload` |
| M3 | PSK-04 AC2 | `scripts/adopt.py:41` | Dropped `.agents/skills/wtasks` from `CORE_PATHS` | ✅ Killed — `test_adopt.py` exit 1, `core plan omits .agents/skills/wtasks` |
| M4 | PSK-03 AC4 | `workflow_config.py:578` | Sync check accepts a hollow skill dir (`SKILL.md.is_file()` → `.is_dir()`) | ✅ Killed — exit 1, `sync accepted preload skill 'hollow'` |
| M5 | PSK-02 AC1 | router `SKILL.md` | Appended 20 blank lines (136 → 156) | ✅ Killed — exit 1, `router SKILL.md is 156 lines, cap is 150` |
| M6 | PSK-03 AC2 | `templates/agents/claude/verifier.md:7` | `skills: [wverify]` → `[ponytail]` | ✅ Killed — exit 1, `verifier: skills are '[ponytail]'` |
| M7 | PSK-03 AC3 | `workflow_config.py` render path | Renderer strips `disallowedTools: Skill` from the generated packet | ✅ Killed — exit 1, `generated implementer differs from its template beyond model and effort` |
| M8 | Edge case 3 | `templates/agents/cursor/planner.md:13` | Cursor planner names `wverify` where Claude names `wspecify` | ✅ Killed — exit 1, `cursor/planner.md does not name its phase skill wspecify` (names one file, see SP-2) |
| M9 | Edge case 4 | `.claude/skills/wtasks` | Symlink replaced by a real directory holding a copied SKILL.md | ✅ Killed — exit 1, `.claude/skills/wtasks is not a symlink` |
| M10 | Loosened gate | `tools/shared/tests/qa-skills.test.ts` | Dropped `docs/qa/reports` from `frozenQaRoots` | ✅ Killed — `bun test` exit 1, 1 fail / 29 pass |

**Sensor depth**: extended lightweight (10 mutations, one per AC family plus both testable edge cases
plus the one gate that was loosened during the feature).
**Result**: 10/10 killed, 0 survived — ✅ PASS.

---

## Edge Cases

- [x] `disable-model-invocation: true` on a phase skill → contract test fails naming the skill (M2).
- [x] Phase SKILL.md over 200 lines → cap test fails (`tools/test_phase_skills.py:129`); the shipped
      split moved templates to `references/` rather than deleting rules (AC5 budgets hold).
- [x] Two templates disagree on a skill name → contract test fails (M8), naming one file (SP-2).
- [x] `.claude/skills/<name>` is a directory instead of a symlink → contract test fails (M9); sync
      leaves the path alone (`workflow_config.py` writes only under `.<provider>/agents/`).

---

## Gate Check

| Command | Exit code | Result |
| --- | --- | --- |
| `bun run test:all` | 0 | bun 124 pass / 0 fail across 8 files; every Python suite OK |
| `python3 tools/test_phase_skills.py` | 0 | 11 passed, 0 failed |
| `python3 tools/test_workflow_config.py` | 0 | 58 passed, 0 failed |
| `python3 scripts/test_adopt.py` | 0 | ok (84 tests) |
| `git diff --check` | 0 | clean |
| `validate_spec.py .specs/features/phase-skills/spec.md` | 0 | 0 errors, 0 warnings |
| `validate_tasks.py .specs/features/phase-skills/tasks.md` | 0 | 0 errors, 0 warnings |

`uptime` load at gate start 17.29 (below the 20 threshold); `tools/test_parallel_resource_lock.py`
passed inside `bun run test:all` with no rerun needed.

**Test integrity**
- Bun `it(...)` cases under `tools/shared/tests/`: 78 at `b5dc370`, 78 at HEAD — no decrease.
- `tools/test_workflow_config.py`: 55 → 58 test functions (+3, IT-001/IT-002 + hollow-dir variant).
- `scripts/test_adopt.py`: 83 → 84 (+1, IT-003).
- `tools/test_phase_skills.py`: new, 11 test functions (UT-001…UT-009).
- Net +15 tests. No test deleted, no assertion weakened.
- One gate **was** narrowed: commit `50ca157b` removed `docs/qa/scenarios` from the frozen-QA-history
  set in `tools/shared/tests/qa-skills.test.ts`. Re-derived independently: `docs/guidelines/QA-SCENARIOS.md:122`
  is the sole status authority and *requires* resetting a changed scenario to `untested`, which the
  freeze made impossible; the defect is filed as
  `docs/qa/bugs/BUG-20260903-history-gate-forbids-resetting-baseline-scenarios.md`. The
  command-authority exemption for scenarios is unchanged, and the freeze still bites for reports
  (sensor M10). This is a corrected false constraint, not a weakened gate.
- **Skipped tests**: none.
- **Failures**: none.

---

## Code Quality

| Principle | Status |
| --- | --- |
| No features beyond what was asked | ✅ — every changed path is named in the spec's Impact section or is a phase-skill move |
| No abstractions for single-use code | ✅ — `_preload_skills` is one 8-line helper for one call site |
| No unnecessary flexibility | ✅ — the sync check is an existence test, no config surface added |
| Only touched files required for task | ✅ — 71 files, all traceable to T1–T12, QA, or the `50ca157b` gate defect |
| Didn't improve unrelated code | ✅ |
| Matches existing patterns/style | ✅ — new suites follow the repo's plain-`assert` + `__main__` runner pattern |
| Would a senior engineer approve? | ✅ |
| Tests map to ACs and are non-shallow | ✅ — spot-checked PSK-03: UT-005 asserts exact frontmatter values, IT-001 asserts byte equality, IT-002 asserts exit code + stderr + no writes + unchanged tree |
| Spec-anchored outcome check | ✅ with SP-1, SP-2 flagged |
| Per-layer Coverage Expectation met | ✅ — no domain/route layer here; docs-and-skill-text surface covered by contract tests + one integration path per behaviour |
| Every test maps to a spec AC or edge case | ✅ — 11 UT + 3 IT map to UT-001…UT-009, IT-001…IT-003 in `tests.md`; no unclaimed test |
| Documented guidelines followed | ✅ — `docs/guidelines/TEST-CONTRACT.md`, `docs/guidelines/QA-SCENARIOS.md`, `docs/guidelines/CONTEXT-BUDGET.md` (AGENTS.md held at 134 lines) |

---

## Success Criteria

- [x] Implementer packet carries `wimplement` + `ponytail` and no `Skill` tool — template evidence at
      `templates/agents/claude/implementer.md:7-8`; the author's probe (2026-09-03) is cited, not
      re-run in this read-only session.
- [x] Planner Specify context drops from 200 + 228 to 136 + 117 lines — re-measured this session:
      `git show b5dc370:.agents/skills/workflow-spec-driven/SKILL.md | wc -l` = 200,
      `specify.md` = 228; HEAD router = 136, `wspecify/SKILL.md` = 117.

---

## Requirement Traceability Update

| Requirement | Previous Status | New Status |
| --- | --- | --- |
| PSK-01 | Verified (slice) | ✅ Verified (integrated) |
| PSK-02 | Verified (slice) | ✅ Verified (integrated) |
| PSK-03 | Verified (slice) | ✅ Verified (integrated) |
| PSK-04 | Verified (slice) | ✅ Verified (integrated) |

---

## Summary

**Overall**: ✅ Ready

**Verdict**: PASS
**Spec-anchored check**: 20/20 ACs matched the spec-defined outcome; 2 spec-precision gaps flagged
**Sensor**: 10/10 mutations killed, 0 survived
**Gate**: `bun run test:all` exit 0 (124 bun pass, all Python suites OK); 6 scoped commands exit 0

**What works**: five phase skills each carry their own procedure under the 200-line cap with their
templates in local `references/`; the router is 136 lines and dispatches by skill name only; Claude
packets declare `skills:` and `disallowedTools:` and sync passes them through byte-identically while
rejecting an unknown or hollow preload skill before any write; the five skills install with the core
adopt layer and resolve through tracked `.claude/skills` symlinks.

**Issues found**: none blocking. Two spec-precision gaps (SP-1 `wdesign` has no preloading agent, so
PSK-01 AC1's wording does not fit it; SP-2 Edge Case 3 promises a message naming both files but the
assertion names one). Both are wording gaps in the spec/test message, not behaviour gaps — no fix
task is required for this feature to close.

**Next steps**: close the feature. If PSK-01 AC1 or Edge Case 3 is reused as a template for a future
phase-skill slice, tighten the wording first.
