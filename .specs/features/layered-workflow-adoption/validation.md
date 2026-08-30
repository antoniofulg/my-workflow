# Layered Workflow Adoption Validation

**Date**: 2026-08-30
**Spec**: `.specs/features/layered-workflow-adoption/spec.md`
**Diff range**: `48cfd97..fc13769`
**Verifier**: independent verifier (author != verifier)
**Verdict**: PASS

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| T1 | Done | Fixed layers, manifest, plan, and status verified. |
| T2 | Done | Conflict-safe cumulative apply and managed blocks verified. |
| T3 | Done | Full Bun-native adoption and package boundary verified. |
| T4 | Done | Public layered commands and adoption guidance pass the build gate. |

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | `file:line` + assertion expression | Result |
| --- | --- | --- | --- |
| LAY-01 | Exactly four layers; `full` resolves all four. | `scripts/test_adopt.py:88-90` — `assert ...["resolved_layers"] == ["core", "parallel", "quality", "extras"]` | PASS |
| LAY-02 | Plan emits deterministic resolved layers and unique per-path actions without target mutation. | `scripts/test_adopt.py:67-80` — exact layer/action assertions plus `assert snapshot(target) == before` | PASS |
| LAY-03 | JSON mode emits one parseable stdout object and no diagnostics on stdout. | `scripts/test_adopt.py:64-66` — `assert result.stderr == ""` and `document = json.loads(result.stdout)` | PASS |
| LAY-04 | Unknown layers and invalid fixed DAG exit 2 before target access. | `scripts/test_adopt.py:101-103` and `scripts/test_adopt.py:852-866` — exit 2 and empty snapshot assertions | PASS |
| LAY-05 | Apply includes core transitively and retains the cumulative installed-layer union. | `scripts/test_adopt.py:313-325` and `scripts/test_adopt.py:752-756` — exact cumulative manifests and `core,parallel` resolution | PASS |
| LAY-06 | Successful apply records schema, ordered layers, deterministic ownership hashes, and no unsupported manifest fields. | `scripts/test_adopt.py:147-154` and `scripts/test_adopt.py:169-174` — schema/layer/hash assertions followed by clean status validation | PASS |
| LAY-07 | Clean managed bytes update; drifted or unowned differing bytes conflict with zero writes. | `scripts/test_adopt.py:827-830` and `scripts/test_adopt.py:347-362` — exact updated bytes, complete conflict set, unchanged snapshot | PASS |
| LAY-08 | Consumer instruction prose survives; only valid blocks change; skip-agents is byte-identical. | `scripts/test_adopt.py:179-196`, `scripts/test_adopt.py:201-220`, and `scripts/test_adopt.py:367-376` — prefix, block, nested-conflict, and byte identity assertions | PASS |
| LAY-09 | Symlink, non-directory, and escaping paths fail before target/external mutation. | `scripts/test_adopt.py:244-269`, `scripts/test_adopt.py:396-420`, and `scripts/test_adopt.py:761-773` — exit 2 with unchanged target/referent snapshots | PASS |
| LAY-10 | Core synchronization uses staged inputs, preserves consumer config, and publishes no partial state on sync failure. | `scripts/test_adopt.py:581-600` and `scripts/test_adopt.py:675-697` — 15 packet assertion, preserved config, and unchanged failure snapshots | PASS |
| LAY-11 | Status reports only clean, missing, modified, or retained for installed state. | `scripts/test_adopt.py:795-814` — vocabulary subset plus explicit missing/modified/retained assertions | PASS |
| LAY-12 | Clean status exits 0; drift exits 1 read-only. | `scripts/test_adopt.py:153-161` and `scripts/test_adopt.py:804-807` — exact exits/status and unchanged snapshot | PASS |
| LAY-13 | Missing or invalid manifests exit 2 without writes; fresh apply remains valid. | `scripts/test_adopt.py:118-127`, `scripts/test_adopt.py:779-790`, and `scripts/test_adopt.py:915-942` — fresh/status distinction, duplicate/non-normalized rejection, unchanged snapshots | PASS |
| LAY-14 | Full installs the frozen complete inventory, missing-only ownership, links, config, and provider packets. | `scripts/test_adopt.py:425-456`, `scripts/test_adopt.py:581-587`, and `scripts/test_adopt.py:837-847` — exact inventories, 15 packets, and consumer ownership assertions | PASS |
| LAY-15 | Dependent-layer selection installs core first. | `scripts/test_adopt.py:749-756` — exact `core,parallel` result and core guideline presence | PASS |
| LAY-16 | Staged sync succeeds before publication; packets precede a manifest published last; failures roll back. | `scripts/test_adopt.py:675-684`, `scripts/test_adopt.py:872-890`, and `scripts/test_adopt.py:895-910` — unchanged prepublication failure, final manifest event, byte-identical rollback | PASS |
| LAY-17 | Adopted knowledge runs directly with Bun; consumer package bytes remain unchanged; probe import calls Orca zero times. | `scripts/test_adopt.py:461-481` — package/lock equality, Bun exit 0, import exit 0, no call file | PASS |
| LAY-18 | Positional legacy CLI exits 2 and directs callers to subcommands. | `scripts/test_adopt.py:91-93` — `assert legacy.returncode == 2` and plan/apply guidance | PASS |

**Status**: 18/18 requirements matched their spec-defined outcomes; 0 precision gaps.

## Edge Cases

- Duplicate and whitespace layer selections normalize deterministically.
- Future, malformed, dependency-open, and oversized manifest versions fail closed; an older supported version remains readable.
- Manifest block topology permits installed AGENTS layers and only CLAUDE core.
- Nested, duplicate, incomplete, altered, CRLF, and no-final-newline instruction forms are covered.
- Status and apply do not follow target, instruction, config, destination, or manifest-path symlinks.
- Missing-only consumer files, omitted installed layers, consumer Claude pointers, and obsolete-looking consumer paths survive.
- Publication failures before the authority marker restore the previous tree and manifest.

## Discrimination Sensor

| Mutation | File:line | Fault | Covering test | Result |
| --- | --- | --- | --- | --- |
| 1 | `scripts/adopt.py:23` | Removed core dependency from parallel. | `test_dependency_selection_installs_core_transitively` | Killed: exact resolved layers assertion failed. |
| 2 | `scripts/adopt.py:133` | Disabled no-follow rejection in `_safe_path`. | `test_symlinked_local_config_is_rejected_before_read` | Killed: expected exit 2/symlink diagnostic failed. |
| 3 | `scripts/adopt.py:802` | Inverted manifest-skip publication condition. | `test_public_publication_publishes_packets_before_manifest_last` | Killed: runtime-before-manifest assertion failed. |

**Sensor depth**: lightweight, three high-risk behavior mutations in detached temporary worktrees.
**Result**: 3/3 killed; real worktree status unchanged after cleanup.

## Gate Check

- `python3 scripts/test_adopt.py` -> `ok (64 tests)`, exit 0.
- `bun install --frozen-lockfile && bun run test:all && bun run knowledge && bun pm pack --dry-run --ignore-scripts` -> exit 0; Bun 123 passed, 0 failed across 8 files; every Python suite passed; knowledge 0 errors and 34 gaps (including this new unharvested validation); pack 448 files.
- `git show 48cfd97:scripts/test_adopt.py | rg -c '^def test_'` -> 27 pre-feature adopter tests.
- `rg -c '^def test_' scripts/test_adopt.py` -> 64 current adopter tests, delta +37.
- Skipped tests: none.
- `git diff --check` -> exit 0.

## High-Risk Scratch Checks

The targeted scratch runner invoked 13 named adopter checks and reported `13/13 passed`: manifest block topology; future/old/oversized semver; complete unique plan actions with correct owning layers and no sync; no obsolete consumer deletion; managed-only Claude links; status no-follow; config symlink; nested and CRLF blocks; core Ponytail ownership; manifest-last publication; rollback; dependency closure.

The public incremental journey ran `plan core -> apply core -> apply parallel -> apply quality,extras -> status`, then Bun knowledge, fake-Orca probe import, and drifted status. It reported:

- 106 plan actions and 106 unique paths; plan snapshot byte-identical.
- 122 manifest files, four valid blocks, and layers `core,parallel,quality,extras`.
- Clean status, then drift status after a managed-byte mutation.
- Bun knowledge exit 0; probe import exit 0; zero Orca calls.
- Consumer package/lock, custom Claude pointer, and obsolete-looking consumer path byte-identical.
- Temporary journey removed; no `.tgz`; only the three expected source worktrees remain.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum standard-library implementation | PASS |
| Surgical feature scope; no arbitrary layer/plugin framework | PASS |
| Fixed catalog and strict schema avoid speculative flexibility | PASS |
| Tests map to spec requirements and named security edges | PASS |
| Spec-anchored assertions discriminate high-risk behavior | PASS |
| Guidelines followed: `TEST-CONTRACT.md`, `VERIFICATION-EVIDENCE.md`, `GATES.md` | PASS |

## Requirement Traceability Update

LAY-01 through LAY-18 moved from `In Design` to `Verified` in `spec.md`.

## Summary

**Overall**: Ready.

All 18 requirements have file:line assertion evidence. Canonical and build gates pass, all three mutants die, and the disposable existing-project journey proves incremental adoption, read-only planning/status, Bun execution, import safety, ownership preservation, and cleanup without residue.
