# Specify Impact and Designer Validation

**Date**: 2026-09-03
**Spec**: `.specs/features/specify-impact-designer/spec.md`
**Diff range**: `origin/main..HEAD` (`3bb242af..89800fa1`)
**HEAD**: `89800fa1dbdfa4e69e0628c5cecd44c2a1cfdd39`
**Verifier**: independent sub-agent (author ≠ verifier)
**Verdict**: PASS

Feature close over SID-01..03. Latest slice reports (`validation-s1-r8.md`, `validation-s2-r7.md`) listed no survivors, so none were re-injected. Seven new unused AC-element deletions, at least two per requirement, all die. Prior evidence cited: `validation-s1-r7.md`, `validation-s2-r7.md`, `.deep-review/specify-impact-designer/review.md` (SHIP, 0 defects), `docs/qa/reports/2026-09-03-specify-impact-designer.md` (all named scenarios pass).

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1 | ✅ Done | Impact, uiux.md, gap-hunt in wspecify; `wc -l` 140 ≤ 200 |
| T2 | ✅ Done | wdesign step 1, wverify 3.5, UI-UX.md timing |
| T3 | ✅ Done | Size-aware Impact in `validate_spec.py`; Small fixture present; this feature spec exits 0 |
| T4 | ✅ Done | Designer in `ROLES` / `DELEGATED_ROLES`; example tables; UT-005, IT-001, IT-002 |
| T5 | ✅ Done | Three templates; adopt `RUNTIME_PATHS`; UT-004, IT-003 |
| T6 | ✅ Done | AGENTS.md 134/134; pack.md five windows; AD-029; UT-006 |
| TR1 | ✅ Done | Canonical suite kills the listed S1/S2 rule-sentence set |
| TR2 | ✅ Done | N5–N8 remain dead |

---

## Spec-Anchored Acceptance Criteria

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| SID-01 AC1: Impact step after dimensions, before user stories; two explorers; write `## Impact` listing features, pages, and scenario ids | Procedure contains that step, both explorer traces (including jobs, events, QA scenarios), and the listing rule | `tools/test_phase_skills.py:388` - `assert impact_idx < user_stories_idx`; `:393` - `assert sweep_idx < impact_heading_idx`; `:409-415` - two explorers, data/model, pages/journeys/QA, journeys, jobs, events, QA scenarios; `:416-420` - `## Impact`, `affected features`, `pages` on the listing line, `scenario ids` | ✅ PASS |
| SID-01 AC2: WHEN Impact lists an affected feature THEN one ubiquitous no-regression AC | Skill instructs a ubiquitous unchanged-behaviour AC per listed feature | `tools/test_phase_skills.py:421-423` - `"For each affected feature listed"` / `"ubiquitous acceptance criterion"` / `"behaviour is unchanged"` | ✅ PASS |
| SID-01 AC3: uiux.md step after ACs, before closure, only when a screen is added or changed, follows UI-UX.md | Ordered uiux.md step with the screen gate and the guideline path | `tools/test_phase_skills.py:403` - `assert ac_idx < uiux_idx < closure_idx`; `:426` - `"Only when a screen is added or changed"`; `:427` - `"docs/guidelines/UI-UX.md" in uiux_body` | ✅ PASS |
| SID-01 AC4: UI-UX.md says uiux.md is written in Specify; wdesign step 1 loads uiux.md when present | Exact phrase plus step-1 load of uiux.md on the uiux.md sentence | `tools/test_phase_skills.py:512` - `"written in Specify" in uiux_guideline`; `:488` - `"uiux.md" in step1_body`; `:490` - `"exists, load it" in uiux_sentence` | ✅ PASS |
| SID-01 AC5: wverify reruns Impact scenario ids and reports pass, fail, or untested | Rerun named ids; report those three statuses; `none` means no reruns | `tools/test_phase_skills.py:502-505` - `"scenario ids"` / `"## Impact"` / `"pass, fail, or untested"` / `"no reruns"` in `heading_body(..., "### 3.5.")` | ✅ PASS |
| SID-01 AC6: Large/Complex without Impact exit 1 naming the section; Medium/Small do not require it | Large and Complex reject naming `## Impact`; Medium and Small accept; `none` body accepted | `tools/test_tlc_validators.py:121-124` Large `"Impact" in error` and `ret == 1`; `:122` - `"missing required section: ## Impact"`; `:130-133` Complex; `:139-142` Medium `ret == 0`; `:147-150` Small `ret == 0`; `:157-160` `none` `ret == 0` | ✅ PASS |
| SID-01 AC7: spec-template has `## Impact` between Assumptions and User Stories | Heading order in the template | `tools/test_phase_skills.py:475` - `assert impact_idx != -1`; `:477` - `assert assumptions_idx < impact_idx < stories_idx` | ✅ PASS |
| SID-02 AC1: gap-hunt step at plan approval; skip Small; ask Medium/Large; recommend Complex; cite `references/gap-hunt.md` | Sizing rule plus citation; reference exists | `tools/test_phase_skills.py:405-406` citation and file exists; `:431` plan-approval cite; `:432-434` Small-skip / Medium-Large-ask / Complex-recommend in SKILL.md; `:445-447` same three in `gap-hunt.md` | ✅ PASS |
| SID-02 AC2: WHEN accepted THEN two explorers and numbered frontier questions each with a recommended answer | Two named explorers plus recommended-answer rounds | `tools/test_phase_skills.py:452-459` two explorers, unhappy paths, current behaviour, QA scenarios, domain/data, numbered questions, frontier; `:461` - `"each providing a concrete recommended answer" in procedure_line` | ✅ PASS |
| SID-02 AC3: WHEN a round settles THEN AC or `context.md` decision, never a note | Settlement must be an AC or a context.md record | `tools/test_phase_skills.py:462-464` - `"acceptance criterion"` / `"context.md"` / `"Never leave a settled finding as an informal note"` | ✅ PASS |
| SID-02 AC4: WHILE autonomous, run only for Complex and record the skip in `decisions.md` | Autonomous skip rule | `tools/test_phase_skills.py:436` - `"only for Complex"`; `:438` - `"decisions.md"` in `gap_offer`; `:449-450` same in `gap-hunt.md` | ✅ PASS |
| SID-03 AC1: `ROLES` includes `designer` as a delegated role for every provider; example carries `[models.<provider>.designer]` with the Assumptions models | `designer` in `ROLES` and `DELEGATED_ROLES`; Claude `inherit`/`high`; Codex `gpt-5.6-sol`/`high`; Cursor `claude-fable-5-1-thinking-high`/`high` | `tools/test_workflow_config.py:1798-1805` - `assert "designer" in workflow_config.ROLES`; `:1799` - `DELEGATED_ROLES`; `:1803-1805` exact example dicts | ✅ PASS |
| SID-03 AC2: three designer templates; Claude `skills: [wdesign, ponytail]`, no `disallowedTools`; body loads `uiux.md`, `spec.md`, `UI-UX.md`, `FRONTEND.md`; writes `docs/design/` and `uiux-review.md`; never writes product code | All named paths and the no-product-code rule on each provider body | `tools/test_phase_skills.py:521-527` - three files, skills, no `disallowedTools`; `:532-539` - `uiux.md`, `docs/design/`, `uiux-review.md`, Claude Load `spec.md` / `UI-UX.md` / `FRONTEND.md`; `:535` Claude never-write; `:548-552` Codex/Cursor `wdesign` and exact never-write sentences | ✅ PASS |
| SID-03 AC3: `--sync-agents` writes the three designer packets; `adopt.py` `RUNTIME_PATHS` lists them | Runtime files exist; Claude `skills:` line byte-identical; three runtime paths and managed templates | `tools/test_workflow_config.py:1823-1832` - three files and `claude_designer_skills == claude_runtime_skills`; `scripts/test_adopt.py:641-651` - path in `RUNTIME_PATHS` and plan `managed` | ✅ PASS |
| SID-03 AC4: missing `[models.<provider>.designer]` → `--sync-agents` non-zero naming that table; nothing written | Each provider table named in stderr; tree unchanged | `tools/test_workflow_config.py:1863-1865` - loop `PROVIDERS`; `:1863` `returncode != 0`; `:1864` `f"models.{provider}.designer" in stderr`; `:1865` `tree_state` unchanged | ✅ PASS |
| SID-03 AC5: when `uiux.md` exists, `wdesign` dispatches `designer` before internal design; planner keeps the architecture half of `design.md` | Dispatch-before plus architecture ownership | `tools/test_phase_skills.py:488-493` - `"uiux.md"`, `"exists, load it"` on the uiux.md sentence, `"designer"`, `"before internal design"`, `"architecture half"` | ✅ PASS |
| SID-03 AC6: `AGENTS.md` names designer and is ≤ 134 lines; `pack.md` names five windows | Designer present; line cap; "five windows" | `tools/test_phase_skills.py:559-565` - `line_count <= 134`, `"designer" in agents_text`, `"designer" in pack_text`, `"five windows" in pack_text` | ✅ PASS |

**Status**: ✅ All ACs covered

### Success Criteria

| Criterion | Evidence | Result |
| --------- | -------- | ------ |
| A Large spec without `## Impact` fails the validator; this feature's own spec passes | Fresh `validate_spec.py` on `spec-size-large-no-impact.md` names `## Impact` and exits 1 (`test_tlc_validators.py:121-124`); this feature spec exits 0 | ✅ PASS |
| A spawned `designer` reports `# Design` present and `wdesign` in its preload | Packet preload is `skills: [wdesign, ponytail]` (`.claude/agents/designer.md:7`; `templates/agents/claude/designer.md:7`); `wdesign/SKILL.md:10` is `# Design`. Live Claude spawn was not executed this session | ✅ PASS (structural; spawn untested) |

---

## Discrimination Sensor

Scratch: `git worktree add /tmp/sid-feature-sensor HEAD`. Targeted suite in scratch: `python3 tools/test_phase_skills.py`. Scratch baseline: 18 passed.

Each mutant used unlink + rewrite (new inode). After `git worktree remove --force`, real-tree porcelain matches the pre-sensor baseline: only untracked `validation-s1-r8.md`. Implementation and test files match HEAD.

Latest S1 (`validation-s1-r8.md`) and S2 (`validation-s2-r7.md`) listed 0 survivors, so 0 re-injects. Did not retry the six prior S1 reports' killed mutants (`validation-s1.md` through `validation-s1-r6.md`). Seven new AC-element deletions (N32–N38). None was a prior-report mutant: N32 deletes explorer `QA scenarios` (N9/N21/N23 were jobs/events/journeys); N33 deletes listing `scenario ids` (N3 dropped the whole listing; N8 dropped pages); N34 moves template `## Impact` after User Stories; N35 deletes `frontier rounds`; N36 deletes unhappy-path `QA scenarios` (N25 dropped current behaviour); N37 deletes Cursor never-write (M12 was Codex; M21 was Claude); N38 deletes `architecture half` alone (M17 dropped dispatch-before and architecture together).

| Mutation | AC clause | File:line | Description | Killed? |
| -------- | --------- | --------- | ----------- | ------- |
| N32 | SID-01 AC1 explorer list includes QA scenarios | `wspecify/SKILL.md:68` | Drop `QA scenarios` from the pages/journeys explorer trace; keep pages, journeys, jobs, events | ✅ Killed (`test_phase_skills.py:411` `AssertionError: Impact step missing the pages/journeys/QA explorer trace`) |
| N33 | SID-01 AC1 listing names scenario ids | `wspecify/SKILL.md:70` | Drop `scenario ids` from the Impact listing; keep features and pages | ✅ Killed (`test_phase_skills.py:420` `AssertionError: Impact step does not list scenario ids`) |
| N34 | SID-01 AC7 `## Impact` between Assumptions and User Stories | `spec-template.md:40` | Move the `## Impact` block after User Stories | ✅ Killed (`test_phase_skills.py:477` `AssertionError: template must have ## Impact between Assumptions and User Stories`) |
| N35 | SID-02 AC2 numbered questions in frontier rounds | `wspecify/SKILL.md:123` and `gap-hunt.md:25-27` | Drop `frontier` / `Frontier Rounds` from the skill and the procedure heading | ✅ Killed (`test_phase_skills.py:440` `AssertionError: wspecify missing frontier rounds at plan approval`) |
| N36 | SID-02 AC2 unhappy paths against QA scenarios | `gap-hunt.md:20` | Drop `QA scenarios` from the unhappy-paths explorer line; keep current behaviour | ✅ Killed (`test_phase_skills.py:456` `AssertionError: unhappy-paths explorer missing QA scenarios`) |
| N37 | SID-03 AC2 Cursor never writes product code | `templates/agents/cursor/designer.md:8` | Delete both Cursor never-write sentences | ✅ Killed (`test_phase_skills.py:552` `AssertionError: Cursor designer body missing never-write-product-code`) |
| N38 | SID-03 AC5 architecture half of `design.md` | `wdesign/SKILL.md:22` | Drop `architecture half`; keep `uiux.md`, designer, and before internal design | ✅ Killed (`test_phase_skills.py:493` `AssertionError: wdesign step 1 does not keep the architecture half with the planner`) |

**Sensor depth**: lightweight, 7 behaviour-level mutants (0 survivors re-injected + 7 new unused AC elements)
**Result**: 7/7 killed — PASS

Minor precision note (not a survivor): N35 still leaves `the frontier` on `gap-hunt.md:27` and `:35`, so `:459` (`"frontier" in hunt`) would not have killed a gap-hunt-only deletion of `frontier rounds`. `:440` did. Every test was not green.

---

## Interactive UAT Results (if performed)

Not performed. This feature is procedure, validator, agent-matrix, and docs. User-visible walk already recorded in `docs/qa/reports/2026-09-03-specify-impact-designer.md`.

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ |
| Surgical changes | ✅ |
| No scope creep | ✅ |
| Matches patterns | ✅ |
| Spec-anchored outcome check (asserted values match spec) | ✅ |
| Per-layer Coverage Expectation met (domain 1:1 ACs; routes happy+edge+error) | ✅ |
| Every test maps to a spec requirement - no unclaimed tests | ✅ |
| Documented guidelines followed: `docs/guidelines/TEST-CONTRACT.md` | ✅ |

Product surface is skill text, validator + five size fixtures, role matrix, three designer templates, adopt catalog, and T6 docs/AD-029. UT-001..UT-006 and IT-001..IT-003 map to SID-01..03. Deep review SHIP (`review.md`).

---

## Edge Cases

- [x] EC1 validator half: Large `## Impact` body `none` accepted (`test_tlc_validators.py:153-160`, `ret == 0`)
- [x] EC1 wverify half: `## Impact` `none` means no reruns (`test_phase_skills.py:505`)
- [x] EC2: gap hunt finds nothing → one line and proceed (`test_phase_skills.py:437` and `:465`)
- [x] EC3: missing designer template fails `--sync-agents` naming the path (`test_workflow_config.py:1884-1885`; Claude template path)

---

## Impacted QA Scenarios

| Scenario | Result | Evidence |
| -------- | ------ | -------- |
| `CFG-centralize-agent-model-routing` | pass | Fresh `--sync-agents` twice, both exit 0, both `"changed": []` (six designer packets in `unchanged`); `python3 tools/test_workflow_config.py` exit 0 (61 passed); QA execute report pass |
| `ADP-adopt-workflow-safely` | pass | Fresh `python3 scripts/test_adopt.py` exit 0 (85 tests), including IT-003; QA execute report pass |
| `QAS-resolve-phase-skill-procedures` | pass | Fresh `python3 tools/test_phase_skills.py` exit 0 (18 passed), including `references/gap-hunt.md` existence; QA execute report pass |

This is the technical Impact rerun plus citation of `docs/qa/reports/2026-09-03-specify-impact-designer.md`. Live Claude spawn of `designer` was not executed.

---

## Gate Check

- **Gate command**: `bun run test:all && python3 tools/test_phase_skills.py && python3 tools/test_tlc_validators.py && python3 tools/test_workflow_config.py && python3 scripts/test_adopt.py && git diff --check` plus `validate_spec.py` and `validate_tasks.py` on `.specs/features/specify-impact-designer`
- **Result**: all named commands exit 0; 0 failed, 0 skipped
- **`bun run test:all`**: exit 0; bun `124 pass`, `0 fail`, `1180 expect() calls`; python lanes include adopt 85, phase-skills 18, tlc-validators 40, workflow-config 61
- **`python3 tools/test_phase_skills.py`**: exit 0; `18 passed, 0 failed`
- **`python3 tools/test_tlc_validators.py`**: exit 0; `Ran 40 tests` OK
- **`python3 tools/test_workflow_config.py`**: exit 0; `61 passed, 0 failed`
- **`python3 scripts/test_adopt.py`**: exit 0; `ok (85 tests)`
- **`git diff --check`**: exit 0
- **This feature spec**: `python3 .agents/skills/workflow-spec-driven/scripts/validate_spec.py .specs/features/specify-impact-designer` — exit 0
- **This feature tasks**: `python3 .agents/skills/workflow-spec-driven/scripts/validate_tasks.py .specs/features/specify-impact-designer` — exit 0
- **`--sync-agents` #1**: exit 0; `changed: []`
- **`--sync-agents` #2**: exit 0; `changed: []`
- **Test count before feature** (`3bb242af` / S2 pre `c73813a0`, from `validation-s1-r7.md` and `validation-s2-r7.md`): `test_phase_skills.py` 13, `test_tlc_validators.py` 35, `test_workflow_config.py` 58, `test_adopt.py` 84, bun 124
- **Test count after feature** (HEAD, this session): 18, 40, 61, 85, bun 124
- **Delta**: +5 phase-skill, +5 validator, +3 workflow-config, +1 adopt, bun unchanged
- **Skipped tests**: none
- **Failures**: none

---

## Fix Plans (if issues found)

None. Zero survivors. N35 leftover `the frontier` on other lines is a Minor precision note.

---

## Requirement Traceability Update

Do not edit `spec.md` in this session.

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| SID-01 | ✅ Verified (`validation-s1-r7.md` / `validation-s1-r8.md`) | ✅ Verified (N32–N34 killed) |
| SID-02 | ✅ Verified (`validation-s1-r7.md` / `validation-s1-r8.md`) | ✅ Verified (N35–N36 killed) |
| SID-03 | ✅ Verified (`validation-s2-r7.md`) | ✅ Verified (N37–N38 killed) |

---

## Summary

**Overall**: ✅ Ready

**Spec-anchored check**: 17/17 ACs matched spec outcome; 0 spec-precision gaps
**Sensor**: 7/7 mutations killed
**Gate**: named commands all exit 0

**What works**: Impact mapping, size-aware validator, uiux.md timing, gap hunt, designer matrix/templates/sync/adopt, wdesign dispatch, AGENTS.md/pack.md, gates green, sync idempotent. Seven unused AC-element deletions die.

**Issues found**: none that fail the feature. Minor: `frontier` substring on gap-hunt.md still satisfies `:459` after `frontier rounds` is gone.

**Next steps**: feature-level `validation.md` is the integrated close record.
