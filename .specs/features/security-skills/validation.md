# External Security Skills Validation

**Date**: 2026-08-22
**Phase**: technical
**Spec**: `.specs/features/security-skills/spec.md`
**Diff range**: `b9024ea..HEAD` (`b9024ea..7795295`)
**Verifier**: fresh independent Verifier (author != verifier)
**Verdict**: PASS
**Result**: PASS

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| SSK-01 | Adoption leaves all three external trees absent and prints the exact authorized command | `scripts/test_adopt.py:62`-`82` — exact full command at `:75`-`:79`, all three trees absent at `:69`-`:74`, external/gate boundary at `:80`-`:82`; process-level assertions at `tools/shared/tests/security-skills-installation.test.ts:137`-`150` | PASS |
| SSK-02 | Every external skill has an exact repository, allowlisted source type, immutable 40-hex commit, skill path, CLI version and 64-hex tree hash | `tools/shared/tests/security-skills-installation.test.ts:156`-`164` — `toMatchObject`, exact `1.5.23`, 40/64-hex assertions; authoritative values at `skills-lock.json:14`-`36` | PASS |
| SSK-03 | Authorized `--yes` installs exactly three pinned trees under `.agents/skills/` and creates matching Claude links | `tools/shared/tests/security-skills-installation.test.ts:188`-`250` — status `0` at `:225`, exact tree bytes and links at `:236`-`:240`, exactly three pinned commands at `:242`-`:250` | PASS |
| SSK-04 | Publication preserves consumer files and unrelated lock entries byte-for-byte | `tools/shared/tests/security-skills-installation.test.ts:212`-`235` — binary sentinel equality at `:228`, unrelated object equality at `:227`-`:231`, exact raw lock-member bytes at `:232`-`:235`; production retains raw members at `scripts/install_security_skills.py:328`-`397` | PASS |
| SSK-05 | CLI unavailable/failure, changed managed paths, staged symlinks, mismatched trees and publication failures return non-zero, restore prior state and report gate unavailable | Hash mismatch and preservation at `tools/shared/tests/security-skills-installation.test.ts:257`-`269`; missing CLI at `:275`-`:291`; non-zero CLI at `:297`-`:314`; external target paths at `:338`-`:372`; publication rollback at `:375`-`:434`; hash-matching internal staged symlink rejection plus unchanged referent at `:519`-`:535`; recursive no-follow control at `scripts/install_security_skills.py:109`-`116`, invoked at `:498`-`:512` before publication | PASS |
| SSK-06 | Reviewed source metadata, exact CLI `1.5.23`, immutable refs and hashes remain authoritative; `latest`, alternate metadata and prior CLI `1.5.22` are rejected | Source substitution at `tools/shared/tests/security-skills-installation.test.ts:458`-`469`; source type/path/alternate 40-hex ref at `:475`-`:491`; production constant remains `1.5.23` at `scripts/install_security_skills.py:20`; lock `1.5.22` rejection before CLI invocation at `tools/shared/tests/security-skills-installation.test.ts:542`-`556`; `latest` rejection at `:562`-`:573` | PASS |
| SSK-07 | Onboarding output and README distinguish bundled workflow skills from separately authorized external security skills | `tools/shared/tests/security-skills-installation.test.ts:129`-`150`; `tools/shared/tests/qa-skills.test.ts:588`-`604`; public contract at `README.md:169`-`190` and `docs/workflow/pack.md:19`-`25` | PASS |

**Acceptance criteria**: 7/7 matched exact spec outcomes; 0 gaps; 0 spec-precision gaps.

## Contract Cases

| Case | Result | Assertion evidence |
| --- | --- | --- |
| IT-001 | PASS | `tools/shared/tests/security-skills-installation.test.ts:167`-`182` — status `2`, exact plan facts, no CLI log or `.agents`, consumer bytes unchanged |
| IT-002 | PASS | `tools/shared/tests/security-skills-installation.test.ts:188`-`250` — three pinned commands, exact tree bytes, hashes and Claude links |
| IT-003 | PASS | `tools/shared/tests/security-skills-installation.test.ts:212`-`235` — consumer bytes and unrelated lock member preserved exactly |
| IT-004 | PASS | `tools/shared/tests/security-skills-installation.test.ts:257`-`314`, `:375`-`:434`, and `:519`-`:535` — divergence, unavailable/non-zero CLI, post-publication failure and staged path change all fail closed with required restoration or non-publication |
| IT-005 | PASS | `tools/shared/tests/security-skills-installation.test.ts:579`-`599` — contender `1`, winner `0`, winner tree remains |
| IT-006 | PASS | `tools/shared/tests/security-skills-installation.test.ts:320`-`332` — dead-owner lock recovered, install succeeds, lock removed |
| IT-007 | PASS | `tools/shared/tests/security-skills-installation.test.ts:440`-`452` — hostile target absent and `env=<missing>` present in child log |
| IT-008 | PASS | `scripts/test_adopt.py:62`-`82` and `tools/shared/tests/security-skills-installation.test.ts:137`-`150` — fresh adoption installs no external tree and prints exact authorized step |
| SEC-001 | PASS | `tools/shared/tests/security-skills-installation.test.ts:338`-`372` — external managed-directory and lock referents unchanged; `:519`-`:535` — internal staged symlink rejected and external sentinel unchanged |
| SEC-002 | PASS | `tools/shared/tests/security-skills-installation.test.ts:458`-`491` — repository/sourceType/skillPath/ref substitutions rejected; `:542`-`:556` — lock `cliVersion: "1.5.22"` rejected while production authority stays `1.5.23` at `scripts/install_security_skills.py:20` |
| SEC-003 | PASS | `tools/shared/tests/security-skills-installation.test.ts:257`-`269` — mismatched tree hash returns `1`, reports gate unavailable and preserves unrelated state |
| SEC-004 | PASS | `tools/shared/tests/security-skills-installation.test.ts:475`-`491` and `:562`-`:573` — alternate 40-hex ref and `latest` rejected before publication |

**Contract coverage**: 12/12 cases proven at integration/public-command layer. No hollow or wrong-layer case found under `docs/guidelines/TEST-CONTRACT.md:23`-`66`.

## Edge Cases

| Edge case | Evidence | Result |
| --- | --- | --- |
| Missing `--yes` returns `2`, prints the plan and makes no target/CLI write | `tools/shared/tests/security-skills-installation.test.ts:167`-`182` | PASS |
| Managed or lock path escaping through symlink fails without changing referent | `tools/shared/tests/security-skills-installation.test.ts:338`-`372` | PASS |
| Hash-matching staged internal symlink fails without changing referent | `tools/shared/tests/security-skills-installation.test.ts:519`-`535` | PASS |
| Concurrent installers serialize so loser cannot roll back winner | `tools/shared/tests/security-skills-installation.test.ts:579`-`599` | PASS |
| Dead-owner lock is recovered | `tools/shared/tests/security-skills-installation.test.ts:320`-`332` | PASS |
| `MY_WORKFLOW_TARGET` is removed from every child invocation | `tools/shared/tests/security-skills-installation.test.ts:440`-`452` | PASS |

## Gate Evidence

- **Targeted command**: `npx vitest run tools/shared/tests/security-skills-installation.test.ts tools/shared/tests/qa-skills.test.ts --reporter=verbose`
- **Targeted outcome**: exit `0`; 2 files, 42 passed, 0 failed, 0 skipped.
- **Full command**: `python3 scripts/test_adopt.py && python3 tools/test_ad_index.py && python3 tools/test_deep_review_token_metrics.py && python3 tools/test_workflow_config.py && npm test && npm run knowledge && git diff --check origin/main..HEAD`
- **Full outcome**: exit `0`; adoption `ok`; AD index `ok`; token metrics 19/19; workflow config 11/11; Vitest 10 files and 122/122 tests; diff check clean.
- **Knowledge diagnostic**: 0 errors, 10 existing warnings. Per `docs/guidelines/GATES.md:25`, knowledge is diagnostic, not the product full gate.
- **Test integrity**: prior technical validation at `964243e` recorded 120 Vitest tests. Current tree has 122; final remediation added two direct regression cases. `git diff --name-only --diff-filter=D origin/main..HEAD -- '*test*'` returned no deleted tests.
- **Warnings affecting verdict**: none.

## Discrimination Sensor

One detached scratch worktree at `20ba4b4baf08182526bc8a859df7d96e885d3fc3`. Each production mutation ran only its owning integration case. Production authority `CLI_VERSION = "1.5.23"` stayed unchanged for the prior-CLI mutation. The scratch was restored, its clean installer suite passed 22/22, then it was removed. Real checkout porcelain matched the empty pre-sensor baseline after cleanup.

| # | Mutation | Production location | Owning assertion | Result |
| --- | --- | --- | --- | --- |
| 1 | Remove recursive staged-tree symlink rejection, leaving hash comparison unchanged | `scripts/install_security_skills.py:508` | `tools/shared/tests/security-skills-installation.test.ts:519`-`535` | KILLED: status became `0`, expected `1` at `:532`; baseline also proves referent bytes unchanged at `:535` |
| 2 | Accept lock `cliVersion: "1.5.22"` in addition to authoritative `1.5.23` | `scripts/install_security_skills.py:76` | `tools/shared/tests/security-skills-installation.test.ts:542`-`556` | KILLED: status became `0`, expected `1` at `:553` |
| 3 | Accept substituted repository provenance | `scripts/install_security_skills.py:72` | `tools/shared/tests/security-skills-installation.test.ts:458`-`469` | KILLED: status became `0`, expected `1` at `:468` |
| 4 | Bypass missing-authorization plan boundary | `scripts/install_security_skills.py:582` | `tools/shared/tests/security-skills-installation.test.ts:167`-`182` | KILLED: status became `1`, expected plan-only `2` at `:177` |
| 5 | Remove rollback after partial publication failure | `scripts/install_security_skills.py:573` | `tools/shared/tests/security-skills-installation.test.ts:375`-`434` | KILLED: new skill bytes remained instead of exact old bytes at `:425`-`:427` |
| 6 | Drop unrelated lock members during merge | `scripts/install_security_skills.py:378` | `tools/shared/tests/security-skills-installation.test.ts:188`-`235` | KILLED: unrelated member became `undefined` at `:227` |
| 7 | Preserve hostile `MY_WORKFLOW_TARGET` in CLI environment | `scripts/install_security_skills.py:558` | `tools/shared/tests/security-skills-installation.test.ts:440`-`452` | KILLED: child log exposed `/outside/target` at `:451` |
| 8 | Bypass per-target transaction lock | `scripts/install_security_skills.py:596` | `tools/shared/tests/security-skills-installation.test.ts:579`-`599` | KILLED: contender returned `0`, expected serialized rejection `1` at `:596` |

**Sensor depth**: security-critical manual full sensor, 8 branch-spanning behavior mutations.
**Sensor outcome**: 8/8 killed, 0 survived — PASS.

## Threat Model and Security Review

- **Security skills applied**: none. The three named security skills are the external dependencies this feature installs and are absent by design; residual review used the project security guideline and the scoped threat model directly.
- **Threat model**: `.specs/features/security-skills/threat-model.md:1`-`64`; required by S9/S11 under `docs/guidelines/SECURITY.md:92`-`102`.
- **TM-001**: PASS. Environment scrub at `scripts/install_security_skills.py:552`-`559`; recursive staged no-symlink enforcement at `:109`-`:116` and `:498`-`:512`; target descriptor opens use `O_NOFOLLOW` at `:162`-`:179`; SEC-001 assertions at `tools/shared/tests/security-skills-installation.test.ts:338`-`372` and `:519`-`:535`.
- **TM-002**: PASS. Target lock spans the transaction at `scripts/install_security_skills.py:588`-`597`; snapshot/rollback is asserted at `tools/shared/tests/security-skills-installation.test.ts:375`-`434`.
- **TM-003**: PASS. Exact metadata checks at `scripts/install_security_skills.py:55`-`89`; source/ref/CLI substitutions are asserted at `tools/shared/tests/security-skills-installation.test.ts:458`-`491`, `:542`-`:556`, and `:562`-`:573`.
- **TM-004**: PASS. Lock recovery at `scripts/install_security_skills.py:240`-`306`; stale and concurrent outcomes at `tools/shared/tests/security-skills-installation.test.ts:320`-`332` and `:579`-`:599`.
- **SEC-001 / S6**: PASS — `tools/shared/tests/security-skills-installation.test.ts:338`-`372`, `:519`-`:535`.
- **SEC-002 / S1, S9**: PASS — `tools/shared/tests/security-skills-installation.test.ts:458`-`491`, `:542`-`:556`.
- **SEC-003 / S6, S9**: PASS — `tools/shared/tests/security-skills-installation.test.ts:257`-`269`.
- **SEC-004 / S1, S9**: PASS — `tools/shared/tests/security-skills-installation.test.ts:475`-`491`, `:562`-`:573`.
- **Open Critical count**: 0.
- **Open High count**: 0.
- **Security verdict**: PASS.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum code / no scope creep | PASS |
| Surgical diff / existing patterns | PASS |
| Spec-anchored outcomes | PASS — 7/7 SSK criteria assert exact status, bytes, paths, pins or public text |
| Per-layer coverage | PASS — all public CLI, filesystem, subprocess and adoption boundaries use integration/process assertions |
| Every in-scope case has a contract owner | PASS — IT-001..008 and SEC-001..004 are claimed above; no orphan or duplicate behavior |
| Test integrity | PASS — no weakened, skipped or deleted in-scope test; all eight mutants killed |
| Guidelines | PASS — `docs/guidelines/TEST-CONTRACT.md`, `SECURITY.md`, `GATES.md`, and `VERIFICATION-EVIDENCE.md` |

## QA Dispatch

The diff changes a public CLI, adoption output and docs-as-interface. Technical verification passes. Dispatch a separate fresh `qa-plan` Verifier session next; end that session before a separate fresh `qa-execute` session.

## Summary

**Overall**: PASS. All SSK-01..07, IT-001..008 and SEC-001..004 match their specified outcomes. Targeted and full gates pass. Eight of eight security-critical mutants were killed. Scratch and live targets were removed, and real-tree porcelain returned to its empty baseline before this ignored report was written.

---

## QA Bug-Fix Reverification: `1fa087d`

**Date**: 2026-08-22
**Phase**: technical
**Bug**: `docs/qa/bugs/BUG-20260822-security-installer-rejects-active-npx.md`
**Diff range**: `b9024ea..1fa087d`
**Verifier**: fresh independent Verifier (author != verifier)
**Verdict**: FAIL

### Public Reproduction

- **Active toolchain**: `node`, `npm`, and `npx` resolve through `<user-home>/.local/share/mise/shims/`; `npx --version` is `10.9.8`.
- **Exact public command**: `python3 scripts/install_security_skills.py .specs/features/security-skills/verifier-scratch/real-mise-target --yes`.
- **Public outcome**: exit `1`; `mise ERROR no tasks defined in .../my-workflow-security-staging-*`; installer reports `skills CLI failed for security-best-practices`. The documented active-shim symptom remains reproducible.
- **Direct-tool probe**: with `PATH=<user-home>/.local/share/mise/installs/node/22/bin:/usr/bin:/bin`, the same public installer exits `0` and installs all three pinned skills. Production resolves active candidates at `scripts/install_security_skills.py:518`-`534` and invokes them from staging at `:674`-`:687`; resolving a mise shim does not make that shim staging-independent.

### Spec-Anchored Trust-Boundary Evidence

| Outcome | Assertion evidence | Result |
| --- | --- | --- |
| Active mise-style external toolchain succeeds | `tools/shared/tests/security-skills-installation.test.ts:801`-`827` — status `0` at `:821` | FAIL — synthetic symlink fixture passes, real active mise shim exits `1` |
| Exact `skills@1.5.23 add ... --skill ... --agent claude-code cursor codex --yes` arguments | `tools/shared/tests/security-skills-installation.test.ts:823` — only `toContain("skills@1.5.23")` | GAP — removing `--agent` survives |
| Target, staging, and pack candidates are rejected | `tools/shared/tests/security-skills-installation.test.ts:586`-`620`, `:829`-`:849` | PASS for ordinary candidates; lexical-path-only control is not discriminated |
| Shim resolving into an untrusted root is rejected | `tools/shared/tests/security-skills-installation.test.ts:870`-`:890` — exact unsafe-target error and no publication | PASS |
| Broken, directory, and non-executable candidates are rejected | `tools/shared/tests/security-skills-installation.test.ts:892`-`:916` — status `1`, exact invalid-executable error, no publication | PASS |
| Child secrets and `MY_WORKFLOW_TARGET` are absent | `tools/shared/tests/security-skills-installation.test.ts:622`-`:646` — exact absence assertions at `:638`-`:643` | PASS |
| Child `PATH` contains only wrapper, validated tool parents, and fixed roots | no assertion; production construction at `scripts/install_security_skills.py:554`-`:569` | GAP — restoring inherited caller `PATH` survives all 37 installer tests |
| Missing active candidate falls back to fixed roots | direct probe with an empty/missing caller path resolves `git` to `/usr/bin/git`; fallback at `scripts/install_security_skills.py:530`-`:534` | PASS |

The active-toolchain and child-environment controls added to TM-001 at `.specs/features/security-skills/threat-model.md:18`-`22`, `:35`-`37` have no `SEC-NNN` owner in `.specs/features/security-skills/tests.md:16`-`23`. This violates `docs/guidelines/SECURITY.md:53`-`72` and the one-owner test-contract rule in `docs/guidelines/TEST-CONTRACT.md`.

### Discrimination Sensor

One checkout-local scratch worktree was reused and removed. Seven behavior mutations were injected against `scripts/install_security_skills.py`; four were killed and three survived.

| # | Mutation | Result |
| --- | --- | --- |
| 1 | Remove `--agent` from the pinned CLI command | SURVIVED — named “exact pinned args” test still passed 1/1 |
| 2 | Disable lexical candidate-root rejection only | SURVIVED — staging/target/pack tests passed 3/3 because resolved-path rejection masked the missing lexical control |
| 3 | Disable both lexical and resolved untrusted-root rejection | KILLED — staging/target/pack tests failed 3/3 |
| 4 | Disable resolved-target rejection only | KILLED — untrusted-target shim test failed 1/1 |
| 5 | Disable regular-file/executable validation | KILLED — directory and non-executable tests failed 2/2; clean baseline also passes the broken-link case |
| 6 | Allow `MY_WORKFLOW_TARGET` and four secret variables into child environment | KILLED — scrub test failed 1/1 with all five values exposed |
| 7 | Restore inherited caller `PATH` in child environment | SURVIVED — full installer suite passed 37/37 |

**Sensor outcome**: 7 injected, 4 killed, 3 survived — FAIL. Surviving mutants are fix tasks; this Verifier made no code change.

### Gate Evidence

- **Targeted**: `npx vitest run tools/shared/tests/security-skills-installation.test.ts --reporter=verbose` — exit `0`; 1 file, 37 passed, 0 failed, 0 skipped.
- **Full**: `python3 scripts/test_adopt.py && python3 tools/test_ad_index.py && python3 tools/test_deep_review_token_metrics.py && python3 tools/test_workflow_config.py && npm test && npm run knowledge && git diff --check origin/main..HEAD` — exit `0`; adoption `ok`; AD index `ok`; token metrics 19/19; workflow config 11/11; Vitest 17 files, 236 passed, 0 failed, 0 skipped; knowledge 0 errors and 10 existing warnings; diff check clean.
- **Diff integrity**: `git diff --check b9024ea..HEAD` exits `0`; fix diff changes 2 files, +217/-64. No test was deleted.
- **Isolation**: scratch worktree and both disposable live targets were removed. Real-tree porcelain matches the pre-sensor baseline exactly; only concurrent QA documentation remains dirty.

### Ranked Fix Tasks

1. Make the exact documented command work with the active mise shim, then reproduce the original bug command red-before/green-after. The direct mise install binary passing is not the reported public path.
2. Strengthen the integration fixture/assertion to verify the complete argument vector for all three pinned skills; mutation #1 must die.
3. Assert the complete scrubbed child `PATH` (wrapper first, then only validated lexical/resolved parents and fixed roots); mutation #7 must die.
4. Add a lexical candidate under target/staging/pack whose parent path resolves outside, assign the active-tool boundary to explicit `SEC-NNN` case(s), and kill mutation #2.

### Security Verdict

- **TM-001**: FAIL — real active shim unsupported; two trust-boundary controls have surviving mutants and no security case owner.
- **SEC-001..SEC-004**: 4 PASS, 0 FAIL for their existing declared outcomes; they do not claim active toolchain discovery or child `PATH` confinement.
- **Open Critical count**: 0.
- **Open High count**: 0 — surviving mutants are test-evidence gaps, not vulnerabilities present in the current production code.
- **Overall QA-fix verdict**: FAIL. Return to an Implementer; require a fresh technical Verifier after remediation before QA Execute resumes the affected journey.

---

## QA Bug-Fix Reverification: `7795295`

**Date**: 2026-08-22
**Phase**: technical
**Bug**: `docs/qa/bugs/BUG-20260822-security-installer-rejects-active-npx.md`
**Diff range**: `b9024ea..7795295`
**Verifier**: fresh independent Verifier (author != verifier)
**Verdict**: PASS

### Public Red/Green Reproduction

- Active public toolchain: `node`, `npm`, and `npx` use `<user-home>/.local/share/mise/shims/`; `node --version` is `v22.23.1`, `npx --version` is `10.9.8`, and the npx shim resolves to `<user-home>/.local/bin/mise`.
- Red at `b9024ea`: `python3 scripts/install_security_skills.py <disposable-target> --yes` exited `1` with `trusted npx executable unavailable`.
- Green at `7795295`: the same public argv against a clean disposable target exited `0`, installed exactly three `.agents/skills` trees, and created exactly three Claude links. Every link had the exact relative target `../../.agents/skills/<skill-name>`.
- Production evidence: lexical and resolved candidate validation at `scripts/install_security_skills.py:501`-`518`; original lexical shim returned for execution at `:515`-`:518`; exact CLI argv at `:540`-`:553`; constrained child PATH at `:556`-`:571`; both lexical and canonical target/staging/pack roots at `:693`-`:710`.

### SEC-005 and Threat-Boundary Evidence

| Contracted outcome | `file:line` assertion or live public evidence | Result |
| --- | --- | --- |
| Active mise-style candidates install successfully | `tools/shared/tests/security-skills-installation.test.ts:803`-`830` — `expect(result.status).toBe(0)`; exact active mise public command above also exits `0` | PASS |
| Exactly three immutable CLI invocations use `--agent universal --copy --yes` | `tools/shared/tests/security-skills-installation.test.ts:831`-`838` and `:350`-`:360` — `toHaveLength(3)` plus exact ordered `toEqual(...)` vectors | PASS |
| Child PATH contains only wrapper, validated lexical/resolved parents, and fixed roots | `tools/shared/tests/security-skills-installation.test.ts:839`-`851` — exact ordered array, uniqueness, hostile directory exclusion, and no hostile execution | PASS |
| Secrets and `MY_WORKFLOW_TARGET` are removed | `tools/shared/tests/security-skills-installation.test.ts:624`-`645` — target absent and four named secrets all `False`; active-tool test also checks `GITHUB_TOKEN=False` at `:852` | PASS |
| Lexical candidate under an untrusted root is rejected even when its target is external | `tools/shared/tests/security-skills-installation.test.ts:921`-`937` — status `1`, exact unsafe-location error, no publication | PASS |
| Safe-looking candidate resolving into an untrusted root is rejected | `tools/shared/tests/security-skills-installation.test.ts:899`-`915` — status `1`, exact unsafe-target error, no publication | PASS |
| `/tmp` lexical root and `/private/tmp` canonical root are both enforced on macOS | inverse-realpath probe observed `/tmp/my-workflow-reverify.*` resolving to `/private/tmp/my-workflow-reverify.*`; the lexical-root case at `tools/shared/tests/security-skills-installation.test.ts:921`-`937` passed | PASS |
| Exactly three installed trees and Claude links match pins | `tools/shared/tests/security-skills-installation.test.ts:344`-`360` — exact bytes/hashes, all links symbolic, exactly three exact commands; public green probe counted 3 trees and 3 links | PASS |

SEC-005 now owns the active-toolchain control in `.specs/features/security-skills/tests.md:24`. TM-001 matches the implementation and evidence above. Open Critical: 0. Open High: 0.

### Discrimination Sensor

One detached scratch worktree was reused for the historical reproduction, all four mutations, and public probes, then removed. Real checkout porcelain after cleanup exactly retained only the pre-existing tracked/untracked QA documents.

| # | Mutation | Owning probe | Result |
| --- | --- | --- | --- |
| 1 | Remove `--agent universal` | Exact ordered argv assertions at `tools/shared/tests/security-skills-installation.test.ts:831`-`838` | KILLED — selected test failed 1/1 at `:833` |
| 2 | Restore inherited caller PATH | Exact confined PATH assertion at `tools/shared/tests/security-skills-installation.test.ts:839`-`851` | KILLED — selected test failed 1/1 at `:841`, exposing hostile and inherited directories |
| 3 | Remove lexical candidate-root guard | Inverse lexical/resolved-root assertion at `tools/shared/tests/security-skills-installation.test.ts:921`-`937` | KILLED — mutant returned `0`, expected `1` at `:935` |
| 4 | Execute resolved mise target instead of validated shim | Exact active-mise public installation command | KILLED — synthetic symlink test passed, but the real public probe exited `1` with `mise ERROR no tasks defined`; clean code exits `0` |

**Sensor outcome**: 4/4 behavior mutations killed, 0 survived — PASS. Mutation 4 requires the real active-mise public interface because the portable symlink fixture does not emulate mise's argv[0]-dependent dispatch; this limitation is explicit, not treated as synthetic coverage.

### Gate Evidence

- Targeted: `npx vitest run tools/shared/tests/security-skills-installation.test.ts --reporter=verbose` — exit `0`; 1 file, 38 passed, 0 failed, 0 skipped.
- Focused trust-boundary probes: selected active-toolchain, secret-scrub, and inverse-realpath cases — exit `0`; 3 selected passed, 0 failed.
- Full: `python3 scripts/test_adopt.py && python3 tools/test_ad_index.py && python3 tools/test_deep_review_token_metrics.py && python3 tools/test_workflow_config.py && npm test && npm run knowledge && git diff --check origin/main..HEAD` — exit `0`; adoption `ok`; AD index `ok`; token metrics 19/19; workflow config 11/11; Vitest 10 files and 138/138 tests; knowledge 0 errors and 10 existing warnings; diff check clean.
- Diff integrity: `git diff --check b9024ea..HEAD` exited `0`; two files changed, +313/-77; no test file was deleted.
- Test integrity: no weakened, skipped, or deleted in-scope test. Current installer suite is 38/38, up from 37/37 in the prior re-verification.

### Summary

**Overall**: PASS. The original public mise failure is red before the fix and green after it. SEC-005 matches the spec and threat model. Targeted and full gates pass. Four of four required behavior mutations were killed. Scratch and disposable targets were removed; QA documents were preserved byte-for-byte.
