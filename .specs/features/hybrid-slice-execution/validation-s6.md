# Hybrid Slice Execution S6 Validation

**Verdict:** FAIL
**Date:** 2026-08-28
**Phase:** Technical
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Diff range:** `ecb5cad..53db1ed`
**Verifier:** independent session, author != verifier

## FAIL

CP-S6 is not releasable. Fresh adoption installs the intended hybrid workflow and preserves the
consumer-owned config/profile, but two blocking gaps remain: adoption can follow a symlinked
`.gitignore` outside the target, and the canonical full gate does not execute the adoption suite.
No live Orca command ran.

## Task completion

| Task | Status | Notes |
| --- | --- | --- |
| T12 | Failed verification | Implementation and focused suite are green; SEC-010 and IT-015 are not satisfied. |

## Spec-anchored acceptance criteria

| Requirement | Spec-defined outcome | `file:line` + assertion/evidence | Result |
| --- | --- | --- | --- |
| HSE-01 | Install only `workflow-spec-driven`; leave old TLC absent. | `scripts/adopt.py:54` installs the new skill; `scripts/adopt.py:77`-`:80` owns obsolete removal; `scripts/test_adopt.py:432`-`:433` assert both old paths absent. | PASS |
| HSE-35 | Install the complete workflow at byte-identical destinations. | `scripts/adopt.py:43`-`:66` own probe, autonomous runtime, resolver, skill, and guidance; `scripts/adopt.py:70`-`:75` own config/template first install; `scripts/test_adopt.py:404`-`:433` byte-compare every named authority. Disposable adoption independently compared 62 owned files and the probe. | PASS |
| HSE-36 | Re-adoption updates owned files and preserves consumer config/profile. | `scripts/test_adopt.py:376`-`:399` assert stale managed files are repaired while `.my-workflow.toml` and `docs/qa/README.md` remain byte-identical. | PASS |
| HSE-37 | The exact offline canonical gate exercises adoption and import safety without live Orca. | `package.json:10`-`:12` run Vitest plus Python discovery limited to `tools/test_*.py`; `scripts/test_adopt.py` is outside both. Removing the probe from `COPY_PATHS` left `npm_config_offline=true npm run test:all` green. | FAIL — Gap 2 |
| HSE-38 | Live Orca remains honestly blocked while fake/adoption proof is separated. | `docs/qa/scenarios/QAS-run-resource-free-parallel-orca-slices.md:9` and `:23`-`:27` retain `blocked-verify` and name the upstream Orca/Codex boundary; `scripts/test_adopt.py:489`-`:499` reject a false live pass. The changed adoption and config scenarios remain `untested` pending fresh QA, as recorded at `docs/qa/scenarios/ADP-adopt-workflow-safely.md:9` and `:81`-`:83`. | PASS for truthful pre-QA registry; fresh QA still required |
| HSE-39 | Every unsafe adoption destination is rejected before an external write. | `scripts/adopt.py:133`-`:143` preflight only `COPY_PATHS`, `COPY_MISSING_PATHS`, and `AGENTS.md`; `scripts/adopt.py:275`-`:279` later writes `.gitignore`/`.ignore`, which are omitted. A disposable `.gitignore` symlink changed an outside sentinel and adoption exited 0. | FAIL — Gap 1 |

**Spec result:** 4/6 scoped requirements pass, 2/6 fail. There are 0 spec-precision gaps.

## Ranked gaps

### Gap 1 — Blocker — unsafe adoption symlink escape

- **Premise:** `scripts/adopt.py:135` preflights only copied/missing paths and `AGENTS.md`; the merge
  targets written at `scripts/adopt.py:275`-`:279` are absent.
- **Path:** Consumer makes `.gitignore` a symlink to an outside file → adoption passes preflight →
  `merge_ignore_file` follows the symlink → outside bytes change → adoption exits 0.
- **Verdict:** Blocker. SEC-010 and HSE-35/HSE-39 require refusal before mutation.
- **Fingerprint:** `1269d6cc1c356f573927510fe52e8dea0b022e7a8cf0bba5535918ad42930be9`
  (generation 1, failed remediation 1, open).

### Gap 2 — Major — canonical gate omits adoption owner suite

- **Premise:** `package.json:11` discovers Python tests only under `tools`; the adoption owner is
  `scripts/test_adopt.py`.
- **Path:** Remove `tools/orca_assisted_probe.py` from `COPY_PATHS` → focused adoption suite fails →
  exact canonical `test:all` still exits 0 → a broken adopted workflow can ship behind a green gate.
- **Verdict:** Major. IT-015 and HSE-37 require adoption/import lanes in the canonical gate.
- **Fingerprint:** `bfee4dc68cce58fc7f8598cda9c9fa99ff0629d024bc01165618de7ed3bea770`
  (generation 1, failed remediation 1, open).

## Gates and real adoption

- `python3 scripts/test_adopt.py` -> exit 0, `ok`; 23 registered test functions.
- `python3 -m compileall -q .agents/skills tools scripts` -> exit 0.
- `npm_config_offline=true npm run test:all` -> exit 0; Vitest 8/8 files and 114/114 tests;
  15 discovered Python suites completed with no failure or skip.
- Disposable adoption -> exit 0; 62 owned source files byte-identical; probe present; old TLC absent.
- Installed import with an empty executable `PATH` -> exit 0. The focused call-counting fake at
  `scripts/test_adopt.py:438`-`:459` records zero Orca calls.
- `.specs/features/hybrid-slice-execution/review-fingerprints.json` records both blockers without
  rewriting prior fingerprints.
- `git diff --check ecb5cad..53db1ed` -> exit 0; `git diff --shortstat` reports 11 files changed,
  190 insertions, 33 deletions.
- Historical evidence under `docs/qa/evidence/` was not modified.
- Worktree count was 2 before sensors and returned to 2 after cleanup.
- No live Orca command ran.

## Discrimination sensor

Mutations ran in detached disposable worktrees. The real checkout retained only this report and
fingerprint/lesson state.

| Mutation | Fault | Focused result | Canonical-gate result |
| --- | --- | --- | --- |
| M1 | Remove probe from `COPY_PATHS`. | KILLED: missing installed probe. | SURVIVED: `test:all` exit 0. |
| M2 | Overwrite consumer `.my-workflow.toml` from the example. | KILLED: preservation assertion fails. | Not needed after M1 proved gate omission. |
| M3 | Move QA profile from copy-missing to managed overwrite. | KILLED: profile preservation assertion fails. | Not needed. |
| M4 | Retain obsolete TLC by skipping removal. | KILLED: old authority remains. | Not needed. |
| M5 | Disable managed-destination symlink rejection. | KILLED: rejection assertion fails. | Not needed. |
| M6 | Dispatch `orca` at module import. | KILLED: call-counting fake records a call. | Not needed. |
| M7 | Falsely mark live Orca scenario `pass`. | KILLED: registry assertion requires `blocked-verify`. | Not needed. |

**Sensor result:** focused adoption suite killed 7/7 required mutations. One additional canonical-gate
probe survived, creating Gap 2. A direct behavior probe also exposed the untested `.gitignore`
symlink path, creating Gap 1.

## Code quality and QA disposition

The implementation is stdlib-only, uses existing adoption ownership conventions, ships no live
Orca dependency, and does not alter historical evidence. No unrelated refactor was found. The
symlink preflight is incomplete because it does not enumerate every adoption write target.

Public behavior changed. Technical verification stops here. QA Plan and QA Execute must wait for
both blocking fixes and a fresh independent Technical Verifier. The live-host journey remains
`blocked-verify`; no fake result is presented as live-host success.

## Summary

**Overall:** FAIL. Route Gap 1 and Gap 2 to an Implementer, then dispatch a fresh S6 Technical
Verifier. Do not start final Deep Review or QA from this checkpoint.
