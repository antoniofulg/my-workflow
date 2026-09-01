# 2026-09-01 — gate cache tool

- **Phase:** `qa-execute`, fresh Verifier session, author ≠ verifier.
- **Branch / HEAD:** `feat/gate-cache-tool` at `aa2fbc6`.
- **Adapter:** CLI/manual, per [`docs/qa/README.md`](../README.md). No browser, API, or mobile
  surface exists in this repository.
- **Exact execution path:** `python3 tools/gate_cache.py run --gate <label> --root <repo> -- <command>`,
  driven against two checkout-local disposable Git repositories created under the ignored evidence
  path, plus the source checkout itself for the real-gate and Git-visibility legs.
- **Environment:** Python 3.14.7, git 2.50.1 (Apple Git-155), darwin 25.6.0.
- **Evidence destination:** `docs/qa/evidence/2026-09-01-gate-cache-tool/` (ignored).
- **Gate authority:** the `test:all` script in [`package.json`](../../../package.json), invoked as
  `bun run test:all`.
- **Charters walked:** [`CH-reuse-gate-results-2026-09-01`](../charters/CH-reuse-gate-results-2026-09-01.md),
  [`CH-refuse-cache-authority-over-gates-2026-09-01`](../charters/CH-refuse-cache-authority-over-gates-2026-09-01.md).
- **Journey:** [`J-run-project-gates`](../journeys/J-run-project-gates.md).
- **Out of scope this cycle:** adoption. The tool is not in the adoption payload in this delivery, so
  no `ADP` leg was walked and no adoption canary is claimed.

## Matrix

| Charter / scenario | Verdict | Evidence |
| --- | --- | --- |
| `CH-reuse-gate-results-2026-09-01` | pass | `evidence/2026-09-01-gate-cache-tool/reuse/walk.log`; `reuse/real-gate-hit.log` |
| [`QAS-reuse-gate-result-for-unchanged-tree`](../scenarios/QAS-reuse-gate-result-for-unchanged-tree.md) | `pass` | `reuse/walk.log`; `reuse/real-gate-hit.log`; `docs/wired-documents.log` |
| `CH-refuse-cache-authority-over-gates-2026-09-01` | pass | `refusal/walk.log`; `refusal/step10-redo.log`; `refusal/interrupt.log` |
| [`QAS-run-the-gate-when-the-cache-cannot-vouch`](../scenarios/QAS-run-the-gate-when-the-cache-cannot-vouch.md) | `pass` | `refusal/walk.log`; `refusal/step10-redo.log`; `refusal/interrupt.log` |
| [`CFG-keep-the-gate-cache-out-of-git`](../scenarios/CFG-keep-the-gate-cache-out-of-git.md) | `pass` | `gitvis/git-visibility.log`; `gitvis/package-and-clone.log` |

No row remained pending. One leg is recorded unwalked; see **Legs not walked**.

## Reuse tour — `QAS-reuse-gate-result-for-unchanged-tree`

Disposable repository with a counting gate that appends to a counter **outside** the fingerprinted
tree. Every verdict was read from the counter, the record file, and the log — never from elapsed
time. Counter total after the tour: 6 executions across 15 invocations.

| Journey step | Leg | Fingerprint | Exit | Counter delta |
| --- | --- | --- | --- | --- |
| 1 | first run, clean tree | `cd119406…` MISS | 0 | +1 |
| 2 | identical rerun | `cd119406…` HIT | 0 | 0 |
| 2 | identical rerun again | `cd119406…` HIT | 0 | 0 |
| 3a | tracked-file edit | `897093ec…` MISS | 0 | +1 |
| 3a | reverted | `cd119406…` HIT | 0 | 0 |
| 3b | staged, not committed | `02431ddd…` MISS | 0 | +1 |
| 3b | reverted | `cd119406…` HIT | 0 | 0 |
| 3c | untracked, unignored | `428bc3f8…` MISS | 0 | +1 |
| 3c | reverted | `cd119406…` HIT | 0 | 0 |
| 3d | ignored file (control) | `cd119406…` HIT | 0 | 0 |
| 4 | `--allow-empty` commit | `cd119406…` HIT | 0 | 0 |
| 5a / 7 | same command, `--gate full` | `a98a119d…` MISS | 0 | +1 |
| 5b | same label, different command | `22ebe030…` MISS | 0 | +1 |

Step 1's record was read directly: `version: 1`, `status: "pass"`, `exit_code: 0`, gate `scoped`,
tree `b13b384f…`, and a log holding exactly the command's output. The evidence line names outcome,
gate, fingerprint, and log path on every invocation.

**Scope binding (`AD-021`, journey step 7).** The `scoped` passing record for tree `b13b384f…`
did not satisfy `--gate full` on that same tree and same command: the full invocation fingerprinted
`a98a119d…`, missed, and executed. The observable is a different fingerprint, not a judgement call.

**Real gate, source checkout.** On the unchanged tree at `aa2fbc6`,
`python3 tools/gate_cache.py run --gate full -- bun run test:all` returned
`HIT gate=full fingerprint=da698c7e…` in 0.61 s wall, exit 0. Independent read path: the record file
`.gate-cache/da698c7e….json` (`status: "pass"`, tree `cec5c43d…`) and the cited log, whose tail shows
the real suites (`45 passed, 0 failed`; `Ran 5 tests in 2.131s / OK`). A second identical invocation
returned the same HIT — the verdict survives a re-read.

**Documents (journey step 6) — divergence, not a defect.** Only
[`docs/guidelines/GATES.md`](../../guidelines/GATES.md) names the cached invocation, at line 58, with
the citation rule at lines 51–52. `.agents/skills/autonomous/SKILL.md`, the `implement.md` reference,
and `.agents/skills/qa-execute/SKILL.md` do not, and `autonomous` line 135 still reads "A cached or
partial result is not evidence". That is **correct for this delivery**:
`.specs/features/gate-result-cache/spec.md` carries five criteria (`GRC-01`–`GRC-05`), no `GRC-06`
and no P2, and its assumption table records "Wiring depth: Tool only in this delivery". Its only
documentation success criterion — "`GATES.md` names the invocation that produces a record" — holds.
The `GRC-06` rows in both charters and the four-document claim in the reuse scenario body were
written against an older base and do not describe this spec; they are corrected here rather than
walked. The `autonomous` readiness row will need wiring in a later delivery; no bug is filed against
this one.

## Refusal tour — `QAS-run-the-gate-when-the-cache-cannot-vouch`

Twenty legs, each capturing stdout, stderr, and the exit status separately, each scanned for a
traceback. **Zero tracebacks across the whole tour, and no leg produced a non-zero exit that the gate
command did not itself produce.** Counter total: 30.

| Journey step | Leg | Exit | Counter delta | Observed |
| --- | --- | --- | --- | --- |
| 8 | failing gate, first run | 7 | +1 | MISS, record `status: "fail"`, `exit_code: 7`, log readable |
| 8 | identical rerun | 7 | +1 | executed again; earlier failing record never short-circuited |
| 9a | record truncated mid-object | 0 | +1 | treated as absent, gate ran |
| 9b | record replaced with `[]` | 0 | +1 | treated as absent — the regression this tour exists for |
| 9c | record replaced with `"pass"` | 0 | +1 | treated as absent |
| 9 | record replaced with literal `null` | 0 | +1 | treated as absent; the historic `AttributeError` exit 1 did **not** reproduce |
| 9 | record replaced with `42` | 0 | +1 | treated as absent |
| 9 | record replaced with non-JSON text | 0 | +1 | treated as absent |
| 9 | record replaced with `true` | 0 | +1 | treated as absent |
| 9c | `version` bumped to `99` | 0 | +1 | treated as absent |
| 9d | record intact, log deleted | 0 | +1 | treated as absent |
| 9 | `log` field removed | 0 | +1 | treated as absent |
| 9 | `log` field set to `null` | 0 | +1 | treated as absent |
| 9 | record `chmod 000` | 0 | +1 | treated as absent |
| 10 | `--root` outside every Git repository | 0 | +1 | `NOCACHE … reason=CalledProcessError`; root left empty, nothing written |
| 10 | `git` absent from `PATH` | 0 | +1 | `NOCACHE … reason=FileNotFoundError`; no `.gate-cache/` created |
| 11 | no command after `--` | 2 | 0 | `USAGE` line, stderr `no command after --`, cache listing byte-identical |
| 11 | no `--` at all | 2 | 0 | same refusal, cache listing byte-identical |
| 12 | closing clean run | 0 | +1 | MISS, record written |
| 12 | closing rerun | 0 | 0 | HIT — the cache still earns an honest hit after the whole tour |

Every damaged-record leg started from a freshly earned passing record and mutated the record file by
hand, never through the tool's own writer.

**Correction to my own first attempt at step 10.** The first starved-fingerprint probe pointed
`--root` at a new directory under `docs/qa/evidence/`, which is *inside* this checkout's repository.
`git write-tree` therefore succeeded from the enclosing repo and the leg produced a MISS, not
`NOCACHE`. That probe was invalid, not a product divergence. It was redone against a directory under
`/tmp` outside every repository (`git rev-parse --show-toplevel` → `fatal: not a git repository`),
which produced `NOCACHE`, ran the command, returned its exit status, and left the root empty
(`refusal/step10-redo.log`).

## Git visibility — `CFG-keep-the-gate-cache-out-of-git`

Walked in the source checkout as the Workflow adopter. `.gitignore:23` carries `.gate-cache/`. A gate
run through the cache under a fresh label wrote `3dcd9b58….json` and its log into `.gate-cache/`;
Git then reported nothing through four independent read paths: `git status --porcelain` (empty),
`git status --porcelain -uall` (empty), `git ls-files` (no cache file tracked — the only match is
this cycle's scenario document), and `git check-ignore -v .gate-cache` → `.gitignore:23`.
`git status --ignored --porcelain` lists `!! .gate-cache/`, confirming Git sees the directory and
classifies it as ignored rather than simply missing it.

Package: `bun pm pack --dry-run` lists 522 entries; none is under `.gate-cache/` and none is
fingerprint-named. Clean-clone canary from the local repository into a disposable `/tmp` path (no
remote contacted): `.gate-cache/` absent, clone status clean.

## Legs not walked

- **Interrupted command** (`QAS-run-the-gate-when-the-cache-cannot-vouch`, charter edge). One
  attempt: a 20-second gate started through the wrapper, `SIGINT` sent to the process group after
  3 s. The signal never reached the run — the gate printed "slow gate end", the wrapper exited 0 and
  wrote a normal passing record. A non-interactive background signal is not the operator's
  foreground Ctrl-C, so the CLI adapter cannot deliver this leg deterministically. The leg was not
  simulated and no verdict was inferred from it (`refusal/interrupt.log`). It is a limitation of the
  adapter, not an unreachable product surface, so it does not put the scenario in `blocked-verify`.
- **Torn / concurrent record write.** Internal durability rule, observable only mid-write. Not
  reachable from a CLI/manual adapter; remains a technical-verification surface.
- **Adoption.** Out of scope for this delivery by packet instruction and by the spec's "Tool only in
  this delivery" wiring decision.

## Findings

No product defect was found. No bug was filed; nothing here deduplicates against an existing record
in `docs/qa/bugs/`.

Two durable-artifact problems are recorded for the next planning cycle, neither a product defect:

1. **Verdicts committed without a report.** At `8461180`, both `QAS-` scenarios were committed at
   `qa_status: pass` citing `last_report: docs/qa/reports/2026-09-01-gate-result-cache.md`, a file
   that does not exist in the repository. This session re-derived every verdict from its own
   evidence and repointed `evidence` and `last_report` at this report.
2. **Stale charter and journey references.** Both charters carry `GRC-06` rows and a P2 the current
   spec does not contain, and `J-run-project-gates` step 6 names
   `.agents/skills/tlc-spec-driven/references/implement.md`, a path absent from this repository (the
   skill is installed as `workflow-spec-driven`). Charters are immutable once written and the journey
   is a `qa-plan` artifact, so both are reported rather than edited here.

## Final gate result

Command, run after the three scenario edits and this report were written:

```
python3 tools/gate_cache.py run --gate full -- bun run test:all
```

Outcome: `MISS gate=full fingerprint=c51a6d2c… status=pass`, **exit 0**, at 18:58:17 UTC under load
average 11.82. The tree had changed, so the cache correctly refused to reuse `da698c7e…` and the
suite actually ran. Nothing reported a failure; the flake hazard on
`tools/shared/tests/security-skills-installation.test.ts` and
`tools/test_deep_review_token_metrics.py` did not materialise, so no rerun was needed. Record read
back independently: `status: "pass"`, `exit_code: 0`, tree `4df88a41…`.

Evidence line: `docs/qa/evidence/2026-09-01-gate-cache-tool/final-gate.log`.

## Residue

Source checkout carries only this report and the three scenario edits. Both disposable repositories,
the `/tmp` non-repo root, and the clean clone live under (or were removed from) the ignored evidence
path; no disposable target remains outside it.
