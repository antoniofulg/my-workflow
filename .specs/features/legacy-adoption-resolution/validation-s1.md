# Legacy Adoption Resolution — Slice 1 Technical Validation

**Verdict**: FAIL
**Date**: 2026-08-31
**Spec**: `.specs/features/legacy-adoption-resolution/spec.md`
**Diff range**: `3113066..744d06cf016964077c8717e1470a80ad078c6ebb`
**Verifier**: independent Verifier (author != verifier)

## Ranked gaps

1. **Major — rollback does not restore executable modes.** Premise: `scripts/adopt.py:543` snapshots only entry kind and bytes/link target, and `scripts/adopt.py:565` restores regular files with `write_bytes()` without their original mode. Path: a clean target contains a tracked `0755` consumer file; publication reaches a later injected failure; rollback recreates that file as `0644`; `git status --porcelain` reports `M consumer.sh`, so the clean baseline required by LAR-06 is not restored. The existing test at `scripts/test_adopt.py:1208` and `scripts/test_adopt.py:1217` compares a snapshot that also omits modes. Reproduction on current code: injected `_link_claude_skills` failure returned `2`, left `consumer.sh` at `0644`, and printed `M consumer.sh`. Fingerprint: `LAR-06 + mode-free tree snapshot + failed publication leaves tracked executable mode changed`.
2. **Major — clean targets with ignored files are rejected beyond the DX contract.** Premise: `scripts/adopt.py:728` runs porcelain with `--ignored=matching`, while `.specs/features/legacy-adoption-resolution/dx.md:41` requires no porcelain entries “including untracked files,” not absence of ignored dependency/build artifacts. Path: standard `git status --porcelain --untracked-files=all` is empty, but an ignored `cache/dependency.bin` yields `!!` only because resolve opts into ignored entries; resolve exits `2` as dirty. Current-code reproduction: standard porcelain `''`; resolve exit `2`; stderr `resolve requires a clean Git target`. Fingerprint: `LAR-05 + --ignored=matching + clean target with ignored file is refused`.
3. **Major test gap — manifest-last boundary is not discriminated.** Premise: IT-001 requires manifest-last at `.specs/features/legacy-adoption-resolution/tests.md:14`, but `scripts/test_adopt.py:1095` only reads the manifest after success and `scripts/test_adopt.py:1217` only checks rollback's final snapshot. Path: a mutant writing `.my-workflow/adoption.json` before every other publication action passed both IT-001 and IT-006 tests. This survives the mandatory sensor and becomes a fix task. Fingerprint: `IT-001/LAR-06 + final-state-only assertions + manifest-first publication survives`.
4. **Major coverage gap — resolve-specific no-follow containment has zero evidence.** Premise: SEC-002 requires a replaceable leaf or parent symlink during resolve at `.specs/features/legacy-adoption-resolution/tests.md:33`. Path: existing symlink tests invoke apply/status, while no resolve test asserts exit `2`, unchanged referent, and zero target writes. `_safe_path` exists at `scripts/adopt.py:131`, but implementation presence is not contract evidence. Fingerprint: `SEC-002 + no resolve symlink case + referent/zero-write outcome unproved`.
5. **Major coverage gap — unsafe-state atomicity is only partly asserted.** Premise: IT-004 requires dirty, non-Git, missing-HEAD, and manifest-backed targets to exit `2` with zero writes at `.specs/features/legacy-adoption-resolution/tests.md:17`. Path: `scripts/test_adopt.py:1155`-`scripts/test_adopt.py:1159` checks only return codes for the first three states; only the manifest-backed branch compares a snapshot at `scripts/test_adopt.py:1165`-`scripts/test_adopt.py:1167`. Fingerprint: `IT-004 + return-code-only assertions + zero-write outcomes unproved for three target states`.
6. **Major coverage gap — contracted path/argv abuse matrix is incomplete.** SEC-001 names separator tricks, but `scripts/test_adopt.py:1138` covers only `../x`, `/tmp/x`, and a block key. SEC-003 names both target and replacement metacharacters, but `scripts/test_adopt.py:1256` exercises only a metacharacter target. Fingerprints: `SEC-001 + missing separator-trick cases + normalized-path rejection unproved`; `SEC-003 + missing replacement-metacharacter case + literal replacement argv unproved`.
7. **Major coverage gap — E2E-001 is not one complete journey.** Premise: `.specs/features/legacy-adoption-resolution/tests.md:26` requires plan, review, resolve with skip-agents, status, and re-apply. Path: `scripts/test_adopt.py:1082` begins at resolve and does not create/preserve instruction files; instruction preservation is tested separately at `scripts/test_adopt.py:1173`. No test walks the contracted sequence end to end. Fingerprint: `E2E-001 + split partial journeys + complete adoption journey unproved`.
8. **Major security-process gap — required S11 threat model is absent.** Premise: the spec declares S11 at `.specs/features/legacy-adoption-resolution/spec.md:49`, and `docs/guidelines/SECURITY.md` requires a scoped threat model when S11 changes. Path: the feature directory contains no `threat-model.md`, so Git/process isolation assumptions and attacker boundaries were never recorded before implementation. Fingerprint: `S11 + missing threat-model.md + required pre-code threat analysis absent`.

## Requirement evidence

| Requirement | Spec-defined outcome | Evidence | Result |
| --- | --- | --- | --- |
| LAR-01 | Separate repeatable `resolve ... --replace` command | `scripts/adopt.py:835`-`scripts/adopt.py:840`; invocation/assertion at `scripts/test_adopt.py:1085`-`scripts/test_adopt.py:1091` | PASS |
| LAR-02 | Exact complete current conflict set publishes | set validation at `scripts/adopt.py:870`-`scripts/adopt.py:882`; exact/incomplete/extra assertions at `scripts/test_adopt.py:1089`-`scripts/test_adopt.py:1094`, `scripts/test_adopt.py:1110`-`scripts/test_adopt.py:1114`, and `scripts/test_adopt.py:1129`-`scripts/test_adopt.py:1132` | PASS |
| LAR-03 | Every authorization reports `replace`; later status clean | `scripts/test_adopt.py:1091`-`scripts/test_adopt.py:1097` asserts command, replacement set/actions, and clean status | PASS |
| LAR-04 | Incomplete exits 1; invalid authorization exits 2; zero writes | `scripts/test_adopt.py:1108`-`scripts/test_adopt.py:1114`, `scripts/test_adopt.py:1128`-`scripts/test_adopt.py:1132`, `scripts/test_adopt.py:1141`-`scripts/test_adopt.py:1144`, `scripts/test_adopt.py:1196`-`scripts/test_adopt.py:1200` | PASS for covered inputs; separator-trick contract gap remains under SEC-001 |
| LAR-05 | Git root with HEAD and empty porcelain; second clean check | implementation `scripts/adopt.py:716`-`scripts/adopt.py:734` and `scripts/adopt.py:737`-`scripts/adopt.py:740`; dirty-race assertion `scripts/test_adopt.py:1241`-`scripts/test_adopt.py:1251` | FAIL: ignored-file overrestriction; atomicity assertions incomplete |
| LAR-06 | Existing staged rollback; manifest last | implementation `scripts/adopt.py:737`-`scripts/adopt.py:756`; rollback assertion `scripts/test_adopt.py:1208`-`scripts/test_adopt.py:1219` | FAIL: executable modes not restored; manifest-first mutant survives |
| LAR-07 | `--skip-agents` preserves AGENTS/CLAUDE bytes | `scripts/test_adopt.py:1178`-`scripts/test_adopt.py:1185` compares both byte strings | PASS |
| LAR-08 | Existing manifest exits 2 with zero writes | `scripts/adopt.py:860`-`scripts/adopt.py:863`; `scripts/test_adopt.py:1165`-`scripts/test_adopt.py:1167` | PASS |
| SEC-001 | Unsafe/unnormalized replacement paths exit 2 before mutation | path checks `scripts/adopt.py:122`-`scripts/adopt.py:128`; partial abuse assertions `scripts/test_adopt.py:1137`-`scripts/test_adopt.py:1145` | FAIL: separator tricks named by contract have no test evidence |
| SEC-002 | Resolve rejects symlink leaf/parent; referent unchanged | implementation only at `scripts/adopt.py:131`-`scripts/adopt.py:143` | FAIL: evidence-or-zero |
| SEC-003 | Git/helpers use direct argv; shell characters remain literal | direct Git vectors `scripts/adopt.py:717`-`scripts/adopt.py:728`; target sentinel assertion `scripts/test_adopt.py:1256`-`scripts/test_adopt.py:1264` | FAIL: replacement-name half of contracted abuse case unproved |

**Requirement result**: 6/11 fully verified; 5/11 have defects or evidence gaps.

## Test-contract disposition

| Case | Evidence | Result |
| --- | --- | --- |
| UT-001 | Integration assertions at `scripts/test_adopt.py:1082`-`scripts/test_adopt.py:1146` and `scripts/test_adopt.py:1190`-`scripts/test_adopt.py:1201` | GAP: not exercised at declared unit layer; separator-trick input absent |
| UT-002 | `scripts/test_adopt.py:1149`-`scripts/test_adopt.py:1167`; clean success at `scripts/test_adopt.py:1082`-`scripts/test_adopt.py:1089` | GAP: not exercised at declared unit layer; three zero-write outcomes absent |
| IT-001 | `scripts/test_adopt.py:1082`-`scripts/test_adopt.py:1097` | FAIL: manifest-last assertion hollow; mutant survived |
| IT-002 | `scripts/test_adopt.py:1105`-`scripts/test_adopt.py:1114` | PASS |
| IT-003 | `scripts/test_adopt.py:1119`-`scripts/test_adopt.py:1134` | PASS |
| IT-004 | `scripts/test_adopt.py:1149`-`scripts/test_adopt.py:1167` | GAP: zero-write assertion exists only for manifest-backed target |
| IT-005 | `scripts/test_adopt.py:1173`-`scripts/test_adopt.py:1185` | PASS |
| IT-006 | `scripts/test_adopt.py:1205`-`scripts/test_adopt.py:1219` | FAIL: byte-only snapshot misses modes; manifest ordering not observed |
| IT-007 | existing plan/conflict tests at `scripts/test_adopt.py:77`-`scripts/test_adopt.py:100` and normal apply idempotence at `scripts/test_adopt.py:1097`-`scripts/test_adopt.py:1100` | PASS |
| E2E-001 | partial flow at `scripts/test_adopt.py:1082`-`scripts/test_adopt.py:1100`; separate instruction check at `scripts/test_adopt.py:1173`-`scripts/test_adopt.py:1185` | GAP: no complete plan-to-reapply journey |
| SEC-001 | `scripts/test_adopt.py:1137`-`scripts/test_adopt.py:1145` | GAP: separator tricks absent |
| SEC-002 | no resolve-specific assertion | GAP: evidence-or-zero |
| SEC-003 | `scripts/test_adopt.py:1256`-`scripts/test_adopt.py:1264` | GAP: replacement metacharacters absent |

## Discrimination sensor

Scratch worktrees were created from `744d06cf016964077c8717e1470a80ad078c6ebb`, then removed.

| Mutation | Target | Scoped test | Result |
| --- | --- | --- | --- |
| Incomplete authorization returns `0` instead of `1` | `scripts/adopt.py:881` | `test_resolve_incomplete_authorization_reports_all_unresolved_without_writes` | KILLED |
| Disable second Git-clean check immediately before publication | `scripts/adopt.py:739` | `test_resolve_rejects_target_dirty_before_publication` | KILLED |
| Publish adoption manifest before all other staged entries | `scripts/adopt.py:741` | IT-001 success plus IT-006 rollback tests | SURVIVED — fix task required |

**Sensor result**: 2/3 killed; 1/3 survived — FAIL.

## Gate evidence

- Command: `npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check origin/main...HEAD`
- Result: exit `0`.
- Bun: 123 passed, 0 failed, 1123 assertions.
- Python adoption suite: 75 passed, 0 failed. Baseline at `3113066`: 65 cases; delta: +10.
- Other Python suites in the full gate: passed; no skipped tests reported.
- Knowledge: 0 errors, 36 warnings.
- Diff check: clean.

## CLI contract comparison

Parser at `scripts/adopt.py:826`-`scripts/adopt.py:844` matches `.specs/features/legacy-adoption-resolution/dx.md:5`: separate `resolve`, required target/layers, repeatable `--replace`, optional `--json` and `--skip-agents`, and no `--replace-all`. JSON ordering and fields are asserted at `scripts/test_adopt.py:1090`-`scripts/test_adopt.py:1094`. Git-boundary behavior differs for ignored files as ranked gap 2.

## Security

- Applied guidance: `docs/guidelines/SECURITY.md` residual review and filesystem-writer rules; no separate security skill was included in this verifier packet.
- Threat model: FAIL — `.specs/features/legacy-adoption-resolution/threat-model.md` is absent even though declared S11 requires one under `docs/guidelines/SECURITY.md`.
- SEC-001 / S6: FAIL — separator-trick evidence missing.
- SEC-002 / S6: FAIL — resolve-specific no-follow evidence missing.
- SEC-003 / S11: FAIL — target argv covered, replacement argv incomplete.
- Open Critical: 0.
- Open High: 0.
- Security verdict: FAIL due to contract evidence gaps, not an identified Critical/High vulnerability.

## Process evidence

Author initially committed documentation after a red environment gate caused by absent `node_modules`. Coordinator then performed an offline frozen dependency install and ran the exact full gate successfully (123/123 Bun tests). This is a process deviation, recorded separately; it is not a fabricated product defect and does not change the current-code gate result.

## Isolation and disposition

- Real-tree porcelain before sensor: empty.
- Real-tree porcelain after sensor cleanup: empty.
- No product code was changed.
- FAIL report intentionally remains uncommitted. No PASS validation commit was created.
