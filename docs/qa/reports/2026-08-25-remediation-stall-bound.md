# QA Execute — remediation stall bound

- **Date:** 2026-08-25
- **Charter:** [`CH-remediation-stall-bound-2026-08-25`](../charters/CH-remediation-stall-bound-2026-08-25.md)
- **Persona:** Workflow adopter
- **Adapter:** CLI/manual through checkout-local disposable Git repositories, the documented `workflow_config.py` and `scripts/adopt.py` commands, plus independent TOML/JSON/filesystem/Git inspection
- **Environment:** macOS workstation; active checkout `/Users/antoniofulg/Projects/my-workflow-pr60-refresh`; branch `fix/stall-based-remediation-halt`; HEAD `cada159`; no server, browser, API, auth, live-model harness, networked installer, or remote service
- **Entry path:** `.my-workflow.toml.example` -> local `.my-workflow.toml` -> `.agents/skills/workflow-config/scripts/workflow_config.py` resolve/resume; `README.md` -> `scripts/adopt.py`
- **Preflight automated gate:** technical validation records `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py && git diff --check 70e447d..997ba25 && git diff --check` at exit 0 with 163 passed, 0 failed, 0 skipped
- **Final automated gate:** `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py && git diff --check` exited 0 at HEAD `cada159`: 108 Vitest + 18 registered adoption + 37 resolver = 163 passed, 0 failed, 0 skipped; diff check passed
- **Raw evidence:** `docs/qa/evidence/2026-08-25-remediation-stall-bound/`

## Matrix

| Scenario | Scope | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `CFG-resolve-deep-review-cadence` | Default, positive, zero, invalid, and balanced-cadence resolution | pass | Independent JSON reload found default `3`, positive `5`, zero `0`, large nonnegative `2147483647`, balanced groups `[[1,2,3],[4,5],[6,7]]`, and no remediation key in snapshots; five invalid families exited 2 before snapshot creation | [`summary.json`](../evidence/2026-08-25-remediation-stall-bound/summary.json) |
| `CFG-freeze-feature-workflow` | Snapshot exclusion and live-threshold resume with frozen route/model/effort/cadence | pass | Threshold changed `4` to `6`; reloaded snapshot stayed byte-identical at SHA-256 `06eb09a03d166f2393ca190677097817cbd85c9718e34a56b7d46ae5dfd315e2`, with exact route/model/effort/cadence and no remediation key | [`session.log`](../evidence/2026-08-25-remediation-stall-bound/session.log) |
| `ADP-adopt-workflow-safely` | Adjacent fresh/re-adoption canary for tracked example and consumer-owned local config | pass | Fresh adoption installed the tracked remediation example; re-adoption preserved customized local config SHA-256 `0f0c9861bdaf7315f85b6f06a4ff556b649a04a92854a38900a278d5f6faf09d`; installer command was printed but not run | [`summary.json`](../evidence/2026-08-25-remediation-stall-bound/summary.json) |

## Probe results

1. **PASS — documented setup and default.** A local clone at exact HEAD `cada159` used the public
   `--sync-agents` prerequisite, then resolved seven slices. Current JSON reported default `3` and
   balanced `grouped.3` groups; the independently reloaded snapshot had no remediation key.
2. **PASS — positive, zero, and no-persist.** Fresh feature slugs reported exact values `5` and `0`.
   Neither snapshot persisted remediation state.
3. **PASS — six edge probes.** A large nonnegative value `2147483647` resolved exactly without
   persistence. Negative, boolean, TOML float, string, and unknown-key inputs each exited `2`, named
   remediation in stderr, and created no workflow snapshot.
4. **PASS — live resume and frozen state.** One feature resolved at `4`, then resumed at `6` after
   changing only local remediation config. Route, model, effort, cadence, Git head, and exact
   snapshot bytes remained unchanged; current JSON alone carried the new threshold.
5. **PASS — adjacent adoption canary.** Fresh adoption installed the tracked example with the
   remediation table. Re-adoption preserved a consumer-customized `.my-workflow.toml`
   byte-for-byte. Both runs printed the separately authorized external-security installer command;
   neither invoked it.
6. **PASS — cleanup and final gate.** Fourteen independent checks passed. Checkout-owned runtime
   targets were removed. The final gate passed 163 checks with no failures or skips, and
   `git diff --check` passed.

One setup stall occurred before product assertions because the initial local clone lacked ignored
`.my-workflow.toml` and generated provider packets. The protocol's one clean retry used the
documented `--sync-agents` prerequisite and completed cleanly; both attempts remain in `session.log`.

## Debrief

Verdict: **PASS**. One charter and all three scenario rows reached their expected public
observables. No product defect, bug record, or Implementer handoff is required.

Limitations: the profile has no live-model or agent-execution harness, so `SRH-03`, `SRH-04`, and
`SRH-05` retain their technical-validation-only disposition. This repository has no browser, API,
mobile, auth, server, or production-health surface. No external security-skill installer, network
service, GitHub command, remote fetch, push, pull request, merge, or product edit ran. The CLI/manual
adapter cannot observe autonomous model behavior or hostile staged-file, process-race, and
interrupted-publication controls.
