# Specify Impact and Designer Validation (S1 r2)

**Date**: 2026-09-03
**Spec**: `.specs/features/specify-impact-designer/spec.md`
**Diff range**: `3bb242af781c3ca6816c8eb40271d85ec973cd8b..HEAD` (S1 `84846af1`, `f8a0fae6`, `dd2b36a8`; later S2 and docs commits are on HEAD; no test-strength commit is present)
**Verifier**: independent sub-agent (author ≠ verifier)
**Verdict**: FAIL

HEAD `0f03d13e` still ships the same UT-001..UT-003 assertions judged hollow in `validation-s1.md`. There is no Small-size fixture and no stronger procedure-clause asserts. A test-strength batch is not on this branch.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1 | ✅ Done | Impact, uiux.md, gap-hunt in wspecify; `wc -l` 142 ≤ 200 |
| T2 | ✅ Done | wdesign step 1, wverify 3.5, UI-UX.md timing |
| T3 | ✅ Done | Size-aware Impact in `validate_spec.py`; this feature spec exits 0 |
| T4–T6 | ⏭️ S2 | Not in this packet |

---

## Spec-Anchored Acceptance Criteria

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| SID-01 AC1: Impact step after dimensions, before user stories; two explorers; write `## Impact` listing features, pages, scenario ids | Procedure contains that step, both explorer traces, and the listing rule | `tools/test_phase_skills.py:340` - `assert impact_idx < user_stories_idx` (order only) | ❌ GAP |
| SID-01 AC2: WHEN Impact lists an affected feature THEN one ubiquitous no-regression AC | Skill instructs a ubiquitous unchanged-behaviour AC per listed feature | no evidence | ❌ GAP |
| SID-01 AC3: uiux.md step after ACs, before closure, only when a screen is added or changed, follows UI-UX.md | Ordered uiux.md step with the screen gate | `tools/test_phase_skills.py:350` - `assert ac_idx < uiux_idx < closure_idx` (order only; screen gate untested) | ❌ GAP |
| SID-01 AC4: UI-UX.md says uiux.md is written in Specify; wdesign step 1 loads uiux.md when present | Exact phrase plus step-1 load | `tools/test_phase_skills.py:376` - `assert "uiux.md" in step1_body`; `tools/test_phase_skills.py:389` - `assert "written in Specify" in uiux_guideline` | ✅ PASS |
| SID-01 AC5: wverify reruns Impact scenario ids and reports pass, fail, or untested | Rerun named ids; report those three statuses; `none` means no reruns | `tools/test_phase_skills.py:382-384` - `"Impact" in text` / `"scenario" in text.lower()` / `"rerun" in text.lower()` | ❌ GAP |
| SID-01 AC6: Large/Complex without Impact exit 1 naming the section; Medium/Small do not require it | Large and Complex reject; Medium and Small accept | `tools/test_tlc_validators.py:116-118` Large `"Impact" in error` and `ret == 1`; `:124-126` Complex; `:132-135` Medium `errors == []` and `ret == 0`; Small: no evidence | ❌ GAP |
| SID-01 AC7: spec-template has `## Impact` between Assumptions and User Stories | Heading order in the template | `tools/test_phase_skills.py:365` - `assert assumptions_idx < impact_idx < stories_idx` | ✅ PASS |
| SID-02 AC1: gap-hunt step at plan approval; skip Small; ask Medium/Large; recommend Complex; cite `references/gap-hunt.md` | Sizing rule plus citation; reference exists | `tools/test_phase_skills.py:352-353` - `"references/gap-hunt.md" in text` and file exists | ❌ GAP |
| SID-02 AC2: WHEN accepted THEN two explorers and numbered frontier questions each with a recommended answer | Two named explorers plus recommended-answer rounds | no evidence | ❌ GAP |
| SID-02 AC3: WHEN a round settles THEN AC or `context.md` decision, never a note | Settlement must be an AC or a context/decisions record | no evidence | ❌ GAP |
| SID-02 AC4: WHILE autonomous, run only for Complex and record the skip in `decisions.md` | Autonomous skip rule | no evidence | ❌ GAP |

**Status**: ❌ Gaps present

AC1 order is asserted; two-explorer dispatch (M9) and listing contents (N3) survived. AC2 has no assertion (M6 survived). AC3 order is asserted; the screen-only gate survived (N2). AC5 substrings are satisfied by the `### 3.5. Rerun Impacted QA Scenarios` heading (M12 survived) and do not pin `pass`/`fail`/`untested` or `none` (N4 survived). AC6 has no Small fixture (M7 survived). SID-02 AC1 citation exists; sizing, explorers, settlement, and autonomous rules are untested (M8, M10, M13 survived).

---

## Discrimination Sensor

Scratch: `git worktree add /tmp/sid-s1-r2-sensor.vyXI9k HEAD`. Gate in scratch: `python3 tools/test_phase_skills.py && python3 tools/test_tlc_validators.py`. Baseline in scratch passed. Real tree porcelain empty before and after `git worktree remove --force`.

Re-injected every r1 survivor (M6–M13) plus four new mutants (N1–N4).

| Mutation | File:line | Description | Killed? |
| -------- | --------- | ----------- | ------- |
| M6 | `wspecify/SKILL.md:70` | Remove ubiquitous no-regression AC instruction | ❌ Survived |
| M7 | `validate_spec.py:167` | Require Impact for Small | ❌ Survived |
| M8 | `gap-hunt.md:39-43` | Settlement becomes notes | ❌ Survived |
| M9 | `wspecify/SKILL.md:66-68` | Drop two-explorer Impact dispatch, keep heading | ❌ Survived |
| M10 | `wspecify/SKILL.md:123` | Drop autonomous-only-Complex rule | ❌ Survived |
| M11 | `wspecify/SKILL.md:125` | Drop one-line empty gap-hunt proceed rule | ❌ Survived |
| M12 | `wverify/SKILL.md:69` | Drop Impact rerun body; leave heading | ❌ Survived |
| M13 | `gap-hunt.md:19-27` | Drop two explorers and recommended-answer rounds | ❌ Survived |
| N1 | `validate_spec.py:167` | Drop Complex from Impact require set | ✅ Killed (`test_tlc_validators.py:124` `AssertionError: False is not true`) |
| N2 | `wspecify/SKILL.md:97` | Remove screen-only gate from uiux.md step | ❌ Survived |
| N3 | `wspecify/SKILL.md:70` | Drop Impact listing of features, pages, and scenario ids | ❌ Survived |
| N4 | `wverify/SKILL.md:69` | Drop none-means-no-reruns clause; keep pass/fail/untested | ❌ Survived |

**Sensor depth**: lightweight, 12 behaviour-level mutants (8 r1 survivors re-injected + 4 new)
**Result**: 1/12 killed — FAIL ❌

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

S1-only diff (`3bb242af..dd2b36a8`) is 14 files, +340/−13: skill text, validator, four size fixtures, and the two unit files. Validator branches for Large, Complex, Medium, and `none` match existing `section_bounds` style. UT-001/002/003 map to named contract ids. They do not assert several precise AC clauses, so they fail the hollow-case rule in TEST-CONTRACT.md. `tests.md` UT-001 also omits Small while spec AC6 includes it.

---

## Edge Cases

- [x] EC1 validator half: Large `## Impact` body `none` accepted (`test_tlc_validators.py:141-144`, `ret == 0`)
- [ ] EC1 wverify half: `## Impact` `none` means no reruns — M12 and N4 survived
- [ ] EC2: gap hunt finds nothing → one line and proceed — M11 survived
- [ ] EC3: missing designer template fails `--sync-agents` naming the path — S2 / SID-03; no S1 evidence

---

## Impacted QA Scenarios

| Scenario | Result | Evidence |
| -------- | ------ | -------- |
| `QAS-resolve-phase-skill-procedures` | pass | Fresh `python3 tools/test_phase_skills.py` exit 0 (18 passed), including path existence for `references/gap-hunt.md` |
| `CFG-centralize-agent-model-routing` | pass | `--sync-agents` twice, both exit 0, both `"changed": []` |
| `ADP-adopt-workflow-safely` | untested | S1 did not change `scripts/adopt.py`; no disposable adopt walk this session |

---

## Gate Check

- **Gate command**: `python3 tools/test_phase_skills.py && python3 tools/test_tlc_validators.py && bun test && git diff --check`
- **Result**: 18 + 39 + 124 passed, 0 failed, 0 skipped
- **`python3 tools/test_phase_skills.py`**: exit 0; `18 passed, 0 failed`
- **`python3 tools/test_tlc_validators.py`**: exit 0; `Ran 39 tests in 0.117s` OK
- **`bun test`**: exit 0; `124 pass`, `0 fail`, `1180 expect() calls`
- **`git diff --check`**: exit 0
- **This feature spec**: `python3 .agents/skills/workflow-spec-driven/scripts/validate_spec.py .specs/features/specify-impact-designer/spec.md` — exit 0
- **`--sync-agents` #1**: exit 0; `changed: []`
- **`--sync-agents` #2**: exit 0; `changed: []`
- **Test count before feature** (`3bb242af`): `test_phase_skills.py` 13, `test_tlc_validators.py` 35, bun 124
- **Test count after feature** (HEAD): 18, 39, 124
- **Delta**: +5 phase-skill tests (3 S1 + 2 S2), +4 validator tests, bun count unchanged
- **Skipped tests**: none
- **Failures**: none (gates green; sensor and AC evidence fail the slice)

---

## Fix Plans (if issues found)

Same fingerprints as `validation-s1.md` Fix 1–3. N2/N3/N4 are additional survivors on those fingerprints, not new root causes.

### Fix 1: Discriminate SID-01 AC1, AC2, AC3 screen gate, and SID-02 procedure clauses

- **Root cause**: UT-002 only checks that `Impact` precedes `User Stories`, that `uiux.md` sits between Acceptance Criteria and the closure gate, and that `references/gap-hunt.md` is cited. Removing the two-explorer dispatch, the listing contents, the no-regression AC sentence, the screen-only gate, the autonomous rule, or the empty-hunt line leaves the suite green. `gap-hunt.md` settlement and explorer/round text are unread.
- **Fix task**: Extend `test_specify_carries_the_new_steps` (and a `gap-hunt.md` read) so it asserts both explorer traces, the listing of features/pages/scenario ids, the ubiquitous no-regression sentence, the screen-only uiux.md gate, Small/Medium/Large/Complex/autonomous sizing, recommended-answer rounds, settlement as AC or `context.md`, and the one-line empty-hunt proceed rule.
- **Verify**: Re-run M6, M8, M9, M10, M11, M13, N2, N3 in a scratch worktree; each must be killed.
- **Done when**: Those clauses have `file:line` assertions; sensor kills the same faults.
- **Priority**: Blocker

### Fix 2: Add a Small-size Impact fixture

- **Root cause**: AC6 exempts Small; only Medium is tested. Adding Small to the require set survived. `tests.md` UT-001 also omits Small.
- **Fix task**: Add `tools/fixtures/tlc-validator/spec-size-small-no-impact.md` and a UT-001 case that expects exit 0. Name Small in `tests.md` UT-001.
- **Verify**: Mutating `if size in ("Large", "Complex"):` to include `"Small"` fails that case (M7).
- **Done when**: UT-001 covers Large, Complex, Medium, Small, and `none`.
- **Priority**: Blocker

### Fix 3: Stop treating the wverify heading as AC5 evidence

- **Root cause**: UT-003 accepts any occurrence of `Impact`, `scenario`, and `rerun`. The `### 3.5` heading supplies all three after the body is deleted. Deleting only the `none` sentence also survives.
- **Fix task**: Assert the body text: report `pass`, `fail`, or `untested`, and that `none` means no reruns.
- **Verify**: M12 (body removed, heading kept) and N4 (`none` clause removed) are killed.
- **Done when**: AC5 and EC1 wverify half have precise assertions.
- **Priority**: Blocker

---

## Requirement Traceability Update

Do not edit `spec.md` in this session.

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| SID-01 | ❌ Needs Fix (`validation-s1.md`) | ❌ Needs Fix |
| SID-02 | ❌ Needs Fix (`validation-s1.md`) | ❌ Needs Fix |
| SID-03 | ⏭️ S2 (out of slice) | ⏭️ S2 (out of slice) |

---

## Summary

**Overall**: ❌ Not Ready

**Spec-anchored check**: 2/11 S1 ACs matched spec outcome (AC4, AC7); 9 gaps; 0 spec-precision gaps
**Sensor**: 1/12 mutations killed (N1 only)
**Gate**: slice 18+39 passed; bun 124 passed; `git diff --check` clean

**What works**: Size-aware Impact rejection for Large and Complex (N1 killed dropping Complex), Medium exemption, `none` body accepted, template heading order, UI-UX.md “written in Specify”, wdesign step 1 names `uiux.md`, gates green, sync idempotent.

**Issues found**: All eight r1 survivors still survive. Three new mutants on spec ACs also survived (N2 screen gate, N3 listing contents, N4 none-means-no-reruns). No test-strength batch is on HEAD.

**Next steps**: Route Fix 1–3 to a new Implementer. Re-verify S1 in a fresh Verifier session after the batch is actually on the branch. Do not treat this checkpoint as S1-done.
