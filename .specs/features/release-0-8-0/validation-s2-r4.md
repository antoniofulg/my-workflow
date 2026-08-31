# Release 0.8.0 Identity — Slice 2 Revalidation Round 4

**Date**: 2026-08-31
**Spec**: `.specs/features/release-0-8-0/spec.md`
**Diff range**: `ef408622ef8e16d6318c9e7175cb4dc73a679d82..587d1b6e7b4c6f82877b9a3346842b7ca9fbe0b3`
**Verifier**: independent verifier (author != verifier)
**Verdict**: PASS

## Scope

Technical revalidation covers RLS-01, RLS-02, and RLS-04 only. RLS-03 remains assigned to fresh
QA Plan/Execute. RLS-05 remains assigned to remote delivery. This report makes no QA, merge, tag,
GitHub Release, publication, or live Orca claim.

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | Evidence | Result |
| --- | --- | --- | --- |
| RLS-01 | Package metadata, newest changelog heading, canonical release test, and current release scenario identify `0.8.0`; `bun.lock` identifies the root package and dependency graph; dependency disagreement fails frozen install. | `package.json:3` identifies `0.8.0`; `CHANGELOG.md:5` is the newest `0.8.0` heading; `docs/qa/scenarios/REL-report-current-workflow-release.md:19,25,37` identifies the current scenario as `0.8.0`; `bun.lock:5-13` identifies `my-workflow` and its exact direct dependencies. `tools/shared/tests/qa-skills.test.ts:1070,1074,1076-1078` asserts package, lock, changelog, and scenario identity; `tools/shared/tests/deep-review-installation.test.ts:67` independently asserts package version. A package dependency mismatch makes `bun install --frozen-lockfile` exit 1. | PASS |
| RLS-02 | Source pack remains private, contains adopted parallel tooling, and leaves no publication residue. | `package.json:4` is `private: true`, asserted exactly by `tools/shared/tests/qa-skills.test.ts:1071`. `scripts/adopt.py:44-47` assigns the assisted probe, parallel pilot, resource lock, and autonomous skill to the parallel layer. Package dry-run listed all four surfaces in a 502-file, 3.96 MB unpacked pack; root `.tgz` count remained zero. | PASS |
| RLS-04 | Unverified live Orca transport retains `blocked-verify` and does not claim a successful live run. | `CHANGELOG.md:22` retains `blocked-verify`; `docs/qa/scenarios/REL-report-current-workflow-release.md:28-30` forbids converting the live lifecycle to pass; `tools/shared/tests/qa-skills.test.ts:1088` asserts the boundary. Replacing the changelog boundary with a successful-live-run claim fails the canonical suite. | PASS |

**Spec-anchored status**: 3/3 in-scope requirements match their complete outcomes.

## Discrimination Sensor

The six required mutations ran only in detached scratch worktree
`/tmp/my-workflow-release080-r4-sensor.zVCmAA`. The real-tree porcelain was empty before sensor work
and remained empty after removal of the scratch worktree.

| Mutation | Target | Canonical result | Outcome |
| --- | --- | --- | --- |
| Package version `0.8.0` -> `0.8.1` | `package.json:3` | 29 pass, 2 fail across 31 targeted tests | Killed |
| Current scenario version `0.8.0` -> `0.8.1` | `docs/qa/scenarios/REL-report-current-workflow-release.md:19,25,37` | Release identity test fails at `tools/shared/tests/qa-skills.test.ts:1078` | Killed |
| Package privacy `true` -> `false` | `package.json:4` | 29 pass, 1 fail across 30 targeted tests | Killed |
| Bun root name `my-workflow` -> `wrong-workflow` | `bun.lock:6` | 29 pass, 1 fail across 30 targeted tests | Killed |
| TypeScript dependency `5.9.3` -> `5.9.2` with unchanged lock | `package.json:23` | `bun install --frozen-lockfile` exits 1: `lockfile had changes, but lockfile is frozen` | Killed |
| Honest Orca boundary -> successful live-run claim | `CHANGELOG.md:22` | 29 pass, 1 fail across 30 targeted tests | Killed |

**Sensor result**: 6/6 killed — PASS.

## Gates

- `npm_config_offline=true rtk bun test tools/shared/tests/deep-review-installation.test.ts tools/shared/tests/qa-skills.test.ts` — 31 passed, 0 failed, 580 assertions.
- `npm_config_offline=true rtk bun run test:all` — 123 Bun tests passed with 1,130 assertions; all 19 tracked Python suites passed; exit 0.
- `npm_config_offline=true rtk bun run knowledge` — 0 errors, 37 warnings; exit 0.
- `npm_config_offline=true rtk bun pm pack --dry-run --ignore-scripts` — 502 files, 3.96 MB unpacked; assisted probe, parallel pilot, resource lock, and autonomous skill present; zero `.tgz` files before and after.
- `rtk python3 .agents/skills/workflow-spec-driven/scripts/validate_spec.py release-0-8-0` — 0 errors, 0 warnings.
- `rtk git diff --check ef40862..HEAD` — exit 0.

The previous round also had 123 Bun tests; no test-count decrease occurred. The canonical targeted
suite remains 31 tests and now records 580 assertions.

## Edge Cases and Quality

- Package/lock dependency disagreement fails through Bun's native frozen-lockfile gate.
- Unverified live Orca transport remains explicitly blocked rather than overstated.
- No unrelated implementation, compatibility layer, dependency, remote action, or publication was added.
- Tests stay in the canonical release identity suite and map directly to RLS-01, RLS-02, and RLS-04.
- The diff remains limited to release identity, changelog, current scenario, canonical assertions,
  decisions, and workflow evidence.

## Requirement Traceability

| Requirement | Spec status | Revalidation result |
| --- | --- | --- |
| RLS-01 | Verified | Verified |
| RLS-02 | Verified | Verified |
| RLS-04 | Verified | Verified |

## Summary

**Overall**: PASS for the assigned technical scope. All three in-scope requirements have exact
file-and-assertion evidence, the complete gate is green, and all six required mutants are killed.
RLS-03 and RLS-05 remain intentionally unverified by this session.
