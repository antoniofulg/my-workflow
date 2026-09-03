# Specify Impact and Designer Tasks

## Execution Protocol

Implement these tasks with the `wimplement` skill and the `workflow-spec-driven` Critical Rules. Cursor implementers read both skill files in full.

---

**Design**: `.specs/features/specify-impact-designer/design.md`
**Status**: Approved

---

## Test Coverage Matrix

> Guidelines found: `AGENTS.md`, `docs/guidelines/TEST-CONTRACT.md`, `package.json`.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Skill and template text | unit | 1:1 to spec ACs | `tools/test_phase_skills.py` | `python3 tools/test_phase_skills.py` |
| Spec validator | unit | every branch: Large, Complex, Medium, Small, `none` body | `tools/test_tlc_validators.py` | `python3 tools/test_tlc_validators.py` |
| Config materializer | integration | designer render and reject paths | `tools/test_workflow_config.py` | `python3 tools/test_workflow_config.py` |
| Adopt catalog and TS suites | integration | runtime paths and template enumerations | `scripts/test_adopt.py`, `tools/shared/tests/*.ts` | `python3 scripts/test_adopt.py && bun test` |
| Docs | none | build gate only | - | - |

## Gate Check Commands

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | Skill text tasks | `python3 tools/test_phase_skills.py` |
| Full | Validator, config, adopt tasks | `python3 tools/test_phase_skills.py && python3 tools/test_tlc_validators.py && python3 tools/test_workflow_config.py && python3 scripts/test_adopt.py && bun test` |
| Build | Slice completion | `bun run test:all && git diff --check` |

---

## Vertical Slice Closure

| Slice | Observable outcome | Independent gate | Merge if later slices are cancelled? | Why |
| --- | --- | --- | --- | --- |
| S1 | Specify writes Impact and uiux.md, offers the gap hunt, the validator enforces Impact by size, wverify reruns impacted scenarios | `python3 tools/test_phase_skills.py && python3 tools/test_tlc_validators.py` | yes | Procedure and validator stand alone |
| S2 | A designer role renders for all providers and wdesign dispatches it | `python3 tools/test_workflow_config.py && python3 scripts/test_adopt.py && bun test && python3 tools/test_phase_skills.py` | yes | Matrix role is self-contained |

## Execution Plan

### Phase 1: Specify and verify text (S1)

```
T1 → T2 → T3
```

### Phase 2: Designer role (S2)

```
T4 → T5 → T6
```

---

## Task Breakdown

### T1: Impact, uiux.md, and gap hunt in wspecify

**Slice:** S1
**What**: Add the Impact step (two explorers, `## Impact` output, one no-regression AC per affected feature), the `uiux.md` step, and the gap-hunt question to `wspecify/SKILL.md`; add `references/gap-hunt.md` (round format with numbered questions and a recommended answer each, sizing rule, autonomous rule); add `## Impact` to `references/spec-template.md`. Keep SKILL.md ≤ 200 lines. UT-002 and the template half of UT-003.
**Where**: `.agents/skills/wspecify/`
**Depends on**: None
**Reuses**: installed `grilling` round format (described, not copied)
**Requirement**: SID-01, SID-02

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] UT-002 passes; `wc -l` ≤ 200
- [x] Quick gate passes

**Tests**: unit (UT-002, UT-003)
**Gate**: quick

---

### T2: Wire wdesign, wverify, and UI-UX.md

**Slice:** S1
**What**: wdesign step 1 loads `uiux.md` when present and dispatches `designer` before internal design; wverify gains an Impact rerun step reporting each scenario id; UI-UX.md says `uiux.md` is written in Specify. Rest of UT-003.
**Where**: `.agents/skills/wdesign/SKILL.md`
**Depends on**: T1
**Reuses**: existing step numbering
**Requirement**: SID-01

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] UT-003 passes; caps hold
- [x] Quick gate passes

**Tests**: unit (UT-003)
**Gate**: quick

---

### T3: Size-aware Impact requirement in validate_spec

**Slice:** S1
**What**: Parse `Size:` from the header; require `## Impact` for Large and Complex; accept a `none` body; add UT-001 cases to `tools/test_tlc_validators.py` with fixtures.
**Where**: `.agents/skills/workflow-spec-driven/scripts/validate_spec.py`
**Depends on**: T2
**Reuses**: `section_bounds`, existing fixture directory
**Requirement**: SID-01

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] UT-001 four cases pass; this feature's spec still validates
- [x] Full gate passes

**Tests**: unit (UT-001)
**Gate**: full

---

### T4: Designer role in config and example

**Slice:** S2
**What**: Add `designer` to `ROLES` and the delegated set in `workflow_config.py`; add the three tables to `.my-workflow.toml.example` and to this checkout's `.my-workflow.toml`; extend `tools/test_workflow_config.py` role fixtures; add UT-005, IT-001, IT-002.
**Where**: `.agents/skills/workflow-config/scripts/workflow_config.py`
**Depends on**: None
**Reuses**: role loops, `make_preload_root`
**Requirement**: SID-03

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] UT-005, IT-001, IT-002 pass
- [x] Full gate passes

**Tests**: unit (UT-005), integration (IT-001, IT-002)
**Gate**: full

---

### T5: Designer templates and adopt paths

**Slice:** S2
**What**: Create the three designer templates; add designer runtime files to `RUNTIME_PATHS` in `scripts/adopt.py` and the frozen inventory in `scripts/test_adopt.py`; update TS enumerations in `tools/shared/tests/*.ts`; run sync; add UT-004 and IT-003.
**Where**: `templates/agents/`
**Depends on**: T4
**Reuses**: planner template bodies
**Requirement**: SID-03

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] UT-004, IT-003 pass; sync reports three designer packets
- [x] Full gate passes

**Tests**: unit (UT-004), integration (IT-003)
**Gate**: full

---

### T6: Docs name the designer

**Slice:** S2
**What**: AGENTS.md role line names the designer (≤ 134 lines); pack.md says five windows and lists the designer; roadmap marks slice 3 done; record AD-029 in STATE.md and run `python3 tools/ad-index.py`. UT-006.
**Where**: `AGENTS.md`
**Depends on**: T5
**Reuses**: existing role sentences
**Requirement**: SID-03

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] UT-006 passes
- [x] Build gate passes

**Tests**: unit (UT-006)
**Gate**: build

---

## Dependency Execution Map

```
Phase 1:  T1 → T2 → T3
Phase 2:  T4 → T5 → T6
```

## Task Granularity Check

| Task | Scope | Status |
| --- | --- | --- |
| T1–T3 | one skill dir, two skill files plus a guideline, one script | ✅ Granular |
| T4–T6 | one script plus fixtures, one template dir, docs | ✅ Granular |

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | none | ✅ Match |
| T2 | T1 | T1 | ✅ Match |
| T3 | T2 | T2 | ✅ Match |
| T4 | None | none | ✅ Match |
| T5 | T4 | T4 | ✅ Match |
| T6 | T5 | T5 | ✅ Match |

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1, T2 | Skill and template text | unit | unit | ✅ OK |
| T3 | Spec validator | unit | unit | ✅ OK |
| T4 | Config materializer | integration | unit + integration | ✅ OK |
| T5 | Templates, adopt, TS suites | integration | unit + integration | ✅ OK |
| T6 | Docs | none | unit (text contract) | ✅ OK |

---

### TR1: Lock the rule sentences the sensors exposed

**Slice:** S1+S2 remediation
**What**: Strengthen UT-001/002/003/004 and IT-002 so survived mutants M6–M13 (S1) and M6, M7, M8, M12, M17, M23 (S2) die. Small fixture for Impact exemption. No skill-sentence additions; the rules were already present.
**Where**: `tools/test_phase_skills.py`, `tools/test_tlc_validators.py`, `tools/test_workflow_config.py`
**Depends on**: T6
**Requirement**: SID-01, SID-02, SID-03

**Done when**:

- [x] Canonical suite discriminates each listed mutant
- [x] Gate below passes

**Tests**: unit (UT-001–004), integration (IT-002)
**Gate**: full

---

### TR2: Lock every SID-01 and SID-02 clause element

**Slice:** S1 remediation
**What**: One assertion per named SID-01 and SID-02 AC element so N5–N8 die and sibling clauses cannot hide behind a neighbour. Mapping comment at the top of the test group. No skill-sentence additions; the rules were already present.
**Where**: `tools/test_phase_skills.py`, `tools/test_tlc_validators.py`
**Depends on**: TR1
**Requirement**: SID-01, SID-02

**Done when**:

- [x] Every named SID-01 and SID-02 AC element has an assertion
- [x] N5–N8 fail in a temp copy
- [x] Gate below passes

**Tests**: unit (UT-001–003)
**Gate**: full
