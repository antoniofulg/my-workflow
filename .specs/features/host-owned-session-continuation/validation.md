# Host-Owned Session Continuation Validation

**Date**: 2026-08-25
**Spec**: `.specs/features/host-owned-session-continuation/spec.md`
**Diff range**: `1451afa960c65c120035a201210b95664b0d8c52..045acc2d87e7419c1f9a5e2a6c03b728f4c1536c`
**Verifier**: independent technical verifier; author ≠ verifier; no Implementer transcript or operator handoff loaded

## Verdict

**Verdict**: PASS

Technical verification passes 16/17 acceptance criteria. HSC-10/QA-001 remains explicitly
deferred to the separate fresh `qa-plan` and `qa-execute` packets required by the feature
protocol. This packet did not create or execute the dated v0.6.0 QA charter/report.

## Task Completion

| Task | Status | Evidence |
| --- | --- | --- |
| T1 | ✅ Done | `.specs/features/host-owned-session-continuation/tasks.md:45-69`; decision-index test and check passed |
| T2 | ✅ Done | `.specs/features/host-owned-session-continuation/tasks.md:71-95`; deleted-path/package contracts passed |
| T3 | ✅ Done | `.specs/features/host-owned-session-continuation/tasks.md:97-121`; 19 registered adoption checks passed |
| T4 | ✅ Done | `.specs/features/host-owned-session-continuation/tasks.md:123-147`; host/reviewer contracts passed |
| T5 | ✅ Technical phase done | `.specs/features/host-owned-session-continuation/tasks.md:149-173`; current scenarios remain `untested` for fresh QA |
| T6 | ✅ Done | `.specs/features/host-owned-session-continuation/tasks.md:175-199`; release, package, history, and scan contracts passed |

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion/evidence | Result |
| --- | --- | --- | --- |
| HSC-01: deleted active paths absent | No implementation, test, guide, active scenario, or obsolete feature tree at named paths | `tools/shared/tests/qa-skills.test.ts:73-102` asserts each deleted path and repository listing are absent | ✅ PASS |
| HSC-02: clean adoption has no removed subsystem | Disposable clean adoption contains no config, database, marker, source line, hook, payload, script, guide, scenario, or feature test | `scripts/test_adopt.py:245-298` checks disposable project paths, source line, and project hook; adoption gate passed | ✅ PASS |
| HSC-03: repeated adoption is idempotent and host-neutral | Second adoption leaves managed output stable and shell, hook, and host sentinels byte-identical | `scripts/test_adopt.py:300-310` compares second snapshot, project hook, and host snapshot; adoption gate passed | ✅ PASS |
| HSC-04: package has no removed artifact | Local package manifest contains zero removed integration paths | `tools/shared/tests/workflow-config.test.ts:70-103` filters dry-run paths; `npm pack --dry-run --json` reported `my-workflow@0.6.0`, `entryCount=289`, removed paths `[]` | ✅ PASS |
| HSC-05: current host-owned rule | README and workflow index contain the exact host-owned continuation rule | `README.md:222-223`, `docs/workflow/README.md:9-10`, and `tools/shared/tests/qa-skills.test.ts:105-119` assert normalized rule | ✅ PASS |
| HSC-06: no current removed-integration instructions | No current instruction to install, enable, source, disable, re-enable, purge, isolate, detect, test, or use removed integration | `tools/shared/tests/qa-skills.test.ts:130-143` rejects removed lifecycle phrases in current public/reviewer surfaces; final tracked scan had 29 matches, all allowlisted | ✅ PASS |
| HSC-07: fresh independent reviewer packets | Verifier and Deep Reviewer packets exclude Implementer transcript/operator handoff and use spec, diff, tests, assigned evidence | `docs/guidelines/REVIEW-ROUNDS.md:75-80`; packet assertions `tools/shared/tests/qa-skills.test.ts:105-128`; all six provider templates matched | ✅ PASS |
| HSC-08: host-neutral generic guidance | Current generic guidance contains no Orca dependency or command | `tools/shared/tests/qa-skills.test.ts:140-143` rejects Orca in current surfaces; Orca appears only in AD-011 rationale at `.specs/STATE.md:154-156` | ✅ PASS |
| HSC-09: current QA has no active removed promise | Current QA profile, journey, and scenarios contain no active removed-integration promise | `tools/shared/tests/qa-skills.test.ts:223-244`; current scenarios are `untested` at `docs/qa/scenarios/ADP-adopt-workflow-safely.md:9` and `docs/qa/scenarios/REL-report-current-workflow-release.md:9`; removed WFL scenario absent | ✅ PASS |
| HSC-10: v0.6.0 QA charter/report | Fresh QA Plan and Execute create dated charter/report covering documentation, adoption, package, parity, and allowlist observables | Fresh QA packets were not run in technical phase; no technical evidence claimed | ⏭️ DEFERRED |
| HSC-11: immutable historical evidence | Every protected v0.5.0 historical file remains byte-for-byte equal | `tools/shared/tests/qa-skills.test.ts:1001-1057`; independent comparison: 65 protected files, 0 byte changes, 0 missing; v0.4.0 and v0.5.0 changelog sections equal | ✅ PASS |
| HSC-12: explicit final reference allowlist | Every remaining removed-integration match belongs to historical changelog, historical QA evidence, or v0.6.0 removal note | `tools/shared/tests/qa-skills.test.ts:146-220`; independent scan: 29 matches = 20 historical QA evidence, 7 v0.6 removal note, 2 historical changelog, 0 unexpected | ✅ PASS |
| HSC-13: version parity | Package, lockfile, current release scenario, and release-version assertions equal `0.6.0` | `tools/shared/tests/qa-skills.test.ts:969-999`, `tools/shared/tests/deep-review-installation.test.ts:70-72`; package, lock root, lock package, scenario, and assertions all matched | ✅ PASS |
| HSC-14: v0.6.0 changelog contract | Entry records removal, host responsibility, durable semantic context, and adoption external-state rule | `CHANGELOG.md:5-19`; exact contract assertions `tools/shared/tests/qa-skills.test.ts:993-998` passed | ✅ PASS |
| HSC-15: migration guidance | Note links tagged v0.5.0 lifecycle guide and does not invent or execute cleanup commands | `CHANGELOG.md:14-19`; tagged-guide assertions `tools/shared/tests/qa-skills.test.ts:997-998` passed; no cleanup command executed | ✅ PASS |
| HSC-16: AD-011 ownership decision | AD-011 supersedes AD-008, names Orca only as rationale, and sets host-neutral boundary | `.specs/STATE.md:99-118`, `.specs/STATE.md:150-162`, `.specs/AD-INDEX.md:16-19`; `python3 tools/test_ad_index.py` and index check passed | ✅ PASS |
| HSC-17: local-only preparation | Feature performs no tag, push, PR, merge, publication, release, deploy, or operator-machine mutation | `package.json:3-4` remains private; feature branch has no tag at HEAD; dry-run package only; adoption uses disposable targets (`scripts/test_adopt.py:245-313`); no remote mutation command executed | ✅ PASS |

**Spec-anchored result**: 16/17 criteria matched exact outcomes; HSC-10 is a deliberate QA-phase
handoff, not a technical failure.

## Test-Contract Cases

| Case | Evidence | Result |
| --- | --- | --- |
| CT-001 | `tools/shared/tests/qa-skills.test.ts:146-220`; allowlist scan | ✅ PASS |
| CT-002 | `tools/shared/tests/qa-skills.test.ts:105-143`; targeted contract | ✅ PASS |
| CT-003 | `tools/shared/tests/qa-skills.test.ts:969-999`; parity contract | ✅ PASS |
| CT-004 | `tools/shared/tests/qa-skills.test.ts:1001-1057`; 65-file byte comparison | ✅ PASS |
| ADP-001 | `scripts/test_adopt.py:245-298`; clean adoption | ✅ PASS |
| ADP-002 | `scripts/test_adopt.py:300-310`; repeat adoption and sentinels | ✅ PASS |
| REL-001 | `tools/shared/tests/workflow-config.test.ts:70-103`; package dry-run | ✅ PASS |
| QA-001 | `.specs/features/host-owned-session-continuation/tests.md:24`; fresh QA packets not run | ⏭️ DEFERRED |

## Discrimination Sensor

Sensor used three temporary detached worktrees, never `git stash`, and deleted each scratch after
the test. Real-tree `git status --porcelain=v1` was empty before and after sensor cleanup.

| Mutation | Scratch fault | Test result | Killed? |
| --- | --- | --- | --- |
| 1 | Made `scripts/adopt.py` write `scripts/ai-memory.zsh` into every adopted target | `python3 scripts/test_adopt.py` failed at `scripts/test_adopt.py:291` with `AssertionError: scripts/ai-memory.zsh` | ✅ Killed |
| 2 | Removed the host feature design path from the explicit reference allowlist | Targeted HSC contract failed with one test failed and three passed | ✅ Killed |
| 3 | Removed `Assigned evidence` from Codex Verifier packet | Targeted HSC contract failed with one test failed and three passed | ✅ Killed |

**Sensor depth**: lightweight, 3 targeted behavior-level mutations.  **Result**: 3/3 killed.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum/surgical change | ✅ Requested removal, host-neutral contracts, QA reset, release metadata, tests, and evidence only |
| No replacement runtime or compatibility path | ✅ |
| Adoption isolation and host boundary | ✅ Disposable project/host fixtures; no operator path touched |
| Historical bytes protected | ✅ Exact per-file comparison passed |
| Test integrity | ✅ No test weakened or deleted to make a gate pass; baseline 108 → current 113 |
| Reviewer independence | ✅ Fresh Verifier and Deep Reviewer packets across all provider templates |
| Documented guidelines | ✅ `docs/guidelines/GATES.md`, `TEST-CONTRACT.md`, `REVIEW-ROUNDS.md`, `QA-SCENARIOS.md`, and `VERIFICATION-EVIDENCE.md` applied |

## Gate Check

| Command | Exit/result |
| --- | --- |
| `python3 scripts/test_adopt.py` | 0; 19 registered checks, 0 failed, final `ok` |
| `python3 tools/test_workflow_config.py` | 0; 37 passed, 0 failed |
| `npm test` | 0; 7 files passed, 113 tests passed, 0 failed |
| `python3 tools/test_ad_index.py` | 0; `ok` |
| `python3 tools/ad-index.py --check` | 0; `AD-INDEX.md up to date` |
| `python3 .agents/skills/tlc-spec-driven/scripts/validate_spec.py host-owned-session-continuation` | 0 errors, 0 warnings |
| `python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py host-owned-session-continuation` | 0 errors, 1 expected T1 `Tests: none` warning; matrix marks decision/metadata layer as none |
| `git diff --check 1451afa960c65c120035a201210b95664b0d8..045acc2d87e7419c1f9a5e2a6c03b728f4c1536c` | 0; no output |
| `npx vitest run tools/shared/tests/qa-skills.test.ts -t 'host-owned session continuation removal contract'` | 0; 4 passed, 24 selector-skipped |
| `npm pack --dry-run --json` | 0; `my-workflow@0.6.0`, 289 package entries, removed paths `[]` |
| Full Build gate: `python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py && npm test && python3 tools/ad-index.py --check && git diff --check ...` | 0; all component gates passed |

### Test-count integrity

The same Vitest command on isolated pre-feature commit `1451afa960c65c120035a201210b95664b0d8`
passed 7 files and 108 tests. Current HEAD passed 7 files and 113 tests: delta `+5` tests.

## Local-Only Evidence

- Current branch is `feat/host-owned-session-continuation` at `045acc2`; no tag points at this
  feature HEAD.
- Local repository already contains a separate `v0.6.0` ref at `22ae66c2` on `origin/main`; this
  verifier did not create or move it, and it is not the feature branch's release tag.
- No push, pull request, merge, publication, release, deploy, operator-shell, hook, database,
  credential, or host-setting mutation command was run. Package check used `--dry-run` only.

## QA Handoff

Technical packet closes with HSC-10/QA-001 pending. Fresh `qa-plan` and `qa-execute` packets must
create the dated v0.6.0 charter and execution report, walk the declared CLI/manual adapter, and
update the two current `untested` scenario rows only after independent evidence survives reload.

## Lessons

No lesson recorded: no acceptance criterion failed, no mutant survived, no spec-precision gap or
SPEC_DEVIATION was found, and all technical gates passed. HSC-10/QA-001 is an explicit phase
handoff, not a verification failure.
