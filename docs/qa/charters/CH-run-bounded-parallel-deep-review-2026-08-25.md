# CH-run-bounded-parallel-deep-review-2026-08-25

- **Date:** 2026-08-25
- **Scope:** `origin/main..5252fae` on `feat/parallel-deep-review`
- **Time-box:** 45 minutes
- **Persona:** Workflow operator
- **Journey:** [`J-run-deep-review`](../journeys/J-run-deep-review.md)
- **Tour:** Configuration, boundary, overlap, determinism, recovery, and metrics tour
- **Public entry point:** `.agents/skills/deep-review/SKILL.md` -> `build_manifest.py` -> `run_jobs.py`
- **Adapter candidate:** CLI/manual through the public Deep Review scripts and checkout-local fake provider pattern declared in [`docs/qa/README.md`](../README.md)
- **Scenarios:** `QAS-run-bounded-parallel-deep-review`, `QAS-observe-serialized-deep-review-metrics`

## Mission

Use a checkout-local disposable Git repository and isolated Deep Review output directories to
experience bounded reviewer scheduling through the documented public CLI. Resolve every
configuration source and boundary, prove actual overlap and its cap independently, invert reviewer
completion order, and walk provider block plus resume without losing valid outputs. Observe metrics
as a serial ledger canary while jobs overlap.

## Expected observable

The operator gets default concurrency `3`, repository and CLI overrides from `1` through `6`, clear
pre-dispatch rejection for invalid inputs and `--workers`, real overlap bounded by the resolved
value, manifest-ordered artifacts despite inverted completion, coherent blocked/resumed state, and
serialized cumulative metrics without per-job attribution.

## Criterion disposition ledger

| Requirement | Disposition | Canonical QA coverage |
| --- | --- | --- |
| `P1.1` | Public default configuration promise | `J-run-deep-review` -> `QAS-run-bounded-parallel-deep-review` |
| `P1.2` | Public repository YAML and persisted-manifest promise | `J-run-deep-review` -> `QAS-run-bounded-parallel-deep-review` |
| `P1.3` | Public CLI precedence and boundary promise | `J-run-deep-review` -> `QAS-run-bounded-parallel-deep-review` |
| `P1.4` | Public pre-dispatch rejection promise | `J-run-deep-review` -> `QAS-run-bounded-parallel-deep-review` |
| `P1.5` | Public bounded-overlap promise; reachable through external CLI runner, while live native/Workflow hosts remain a profile limitation | `J-run-deep-review` -> `QAS-run-bounded-parallel-deep-review` |
| `P1.6` | Public deterministic status/report promise under inverted completion | `J-run-deep-review` -> `QAS-run-bounded-parallel-deep-review` |
| `P2.1` | Public retry-within-slot promise | `J-run-deep-review` -> `QAS-run-bounded-parallel-deep-review` |
| `P2.2` | Public provider-block exit/ledger promise; reachable through external CLI runner, while live native/Workflow hosts remain a profile limitation | `J-run-deep-review` -> `QAS-run-bounded-parallel-deep-review` |
| `P2.3` | Public resume and valid-output preservation promise | `J-run-deep-review` -> `QAS-run-bounded-parallel-deep-review` |
| `P2.4` | Public source-drift exit and invalid-review promise | `J-run-deep-review` -> `QAS-run-bounded-parallel-deep-review` |
| `P2.5` | Public serialized cumulative metrics promise | `J-run-deep-review` -> `QAS-observe-serialized-deep-review-metrics` |
| `P2.6` | Public rejection of legacy `--workers` | `J-run-deep-review` -> `QAS-run-bounded-parallel-deep-review` |

## Planned probes

- Build manifests with no setting, `.deep-review.yaml`, and `--concurrency`; independently reload
  JSON and require precedence `CLI > YAML > 3`.
- Require both valid boundaries: `1` runs without overlap and `6` reaches six active jobs when at
  least six are pending. With fewer pending jobs, require peak activity equal to pending count.
- Against fresh output paths, try `0`, `7`, boolean, quoted integer, float, non-integer CLI input,
  and `--workers`; require nonzero exit, precise rejection, and no job dispatch evidence.
- Use delayed fixture jobs at resolved `3` and `6`; independently track active and peak counts,
  require actual overlap, and require peak `min(concurrency, pending)`.
- Complete jobs in forward and inverted schedules. Compare run status, validate-only status,
  findings, and report ordering after independent reload; require manifest order and equal canonical
  output.
- Make one job retry while siblings continue; require two attempts for that job, one worker slot,
  and bounded sibling overlap.
- Trigger a provider block while sibling attempts are active; require no refill, active completion,
  exit `2`, first block reason, and every unfinished job in `run-blocker.json`. Re-run after clearing
  the fixture block; require valid outputs unchanged and only missing, blocked, or invalid jobs run.
- Change a selected source during active work; require active jobs to finish, exit `3`, and no valid
  rendered review.
- With checkout-local compatible telemetry, require serialized cumulative checkpoint numbers,
  absence of any job attribution, `running` after a narrowed `--only` scope, and final totals only
  after full completion. Repeat without telemetry and require unchanged execution/result semantics.
- Preserve ordinary-failure sibling continuation, multiple-block first-reason, and old-valid-output
  reuse as edge probes.
- Remove only checkout-owned disposable targets. Source residue must be limited to planned durable
  QA records and ignored raw evidence.

## QA Execute handoff

Start a fresh Verifier session with `phase: qa-execute`. Read `docs/qa/README.md`, invoke canonical
`qa-execute`, and use its CLI/manual adapter at HEAD `5252fae`. Work inside a checkout-local
disposable Git repository and separate output directories. Use the documented manifest and runner
entry points exactly:

```bash
python3 .agents/skills/deep-review/scripts/build_manifest.py \
  --out <checkout-owned-out> --base HEAD^ [--concurrency N]

python3 .agents/skills/deep-review/scripts/run_jobs.py \
  --out <checkout-owned-out> --jobs-file <checkout-owned-jobs.json> \
  --command "<checkout-owned-fake-provider> {prompt} {output} {label}"

python3 .agents/skills/deep-review/scripts/run_jobs.py \
  --out <checkout-owned-out> --jobs-file <checkout-owned-jobs.json> --validate-only
```

Derive the fake-provider behavior from the existing checkout-local adapter pattern owned by
`tools/test_deep_review_token_metrics.py`; do not invoke `compozy`, a live model provider, or any
remote service. Use `.deep-review.yaml` only inside the disposable repository. Store raw evidence
under `docs/qa/evidence/2026-08-25-parallel-deep-review/`, write a new durable report at
`docs/qa/reports/2026-08-25-parallel-deep-review.md`, then update only scenario verdict fields
supported by observed public-interface evidence.

Limitation: the profile has no live-model or automated agent-execution harness. The external runner
is reachable with the fake provider; native, Workflow, and generic Agent scheduling can only be
inspected as installed contracts and must not receive a live-behavior pass from that inspection.
This repository has no browser, API, mobile, auth, server, or production-health surface.

End before product remediation. A confirmed product defect returns to an Implementer and requires a
fresh Verifier after the fix.
