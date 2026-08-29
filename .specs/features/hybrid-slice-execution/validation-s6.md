# Hybrid Slice Execution S6 Validation

**Verdict:** PASS
**Date:** 2026-08-28
**Phase:** Technical
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Diff range:** `ecb5cad..10c776d`
**Verifier:** independent session, author != verifier

## PASS

CP-S6 satisfies the scoped adoption, import-safety, ownership, and truthful-QA contract. The two
prior blocking fingerprints are remediated. No live Orca command ran.

## Task completion

| Task | Status | Notes |
| --- | --- | --- |
| T12 | PASS | Build gate, real disposable adoption, and discrimination sensor are green. |

## Spec-anchored acceptance criteria

| Requirement | Spec-defined outcome | `file:line` + assertion/evidence | Result |
| --- | --- | --- | --- |
| HSE-01 | Install only `workflow-spec-driven`; leave old TLC absent. | `scripts/adopt.py:54` installs the new skill; `scripts/adopt.py:76`-`:80` own obsolete removal; `scripts/test_adopt.py:433`-`:434` assert both old paths absent. | PASS |
| HSE-35 | Install the complete workflow at byte-identical owned destinations. | `scripts/adopt.py:43`-`:75` enumerate the owned package; `scripts/test_adopt.py:405`-`:434` compare the named authorities byte-identically. Independent adoption compared 121 owned files; the single source-only tour index is intentionally transformed by `scripts/adopt.py:252`-`:260`. | PASS |
| HSE-36 | Re-adoption updates owned files and preserves consumer config/profile. | `scripts/test_adopt.py:363`-`:400` repair stale managed files and assert `.my-workflow.toml` plus `docs/qa/README.md` retain consumer bytes. Config-overwrite and profile-overwrite mutants both failed. | PASS |
| HSE-37 | Exact offline canonical gate exercises adoption and import safety without live Orca. | `package.json:11` explicitly runs `scripts/test_adopt.py`; `scripts/test_adopt.py:439`-`:460` imports the installed probe with a call-counting fake and asserts zero calls. Removing probe COPY_PATH made the exact full gate exit 1. | PASS |
| HSE-38 | Live Orca remains honestly blocked while fake/adoption proof stays separate. | `scripts/test_adopt.py:536`-`:546` asserts current fake/adoption status and `blocked-verify`; `docs/qa/scenarios/QAS-run-resource-free-parallel-orca-slices.md:9` and `:23`-`:27` name the upstream Orca/Codex limitation. A false live `pass` mutant failed. | PASS |
| HSE-39 | Unsafe adoption destinations are rejected before any write. | `scripts/adopt.py:133`-`:153` reject symlink/non-regular nodes; `scripts/adopt.py:167`-`:217` enumerate copied, missing, ignore, config, generated-runtime, and pointer destinations before `main` mutates at `scripts/adopt.py:335`. `scripts/test_adopt.py:465`-`:533` assert rejection and unchanged trees/SHA. | PASS |

**Spec result:** 6/6 scoped requirements pass. Zero spec-precision gaps.

## Gates and real adoption

- `python3 scripts/test_adopt.py` -> exit 0, `ok`; 24 registered tests.
- `python3 -m compileall -q .agents/skills tools scripts` -> exit 0.
- `npm_config_offline=true npm run test:all` -> exit 0; 8/8 Vitest files and 114/114 tests;
  `test:python` visibly invoked `python3 scripts/test_adopt.py`, then 15 discovered tool suites.
- Independent disposable adoption -> exit 0; 121 owned files byte-identical, pointer probe present,
  old TLC authorities absent. Import -> exit 0 and fake Orca call count 0.
- `git diff --check ecb5cad..10c776d` -> exit 0; 16 files changed, 474 insertions, 37 deletions.
- Historical `docs/qa/evidence/` changes in the diff: 0.
- Worktree count before sensors: 2; after cleanup: 2.
- No skipped test or conditional adoption-suite bypass was found.

## Discrimination sensor

Every mutation ran in a detached disposable worktree. The integration checkout remained unchanged.

| Mutation | Fault | Expected owner | Result |
| --- | --- | --- | --- |
| M1 | Remove `tools/orca_assisted_probe.py` from `COPY_PATHS`. | Exact `npm_config_offline=true npm run test:all` | KILLED: full gate exit 1 at installed-probe assertion. |
| M2 | Overwrite consumer `.my-workflow.toml`. | `scripts/test_adopt.py` | KILLED: preservation assertion failed. |
| M3 | Move QA profile into managed overwrite. | `scripts/test_adopt.py` | KILLED: profile preservation assertion failed. |
| M4 | Skip obsolete TLC removal. | `scripts/test_adopt.py` | KILLED: old-authority absence assertion failed. |
| M5 | Disable symlink rejection. | `scripts/test_adopt.py` | KILLED: redirected-destination rejection assertion failed. |
| M6 | Dispatch Orca during module import. | `scripts/test_adopt.py` | KILLED: call-counting fake recorded the import effect. |
| M7 | Change live Orca QA status to `pass`. | `scripts/test_adopt.py` | KILLED: registry assertion required `blocked-verify`. |

Additional independent probes created `.gitignore`, `.ignore`, and ancestor `tools` symlinks to
outside sentinels. All three were rejected with sentinel SHA unchanged and zero partial target writes.

**Sensor result:** 7/7 mutants killed; 3/3 redirect probes rejected safely.

## Fingerprint disposition

- `1269d6cc1c356f573927510fe52e8dea0b022e7a8cf0bba5535918ad42930be9`: gate-passed;
  generated and merge destinations are preflighted before mutation.
- `bfee4dc68cce58fc7f8598cda9c9fa99ff0629d024bc01165618de7ed3bea770`: gate-passed;
  the exact canonical gate now owns and executes the adoption suite.

## Code quality and QA disposition

Implementation remains stdlib-only and reuses the existing adoption ownership model. No unrelated
product code or historical evidence changed. Active fake/adoption scenarios remain truthfully
`untested` pending fresh QA; the previously proven fallback stays `pass`; live Orca stays
`blocked-verify`. Public behavior changed, so fresh QA Plan and QA Execute remain required after
final Deep Review.

## Summary

**Overall:** PASS. CP-S6 may release to final Deep Review, then fresh QA Plan and QA Execute.
