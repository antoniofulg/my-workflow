# Configurable Test Lock — Slice S1 Validation

**Date**: 2026-08-30
**Spec**: `.specs/features/configurable-test-lock/spec.md`
**Diff range**: `4c2ca56..767b174`
**Verifier**: independent sub-agent (author ≠ verifier)
**Verdict**: FAIL

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| T1 | ❌ Not done | Required Build gate exits 1; `tasks.md` marks it complete without current supporting evidence. |

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| CTL-01 | Linked worktrees serialize the same project resource. | `tools/test_parallel_resource_lock.py:95-100` — `assert ... == ["first-start", "first-end", "second-start", "second-end"]` | ✅ PASS |
| CTL-02 | Unrelated repositories serialize the same machine resource. | `tools/test_parallel_resource_lock.py:119-124` — `assert ... == ["first-start", "first-end", "second-start", "second-end"]` | ✅ PASS |
| CTL-03 | Different resources overlap. | `tools/test_parallel_resource_lock.py:103-110` — `assert events.index("second-start") < events.index("first-end")` | ✅ PASS |
| CTL-04 | Omitting scope uses project scope. | No invocation omits `--scope`; both helpers always add it at `tools/test_parallel_resource_lock.py:21-35`. | ❌ GAP |
| CTL-05 | Wrapper returns exact child status. | `tools/test_parallel_resource_lock.py:165` — `assert ...returncode == 17` | ✅ PASS |
| CTL-06 | Timeout returns 75 and never starts the command. | `tools/test_parallel_resource_lock.py:134-136` — `assert waiter.returncode == 75` and sentinel absence | ✅ PASS |
| CTL-07 | Abnormal wrapper exit retains the inherited lock until child exit, then recovery needs no cleanup. | `tools/test_parallel_resource_lock.py:139-147` — waiter remains alive and ordered events prove delayed acquisition | ✅ PASS |
| CTL-08 | Exact settings apply; invalid scope/resource/timeout/command fail before execution; argv is direct. | `tools/test_parallel_resource_lock.py:157-167` covers direct argv, several resource values, missing command, exit status, missing executable, and negative timeout. No invalid-scope assertion; resource rejection lacks the full contracted input set. | ❌ GAP |
| SEC-001 | Shell metacharacters remain literal argv and create no injected file. | `tools/test_parallel_resource_lock.py:155-160` — recorded argv equals literals and `injected` is absent | ✅ PASS |
| SEC-002 | Traversal, absolute path, separator, and whitespace are rejected before filesystem or command mutation. | `tools/test_parallel_resource_lock.py:161-163` checks traversal, separator, whitespace return 2; no `/tmp/x` case and no filesystem-mutation sentinel. | ❌ GAP |
| SEC-003 | Symlinked private root and lock file fail closed without touching referents. | `tools/test_parallel_resource_lock.py:197-200` and `:216-219` — return 2, empty directory/unchanged referent | ✅ PASS |
| SEC-004 | Command/environment secrets are absent from diagnostics and metadata. | `tools/test_parallel_resource_lock.py:169-187` — secret absent from stderr and required diagnostic fields present. Lock-file metadata is not inspected. | ❌ GAP |

**Status**: 8/12 requirements have complete assertion evidence; 4/12 have gaps.

## Edge Cases

- ✅ Outside Git fails before command: `tools/test_parallel_resource_lock.py:201-204` asserts status 2.
- ❌ Resource matrix is incomplete: no empty name, 65-character name, or absolute `/tmp/x`, despite `.specs/features/configurable-test-lock/tests.md:7,34`.
- ✅ Symlinked private root and lock file fail closed: `tools/test_parallel_resource_lock.py:191-219`.
- ❌ Another-user ownership rejection has no executable assertion.
- ❌ Interrupted waiter leaving the current holder undisturbed has no assertion.
- ❌ UT-002 requires an unrelated repository to derive a different project key; no assertion covers that third repository.

## Gate Check

- **Command**: `npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check origin/main...HEAD`
- **Result**: exit 1.
- **Bun**: 123 tests executed; 122 passed; 1 failed; 0 skipped; 1,122 assertions.
- **Failure**: `tools/shared/tests/qa-skills.test.ts:1115` expected the canonical Python suite inventory, but found two unregistered additions: `tools/test_parallel_resource_lock.py` and `tools/test_resource_lock.py`.
- **Python/knowledge/diff stages**: not executed because `&&` stopped at the Bun failure.
- **Inventory before feature**: 17 tracked `scripts|tools/test_*.py` candidates from `git ls-tree -r --name-only 4c2ca56 | rg '^(scripts|tools)/test_[^/]+\.py$' | wc -l`.
- **Inventory after feature**: 19 candidates from `git ls-files -- 'scripts/test_*.py' 'tools/test_*.py' | wc -l`; delta +2. Only one addition is a test suite. The public wrapper's `test_` prefix also puts it in the executable suite glob at `package.json:15`.

## Discrimination Sensor

Not run. `workflow-spec-driven/references/validate.md` requires an immediate stop when the Build gate is non-zero. Therefore the requested project-vs-machine, timeout-side-effect, and inherited-lock/argv/symlink mutants have no valid result yet.

## Security Residual

- Applied requirements: SEC-001 through SEC-004 from `.specs/features/configurable-test-lock/tests.md:29-36`.
- Threat model: `.specs/features/configurable-test-lock/threat-model.md`; this report reviews its S1, S6, and S11 controls and residuals.
- SEC-001: PASS — `tools/test_parallel_resource_lock.py:155-160`.
- SEC-002: FAIL (coverage incomplete) — `tools/test_parallel_resource_lock.py:161-163`.
- SEC-003: PASS — `tools/test_parallel_resource_lock.py:197-200,216-219`.
- SEC-004: FAIL (metadata assertion absent) — `tools/test_parallel_resource_lock.py:169-187`.
- Open Critical: 0.
- Open High: 0.
- Verdict: FAIL due evidence gaps; no Critical/High implementation vulnerability established.

## Ranked Gaps / Fix Tasks

1. **Blocker — Build gate is red.** Resolve the collision between public `tools/test_resource_lock.py` and the repository's `tools/test_*.py` suite discovery, register the actual contract suite in the canonical inventory, then rerun the full Build gate.
2. **Major — CTL-04 has zero evidence.** Add an invocation that truly omits `--scope` and proves project-scoped linked-worktree serialization.
3. **Major — CTL-08 / SEC-002 input contract is incomplete.** Assert invalid scope, empty resource, 65-character resource, and `/tmp/x`, with sentinels proving neither command nor filesystem mutation occurs.
4. **Major — SEC-004 checks diagnostics only.** Read holder metadata during contention and prove the argv/environment sentinel is absent there too.
5. **Major — listed lifecycle edges lack evidence.** Assert waiter interruption does not release/disturb the holder and another-user lock-root ownership fails closed; cover UT-002's unrelated project namespace discrimination.

## Isolation

- Real-tree porcelain before verification: empty.
- No scratch mutation was created because the gate failed before the sensor.
- Real-tree porcelain after verification contains only this required report: `.specs/features/configurable-test-lock/validation-s1.md`.
