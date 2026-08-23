# Deep Review Token Metrics Validation

**Date**: 2026-08-22
**Spec**: `.specs/features/deep-review-token-metrics/spec.md`
**Diff range**: `origin/main..b509b10`
**Phase**: technical
**Verifier**: independent sub-agent (author != verifier)
**Verdict**: PASS

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| DRM-01 | Compatible telemetry persists baseline, checkpoints, content-safe final per-thread snapshot, aggregate final provider totals, and a recomputable round delta. | `tools/test_deep_review_token_metrics.py:118` asserts baseline `100`, checkpoint delta `60`, final delta `80`, final thread total `180`, aggregate total `180`, and recomputation; `tools/test_deep_review_token_metrics.py:140` rejects altered or missing final totals/snapshots. | PASS |
| DRM-02 | Valid outputs remain preserved and cumulative checkpoints occur between serial jobs. | `tools/test_deep_review_token_metrics.py:152` asserts exit `0`, no overlap, exact order `job-1, job-2`, complete metrics, and checkpoints `[1, 2]`; `tools/test_deep_review_token_metrics.py:283` asserts a completed output is not rerun. | PASS |
| DRM-03 | Missing, invalid, regressing, incomplete, or failed observation becomes `unavailable` without changing review dispatch or exit. | `tools/test_deep_review_token_metrics.py:173` covers five telemetry/ledger faults and both jobs; `tools/test_deep_review_token_metrics.py:211` and `:234` inject checkpoint/finalize exceptions and assert exit `0`, both jobs, and `unavailable`. | PASS |
| DRM-04 | Jobs and retries have exactly one active reviewer; retry outcomes and full-scope selective resumes remain unchanged. | `tools/test_deep_review_token_metrics.py:257` asserts no overlap, retry order `job-1:1, job-1:2, job-2:1, job-2:2`, exit `0`, attempts `[2,2]`, and complete metrics; `tools/test_deep_review_token_metrics.py:303` asserts the first selective run remains `running` and the second finalizes the full round at `30` tokens. | PASS |
| DRM-05 | Metrics contain allowlisted metadata/identifiers only and use exact-shape, atomic mode-0600 persistence. | `tools/test_deep_review_token_metrics.py:338` rejects prompt/response/source fields and asserts `0600`; `tools/test_deep_review_token_metrics.py:353` proves atomic replacement and failure safety; `tools/test_deep_review_token_metrics.py:388` rejects unavailable-ledger shape/content drift. | PASS |
| DRM-06 | Shared measurement policy is provider-neutral; prompt materialization attempts pinned local Graft context and every absence/failure falls back without blocking. | `tools/test_deep_review_token_metrics.py:406` rejects control/provider leakage and requires serial neutral hooks; `tools/test_deep_review_token_metrics.py:435` executes prompt materialization and dot-directory fallback; `tools/test_deep_review_token_metrics.py:482` rejects PATH fallback; `tools/test_deep_review_token_metrics.py:497` covers map/ask/callers failures. `graft_context.py:12` accepts only a repo-local package with version `0.10.1`; `build_jobs.py:460` prepares context before rendering. | PASS |
| DRM-07 | Codex telemetry reads only allowlisted fields for the explicit reviewer subtree. | `tools/test_deep_review_token_metrics.py:546` excludes a sibling prefix and includes its child; `token_metrics.py:92` sets query-only SQLite and `token_metrics.py:98` selects only `id`, `rollout_path`, `tokens_used`, and `agent_path`. | PASS |
| DRM-08 | Unsupported providers report `unavailable` without totals, enforcement, or changed review exit. | `tools/test_deep_review_token_metrics.py:558` asserts exit `0`, `status=unavailable`, and no `total_tokens`; `subagent-runtimes.md:22` documents honest unavailability for Claude/Cursor. | PASS |

**Spec-anchored result**: 8/8 ACs matched; 0 spec-precision gaps.

## Round-2 Findings and Final Contracts

- Completed ledgers retain baseline and final per-thread snapshots, aggregate final totals, and validated recomputable delta at `token_metrics.py:221` and `token_metrics.py:344`.
- `graft_binary` ignores PATH, requires the checkout-local package and exact version `0.10.1`, and returns fallback for missing/mismatched packages at `graft_context.py:12`.
- Real Graft build/map/symbol/callers materialization produced all four expected sections; dot-directory paths were explicitly delegated to plain inspection.
- Map, symbol, callers, build, missing, mismatched, and dot-directory cases stay nonblocking at `graft_context.py:56`.
- The runner performs the sole serial job/retry loop at `run_jobs.py:250`; metrics failures are absorbed at `run_jobs.py:127`; provider blocks retain `run-blocker.json` and exit `2` at `run_jobs.py:266`.
- Shared metrics policy is provider-neutral. Codex adapter details live in `subagent-runtimes.md:22`; Claude/Cursor omit unsupported telemetry and receive `unavailable` without fabricated totals.
- No token budget, cap, enforcement, token-driven stop, `--workers`, or parallel reviewer dispatch exists in the changed contract.
- Deep review reached round 2. Post-round remediation was verified here without starting a forbidden round 3, matching `docs/guidelines/REVIEW-ROUNDS.md`.

## Post-Main Integration

- Cadence remains outside the review runner: `workflow_config.py:309-327` freezes balanced review groups and the `deep_reviewer` route; a resolved group invokes deep-review, whose jobs are then serialized at `run_jobs.py:247-258`.
- Provider routing remains outside prompt construction: `workflow_config.py:316-329` selects the provider and agent file, while `build_jobs.py:460-472` prepares the same optional Graft artifact before materializing prompts for every provider.
- Native providers use their selected `deep-reviewer` agent one at a time at `orchestration.md:60-73`; external providers use the same serialized runner at `orchestration.md:105-110`.
- Metrics stay adapter-scoped after routing: shared hooks remain provider-neutral, Codex supplies its explicit telemetry path, and unsupported providers record `unavailable` without changing cadence, dispatch, retries, or exits.
- The resumed feature predates workflow snapshots and has no feature-local `workflow.json`; integration therefore validates the current contracts rather than inventing or refreshing a route retroactively.

## Gate Check

- `npm ci`: PASS — 95 packages installed, 0 vulnerabilities. `package-lock.json` remained `56fa4b2ab3f7e8fe31d3dc948faaa1e39cfbed1e9e09118d69707f53c17af4dc`.
- `npm run review:graft:version`: PASS — `0.10.1`.
- `npm run review:graft:build`: PASS — 121 nodes, 310 edges, 15 cards.
- `python3 scripts/test_adopt.py && python3 tools/test_ad_index.py && python3 tools/test_deep_review_token_metrics.py && python3 tools/test_workflow_config.py`: PASS — 32 top-level tests (3 + 2 + 19 + 8), 0 failed.
- `npm test`: PASS — 61 passed across 6 files, 0 failed, 0 skipped.
- Aggregate automated tests: 93 passed, 0 failed, 0 skipped.
- `npm run knowledge`: PASS — 0 errors, 7 warnings (five unharvested ADs and two unharvested feature validations).
- `python3 -m py_compile` over the four changed deep-review scripts, workflow resolver, and their Python tests: PASS.
- `validate_spec.py`: PASS — 0 errors, 0 warnings.
- `check_commit.py`: PASS — 14/14 non-merge commits in `origin/main..HEAD`; the fifteenth unique commit is the main integration merge.
- `git diff --check origin/main..HEAD`: PASS.
- High-confidence secret scan: PASS.
- `skills-lock.json` remained `f49009e2789ed94b01e1a2ea90226eb2716c529105f8daee2762d877c8c6c19b`; installation/hash assertions passed in Vitest.

## Discrimination Sensor

Mutations ran only in detached temporary worktrees. Both worktrees were removed; real-tree porcelain matched the empty pre-sensor baseline.

| Mutation | Discriminating assertion | Result |
| --- | --- | --- |
| Replace computed cumulative usage with zero | `tools/test_deep_review_token_metrics.py:126` expected checkpoint delta `60`, received `0`. | KILLED |
| Reverse serial reviewer order | `tools/test_deep_review_token_metrics.py:165` expected `job-1, job-2`, received `job-2, job-1`. | KILLED |
| Remove plain-inspection guidance from Graft fallback | `tools/test_deep_review_token_metrics.py:472` required the fallback artifact to direct plain repository inspection. | KILLED |

**Sensor result**: 3/3 killed, 0 survived. PASS. All mutations used one reusable detached temporary worktree, which was removed after restoration and a clean diff check.

## Code Quality and Edge Cases

- Minimum implementation: stdlib Python for metrics/persistence; one pinned dependency for requested repository context.
- Changed files trace to observational metrics, serial review, Graft integration, installation, docs, and their canonical tests.
- Counter regression, missing baseline thread, invalid schema/content, atomic-write failure, unsupported telemetry, retry failure, selective resume, provider block, and every Graft stage failure are covered.
- No public product UI/API/CLI journey changed; technical phase only. QA Plan/Execute not dispatched.
- Spec Goals remain unchecked while traceability and Success Criteria say PASS. This is a non-behavioral documentation inconsistency, not an AC gap.

## Ranked Gaps

None blocking.

## Post-QA Adoption Fix Re-verification

`BUG-20260822-adoption-omits-graft-ignores` is fixed without reopening deep-review.

- Consumer-owned Git and search ignores survive adoption: `scripts/test_adopt.py:144-155` asserts
  both sentinels remain and every managed entry occurs exactly once.
- Graft cache and graph artifacts stay Git-ignored: `scripts/test_adopt.py:157-170` creates both
  artifacts and requires `git check-ignore` success for each.
- Generated cards remain searchable while cache and graph artifacts do not:
  `scripts/test_adopt.py:172-181` asserts the exact `rg --files` outcomes.
- The shared merge path is surgical: `scripts/adopt.py:131-144` removes only managed entries,
  preserves all other lines, and appends the canonical order; `scripts/adopt.py:181-182` applies it
  independently to `.gitignore` and `.ignore`.
- DRM-06 remains intact: the full Graft/metrics suite passed after the adoption change, including
  optional preparation and fallback contracts.

### Gates

- `python3 scripts/test_adopt.py`: PASS — 4 top-level adoption tests.
- `python3 tools/test_ad_index.py && python3 tools/test_deep_review_token_metrics.py && python3 tools/test_workflow_config.py`: PASS — 29 top-level tests.
- `npm test`: PASS — 99 tests across 9 files.
- Aggregate: 132 passed, 0 failed, 0 skipped.
- `python3 -m py_compile ... && git diff --check origin/main..HEAD`: PASS.
- `validate_spec.py`: PASS — 0 errors, 0 warnings.
- `check_commit.py --message "fix(adopt): install graft ignore contract"`: PASS.
- `npm run knowledge`: PASS — 0 errors, 7 pre-existing harvest warnings.

### Adoption Discrimination Sensor

All mutations ran sequentially in one reusable detached temporary worktree. It was restored and
removed afterward; the real-tree porcelain exactly matched its pre-sensor baseline, including all
uncommitted QA artifacts.

| Mutation | Discriminating assertion | Result |
| --- | --- | --- |
| Remove `graft/` from installed Git ignores | `scripts/test_adopt.py:151` requires the canonical Git entry. | KILLED |
| Remove `graft/.cache/` from installed search ignores | `scripts/test_adopt.py:154-155` requires the cache exclusion. | KILLED |
| Append a later `graft/` search exclusion | `scripts/test_adopt.py:179` requires the generated card in `rg --files`. | KILLED |

**Fix sensor result**: 3/3 killed, 0 survived. PASS.

## Summary

**Overall**: PASS. All 8 ACs match exact assertions; 93 tests pass; 3/3 proportional behavioral mutations die; post-main cadence/provider routing remains orthogonal to Graft and observational metrics; round-2 findings stay closed without deep-review round 3.
