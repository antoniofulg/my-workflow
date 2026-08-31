# Configurable Test Lock — Slice S2 Validation

**Date**: 2026-08-30
**Spec**: `.specs/features/configurable-test-lock/spec.md`
**Diff range**: `f354e72..d385dcd`
**Verifier**: fresh independent Technical Verifier (author != verifier)
**Verdict**: FAIL

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| T2 | ❌ Not done | CTL-09 and IT-008 have complete assertion evidence, but the mandatory Build gate exits 1. |
| T3 | ✅ Contract match | README documents explicit heavy-only activation plus project and machine scopes. |
| T4 | ✅ Contract match | Adopted agent block contains one on-demand pointer without repeating CLI or implementation details. |

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| CTL-09 / adoption AC 1 | Applying `parallel` installs `tools/resource_lock.py` and tracks it in the manifest. | `scripts/test_adopt.py:615-622` — `assert applied.returncode == 0`, installed bytes equal source bytes, and `record["layer"] == "parallel" and record["ownership"] == "managed"`. | ✅ PASS |
| CTL-09 / adoption AC 2 | Applying `core` without `parallel` omits the tool and its manifest record. | `scripts/test_adopt.py:610-613` — file absence and manifest-key absence are both asserted after a real core apply. | ✅ PASS |
| CTL-09 / adoption AC 3 | Dormant installation changes no consumer command or gate. | `scripts/adopt.py:42-45` only adds the source path to `PARALLEL_PATHS`; `scripts/test_adopt.py:624-632` proves unchanged re-adoption is byte-identical and a consumer-modified wrapper conflicts without overwrite. No consumer command file is in the S2 diff. | ✅ PASS |

**Status**: 3/3 adoption criteria match the exact spec outcome; 0 precision gaps.

## IT-008 and Adoption Safety

- Core omission: `scripts/test_adopt.py:610-613`.
- Parallel install and byte identity: `scripts/test_adopt.py:615-618`.
- Manifest ownership: `scripts/test_adopt.py:619-622`.
- Safe re-adoption: `scripts/test_adopt.py:624-626`.
- Conflict detection and consumer-byte preservation: `scripts/test_adopt.py:628-632`.
- Canonical suite registration: `scripts/test_adopt.py:1099`.

IT-008 is non-hollow and lives in the canonical adoption suite. The feature adds one adoption case:
64 before and 65 after, counted with `git show f354e72:scripts/test_adopt.py | sed -n '/^TESTS = (/,/^)/p' | rg '^    test_' | wc -l` and the same command against the working file. Python suite inventory remains 18 before and 18 after.

## Public Guidance and Agent Pointer

- `README.md:80-85` says installation is dormant and explicit, names browser/database/container contention, and leaves unit/light gates concurrent.
- `README.md:87-101` gives separate project-default and explicit machine-scope examples.
- `README.md:103-105` keeps flag/default/result-code authority in CLI help.
- `templates/adoption/agents/parallel.md:6-8` fires only when a gate declares a shared resource, points to the public contract, and repeats neither flags nor lock internals.

The pointer follows `writing-for-agents`: one branch trigger, progressive disclosure, one source of truth.

## Intermediate Commit `b81276d`

**Verdict**: scope creep plus coverage gap.

- The spec edge says an interrupted waiting process exits without disturbing the holder; it does not require status `130` during CLI parsing.
- `tools/resource_lock.py:195-199` adds a `KeyboardInterrupt` catch only around `parse_args`.
- `tools/test_parallel_resource_lock.py:165-175` sends `SIGINT` after a fixed 150 ms and asserts status `130`, holder completion, and later acquisition. It never proves the signal occurred during parsing and therefore does not cover the new branch.
- The fixed delay is racy. Across the mandatory Build gate, a focused rerun, and one diagnostic reproduction, the waiter failed the same exact assertion three times. The diagnostic reproduction observed `waiter_returncode: 1`, `holder_returncode: 0`, and only `holder-start`, `holder-end`; the signal arrived before the protected runtime path.
- Correct verification needs a readiness observation (for example the immediate `wait` diagnostic) before sending `SIGINT`. The current exact-status assertion is not deterministic evidence for the spec edge.

## Build Gate

**Command**:

```text
npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check origin/main...HEAD
```

**Result**: exit `1`.

- Bun: 123 passed, 0 failed, 0 skipped; 1,123 assertions across 8 files.
- Canonical adoption suite: `ok (65 tests)` before the later failure.
- Python discovery reached `tools/test_parallel_resource_lock.py` and failed at `tools/test_parallel_resource_lock.py:171`: `assert waiter.wait(timeout=3) == 130`.
- `knowledge` and the gate's diff-check stage did not run because `&&` stopped after `test:all`.
- A separate read-only `git diff --check f354e72..d385dcd` exited zero; it does not replace the skipped gate stages.
- Focused reproduction: `rtk python3 tools/test_parallel_resource_lock.py` exited 1 at the same assertion.
- Third diagnostic reproduction observed the same behavior and then verification stopped per the three-failure rule.

## Discrimination Sensor

Not run. `workflow-spec-driven/references/validate.md` requires an immediate stop when the Build gate is non-zero. Therefore the requested adoption inventory/manifest mutants have no valid result on this checkpoint.

## Code Quality and Security Residual

| Check | Result |
| --- | --- |
| CTL-09 uses the existing fixed-layer inventory and manifest contract | ✅ |
| IT-008 maps to the adoption AC and canonical suite | ✅ |
| README keeps activation explicit and heavy-only | ✅ |
| Agent pointer is on-demand and non-duplicative | ✅ |
| No unrelated runtime behavior in S2 | ❌ `b81276d` |
| Mandatory gate green | ❌ |
| Discrimination sensor complete | ❌ blocked by gate |

The adoption diff preserves fail-closed conflict handling and adds no new secret, shell, or external-provider surface. The interrupt commit touches the S11 process boundary but introduces no established Critical or High vulnerability. Open Critical: 0. Open High: 0.

## Ranked Gaps / Fix Tasks

1. **Blocker — mandatory Build gate is red.** Replace the fixed-delay interrupt race with a deterministic readiness observation before `SIGINT`, then rerun the focused suite and complete Build gate.
2. **Major — `b81276d` is unclaimed and uncovered.** The parse-time catch is neither required by the spec nor discriminated by the test. Remove it unless a precise contract is added; verification should target the existing waiter-interruption edge after acquisition readiness.
3. **Blocked evidence — no discrimination sensor.** After the gate is green, kill 1-3 adoption inventory/manifest mutants and confirm the real-tree porcelain baseline.

## Isolation

- Real-tree porcelain before verification: clean.
- No mutation scratch worktree was created because the Build gate failed.
- Diagnostic `TemporaryDirectory` fixtures cleaned themselves; `git worktree list --porcelain` shows only the three pre-existing project worktrees.
- Real-tree porcelain remained clean before this required report; afterward only `validation-s2.md` is added.

## Summary

**Overall**: FAIL.

**Spec-anchored check**: 3/3 S2 adoption criteria matched; IT-008 complete.
**Gate**: 123 Bun tests passed, but Python resource-lock lifecycle failed; exit 1.
**Sensor**: 0 mutations, correctly blocked by red gate.
**Next step**: route the deterministic interrupt-test fix and removal/justification of `b81276d` to an Implementer, then dispatch a fresh Technical Verifier.
