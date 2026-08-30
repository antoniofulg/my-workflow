# Bun tooling runtime — QA Execute retest

- **Date:** 2026-08-29
- **Reviewed HEAD:** `761d1883d1c212092eb80634b9402f3dac53ec12`
- **Personas:** Repository reader; Workflow adopter
- **Adapter:** CLI/manual through documented Bun, adoption, package, knowledge, assisted-probe,
  and external-security entry points with independent filesystem readback
- **Environment:** active feature checkout plus disposable targets; Bun 1.4.x; network disabled
- **Raw evidence:** `docs/qa/evidence/2026-08-29-bun-tooling-runtime-retest/`
- **Live Orca:** not invoked

## Gate

Opening command: `bun run test:all`.

Exit `0`. Bun reported 122 passes, 0 failures, and 1113 assertions across 8 suites. The command
then ran all 17 Python suite files returned by
`git ls-files -- 'scripts/test_*.py' 'tools/test_*.py' | wc -l`; every suite exited zero. The
previously failing Bun history guard accepted the three current-cycle charters and other new QA
artifacts. Raw output: `docs/qa/evidence/2026-08-29-bun-tooling-runtime-retest/opening-gate.txt`.

## Matrix

| Charter | Scenarios | Verdict | Independent readback |
| --- | --- | --- | --- |
| `CH-review-bun-tooling-runtime-2026-08-29` | `REL-report-current-workflow-release` | pass | Reloaded manifest, lockfile, config, README, changelog, command outputs, and dry-run package list |
| `CH-adopt-bun-tooling-runtime-2026-08-29` | `REL-report-current-workflow-release`; `ADP-adopt-workflow-safely` | pass | Reloaded installed hashes, Bun knowledge output, sentinels, legacy paths, restored managed bytes, and fake-Orca call log |
| `CH-enable-bun-security-skills-2026-08-29` | `REL-report-current-workflow-release`; `ADP-install-pinned-external-security-skills`; `ADP-preserve-security-install-target` | pass for authorized scope; remote success untested | Reloaded three-command plan, target snapshots, refusal outputs, and exact fake-bunx call log |

## Charter results

### Review Bun tooling runtime

`bun --version` reported `1.4.0`. `package.json` declares `bun@1.4.0`, supports
`>=1.4.0 <1.5.0`, runs knowledge directly with Bun, uses `bun test`, and defines the full gate as
`bun run test && bun run test:python`. `bunfig.toml` restricts discovery to `tools/` and preloads the
version guard. The committed `bun.lock` root lists the manifest's five development dependencies.
README documents `bun install --frozen-lockfile`, `bun run test:all`, and `bun run knowledge`; the
newest changelog and package version both report `0.7.0`.

Public command results:

- `bun install --frozen-lockfile`: exit `0`; 49 installs across 50 packages, no changes.
- `bun test`: exit `0`; 122 passes, 0 failures, 1113 assertions across 8 files.
- `bun run knowledge`: exit `0`; 0 errors and 33 non-gating harvest warnings.
- `bun run test:all`: exit `0`; the same 122/0 Bun result plus all 17 tracked Python suite files.
- `bun pm pack --dry-run --ignore-scripts`: exit `0`; 434 files, 3.50 MB unpacked, with all five
  sampled required public members. `find . -maxdepth 1 -type f -name '*.tgz'` returned zero paths.

The opening canonical active-authority/history check passed. Independent reload of its inputs found
only Bun commands in active README/package authority; baseline evidence remained untouched, while
new current-cycle QA artifacts remained accepted.

### Adopt Bun tooling runtime

Fresh adoption and re-adoption each exited `0`. Six sampled installed authorities matched source
bytes: both knowledge sources, shared frontmatter source, assisted probe, parallel pilot, and the
workflow-spec-driven skill. The installed knowledge CLI ran with Bun from the consumer without a
consumer package install and exited `0`.

Repository-owned TypeScript suite bytes installed: `0`. One unchanged v0.7.0 legacy suite was
removed; an edited consumer-owned legacy-path test and a separate consumer test were preserved.
The obsolete TLC skill/link and exact legacy `.specs/features/` ignore entry were removed while the
consumer ignore line remained. Re-adoption restored an intentionally changed managed knowledge file
and preserved four consumer sentinels byte-for-byte. Importing the installed assisted probe with a
call-counting fake `orca` produced exactly 0 Orca calls. Cleanup removed the disposable target.

### Enable Bun security skills

Running the public installer without `--yes` exited `2`, printed exactly three pinned
`bunx --bun --no-install skills add` commands, and left the adopted target byte-identical. A
disposable pack with no trusted `bunx` exited `1` before mutation. A second disposable pack with a
locally resolvable fake reporting `9.9.9` exited `1`; its log contained exactly one
`--bun --no-install skills --version` call and 0 add calls. Both targets remained byte-identical,
and all temporary pack, target, and fake-tool directories were removed.

The prior authorized installation verdict was not contradicted. This cycle did not authorize
network or target writes for the remote success leg, so that leg remains untested rather than
simulated.

## Edge probes and experience lenses

Ten relevant probes passed:

1. new charters no longer trip the historical-evidence gate;
2. frozen install changes no dependency state;
3. test discovery remains under `tools/`;
4. dry-run packing creates no checkout tarball;
5. unchanged legacy tests are removed;
6. consumer-edited legacy tests survive;
7. re-adoption restores managed bytes without changing consumer bytes;
8. probe import performs zero Orca calls;
9. unauthorised and missing-executable security paths write nothing; and
10. wrong-version preflight performs one version read and zero add calls.

Comprehension matched README commands to executable manifest authority. Recovery restored managed
bytes on re-adoption. Trust probes confirmed fail-closed, zero-write security behavior and zero
import side effects. CLI language named the exact missing/wrong-version boundary. Browser
accessibility and reload lenses do not apply to this repository's CLI/manual surface; independent
filesystem and output reloads supplied confirmation.

## Limitations

Successful external-security installation is not authorized in this cycle. Its remote network/write
leg remains `untested`; no fake success substitutes for it. No browser, API, mobile, server,
publish, release, live Orca, or registry surface is in scope.

## Cleanup and closing gate

All disposable targets, pack copies, and fake executable directories were removed. The count command
recorded 0 checkout tarballs and 0 disposable directories. Ignored raw evidence remains under the
declared cycle path; durable changes are this new report, the fixed-bug retest, and the one scenario
flagged by the QA Plan. Adjacent canary scenario files retain their prior passing verdicts and
evidence because this run did not contradict them or rerun the authorized remote-success leg.

The first closing attempt exited `1` after the Verifier updated three adjacent canary scenario files
that the QA Plan explicitly retained. The historical-integrity guard correctly named those three
baseline paths. Restoring their unchanged prior verdict/evidence removed the QA-runner mistake; no
product fix or test change was made. The final gate below is the terminal result.

After restoring the retained adjacent scenarios, `bun test tools/shared/tests/qa-skills.test.ts`
passed 29 tests, 0 failures, and 553 assertions. The closing `bun run test:all` exited `0`: 122 Bun
tests passed with 0 failures and 1113 assertions, followed by all 17 tracked Python suite files.
`python3 .agents/skills/workflow-spec-driven/scripts/validate_state.py bun-tooling-runtime` reported
0 errors; `git diff --check` exited `0`. Final residue scans found 0 checkout tarballs and 0
disposable QA target/pack/fake-tool directories. `git status --short` listed exactly three intended
durable paths: this new report, the fixed-bug retest, and the flagged release scenario.

**Cycle verdict:** pass for every reachable Bun tooling and adoption promise. The remote
external-security success leg remains explicitly untested without network/write authorization.
