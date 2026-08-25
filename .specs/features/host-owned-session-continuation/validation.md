# Host-Owned Session Continuation Validation

**Date**: 2026-08-25
**Spec**: `.specs/features/host-owned-session-continuation/spec.md`
**Diff range**: `1451afa960c65c120035a201210b95664b0d8c52..7dee0d8`
**Verifier**: independent technical verifier; author ≠ verifier; no Implementer transcript or operator handoff loaded

## Verdict

**Verdict**: PASS

Technical verification passes 16/17 HSC criteria. HSC-10/QA-001 is explicitly deferred to the
separate fresh `qa-plan` and `qa-execute` packets required by the spec and task protocol; this
technical packet did not create or execute the dated QA charter/report.

## Task Completion

| Task | Status | Evidence |
| --- | --- | --- |
| T1 | Done | `.specs/features/host-owned-session-continuation/tasks.md:45-68`; AD index and decision gates passed |
| T2 | Done | `.specs/features/host-owned-session-continuation/tasks.md:71-95`; deleted-path/package contract passed |
| T3 | Done | `.specs/features/host-owned-session-continuation/tasks.md:99-123`; 19 registered adoption checks passed |
| T4 | Done | `.specs/features/host-owned-session-continuation/tasks.md:127-146`; host/reviewer contract passed |
| T5 | Done for technical phase | `.specs/features/host-owned-session-continuation/tasks.md:150-173`; current scenarios are `untested` for fresh QA |
| T6 | Done | `.specs/features/host-owned-session-continuation/tasks.md:175-200`; release, package, history, and scan gates passed |

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion/evidence | Result |
| --- | --- | --- | --- |
| HSC-01: deleted active paths absent | No implementation, test, guide, active scenario, or obsolete feature tree at the named paths | `tools/shared/tests/qa-skills.test.ts:67-96` asserts each removed path is absent and the repository file listing has zero matches; diff records the deletions | PASS |
| HSC-02: clean adoption has no removed subsystem | No config, DB, marker, source line, hook, payload, script, guide, scenario, or feature test in disposable output | `scripts/test_adopt.py:245-286` asserts sentinels, all named forbidden paths, and the removed source line after clean adoption; command passed | PASS |
| HSC-03: repeated adoption is idempotent and host-neutral | Second adoption leaves managed output stable and shell/hook/host sentinels byte-identical | `scripts/test_adopt.py:259-291` snapshots after first run, runs adoption again, compares snapshots and all sentinel bytes; command passed | PASS |
| HSC-04: package has no removed artifact | `npm pack --dry-run --json` contains zero removed integration paths | `tools/shared/tests/workflow-config.test.ts:70-102` filters package paths; parser output was `version=0.6.0`, `entryCount=288` before this report and `entryCount=289` after the report was added, `removed=[]` in both | PASS |
| HSC-05: current host-owned rule | README and workflow index contain the exact host-owned continuation sentence | `README.md:222-223`, `docs/workflow/README.md:9-10`, and `tools/shared/tests/qa-skills.test.ts:104-108` assert the exact normalized rule | PASS |
| HSC-06: no current removed-integration instructions | No current instruction to install, enable, source, disable, re-enable, purge, isolate, detect, test, or use the removed integration | `tools/shared/tests/qa-skills.test.ts:119-132` rejects removed phrases in current public/reviewer surfaces; final 13-term tracked-file scan found 38 matches, all allowlisted and zero unexpected | PASS |
| HSC-07: fresh independent reviewer packets | Verifier and Deep Reviewer use fresh packets, exclude Implementer transcript/operator handoff, and use spec/diff/tests/assigned evidence | `docs/guidelines/REVIEW-ROUNDS.md:75-80`; verifier packet assertions at `tools/shared/tests/qa-skills.test.ts:99-117`; provider packets at `templates/agents/claude/verifier.md:9-26`, `templates/agents/codex/verifier.toml:7-24`, `templates/agents/cursor/verifier.md:9-26` | PASS |
| HSC-08: host-neutral generic guidance | Current generic guidance contains no Orca dependency or command | `tools/shared/tests/qa-skills.test.ts:129-132` rejects Orca in current surfaces; tracked generic guidance scan found no Orca, while only AD-011 rationale names it at `.specs/STATE.md:154-156` | PASS |
| HSC-09: current QA has no active removed promise | Current profile, journey, and scenarios contain no active removed-integration promise | `docs/qa/README.md:8-18`, `docs/qa/journeys/J-adopt-workflow.md:27-35`, `docs/qa/scenarios/ADP-adopt-workflow-safely.md:19-23`, and `docs/qa/scenarios/REL-report-current-workflow-release.md:19-27`; removed WFL scenario is absent | PASS |
| HSC-10: v0.6.0 QA charter/report | Fresh QA plan and execution create a dated charter/report covering all listed observables | No evidence in technical packet by design. Current scenarios remain `qa_status: untested` at `docs/qa/scenarios/ADP-adopt-workflow-safely.md:9` and `docs/qa/scenarios/REL-report-current-workflow-release.md:9`; defer to fresh QA packets | DEFERRED |
| HSC-11: immutable historical evidence | Protected historical files equal their v0.5.0 bytes | `tools/shared/tests/qa-skills.test.ts:932-951` protects QA history and 0.4.0 changelog; independent comparison found 63 protected QA files, `byte_changed=[]`, `missing=[]`, 0.4.0/0.5.0 changelog sections equal, and no tracked evidence files | PASS |
| HSC-12: explicit final reference allowlist | Every remaining removed-integration reference is classified as historical changelog, historical QA evidence, or v0.6.0 removal note | `tools/shared/tests/qa-skills.test.ts:135-175` owns exact allowlist/classification; independent scan output: 38 matches, historical QA 29, removal note 7, changelog 2, unexpected 0 | PASS |
| HSC-13: version parity | Package, lockfile, release scenario, and every release-version assertion equal `0.6.0` | `tools/shared/tests/qa-skills.test.ts:900-923`, `tools/shared/tests/deep-review-installation.test.ts:70-72`; parity command reported authorities `[0.6.0, 0.6.0, 0.6.0]`, 7 release assertions, all `0.6.0`, scenario exact `true` | PASS |
| HSC-14: v0.6.0 changelog contract | Entry records removal, host responsibility, durable semantic context, and adoption's external-state rule | `CHANGELOG.md:5-19`; exact assertions at `tools/shared/tests/qa-skills.test.ts:924-927` | PASS |
| HSC-15: migration guidance | Note links tagged v0.5.0 lifecycle guide and does not invent or execute cleanup commands | `CHANGELOG.md:14-19`; link and tagged-guide assertions at `tools/shared/tests/qa-skills.test.ts:928-929`; no cleanup command was run | PASS |
| HSC-16: AD-011 ownership decision | AD-011 supersedes AD-008, names Orca only as rationale, and sets host-neutral boundary | `.specs/STATE.md:99-118` and `.specs/STATE.md:150-162`; generated index at `.specs/AD-INDEX.md:16-19`; `test_ad_index.py` and index check passed | PASS |
| HSC-17: local-only preparation | No tag, push, PR, merge, publication, release, deploy, or operator-machine mutation | `package.json:3-4` remains private; clean `git status --short --branch` showed only local feature branch, `git tag --list 'v0.6.0'` was empty, `origin/main` remained at `1451afa`, and adoption tests used disposable temp targets (`scripts/test_adopt.py:245-257`) | PASS |

**Spec-anchored result**: 16/17 technical criteria matched exact outcomes; HSC-10 is a planned
QA-phase handoff, not a technical-phase claim.

## Test-Contract Cases

| Case | Evidence | Result |
| --- | --- | --- |
| CT-001 | `tools/shared/tests/qa-skills.test.ts:135-175`; final allowlist scan | PASS |
| CT-002 | `tools/shared/tests/qa-skills.test.ts:99-132`; targeted contract test | PASS |
| CT-003 | `tools/shared/tests/qa-skills.test.ts:900-923`; parity command | PASS |
| CT-004 | `tools/shared/tests/qa-skills.test.ts:932-951`; 63-file byte comparison | PASS |
| ADP-001 | `scripts/test_adopt.py:245-286`; clean adoption | PASS |
| ADP-002 | `scripts/test_adopt.py:259-291`; repeat adoption and sentinels | PASS |
| REL-001 | `tools/shared/tests/workflow-config.test.ts:70-102`; package dry-run | PASS |
| QA-001 | `.specs/features/host-owned-session-continuation/tests.md:24`; fresh QA charter/report not run in this packet | DEFERRED |

## Discrimination Sensor

Sensor used a temporary copied checkout, never `git stash`, and deleted scratch afterward.

| Mutation | Scratch fault | Test result | Killed |
| --- | --- | --- | --- |
| 1 | `scripts/adopt.py` wrote `scripts/ai-memory.zsh` into every adopted target | `python3 scripts/test_adopt.py` exited 1 at `scripts/test_adopt.py:279` (`AssertionError: scripts/ai-memory.zsh`) | PASS |
| 2 | `tools/shared/tests/qa-skills.test.ts` classified the host feature path as agent-model-routing | Targeted HSC contract exited 1 at `tools/shared/tests/qa-skills.test.ts:173` with five unexpected host-feature references | PASS |
| 3 | `templates/agents/codex/verifier.toml` omitted `the operator handoff` from the packet exclusion | Targeted HSC contract exited 1 at `tools/shared/tests/qa-skills.test.ts:116` | PASS |

**Sensor**: 3/3 killed. Real-tree `git status --porcelain=v1` after scratch deletion was exactly
empty, matching the pre-sensor baseline.

## Gate Check

| Command | Exit/result |
| --- | --- |
| `python3 scripts/test_adopt.py` | 0; 19 registered checks, final `ok` |
| `python3 tools/test_workflow_config.py` | 0; 37 passed, 0 failed |
| `npm test` | 0; 7 files passed, 112 tests passed, 0 failed |
| `python3 .agents/skills/tlc-spec-driven/scripts/validate_spec.py host-owned-session-continuation` | 0 errors, 0 warnings |
| `python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py host-owned-session-continuation` | 0 errors, 1 expected T1 `Tests: none` warning; matrix marks decision/metadata layer as none |
| `python3 tools/test_ad_index.py` | 0; `ok` |
| `python3 tools/ad-index.py --check` | 0; `AD-INDEX.md up to date` |
| `npm pack --dry-run --json` | 0; `my-workflow@0.6.0`, 288 implementation entries; 289 final checkout entries including this validation report; removed paths `[]` |
| `git diff --check 1451afa960c65c120035a201210b95664b0d8..HEAD` | 0; no output |
| targeted HSC removal contract | 0; 3 passed, 24 selector-skipped |
| final reference scan/classification | 0; 13 terms, 38 matches, all classified, 0 unexpected |
| protected historical comparison | 0; 63 files, 0 byte changes, 0 missing, changelog 0.4.0/0.5.0 sections equal |
| full Build gate (`scripts/test_adopt.py && tools/test_workflow_config.py && npm test && tools/ad-index.py --check && git diff --check`) | 0; all component results above passed |

### Test-count integrity and timeout judgment

An isolated clone of the pre-feature commit `1451afa960c65c120035a201210b95664b0d8` ran the
same `npm test` command: 7 files, 108 tests, 107 passed, and the pre-existing package dry-run
test timed out at the default 5,000 ms after Vitest measured 9,346 ms for that test. Current
tree: 7 files, 112 passed. Delta: +4 tests. The 5s→30s timeout in
`tools/shared/tests/workflow-config.test.ts:103` is therefore necessary for this package dry-run
contract in the observed environment, aligns with the repository's other package tests, and stays
within the changed package-absence contract. It is not scope creep.

## Code Quality and Scope

- Minimum/surgical change: PASS. Diff is the requested removal, host-neutral docs/contracts, QA reset,
  release metadata, tests, and stale-reference cleanup; no replacement runtime or compatibility path.
- Historical bytes: PASS. Protected QA and changelog evidence remained unchanged.
- Test integrity: PASS. No existing test was weakened or deleted to pass; the old feature test was
  removed with the deleted subsystem, and current gates pass.
- Reviewer independence: PASS. Fresh-packet rule is asserted across current reviewer guidance and
  all three provider verifier packets.
- Host neutrality: PASS. No Orca dependency/command in current generic guidance; Orca appears only
  in AD-011 rationale and allowlisted feature-contract assertions.
- External state: PASS. No push, PR, merge, tag, publication, release, deploy, or operator-state
  command was run. Package remains private and v0.6.0 remains untagged.

## QA Handoff

Technical packet does not run QA Plan or QA Execute. Fresh QA packets must create the dated v0.6.0
charter and execution report, walk QA-001 through the declared CLI/manual adapter, and update the two
current `untested` scenario rows only after independent evidence survives reload.

## Lessons

No lesson recorded: no AC failed, no mutant survived, no spec-precision gap or SPEC_DEVIATION was
found, and all technical gates passed. HSC-10/QA-001 is an explicit phase handoff, not a verification
failure.
