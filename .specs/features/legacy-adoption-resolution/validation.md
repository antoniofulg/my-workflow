# Legacy Adoption Resolution — Integrated Technical Validation

**Verdict**: PASS
**Date**: 2026-08-31
**Spec**: `.specs/features/legacy-adoption-resolution/spec.md`
**Diff range**: `3113066a48fbca24af1c62b2e5d17122a57d921a..ece68c414a0586f6e0c47fdd0e6f916906c53e32`
**Verifier**: fresh independent Verifier (author != verifier)

## Summary

- All 11 requirements match precise spec outcomes with current `file:line` evidence.
- All 13 test-contract cases assert their contracted outcomes at the cheapest discriminating layer.
- Exact CLI syntax, JSON shape, exit codes, zero-write boundaries, and one-time manifest behavior match the public surface contract.
- The integrated Build gate passed and the highest-risk exact-set mutant was killed.
- Real checkout porcelain was empty before and after the scratch sensor.

## Spec-Anchored Requirement Evidence

| Requirement | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| LAR-01 | Separate `resolve TARGET --layers LIST --replace PATH...` command | `scripts/adopt.py:851`-`scripts/adopt.py:865`; `scripts/test_adopt.py:1121`-`scripts/test_adopt.py:1127` asserts successful public invocation and `command == "resolve"` | PASS |
| LAR-02 | Exact complete current file-conflict set publishes | `scripts/adopt.py:745`-`scripts/adopt.py:759`; `scripts/test_adopt.py:1216`-`scripts/test_adopt.py:1224` asserts exact accepted, missing incomplete, and extra/duplicate/block rejected | PASS |
| LAR-03 | Authorized paths report `replace`; later status is clean | `scripts/test_adopt.py:1126`-`scripts/test_adopt.py:1134` asserts sorted replacements, replace actions, and clean status | PASS |
| LAR-04 | Incomplete exits 1; invalid exits 2; rejected attempts write nothing | `scripts/test_adopt.py:1142`-`scripts/test_adopt.py:1151`, `scripts/test_adopt.py:1181`-`scripts/test_adopt.py:1207` assert exact codes, conflict output, snapshot equality, and absent manifest | PASS |
| LAR-05 | Require Git root, HEAD, empty porcelain; recheck before publication | `scripts/adopt.py:718`-`scripts/adopt.py:742`; `scripts/test_adopt.py:1227`-`scripts/test_adopt.py:1245` and `scripts/test_adopt.py:1365`-`scripts/test_adopt.py:1392` assert the full boundary and pre-write race rejection | PASS |
| LAR-06 | Restore bytes/modes and publish manifest last | `scripts/adopt.py:543`-`scripts/adopt.py:579`, `scripts/adopt.py:762`-`scripts/adopt.py:781`; `scripts/test_adopt.py:955`-`scripts/test_adopt.py:966` and `scripts/test_adopt.py:1340`-`scripts/test_adopt.py:1360` assert order and rollback | PASS |
| LAR-07 | `--skip-agents` preserves both instruction files byte-identically | `scripts/test_adopt.py:1308`-`scripts/test_adopt.py:1320` asserts exact bytes | PASS |
| LAR-08 | Manifest-backed target exits 2 without writes | `scripts/adopt.py:739`-`scripts/adopt.py:742`; `scripts/test_adopt.py:1295`-`scripts/test_adopt.py:1302` asserts exit 2 and identical snapshot | PASS |
| SEC-001 | Unsafe, absolute, escaping, separator-trick, and block paths exit 2 before mutation | `scripts/adopt.py:122`-`scripts/adopt.py:128`; `scripts/test_adopt.py:1199`-`scripts/test_adopt.py:1207` asserts the abuse matrix and zero writes | PASS |
| SEC-002 | Leaf and parent symlinks cannot redirect writes | `scripts/adopt.py:131`-`scripts/adopt.py:143`; `scripts/test_adopt.py:1251`-`scripts/test_adopt.py:1272` asserts unchanged target and referent snapshots | PASS |
| SEC-003 | Git and path values use direct argv; shell characters stay literal | `scripts/adopt.py:718`-`scripts/adopt.py:730`; `scripts/test_adopt.py:1397`-`scripts/test_adopt.py:1420` asserts no target- or replacement-derived sentinel effect | PASS |

**Requirement result**: 11/11 PASS; 0 spec-precision gaps.

## Test-Contract Disposition

| Case | Current evidence | Result |
| --- | --- | --- |
| UT-001 | `scripts/test_adopt.py:1216`-`scripts/test_adopt.py:1224` | PASS |
| UT-002 | `scripts/test_adopt.py:1227`-`scripts/test_adopt.py:1245` | PASS |
| IT-001 | `scripts/test_adopt.py:1110`-`scripts/test_adopt.py:1134`; manifest order at `scripts/test_adopt.py:955`-`scripts/test_adopt.py:966` | PASS |
| IT-002 | `scripts/test_adopt.py:1142`-`scripts/test_adopt.py:1151` | PASS |
| IT-003 | `scripts/test_adopt.py:1181`-`scripts/test_adopt.py:1207` | PASS |
| IT-004 | `scripts/test_adopt.py:1156`-`scripts/test_adopt.py:1176`, `scripts/test_adopt.py:1278`-`scripts/test_adopt.py:1302` | PASS |
| IT-005 | `scripts/test_adopt.py:1308`-`scripts/test_adopt.py:1320` | PASS |
| IT-006 | `scripts/test_adopt.py:1340`-`scripts/test_adopt.py:1360` | PASS |
| IT-007 | Plan read-only at `scripts/test_adopt.py:89`-`scripts/test_adopt.py:100`; apply/status/idempotence at `scripts/test_adopt.py:340`-`scripts/test_adopt.py:356`, `scripts/test_adopt.py:1134`-`scripts/test_adopt.py:1137` | PASS |
| E2E-001 | `scripts/test_adopt.py:1110`-`scripts/test_adopt.py:1137` walks plan, exact resolve, status, and byte-idempotent re-apply | PASS |
| SEC-001 | `scripts/test_adopt.py:1199`-`scripts/test_adopt.py:1207` | PASS |
| SEC-002 | `scripts/test_adopt.py:1251`-`scripts/test_adopt.py:1272` | PASS |
| SEC-003 | `scripts/test_adopt.py:1397`-`scripts/test_adopt.py:1420` | PASS |

**Test-contract result**: 13/13 PASS; no hollow or wrong-layer cases.

## Exact CLI and Public Documentation

- Parser contract: `scripts/adopt.py:851`-`scripts/adopt.py:869` exposes required target/layers, repeatable `--replace`, and optional `--json`/`--skip-agents`; no bulk flag exists.
- Result contract: `scripts/adopt.py:884`-`scripts/adopt.py:910` implements exit 0 success, exit 1 unresolved conflict, and exit 2 invalid state through `AdoptionError`.
- Public usage: `README.md:80`-`README.md:100` and `docs/adoption-prompt.md:25`-`docs/adoption-prompt.md:31` require review, a clean committed baseline, exact repeated paths, manual instruction-block repair, and post-resolve status.
- JSON ordering and fields: `scripts/test_adopt.py:1126`-`scripts/test_adopt.py:1134` assert command, ready status, empty conflicts, sorted replacements, replace actions, schema 1, and clean status.

## Discrimination Sensor

Scratch worktree detached at `ece68c414a0586f6e0c47fdd0e6f916906c53e32`; removed after testing.

| Mutation | Target | Assertion outcome | Result |
| --- | --- | --- | --- |
| Force incomplete replacement sets to report complete (`return replacements, True`) | `scripts/adopt.py:759` | `scripts/test_adopt.py:1221` failed because `complete is False` was violated | KILLED |

**Sensor result**: 1/1 killed — PASS. Real checkout porcelain was empty before sensor creation and empty after scratch removal.

## Build Gate

- **Command**: `npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check origin/main...HEAD`
- **Result**: exit 0.
- **Bun**: 123 passed, 0 failed, 1123 assertions.
- **Python adoption suite**: 81 passed, 0 failed.
- **Other Python suites**: all passed; no skipped tests reported.
- **Knowledge**: 0 errors, 36 non-blocking harvest warnings.
- **Diff check**: clean.

## Goals and Success Criteria

- Explicit path-by-path resolution: PASS — `scripts/test_adopt.py:1110`-`scripts/test_adopt.py:1134`.
- Zero writes until authorization is complete: PASS — `scripts/test_adopt.py:1142`-`scripts/test_adopt.py:1151`.
- Clean recoverable Git baseline: PASS — `scripts/test_adopt.py:1227`-`scripts/test_adopt.py:1245`, `scripts/test_adopt.py:1340`-`scripts/test_adopt.py:1360`.
- Existing transaction and manifest-last boundary: PASS — `scripts/test_adopt.py:955`-`scripts/test_adopt.py:966`.
- CRM and Creatista criterion: PASS from already-recorded read-only canary inventories at `.specs/features/legacy-adoption-resolution/context.md:44`-`.specs/features/legacy-adoption-resolution/context.md:45`, combined with deterministic exact replacement output proved at `scripts/test_adopt.py:1126`-`scripts/test_adopt.py:1130`. No active checkout was touched in this validation.

## Code Quality and Security

- Minimum surgical implementation; no compatibility layer, bulk authorization, or migration framework.
- Every feature test maps to an acceptance criterion, edge case, or named contract case.
- Guidelines applied: `docs/guidelines/TEST-CONTRACT.md`, `docs/guidelines/SECURITY.md`, `docs/guidelines/REVIEW-ROUNDS.md`.
- Threat model: `.specs/features/legacy-adoption-resolution/threat-model.md:1`-`.specs/features/legacy-adoption-resolution/threat-model.md:53`.
- SEC-001 / S6: PASS — `scripts/test_adopt.py:1199`-`scripts/test_adopt.py:1207`.
- SEC-002 / S6: PASS — `scripts/test_adopt.py:1251`-`scripts/test_adopt.py:1272`.
- SEC-003 / S11: PASS — `scripts/test_adopt.py:1397`-`scripts/test_adopt.py:1420`.
- Open Critical: 0. Open High: 0. Security verdict: PASS.

## Requirement Traceability Update

| Requirement | Previous | Current |
| --- | --- | --- |
| LAR-01 through LAR-08 | Implemented | Verified |
| SEC-001 through SEC-003 | Implemented | Verified |

## Final Verdict

**PASS** — 11/11 requirements verified, 13/13 contract cases verified, 1/1 highest-risk mutant killed, full gate green, and real checkout unchanged outside this report and evidence-backed spec status updates.
