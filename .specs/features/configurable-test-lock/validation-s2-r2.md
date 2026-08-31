# Configurable Test Lock — Slice S2 Revalidation R2

**Date**: 2026-08-30
**Spec**: `.specs/features/configurable-test-lock/spec.md`
**Diff range**: `f354e72..c29cded`
**Verifier**: fresh independent Technical Verifier (author != verifier)
**Verdict**: PASS

## Task Completion

| Task | Status | Evidence |
| --- | --- | --- |
| T2 | PASS | CTL-09 and IT-008 match all three adoption outcomes; Build gate exits 0. |
| T3 | PASS | README keeps activation explicit, resource-scoped, and light tests concurrent. |
| T4 | PASS | Adopted agent block contains one on-demand pointer to the public contract. |

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| CTL-09 AC 1 | `parallel` installs and tracks `tools/resource_lock.py`. | `scripts/adopt.py:42-45` places the file only in `PARALLEL_PATHS`; `scripts/test_adopt.py:615-622` asserts successful apply, installed/source byte equality, `record["layer"] == "parallel"`, and `record["ownership"] == "managed"`. | PASS |
| CTL-09 AC 2 | `core` without `parallel` omits the file and manifest record. | `scripts/test_adopt.py:610-613` asserts both filesystem absence and manifest-key absence after a real core apply. | PASS |
| CTL-09 AC 3 | Dormant installation leaves consumer commands and gates unchanged. | `scripts/test_adopt.py:461-471` applies the full profile, which includes `parallel`, and asserts a consumer `package.json` test command and `bun.lock` remain byte-identical. `scripts/test_adopt.py:624-632` also asserts unchanged re-adoption and consumer-byte preservation on conflict. | PASS |

**Spec-anchored result**: 3/3 S2 criteria covered; 0 precision gaps.

## IT-008 and Public Guidance

- IT-008 is owned by the canonical adoption suite at `scripts/test_adopt.py:607-634` and registered at `scripts/test_adopt.py:1099`.
- Adoption cases increased from 64 to 65: `git show f354e72:scripts/test_adopt.py | sed -n '/^TESTS = (/,/^)/p' | rg '^    test_' | wc -l` versus the same current-tree pipeline.
- Python suite inventory stayed 18 to 18: `git ls-tree -r --name-only f354e72 -- scripts tools | rg '/test_.*\.py$' | wc -l` versus `git ls-files -- 'scripts/test_*.py' 'tools/test_*.py' | wc -l`.
- `README.md:80-105` states dormant explicit activation, project-default and machine scopes, heavy-only wrapping, and CLI help authority.
- `templates/adoption/agents/parallel.md:6-8` fires only for a declared shared resource and points to the README without copying flags or implementation details.

The pointer follows `writing-for-agents`: one trigger branch, one disclosed authority, and no duplicated CLI contract.

## R1 Remediation and Waiter Handshake

- `tools/resource_lock.py:195-196` calls `parse_args` directly. The unclaimed parse-time `KeyboardInterrupt` behavior from `b81276d` is removed.
- `tools/test_parallel_resource_lock.py:94-102` waits for and validates the immediate JSON `wait` diagnostic.
- `tools/test_parallel_resource_lock.py:175-187` sends `SIGINT` only after that readiness handshake, then proves status 130, undisturbed holder completion, later acquisition, and absence of the interrupted command's events.

Focused stability command:

```text
rtk python3 - <<'PY'
from tools.test_parallel_resource_lock import test_timeout_exit_status_recovery_and_inherited_descriptor
for iteration in range(3):
    test_timeout_exit_status_recovery_and_inherited_descriptor()
    print(f'waiter-handshake {iteration + 1}/3 passed')
PY
```

Result: exit 0; waiter handshake 3/3 passed.

The immutable fingerprints for the fixed-delay race and unclaimed parser catch each remain at one failed remediation, below the three-failure halt. This PASS is the coordinator's input for closing those open generations in `review-fingerprints.json`; closing that accounting record is not a product-code change for this Verifier.

## Build Gate

Command:

```text
npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check origin/main...HEAD
```

Result: exit 0.

- Bun: 123 passed, 0 failed, 0 skipped; 1,123 assertions across 8 files.
- Python: 18 discovered suite files completed with zero failures; the adoption suite reported 65/65 and the resource-lock suite 5/5.
- Knowledge: 0 errors, 35 existing gap warnings.
- Diff check: exit 0.

## Discrimination Sensor

Baseline real-tree porcelain: clean. Scratch worktree: detached `c29cded` under `/tmp`, removed after the runs.

Each mutation ran the S2 Full gate:

```text
rtk python3 tools/test_parallel_resource_lock.py && rtk python3 scripts/test_adopt.py
```

| Mutation | Expected detector | Result |
| --- | --- | --- |
| Remove `tools/resource_lock.py` from `PARALLEL_PATHS` | Fixed full-profile inventory/adoption boundary | KILLED, exit 1 at `test_full_profile_matches_frozen_pre_feature_inventory`. |
| Also classify `tools/resource_lock.py` as `core` | Unique layer ownership/core omission | KILLED, exit 1: `workflow path belongs to multiple layers: tools/resource_lock.py`. |
| Record managed installed files as consumer-owned | Manifest ownership and re-adoption safety | KILLED, exit 1: `consumer record must not hash installed bytes`. |

**Sensor result**: 3/3 mutants killed; 0 survived.

## Quality and Security Residual

| Check | Result |
| --- | --- |
| Fixed-layer catalog reused without a new adoption selector | PASS |
| Canonical IT-008 asserts absence, bytes, layer, ownership, re-adoption, and conflict preservation | PASS |
| Documentation keeps the CLI and implementation in one public authority | PASS |
| Unclaimed `b81276d` behavior removed | PASS |
| Waiter interruption synchronized to an observed occupied-lock state | PASS |
| Unrelated product/runtime changes | None |

Security surfaces remain S1, S6, and S11 from `.specs/features/configurable-test-lock/threat-model.md`. S2 adds no shell execution, secret storage, network, authentication, or external-provider behavior. The direct-argv and fail-closed adoption controls remain covered by the cited canonical suites. Open Critical: 0. Open High: 0. Security verdict: PASS.

## Isolation and Cleanup

- Real-tree porcelain before gate and sensor: clean.
- Scratch worktree removed; `git worktree list --porcelain` returned only the three pre-existing project worktrees.
- Two disposable pilot-residue directories created by the Build gate were moved recoverably to `/tmp/my-workflow-test-lock-s2-r2-residue.o7geHU`.
- Real-tree porcelain after cleanup was clean before this required report; afterward only `validation-s2-r2.md` is added.

## Ranked Gaps

None. CTL-09, IT-008, documentation/pointer behavior, Build gate, and discrimination sensor all pass.

## Summary

**Overall**: PASS. 3/3 S2 acceptance criteria covered, 3/3 mutants killed, waiter handshake 3/3 stable, Build gate exit 0, and zero Critical or High residuals.
