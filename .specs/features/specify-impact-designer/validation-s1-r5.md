# Specify Impact and Designer Validation (S1 r5)

**Date**: 2026-09-03
**Spec**: `.specs/features/specify-impact-designer/spec.md`
**Diff range**: `3bb242af781c3ca6816c8eb40271d85ec973cd8b..HEAD` (S1 `84846af1`, `f8a0fae6`, `dd2b36a8`; TR1 `cbf455b2`; TR2 `9d49b94a`; r4 docs `c35c5410`; batch `b8ed7c7a`)
**Verifier**: independent sub-agent (author ≠ verifier)
**Verdict**: FAIL

The batch kills the r4 survivor (N14). N19 still survives: SID-02 AC2 `each with a recommended answer` can live only in the gap-hunt example if that example copies the new needle. A survivor on a spec AC element is a FAIL.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1 | ✅ Done | Impact, uiux.md, gap-hunt in wspecify; `wc -l` 142 ≤ 200 |
| T2 | ✅ Done | wdesign step 1, wverify 3.5, UI-UX.md timing |
| T3 | ✅ Done | Size-aware Impact in `validate_spec.py`; Small fixture present; this feature spec exits 0 |
| TR1 | ✅ Done | Canonical suite kills the r2/r3 rule-sentence set |
| TR2 | ✅ Done | N5–N8 and N9–N13 remain dead |
| post-r4 batch `b8ed7c7a` | ⚠️ Partial | N14 dies; `:460` is still a whole-file substring, so N19 lives |
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
| SID-02 AC2: WHEN accepted THEN two explorers and numbered frontier questions each with a recommended answer | Two named explorers plus recommended-answer rounds | `tools/test_phase_skills.py:452-459` two explorers, unhappy paths, current behaviour, QA scenarios, domain/data, numbered questions, frontier; `:460` - `"each providing a concrete recommended answer" in hunt` (whole file, including the example) | ❌ GAP |
| SID-02 AC3: WHEN a round settles THEN AC or `context.md` decision, never a note | Settlement must be an AC or a context/decisions record | `tools/test_phase_skills.py:461-463` - `"acceptance criterion"` / `"context.md"` / `"Never leave a settled finding as an informal note"` | ✅ PASS |
| SID-02 AC4: WHILE autonomous, run only for Complex and record the skip in `decisions.md` | Autonomous skip rule | `tools/test_phase_skills.py:436` - `"only for Complex"`; `:438` - `"decisions.md"`; `:449-450` same in `gap-hunt.md` | ✅ PASS |

**Status**: ❌ Gaps present

SID-02 AC2 explorers, numbered questions, and frontier rounds stay pinned. `:460` now uses a longer needle, so N14 dies. The needle is still matched anywhere in `gap-hunt.md`, so moving that phrase into the fenced example (N19) leaves the suite green.

---

## Discrimination Sensor

Scratch: `git worktree add /tmp/sid-s1-r5-sensor.r5a HEAD`. Gate in scratch: `python3 tools/test_phase_skills.py && python3 tools/test_tlc_validators.py`. Scratch baseline: 18 passed, 40 unittest OK.

Each mutant used unlink + rewrite (new inode). After `git worktree remove --force`, real-tree porcelain matches the pre-sensor baseline: `M .specs/LESSONS.md`, `M .specs/lessons.json` only. S1 implementation and test files match HEAD.

Re-injected the r4 survivor (N14) plus five new AC-element mutants (N15–N19).

| Mutation | AC clause | File:line | Description | Killed? |
| -------- | --------- | --------- | ----------- | ------- |
| N14 | SID-02 AC2 each with a recommended answer | `gap-hunt.md:27` | Drop `each providing a concrete recommended answer` from the procedure; leave the example's `recommended answer` | ✅ Killed (`test_phase_skills.py:460` `AssertionError: gap-hunt.md procedure must require a recommended answer per question`) |
| N15 | SID-01 AC2 ubiquitous unchanged-behaviour AC | `wspecify/SKILL.md:70` | Drop the per-listed-feature ubiquitous AC sentence | ✅ Killed (`test_phase_skills.py:421` `AssertionError: Impact step missing the per-listed-feature trigger`) |
| N16 | SID-01 AC3 only when a screen is added or changed | `wspecify/SKILL.md:97` | Drop the screen-only gate; keep the uiux.md write and UI-UX.md cite | ✅ Killed (`test_phase_skills.py:426` `AssertionError: uiux.md step missing the screen-only gate`) |
| N17 | SID-02 AC3 never a note | `gap-hunt.md:43` | Drop `Never leave a settled finding as an informal note.` | ✅ Killed (`test_phase_skills.py:463` `AssertionError: gap-hunt.md missing the never-a-note rule`) |
| N18 | SID-01 AC6 Medium shall not require Impact | `validate_spec.py:167` | Require Impact for Medium as well as Large and Complex | ✅ Killed (`test_tlc_validators.py:135` `test_medium_spec_without_impact_is_accepted`) |
| N19 | SID-02 AC2 each with a recommended answer | `gap-hunt.md:27` | Move `each providing a concrete recommended answer` from the procedure into the fenced example | ❌ Survived (`test_phase_skills.py` 18 passed) |

**Sensor depth**: lightweight, 6 behaviour-level mutants (1 r4 survivor re-injected + 5 new)
**Result**: 5/6 killed — FAIL ❌

Same fingerprint as r4 Fix 1: SID-02 AC2 + whole-file substring hidable in the example. The batch lengthened the needle; it did not scope the assertion to the procedure sentence. `heading_body(..., "### 2. Frontier Rounds")` still includes the fence, so that helper alone would not kill N19.

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

S1 + batch surface is skill text, the validator, five size fixtures, and the two unit files. UT-001..UT-003 pin every S1 clause except SID-02 AC2 `recommended answer`, which remains a whole-file substring and is hollow under TEST-CONTRACT.md.

---

## Edge Cases

- [x] EC1 validator half: Large `## Impact` body `none` accepted (`test_tlc_validators.py:153-160`, `ret == 0`)
- [x] EC1 wverify half: `## Impact` `none` means no reruns (`test_phase_skills.py:503`; clause still asserted)
- [x] EC2: gap hunt finds nothing → one line and proceed (`test_phase_skills.py:437` and `:464`)
- [ ] EC3: missing designer template fails `--sync-agents` naming the path — S2 / SID-03; no S1 evidence

---

## Impacted QA Scenarios

| Scenario | Result | Evidence |
| -------- | ------ | -------- |
| `QAS-resolve-phase-skill-procedures` | pass | Fresh `python3 tools/test_phase_skills.py` exit 0 (18 passed), including path existence for `references/gap-hunt.md` |
| `CFG-centralize-agent-model-routing` | pass | `--sync-agents` twice on the integration tree, both exit 0, both `"changed": []` |
| `ADP-adopt-workflow-safely` | untested | S1 and the batch did not change `scripts/adopt.py`; no disposable adopt walk this session |

---

## Gate Check

- **Gate command**: `python3 tools/test_phase_skills.py && python3 tools/test_tlc_validators.py && bun test && git diff --check`
- **Result**: 18 + 40 + 124 passed, 0 failed, 0 skipped
- **`python3 tools/test_phase_skills.py`**: exit 0; `18 passed, 0 failed`
- **`python3 tools/test_tlc_validators.py`**: exit 0; `Ran 40 tests in 0.153s` OK
- **`bun test`**: exit 0; `124 pass`, `0 fail`, `1180 expect() calls`
- **`git diff --check`**: exit 0
- **This feature spec**: `python3 .agents/skills/workflow-spec-driven/scripts/validate_spec.py .specs/features/specify-impact-designer/spec.md` — exit 0
- **`--sync-agents` #1**: exit 0; `changed: []`
- **`--sync-agents` #2**: exit 0; `changed: []`
- **Test count before feature** (`3bb242af`): `test_phase_skills.py` 13, `test_tlc_validators.py` 35, bun 124
- **Test count after feature** (HEAD): 18, 40, 124
- **Delta**: +5 phase-skill tests (3 S1 + 2 S2), +5 validator tests (4 original size cases + Small), bun count unchanged
- **Skipped tests**: none
- **Failures**: none (gates green; N19 survivor on SID-02 AC2 fails the slice)

---

## Fix Plans (if issues found)

### Fix 1: Pin SID-02 AC2 recommended-answer on the Frontier Rounds procedure sentence

- **Premise**: `tools/test_phase_skills.py:460` asserts `"each providing a concrete recommended answer" in hunt`.
- **Path**: Delete that clause from `gap-hunt.md:27` and place the same words inside the fenced example. UT-002 still passes (N19). A planner that follows only the procedure sentence no longer has the SID-02 AC2 recommended-answer SHALL.
- **Verdict**: Blocker. Same fingerprint as r4 Fix 1.
- **Root cause**: The batch replaced `"recommended answer" in hunt` with a longer whole-file needle. The example no longer contains that needle by default (N14 dies), but any occurrence in the file still satisfies the assert.
- **Fix task**: In `test_specify_carries_the_new_steps`, assert the phrase on the Frontier Rounds procedure sentence (`first_line_with(hunt, "numbered questions")` or the line before the fence). Do not use `hunt` as a whole. Do not use `heading_body(..., "### 2. Frontier Rounds")` unless the fenced example is stripped first.
- **Verify**: Re-run N19 in a scratch worktree; it must be killed. N14 must stay dead.
- **Done when**: SID-02 AC2 has a `file:line` assertion that fails when the procedure drops the recommended-answer clause and the example still has that clause.
- **Priority**: Blocker

---

## Requirement Traceability Update

Do not edit `spec.md` in this session.

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| SID-01 | ✅ Verified (`validation-s1-r4.md`) | ✅ Verified (S1 ACs; N15, N16, N18 killed) |
| SID-02 | ❌ Needs Fix (`validation-s1-r4.md`) | ❌ Needs Fix (AC2 recommended-answer; N19 survived) |
| SID-03 | ⏭️ S2 (out of slice) | ⏭️ S2 (out of slice) |

---

## Summary

**Overall**: ❌ Not Ready

**Spec-anchored check**: 10/11 S1 ACs matched spec outcome (SID-01 AC1–AC7, SID-02 AC1, AC3, AC4); 1 gap (SID-02 AC2 recommended-answer); 0 spec-precision gaps
**Sensor**: 5/6 mutations killed (N14 killed; N19 survived)
**Gate**: slice 18+40 passed; bun 124 passed; `git diff --check` clean

**What works**: The r4 N14 re-inject is dead. New mutants on the ubiquitous no-regression AC, the uiux.md screen gate, never-a-note settlement, and the Medium Impact exemption all die. Small Impact exemption, `none` body, template order, two-explorer Impact and gap-hunt dispatch, autonomous skip, empty-hunt line, gates green, sync idempotent.

**Issues found**: SID-02 AC2 `recommended answer` is still a whole-file substring hidable in the example (N19). Same fingerprint as r4 Fix 1.

**Next steps**: Route Fix 1 to a new Implementer. Re-verify S1 in a fresh Verifier session. Do not treat this checkpoint as S1-done.
