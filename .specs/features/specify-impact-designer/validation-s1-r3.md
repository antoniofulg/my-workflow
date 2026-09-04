# Specify Impact and Designer Validation (S1 r3)

**Date**: 2026-09-03
**Spec**: `.specs/features/specify-impact-designer/spec.md`
**Diff range**: `3bb242af781c3ca6816c8eb40271d85ec973cd8b..HEAD` (S1 `84846af1`, `f8a0fae6`, `dd2b36a8`; test-strength `cbf455b2`)
**Verifier**: independent sub-agent (author ≠ verifier)
**Verdict**: FAIL

The test-strength batch kills every r1 survivor (M6–M13) and the r2 mutants that batch targeted (N2–N4). Four new mutants on remaining spec clauses still survive: SID-02 AC1 size-tier offer rules, SID-01 AC1 `pages` in the Impact listing, and SID-01 AC3 `follows docs/guidelines/UI-UX.md`. A survivor on a spec AC is a FAIL.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1 | ✅ Done | Impact, uiux.md, gap-hunt in wspecify; `wc -l` 142 ≤ 200 |
| T2 | ✅ Done | wdesign step 1, wverify 3.5, UI-UX.md timing |
| T3 | ✅ Done | Size-aware Impact in `validate_spec.py`; Small fixture present; this feature spec exits 0 |
| TR1 | ⚠️ Partial | Canonical suite now kills M6–M13 and N2–N4; N5–N8 still survive |
| T4–T6 | ⏭️ S2 | Not in this packet |

---

## Spec-Anchored Acceptance Criteria

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| SID-01 AC1: Impact step after dimensions, before user stories; two explorers; write `## Impact` listing features, pages, and scenario ids | Procedure contains that step, both explorer traces, and the listing rule | `tools/test_phase_skills.py:360` - `assert impact_idx < user_stories_idx`; `:376-377` - `"Data and model dependencies"` / `"Pages, journeys, and QA scenarios"`; `:378-379` - `"affected features"` / `"scenario ids"` | ❌ GAP |
| SID-01 AC2: WHEN Impact lists an affected feature THEN one ubiquitous no-regression AC | Skill instructs a ubiquitous unchanged-behaviour AC per listed feature | `tools/test_phase_skills.py:380-381` - `"ubiquitous acceptance criterion"` and `"behaviour is unchanged"` | ✅ PASS |
| SID-01 AC3: uiux.md step after ACs, before closure, only when a screen is added or changed, follows UI-UX.md | Ordered uiux.md step with the screen gate and the guideline path | `tools/test_phase_skills.py:370` - `assert ac_idx < uiux_idx < closure_idx`; `:384` - `"Only when a screen is added or changed"` | ❌ GAP |
| SID-01 AC4: UI-UX.md says uiux.md is written in Specify; wdesign step 1 loads uiux.md when present | Exact phrase plus step-1 load | `tools/test_phase_skills.py:420` - `assert "uiux.md" in step1_body`; `:438` - `assert "written in Specify" in uiux_guideline` | ✅ PASS |
| SID-01 AC5: wverify reruns Impact scenario ids and reports pass, fail, or untested | Rerun named ids; report those three statuses; `none` means no reruns | `tools/test_phase_skills.py:432-433` - `"pass, fail, or untested"` and `"no reruns"` in `heading_body(..., "### 3.5.")` | ✅ PASS |
| SID-01 AC6: Large/Complex without Impact exit 1 naming the section; Medium/Small do not require it | Large and Complex reject; Medium and Small accept; `none` body accepted | `tools/test_tlc_validators.py:116-118` Large `"Impact" in error` and `ret == 1`; `:124-126` Complex; `:132-135` Medium `ret == 0`; `:137-144` Small `ret == 0`; `:146-153` `none` `ret == 0` | ✅ PASS |
| SID-01 AC7: spec-template has `## Impact` between Assumptions and User Stories | Heading order in the template | `tools/test_phase_skills.py:409` - `assert assumptions_idx < impact_idx < stories_idx` | ✅ PASS |
| SID-02 AC1: gap-hunt step at plan approval; skip Small; ask Medium/Large; recommend Complex; cite `references/gap-hunt.md` | Sizing rule plus citation; reference exists | `tools/test_phase_skills.py:372-373` - `"references/gap-hunt.md" in text` and file exists; `:387` - `"only for Complex"` (autonomous only) | ❌ GAP |
| SID-02 AC2: WHEN accepted THEN two explorers and numbered frontier questions each with a recommended answer | Two named explorers plus recommended-answer rounds | `tools/test_phase_skills.py:392-394` - `"Unhappy paths explorer"` / `"Domain & data gaps explorer"` / `"recommended answer"` | ✅ PASS |
| SID-02 AC3: WHEN a round settles THEN AC or `context.md` decision, never a note | Settlement must be an AC or a context/decisions record | `tools/test_phase_skills.py:395-397` - `"acceptance criterion"` / `"context.md"` / `"Never leave a settled finding as an informal note"` | ✅ PASS |
| SID-02 AC4: WHILE autonomous, run only for Complex and record the skip in `decisions.md` | Autonomous skip rule | `tools/test_phase_skills.py:387` - `"only for Complex"`; `:389` - `"decisions.md"` | ✅ PASS |

**Status**: ❌ Gaps present

AC1 explorers, features, and scenario ids are asserted; dropping `pages/routes` from the listing survived (N8). AC3 order and screen gate are asserted and N2 is killed; dropping `following docs/guidelines/UI-UX.md` survived (N7). SID-02 AC1 citation and autonomous-only-Complex are asserted; skip-Small / ask-Medium-Large / recommend-Complex survived in both `SKILL.md` (N5) and `gap-hunt.md` (N6).

---

## Discrimination Sensor

Scratch: `git worktree add /tmp/sid-s1-r3-sensor.k7pQ2w HEAD`. Gate in scratch: `python3 tools/test_phase_skills.py && python3 tools/test_tlc_validators.py`. Scratch baseline: 18 passed, 40 unittest OK. Real tree porcelain empty before and after `git worktree remove --force`.

Re-injected every r1 survivor (M6–M13) plus seven new mutants (N2–N8). N2–N4 repeat the r2 probes the batch claimed to lock.

| Mutation | File:line | Description | Killed? |
| -------- | --------- | ----------- | ------- |
| M6 | `wspecify/SKILL.md:70` | Remove ubiquitous no-regression AC instruction | ✅ Killed (`test_phase_skills.py:380-381`) |
| M7 | `validate_spec.py:167` | Require Impact for Small | ✅ Killed (`test_tlc_validators.py:141` `AssertionError: Lists differ: ['missing required section: ## Impact'] != []`) |
| M8 | `gap-hunt.md:39-43` | Settlement becomes notes | ✅ Killed (`test_phase_skills.py:395-397`) |
| M9 | `wspecify/SKILL.md:66-68` | Drop two-explorer Impact dispatch, keep heading | ✅ Killed (`test_phase_skills.py:376-377`) |
| M10 | `wspecify/SKILL.md:123` | Drop autonomous-only-Complex rule | ✅ Killed (`test_phase_skills.py:387`) |
| M11 | `wspecify/SKILL.md:125` | Drop one-line empty gap-hunt proceed rule | ✅ Killed (`test_phase_skills.py:388`) |
| M12 | `wverify/SKILL.md:69` | Drop Impact rerun body; leave heading | ✅ Killed (`test_phase_skills.py:432-433`) |
| M13 | `gap-hunt.md:19-27` | Drop two explorers and recommended-answer rounds | ✅ Killed (`test_phase_skills.py:392-394`) |
| N2 | `wspecify/SKILL.md:97` | Remove screen-only gate from uiux.md step | ✅ Killed (`test_phase_skills.py:384`) |
| N3 | `wspecify/SKILL.md:70` | Drop Impact listing of features, pages, and scenario ids | ✅ Killed (`test_phase_skills.py:378-379`) |
| N4 | `wverify/SKILL.md:69` | Drop none-means-no-reruns clause; keep pass/fail/untested | ✅ Killed (`test_phase_skills.py:433`) |
| N5 | `wspecify/SKILL.md:120-122` | Drop Small-skip / Medium-Large-ask / Complex-recommend sizing | ❌ Survived |
| N6 | `gap-hunt.md:7-11` | Drop Small / Medium-Large / Complex sizing from gap-hunt.md | ❌ Survived |
| N7 | `wspecify/SKILL.md:97` | Drop `following docs/guidelines/UI-UX.md` from the uiux.md step | ❌ Survived |
| N8 | `wspecify/SKILL.md:70` | Drop `pages/routes` from the Impact listing; keep features and scenario ids | ❌ Survived |

**Sensor depth**: lightweight, 15 behaviour-level mutants (8 r1 survivors re-injected + 7 new)
**Result**: 11/15 killed — FAIL ❌

---

## Interactive UAT Results (if performed)

Not performed. S1 is procedure and validator text, not a user-facing product surface.

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

S1 + batch surface is skill text, the validator, five size fixtures, and the two unit files. UT-001 now covers Large, Complex, Medium, Small, and `none`. UT-002/003 now pin the r1/r2 clauses. They still omit SID-02 AC1 offer sizing, the AC1 `pages` noun, and the AC3 guideline path, so those clauses remain hollow under TEST-CONTRACT.md.

---

## Edge Cases

- [x] EC1 validator half: Large `## Impact` body `none` accepted (`test_tlc_validators.py:146-153`, `ret == 0`)
- [x] EC1 wverify half: `## Impact` `none` means no reruns (`test_phase_skills.py:433`; N4 killed)
- [x] EC2: gap hunt finds nothing → one line and proceed (`test_phase_skills.py:388`; M11 killed)
- [ ] EC3: missing designer template fails `--sync-agents` naming the path — S2 / SID-03; no S1 evidence

---

## Impacted QA Scenarios

| Scenario | Result | Evidence |
| -------- | ------ | -------- |
| `QAS-resolve-phase-skill-procedures` | pass | Fresh `python3 tools/test_phase_skills.py` exit 0 (18 passed), including path existence for `references/gap-hunt.md` |
| `CFG-centralize-agent-model-routing` | pass | `--sync-agents` twice, both exit 0, both `"changed": []` |
| `ADP-adopt-workflow-safely` | untested | S1 and the test-strength batch did not change `scripts/adopt.py`; no disposable adopt walk this session |

---

## Gate Check

- **Gate command**: `python3 tools/test_phase_skills.py && python3 tools/test_tlc_validators.py && bun test && git diff --check`
- **Result**: 18 + 40 + 124 passed, 0 failed, 0 skipped
- **`python3 tools/test_phase_skills.py`**: exit 0; `18 passed, 0 failed`
- **`python3 tools/test_tlc_validators.py`**: exit 0; `Ran 40 tests in 0.107s` OK
- **`bun test`**: exit 0; `124 pass`, `0 fail`, `1180 expect() calls`
- **`git diff --check`**: exit 0
- **This feature spec**: `python3 .agents/skills/workflow-spec-driven/scripts/validate_spec.py .specs/features/specify-impact-designer/spec.md` — exit 0
- **`--sync-agents` #1**: exit 0; `changed: []`
- **`--sync-agents` #2**: exit 0; `changed: []`
- **Test count before feature** (`3bb242af`): `test_phase_skills.py` 13, `test_tlc_validators.py` 35, bun 124
- **Test count after feature** (HEAD): 18, 40, 124
- **Delta**: +5 phase-skill tests (3 S1 + 2 S2), +5 validator tests (4 original size cases + Small), bun count unchanged
- **Skipped tests**: none
- **Failures**: none (gates green; sensor survivors on spec ACs fail the slice)

---

## Fix Plans (if issues found)

### Fix 1: Pin SID-02 AC1 offer sizing in both procedure files

- **Root cause**: UT-002 asserts the gap-hunt citation, autonomous-only-Complex, and the empty-hunt line. It never asserts skip-Small, ask-Medium-and-Large, or recommend-Complex in `wspecify/SKILL.md` or `gap-hunt.md`.
- **Fix task**: In `test_specify_carries_the_new_steps`, assert those three offer rules in the Plan Approval body and in `gap-hunt.md` `## Sizing & Invocation`.
- **Verify**: Re-run N5 and N6 in a scratch worktree; each must be killed.
- **Done when**: SID-02 AC1 has `file:line` assertions for all four size behaviours (Small skip, Medium/Large ask, Complex recommend, autonomous-only-Complex).
- **Priority**: Blocker

### Fix 2: Pin the remaining SID-01 listing and guideline nouns

- **Root cause**: UT-002 asserts `affected features` and `scenario ids`, not `pages`. UT-002 asserts the screen-only gate, not `docs/guidelines/UI-UX.md`.
- **Fix task**: Assert `pages` (or `pages/routes`) in the Impact body, and assert `docs/guidelines/UI-UX.md` in the uiux.md step body.
- **Verify**: Re-run N7 and N8 in a scratch worktree; each must be killed.
- **Done when**: SID-01 AC1 lists features, pages, and scenario ids under assertion; SID-01 AC3 asserts the guideline path.
- **Priority**: Blocker

---

## Requirement Traceability Update

Do not edit `spec.md` in this session.

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| SID-01 | ❌ Needs Fix (`validation-s1-r2.md`) | ❌ Needs Fix |
| SID-02 | ❌ Needs Fix (`validation-s1-r2.md`) | ❌ Needs Fix |
| SID-03 | ⏭️ S2 (out of slice) | ⏭️ S2 (out of slice) |

---

## Summary

**Overall**: ❌ Not Ready

**Spec-anchored check**: 8/11 S1 ACs matched spec outcome (AC2, AC4, AC5, AC6, AC7, SID-02 AC2–AC4); 3 gaps; 0 spec-precision gaps
**Sensor**: 11/15 mutations killed (N5–N8 survived)
**Gate**: slice 18+40 passed; bun 124 passed; `git diff --check` clean

**What works**: All eight r1 survivors are now killed. r2 N2–N4 are killed. Small Impact exemption, `none` body, template order, UI-UX.md “written in Specify”, wverify pass/fail/untested and no-reruns, no-regression AC, two-explorer Impact and gap-hunt dispatch, settlement, autonomous skip, empty-hunt line, gates green, sync idempotent.

**Issues found**: SID-02 AC1 offer sizing is still untested in both files. SID-01 AC1 does not assert `pages`. SID-01 AC3 does not assert the UI-UX.md path.

**Next steps**: Route Fix 1–2 to a new Implementer. Re-verify S1 in a fresh Verifier session. Do not treat this checkpoint as S1-done.
