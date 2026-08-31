# Legacy Adoption Resolution — Slice 1 Technical Re-verification R2

**Verdict**: FAIL
**Date**: 2026-08-31
**Spec**: `.specs/features/legacy-adoption-resolution/spec.md`
**Diff range**: `3113066..b5c5f834c7076e7f659a04e528c5c966dcab97d3`
**Verifier**: independent Verifier (author != verifier)

## Ranked gaps

1. **Major test-contract gap — UT-001 does not directly prove complete-set validation.** Premise: UT-001 requires direct unit-layer evidence for accepting the exact current file-conflict set and rejecting missing, extra, duplicate, and managed-block authorizations at `.specs/features/legacy-adoption-resolution/tests.md:7`. The added helper test calls only `_relative_path` at `scripts/test_adopt.py:1211`-`scripts/test_adopt.py:1214`; exact-set comparison remains inline in `main` at `scripts/adopt.py:866`-`scripts/adopt.py:883` and is exercised only through CLI integration tests at `scripts/test_adopt.py:1110`-`scripts/test_adopt.py:1207`. Path: a defect in complete-set logic has no direct unit assertion despite the contract assigning that invariant to UT-001. Result: evidence-or-zero at the declared layer.
2. **Major test-contract gap — UT-002 does not directly prove the full legacy Git boundary.** Premise: UT-002 requires direct unit-layer evidence that only a clean repository with HEAD and no manifest is eligible, including dirty, non-repository, and manifest-backed cases at `.specs/features/legacy-adoption-resolution/tests.md:8`. The helper test directly calls `_git_clean_with_head` only for clean and untracked-dirty targets at `scripts/test_adopt.py:1216`-`scripts/test_adopt.py:1220`; non-Git, missing-HEAD, and manifest-backed outcomes remain CLI integration assertions at `scripts/test_adopt.py:1252`-`scripts/test_adopt.py:1276`. Path: the declared unit case does not assert its full input matrix. Result: evidence-or-zero at the declared layer.

These are test defects, not product-behaviour defects. All nine immutable fingerprints from R1 are remediated by current behavior and tests. Because the overall verdict is FAIL, none were closed; `review-fingerprints.json` remains unchanged as required by the packet's PASS-only closure rule.

## Prior fingerprint recheck

| Fingerprint | Prior failure | Current evidence | Result |
| --- | --- | --- | --- |
| `d4c63e98ec61a4669b1dbd6634b759f7bde2617863b55afb1d7491ccc7428e38` | Mode-free rollback | modes captured/restored at `scripts/adopt.py:543`-`scripts/adopt.py:579`; executable assertion at `scripts/test_adopt.py:1314`-`scripts/test_adopt.py:1334`; mode-removal mutant killed | REMEDIATED |
| `e764687f12f632f27fcbf9ee223bc95bc62009d43c823b5d8885c338774c6043` | Ignored entries rejected | standard porcelain at `scripts/adopt.py:718`-`scripts/adopt.py:734`; ignored succeeds and untracked fails at `scripts/test_adopt.py:1156`-`scripts/test_adopt.py:1176`; ignored-rejection mutant killed | REMEDIATED |
| `9b9befa6faba81c705d01dea141a1430e3542596039751b862c576097d9e9dd3` | Manifest-first survives | order observer at `scripts/test_adopt.py:955`-`scripts/test_adopt.py:967`; manifest-first mutant killed | REMEDIATED |
| `8f68749d989d83d3e915507b19a8f7ca899771ea7fd0a39165476dfab87518dc` | Resolve symlink outcome unproved | leaf and parent symlink target/referent snapshots at `scripts/test_adopt.py:1225`-`scripts/test_adopt.py:1249` | REMEDIATED |
| `3f9cbdb88bbd3cf6a8d3373b7d1e5161b8a9c3b3485282fa5674a9495ca6ba4f` | Unsafe-state zero-write gaps | snapshot equality for dirty, non-Git, missing-HEAD, and manifest-backed states at `scripts/test_adopt.py:1252`-`scripts/test_adopt.py:1276` | REMEDIATED |
| `a5d1bd6befc18643e79cbdceb1804506b90010b42731a512d555f05a7caeb6ee` | Separator tricks absent | `tools//...` and `./tools/...` rejected without writes at `scripts/test_adopt.py:1199`-`scripts/test_adopt.py:1207` | REMEDIATED |
| `20199e2251b4ab0f6c87a75db9fb4cb9bef614af3184312ba9eda1a4ff5de927` | Replacement metacharacters absent | literal replacement rejection, no sentinel, original bytes unchanged at `scripts/test_adopt.py:1386`-`scripts/test_adopt.py:1397` | REMEDIATED |
| `773a10fb7e3127defedcedc45e43d827051b89bd6e0df8389b8f1ff34946ed59` | E2E split across tests | one plan → reviewed conflicts → exact resolve with `--skip-agents` → clean status → idempotent apply journey at `scripts/test_adopt.py:1110`-`scripts/test_adopt.py:1137` | REMEDIATED |
| `f250f2b4189cbf3756672856addcebd099bc7c380e163f1574f3adb68503dfa1` | S11 threat model absent | scoped assets, trust boundaries, controls, and residuals at `.specs/features/legacy-adoption-resolution/threat-model.md:1`-`.specs/features/legacy-adoption-resolution/threat-model.md:53` | REMEDIATED |

## Requirement evidence

| Requirement | Spec-defined outcome | Evidence | Result |
| --- | --- | --- | --- |
| LAR-01 | Separate repeatable `resolve ... --replace` command | parser at `scripts/adopt.py:828`-`scripts/adopt.py:846`; public journey at `scripts/test_adopt.py:1121`-`scripts/test_adopt.py:1125` | PASS |
| LAR-02 | Exact complete current conflict set publishes | implementation at `scripts/adopt.py:866`-`scripts/adopt.py:884`; exact, incomplete, extra, and duplicate assertions at `scripts/test_adopt.py:1118`-`scripts/test_adopt.py:1207` | PASS |
| LAR-03 | Every authorization reports `replace`; later status clean | `scripts/test_adopt.py:1126`-`scripts/test_adopt.py:1137` | PASS |
| LAR-04 | Incomplete exits 1; invalid exits 2; zero writes | `scripts/test_adopt.py:1142`-`scripts/test_adopt.py:1151`, `scripts/test_adopt.py:1181`-`scripts/test_adopt.py:1207`, and `scripts/test_adopt.py:1299`-`scripts/test_adopt.py:1310` | PASS |
| LAR-05 | Git root with HEAD and empty standard porcelain; recheck before writes | `scripts/adopt.py:718`-`scripts/adopt.py:743`; ignored/untracked and dirty-race assertions at `scripts/test_adopt.py:1156`-`scripts/test_adopt.py:1176` and `scripts/test_adopt.py:1339`-`scripts/test_adopt.py:1366` | PASS |
| LAR-06 | Staged rollback restores baseline including mode; manifest last | `scripts/adopt.py:543`-`scripts/adopt.py:579`, `scripts/adopt.py:739`-`scripts/adopt.py:758`; `scripts/test_adopt.py:955`-`scripts/test_adopt.py:967` and `scripts/test_adopt.py:1314`-`scripts/test_adopt.py:1334` | PASS |
| LAR-07 | `--skip-agents` preserves AGENTS/CLAUDE bytes | `scripts/test_adopt.py:1113`-`scripts/test_adopt.py:1131` and `scripts/test_adopt.py:1282`-`scripts/test_adopt.py:1295` | PASS |
| LAR-08 | Existing manifest exits 2 with zero writes | `scripts/adopt.py:861`-`scripts/adopt.py:865`; `scripts/test_adopt.py:1269`-`scripts/test_adopt.py:1276` | PASS |
| SEC-001 | Unsafe and unnormalized paths exit 2 before mutation | `scripts/adopt.py:122`-`scripts/adopt.py:128`; `scripts/test_adopt.py:1199`-`scripts/test_adopt.py:1207` | PASS |
| SEC-002 | Resolve rejects symlink leaf/parent; target and referent unchanged | `scripts/adopt.py:131`-`scripts/adopt.py:143`; `scripts/test_adopt.py:1225`-`scripts/test_adopt.py:1249` | PASS |
| SEC-003 | Git/helpers use argv; metacharacters stay literal | direct Git argv at `scripts/adopt.py:718`-`scripts/adopt.py:730`; sentinel assertions at `scripts/test_adopt.py:1371`-`scripts/test_adopt.py:1397` | PASS |

**Requirement result**: 11/11 spec requirements match asserted outcomes. Overall FAIL comes from two declared unit cases lacking direct full-matrix evidence.

## Test-contract disposition

| Case | Evidence | Result |
| --- | --- | --- |
| UT-001 | `scripts/test_adopt.py:1211`-`scripts/test_adopt.py:1214` | FAIL: directly covers normalization only, not complete-set acceptance/rejection matrix |
| UT-002 | `scripts/test_adopt.py:1216`-`scripts/test_adopt.py:1220` | FAIL: directly covers clean and untracked dirty only, not full boundary matrix |
| IT-001 | `scripts/test_adopt.py:955`-`scripts/test_adopt.py:967`, `scripts/test_adopt.py:1110`-`scripts/test_adopt.py:1134` | PASS |
| IT-002 | `scripts/test_adopt.py:1142`-`scripts/test_adopt.py:1151` | PASS |
| IT-003 | `scripts/test_adopt.py:1181`-`scripts/test_adopt.py:1194` | PASS |
| IT-004 | `scripts/test_adopt.py:1252`-`scripts/test_adopt.py:1276` | PASS |
| IT-005 | `scripts/test_adopt.py:1282`-`scripts/test_adopt.py:1295` | PASS |
| IT-006 | `scripts/test_adopt.py:1314`-`scripts/test_adopt.py:1334` | PASS |
| IT-007 | existing plan/apply/status gates plus `scripts/test_adopt.py:1134`-`scripts/test_adopt.py:1137` | PASS |
| E2E-001 | `scripts/test_adopt.py:1110`-`scripts/test_adopt.py:1137` | PASS |
| SEC-001 | `scripts/test_adopt.py:1199`-`scripts/test_adopt.py:1207` | PASS |
| SEC-002 | `scripts/test_adopt.py:1225`-`scripts/test_adopt.py:1249` | PASS |
| SEC-003 | `scripts/test_adopt.py:1371`-`scripts/test_adopt.py:1397` | PASS |

## Discrimination sensor

Each mutation ran in a separate detached temporary worktree at `b5c5f83`; each worktree was removed afterward.

| Mutation | Targeted assertion | Result |
| --- | --- | --- |
| Remove regular-file mode restoration at `scripts/adopt.py:578`-`scripts/adopt.py:579` | `test_resolve_publication_failure_rolls_back_and_keeps_manifest_absent` | KILLED: snapshot equality failed at `scripts/test_adopt.py:1331` |
| Restore ignored-file rejection by adding `--ignored=matching` at `scripts/adopt.py:730` | `test_resolve_allows_ignored_files_but_rejects_untracked_files` | KILLED: ignored-file success assertion failed at `scripts/test_adopt.py:1165` |
| Publish manifest before other staged entries at `scripts/adopt.py:743` | `test_resolve_publication_writes_adoption_manifest_after_other_entries` | KILLED: pre-manifest workflow-write assertion failed at `scripts/test_adopt.py:965` |

**Sensor result**: 3/3 killed.

## Gate evidence

- Command: `npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check origin/main...HEAD`
- Result: exit `0`.
- Bun: 123 passed, 0 failed, 1123 assertions.
- Adoption suite: 80 passed, 0 failed. Baseline count command against `3113066`: 65; current count: 80; delta: +15.
- Other Python suites: passed; no skipped tests reported.
- Knowledge: 0 errors, 36 warnings.
- Diff check: clean.

## CLI contract comparison

The parser at `scripts/adopt.py:828`-`scripts/adopt.py:846` matches `.specs/features/legacy-adoption-resolution/dx.md:5` exactly: separate `resolve`, required target and layers, repeatable `--replace`, optional `--json` and `--skip-agents`, and no bulk replacement flag. Exit/write boundaries match `.specs/features/legacy-adoption-resolution/dx.md:7`-`.specs/features/legacy-adoption-resolution/dx.md:14`. JSON fields and deterministic replacement/action ordering are asserted at `scripts/test_adopt.py:1126`-`scripts/test_adopt.py:1134`. Standard porcelain includes untracked files but excludes ignored files, matching `.specs/features/legacy-adoption-resolution/dx.md:35`-`.specs/features/legacy-adoption-resolution/dx.md:44`. No DX mismatch found.

## Security

- Applied guidance: `docs/guidelines/SECURITY.md` residual review and external-filesystem-writer rules.
- Threat model: `.specs/features/legacy-adoption-resolution/threat-model.md:1`-`.specs/features/legacy-adoption-resolution/threat-model.md:53`.
- SEC-001 / S6: PASS at `scripts/test_adopt.py:1199`-`scripts/test_adopt.py:1207`.
- SEC-002 / S6: PASS at `scripts/test_adopt.py:1225`-`scripts/test_adopt.py:1249`.
- SEC-003 / S11: PASS at `scripts/test_adopt.py:1371`-`scripts/test_adopt.py:1397`.
- Open Critical: 0.
- Open High: 0.
- Security verdict: PASS.

## Isolation and disposition

- Real-tree porcelain before sensor: empty.
- Real-tree porcelain after sensor cleanup: empty.
- No product code was changed.
- `review-fingerprints.json` was not changed because no prior immutable fingerprint still fails and PASS-only closure was not authorized under an overall FAIL.
- FAIL report remains uncommitted. No validation commit was created.
