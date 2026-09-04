# Specify Impact and Designer Validation (S1 r4)

**Date**: 2026-09-03
**Spec**: `.specs/features/specify-impact-designer/spec.md`
**Diff range**: `3bb242af781c3ca6816c8eb40271d85ec973cd8b..HEAD` (S1 `84846af1`, `f8a0fae6`, `dd2b36a8`; test-strength `cbf455b2`, `9d49b94a`)
**Verifier**: independent sub-agent (author ≠ verifier)
**Verdict**: FAIL

TR2 kills every r3 survivor (N5–N8) and five new AC-element mutants (N9–N13). N14 still survives: SID-02 AC2 `recommended answer` can live only in the gap-hunt example. A survivor on a spec AC is a FAIL.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1 | ✅ Done | Impact, uiux.md, gap-hunt in wspecify; `wc -l` 142 ≤ 200 |
| T2 | ✅ Done | wdesign step 1, wverify 3.5, UI-UX.md timing |
| T3 | ✅ Done | Size-aware Impact in `validate_spec.py`; Small fixture present; this feature spec exits 0 |
| TR1 | ✅ Done | Canonical suite kills M6–M13 and N2–N4 |
| TR2 | ⚠️ Partial | N5–N8 and N9–N13 die; N14 (SID-02 AC2 recommended-answer in the procedure body) survives |
| T4–T6 | ⏭️ S2 | Not in this packet |

---

## Spec-Anchored Acceptance Criteria

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| SID-01 AC1: Impact step after dimensions, before user stories; two explorers; write `## Impact` listing features, pages, and scenario ids | Procedure contains that step, both explorer traces (including jobs and events), and the listing rule | `tools/test_phase_skills.py:388` - `assert impact_idx < user_stories_idx`; `:393` - `assert sweep_idx < impact_heading_idx`; `:409-415` - two explorers, data/model, pages/journeys/QA, journeys, jobs, events, QA scenarios; `:416-420` - `## Impact`, `affected features`, `pages` on the listing line, `scenario ids` | ✅ PASS |
| SID-01 AC2: WHEN Impact lists an affected feature THEN one ubiquitous no-regression AC | Skill instructs a ubiquitous unchanged-behaviour AC per listed feature | `tools/test_phase_skills.py:421-423` - `"For each affected feature listed"` / `"ubiquitous acceptance criterion"` / `"behaviour is unchanged"` | ✅ PASS |
| SID-01 AC3: uiux.md step after ACs, before closure, only when a screen is added or changed, follows UI-UX.md | Ordered uiux.md step with the screen gate and the guideline path | `tools/test_phase_skills.py:403` - `assert ac_idx < uiux_idx < closure_idx`; `:426` - `"Only when a screen is added or changed"`; `:427` - `"docs/guidelines/UI-UX.md" in uiux_body` | ✅ PASS |
| SID-01 AC4: UI-UX.md says uiux.md is written in Specify; wdesign step 1 loads uiux.md when present | Exact phrase plus step-1 load | `tools/test_phase_skills.py:487-488` - `"uiux.md" in step1_body` / `"exists, load it"`; `:510` - `"written in Specify" in uiux_guideline` | ✅ PASS |
| SID-01 AC5: wverify reruns Impact scenario ids and reports pass, fail, or untested | Rerun named ids; report those three statuses; `none` means no reruns | `tools/test_phase_skills.py:500-503` - `"scenario ids"` / `"## Impact"` / `"pass, fail, or untested"` / `"no reruns"` in `heading_body(..., "### 3.5.")` | ✅ PASS |
| SID-01 AC6: Large/Complex without Impact exit 1 naming the section; Medium/Small do not require it | Large and Complex reject; Medium and Small accept; `none` body accepted | `tools/test_tlc_validators.py:121-124` Large `"Impact" in error` and `ret == 1`; `:130-133` Complex; `:139-142` Medium `ret == 0`; `:147-150` Small `ret == 0`; `:157-160` `none` `ret == 0` | ✅ PASS |
| SID-01 AC7: spec-template has `## Impact` between Assumptions and User Stories | Heading order in the template | `tools/test_phase_skills.py:476` - `assert assumptions_idx < impact_idx < stories_idx` | ✅ PASS |
| SID-02 AC1: gap-hunt step at plan approval; skip Small; ask Medium/Large; recommend Complex; cite `references/gap-hunt.md` | Sizing rule plus citation; reference exists | `tools/test_phase_skills.py:405-406` citation and file exists; `:432-434` Small-skip / Medium-Large-ask / Complex-recommend in SKILL.md; `:445-447` same three in `gap-hunt.md` | ✅ PASS |
| SID-02 AC2: WHEN accepted THEN two explorers and numbered frontier questions each with a recommended answer | Two named explorers plus recommended-answer rounds | `tools/test_phase_skills.py:452-459` two explorers, unhappy paths, current behaviour, QA scenarios, domain/data, numbered questions, frontier; `:460` - `"recommended answer" in hunt` (whole file, including the example) | ❌ GAP |
| SID-02 AC3: WHEN a round settles THEN AC or `context.md` decision, never a note | Settlement must be an AC or a context/decisions record | `tools/test_phase_skills.py:461-463` - `"acceptance criterion"` / `"context.md"` / `"Never leave a settled finding as an informal note"` | ✅ PASS |
| SID-02 AC4: WHILE autonomous, run only for Complex and record the skip in `decisions.md` | Autonomous skip rule | `tools/test_phase_skills.py:436` - `"only for Complex"`; `:438` - `"decisions.md"`; `:449-450` same in `gap-hunt.md` | ✅ PASS |

**Status**: ❌ Gaps present

SID-02 AC2 explorers, numbered questions, and frontier rounds are pinned and N10 dies. `:460` matches `recommended answer` anywhere in `gap-hunt.md`, so the example line still satisfies it after the procedure clause is removed (N14).

---

## Discrimination Sensor

Scratch A: `git worktree add /tmp/sid-s1-r4-sensor.k4mR9x HEAD`. Gate in scratch: `python3 tools/test_phase_skills.py && python3 tools/test_tlc_validators.py`. Scratch baseline: 18 passed, 40 unittest OK.

Scratch B (N14 only): `git worktree add /tmp/sid-s1-r4-n14.w7 HEAD`, then `unlink` + rewrite so the mutant file is a new inode (`336054364` vs real `334651107`). Real-tree porcelain after both removals matches the pre-sensor baseline: `M .specs/LESSONS.md`, `M .specs/lessons.json` only.

Re-injected every r3 survivor (N5–N8) plus six new AC-element mutants (N9–N14).

| Mutation | AC clause | File:line | Description | Killed? |
| -------- | --------- | --------- | ----------- | ------- |
| N5 | SID-02 AC1 skip-Small / ask-Medium-and-Large / recommend-Complex | `wspecify/SKILL.md:120-122` | Drop the three size-tier offer bullets; keep autonomous | ✅ Killed (`test_phase_skills.py:432` `AssertionError: wspecify missing Small-skip gap-hunt sizing`) |
| N6 | SID-02 AC1 skip-Small / ask-Medium-and-Large / recommend-Complex | `gap-hunt.md:8-10` | Drop the three size-tier bullets from `## Sizing & Invocation` | ✅ Killed (`test_phase_skills.py:445` `AssertionError: gap-hunt.md missing Small-skip sizing`) |
| N7 | SID-01 AC3 follows `docs/guidelines/UI-UX.md` | `wspecify/SKILL.md:97` | Drop `following docs/guidelines/UI-UX.md` from the uiux.md step | ✅ Killed (`test_phase_skills.py:427`) |
| N8 | SID-01 AC1 listing names pages | `wspecify/SKILL.md:70` | Drop `pages/routes` from the Impact listing; keep features and scenario ids | ✅ Killed (`test_phase_skills.py:419` `AssertionError: Impact listing does not name pages`) |
| N9 | SID-01 AC1 explorer list includes jobs | `wspecify/SKILL.md:67` | Drop `jobs` from the data/model explorer trace | ✅ Killed (`test_phase_skills.py:413` `AssertionError: Impact step missing jobs`) |
| N10 | SID-02 AC2 numbered questions | `gap-hunt.md:27` | Drop `numbered questions` and `recommended answer` from the frontier procedure sentence | ✅ Killed (`test_phase_skills.py:458` `AssertionError: gap-hunt.md missing numbered questions`) |
| N11 | SID-01 AC5 report each as pass, fail, or untested | `wverify/SKILL.md:69` | Replace the three statuses with `report each result` | ✅ Killed (`test_phase_skills.py:502`) |
| N12 | SID-01 AC4 uiux.md is written in Specify | `docs/guidelines/UI-UX.md:11` | Replace `written in Specify` with `written before Design` | ✅ Killed (`test_phase_skills.py:510`) |
| N13 | SID-01 AC6 Complex specs require `## Impact` | `validate_spec.py:167` | Require Impact only for Large | ✅ Killed (`test_tlc_validators.py:126` `test_complex_spec_without_impact_is_rejected` `AssertionError: False is not true`) |
| N14 | SID-02 AC2 each with a recommended answer | `gap-hunt.md:27` | Drop `each providing a concrete recommended answer` from the procedure; leave it in the example | ❌ Survived (`test_phase_skills.py` 18 passed) |

**Sensor depth**: lightweight, 10 behaviour-level mutants (4 r3 survivors re-injected + 6 new)
**Result**: 9/10 killed — FAIL ❌

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

S1 + TR2 surface is skill text, the validator, five size fixtures, and the two unit files. UT-001..UT-003 now pin the r3 clauses. SID-02 AC2 `recommended answer` is still a whole-file substring and is hollow under TEST-CONTRACT.md.

---

## Edge Cases

- [x] EC1 validator half: Large `## Impact` body `none` accepted (`test_tlc_validators.py:153-160`, `ret == 0`)
- [x] EC1 wverify half: `## Impact` `none` means no reruns (`test_phase_skills.py:503`; N4 previously killed, clause still asserted)
- [x] EC2: gap hunt finds nothing → one line and proceed (`test_phase_skills.py:437` and `:464`)
- [ ] EC3: missing designer template fails `--sync-agents` naming the path — S2 / SID-03; no S1 evidence

---

## Impacted QA Scenarios

| Scenario | Result | Evidence |
| -------- | ------ | -------- |
| `QAS-resolve-phase-skill-procedures` | pass | Fresh `python3 tools/test_phase_skills.py` exit 0 (18 passed), including path existence for `references/gap-hunt.md` |
| `CFG-centralize-agent-model-routing` | pass | `--sync-agents` twice on the integration tree, both exit 0, both `"changed": []` |
| `ADP-adopt-workflow-safely` | untested | S1 and TR2 did not change `scripts/adopt.py`; no disposable adopt walk this session |

---

## Gate Check

- **Gate command**: `python3 tools/test_phase_skills.py && python3 tools/test_tlc_validators.py && bun test && git diff --check`
- **Result**: 18 + 40 + 124 passed, 0 failed, 0 skipped
- **`python3 tools/test_phase_skills.py`**: exit 0; `18 passed, 0 failed`
- **`python3 tools/test_tlc_validators.py`**: exit 0; `Ran 40 tests in 0.097s` OK
- **`bun test`**: exit 0; `124 pass`, `0 fail`, `1180 expect() calls`
- **`git diff --check`**: exit 0
- **This feature spec**: `python3 .agents/skills/workflow-spec-driven/scripts/validate_spec.py .specs/features/specify-impact-designer/spec.md` — exit 0
- **`--sync-agents` #1**: exit 0; `changed: []`
- **`--sync-agents` #2**: exit 0; `changed: []`
- **Test count before feature** (`3bb242af`): `test_phase_skills.py` 13, `test_tlc_validators.py` 35, bun 124
- **Test count after feature** (HEAD): 18, 40, 124
- **Delta**: +5 phase-skill tests (3 S1 + 2 S2), +5 validator tests (4 original size cases + Small), bun count unchanged
- **Skipped tests**: none
- **Failures**: none (gates green; N14 survivor on SID-02 AC2 fails the slice)

---

## Fix Plans (if issues found)

### Fix 1: Pin SID-02 AC2 recommended-answer in the frontier procedure body

- **Root cause**: UT-002 asserts `"recommended answer" in hunt`. The example block contains that phrase, so deleting it from the Frontier Rounds procedure sentence leaves the suite green.
- **Fix task**: In `test_specify_carries_the_new_steps`, assert `recommended answer` on the Frontier Rounds procedure sentence (or `heading_body(..., "### 2. Frontier Rounds")` excluding the fenced example), not the whole file.
- **Verify**: Re-run N14 in a scratch worktree; it must be killed.
- **Done when**: SID-02 AC2 has a `file:line` assertion that fails when the procedure drops `recommended answer` and the example still has it.
- **Priority**: Blocker

---

## Requirement Traceability Update

Do not edit `spec.md` in this session.

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| SID-01 | ❌ Needs Fix (`validation-s1-r3.md`) | ✅ Verified (S1 ACs; N5–N13 killed) |
| SID-02 | ❌ Needs Fix (`validation-s1-r3.md`) | ❌ Needs Fix (AC2 recommended-answer; N14 survived) |
| SID-03 | ⏭️ S2 (out of slice) | ⏭️ S2 (out of slice) |

---

## Summary

**Overall**: ❌ Not Ready

**Spec-anchored check**: 10/11 S1 ACs matched spec outcome (SID-01 AC1–AC7, SID-02 AC1, AC3, AC4); 1 gap (SID-02 AC2 recommended-answer); 0 spec-precision gaps
**Sensor**: 9/10 mutations killed (N14 survived)
**Gate**: slice 18+40 passed; bun 124 passed; `git diff --check` clean

**What works**: Every r3 survivor is dead. New mutants on jobs, numbered questions, wverify statuses, UI-UX.md “written in Specify”, and Complex Impact all die. Small Impact exemption, `none` body, template order, no-regression AC, two-explorer Impact and gap-hunt dispatch, settlement, autonomous skip, empty-hunt line, gates green, sync idempotent.

**Issues found**: SID-02 AC2 `recommended answer` is still a whole-file substring hidable in the example.

**Next steps**: Route Fix 1 to a new Implementer. Re-verify S1 in a fresh Verifier session. Do not treat this checkpoint as S1-done.
