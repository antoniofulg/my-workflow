# Legacy Adoption Resolution QA Execute

**Date:** 2026-08-31
**Candidate:** `827d629f427020c8a1940a47cf9570e9a1adf808`
**Adapter:** CLI/manual through `scripts/adopt.py` with independent Git and filesystem reads
**Environment:** checkout-local disposable Git targets; Python 3; no network or live Orca
**Opening gate:** integrated technical validation at `.specs/features/legacy-adoption-resolution/validation.md` records exit 0 for `npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check origin/main...HEAD`
**Raw evidence:** `docs/qa/evidence/2026-08-31-legacy-adoption-resolution/`

## Matrix

| Charter | Scenario | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `CH-resolve-legacy-adoption-conflicts-2026-08-31` | `ADP-resolve-legacy-adoption-conflicts` | pass | Reloaded snapshots, Git `HEAD`/index, manifest, instruction bytes, status JSON, external referents, and sentinel absence confirmed the result. | `summary.json`; `commands.jsonl`; `plan-*`; `resolve-*`; `status-after-resolve.*`; `apply-after-resolve.*`; `edge-*` |
| Adjacent normal-command canary | `ADP-layered-workflow-adoption` | pass | Fresh-target snapshots and status JSON confirmed read-only plan, successful apply, clean status, reversible drift, and restored clean status. | `summary.json`; `canary-*` |

## Session

The exact public adapter path was `python3 scripts/adopt.py <plan|resolve|apply|status> TARGET ...`.
The primary target was
`docs/qa/evidence/2026-08-31-legacy-adoption-resolution/targets/legacy;touch UNEXPECTED_PROCESS_MARKER`;
all argument vectors, exits, and working directories are recorded in `commands.jsonl`.

Two text plans and two JSON plans for `parallel --skip-agents` each found exactly
`tools/qa_parallel_pilot.py` and `tools/resource_lock.py` as conflicts. Repeated output was stable,
JSON stdout parsed without diagnostics, and an independent recursive byte/mode/symlink snapshot was
unchanged.

An incomplete replacement exited 1 and reported both current conflicts without writes. Extra,
duplicate, absolute, escaping, doubled-separator, dot-separator, and managed-block authorizations
each exited 2 without writes or a manifest. Exact sorted authorization through
`resolve --layers parallel --replace tools/qa_parallel_pilot.py --replace tools/resource_lock.py
--skip-agents --json` exited 0; both actions were `replace`, conflicts were empty, and the reloaded
manifest had schema 1 with `core,parallel`.

Independent reads confirmed `AGENTS.md` and `CLAUDE.md` stayed byte-identical, target `HEAD` stayed
at the committed legacy baseline, the Git index had no staged diff, adoption `status --json` exited
0 with `clean`, and no helper, backup, transaction, temp, or process-marker effect appeared. A
second `resolve` exited 2 unchanged because the manifest existed. Normal `apply parallel
--skip-agents --json` exited 0 and was byte-idempotent.

The adjacent fresh target used normal `plan`, `apply`, and `status` commands. Plan exited 0 without
writes, apply exited 0, and status reloaded clean. Appending reversible drift to
`.agents/skills/autonomous/SKILL.md` made status exit 1 without writes; restoring the original bytes
returned status to exit 0.

## Edge probes and lenses

- Authorization edges passed: incomplete, extra, duplicate, absolute, escaping,
  doubled-separator, dot-separator, and managed-block replacement values.
- Git/trust edges passed: non-Git, missing `HEAD`, dirty, manifest-backed, replaceable-leaf symlink,
  `tools` parent symlink, and `.claude` parent symlink. Each exited 2 with unchanged target; symlink
  probes also left external referents unchanged.
- Comprehension/language: text output named conflicts and JSON remained machine-parseable with
  diagnostics isolated to stderr.
- Recovery/trust: committed legacy bytes remained recoverable from unchanged `HEAD`; refused paths
  had exact snapshot equality; successful publication left no staged index state.
- Speed/accessibility: the whole local CLI walk completed without a server, package installation,
  network, or interactive step. No visual UI exists for an accessibility walk.

## Limitations and boundaries

No browser, API, mobile, auth, server, or production-health surface exists. Injected publication
failure, hostile process races, exact manifest-last timing, and direct-argv implementation inspection
remain technical-only; public QA observed their no-write/no-unexpected-effect boundary. No live
Orca, network, external installer, active consumer checkout, or non-disposable target was used.

Before the verdict-bearing run, the disposable evidence harness aborted on two checker assumptions
(pre-existing manifest absence and manifest ownership spelling). Both were evidence-code errors,
not product divergences; the completed run rebuilt every target from a clean directory.

## Cleanup and residue

The harness removed all 12 checkout-owned disposable target/referent directories. `summary.json`
records `disposable_targets_remaining: false`, `marker_exists: false`, no unexpected transaction
residue, and source status limited to the planned durable QA report before status updates. No
process, lock, server, or external checkout was created or touched. The full gate's two run-owned
parallel-pilot residue directories (`c_dpmwaz` and `6_bl8ohp`) were removed after the gate; a process
scan and exact path checks then found zero session-owned residue. Older parallel-pilot residue with
pre-session timestamps was left untouched.

## Final gate

`npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check
origin/main...HEAD` exited 0. Bun reported 123 passed, 0 failed, and 1123 assertions across 8 files;
the adoption suite reported `ok (83 tests)` and every other tracked Python suite passed. Knowledge
reported 0 errors and 37 non-blocking harvest warnings. Diff check produced no output. Evidence:
`final-gate.txt`.
