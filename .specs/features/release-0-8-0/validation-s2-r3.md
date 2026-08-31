# Release 0.8.0 Identity — Slice 2 Revalidation Round 3

**Date**: 2026-08-31
**Spec**: `.specs/features/release-0-8-0/spec.md`
**Diff range**: `ef408622ef8e16d6318c9e7175cb4dc73a679d82..ec63563ee188308dc55696d92d352a7882d5a8be`
**Verifier**: independent verifier (author != verifier)
**Verdict**: FAIL

## Scope

Technical revalidation covers RLS-01, RLS-02, and RLS-04 only. RLS-03 remains assigned to fresh
QA Plan/Execute. RLS-05 remains assigned to remote delivery. This report makes no QA, merge, tag,
GitHub Release, publication, or live Orca claim.

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | Evidence | Result |
| --- | --- | --- | --- |
| RLS-01 | Package metadata, newest changelog heading, canonical release test, and current release scenario identify `0.8.0`; `bun.lock` identifies the root package and dependency graph; package/lock dependency disagreement fails frozen install. | `package.json:3` and `CHANGELOG.md:5` identify `0.8.0`; `tools/shared/tests/deep-review-installation.test.ts:67` and `tools/shared/tests/qa-skills.test.ts:1067,1073-1074` assert those authorities exactly. `bun.lock:6-13` records the root name and direct dependency graph; `tools/shared/tests/qa-skills.test.ts:1071` asserts the root name, and changing `package.json:23` while retaining the lock makes `bun install --frozen-lockfile` exit 1. `docs/qa/scenarios/REL-report-current-workflow-release.md:19,25,37` identifies `0.8.0`, but the only scenario assertion at `tools/shared/tests/qa-skills.test.ts:1075-1077` checks a version-neutral `expected:` field. Changing all three current-scenario references to `0.8.1` leaves the canonical suite at 31/31 passing. | **FAIL** |
| RLS-02 | Source pack remains private, contains adopted parallel tooling, and leaves no publication residue. | `package.json:4` is `private: true`; `tools/shared/tests/qa-skills.test.ts:1068` asserts it exactly, and changing it to `false` fails the canonical suite. `scripts/adopt.py:44-47` assigns the parallel pilot, assisted probe, resource lock, and autonomous skill to the parallel layer. `bun pm pack --dry-run --ignore-scripts` completed with 501 files and 3.95 MB unpacked; root `.tgz` count remained 0 before and after. | PASS |
| RLS-04 | Unverified live Orca transport retains `blocked-verify` and does not claim a successful live run. | `CHANGELOG.md:22` retains `blocked-verify`; `docs/qa/scenarios/REL-report-current-workflow-release.md:28-30` forbids converting the live lifecycle to pass; `tools/shared/tests/qa-skills.test.ts:1084` asserts the boundary. Replacing the changelog boundary with a successful-live-run claim fails the canonical suite. | PASS |

**Spec-anchored status**: 2/3 in-scope requirements match their complete outcomes. RLS-01 remains
non-discriminating for the current scenario's version.

## Discrimination Sensor

The six required mutations ran in detached worktree
`/tmp/my-workflow-release080-r3-sensor.2HuaeV`. The real-tree porcelain was empty before sensor
work and remained empty after forced removal of the scratch worktree.

| Mutation | Target | Canonical result | Outcome |
| --- | --- | --- | --- |
| Package version `0.8.0` -> `0.8.1` | `package.json:3` | 29 pass, 2 fail across 31 targeted tests | Killed |
| Current scenario version `0.8.0` -> `0.8.1` | `docs/qa/scenarios/REL-report-current-workflow-release.md:19,25,37` | 31 pass, 0 fail, 579 assertions | **Survived** |
| Package privacy `true` -> `false` | `package.json:4` | 30 pass, 1 fail across 31 targeted tests | Killed |
| Bun root name `my-workflow` -> `wrong-workflow` | `bun.lock:6` | 30 pass, 1 fail across 31 targeted tests | Killed |
| TypeScript dependency `5.9.3` -> `5.9.2` with unchanged lock | `package.json:23` | `bun install --frozen-lockfile` exited 1 with `lockfile had changes, but lockfile is frozen` | Killed |
| Honest Orca boundary -> successful live-run claim | `CHANGELOG.md:22` | 30 pass, 1 fail across 31 targeted tests | Killed |

**Sensor result**: 5/6 killed, 1/6 survived — FAIL.

## Gates

- `npm_config_offline=true rtk bun test tools/shared/tests/deep-review-installation.test.ts tools/shared/tests/qa-skills.test.ts` — 31 passed, 0 failed, 579 assertions.
- `npm_config_offline=true rtk bun run test:all` — 123 Bun tests passed with 1,129 assertions; every tracked Python suite passed; exit 0.
- `npm_config_offline=true rtk bun run knowledge` — 0 errors, 37 warnings; exit 0.
- `npm_config_offline=true rtk bun pm pack --dry-run --ignore-scripts` — exit 0; 501 files; 3.95 MB unpacked; zero `.tgz` files before and after.
- `rtk python3 .agents/skills/workflow-spec-driven/scripts/validate_spec.py release-0-8-0` — 0 errors, 0 warnings.
- `rtk git diff --check ef40862..HEAD` — exit 0.

## Ranked Gaps

1. **Major — RLS-01 / `current-scenario-version-unenforced`**: the remediation asserts the
   scenario's exact `expected:` field, but that field is intentionally version-neutral. It does not
   assert the three current `0.8.0` authorities at
   `docs/qa/scenarios/REL-report-current-workflow-release.md:19,25,37`. The same immutable mutant
   survives for a second failed remediation. Extend the existing canonical release identity case
   with an exact assertion over the current scenario version; do not add another suite.

## Quality and Isolation

- The diff remains limited to release identity, changelog, current scenario, canonical assertions,
  and workflow evidence.
- `docs/guidelines/TEST-CONTRACT.md:53-55` requires the contracted result, not a hollow existence or
  adjacent-field check. The scenario assertion remains adjacent to, rather than discriminating for,
  the required version.
- No remote action, publication, live Orca execution, QA execution, or product-code fix occurred.
- The scratch worktree was removed. The real tree was unchanged until this report was written.

## Requirement Traceability

| Requirement | Spec status | Revalidation result |
| --- | --- | --- |
| RLS-01 | Verified | Needs fix |
| RLS-02 | Verified | Verified |
| RLS-04 | Verified | Verified |

## Summary

**Overall**: Not ready for QA or remote delivery. Private packaging, Bun dependency-graph drift, and
the honest Orca boundary are discriminating. The current scenario can still claim release `0.8.1`
while all canonical release tests pass.
