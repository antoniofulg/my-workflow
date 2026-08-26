# CH-confirm-parallel-execution-fallback-2026-08-24

- **Date:** 2026-08-24
- **Time-box:** 25 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-configure-feature-workflow`](../journeys/J-configure-feature-workflow.md) → [`J-execute-parallel-slices`](../journeys/J-execute-parallel-slices.md)
- **Tour:** Configuration, serial fallback, and unchanged-delivery canary
- **Public entry point:** `.my-workflow.toml` → `workflow_config.py` → `parallel_plan.py` → `parallel_execute.py start|status`
- **Declared adapter:** CLI/manual in checkout-local disposable Git repositories
- **Scenarios:** `CFG-freeze-feature-workflow`, `CFG-fallback-unproven-parallel-execution`, `CFG-plan-parallel-slice-dispatch`, `QAS-bound-verifier-remediation-per-blocker`
- **Adjacent canary:** `CFG-plan-parallel-slice-dispatch`

## Mission

Confirm that configuration and capability uncertainty never create a parallel effect, and that the
executor addition preserves deterministic planning, sequential slice tasks, every verification
stage, and blocker-scoped unattended remediation.

## Expected observable

Disabled, unsupported, incomplete-resource, and unprovided-resource cases emit their exact serial
reason with zero worktree/worker/event/Git/resource effects; the existing planner contract remains
deterministic; and distinct verifier blocker fingerprints progress independently while the same
fingerprint halts only on its third failed remediation.

## Planned probes

- Resolve absent, disabled, safe, and full modes and inspect the frozen optional provider path.
- Start disabled mode and one forced unsupported-capability fixture; compare status and Git state before and after.
- Plan missing/ambiguous resources and a runtime/port/database lane without a configured provider; require serial fallback.
- Rewalk deterministic ready/blocked/checkpoint output and inspect the installed policy for unchanged TLC, Verifier, grouped review, QA, and full-gate stages.
- Drive the public convergence ledger with two distinct fingerprints and one reopened fingerprint; confirm independent counts and the third-failure halt.
- Re-read status from a fresh process and confirm no external receipt or disposable worktree was created by fallback cases.

Do not create a fake product resource provider. This repository's correct observable for
resource-bearing lanes is serialization.

## Terminal outcome

`CFG-fallback-unproven-parallel-execution` passed: R18 proved disabled and unsupported capability
fallback with zero effects; R19 proved missing provider fallback with zero effects and residue.
`QAS-bound-verifier-remediation-per-blocker` passed in R19: independent closed fingerprints stayed
unchanged and a distinct fingerprint halted on failed remediation 3. The real worker lifecycle was
not re-run in this charter and remains `blocked-verify` in its execution charter.
