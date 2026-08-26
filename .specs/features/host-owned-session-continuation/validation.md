# Host-Owned Session Continuation Validation

**Date**: 2026-08-26
**Spec**: .specs/features/host-owned-session-continuation/spec.md
**Tasks**: .specs/features/host-owned-session-continuation/tasks.md
**Diff range**: 2ab4cec..7c6fd8a (origin/main parent through current HEAD 7c6fd8a73e1e1f47f06667b5abac2ebaef04a467)
**Merge parents**: 1a35fbe7ab0b511a4bc49fb6f0c1b542f9b25ac0, 2ab4cecc2d9daede27015c7edec543800e7bd763
**Post-verification correction**: 7c6fd8a changes only spec.md traceability HSC-10 to Verified (1 file, 1 insertion, 1 deletion); no implementation or test behavior changed
**Verifier**: fresh independent verifier; author ≠ verifier; no Implementer transcript or operator handoff loaded
**Verdict**: PASS

## Validation

Result: PASS

## Validation result

**PASS — 17/17 HSC acceptance criteria, 8/8 test-contract IDs, 3/3 sensor mutants killed, current QA rows pass, and the full build gate passes.**

The merge preserves origin/main behavior while retaining host-owned continuation. Active removed
integration paths are absent. Historical v0.5.0 evidence is byte-identical. The only real-tree
write made by this verifier is this report.

## Task completion

| Task | Status | Evidence |
| --- | --- | --- |
| T1 ownership decision | ✅ Done | tasks.md:45-69; AD-015 appended and AD-INDEX regenerated |
| T2 subsystem removal | ✅ Done | tasks.md:71-95; five active paths absent; package contract passes |
| T3 host-neutral adoption | ✅ Done | tasks.md:97-121; clean/repeated adoption and host-boundary assertions pass |
| T4 continuation/reviewer contract | ✅ Done | tasks.md:123-147; exact host rule and fresh packet contract pass |
| T5 current QA promises | ✅ Done | tasks.md:149-173; current QA charter/report and scenario evidence present |
| T6 v0.6.0 release contract | ✅ Done | tasks.md:175-197; version, migration, allowlist, and history contracts pass |

All task records are complete and all Done-when checkboxes are checked. validate_tasks.py
reports zero errors and one expected T1 no-test warning.

## Spec-anchored acceptance criteria

| Criterion | Spec-defined outcome | File:line + assertion/evidence | Result |
| --- | --- | --- | --- |
| HSC-01 | Deleted implementation, test, guide, active scenario, and obsolete feature tree are absent | tools/shared/tests/qa-skills.test.ts:85 — expect(existsSync(...)).toBe(false); :102 — removed package paths toEqual([]) | ✅ PASS |
| HSC-02 | Clean disposable adoption contains no removed artifacts, source marker, hook, or payload | scripts/test_adopt.py:291 — every forbidden path assert not ...exists(); :298 — source marker absent | ✅ PASS |
| HSC-03 | Re-adoption is stable and project/host shell, hook, and settings sentinels stay byte-identical | scripts/test_adopt.py:301 — project snapshot equals first; :302 — project hook unchanged; :310 — host snapshot equals baseline | ✅ PASS |
| HSC-04 | Locally generated package manifest contains no removed integration artifact | tools/shared/tests/workflow-config.test.ts:102 — removed package paths toEqual([]); independent pack reload: active removed paths [] | ✅ PASS |
| HSC-05 | README and workflow index contain the exact host-owned continuation rule | tools/shared/tests/qa-skills.test.ts:115-116 — README/workflow toContain(hostRule); README.md:222-223; docs/workflow/README.md:9-10 | ✅ PASS |
| HSC-06 | Current surfaces contain no instruction to operate the removed integration | tools/shared/tests/qa-skills.test.ts:141 — lifecycle phrase set toBe(false); current active scan has no non-allowlisted matches | ✅ PASS |
| HSC-07 | Verifier/Deep Reviewer receive fresh packets, exclude Implementer/operator context, and use spec/diff/tests/assigned evidence | tools/shared/tests/qa-skills.test.ts:122-126 — all packet terms asserted; docs/guidelines/REVIEW-ROUNDS.md:77-79 — fresh packet rule | ✅ PASS |
| HSC-08 | Generic guidance has no Orca dependency/command; Orca appears only as v0.6 decision rationale | tools/shared/tests/qa-skills.test.ts:142 — current generic surfaces not.toMatch(/\bOrca\b/); .specs/STATE.md:228-230 — AD-015 Reason names Orca | ✅ PASS |
| HSC-09 | Current QA profile/journey/scenarios contain no active removed promise | tools/shared/tests/qa-skills.test.ts:239-240 — pass requires v0.6 evidence and last_report; scenario frontmatter ADP...:9-15, REL...:9-15 is pass with current report | ✅ PASS |
| HSC-10 | Dated v0.6.0 QA charter/report cover docs, adoption, package, parity, history, and allowlist | docs/qa/charters/CH-review-release-0-6-0-2026-08-25.md:34-40 — expected observables; docs/qa/reports/2026-08-25-release-0-6-0.md:18-21 — all four HSC rows pass; spec.md:129 — traceability Verified | ✅ PASS |
| HSC-11 | Protected v0.5.0 evidence and prior changelog sections remain byte-identical | tools/shared/tests/qa-skills.test.ts:1076 — each protected file equals tagged; :1088-1090 — v0.4.0 section equality; independent result 65/65, 0 differences | ✅ PASS |
| HSC-12 | Every remaining removed-integration match belongs to explicit historical/removal-note allowlist | tools/shared/tests/qa-skills.test.ts:214-221 — unexpected matches toEqual([]) and every match classified; independent result 60/60 classified | ✅ PASS |
| HSC-13 | Package, lockfile, current release scenario, and release assertions equal 0.6.0 | tools/shared/tests/qa-skills.test.ts:1017-1023 — exact 0.6.0 assertions; package.json:3; package-lock.json:3,9; release scenario :7 | ✅ PASS |
| HSC-14 | Changelog records removal, host responsibility, durable semantic context, and external-state rule | tools/shared/tests/qa-skills.test.ts:1024-1027 — exact latest-release assertions; CHANGELOG.md:19-24 | ✅ PASS |
| HSC-15 | Migration note links tagged v0.5.0 guide and does not invent/execute cleanup commands | tools/shared/tests/qa-skills.test.ts:1028-1029 — exact tagged URL; CHANGELOG.md:26-31; cleanup commands executed by this verifier: 0 | ✅ PASS |
| HSC-16 | AD-015 supersedes AD-008, establishes host-neutral ownership, and uses Orca only in rationale | .specs/STATE.md:138 — AD-008 superseded; :224-236 — AD-015 decision/reason; .specs/AD-INDEX.md:17,24; index tests pass | ✅ PASS |
| HSC-17 | Preparation stays local-only: no tag, push, PR, publication, release, deploy, or operator mutation | package.json:3 — private: true; git tag --points-at HEAD empty; verifier ran no remote/release/operator command; merge is supplied input, not verifier action | ✅ PASS |

**Spec-anchored result: 17/17 exact outcomes.** No criterion has evidence-or-zero coverage.

All 17 source spec traceability rows, HSC-01 through HSC-17, now read Verified at
spec.md:120-136. The post-verification correction is metadata-only and introduces no new
behavioral surface.

## Test-contract coverage

| ID | Result | Evidence |
| --- | --- | --- |
| CT-001 | ✅ PASS | Allowlist contract: 1 passed, 27 skipped; independent scan 60 matches, 0 unexpected |
| CT-002 | ✅ PASS | Fresh-packet/removal contract: 4 passed, 24 skipped |
| CT-003 | ✅ PASS | Release parity contract: 1 passed, 27 skipped; all authorities 0.6.0 |
| CT-004 | ✅ PASS | Historical contract: 1 passed, 27 skipped; 65 protected files, 0 differences |
| ADP-001 | ✅ PASS | scripts/test_adopt.py:276-298; clean fixture has no forbidden paths/markers |
| ADP-002 | ✅ PASS | scripts/test_adopt.py:264-310; repeat snapshot and host/project sentinels unchanged |
| REL-001 | ✅ PASS | tools/shared/tests/workflow-config.test.ts:70-103; pack has 357 entries and no active removed paths |
| QA-001 | ✅ PASS | docs/qa/reports/2026-08-25-release-0-6-0.md:18-21; all HSC QA matrix rows terminal pass |

## QA plan and execute

| Artifact | Result | Evidence |
| --- | --- | --- |
| QA Plan | ✅ PASS | docs/qa/charters/CH-review-release-0-6-0-2026-08-25.md:21-40 maps current HSC observables |
| QA Execute / QA-001 | ✅ PASS | docs/qa/reports/2026-08-25-release-0-6-0.md:14-24; no HSC row pending |
| ADP adoption journey | ✅ PASS | docs/qa/scenarios/ADP-adopt-workflow-safely.md:9-15; pass, fresh v0.6 evidence/report |
| REL release journey | ✅ PASS | docs/qa/scenarios/REL-report-current-workflow-release.md:9-15; pass, fresh v0.6 evidence/report |
| QAS packet canary | ✅ PASS | docs/qa/scenarios/QAS-discover-independent-qa-skills.md:9-15; six packet pairs and current contract evidence |

The repository has no browser, API, mobile, server, authentication, or production-health surface;
CLI/manual repository and disposable-fixture inspection is the declared reachable QA adapter.
Unrelated parallel-slice Orca/Codex lifecycle legs remain explicitly blocked-verify in origin/main
QA records; this HSC verification does not convert them to success.

## Gate evidence

Build-level command from tasks.md:

    python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py && npm test && python3 tools/ad-index.py --check && git diff --check

| Command | Result |
| --- | --- |
| python3 scripts/test_adopt.py | exit 0; 20 registered tests; 0 failed; final ok |
| python3 tools/test_workflow_config.py | exit 0; 44 passed; 0 failed |
| npm test | exit 0; 8 files passed; 115 tests passed; 0 failed |
| python3 tools/ad-index.py --check | exit 0; AD-INDEX.md up to date |
| git diff --check | exit 0; no output |
| Full Build gate above | exit 0; all five commands passed |
| python3 tools/test_ad_index.py | exit 0; ok |
| npx vitest run tools/shared/tests/qa-skills.test.ts -t 'host-owned session continuation removal contract' | exit 0; 4 passed; 24 skipped |
| npx vitest run tools/shared/tests/workflow-config.test.ts -t 'keeps local config/runtimes ignored and packages only example/templates' | exit 0; 1 passed; 4 skipped |
| npx vitest run tools/shared/tests/qa-skills.test.ts -t 'CT-003 / IT-005 / AIM-11 reports release version 0.6.0 consistently' | exit 0; 1 passed; 27 skipped |
| npx vitest run tools/shared/tests/qa-skills.test.ts -t 'CT-004 preserves v0.5.0 historical evidence and the v0.4.0 changelog section' | exit 0; 1 passed; 27 skipped |
| npx vitest run tools/shared/tests/deep-review-installation.test.ts -t 'keeps the skill, lock metadata, release version, and project discovery aligned' | exit 0; 1 passed |
| npx vitest run tools/shared/tests/qa-skills.test.ts -t 'IT-013 records the selected QA adapter and checkout-local evidence|IT-022 reconciles immutable QA charters, spec-anchored cases, and filed-issue QA' | exit 0; 2 passed; 26 skipped |
| npm pack --dry-run --json | exit 0; reloaded my-workflow@0.6.0; private package; 357 entries; active removed paths [] |
| exact protected-history comparison against v0.5.0 | 65 protected files; 0 missing; 0 byte differences; v0.4.0 and v0.5.0 changelog sections equal |
| current reference scan | 360 tracked files; 30 terms; 60 matches; 22 historical QA, 2 historical changelog, 36 v0.6 removal note; 0 unexpected |
| baseline origin/main npm test | exit 0; 8 files passed; 110 tests passed; current delta +5 tests |
| python3 /Users/antoniofulg/.agents/skills/tlc-spec-driven/scripts/validate_spec.py host-owned-session-continuation | exit 0; 0 errors, 0 warnings |
| python3 /Users/antoniofulg/.agents/skills/tlc-spec-driven/scripts/validate_tasks.py host-owned-session-continuation | exit 0; 0 errors, 1 expected T1 matrix warning |

The first baseline worktree attempt lacked a dependency link and failed only with module-resolution
errors; a clean rerun with the existing node_modules linked into the disposable worktree passed
8 files/110 tests. No real-tree file was changed by either attempt.

## Adoption, packaging, history, and locality

- Active paths scripts/ai-memory.zsh, scripts/test_ai_memory.py, docs/workflow/ai-memory.md,
  docs/qa/scenarios/WFL-ai-memory-handoff.md, and .specs/features/ai-memory-handoff/ are absent
  from disk and git ls-files.
- scripts/test_adopt.py used only disposable project/host fixtures, redirected HOME/ZDOTDIR inside
  the test, compared project/hook/host sentinels, and returned 0. It did not install external
  security skills; it only printed the separately authorized command.
- npm pack --dry-run --json contained no active removed integration path. Two historical QA path
  names containing ai-memory remain intentionally packaged as immutable evidence and are included
  in the historical allowlist below; no runtime, guide, test, active scenario, or feature-tree path
  is packaged.
- Protected-history comparison: 65 files, 0 missing, 0 byte differences. Both 0.4.0 and 0.5.0
  changelog sections equal their v0.5.0 versions.
- HEAD=7c6fd8a73e1e1f47f06667b5abac2ebaef04a467, branch
  feat/host-owned-session-continuation; no tag points at HEAD. Existing annotated v0.6.0 resolves
  to 2177564d1f16597ed566afb8f3b28f388e6aa5ce, not this branch. No fetch, push, pull request,
  publication, release, deploy, tag, or operator-state action was run by this verifier.
- Real-tree status before sensor: empty. After each scratch cleanup: empty. Final status after this
  report write has exactly one authorized path: .specs/features/host-owned-session-continuation/validation.md.

## Discrimination sensor

Sensor depth: lightweight, three behavior-level mutations in detached temporary worktrees. No stash,
remote, tag, release, publication, deploy, or operator-state action was used. Every scratch was
removed; real-tree porcelain matched the empty pre-sensor baseline. The 7c6fd8a correction is
metadata-only (spec.md HSC-10 traceability), so the prior 3/3 sensor result remains valid without
rerunning implementation mutations.

| Mutation | Scratch fault | Command/result | Killed? |
| --- | --- | --- | --- |
| S1 | Changed docs/qa/scenarios/ADP-adopt-workflow-safely.md:15 from last_report: to report: | HSC-09 targeted test; exit 1, 1 failed/27 skipped at tools/shared/tests/qa-skills.test.ts:240 | ✅ Killed |
| S2 | Added deleted scripts/ai-memory.zsh | HSC removal contract; exit 1, 1 failed/3 passed/24 skipped at tools/shared/tests/qa-skills.test.ts:85 | ✅ Killed |
| S3 | Removed Assigned evidence named by the packet. from templates/agents/codex/verifier.toml:17 | HSC removal contract; exit 1, 1 failed/3 passed/24 skipped at tools/shared/tests/qa-skills.test.ts:126 | ✅ Killed |

**Sensor result: 3/3 killed.** No surviving mutant; no fix task required.

## Final reference scan: every match classified

The scan used the 30 terms and explicit allowlist enforced by
tools/shared/tests/qa-skills.test.ts:146-221. All 60 matches are listed by path and term set;
no path outside the three categories matched.

| Classification | Path | Matched terms |
| --- | --- | --- |
| historical QA evidence | .specs/features/agent-model-routing/validation.md | ai-memory |
| historical QA evidence | .specs/features/parallel-slice-dispatch/validation.md | ai-memory, ai_memory |
| historical QA evidence | .specs/features/release-0.4.0/validation.md | ai-memory, ai_memory, memory handoff |
| historical QA evidence | docs/qa/bugs/BUG-20260824-noninteractive-codex-finalizes-open-session.md | ai-memory, finalize-session |
| historical QA evidence | docs/qa/bugs/BUG-20260824-release-overstates-lifecycle-qa.md | ai-memory |
| historical QA evidence | docs/qa/charters/CH-agent-model-routing-adoption-boundary-2026-08-24.md | ai-memory |
| historical QA evidence | docs/qa/charters/CH-ai-memory-handoff-2026-08-24.md | ai-memory, finalize-session |
| historical QA evidence | docs/qa/charters/CH-review-release-0-4-0-2026-08-24.md | ai-memory |
| historical QA evidence | docs/qa/charters/CH-review-release-0-5-0-2026-08-25.md | ai-memory, memory handoff |
| historical QA evidence | docs/qa/reports/2026-08-24-agent-model-routing-local-state.md | ai-memory |
| historical QA evidence | docs/qa/reports/2026-08-24-agent-model-routing.md | ai-memory |
| historical QA evidence | docs/qa/reports/2026-08-24-ai-memory-handoff.md | ai-memory, ai_memory, memory handoff |
| historical QA evidence | docs/qa/reports/2026-08-24-release-0-4-0.md | ai-memory |
| historical QA evidence | docs/qa/reports/2026-08-25-release-0-5-0.md | ai-memory |
| historical changelog | CHANGELOG.md | ai-memory, memory handoff |
| v0.6 removal note | .specs/features/host-owned-session-continuation/design.md | ai-memory |
| v0.6 removal note | .specs/features/host-owned-session-continuation/spec.md | ai-memory, session-memory, handoff payload |
| v0.6 removal note | .specs/features/host-owned-session-continuation/tasks.md | ai-memory, session memory |
| v0.6 removal note | .specs/features/host-owned-session-continuation/validation.md | ai-memory, ai_memory, ai memory, memory handoff, cross-provider handoff, install-hooks, finalize-session, session memory, session-memory, handoff payload, install ai-memory, install ai_memory, enable ai-memory, enable ai_memory, source ai-memory, source ai_memory, disable ai-memory, disable ai_memory, re-enable ai-memory, re-enable ai_memory, purge ai-memory, purge ai_memory, isolate ai-memory, isolate ai_memory, detect ai-memory, detect ai_memory, test ai-memory, test ai_memory, use ai-memory, use ai_memory |

**Classification totals: 22 historical QA evidence, 2 historical changelog, 36 v0.6 removal-note
matches; 60/60 classified; 0 unexpected.**

## Code quality and scope

| Check | Status |
| --- | --- |
| No features beyond request | ✅ |
| No single-use abstraction or unnecessary flexibility | ✅ |
| Only required feature/diff files assessed; no verifier code/test/doc/config writes | ✅ |
| Existing patterns and provider-neutral style preserved | ✅ |
| Tests map to ACs/test-contract IDs and are non-shallow | ✅ |
| Domain/contract coverage expectation met; adoption and route-equivalent CLI paths cover happy/error/retry boundaries | ✅ |
| No unclaimed tests in feature scope | ✅ |
| Guidelines followed | ✅ docs/guidelines/TEST-CONTRACT.md, GATES.md, QA-EXECUTION.md, QA-SCENARIOS.md, VERIFICATION-EVIDENCE.md |

No security surface exists for this removal; spec.md records none. No lesson was recorded because
final validation is clean: no failed AC, spec-precision gap, surviving mutant, or implementation
deviation.

## Final status

**Ready: PASS.** Current HEAD preserves origin/main behavior and satisfies host-owned continuation:
17/17 ACs, 8/8 contract IDs, 20 adoption checks, 44 workflow-config checks, 115 Vitest tests,
65 protected historical files with zero differences, 60/60 classified references, 3/3 killed
sensor mutants, all 17 spec traceability rows Verified, and passing dated QA artifacts. Only authorized real-tree change: this
validation.md report.
