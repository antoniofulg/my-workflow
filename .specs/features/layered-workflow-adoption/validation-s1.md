# Layered Workflow Adoption — S1 Validation

**Date**: 2026-08-30
**Spec**: `.specs/features/layered-workflow-adoption/spec.md`
**Diff range**: `ddd5a3c..71175b8`
**Verifier**: independent sub-agent (author != verifier)
**Verdict**: PASS

---

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| T1 | PASS | Fixed catalog, deterministic plan, strict manifest, and status verified. |
| T2 | PASS | Additive apply, ownership, blocks, preflight, rollback, and idempotence verified. |
| T3 | PASS | Frozen complete inventory, Bun boundary, packet sync, and manifest-last publication verified. |
| T4 | PASS | Active docs expose only the layered subcommand contract. |

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| LAY-01 | Exactly `core`, `parallel`, `quality`, `extras`; `full` resolves all four. | `scripts/test_adopt.py:63-70` asserts normalized exact layers/action; `scripts/test_adopt.py:79-81` asserts full's exact four-layer list. | PASS |
| LAY-02 | Plan returns deterministic layers/actions without target mutation. | `scripts/test_adopt.py:62-71` asserts exact JSON fields/action and byte-identical snapshot. | PASS |
| LAY-03 | JSON mode emits one parseable object on stdout and diagnostics only on stderr. | `scripts/test_adopt.py:64-66` asserts exit 0, empty stderr, object-prefixed stdout, and full JSON parse. | PASS |
| LAY-04 | Unknown layers and invalid fixed DAG exit 2 before target access. | `scripts/test_adopt.py:92-94` asserts unknown-layer exit 2 with empty target; `scripts/test_adopt.py:672-686` corrupts the DAG and asserts controlled exit 2, diagnostic, and empty target. | PASS |
| LAY-05 | Apply includes core transitively and retains cumulative installed layers. | `scripts/test_adopt.py:169-180` asserts cumulative union, omission retention, idempotence, and installed probe bytes; `scripts/test_adopt.py:569-576` asserts `parallel` resolves `core,parallel` and installs a core path. | PASS |
| LAY-06 | Manifest records schema/version/layers and exact SHA ownership; clean managed bytes update. | `scripts/test_adopt.py:112-117` asserts schema/layers/hash fields; `scripts/test_adopt.py:131-139` asserts exact SHA-256 values; `scripts/test_adopt.py:639-650` asserts source-byte update publication. | PASS |
| LAY-07 | Managed drift and unowned differing destinations report every conflict and write nothing. | `scripts/test_adopt.py:188-200` asserts both exact conflict paths, exit 1, and unchanged full snapshot. | PASS |
| LAY-08 | Consumer AGENTS/CLAUDE prose remains byte-identical outside managed blocks. | `scripts/test_adopt.py:147-161` asserts both consumer prefixes and both managed records. | PASS |
| LAY-09 | `--skip-agents` leaves both instruction files byte-identical. | `scripts/test_adopt.py:208-214` asserts both byte sets unchanged and no block ownership. | PASS |
| LAY-10 | Symlink/non-directory/escaping destinations and sync failures precede target/external mutation. | `scripts/test_adopt.py:234-245`, `scripts/test_adopt.py:480-517`, and `scripts/test_adopt.py:581-593` assert managed/generated/root safety with unchanged target and referent. | PASS |
| LAY-11 | Status reports installed layers and only clean/missing/modified/retained states. | `scripts/test_adopt.py:618-634` asserts exact state vocabulary and observes all four states. | PASS |
| LAY-12 | Status exits 0 clean and 1 on missing/modified drift, without writes. | `scripts/test_adopt.py:118-126` asserts clean 0 and modified 1 with unchanged snapshot; `scripts/test_adopt.py:623-627` asserts missing 1, empty stderr, and unchanged snapshot. | PASS |
| LAY-13 | Missing/invalid manifest state exits 2; duplicate, non-canonical, and escaping paths cannot mutate. | `scripts/test_adopt.py:97-104` asserts escaping/unknown manifest rejection; `scripts/test_adopt.py:599-610` asserts exact duplicate-key rejection for status/apply; `scripts/test_adopt.py:738-749` asserts non-canonical aliases reject for both commands without writes. A disposable missing-manifest status scratch asserted exit 2. | PASS |
| LAY-14 | Full retains frozen complete capabilities, missing-only ownership, and packet synchronization. | `scripts/test_adopt.py:270-282` asserts exact frozen inventory; `scripts/test_adopt.py:407-413` asserts 15 packets; `scripts/test_adopt.py:657-667` asserts consumer ownership without installed hashing. | PASS |
| LAY-15 | Dependent selection installs core before dependent paths. | `scripts/test_adopt.py:569-576` asserts exact closure and installed core path; the dependency mutant was killed. | PASS |
| LAY-16 | Sync sees fully staged inputs; all files/packets/helpers precede the manifest, published last; helper failure restores prior bytes. | `scripts/test_adopt.py:692-713` asserts packet writes and all instrumented helpers precede manifest; `scripts/test_adopt.py:718-733` asserts failure rollback. Independent live wrappers observed 104 events with manifest final and byte-identical rollback for all three cleanup/link helpers. | PASS |
| LAY-17 | Adopted knowledge runs under Bun without product package mutation or import-time Orca effects. | `scripts/test_adopt.py:290-307` asserts package/lock bytes, Bun exit 0, probe import exit 0, and zero Orca calls. | PASS |
| LAY-18 | Positional legacy invocation exits 2 with new-command guidance. | `scripts/test_adopt.py:82-84` asserts exit 2 and both `plan`/`apply` guidance. | PASS |

**Status**: 18/18 requirements match spec-defined outcomes.

## Required Behavior Sensors

| Sensor | Exact observed result | Result |
| --- | --- | --- |
| Exact duplicate JSON key | status/apply exit 2; duplicate diagnostic; snapshot unchanged | PASS |
| Non-canonical and escaping manifest paths | status/apply exit 2; normalized/unsafe diagnostic; snapshot unchanged | PASS |
| Dependency closure | parallel resolves `core,parallel`; core file installed | PASS |
| Root symlink | plan/apply/status exit 2; external referent unchanged | PASS |
| Managed block drift | apply exits 1; `AGENTS.md:core` conflict; snapshot unchanged | PASS |
| Missing managed status | status exits 1; `missing` action; snapshot unchanged | PASS |
| Invalid fixed DAG | controlled exit 2; diagnostic; target remains empty | PASS |
| Complete live publication | 104 live helper/write events; manifest was final | PASS |
| Cleanup/link rollback | obsolete cleanup, legacy cleanup, and Claude-link injected partial mutations each restored target and prior manifest byte-identically | PASS |

The prior normalized-path coverage signal is remediated: removing canonical-path rejection now fails `test_distinct_manifest_keys_with_same_normalized_path_are_rejected`.

## Discrimination Sensor

Mutations ran only in detached temporary worktree `/tmp/layered-adopt-sensor.R2sal1`; it was removed. Real-checkout porcelain matched before and after.

| Mutation | File:line | Result |
| --- | --- | --- |
| Remove canonical-path rejection | `scripts/adopt.py:128-129` | KILLED by `test_distinct_manifest_keys_with_same_normalized_path_are_rejected` |
| Publish manifest before cleanup/link helpers | `scripts/adopt.py:692-695` | KILLED by `test_public_publication_publishes_packets_before_manifest_last` |
| Return 0 for all status outcomes | `scripts/adopt.py:652` | KILLED by `test_status_uses_only_public_state_vocabulary` |

**Sensor depth**: lightweight, three highest-risk behavior mutations.
**Result**: 3/3 killed — PASS.

## Test Integrity

- `git show ddd5a3c:scripts/test_adopt.py | rg -c '^def test_'` -> 27 pre-feature named tests.
- `rg -c '^def test_' scripts/test_adopt.py` -> 52 current named tests.
- Delta: +25 tests; no existing named test was removed.
- `python3 scripts/test_adopt.py` -> `ok (52 tests)`.
- Build gate `bun test` -> 123 passed, 0 failed, 1120 assertions across 8 files.

## Gate Evidence

- `rtk bun install --frozen-lockfile && rtk bun run test:all && rtk bun run knowledge && rtk bun pm pack --dry-run --ignore-scripts` -> exit 0; install unchanged; Bun 123/123; all tracked Python suites green; adopter 52/52; knowledge 0 errors/33 warnings; pack 447 files/3.58 MB.
- Disposable full adoption -> plan/apply/status/knowledge/probe-import all exit 0; status clean with 4 layers and 128 actions; residue 0; Orca calls 0; `package.json` and `bun.lock` byte-identical.
- `rtk python3 .agents/skills/workflow-spec-driven/scripts/validate_spec.py .specs/features/layered-workflow-adoption/spec.md` -> 0 errors, 0 warnings.
- `rtk python3 .agents/skills/workflow-spec-driven/scripts/validate_tasks.py .specs/features/layered-workflow-adoption/tasks.md` -> 0 errors, 0 warnings.
- `rtk proxy find . -maxdepth 1 -name '*.tgz' -print` -> no package residue.
- `rtk git diff --check` -> exit 0.

## Edge Cases

- PASS — duplicate/whitespace layer selection normalizes deterministically.
- PASS — omitted installed layers remain and reapply is byte-stable.
- PASS — exact duplicate, non-canonical, escaping, root-symlink, and managed-block inputs fail closed.
- PASS — missing-only consumer content remains un-hashed and retained.
- PASS — missing/modified status is read-only and exits 1.
- PASS — invalid fixed DAG is a controlled exit-2 error.
- PASS — manifest is the final live publication event; every cleanup/link failure restores prior bytes.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum code / no speculative framework | PASS |
| Surgical public surface | PASS |
| Fail-closed filesystem containment | PASS |
| Spec-anchored exact outcomes | PASS |
| Existing test integrity | PASS |
| No unclaimed feature tests | PASS |
| Guidelines: feature `tests.md`; verifier `validate.md` | PASS |

## Requirement Traceability Update

CP-S1 PASS at `71175b8`. LAY-01..LAY-18 have evidence. Stable fingerprint `LAY-13-normalized-duplicate-mutant+LAY-16-manifest-not-final` is closed: both mutants are killed and complete live publication ends with the manifest. S2 may proceed.

## Summary

**Overall**: PASS — S1 ready for S2.

**Spec-anchored check**: 18/18 matched.
**Sensor**: 3/3 mutations killed; 9/9 required behavior sensors passed.
**Gate**: full build/package/knowledge/status/residue validation passed.

No product fixes were made in this verifier session.
