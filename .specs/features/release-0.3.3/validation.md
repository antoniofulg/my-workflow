# Release 0.3.3 Validation

**Date**: 2026-08-22
**Release contract**: `CHANGELOG.md:5`
**Diff range**: `v0.3.2..75b670982f21eb2c44bf62ea2fd31a9edfd9ab36`
**Verifier**: independent sub-agent (author != verifier)
**Verdict**: PASS

## Release Contract

| Claim | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| Configurable cadence, profiles, overrides, frozen snapshots, and example | Public resolver supports `slice`, `feature`, `grouped.N`; provider precedence is override > profile > native; first resolution remains frozen | `tools/test_workflow_config.py:103` - asserts all cadence outputs and persisted snapshots; `tools/test_workflow_config.py:285` - asserts provider precedence; `tools/test_workflow_config.py:427` - asserts resumed route equals first snapshot | PASS |
| Optional pinned Graft 0.10.1 with plain fallback | Local pinned Graft is attempted; absent, failed, or dot-directory coverage uses plain inspection without blocking | `tools/test_deep_review_token_metrics.py:425` - asserts optional/non-blocking contract and exact pin; `tools/test_deep_review_token_metrics.py:435` - asserts prompt wiring and fallback outcomes | PASS |
| Serialized reviewers/retries and observational content-safe metrics without usage cap | One reviewer attempt runs at a time; retries preserve ordering; persisted metrics reject prompt/response/source content and do not gate usage | `tools/test_deep_review_token_metrics.py:152` - asserts no overlap and ordered jobs; `tools/test_deep_review_token_metrics.py:257` - asserts ordered retries; `tools/test_deep_review_token_metrics.py:338` - rejects content fields; `.agents/skills/deep-review/SKILL.md:31` - metrics are observational and no cap option exists | PASS |
| Adoption installs Graft ignores | Consumer ignores survive; generated Graft cache/graph stay ignored while cards remain searchable | `scripts/test_adopt.py:141` - asserts merged ignore entries, Git exclusion, and search visibility | PASS |
| Release authorities report 0.3.3 | Manifest, lockfile root, canonical assertions, and installed package metadata agree | `package.json:3`, `package-lock.json:3`, `package-lock.json:9`; `tools/shared/tests/deep-review-installation.test.ts:70`; `tools/shared/tests/qa-skills.test.ts:582` | PASS |

No major public capability in `v0.3.2..HEAD` is omitted from the 0.3.3 entry. No causal token-reduction claim is made. Metrics are described as observational, and the final tree contains no usage cap.

## Gate Check

- `npm ci`: PASS - 95 packages installed, 0 vulnerabilities; package-lock and skills-lock hashes unchanged.
- `npm test`: PASS - 99 tests across 9 files, 0 failed, 0 skipped.
- `python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py && python3 tools/test_deep_review_token_metrics.py && python3 tools/test_ad_index.py`: PASS - 33 top-level tests (4 + 8 + 19 + 2), 0 failed.
- `npm run knowledge`: PASS - 0 errors, 7 known harvest warnings.
- `git diff --check v0.3.2..HEAD`: PASS.
- `check_commit.py` over non-merge subjects in `v0.3.2..HEAD`: PASS - 33/33.
- Install/version: PASS - manifest, lockfile, and lockfile root are 0.3.3; installed Graft is 0.10.1.
- Stale-version scan: PASS - `0.3.2` appears only as the historical `CHANGELOG.md:17` heading.

## Discrimination Sensor

One temporary detached worktree at `75b6709` changed `package.json` from 0.3.3 to 0.3.4. Canonical version suites failed with two exact mismatches (`expected '0.3.4' to be '0.3.3'`): 2 failed, 18 passed. Mutant killed. Scratch removed; real-tree porcelain remained identical to the empty baseline.

## Warnings

- Knowledge gate reports seven pre-existing unharvested-decision/validation warnings; none is a release blocker.
- Release work has no dedicated `spec.md`; this verification uses the explicit 0.3.3 changelog entry as the release contract.

## Ranked Gaps

None.
