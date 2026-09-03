# Specify Impact and Designer Validation (S1 r6)

**Date**: 2026-09-03
**Spec**: `.specs/features/specify-impact-designer/spec.md`
**Diff range**: `3bb242af781c3ca6816c8eb40271d85ec973cd8b..HEAD` (S1 `84846af1`, `f8a0fae6`, `dd2b36a8`; TR1 `cbf455b2`; TR2 `9d49b94a`; r4 docs `c35c5410`; r4 batch `b8ed7c7a`; r5 docs `f7eee103`; r5 batch `b7b9a10b`)
**Verifier**: independent sub-agent (author ≠ verifier)
**Verdict**: FAIL

The r5 batch kills the N19 re-inject. N20 survives: SID-01 AC4 `wdesign step 1 SHALL load uiux.md when present` can live only on the later `context.md` sentence if that sentence still contains `exists, load it`. A survivor on a spec AC element is a FAIL.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1 | ✅ Done | Impact, uiux.md, gap-hunt in wspecify; `wc -l` 142 ≤ 200 |
| T2 | ✅ Done | wdesign step 1, wverify 3.5, UI-UX.md timing |
| T3 | ✅ Done | Size-aware Impact in `validate_spec.py`; Small fixture present; this feature spec exits 0 |
| TR1 | ✅ Done | Canonical suite kills the r2/r3 rule-sentence set |
| TR2 | ✅ Done | N5–N8 and N9–N13 remain dead |
| post-r4 batch `b8ed7c7a` | ✅ Done | N14 stays dead |
| post-r5 batch `b7b9a10b` | ⚠️ Partial | N19 dies; `:488` is still a step-body substring, so N20 lives |
| T4–T6 | ⏭️ S2 | Not in this packet |

---

## Spec-Anchored Acceptance Criteria

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| SID-01 AC1: Impact step after dimensions, before user stories; two explorers; write `## Impact` listing features, pages, and scenario ids | Procedure contains that step, both explorer traces (including jobs and events), and the listing rule | `tools/test_phase_skills.py:388` - `assert impact_idx < user_stories_idx`; `:393` - `assert sweep_idx < impact_heading_idx`; `:409-415` - two explorers, data/model, pages/journeys/QA, journeys, jobs, events, QA scenarios; `:416-420` - `## Impact`, `affected features`, `pages` on the listing line, `scenario ids` | ✅ PASS |
| SID-01 AC2: WHEN Impact lists an affected feature THEN one ubiquitous no-regression AC | Skill instructs a ubiquitous unchanged-behaviour AC per listed feature | `tools/test_phase_skills.py:421-423` - `"For each affected feature listed"` / `"ubiquitous acceptance criterion"` / `"behaviour is unchanged"` | ✅ PASS |
| SID-01 AC3: uiux.md step after ACs, before closure, only when a screen is added or changed, follows UI-UX.md | Ordered uiux.md step with the screen gate and the guideline path | `tools/test_phase_skills.py:403` - `assert ac_idx < uiux_idx < closure_idx`; `:426` - `"Only when a screen is added or changed"`; `:427` - `"docs/guidelines/UI-UX.md" in uiux_body` | ✅ PASS |
| SID-01 AC4: UI-UX.md says uiux.md is written in Specify; wdesign step 1 loads uiux.md when present | Exact phrase plus step-1 load of uiux.md | `tools/test_phase_skills.py:510` - `"written in Specify" in uiux_guideline`; `:487` - `"uiux.md" in step1_body`; `:488` - `"exists, load it" in step1_body` (matches the later `context.md` sentence) | ❌ GAP |
| SID-01 AC5: wverify reruns Impact scenario ids and reports pass, fail, or untested | Rerun named ids; report those three statuses; `none` means no reruns | `tools/test_phase_skills.py:500-503` - `"scenario ids"` / `"## Impact"` / `"pass, fail, or untested"` / `"no reruns"` in `heading_body(..., "### 3.5.")` | ✅ PASS |
| SID-01 AC6: Large/Complex without Impact exit 1 naming the section; Medium/Small do not require it | Large and Complex reject; Medium and Small accept; `none` body accepted | `tools/test_tlc_validators.py:121-124` Large `"Impact" in error` and `ret == 1`; `:130-133` Complex; `:139-142` Medium `ret == 0`; `:147-150` Small `ret == 0`; `:157-160` `none` `ret == 0` | ✅ PASS |
| SID-01 AC7: spec-template has `## Impact` between Assumptions and User Stories | Heading order in the template | `tools/test_phase_skills.py:476` - `assert assumptions_idx < impact_idx < stories_idx` | ✅ PASS |
| SID-02 AC1: gap-hunt step at plan approval; skip Small; ask Medium/Large; recommend Complex; cite `references/gap-hunt.md` | Sizing rule plus citation; reference exists | `tools/test_phase_skills.py:405-406` citation and file exists; `:431` plan-approval cite; `:432-434` Small-skip / Medium-Large-ask / Complex-recommend in SKILL.md; `:445-447` same three in `gap-hunt.md` | ✅ PASS |
| SID-02 AC2: WHEN accepted THEN two explorers and numbered frontier questions each with a recommended answer | Two named explorers plus recommended-answer rounds | `tools/test_phase_skills.py:452-459` two explorers, unhappy paths, current behaviour, QA scenarios, domain/data, numbered questions, frontier; `:460-461` - `"each providing a concrete recommended answer" in procedure_line` (procedure sentence; example lines starting with `` ` `` / `❓` / `➡️` skipped) | ✅ PASS |
| SID-02 AC3: WHEN a round settles THEN AC or `context.md` decision, never a note | Settlement must be an AC or a context/decisions record | `tools/test_phase_skills.py:462-464` - `"acceptance criterion"` / `"context.md"` / `"Never leave a settled finding as an informal note"` | ✅ PASS |
| SID-02 AC4: WHILE autonomous, run only for Complex and record the skip in `decisions.md` | Autonomous skip rule | `tools/test_phase_skills.py:436` - `"only for Complex"`; `:438` - `"decisions.md"`; `:449-450` same in `gap-hunt.md` | ✅ PASS |

**Status**: ❌ Gaps present

SID-02 AC2 is now pinned to the Frontier Rounds procedure sentence. N19 dies. SID-01 AC4 `written in Specify` stays pinned. `:488` still matches any `exists, load it` in step 1, so dropping the uiux.md load and leaving the `context.md` load (N20) leaves the suite green.

---

## Discrimination Sensor

Scratch: `git worktree add /tmp/sid-s1-r6-sensor HEAD`. Gate in scratch: `python3 tools/test_phase_skills.py && python3 tools/test_tlc_validators.py`. Scratch baseline: 18 passed, 40 unittest OK.

Each mutant used unlink + rewrite (new inode). After `git worktree remove --force`, real-tree porcelain matches the pre-sensor baseline: empty. S1 implementation and test files match HEAD.

Re-injected the r5 survivor (N19) plus three new AC-element mutants (N20–N22). None of N20–N22 was a prior-report mutant: N20 is the uiux.md load-when-present clause (M5/N12 mutated `written in Specify` only); N21 is `events` (N9 dropped `jobs`); N22 deletes the `references/gap-hunt.md` cite (prior rounds asserted the path, never removed it).

| Mutation | AC clause | File:line | Description | Killed? |
| -------- | --------- | --------- | ----------- | ------- |
| N19 | SID-02 AC2 each with a recommended answer | `gap-hunt.md:27` | Move `each providing a concrete recommended answer` from the procedure into the fenced example | ✅ Killed (`test_phase_skills.py:461` `AssertionError: gap-hunt.md procedure sentence must require a recommended answer per question`) |
| N20 | SID-01 AC4 wdesign step 1 loads uiux.md when present | `wdesign/SKILL.md:22` | Drop `exists, load it` from the uiux.md sentence; keep `uiux.md`, designer dispatch, architecture half, and the later `context.md` `exists, load it too` | ❌ Survived (`test_phase_skills.py` 18 passed; isolated `test_downstream_phases_wired_for_impact_and_designer` also passed) |
| N21 | SID-01 AC1 explorer list includes events | `wspecify/SKILL.md:67` | Drop `events` from the data/model explorer trace; keep jobs | ✅ Killed (`test_phase_skills.py:414` `AssertionError: Impact step missing events`) |
| N22 | SID-02 AC1 cite `references/gap-hunt.md` | `wspecify/SKILL.md:119` and `:125` | Replace both `[gap-hunt.md](references/gap-hunt.md)` cites; leave the file in place | ✅ Killed (`test_phase_skills.py:192` `AssertionError: wspecify/SKILL.md does not name references/gap-hunt.md`; `:405` would also fail) |

**Sensor depth**: lightweight, 4 behaviour-level mutants (1 r5 survivor re-injected + 3 new unused AC elements)
**Result**: 3/4 killed — FAIL ❌

New fingerprint: SID-01 AC4 + step-body substring hidable on a sibling sentence. Not the r4/r5 recommended-answer / example fingerprint. `heading_body` of step 1 still includes the `context.md` line, so that helper alone would not kill N20.

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

S1 + r5-batch surface is skill text, the validator, five size fixtures, and the two unit files. UT-001..UT-003 pin every S1 clause except SID-01 AC4 `load uiux.md when present`, which remains a step-body substring and is hollow under TEST-CONTRACT.md.

---

## Edge Cases

- [x] EC1 validator half: Large `## Impact` body `none` accepted (`test_tlc_validators.py:153-160`, `ret == 0`)
- [x] EC1 wverify half: `## Impact` `none` means no reruns (`test_phase_skills.py:503`; clause still asserted)
- [x] EC2: gap hunt finds nothing → one line and proceed (`test_phase_skills.py:437` and `:465`)
- [ ] EC3: missing designer template fails `--sync-agents` naming the path — S2 / SID-03; no S1 evidence

---

## Impacted QA Scenarios

| Scenario | Result | Evidence |
| -------- | ------ | -------- |
| `QAS-resolve-phase-skill-procedures` | pass | Fresh `python3 tools/test_phase_skills.py` exit 0 (18 passed), including path existence for `references/gap-hunt.md` |
| `CFG-centralize-agent-model-routing` | pass | `--sync-agents` twice on the integration tree, both exit 0, both `"changed": []` |
| `ADP-adopt-workflow-safely` | untested | S1 and the r5 batch did not change `scripts/adopt.py`; no disposable adopt walk this session |

---

## Gate Check

- **Gate command**: `python3 tools/test_phase_skills.py && python3 tools/test_tlc_validators.py && bun test && git diff --check`
- **Result**: 18 + 40 + 124 passed, 0 failed, 0 skipped
- **`python3 tools/test_phase_skills.py`**: exit 0; `18 passed, 0 failed`
- **`python3 tools/test_tlc_validators.py`**: exit 0; `Ran 40 tests in 0.132s` OK
- **`bun test`**: exit 0; `124 pass`, `0 fail`, `1180 expect() calls`
- **`git diff --check`**: exit 0
- **This feature spec**: `python3 .agents/skills/workflow-spec-driven/scripts/validate_spec.py .specs/features/specify-impact-designer/spec.md` — exit 0
- **`--sync-agents` #1**: exit 0; `changed: []`
- **`--sync-agents` #2**: exit 0; `changed: []`
- **Test count before feature** (`3bb242af`): `test_phase_skills.py` 13, `test_tlc_validators.py` 35, bun 124
- **Test count after feature** (HEAD): 18, 40, 124
- **Delta**: +5 phase-skill tests (3 S1 + 2 S2), +5 validator tests (4 original size cases + Small), bun count unchanged
- **Skipped tests**: none
- **Failures**: none (gates green; N20 survivor on SID-01 AC4 fails the slice)

---

## Fix Plans (if issues found)

### Fix 1: Pin SID-01 AC4 uiux.md load-when-present on the uiux.md sentence

- **Premise**: `tools/test_phase_skills.py:488` asserts `"exists, load it" in step1_body`.
- **Path**: Change the uiux.md sentence from `When .../uiux.md exists, load it and dispatch...` to `When .../uiux.md is listed, dispatch...`. Leave `If .../context.md exists, load it too`. UT-003 still passes (N20). A designer dispatch that never loads `uiux.md` no longer has the SID-01 AC4 load-when-present SHALL.
- **Verdict**: Blocker. New fingerprint (not r4/r5 SID-02 AC2 / example).
- **Root cause**: `:488` is a step-1 substring. The next sentence already contains `exists, load it`.
- **Fix task**: In `test_downstream_phases_wired_for_impact_and_designer`, assert the load-when-present clause on `first_line_with(step1_body, "uiux.md")`. Do not use `step1_body` as a whole for that needle.
- **Verify**: Re-run N20 in a scratch worktree; it must be killed. N19 must stay dead.
- **Done when**: SID-01 AC4 has a `file:line` assertion that fails when the uiux.md sentence drops the load-when-present clause and the `context.md` sentence still has that clause.
- **Priority**: Blocker

---

## Requirement Traceability Update

Do not edit `spec.md` in this session.

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| SID-01 | ✅ Verified (`validation-s1-r5.md`) | ❌ Needs Fix (AC4 load uiux.md when present; N20 survived) |
| SID-02 | ❌ Needs Fix (`validation-s1-r5.md`) | ✅ Verified (AC2 recommended-answer; N19 killed) |
| SID-03 | ⏭️ S2 (out of slice) | ⏭️ S2 (out of slice) |

---

## Summary

**Overall**: ❌ Not Ready

**Spec-anchored check**: 10/11 S1 ACs matched spec outcome (SID-01 AC1–AC3, AC5–AC7, SID-02 AC1–AC4); 1 gap (SID-01 AC4 load-when-present); 0 spec-precision gaps
**Sensor**: 3/4 mutations killed (N19, N21, N22 killed; N20 survived)
**Gate**: slice 18+40 passed; bun 124 passed; `git diff --check` clean

**What works**: The r5 N19 re-inject is dead. New mutants on Impact `events` and the gap-hunt citation die. Small Impact exemption, `none` body, template order, two-explorer Impact and gap-hunt dispatch, autonomous skip, empty-hunt line, gates green, sync idempotent.

**Issues found**: SID-01 AC4 `load uiux.md when present` is still a step-body substring hidable on the `context.md` sentence (N20).

**Next steps**: Route Fix 1 to a new Implementer. Re-verify S1 in a fresh Verifier session. Do not treat this checkpoint as S1-done.
