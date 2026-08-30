# Bun Tooling Runtime S2 Validation

**Date**: 2026-08-29
**Spec**: `.specs/features/bun-tooling-runtime/spec.md`
**Diff range**: `1438b7d..f819672`
**Verifier**: independent sub-agent (author != verifier)

## Verdict

**PASS** — T3 satisfies BUN-09 and BUN-10. The installer uses fixed locked Bun arguments, fails
closed before any alternate executable or network path when `bunx` is absent, and preserves the
existing provenance, staging, rollback, environment-scrubbing, and concurrency protections.

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| T3 | PASS | Exact Bun argv and fail-closed executable boundary verified. |

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| BUN-09: locked CLI invocation | Exact `bunx --bun --no-install skills@1.5.23 add <source>#<commit> --skill <name> --agent universal --copy --yes` argv | `scripts/install_security_skills.py:522` builds the fixed argv; `tools/shared/tests/security-skills-installation.test.ts:380` asserts every executed argument vector equals the complete expected list. | PASS |
| BUN-10: missing locked executable | Non-zero exit, no npm/npx/network fallback, and no consumer mutation | `scripts/install_security_skills.py:688` resolves `bunx` before resolving `git` or running a child; `tools/shared/tests/security-skills-installation.test.ts:409` removes `bunx` from PATH, then lines 428-433 assert exit 1, unchanged consumer bytes and lock bytes, and no managed tree. | PASS |

**Spec-anchored status**: 2/2 criteria match precise spec outcomes; 0 precision gaps.

## Preserved Installer Protections

| Protection | Evidence | Result |
| --- | --- | --- |
| Pinned provenance and CLI version | `tools/shared/tests/security-skills-installation.test.ts:676` rejects changed source provenance; lines 994-1006 reject an unapproved CLI version before invocation. | PASS |
| Trusted executable path | `scripts/install_security_skills.py:483` rejects lexical/resolved tools under untrusted roots; `tools/shared/tests/security-skills-installation.test.ts:883` exercises target and pack-root rejection. | PASS |
| Staging validation | `scripts/install_security_skills.py:673` creates sibling staging and lines 701-706 validate it before publication; `tools/shared/tests/security-skills-installation.test.ts:613` rejects a staging-root executable. | PASS |
| Rollback | `scripts/install_security_skills.py:711` rolls back affected paths on installation errors; `tools/shared/tests/security-skills-installation.test.ts:519` asserts byte/link restoration after publication failure. | PASS |
| Environment scrubbing | `scripts/install_security_skills.py:545` allowlists child environment fields; `tools/shared/tests/security-skills-installation.test.ts:649` asserts target and four secret variables are absent. | PASS |
| Transient child failure | `tools/shared/tests/security-skills-installation.test.ts:439` induces CLI non-zero and lines 450-455 assert one failed transaction preserves consumer and lock bytes. | PASS |
| Concurrent publication | `tools/shared/tests/security-skills-installation.test.ts:1029` asserts the loser fails while the completed winner remains installed. | PASS |

The pinned `git fetch` wrapper at `scripts/install_security_skills.py:581` is reached only during an
authorized CLI clone after `bunx` resolved. It is not a missing-executable fallback. All verification
used fake executables and required no network.

## Discrimination Sensor

Sensors ran in detached temporary worktree `/tmp/my-workflow-bun-s2-sensor.Q8OVyw/tree`, then the
worktree was removed. Real-tree porcelain was empty before and after.

| Mutation | Expected discriminator | Result |
| --- | --- | --- |
| `--no-install` -> `--install` | Exact argv assertions | KILLED: 3 targeted tests failed. |
| trusted executable name `bunx` -> `git` | Successful Bun execution and executable-boundary assertions | KILLED: targeted suite failed. |
| allow `GITHUB_TOKEN` into child environment | Secret-scrubbing assertion | KILLED: focused test failed with `GITHUB_TOKEN=True`. |

**Sensor result**: 3/3 mutations killed; 0 survived.

## Gate Evidence

- `bun test tools/shared/tests/security-skills-installation.test.ts`: 38 passed, 0 failed, 177 expectations.
- `bun test tools/shared/tests/qa-skills.test.ts`: 27 passed, 0 failed, 528 expectations.
- `bun install --frozen-lockfile && bun run test:all`: exit 0; 117 Bun tests passed across 8 files,
  0 failed, 1070 expectations; `scripts/test_adopt.py` and all 15 `tools/**/test_*.py` suite files passed.
- `shasum -a 256 bun.lock` before and after frozen install: both
  `2017e1f780055f755fa145636d98b8f54a7dfc4fcbc89bf982f0ed42dc22cfb5`.
- Baseline `git worktree add --detach <temp> 1438b7d && bun test`: 117 passed, 0 failed across 8 files.
  S2 test-count delta: 0; existing assertions were retargeted without deletion or weakening.
- `python3 .agents/skills/workflow-spec-driven/scripts/validate_spec.py .specs/features/bun-tooling-runtime/spec.md`:
  0 errors, 0 warnings.
- `python3 .agents/skills/workflow-spec-driven/scripts/validate_tasks.py .specs/features/bun-tooling-runtime/tasks.md`:
  0 errors, 0 warnings.
- `python3 .agents/skills/workflow-spec-driven/scripts/check_commit.py --message 'test(skills): verify Bun installer checkpoint'`:
  OK.
- `git diff --check`: exit 0.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum code and no new abstraction | PASS |
| Surgical T3 boundary change | PASS |
| No npm/npx/fetch fallback on missing `bunx` | PASS |
| Existing security transaction semantics preserved | PASS |
| Tests map to BUN-09/BUN-10 and named contract cases UT-003/IT-007/SEC-001 | PASS |
| Guidelines | PASS — spec and task gates plus evidence-or-zero verifier contract applied. |

## Requirement Traceability

| Requirement | Previous | New |
| --- | --- | --- |
| BUN-09 | In Tasks | Verified by T3 |
| BUN-10 | In Tasks | Verified by T3 |

## Summary

CP-S2 is PASS. T5 may consume T3. No verifier gap, surviving mutant, skipped test, network access,
or checkout residue was found.
