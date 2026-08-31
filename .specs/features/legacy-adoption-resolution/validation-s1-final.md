# Legacy Adoption Resolution — Slice 1 Final Technical Validation

**Verdict**: PASS
**Date**: 2026-08-31
**Spec**: `.specs/features/legacy-adoption-resolution/spec.md`
**Diff range**: `3113066..356de15c212d42bb936c25e12392b8de29758cc2`
**Verifier**: independent Verifier (author != verifier)

## Summary

- All 11 requirements match their spec-defined outcomes with direct `file:line` evidence.
- All 13 test-contract cases assert their contracted outcomes at the assigned layer.
- The two prior unit-layer gaps are closed: UT-001 directly covers exact, missing, extra,
  duplicate, and managed-block sets; UT-002 directly covers clean, dirty, non-Git, missing-HEAD,
  and manifest-backed targets.
- All nine prior behavioral fingerprints remain remediated.
- The full Build gate passed and all three targeted mutants were killed.

## Spec-Anchored Requirement Evidence

| Requirement | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| LAR-01 | Expose a separate repeatable `resolve TARGET --layers LIST --replace PATH...` command | Parser: `scripts/adopt.py:851`-`scripts/adopt.py:869`; public invocation and command assertion: `scripts/test_adopt.py:1121`-`scripts/test_adopt.py:1127` | PASS |
| LAR-02 | Exact complete current file-conflict set publishes | Decision helper: `scripts/adopt.py:745`-`scripts/adopt.py:759`; direct exact/missing/extra/duplicate/block assertions: `scripts/test_adopt.py:1216`-`scripts/test_adopt.py:1224` | PASS |
| LAR-03 | Every authorization reports `replace`; later status is clean | `scripts/test_adopt.py:1126`-`scripts/test_adopt.py:1134` asserts deterministic replacements/actions and clean status | PASS |
| LAR-04 | Incomplete exits 1; invalid exits 2; rejected attempts write nothing | `scripts/test_adopt.py:1142`-`scripts/test_adopt.py:1151`, `scripts/test_adopt.py:1181`-`scripts/test_adopt.py:1207` assert codes, conflicts, snapshot equality, and absent manifest | PASS |
| LAR-05 | Require Git root, HEAD, empty standard porcelain, and recheck before publication | Helper: `scripts/adopt.py:718`-`scripts/adopt.py:742`; direct eligibility matrix: `scripts/test_adopt.py:1227`-`scripts/test_adopt.py:1245`; publication-race assertion: `scripts/test_adopt.py:1365`-`scripts/test_adopt.py:1392` | PASS |
| LAR-06 | Reuse staged rollback, restore bytes/modes, and publish manifest last | Snapshot/restore: `scripts/adopt.py:543`-`scripts/adopt.py:579`; transaction: `scripts/adopt.py:762`-`scripts/adopt.py:781`; order assertion: `scripts/test_adopt.py:955`-`scripts/test_adopt.py:966`; rollback/mode assertion: `scripts/test_adopt.py:1340`-`scripts/test_adopt.py:1360` | PASS |
| LAR-07 | `--skip-agents` preserves AGENTS.md and CLAUDE.md byte-identically | Complete journey: `scripts/test_adopt.py:1113`-`scripts/test_adopt.py:1131`; focused assertion: `scripts/test_adopt.py:1308`-`scripts/test_adopt.py:1320` | PASS |
| LAR-08 | Manifest-backed targets exit 2 without writes | Eligibility helper: `scripts/adopt.py:739`-`scripts/adopt.py:742`; direct helper assertion: `scripts/test_adopt.py:1240`-`scripts/test_adopt.py:1245`; CLI snapshot assertion: `scripts/test_adopt.py:1295`-`scripts/test_adopt.py:1302` | PASS |
| SEC-001 | Unsafe, unnormalized, absolute, escaping, separator-trick, and block paths exit 2 before mutation | Normalization: `scripts/adopt.py:122`-`scripts/adopt.py:128`; direct and CLI matrices: `scripts/test_adopt.py:1211`-`scripts/test_adopt.py:1214`, `scripts/test_adopt.py:1199`-`scripts/test_adopt.py:1207` | PASS |
| SEC-002 | Resolve rejects replaceable leaf/parent symlinks without target or referent mutation | No-follow check: `scripts/adopt.py:131`-`scripts/adopt.py:143`; target/referent snapshots: `scripts/test_adopt.py:1251`-`scripts/test_adopt.py:1272` | PASS |
| SEC-003 | Git and path arguments use direct argv; shell characters remain literal | Direct Git vectors: `scripts/adopt.py:718`-`scripts/adopt.py:730`; target and replacement sentinel assertions: `scripts/test_adopt.py:1397`-`scripts/test_adopt.py:1420` | PASS |

**Requirement result**: 11/11 PASS; 0 spec-precision gaps.

## Test-Contract Disposition

| Case | Contracted evidence | Result |
| --- | --- | --- |
| UT-001 | `scripts/test_adopt.py:1216`-`scripts/test_adopt.py:1224` directly calls `_resolve_replacement_set` and asserts exact accepted, missing incomplete, and extra/duplicate/block rejected | PASS |
| UT-002 | `scripts/test_adopt.py:1227`-`scripts/test_adopt.py:1245` directly calls `_legacy_target_eligible` for clean, dirty, non-Git, missing-HEAD, and manifest-backed targets | PASS |
| IT-001 | `scripts/test_adopt.py:1110`-`scripts/test_adopt.py:1134` asserts replace actions, schema-1 manifest, and clean status; `scripts/test_adopt.py:955`-`scripts/test_adopt.py:966` observes manifest-last order | PASS |
| IT-002 | `scripts/test_adopt.py:1142`-`scripts/test_adopt.py:1151` asserts exit 1, omitted conflict, identical snapshot, and absent manifest | PASS |
| IT-003 | `scripts/test_adopt.py:1181`-`scripts/test_adopt.py:1207` asserts extra/identical/absent/unmanaged/unsafe authorizations exit 2 without writes | PASS |
| IT-004 | `scripts/test_adopt.py:1278`-`scripts/test_adopt.py:1302` asserts dirty, non-Git, missing-HEAD, and manifest-backed exit 2 with identical snapshots | PASS |
| IT-005 | `scripts/test_adopt.py:1308`-`scripts/test_adopt.py:1320` asserts both instruction files retain exact bytes | PASS |
| IT-006 | `scripts/test_adopt.py:1340`-`scripts/test_adopt.py:1360` injects publication failure and asserts full snapshot/mode restoration plus absent manifest | PASS |
| IT-007 | Existing plan read-only behavior: `scripts/test_adopt.py:89`-`scripts/test_adopt.py:100`; apply idempotence: `scripts/test_adopt.py:340`-`scripts/test_adopt.py:356`; post-resolve apply: `scripts/test_adopt.py:1134`-`scripts/test_adopt.py:1137` | PASS |
| E2E-001 | `scripts/test_adopt.py:1110`-`scripts/test_adopt.py:1137` walks plan, reviews exact conflicts, resolves with `--skip-agents`, checks clean status, and re-applies byte-idempotently | PASS |
| SEC-001 | `scripts/test_adopt.py:1199`-`scripts/test_adopt.py:1207` covers escape, absolute, separator tricks, and block key with zero writes | PASS |
| SEC-002 | `scripts/test_adopt.py:1251`-`scripts/test_adopt.py:1272` covers replaceable leaf and parent symlinks with unchanged target and referent | PASS |
| SEC-003 | `scripts/test_adopt.py:1397`-`scripts/test_adopt.py:1420` covers shell metacharacters in target and replacement values with no sentinel effect | PASS |

**Test-contract result**: 13/13 PASS; no hollow or wrong-layer cases.

## Prior Fingerprint Recheck

| Fingerprint | Prior failure | Current evidence | Result |
| --- | --- | --- | --- |
| `d4c63e98ec61a4669b1dbd6634b759f7bde2617863b55afb1d7491ccc7428e38` | Mode-free rollback | `scripts/adopt.py:543`-`scripts/adopt.py:579`; `scripts/test_adopt.py:1340`-`scripts/test_adopt.py:1360` | REMEDIATED |
| `e764687f12f632f27fcbf9ee223bc95bc62009d43c823b5d8885c338774c6043` | Ignored entries rejected | `scripts/adopt.py:730`-`scripts/adopt.py:734`; `scripts/test_adopt.py:1156`-`scripts/test_adopt.py:1176` | REMEDIATED |
| `9b9befa6faba81c705d01dea141a1430e3542596039751b862c576097d9e9dd3` | Manifest-first survived | `scripts/adopt.py:767`-`scripts/adopt.py:775`; `scripts/test_adopt.py:955`-`scripts/test_adopt.py:966`; mutation killed | REMEDIATED |
| `8f68749d989d83d3e915507b19a8f7ca899771ea7fd0a39165476dfab87518dc` | Resolve symlink outcome unproved | `scripts/test_adopt.py:1251`-`scripts/test_adopt.py:1272` | REMEDIATED |
| `3f9cbdb88bbd3cf6a8d3373b7d1e5161b8a9c3b3485282fa5674a9495ca6ba4f` | Unsafe-state zero-write gaps | `scripts/test_adopt.py:1278`-`scripts/test_adopt.py:1302` | REMEDIATED |
| `a5d1bd6befc18643e79cbdceb1804506b90010b42731a512d555f05a7caeb6ee` | Separator tricks absent | `scripts/test_adopt.py:1199`-`scripts/test_adopt.py:1207` | REMEDIATED |
| `20199e2251b4ab0f6c87a75db9fb4cb9bef614af3184312ba9eda1a4ff5de927` | Replacement metacharacters absent | `scripts/test_adopt.py:1412`-`scripts/test_adopt.py:1420` | REMEDIATED |
| `773a10fb7e3127defedcedc45e43d827051b89bd6e0df8389b8f1ff34946ed59` | Split E2E journey | `scripts/test_adopt.py:1110`-`scripts/test_adopt.py:1137` | REMEDIATED |
| `f250f2b4189cbf3756672856addcebd099bc7c380e163f1574f3adb68503dfa1` | Missing S11 threat model | `.specs/features/legacy-adoption-resolution/threat-model.md:1`-`.specs/features/legacy-adoption-resolution/threat-model.md:53` | REMEDIATED |
| `e9f41714279e0f942c1ad5032841b05e53185bfa4ba1d720e9fdaa967131b732` | UT-001 helper matrix absent | `scripts/test_adopt.py:1216`-`scripts/test_adopt.py:1224` | REMEDIATED |
| `b8f0c7c0c97468e439d33ff4393adb26044ac1b97041369c9c4a042188c88631` | UT-002 helper matrix incomplete | `scripts/test_adopt.py:1227`-`scripts/test_adopt.py:1245` | REMEDIATED |

## Discrimination Sensor

Scratch worktree: detached from `356de15c212d42bb936c25e12392b8de29758cc2`, removed after testing.

| Mutation | Target | Scoped assertion | Result |
| --- | --- | --- | --- |
| Force complete-set decision to return complete for missing authorization | `scripts/adopt.py:759` | `test_resolve_helpers_validate_replacements_and_git_boundary` failed at `scripts/test_adopt.py:1221` | KILLED |
| Accept a repository without HEAD | `scripts/adopt.py:728` | `test_resolve_legacy_target_helper_validates_full_git_boundary` failed at `scripts/test_adopt.py:1239` | KILLED |
| Allow adoption manifest into the pre-helper publication loop | `scripts/adopt.py:768` | `test_resolve_publication_writes_adoption_manifest_after_other_entries` failed at `scripts/test_adopt.py:966` | KILLED |

**Sensor result**: 3/3 killed — PASS.

Real checkout porcelain was empty before sensor creation and empty after scratch removal.

## Build Gate Evidence

- **Command**: `npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check origin/main...HEAD`
- **Result**: exit 0.
- **Bun**: 123 passed, 0 failed, 1123 assertions.
- **Python adoption suite**: 81 passed, 0 failed. Base `3113066`: 65 tests; delta: +16.
- **Other Python suites**: all passed; no skipped tests reported.
- **Knowledge**: 0 errors, 36 warnings.
- **Diff check**: clean.

## DX and Code Quality

- `.specs/features/legacy-adoption-resolution/dx.md:5`-`.specs/features/legacy-adoption-resolution/dx.md:45` matches the parser, JSON fields, exit codes, direct Git boundary, and one-time manifest behavior at `scripts/adopt.py:851`-`scripts/adopt.py:910`.
- Changed implementation is limited to the existing adopter and canonical adoption suite.
- Helpers isolate only contract-owned decisions; no compatibility layer, bulk authorization, or speculative migration framework was added.
- Tests map to the 11 requirements and 13 named cases; no unclaimed feature tests found.

## Security

- Guidance applied: `docs/guidelines/SECURITY.md`, external filesystem-writer rules, S6/S11 residual review.
- Threat model: `.specs/features/legacy-adoption-resolution/threat-model.md:1`-`.specs/features/legacy-adoption-resolution/threat-model.md:53`.
- SEC-001 / S6: PASS — `scripts/test_adopt.py:1199`-`scripts/test_adopt.py:1207`.
- SEC-002 / S6: PASS — `scripts/test_adopt.py:1251`-`scripts/test_adopt.py:1272`.
- SEC-003 / S11: PASS — `scripts/test_adopt.py:1397`-`scripts/test_adopt.py:1420`.
- Open Critical: 0.
- Open High: 0.
- Security verdict: PASS.

## Final Verdict

**PASS** — 11/11 requirements verified, 13/13 contract cases verified, 3/3 mutants killed,
full gate green, and all 11 remediation fingerprints independently rechecked.
