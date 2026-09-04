# Specify Impact and Designer Validation (S2)

**Date**: 2026-09-03
**Spec**: `.specs/features/specify-impact-designer/spec.md`
**Diff range**: `c73813a05082dece75e9816b51d04cfb1932905e..HEAD`
**Verifier**: independent sub-agent (author ≠ verifier)
**Verdict**: FAIL

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T3 | ⏭️ S1 | Out of this packet |
| T4 | ✅ Done | Designer in `ROLES` / `DELEGATED_ROLES`; example tables; UT-005, IT-001, IT-002 |
| T5 | ✅ Done | Three templates; adopt `RUNTIME_PATHS`; UT-004, IT-003 |
| T6 | ✅ Done | AGENTS.md 134/134; pack.md five windows; AD-029; UT-006 |

---

## Spec-Anchored Acceptance Criteria

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| SID-03 AC1: `ROLES` includes `designer` for every provider; example carries `[models.<provider>.designer]` with Assumptions models | `designer` in `ROLES` and delegated set; Claude `inherit`/`high`; Codex `gpt-5.6-sol`/`high`; Cursor `claude-fable-5-1-thinking-high`/`high` | `tools/test_workflow_config.py:1798-1805` - `assert "designer" in workflow_config.ROLES` and exact example dicts | ✅ PASS |
| SID-03 AC2: three designer templates; Claude `skills: [wdesign, ponytail]`, no `disallowedTools`; body loads `uiux.md`, `spec.md`, `UI-UX.md`, `FRONTEND.md`; writes `docs/design/` and `uiux-review.md`; never writes product code | All named paths and the no-product-code rule on the role | `tools/test_phase_skills.py:403-417` - skills, no `disallowedTools`, `uiux.md`, `docs/design/`, `uiux-review.md`, Claude never-write, Codex/Cursor `wdesign` | ❌ GAP |
| SID-03 AC3: `--sync-agents` writes the three designer packets; `adopt.py` `RUNTIME_PATHS` lists them | Runtime files exist; Claude `skills:` line byte-identical; three runtime paths and managed templates | `tools/test_workflow_config.py:1842-1851` - three files and `claude_designer_skills == claude_runtime_skills`; `scripts/test_adopt.py:641-651` - path in `RUNTIME_PATHS` and plan `managed` | ✅ PASS |
| SID-03 AC4: missing `[models.<provider>.designer]` → `--sync-agents` non-zero naming that table; nothing written | Any provider table named in stderr; tree unchanged | `tools/test_workflow_config.py:1879-1883` - `returncode != 0` and `"models.claude.designer" in stderr` | ❌ GAP |
| SID-03 AC5: when `uiux.md` exists, `wdesign` dispatches `designer` before internal design; planner keeps the architecture half of `design.md` | Dispatch-before plus architecture ownership | `tools/test_phase_skills.py:376-377` - `"uiux.md" in step1_body` and `"designer" in step1_body` | ❌ GAP |
| SID-03 AC6: `AGENTS.md` names designer and is ≤ 134 lines; `pack.md` names five windows | Designer present; line cap; "five windows" | `tools/test_phase_skills.py:424-430` - `"designer" in agents_text`, `line_count <= 134`, `"five windows" in pack_text` | ✅ PASS |

**Status**: ❌ Gaps present

AC2 asserts a subset of the load/deliver list. Removing `spec.md`, `UI-UX.md`, or `FRONTEND.md` (M6–M8) or Codex's never-write sentence (M12) leaves UT-004 green. AC4 is proven only for `models.claude.designer`; skipping the designer table for Codex/Cursor (M23) survives. AC5 is satisfied by the words `uiux.md` and `designer` in step 1 (M17 survived).

---

## Discrimination Sensor

Scratch: `git worktree add /tmp/sid-s2-sensor.e4vHpC HEAD` (M1–M22) and `/tmp/sid-s2-sensor.m9H12H HEAD` (M23). Targeted tests in scratch. Both worktrees removed with `git worktree remove --force`. Real-tree porcelain before and after: ` M .specs/LESSONS.md` and ` M .specs/lessons.json` (pre-existing S1 lesson distillation; unchanged by the sensor).

| Mutation | File:line | Description | Killed? |
| -------- | --------- | ----------- | ------- |
| M1 | `workflow_config.py:22` | Drop `designer` from `ROLES` | ✅ Killed (`test_workflow_config.py:1798`) |
| M2 | `.my-workflow.toml.example:44` | Claude designer model `inherit` → `claude-sonnet-4-6` | ✅ Killed (`test_workflow_config.py:1803`) |
| M3 | `templates/agents/claude/designer.md:7` | `skills: [wdesign, ponytail]` → `[wdesign]` | ✅ Killed (`test_phase_skills.py:403`) |
| M4 | `templates/agents/claude/designer.md:7` | Add `disallowedTools: Write` | ✅ Killed (`test_phase_skills.py:404`) |
| M5 | `templates/agents/claude/designer.md:15` | Remove `uiux.md` from Load | ✅ Killed (`test_phase_skills.py:409`) |
| M6 | `templates/agents/claude/designer.md:15` | Remove `spec.md`, keep `uiux.md` | ❌ Survived |
| M7 | `templates/agents/claude/designer.md:17` | Remove `FRONTEND.md` | ❌ Survived |
| M8 | `templates/agents/claude/designer.md:16` | Remove `UI-UX.md` | ❌ Survived |
| M9b | `templates/agents/claude/designer.md` | Replace every `docs/design/` | ✅ Killed (`test_phase_skills.py:410`) |
| M10b | `templates/agents/claude/designer.md` | Replace every `uiux-review.md` | ✅ Killed (`test_phase_skills.py:411`) |
| M11 | `templates/agents/codex/designer.toml:11` | `wdesign` → `wspecify` | ✅ Killed (`test_phase_skills.py:415`) |
| M12 | `templates/agents/codex/designer.toml:7` | Remove Codex never-write-product-code | ❌ Survived |
| M13 | `workflow_config.py:565` | Skip `designer` in sync render loop | ✅ Killed (`test_workflow_config.py:1842`) |
| M14 | `scripts/adopt.py:63` | Drop `designer` from `RUNTIME_PATHS` | ✅ Killed (`test_adopt.py:642`) |
| M15 | `workflow_config.py:277` | Missing-table error omits `models.<provider>.<role>` | ✅ Killed (`test_workflow_config.py:1880`) |
| M16 | `workflow_config.py:573` | Missing-template error omits the path | ✅ Killed (`test_workflow_config.py:1902`) |
| M17 | `wdesign/SKILL.md:22` | Keep `uiux.md` and `designer`; drop dispatch-before and architecture ownership | ❌ Survived |
| M18 | `AGENTS.md:13` | Remove designer from the role line | ✅ Killed (`test_phase_skills.py:425`) |
| M19 | `docs/workflow/pack.md:34` | `five windows` → `four windows` | ✅ Killed (`test_phase_skills.py:430`) |
| M20 | `AGENTS.md` | Pad past the 134-line cap | ✅ Killed (`test_phase_skills.py:424`) |
| M21 | `templates/agents/claude/designer.md:10` | Remove Claude never-write phrasings | ✅ Killed (`test_phase_skills.py:412`) |
| M22 | `templates/agents/cursor/designer.md:12` | Cursor `wdesign` → `wspecify` | ✅ Killed (`test_phase_skills.py:417`) |
| M23 | `workflow_config.py:274` | Do not require a designer table for non-Claude providers | ❌ Survived |

Discarded (fault did not remove the asserted token): M9 Deliver-only `docs/design/` rewrite and M10 Deliver-only `uiux-review.md` rewrite still left those strings in Load/Report.

**Sensor depth**: lightweight, 23 valid behaviour-level mutants across SID-03 ACs and EC3 (packet minimum 5)
**Result**: 17/23 killed — FAIL

---

## Interactive UAT Results (if performed)

Not performed. S2 is agent-matrix, templates, and docs. No user-facing product surface.

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ |
| Surgical changes | ✅ |
| No scope creep | ✅ |
| Matches patterns | ✅ |
| Spec-anchored outcome check (asserted values match spec) | ❌ |
| Per-layer Coverage Expectation met (domain 1:1 ACs; routes happy+edge+error) | ❌ |
| Every test maps to a spec requirement - no unclaimed tests | ✅ |
| Documented guidelines followed: `docs/guidelines/TEST-CONTRACT.md` | ❌ |

Diff is 20 files, +348/−29, limited to the role matrix, templates, adopt catalog, role enumerations, and T6 docs/AD-029. UT-004/005/006 and IT-001/002/003 map to named contract ids. They do not assert every AC2 load path, AC5 dispatch/ownership, or AC4 for a non-Claude provider, so those cases fail the hollow-case rule in TEST-CONTRACT.md. IT-001 rewrites a temp Claude designer template when the skills line is missing; UT-004 still owns the source-template skills line.

---

## Edge Cases

- [x] EC1 validator half: Large `## Impact` body `none` accepted (`test_tlc_validators.py:137-144`, `ret == 0`). S1-owned; still true on this tree.
- [ ] EC1 wverify half: `## Impact` `none` means no reruns. No S2 assertion; S1 M12 still applies.
- [ ] EC2: gap hunt finds nothing → one line and proceed. No S2 assertion; S1 residual.
- [x] EC3: missing designer template fails `--sync-agents` naming the path (`test_workflow_config.py:1901-1902`; M16 killed). Proven for the Claude template path only.

---

## Impacted QA Scenarios

| Scenario | Result | Evidence |
| -------- | ------ | -------- |
| `CFG-centralize-agent-model-routing` | pass | `--sync-agents` twice, both exit 0, both `"changed": []`; designer packets listed in `unchanged` (18 runtimes, not the scenario's older "fifteen fields") |
| `ADP-adopt-workflow-safely` | pass | Fresh `python3 scripts/test_adopt.py` exit 0 (85 tests), including IT-003 designer runtime/managed paths and the consumer-config preservation case |
| `QAS-resolve-phase-skill-procedures` | pass | Fresh `python3 tools/test_phase_skills.py` exit 0 (18 passed), including UT-003/004/006 designer wiring |

This is the technical Impact rerun, not a QA Execute session. Live Claude spawn of `designer` with `# Design` in context was not executed.

---

## Gate Check

- **Slice gate**: `python3 tools/test_workflow_config.py && python3 scripts/test_adopt.py && bun test && python3 tools/test_phase_skills.py` — each command exit 0; 61 / 85 / 124 / 18 passed, 0 failed
- **bun test**: exit 0; 124 pass, 0 fail, 1180 expect() calls
- **git diff --check**: exit 0
- **Build complement**: `bun run test:python` — exit 0
- **`--sync-agents` #1**: exit 0; `changed: []` (six designer packets in `unchanged`)
- **`--sync-agents` #2**: exit 0; `changed: []`
- **Test count before S2** (`c73813a`): `test_phase_skills.py` 16, `test_workflow_config.py` 58, `test_adopt.py` 84, bun 124
- **Test count after S2**: 18, 61, 85, bun 124
- **Delta**: +2 phase-skill tests, +3 workflow-config tests, +1 adopt test, bun count unchanged, expect() 1157 → 1180
- **Skipped tests**: none
- **Failures**: none (gates green; sensor and AC evidence fail the slice)

---

## Fix Plans (if issues found)

### Fix 1: Assert every AC2 load and no-product-code clause

- **Root cause**: UT-004 checks `uiux.md`, `docs/design/`, `uiux-review.md`, and Claude never-write. `spec.md`, `UI-UX.md`, `FRONTEND.md`, and Codex/Cursor never-write are untested.
- **Fix task**: Extend `test_designer_templates_and_preload` so each provider body asserts `spec.md`, `docs/guidelines/UI-UX.md`, `docs/guidelines/FRONTEND.md`, and a never-write-product-code phrasing.
- **Verify**: Re-run M6, M7, M8, M12 in a scratch worktree; each must be killed.
- **Done when**: Those clauses have `file:line` assertions; the same faults die.
- **Priority**: Blocker

### Fix 2: Discriminate AC5 dispatch and architecture ownership

- **Root cause**: UT-003 accepts any step-1 occurrence of `uiux.md` and `designer`.
- **Fix task**: Assert the dispatch-before-internal-design clause and that the planner keeps the architecture half of `design.md`.
- **Verify**: M17 is killed.
- **Done when**: AC5 has precise assertions.
- **Priority**: Blocker

### Fix 3: Prove AC4 for more than Claude

- **Root cause**: IT-002 deletes only `[models.claude.designer]`. Skipping the designer table for Codex/Cursor survives.
- **Fix task**: Add a missing-table case for at least one other provider (or loop providers) that expects `models.<provider>.designer` in stderr and nothing written.
- **Verify**: M23 is killed.
- **Done when**: AC4's `<provider>` quantification has evidence beyond Claude.
- **Priority**: Blocker

---

## Requirement Traceability Update

Do not edit `spec.md` in this session.

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| SID-01 | S1 Needs Fix | ⏭️ S1 (out of slice) |
| SID-02 | S1 Needs Fix | ⏭️ S1 (out of slice) |
| SID-03 | Design / Pending | ❌ Needs Fix |

---

## Summary

**Overall**: ❌ Not Ready

**Spec-anchored check**: 3/6 SID-03 ACs matched spec outcome (AC1, AC3, AC6); 3 gaps; 0 spec-precision gaps
**Sensor**: 17/23 mutations killed
**Gate**: slice 61+85+124+18 passed; `git diff --check` clean; sync twice `changed: []`

**What works**: Designer in the matrix and example models, Claude skills/no-disallowedTools, sync render of three packets, adopt runtime paths, missing Claude table/template errors, AGENTS.md cap, pack.md five windows, gates green, sync idempotent.

**Issues found**: Template tests miss AC2 load/no-product-code clauses; wdesign test misses dispatch/ownership; missing-table test is Claude-only.

**Next steps**: Route Fix 1–3 to a new Implementer. Re-verify S2 in a fresh Verifier session. S1 residuals (EC1 wverify, EC2) stay on the S1 fix path.
