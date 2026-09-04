# Specify Impact and Designer Validation (S1 r7)

**Date**: 2026-09-03
**Spec**: `.specs/features/specify-impact-designer/spec.md`
**Diff range**: `3bb242af781c3ca6816c8eb40271d85ec973cd8b..HEAD` (S1 `84846af1`, `f8a0fae6`, `dd2b36a8`; remediations through r6; test-strength batch `eb5a2e68`)
**Verifier**: independent sub-agent (author ≠ verifier)
**Verdict**: PASS

The r6 survivor N20 is dead. `test_phase_skills.py:490` pins `exists, load it` to the uiux.md sentence, so dropping that clause while the `context.md` sentence still has it fails UT-003. Three new unused AC-element mutants also die.

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
| post-r5 batch `b7b9a10b` | ✅ Done | N19 stays dead |
| post-r6 batch `eb5a2e68` | ✅ Done | N20 dies on the uiux.md sentence |
| T4–T6 | ⏭️ S2 | Not in this packet |

---

## Spec-Anchored Acceptance Criteria

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| SID-01 AC1: Impact step after dimensions, before user stories; two explorers; write `## Impact` listing features, pages, and scenario ids | Procedure contains that step, both explorer traces (including jobs and events), and the listing rule | `tools/test_phase_skills.py:388` - `assert impact_idx < user_stories_idx`; `:393` - `assert sweep_idx < impact_heading_idx`; `:409-415` - two explorers, data/model, pages/journeys/QA, journeys, jobs, events, QA scenarios; `:416-420` - `## Impact`, `affected features`, `pages` on the listing line, `scenario ids` | ✅ PASS |
| SID-01 AC2: WHEN Impact lists an affected feature THEN one ubiquitous no-regression AC | Skill instructs a ubiquitous unchanged-behaviour AC per listed feature | `tools/test_phase_skills.py:421-423` - `"For each affected feature listed"` / `"ubiquitous acceptance criterion"` / `"behaviour is unchanged"` | ✅ PASS |
| SID-01 AC3: uiux.md step after ACs, before closure, only when a screen is added or changed, follows UI-UX.md | Ordered uiux.md step with the screen gate and the guideline path | `tools/test_phase_skills.py:403` - `assert ac_idx < uiux_idx < closure_idx`; `:426` - `"Only when a screen is added or changed"`; `:427` - `"docs/guidelines/UI-UX.md" in uiux_body` | ✅ PASS |
| SID-01 AC4: UI-UX.md says uiux.md is written in Specify; wdesign step 1 loads uiux.md when present | Exact phrase plus step-1 load of uiux.md on the uiux.md sentence | `tools/test_phase_skills.py:512` - `"written in Specify" in uiux_guideline`; `:488` - `"uiux.md" in step1_body`; `:490` - `"exists, load it" in uiux_sentence` | ✅ PASS |
| SID-01 AC5: wverify reruns Impact scenario ids and reports pass, fail, or untested | Rerun named ids; report those three statuses; `none` means no reruns | `tools/test_phase_skills.py:502-505` - `"scenario ids"` / `"## Impact"` / `"pass, fail, or untested"` / `"no reruns"` in `heading_body(..., "### 3.5.")` | ✅ PASS |
| SID-01 AC6: Large/Complex without Impact exit 1 naming the section; Medium/Small do not require it | Large and Complex reject; Medium and Small accept; `none` body accepted | `tools/test_tlc_validators.py:121-124` Large `"Impact" in error` and `ret == 1`; `:130-133` Complex; `:139-142` Medium `ret == 0`; `:147-150` Small `ret == 0`; `:157-160` `none` `ret == 0` | ✅ PASS |
| SID-01 AC7: spec-template has `## Impact` between Assumptions and User Stories | Heading order in the template | `tools/test_phase_skills.py:475` - `assert impact_idx != -1`; `:477` - `assert assumptions_idx < impact_idx < stories_idx` | ✅ PASS |
| SID-02 AC1: gap-hunt step at plan approval; skip Small; ask Medium/Large; recommend Complex; cite `references/gap-hunt.md` | Sizing rule plus citation; reference exists | `tools/test_phase_skills.py:405-406` citation and file exists; `:431` plan-approval cite; `:432-434` Small-skip / Medium-Large-ask / Complex-recommend in SKILL.md; `:445-447` same three in `gap-hunt.md` | ✅ PASS |
| SID-02 AC2: WHEN accepted THEN two explorers and numbered frontier questions each with a recommended answer | Two named explorers plus recommended-answer rounds | `tools/test_phase_skills.py:452-459` two explorers, unhappy paths, current behaviour, QA scenarios, domain/data, numbered questions, frontier; `:461` - `"each providing a concrete recommended answer" in procedure_line` | ✅ PASS |
| SID-02 AC3: WHEN a round settles THEN AC or `context.md` decision, never a note | Settlement must be an AC or a context/decisions record | `tools/test_phase_skills.py:462-464` - `"acceptance criterion"` / `"context.md"` / `"Never leave a settled finding as an informal note"` | ✅ PASS |
| SID-02 AC4: WHILE autonomous, run only for Complex and record the skip in `decisions.md` | Autonomous skip rule | `tools/test_phase_skills.py:436` - `"only for Complex"`; `:438` - `"decisions.md"` in `gap_offer`; `:449-450` same in `gap-hunt.md` | ✅ PASS |

**Status**: ✅ All ACs covered

SID-01 AC4 `load uiux.md when present` is pinned to the uiux.md sentence (`:490`). The r6 substring hide on the `context.md` line no longer keeps the suite green.

---

## Discrimination Sensor

Scratch: `git worktree add /tmp/sid-s1-r7-sensor HEAD`. Gate in scratch: `python3 tools/test_phase_skills.py && python3 tools/test_tlc_validators.py`. Scratch baseline: 18 passed, 40 unittest OK.

Each mutant used unlink + rewrite (new inode). After `git worktree remove --force`, real-tree porcelain matches the pre-sensor baseline: empty. S1 implementation and test files match HEAD.

Re-injected the r6 survivor (N20) plus three new AC-element mutants (N23–N25). None of N23–N25 was a prior-report mutant: N23 deletes `journeys` (N9 dropped `jobs`; N21 dropped `events`); N24 deletes the `decisions.md` skip-record cite (prior rounds asserted the path, never removed it); N25 deletes `current behaviour` from the unhappy-paths explorer (M13 dropped the explorer pair as a whole).

| Mutation | AC clause | File:line | Description | Killed? |
| -------- | --------- | --------- | ----------- | ------- |
| N20 | SID-01 AC4 wdesign step 1 loads uiux.md when present | `wdesign/SKILL.md:22` | Drop `exists, load it` from the uiux.md sentence; keep `uiux.md`, designer dispatch, architecture half, and the later `context.md` `exists, load it too` | ✅ Killed (`test_phase_skills.py:490` `AssertionError: wdesign step 1 must load uiux.md when it exists, in the uiux.md sentence itself`; isolated `test_downstream_phases_wired_for_impact_and_designer` also failed) |
| N23 | SID-01 AC1 explorer list includes journeys | `wspecify/SKILL.md:68` | Drop `journeys` from the pages/journeys/QA explorer trace; keep jobs and events | ✅ Killed (`test_phase_skills.py:411` `AssertionError: Impact step missing the pages/journeys/QA explorer trace`; `:412` would also fail) |
| N24 | SID-02 AC4 record the skip in `decisions.md` | `wspecify/SKILL.md:123` and `gap-hunt.md:11` | Drop `decisions.md` from both autonomous skip sentences; leave settlement `(or decisions.md)` | ✅ Killed (`test_phase_skills.py:438` `AssertionError: autonomous skip is not recorded in decisions.md`) |
| N25 | SID-02 AC2 unhappy paths against current behaviour | `gap-hunt.md:20` | Drop `current application behaviour` from the unhappy-paths explorer line; keep the explorer name and QA scenarios | ✅ Killed (`test_phase_skills.py:455` `AssertionError: unhappy-paths explorer missing current behaviour`) |

**Sensor depth**: lightweight, 4 behaviour-level mutants (1 r6 survivor re-injected + 3 new unused AC elements)
**Result**: 4/4 killed — PASS

N24 still names `decisions.md` on the settlement line, so `:450` (`"decisions.md" in hunt`) would not have killed this skip-only deletion. `:438` did. Not a survivor.

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
| Spec-anchored outcome check (asserted values match spec) | ✅ |
| Per-layer Coverage Expectation met (domain 1:1 ACs; routes happy+edge+error) | ✅ |
| Every test maps to a spec requirement - no unclaimed tests | ✅ |
| Documented guidelines followed: `docs/guidelines/TEST-CONTRACT.md` | ✅ |

S1 + r7-batch surface is skill text, the validator, five size fixtures, and the two unit files. The batch is a two-line pin of SID-01 AC4 onto `first` uiux.md sentence. UT-001..UT-003 pin every S1 clause.

---

## Edge Cases

- [x] EC1 validator half: Large `## Impact` body `none` accepted (`test_tlc_validators.py:153-160`, `ret == 0`)
- [x] EC1 wverify half: `## Impact` `none` means no reruns (`test_phase_skills.py:505`; clause still asserted)
- [x] EC2: gap hunt finds nothing → one line and proceed (`test_phase_skills.py:437` and `:465`)
- [ ] EC3: missing designer template fails `--sync-agents` naming the path — S2 / SID-03; no S1 evidence

---

## Impacted QA Scenarios

| Scenario | Result | Evidence |
| -------- | ------ | -------- |
| `QAS-resolve-phase-skill-procedures` | pass | Fresh `python3 tools/test_phase_skills.py` exit 0 (18 passed), including path existence for `references/gap-hunt.md` |
| `CFG-centralize-agent-model-routing` | pass | `--sync-agents` twice on the integration tree, both exit 0, both `"changed": []` |
| `ADP-adopt-workflow-safely` | untested | S1 and the r7 batch did not change `scripts/adopt.py`; no disposable adopt walk this session |

---

## Gate Check

- **Gate command**: `python3 tools/test_phase_skills.py && python3 tools/test_tlc_validators.py && bun test && git diff --check`
- **Result**: 18 + 40 + 124 passed, 0 failed, 0 skipped
- **`python3 tools/test_phase_skills.py`**: exit 0; `18 passed, 0 failed`
- **`python3 tools/test_tlc_validators.py`**: exit 0; `Ran 40 tests in 0.093s` OK
- **`bun test`**: exit 0; `124 pass`, `0 fail`, `1180 expect() calls`
- **`git diff --check`**: exit 0
- **This feature spec**: `python3 .agents/skills/workflow-spec-driven/scripts/validate_spec.py .specs/features/specify-impact-designer/spec.md` — exit 0
- **`--sync-agents` #1**: exit 0; `changed: []`
- **`--sync-agents` #2**: exit 0; `changed: []`
- **Test count before feature** (`3bb242af`): `test_phase_skills.py` 13, `test_tlc_validators.py` 35, bun 124
- **Test count after feature** (HEAD): 18, 40, 124
- **Delta**: +5 phase-skill tests (3 S1 + 2 S2), +5 validator tests (4 original size cases + Small), bun count unchanged
- **Skipped tests**: none
- **Failures**: none

---

## Fix Plans (if issues found)

None.

---

## Requirement Traceability Update

Do not edit `spec.md` in this session.

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| SID-01 | ❌ Needs Fix (`validation-s1-r6.md`) | ✅ Verified (AC4 load uiux.md when present; N20 killed) |
| SID-02 | ✅ Verified (`validation-s1-r6.md`) | ✅ Verified (unchanged; N24/N25 killed) |
| SID-03 | ⏭️ S2 (out of slice) | ⏭️ S2 (out of slice) |

---

## Summary

**Overall**: ✅ Ready

**Spec-anchored check**: 11/11 S1 ACs matched spec outcome; 0 spec-precision gaps
**Sensor**: 4/4 mutations killed
**Gate**: slice 18+40 passed; bun 124 passed; `git diff --check` clean

**What works**: The r6 N20 re-inject is dead. New mutants on Impact `journeys`, the autonomous `decisions.md` skip cite, and unhappy-path `current behaviour` die. Small Impact exemption, `none` body, template order, two-explorer Impact and gap-hunt dispatch, autonomous skip, empty-hunt line, gates green, sync idempotent.

**Issues found**: none that fail the slice.

**Next steps**: S1 checkpoint is verified. S2 remains out of this packet. Feature-level `validation.md` waits for integrated close.
