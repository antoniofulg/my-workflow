# S1 Lean Context Checkpoint Validation

**Verdict:** FAIL
**Date:** 2026-08-28
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Diff range:** `76f09e5..55fc323`
**Author commits:** `42cc7a1`, `55fc323`
**Verifier:** independent Technical Verifier (author != verifier)

## Task Completion

| Task | Recorded state | Verification result |
| --- | --- | --- |
| T1 | Done | FAIL: HSE-01 and HSE-04 do not meet the spec outcome |
| T2 | Done | FAIL: HSE-03, HSE-05, HSE-06, and HSE-42 lack discriminating proof or implementation |

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | `file:line` + assertion/evidence | Result |
| --- | --- | --- | --- |
| HSE-01 | Adoption installs `workflow-spec-driven` and leaves `tlc-spec-driven` absent. | `scripts/adopt.py:234` copies only current `COPY_PATHS`; `tools/shared/tests/qa-skills.test.ts:178` asserts absence only in the source checkout. `tmp_target=$(mktemp -d /tmp/hse-s1-adopt.XXXXXX); mkdir -p "$tmp_target/.agents/skills/tlc-spec-driven"; python3 scripts/adopt.py --skip-agents "$tmp_target"; find "$tmp_target/.agents/skills" -maxdepth 1 -type d -print` showed both skill directories after adoption. | FAIL |
| HSE-02 | NOTICE identifies adaptation, original author/source, CC BY 4.0, and material changes. | `.agents/skills/workflow-spec-driven/NOTICE.md:3` identifies the original work and author; `NOTICE.md:6` gives the source; `NOTICE.md:8` gives the license; `NOTICE.md:9` names material changes. `tools/shared/tests/qa-skills.test.ts:179`-`183` assert author, license, and source. | PASS |
| HSE-03 | A packet contains only its slice tasks, cited ACs, assigned tests, gate, design excerpt, and memory. | `.agents/skills/workflow-spec-driven/scripts/slice_packet.py:57`-`71` renders the fields, but `tools/test_workflow_spec_driven.py:58`-`65` only rejects one unknown key and `tools/test_workflow_spec_driven.py:92` only asserts one body marker. No assertion proves every required section or exclusion of whole-feature/unrelated-slice context. Evidence-or-zero applies. | FAIL |
| HSE-04 | Guidelines load only on their trigger; no phase-batch or feature-only-Verifier instruction remains. | `.agents/skills/workflow-spec-driven/SKILL.md:114`-`128` provides on-demand loading and `SKILL.md:151` requires a per-slice verifier. However `.agents/skills/workflow-spec-driven/references/tasks.md:136`-`143` still groups sequential phases into whole-phase, task-budgeted worker dispatches. `tools/shared/tests/qa-skills.test.ts:184` checks only literal `phase[- ]batch`, so this legacy behavior escapes. | FAIL |
| HSE-05 | More than 3,072 role bytes or 10,240 slice bytes reports the exact count and stops before dispatch. | `.agents/skills/workflow-spec-driven/scripts/slice_packet.py:108`-`120` contains the intended comparisons. `tools/test_workflow_spec_driven.py:70` checks role size 3,073, while `tools/test_workflow_spec_driven.py:77`-`83` uses a far-oversize packet and only asserts `>= 10,241`. No 3,072/10,240 accepted-boundary assertion exists; two threshold mutants survived. | FAIL |
| HSE-06 | Telemetry reports component and total byte counts without bodies, secrets, home paths, or environment values. | `.agents/skills/workflow-spec-driven/scripts/slice_packet.py:77`-`85` emits component counts but no total byte count. `tools/test_workflow_spec_driven.py:95`-`99` does not assert `components` or a total. | FAIL |
| HSE-42 | Every emitted diagnostic redacts secrets, environment values, packet/terminal text, and absolute home prefixes. | `tools/test_workflow_spec_driven.py:101`-`110` checks one marker in one unknown-field path only. Output write failures at `.agents/skills/workflow-spec-driven/scripts/slice_packet.py:122`-`125` escape the CLI's `PacketError` handler at `slice_packet.py:138`-`142`, allowing an absolute script path in a Python traceback. Failure-path coverage required by SEC-011 is absent. | FAIL |

**Spec-anchored result:** 1/7 requirements pass; 6/7 have implementation or proof gaps.

## Gate Check

- Current command: `npm_config_offline=true npm run test:all`
- Current result: exit 0; Vitest 8 files, 111/111 tests; every Python suite exited 0, including `tools/test_workflow_spec_driven.py` with 4/4 tests.
- Baseline command: temporary detached worktree at `76f09e5`, local `node_modules` linked, then `npm_config_offline=true npm run test:all`.
- Baseline result: exit 0; Vitest 8 files, 110/110 tests; every Python suite exited 0.
- Added-case command: `git diff --unified=0 76f09e5..55fc323 -- tools scripts | rg --pcre2 '^\+(?!\+\+\+).*(?:def test_|\bit\()'`
- Added-case result: 5 cases, one TypeScript and four Python; no test deletion was found.
- Python definition count command: `rg -n '^[[:space:]]*def test_' tools -g 'test_*.py' | wc -l`
- Python definition count: 252 current versus 248 at `76f09e5` using `git grep -nE '^[[:space:]]*def test_' 76f09e5 -- tools | wc -l`.
- Failed/skipped: 0/0 in the successful current gate.

## Discrimination Sensor

All mutations ran against detached temporary worktrees at `55fc323`. Each command was
`python3 tools/test_workflow_spec_driven.py`; each scratch was removed afterward.

| Mutation | Fault | Result |
| --- | --- | --- |
| M1 | `slice_packet.py:109`, `role_bytes > ROLE_BUDGET_BYTES` -> `>=` | SURVIVED: 4/4 tests passed |
| M2 | `slice_packet.py:115`, permit 1,000 bytes above `SLICE_BUDGET_BYTES` | SURVIVED: 4/4 tests passed |
| M3 | `slice_packet.py:84`, remove the `components` telemetry field | SURVIVED: 4/4 tests passed |

**Sensor result:** 0/3 killed, 3/3 survived. FAIL.

## Ranked Gaps

1. **Major — legacy skill survives adoption.** Premise: `scripts/adopt.py:234` copies the new sibling but has no obsolete-skill removal. Path: a project adopting over the previous workflow retains both authorities, so agents can activate the obsolete contract. Verdict: FIX_BEFORE_SHIP. Fingerprint: `HSE-01 + no obsolete sibling removal + re-adoption retains tlc-spec-driven`.
2. **Major — legacy phase-batch dispatch remains active.** Premise: `.agents/skills/workflow-spec-driven/references/tasks.md:136`-`143` assigns whole ordered phases to task-budgeted workers. Path: planner follows this reference, serializes phase groups, and reloads context contrary to slice-native execution. Verdict: FIX_BEFORE_SHIP. Fingerprint: `HSE-04 + semantic phase packing escaped literal regex + task planning dispatches whole phases`.
3. **Major — exact packet budgets are not discriminated.** Premise: `tools/test_workflow_spec_driven.py:67`-`83` omits accepted-boundary checks and uses a far-oversize slice. Path: role size 3,072 can be wrongly rejected or slice limits can drift upward while the suite remains green. Verdict: FIX_BEFORE_SHIP. Fingerprint: `HSE-05 + missing exact accepted boundaries + role or slice admission threshold drifts`.
4. **Major — telemetry omits required total bytes.** Premise: `.agents/skills/workflow-spec-driven/scripts/slice_packet.py:77`-`85` has no total field. Path: coordinator cannot compare total serialized packet cost to the contract from telemetry. Verdict: FIX_BEFORE_SHIP. Fingerprint: `HSE-06 + telemetry schema lacks total byte count + normal packet report is incomplete`.
5. **Major — slice-only packet content has evidence zero.** Premise: `tools/test_workflow_spec_driven.py:58`-`65` proves one rejection but never asserts all required rendered sections. Path: required slice context can disappear or unrelated context can enter without failing the canonical suite. Verdict: FIX_BEFORE_SHIP. Fingerprint: `HSE-03 + incomplete render assertions + packet loses or gains slice context undetected`.
6. **Major — diagnostic redaction does not cover failure paths.** Premise: output I/O errors at `slice_packet.py:122`-`125` are outside the caught error set, while SEC-011 exercises only unknown input. Path: a normal filesystem failure emits a traceback containing an absolute home path. Verdict: FIX_BEFORE_SHIP. Fingerprint: `HSE-42 + unhandled output IO and one-path redaction test + failure diagnostic leaks absolute path`.

## Isolation And Quality

- Real-tree porcelain before sensor: empty.
- Real-tree porcelain after all scratch cleanup: empty before this report was written.
- Scratch worktrees remaining after cleanup: zero.
- No production file or test was modified by the Verifier.
- Quality verdict: FAIL. The implementation is small and stdlib-only, but retained phase-batch prose, incomplete adoption cleanup, incomplete telemetry, and hollow boundary tests violate the approved contract and `docs/guidelines/TEST-CONTRACT.md:38`-`55`.

## Next Step

Route the six fingerprints to an Implementer, then run a fresh S1 Technical Verifier. CP-S1 must not
release dependent slices until every blocker is fixed and the sensor kills the boundary/telemetry mutants.
