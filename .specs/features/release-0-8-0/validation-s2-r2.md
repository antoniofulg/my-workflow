# Release 0.8.0 Identity — Slice 2 Revalidation

**Date**: 2026-08-31
**Spec**: `.specs/features/release-0-8-0/spec.md`
**Diff range**: `ef408622ef8e16d6318c9e7175cb4dc73a679d82..ebcf4437d9fe302880f6c2efd27ae07c9312ef77`
**Verifier**: independent verifier (author != verifier)
**Verdict**: FAIL

## Scope

Technical revalidation covers RLS-01, RLS-02, and RLS-04 only. RLS-03 remains assigned to fresh QA Plan/Execute. RLS-05 remains assigned to remote delivery. This report makes no QA, merge, tag, GitHub Release, publication, or live Orca claim.

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | Evidence | Result |
| --- | --- | --- | --- |
| RLS-01 | Package metadata, newest changelog heading, canonical release test, and current release scenario identify `0.8.0`; `bun.lock` identifies the root package and dependency graph; package/lock dependency disagreement fails frozen install. | `package.json:3` contains `"version": "0.8.0"`; `tools/shared/tests/deep-review-installation.test.ts:67` and `tools/shared/tests/qa-skills.test.ts:1065` assert exact package version. `CHANGELOG.md:5` is the newest `0.8.0` heading; `tools/shared/tests/qa-skills.test.ts:1070-1071` asserts exact heading and equality to the manifest. `bun.lock:5-13` identifies the root name and exact direct dependency graph; `tools/shared/tests/qa-skills.test.ts:1068` asserts the root name, and changing `package.json`'s TypeScript dependency while retaining `bun.lock` makes `bun install --frozen-lockfile` exit 1. `docs/qa/scenarios/REL-report-current-workflow-release.md:19-30` identifies `0.8.0`, but no canonical assertion reads that version: changing all current-scenario `0.8.0` references to `0.8.1` left `tools/shared/tests/qa-skills.test.ts` at 30/30 passing. | **FAIL** |
| RLS-02 | Source pack remains private, contains adopted parallel tooling, and leaves no publication residue. | `package.json:4` contains `"private": true`, but no canonical assertion checks it: changing it to `false` left `tools/shared/tests/qa-skills.test.ts` at 30/30 passing. `scripts/adopt.py:44-47` assigns the probe, pilot, lock, and autonomous skill to the parallel layer. `bun pm pack --dry-run --ignore-scripts` listed `.agents/skills/autonomous/SKILL.md`, `.agents/skills/autonomous/remediation.py`, `.agents/skills/autonomous/scripts/parallel_execute.py`, `tools/orca_assisted_probe.py`, `tools/qa_parallel_pilot.py`, and `tools/resource_lock.py` in a 500-file, 3.94 MB unpacked pack. A root `find` returned `tgz_count=0` after the dry-run. | **FAIL** |
| RLS-04 | Unverified live Orca transport retains `blocked-verify` and does not claim a successful live run. | `CHANGELOG.md:22` retains `blocked-verify`; `docs/qa/scenarios/REL-report-current-workflow-release.md:25-30` keeps release QA untested and forbids converting the live lifecycle to pass; `tools/shared/tests/qa-skills.test.ts:1078` asserts the release section contains `blocked-verify`. Replacing the changelog boundary with a successful-live-run claim failed the canonical suite: 29 pass, 1 fail. | PASS |

**Spec-anchored status**: 1/3 in-scope requirements has complete discriminating proof. RLS-01 and RLS-02 retain unasserted fields.

## Discrimination Sensor

Sensors ran only in detached temporary worktrees. The real-tree porcelain was captured before the runs, compared after both worktrees were removed, and remained byte-for-byte unchanged.

| Mutation | Target | Canonical result | Outcome |
| --- | --- | --- | --- |
| Package version `0.8.0` -> `0.8.1` | `package.json:3` | 29 pass, 2 fail across 31 targeted tests | Killed |
| Honest Orca boundary -> successful live-run claim | `CHANGELOG.md:22` | 29 pass, 1 fail across 30 targeted tests | Killed |
| Bun root name `my-workflow` -> `wrong-workflow` | `bun.lock:6` | 29 pass, 1 fail across 30 targeted tests | Killed |
| TypeScript dependency `5.9.3` -> `5.9.2` with unchanged lock | `package.json:23` | `bun install --frozen-lockfile` exited 1 with `lockfile had changes, but lockfile is frozen` | Killed |
| Current scenario version `0.8.0` -> `0.8.1` | `docs/qa/scenarios/REL-report-current-workflow-release.md:19,25,37` | 30 pass, 0 fail across the canonical release suite | **Survived** |
| Package privacy `true` -> `false` | `package.json:4` | 30 pass, 0 fail across the canonical release suite | **Survived** |

**Sensor result**: 4/6 killed, 2/6 survived — FAIL.

## Gates

- `npm_config_offline=true rtk bun test tools/shared/tests/deep-review-installation.test.ts tools/shared/tests/qa-skills.test.ts` — 31 passed, 0 failed, 577 assertions.
- `npm_config_offline=true rtk bun run test:all` — 123 Bun tests passed with 1,127 assertions; all 19 tracked Python suites passed; exit 0.
- `npm_config_offline=true rtk bun pm pack --dry-run --ignore-scripts` — exit 0; 500 files; 3.94 MB unpacked; zero `.tgz` files afterward.
- `rtk python3 .agents/skills/workflow-spec-driven/scripts/validate_spec.py release-0-8-0` — 0 errors, 0 warnings.
- `rtk git diff --check ef40862..HEAD` — exit 0.

## Ranked Gaps

1. **Major — RLS-01 / current-scenario-version-unenforced**: `docs/qa/scenarios/REL-report-current-workflow-release.md:19-30` is an explicit release-version authority, but `tools/shared/tests/qa-skills.test.ts:1053-1078` never reads it. A wrong current-scenario version survives. Extend the canonical release identity case with an exact scenario-version assertion.
2. **Major — RLS-02 / package-private-boundary-unenforced**: `package.json:4` is the private distribution boundary, but neither canonical release test asserts `private === true`. A public package declaration survives. Extend the existing release identity/install assertion; do not create another suite.

## Quality and Isolation

- Bun's native lockfile contract is now stated correctly: package version belongs to `package.json`; `bun.lock` owns root identity and dependency graph; frozen install discriminates graph drift.
- Changed implementation files remain limited to release identity, changelog, scenario reset, canonical assertions, and workflow evidence.
- No remote action, publication, live Orca execution, or product/spec fix was performed.
- Both scratch worktrees were removed. Real tracked state stayed unchanged until this report was written.
- `docs/guidelines/TEST-CONTRACT.md:34-39` requires a test to assert the contracted result; both surviving mutants violate that rule.

## Requirement Traceability

| Requirement | Spec status | Revalidation result |
| --- | --- | --- |
| RLS-01 | Verified | Needs fix |
| RLS-02 | Verified | Needs fix |
| RLS-04 | Verified | Verified |

## Summary

**Overall**: Not ready for QA or remote delivery. The previous Bun-lock-version mismatch is corrected, all four required mutations are killed, and the full gate is green. Release scenario identity and package privacy remain non-discriminating, so the corrected compound acceptance criteria are not yet fully proven.
