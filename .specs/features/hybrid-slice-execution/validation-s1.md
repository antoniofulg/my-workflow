# S1 Lean Context Checkpoint Revalidation

**Verdict:** FAIL
**Date:** 2026-08-28
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Diff range:** `76f09e5..ff7271c`
**Author commits:** `42cc7a1`, `55fc323`, `ff7271c`
**Verifier:** independent Technical Verifier (author != verifier)

S1 behavior now meets all seven scoped requirements and all three former mutants are killed. CP-S1
still cannot close because the canonical convergence CLI accepts `--gate-passed` but leaves every
remediated fingerprint `open`.

## Task Completion

| Task | Recorded state | Verification result |
| --- | --- | --- |
| T1 | Done | PASS: HSE-01, HSE-02, HSE-04 match the specified outcomes |
| T2 | Done | PASS: HSE-03, HSE-05, HSE-06, HSE-42 match the specified outcomes |

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | `file:line` + assertion/evidence | Result |
| --- | --- | --- | --- |
| HSE-01 | Adoption installs `workflow-spec-driven` and leaves `tlc-spec-driven` absent. | `scripts/adopt.py:76` defines both obsolete managed paths, `scripts/adopt.py:123` removes files, links, or trees, and `scripts/adopt.py:248` performs removal before copying. `scripts/test_adopt.py:373`-`385` seeds both old paths and asserts both absent after re-adoption. | PASS |
| HSE-02 | NOTICE identifies adaptation, original author/source, CC BY 4.0, and material changes. | `.agents/skills/workflow-spec-driven/NOTICE.md:3`-`11` names the original work, author, source, license, and modifications. `tools/shared/tests/qa-skills.test.ts:180`-`184` asserts the author, license, and source. | PASS |
| HSE-03 | A packet contains only its slice tasks, cited ACs, assigned tests, gate, design excerpt, and memory. | `.agents/skills/workflow-spec-driven/scripts/slice_packet.py:13`-`24` is the strict field allowlist and `slice_packet.py:57`-`71` renders only the scoped sections. `tools/test_workflow_spec_driven.py:82`-`108` rejects transcript/full-state/unrelated-slice fields and asserts every required rendered section. | PASS |
| HSE-04 | Guidelines load only on their trigger; no phase-batch or feature-only-Verifier instruction remains. | `.agents/skills/workflow-spec-driven/SKILL.md:114`-`128` defines on-demand context loading and `SKILL.md:151` requires a fresh verifier per code-changing slice. `.agents/skills/workflow-spec-driven/references/tasks.md:136`-`137` makes dependencies, compatible slices, and sequential in-slice tasks explicit. `tools/shared/tests/qa-skills.test.ts:185`-`192` rejects semantic phase packing and feature-only verification wording. | PASS |
| HSE-05 | More than 3,072 role bytes or 10,240 slice bytes reports the exact count and stops before materialization. | `.agents/skills/workflow-spec-driven/scripts/slice_packet.py:120`-`132` rejects only values above the exact budgets before output write. `tools/test_workflow_spec_driven.py:110`-`145` proves 3,072/10,240 accepted, 3,073/10,241 rejected, exact counts reported, and no output on rejection. | PASS |
| HSE-06 | Telemetry reports component and total byte counts without bodies, secrets, home paths, or environment values. | `.agents/skills/workflow-spec-driven/scripts/slice_packet.py:74`-`89` emits only normalized counts, budgets, status, and reason. `tools/test_workflow_spec_driven.py:147`-`165` asserts exact components/total and absence of body fields and the unique body marker. | PASS |
| HSE-42 | Every emitted diagnostic redacts secrets, environment values, packet text, and absolute home prefixes. | `.agents/skills/workflow-spec-driven/scripts/slice_packet.py:105`-`118` normalizes input errors and `slice_packet.py:134`-`140` normalizes output I/O errors. `tools/test_workflow_spec_driven.py:167`-`185` asserts marker-free unknown-input diagnostics and path-free JSON/stdout/stderr/telemetry for an output I/O failure. | PASS |

**Spec-anchored result:** 7/7 scoped requirements match the specified outcome; 0 precision gaps.

## Direct Checks

- Adoption cleanup: `python3 -c 'import scripts.test_adopt as t; t.test_adoption_installs_parallel_pilot_and_preserves_consumer_config(); print("adoption cleanup: PASS")'` exited 0 and printed `adoption cleanup: PASS` after three adoption passes.
- Slice-only guidance: `rg -n "compatible slices|tasks within each slice remain sequential|fresh Technical Verifier|On-demand load" .agents/skills/workflow-spec-driven/SKILL.md .agents/skills/workflow-spec-driven/references/tasks.md` found the on-demand strategy at `SKILL.md:116`, compatible/sequential slice routing at `tasks.md:136`-`137`, and fresh verification at `tasks.md:349`.
- Redacted output I/O: `python3 -m unittest -v tools.test_workflow_spec_driven.WorkflowSpecDrivenTests.test_sec011_sensitive_unknown_input_never_enters_diagnostics` ran 1 test, 1 passed, 0 failed.

## Gate Check

- Focused packet command: `python3 tools/test_workflow_spec_driven.py`
- Focused packet result: 4/4 passed, 0 failed, 0 skipped.
- Focused adoption command: `python3 scripts/test_adopt.py`
- Focused adoption result: exit 0 and final `ok`.
- Full command: `npm_config_offline=true npm run test:all`
- Full result: exit 0; Vitest 8/8 files and 111/111 tests passed; every discovered Python suite exited 0; 0 reported failures or skips.
- Python definition count command: `rg -n '^[[:space:]]*def test_' tools -g 'test_*.py' | wc -l`
- Python definition count: 252 current.
- Baseline definition count command: `git grep -nE '^[[:space:]]*def test_' 76f09e5 -- tools | wc -l`
- Baseline definition count: 248; delta +4 definitions.

## Discrimination Sensor

Each mutation ran in its own detached temporary worktree at `ff7271c`. Command for each mutant:
`python3 tools/test_workflow_spec_driven.py`. The real-tree porcelain was empty before and after;
all three scratch worktrees were removed.

| Mutation | Fault | Result |
| --- | --- | --- |
| M1 | `slice_packet.py:121`, `role_bytes > ROLE_BUDGET_BYTES` to `>=` | KILLED: accepted 3,072-byte assertion failed; suite exit 1 |
| M2 | `slice_packet.py:127`, permit 1,000 bytes above `SLICE_BUDGET_BYTES` | KILLED: rejected 10,241-byte assertion failed; suite exit 1 |
| M3 | `slice_packet.py:84`, remove `components` telemetry | KILLED: exact telemetry assertion errored; suite exit 1 |

**Sensor result:** 3/3 killed, 0 survived.

## Convergence State

The six required `review_convergence.py` calls used each exact `--previous-fingerprint`, matching
requirement/root-cause/failure-path, `--gate-passed`, and no `--verifier-failed`. Every call returned
`"status": "open"`. Inspection found `review_convergence.py:71` accepts `gate_passed`, but
`review_convergence.py:76`-`99` never reads it to close a fingerprint.

One new failed-verification fingerprint was recorded through the same script, with the green gate:

- `14212a385ac954d4a741581971367ebdcf48aca3abed7acce5548da911aa738e`
- requirement: `cp-s1`
- root cause: `gate-passed flag is ignored`
- failure path: `remediated fingerprints remain open`
- failed remediations: 1
- status: `open`

**Fingerprint count command:** `python3 -c 'import json; p=json.load(open(".specs/features/hybrid-slice-execution/review-fingerprints.json")); from collections import Counter; print(len(p["fingerprints"]), Counter(v["status"] for v in p["fingerprints"].values()))'`

**Fingerprint result:** 7 total; 7 open; 0 closed; 0 halted.

## Ranked Gap

1. **Major — successful re-verification cannot close blocker state.** Premise:
   `.agents/skills/workflow-spec-driven/scripts/review_convergence.py:71` accepts `gate_passed`, but
   the state transition at lines 76-99 ignores it. Failure path: all six corrected blockers remain
   machine-readable as open, so CP-S1 cannot release without bypassing the canonical convergence
   script. Verdict: FIX_BEFORE_SHIP. Fingerprint:
   `CP-S1 + gate-passed flag is ignored + remediated fingerprints remain open`.

## Quality And Isolation

- The remediation is stdlib-only, surgical, and matches existing CLI/test patterns.
- No existing assertion was weakened or deleted in the inspected diff.
- Real-tree porcelain was unchanged by focused checks and mutation worktrees.
- No live Orca command ran.
- No lesson artifact was written because this verifier packet permits only the checkpoint report and convergence state.

## Next Step

Route the convergence transition gap to an Implementer. A fresh verifier must then rerun the six
successful closures and confirm 6 corrected fingerprints are closed before CP-S1 releases.
