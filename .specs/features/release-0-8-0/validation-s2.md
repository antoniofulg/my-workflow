# Release 0.8.0 Identity — Slice 2 Validation

**Date**: 2026-08-31
**Spec**: `.specs/features/release-0-8-0/spec.md`
**Diff range**: `ef408622ef8e16d6318c9e7175cb4dc73a679d82..50e904b777abbf40b900f253c2ec8c9005de7cbe`
**Verifier**: independent verifier (author != verifier)
**Verdict**: FAIL

## Scope

Technical verification covers RLS-01, RLS-02, and RLS-04 only. RLS-03 remains assigned to fresh QA Plan/Execute. RLS-05 remains assigned to remote delivery. This report makes no QA, merge, tag, GitHub Release, publication, or live Orca claim.

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | Evidence | Result |
| --- | --- | --- | --- |
| RLS-01 | Package metadata, Bun lockfile, newest changelog heading, canonical release test, and current scenario identify `0.8.0`; package/lock disagreement fails the gate. | `package.json:3` contains `"version": "0.8.0"`; `CHANGELOG.md:5` heads the newest section with `0.8.0`; `docs/qa/scenarios/REL-report-current-workflow-release.md:19` and `:24` identify `0.8.0`; `tools/shared/tests/deep-review-installation.test.ts:67` asserts `packageManifest.version === "0.8.0"`; `tools/shared/tests/qa-skills.test.ts:1065` and `:1070-1071` assert package/changelog identity. `bun.lock:5-13` contains the root name and dependencies but no root version, while `tools/shared/tests/qa-skills.test.ts:1068` asserts only the root name. A `bun.lock` root version mutation to `0.7.0` survived 31/31 targeted tests. | **FAIL** |
| RLS-02 | Source pack remains private, contains adopted parallel tooling, and leaves no publication residue. | `package.json:2-4` reports name `my-workflow`, version `0.8.0`, and `private: true`. `scripts/adopt.py:44-47` assigns `tools/qa_parallel_pilot.py`, `tools/orca_assisted_probe.py`, `tools/resource_lock.py`, and `.agents/skills/autonomous` to the parallel layer. `npm_config_offline=true rtk bun pm pack --dry-run --ignore-scripts` listed those paths in a 498-file, 3.93 MB unpacked source pack. `rtk find . -maxdepth 1 -type f -name '*.tgz' -print` returned no path before or after the dry-run. | PASS |
| RLS-04 | Unverified live Orca transport retains `blocked-verify` and does not claim a successful live run. | `CHANGELOG.md:22` explicitly retains `blocked-verify`; `docs/qa/scenarios/REL-report-current-workflow-release.md:24-29` leaves release QA untested and forbids converting the live lifecycle to pass; `tools/shared/tests/qa-skills.test.ts:1078` asserts the stable release section contains `blocked-verify`. Replacing the changelog boundary with a successful-live-run claim failed the canonical test. | PASS |

**Spec-anchored status**: 2/3 in-scope requirements match their complete outcomes. RLS-01 is not satisfied.

## Discrimination Sensor

The sensor ran in detached temporary worktree `/tmp/my-workflow-release080-sensor.Bg3s0G`, with the real-tree porcelain captured as empty before the run and confirmed empty after removal.

| Mutation | Target | Canonical result | Outcome |
| --- | --- | --- | --- |
| Package version `0.8.0` -> `0.8.1` | `package.json:3` | 29 pass, 2 fail across 31 targeted tests; failures at `tools/shared/tests/qa-skills.test.ts:1065` and `tools/shared/tests/deep-review-installation.test.ts:67` | Killed |
| Honest Orca boundary -> successful live-run claim | `CHANGELOG.md:22` | 29 pass, 1 fail across `tools/shared/tests/qa-skills.test.ts`; failure at `:1078` | Killed |
| Add conflicting root `version: 0.7.0` | `bun.lock:7` in scratch | 31 pass, 0 fail, 577 assertions | **Survived** |

**Sensor result**: 2/3 killed, 1/3 survived — FAIL.

## Gates

- `npm_config_offline=true rtk bun test tools/shared/tests/deep-review-installation.test.ts tools/shared/tests/qa-skills.test.ts` — 31 passed, 0 failed, 577 assertions.
- `npm_config_offline=true rtk bun run test:all` — 123 Bun tests passed with 1,127 assertions; all 19 tracked Python suites passed; exit 0.
- `npm_config_offline=true rtk bun pm pack --dry-run --ignore-scripts` — exit 0; 498 files; 3.93 MB unpacked; no `.tgz` residue.
- `rtk git diff --check ef408622ef8e16d6318c9e7175cb4dc73a679d82..50e904b777abbf40b900f253c2ec8c9005de7cbe` — exit 0.

## Ranked Gaps

1. **Major — RLS-01 / `RLS-01-bun-lock-version-unenforced`**: `bun.lock` does not identify release `0.8.0`, despite the acceptance criterion and edge case requiring that authority and requiring package/lock disagreement to fail. The canonical test checks only `"name": "my-workflow"`, so a conflicting root version survives. Resolve by either making `bun.lock` a real version authority with a canonical exact-match assertion, or correcting the spec to Bun's actual lockfile contract and naming the authority that can discriminate package-version drift. A fresh verifier must rerun the sensor after the fix.

## Quality and Isolation

- Changed files remain limited to release identity, changelog, scenario reset, tests, and spec traceability.
- No remote action, publication, live Orca execution, or product-code fix was performed.
- Package dry-run created no archive residue.
- Scratch worktree was removed; real tracked files stayed unchanged before this report.
- `docs/guidelines/TEST-CONTRACT.md:34-39` requires the contracted expected result rather than a hollow existence check; the surviving lockfile mutant violates that rule.

## Summary

**Overall**: Not ready for QA or remote delivery. Package identity, private source-pack boundary, and honest Orca boundary are present, but RLS-01's Bun lockfile authority is absent and its disagreement gate is non-discriminating.
