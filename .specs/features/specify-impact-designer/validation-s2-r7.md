# Specify Impact and Designer Validation (S2 r7)

**Date**: 2026-09-03
**Spec**: `.specs/features/specify-impact-designer/spec.md`
**Diff range**: `c73813a05082dece75e9816b51d04cfb1932905e..HEAD` (S2 `90986371`, `4ddf8f2c`, `6cb7d1d1`; test-strength batch `cbf455b2` plus later S1 remediations on shared suites; HEAD `0e53f13c`)
**Verifier**: independent sub-agent (author ≠ verifier)
**Verdict**: PASS

The S2 report listed six survivors. The test-strength batch kills all six. Three new unused SID-03 AC-element mutants also die.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T3 | ⏭️ S1 | Out of this packet |
| T4 | ✅ Done | Designer in `ROLES` / `DELEGATED_ROLES`; example tables; UT-005, IT-001, IT-002 |
| T5 | ✅ Done | Three templates; adopt `RUNTIME_PATHS`; UT-004, IT-003 |
| T6 | ✅ Done | AGENTS.md 134/134; pack.md five windows; AD-029; UT-006 |
| TR1 | ✅ Done | Canonical suite kills S2 M6, M7, M8, M12, M17, M23 |

---

## Spec-Anchored Acceptance Criteria

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| SID-03 AC1: `ROLES` includes `designer` as a delegated role for every provider; example carries `[models.<provider>.designer]` with the Assumptions models | `designer` in `ROLES` and `DELEGATED_ROLES`; Claude `inherit`/`high`; Codex `gpt-5.6-sol`/`high`; Cursor `claude-fable-5-1-thinking-high`/`high` | `tools/test_workflow_config.py:1798-1805` - `assert "designer" in workflow_config.ROLES`; `:1799` - `assert "designer" in workflow_config.DELEGATED_ROLES`; `:1803-1805` exact example dicts | ✅ PASS |
| SID-03 AC2: three designer templates; Claude `skills: [wdesign, ponytail]`, no `disallowedTools`; body loads `uiux.md`, `spec.md`, `UI-UX.md`, `FRONTEND.md`; writes `docs/design/` and `uiux-review.md`; never writes product code | All named paths and the no-product-code rule on each provider body | `tools/test_phase_skills.py:521-527` - three files, skills, no `disallowedTools`; `:532-539` - `uiux.md`, `docs/design/`, `uiux-review.md`, Claude Load `spec.md` / `UI-UX.md` / `FRONTEND.md`; `:535` Claude never-write; `:548-552` Codex/Cursor `wdesign` and exact never-write sentences | ✅ PASS |
| SID-03 AC3: `--sync-agents` writes the three designer packets; `adopt.py` `RUNTIME_PATHS` lists them | Runtime files exist; Claude `skills:` line byte-identical; three runtime paths and managed templates | `tools/test_workflow_config.py:1839-1851` - three files and `claude_designer_skills == claude_runtime_skills`; `scripts/test_adopt.py:641-651` - path in `RUNTIME_PATHS` and plan `managed` | ✅ PASS |
| SID-03 AC4: missing `[models.<provider>.designer]` → `--sync-agents` non-zero naming that table; nothing written | Each provider table named in stderr; tree unchanged | `tools/test_workflow_config.py:1863-1886` - loop `PROVIDERS`; `:1882` `returncode != 0`; `:1883` `f"models.{provider}.designer" in stderr`; `:1884` `tree_state` unchanged | ✅ PASS |
| SID-03 AC5: when `uiux.md` exists, `wdesign` dispatches `designer` before internal design; planner keeps the architecture half of `design.md` | Dispatch-before plus architecture ownership | `tools/test_phase_skills.py:488-493` - `"uiux.md"`, `"exists, load it"` on the uiux.md sentence, `"designer"`, `"before internal design"`, `"architecture half"` | ✅ PASS |
| SID-03 AC6: `AGENTS.md` names designer and is ≤ 134 lines; `pack.md` names five windows | Designer present; line cap; "five windows" | `tools/test_phase_skills.py:559-565` - `line_count <= 134`, `"designer" in agents_text`, `"designer" in pack_text`, `"five windows" in pack_text` | ✅ PASS |

**Status**: ✅ All ACs covered

---

## Discrimination Sensor

Scratch: `git worktree add /tmp/sid-s2-r7-sensor.GEHZfo HEAD`. Targeted suites in scratch: `python3 tools/test_phase_skills.py` and `python3 tools/test_workflow_config.py`. Each mutant used unlink + rewrite (new inode). After `git worktree remove --force`, real-tree porcelain matches the pre-sensor baseline: only untracked `validation-s1-r8.md`. S2 implementation and test files match HEAD.

Re-injected every S2 survivor (M6, M7, M8, M12, M17, M23). Did not retry S1 mutants; the latest S1 report lists no survivors. Three new AC-element mutants (N29–N31). None was a prior S2 mutant: N29 deletes Assumptions model `gpt-5.6-sol` (M2 changed Claude `inherit` only); N30 deletes `claude-fable-5-1-thinking-high`; N31 drops `designer` from `DELEGATED_ROLES` (M1 dropped it from `ROLES`).

| Mutation | AC clause | File:line | Description | Killed? |
| -------- | --------- | --------- | ----------- | ------- |
| M6 | SID-03 AC2 `spec.md` | `templates/agents/claude/designer.md:15` | Remove `spec.md` from Claude Load; keep `uiux.md` | ✅ Killed (`test_phase_skills.py:537` `AssertionError: Claude designer Load list missing spec.md`) |
| M7 | SID-03 AC2 `FRONTEND.md` | `templates/agents/claude/designer.md:17` | Remove `FRONTEND.md` from Claude Load | ✅ Killed (`test_phase_skills.py:539` `AssertionError: Claude designer Load list missing FRONTEND.md`) |
| M8 | SID-03 AC2 `UI-UX.md` | `templates/agents/claude/designer.md:16` | Remove `UI-UX.md` from Claude Load | ✅ Killed (`test_phase_skills.py:538` `AssertionError: Claude designer Load list missing UI-UX.md`) |
| M12 | SID-03 AC2 Codex never-write-product-code | `templates/agents/codex/designer.toml:7` | Remove the Codex opening never-write sentence | ✅ Killed (`test_phase_skills.py:549` `AssertionError: Codex designer body missing never-write-product-code`) |
| M17 | SID-03 AC5 before internal design + architecture half | `.agents/skills/wdesign/SKILL.md:22` | Keep `uiux.md` and `designer`; drop dispatch-before and architecture ownership | ✅ Killed (`test_phase_skills.py:492` `AssertionError: wdesign step 1 does not dispatch designer before internal design`) |
| M23 | SID-03 AC4 `[models.<provider>.designer]` for every provider | `workflow_config.py:274` | Do not require a designer table for non-Claude providers | ✅ Killed (`test_workflow_config.py:1883` `assert f"models.{provider}.designer" in completed.stderr`; Codex path KeyErrors after the missing-role skip) |
| N29 | SID-03 AC1 Assumptions model `gpt-5.6-sol` | `.my-workflow.toml.example:68` | Delete `gpt-5.6-sol` from `[models.codex.designer]` | ✅ Killed (`test_workflow_config.py:1801` `_load_config` raises `models.codex.designer.model is required`; `:1804` would also fail) |
| N30 | SID-03 AC1 Assumptions model `claude-fable-5-1-thinking-high` | `.my-workflow.toml.example:92` | Delete `claude-fable-5-1-thinking-high` from `[models.cursor.designer]` | ✅ Killed (`test_workflow_config.py:1801` `_load_config` raises `models.cursor.designer.model is required`; `:1805` would also fail) |
| N31 | SID-03 AC1 delegated role | `workflow_config.py:23` | Drop `designer` from `DELEGATED_ROLES`; keep it in `ROLES` | ✅ Killed (`test_workflow_config.py:1799` `assert "designer" in workflow_config.DELEGATED_ROLES`) |

**Sensor depth**: lightweight, 9 behaviour-level mutants (6 S2 survivors re-injected + 3 new unused AC elements)
**Result**: 9/9 killed — PASS

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
| Spec-anchored outcome check (asserted values match spec) | ✅ |
| Per-layer Coverage Expectation met (domain 1:1 ACs; routes happy+edge+error) | ✅ |
| Every test maps to a spec requirement - no unclaimed tests | ✅ |
| Documented guidelines followed: `docs/guidelines/TEST-CONTRACT.md` | ✅ |

S2 product diff remains the role matrix, three templates, adopt catalog, role enumerations, and T6 docs/AD-029. TR1 only strengthened the canonical suites. UT-004 now asserts every AC2 load path and each provider's never-write sentence. UT-003 asserts AC5 dispatch-before and architecture ownership. IT-002 loops every provider. No unclaimed tests.

---

## Edge Cases

- [x] EC1 validator half: Large `## Impact` body `none` accepted (`test_tlc_validators.py:157-160`, `ret == 0`). S1-owned; still true on this tree.
- [ ] EC1 wverify half: `## Impact` `none` means no reruns. S1 residual (`validation-s1-r8.md` covers it); not an S2 AC.
- [ ] EC2: gap hunt finds nothing → one line and proceed. S1 residual; not an S2 AC.
- [x] EC3: missing designer template fails `--sync-agents` naming the path (`test_workflow_config.py:1903-1905`; S2 M16 killed). Proven for the Claude template path.

---

## Impacted QA Scenarios

| Scenario | Result | Evidence |
| -------- | ------ | -------- |
| `CFG-centralize-agent-model-routing` | pass | `--sync-agents` twice, both exit 0, both `"changed": []`; six designer packets listed in `unchanged` (18 runtimes) |
| `ADP-adopt-workflow-safely` | pass | Fresh `python3 scripts/test_adopt.py` exit 0 (85 tests), including IT-003 designer runtime/managed paths |
| `QAS-resolve-phase-skill-procedures` | pass | Fresh `python3 tools/test_phase_skills.py` exit 0 (18 passed), including UT-003/004/006 designer wiring |

This is the technical Impact rerun, not a QA Execute session. Live Claude spawn of `designer` with `# Design` in context was not executed.

---

## Gate Check

- **Gate command**: `python3 tools/test_workflow_config.py && python3 scripts/test_adopt.py && bun test && python3 tools/test_phase_skills.py && git diff --check`
- **Result**: 61 + 85 + 124 + 18 passed, 0 failed, 0 skipped; `git diff --check` exit 0
- **bun test**: exit 0; 124 pass, 0 fail, 1180 expect() calls
- **`--sync-agents` #1**: exit 0; `changed: []` (six designer packets in `unchanged`)
- **`--sync-agents` #2**: exit 0; `changed: []`
- **Test count before S2** (`c73813a0`): `test_phase_skills.py` 16, `test_workflow_config.py` 58, `test_adopt.py` 84, bun 124
- **Test count after S2 + batch** (HEAD): 18, 61, 85, bun 124
- **Delta**: +2 phase-skill tests, +3 workflow-config tests, +1 adopt test, bun count unchanged
- **Skipped tests**: none
- **Failures**: none

---

## Fix Plans (if issues found)

None. All six S2 survivors are dead. The three new unused AC-element mutants are dead.

---

## Requirement Traceability Update

Do not edit `spec.md` in this session.

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| SID-01 | S1 Verified (`validation-s1-r8.md`) | ⏭️ S1 (out of slice) |
| SID-02 | S1 Verified (`validation-s1-r8.md`) | ⏭️ S1 (out of slice) |
| SID-03 | ❌ Needs Fix (`validation-s2.md`) | ✅ Verified |

---

## Summary

**Overall**: ✅ Ready

**Spec-anchored check**: 6/6 SID-03 ACs matched spec outcome; 0 spec-precision gaps
**Sensor**: 9/9 mutations killed
**Gate**: slice 61+85+124+18 passed; `git diff --check` clean; sync twice `changed: []`

**What works**: Designer in the matrix and delegated set, Assumptions models, Claude skills/no-disallowedTools, every AC2 load path, each provider never-write, sync render of three packets, adopt runtime and managed paths, missing-table errors for every provider, wdesign dispatch-before and architecture ownership, AGENTS.md cap, pack.md five windows, gates green, sync idempotent.

**Issues found**: none for S2. S1 residuals EC1 wverify / EC2 stay on the S1 record.

**Next steps**: S2 checkpoint is verified. Integrated feature `validation.md` waits until both slices are closed together.
