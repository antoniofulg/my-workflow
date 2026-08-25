# Parallel Deep Review QA — 2026-08-25

- **Scope:** `origin/main..5252fae` on `feat/parallel-deep-review`
- **Phase:** QA Execute
- **Adapter:** CLI/manual through `build_manifest.py`, `run_jobs.py`, `scripts/adopt.py`, and `npm pack --dry-run --json`
- **Environment:** isolated checkout-local disposable Git repositories and targets; fake provider derived from `tools/test_deep_review_token_metrics.py`; no network or live model provider
- **Technical gate before QA:** PASS — 12/12 acceptance criteria, 26/26 discrimination mutations killed, 146 canonical tests passed
- **Raw evidence:** `docs/qa/evidence/2026-08-25-parallel-deep-review/`

## Matrix

| Charter | Scenario | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `CH-run-bounded-parallel-deep-review-2026-08-25` | `QAS-run-bounded-parallel-deep-review` | pass | Reloaded manifests, status/blocker ledgers, validate-only output, call/peak state, and deterministic rendered artifacts | `qa-summary.json`; `deterministic-render-test.log` |
| `CH-run-bounded-parallel-deep-review-2026-08-25` | `QAS-observe-serialized-deep-review-metrics` | pass | Reloaded metrics ledgers after overlapping full run, narrowed scope, full resume, and telemetry-free run | `qa-summary.json`; `metrics.log`; `metrics-partial.log`; `metrics-full-resume.log`; `metrics-unavailable.log` |
| `CH-adopt-parallel-deep-review-canary-2026-08-25` | `ADP-adopt-workflow-safely` | pass | Reloaded package JSON, installed bytes, lock row, printed output, and consumer sentinel after second adoption | `adoption-summary.json`; `npm-pack.log`; `adopt-first.log`; `adopt-second.log` |

## Session results

### Bounded runner and metrics charter — PASS

`qa_walk.py` entered through the public `build_manifest.py` and `run_jobs.py` CLIs in a disposable
Git repository. It produced **26 passing checks**:

- default `3`, YAML `5`, CLI override `2`, and valid boundaries `1` and `6` persisted after JSON reload;
- YAML `true`, `false`, `0`, `7`, quoted `"3"`, and `1.5` each exited `2` before any dispatch path existed;
- peak activity was exactly `1/1`, `6/6`, and `2/6` for serial, full-cap, and fewer-pending probes;
- run status and validate-only rows stayed in manifest order; a focused public-runner pipeline test
  independently proved equal findings and rendered report under forward versus inverted completion;
- retry used attempts `[2,1,1,1,1]` with peak `3`; ordinary failure returned `1` while all siblings ran;
- provider block started only two jobs, finished the active sibling, stopped refill, exited `2`,
  listed `job-1`, `job-3`, and `job-4` unfinished, then resumed only those three while preserving
  `job-2`; multiple blocks retained `BLOCK-A` and `job-1` as the first reason;
- source mutation after two jobs started allowed both to finish, then exited `3` with source-drift
  output and no accepted valid review;
- four overlapping metric completions produced checkpoints `1,2,3,4`, cumulative `40` tokens, no
  `job` attribution, `running` after `--only job-1 job-2`, and `complete` with the same cumulative
  total after full resume; absent telemetry kept both jobs passing with `metrics: unavailable`;
- legacy `--workers 2` exited `2` without output dispatch.

Initial fixture preparation needed clean reruns before the charter result: invalid config was
corrected to expect argparse exit `2`, the multiple-block fixture added its two explicit
`--block-on` values, and the telemetry fixture created its parent directory. These were evidence
adapter setup errors, not product divergences; the final clean walk passed all 26 checks.

### Adoption/package canary — PASS

`adoption_canary.py` produced **15 passing checks** through `npm pack --dry-run --json`, two public
`scripts/adopt.py` invocations, installed-file reloads, and the deterministic rendering canary:

- package membership included the Deep Review skill, orchestration/runtime references, manifest
  builder, and bounded runner;
- installed copies matched all five tracked source files byte-for-byte;
- installed contracts contained `--concurrency`, `.deep-review.yaml`, `1 through 6`,
  `run-blocker.json`, and cumulative metrics language;
- tracked `skills-lock.json` retained the Deep Review source path and a 64-character content hash;
- re-adoption preserved a consumer-owned sentinel byte-for-byte;
- both adoptions only printed the external security installer command; neither invoked it;
- forward/inverted completion produced deterministic status, findings, and rendered report.

### Edge probes and lenses

Ten edge probes passed: fewer pending jobs, serial boundary, max boundary, six invalid config
shapes, ordinary failure continuation, multiple-block first reason, `--only` partial metrics,
telemetry unavailable, existing-valid output reuse, legacy option rejection, and source drift.
Comprehension and language were checked through CLI help/errors and installed contract wording;
recovery through retry/block/resume; trust through pre-dispatch refusal, source freeze, cumulative
metrics, and consumer-byte preservation; speed through measured overlap/peak. Accessibility and
browser reload do not apply to this CLI-only repository.

No product defect was found. No bug record was created.

## Limitations

No live-model or automated agent-execution harness exists. External runner behavior is reachable
through the fake-provider CLI adapter. Native, Workflow, and generic Agent host scheduling can be
inspected as installed contracts but cannot receive a live-engine verdict. This repository has no
browser, API, mobile, auth, server, or production-health surface.

The adapter does not reproduce live provider quota timing or host scheduler internals. It does
observe the public external runner's process overlap, exit codes, persisted artifacts, and resume
behavior. Raw evidence scripts and logs are ignored and checkout-local. Disposable Git/adoption
targets were moved to system Trash after evidence capture; source residue is limited to the planned
durable QA report/scenario records and pre-existing QA Plan changes.

## Final gate

- `npm test` — 7 files passed; 108 tests passed, 0 failed, 0 skipped.
- `python3 tools/test_deep_review_contract.py` — 10 passed, 0 failed, 0 skipped.
- `python3 tools/test_deep_review_token_metrics.py` — 28 passed, 0 failed, 0 skipped.
- Aggregate final gate: **146 passed, 0 failed, 0 skipped**.

## Verdict

**PASS** — both charters completed, all 41 QA checks passed, all 12 feature acceptance criteria
were exercised through the reachable public CLI/package/adoption surfaces, and the final gate is
green. Native/Workflow/generic Agent live scheduling remains an explicit profile limitation, not a
passing live-host claim.
