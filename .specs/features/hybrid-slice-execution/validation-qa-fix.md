# Hybrid slice execution — QA gate fix validation

**Date**: 2026-08-29
**Spec**: `.specs/features/hybrid-slice-execution/spec.md`
**Diff range**: `9653ed1^..9653ed1`
**Verifier**: independent Technical Verifier (author != verifier)
**Verdict**: PASS

## Scope and task state

This report verifies only the canonical adoption-gate correction for
`BUG-20260829-final-qa-pass-conflicts-with-adoption-gate`. T12 final QA remains open for a fresh QA
Execute retest; this technical verification did not run QA or live Orca.

## Spec-anchored acceptance criteria

| Criterion | Spec-defined outcome | Evidence | Result |
| --- | --- | --- | --- |
| HSE-33 | Final public configuration and adoption behavior receives fresh QA Plan and QA Execute sessions. | `.specs/features/hybrid-slice-execution/spec.md:185` defines the phase boundary; `.specs/features/hybrid-slice-execution/tasks.md:547` keeps the fresh QA retest pending instead of treating this Technical Verification as QA. | PASS — routing preserved; QA Execute remains next. |
| HSE-38 | Adoption carries current offline proof while the externally unverified live-host journey remains `blocked-verify` with its limitation named. | `scripts/test_adopt.py:541` asserts adoption `pass`; `scripts/test_adopt.py:542` and `scripts/test_adopt.py:543` assert the current evidence/report; `scripts/test_adopt.py:545` through `scripts/test_adopt.py:548` independently assert `blocked-verify`, upstream Orca/Codex, and fake-provider wording. | PASS |

The durable inputs match those assertions: `docs/qa/scenarios/ADP-adopt-workflow-safely.md:9`
records `pass`, lines 14–15 name current evidence and report, while
`docs/qa/scenarios/QAS-run-resource-free-parallel-orca-slices.md:9` records `blocked-verify` and lines
23–27 name the upstream Orca/Codex boundary. Both current JSON evidence files exist and pass
`python3 -m json.tool`.

## Gate check

- `python3 scripts/test_adopt.py` — exit 0; `python3 -c 'import scripts.test_adopt as t;
  print(len(t.TESTS))'` reports 24 registered adoption tests.
- `npm_config_offline=true npm run test:all` — exit 0; 8/8 Vitest files and 114/114 tests passed,
  followed by the adoption check and all tool Python suites. `find tools -type f -name
  'test_*.py' -print | wc -l` reports 15 tool Python suites.
- Skipped tests: none reported.

## Discrimination sensor

A disposable `git archive HEAD` copy changed the adoption frontmatter from `qa_status: pass` to
`qa_status: untested`, then invoked
`test_qa_registry_keeps_fake_proof_current_and_live_orca_blocked` directly.

| Mutation | Assertion | Result |
| --- | --- | --- |
| `qa_status: pass` → `qa_status: untested` | `scripts/test_adopt.py:541` — `assert "qa_status: pass" in adoption` | KILLED — exit 1, `AssertionError` |

Sensor result: 1/1 killed. Scratch was moved to Trash. Real-tree `git status --porcelain` remained
empty, and `git worktree list --porcelain` still reported exactly 2 worktrees.

## Code quality

- The fix changes the owning canonical adoption assertion, not a parallel test.
- Current evidence/report requirements were added without weakening the live-host assertion.
- No product, scenario, QA report, or live-host behavior was changed during verification.
- The implementation remains the minimum correction described by the bug.

## Summary

The QA gate correction is technically sound. It rejects stale `untested` adoption state, requires
current proof, and retains the external Orca limitation. Fresh QA Execute remains required before
T12 and feature QA can close.
