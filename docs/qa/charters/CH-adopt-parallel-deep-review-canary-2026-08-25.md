# CH-adopt-parallel-deep-review-canary-2026-08-25

- **Date:** 2026-08-25
- **Scope:** `origin/main..5252fae` on `feat/parallel-deep-review`
- **Time-box:** 15 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Installed Deep Review concurrency contract canary
- **Public entry point:** `README.md` -> `scripts/adopt.py`; package membership through `npm pack --dry-run --json`
- **Adapter candidate:** CLI/manual adoption and package inspection declared in [`docs/qa/README.md`](../README.md)
- **Scenarios:** `ADP-adopt-workflow-safely` (retained adjacent canary)

## Mission

Confirm the changed Deep Review skill, references, and bounded runner travel through the existing
adoption and package surfaces without replacing consumer-owned state. This is an adjacent canary;
do not reset its retained verdict unless observation invalidates it.

## Expected observable

A disposable adopted target receives the current bounded-concurrency Deep Review files and lock
metadata, package inspection includes their source paths, re-adoption preserves consumer-owned
state, and no external security installer or remote service runs.

## Planned probes

- Run `npm pack --dry-run --json` from the active checkout and independently inspect membership for
  the Deep Review skill, orchestration/runtime references, manifest builder, and bounded runner.
- Adopt into a separate checkout-local disposable target with `scripts/adopt.py`.
- Compare installed Deep Review files and `skills-lock.json` metadata against active tracked sources;
  require the public `--concurrency`, YAML precedence, `1..6` bounds, bounded dispatch, deterministic
  ordering, provider-block, resume, and serialized-metrics language.
- Modify a consumer-owned local file, re-adopt, and require its bytes unchanged.
- Confirm adoption only prints the external-security installer command; do not invoke it.
- Remove only checkout-owned disposable targets and record source-checkout residue.

## QA Execute handoff

Execute this canary in the same fresh `qa-execute` session as
`CH-run-bounded-parallel-deep-review-2026-08-25`, but through the profile's separate adoption and
package paths:

```bash
npm pack --dry-run --json
python3 scripts/adopt.py <separate-checkout-owned-target>
```

Append evidence to `docs/qa/evidence/2026-08-25-parallel-deep-review/` and results to
`docs/qa/reports/2026-08-25-parallel-deep-review.md`. Do not reset `ADP-adopt-workflow-safely`
before execution; update it only if public-interface evidence changes its retained verdict. Do not
install tools, invoke the printed external-security installer, contact a remote, or change product
code.
