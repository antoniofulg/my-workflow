# QA operational profile

This repository distributes an agent workflow, not a running application. Its public surfaces are
the adoption CLI, the installed agent-facing files, the repository documentation, and package
metadata. Command facts remain in the linked executable authorities.
For consuming projects, those authorities are their executable manifests or CI jobs.

## Public interfaces and area codes

| Area | Interface | Entry point | Authority |
| --- | --- | --- | --- |
| `ADP` | Adoption and external-skill CLI plus generated filesystem | `scripts/adopt.py`; `scripts/install_security_skills.py` with a disposable target | [README adoption contract](../../README.md#adopt-the-workflow), [`scripts/adopt.py`](../../scripts/adopt.py), [`scripts/install_security_skills.py`](../../scripts/install_security_skills.py) |
| `QAS` | Manual agent-file inspection, checkout-local CLI recipes, and Orca-backed workflow execution | `.agents/skills/qa-plan/`, `.agents/skills/qa-execute/`, `.agents/skills/autonomous/scripts/parallel_execute.py`, `tools/gate_cache.py`, `.agents/skills/deep-review/references/publish-github.md`, provider Verifier packets | [Skills contract](../../README.md#skills), [parallel executor contract](../../.agents/skills/autonomous/references/parallelization.md), [Deep Review publication recipe](../../.agents/skills/deep-review/references/publish-github.md) |
| `DOC` | Documentation | `README.md` | [`README.md`](../../README.md) |
| `CFG` | Workflow configuration, generated state, and Git visibility | `.my-workflow.toml.example`; `.my-workflow.toml`; `templates/agents/`; `.agents/skills/workflow-config/scripts/workflow_config.py`; `.gitignore`; `.specs/` | [README configuration contract](../../README.md#adopt-the-workflow), [`workflow-config` skill](../../.agents/skills/workflow-config/SKILL.md), [artifact lifecycle](../guidelines/ARTIFACT-LIFECYCLE.md) |
| `WFL` | Cross-provider workflow handoff | `docs/workflow/ai-memory.md`; `scripts/ai-memory.zsh`; Claude Code, Codex, and Cursor lifecycle hooks | [ai-memory handoff contract](../workflow/ai-memory.md), [`scripts/ai-memory.zsh`](../../scripts/ai-memory.zsh) |
| `REL` | Package metadata | `package.json`, `bun.lock` | [`package.json`](../../package.json) |

No browser, API, or mobile surface exists in this repository.

## Runner and adapter

- Existing runner or adapter: CLI/manual, using the public workflow resolver, adoption script,
  parallel executor, assisted pointer probe, and filesystem inspection. The parallel-slice journey
  uses the installed Orca CLI only after its `orchestration.contract.v1` capability is proven; the
  disposable fixture and lifecycle oracle are owned by
  [`tools/qa_parallel_pilot.py`](../../tools/qa_parallel_pilot.py), while
  [`tools/orca_assisted_probe.py`](../../tools/orca_assisted_probe.py) is the shipped pointer-only
  lifecycle boundary. Deep Review publication recipes
  use a checkout-local fake `gh` that logs arguments;
  [`tools/test_deep_review_contract.py`](../../tools/test_deep_review_contract.py) owns that
  no-network adapter.
- Manifest or CI authority: [`package.json`](../../package.json) owns the structural gate;
  [`scripts/test_adopt.py`](../../scripts/test_adopt.py) owns the disposable adoption smoke path.
- Exact path used by `qa-execute`: invoke the command documented by the
  [`workflow-config` skill](../../.agents/skills/workflow-config/SKILL.md) inside a checkout-local
  disposable Git repository; invoke [`scripts/adopt.py`](../../scripts/adopt.py) against a separate
  checkout-local disposable target; inspect package membership with `bun pm pack --dry-run`
  from the active checkout, and create any clean-clone canary from the active local repository into
  a checkout-owned disposable path without fetching a remote; inspect the adoption script's printed
  external-skill command before invoking
  [`scripts/install_security_skills.py`](../../scripts/install_security_skills.py) only when the
  QA packet explicitly authorizes network access and target writes; then inspect the targets and
  repository files named by each charter. For Deep Review publication, extract the public recipe
  and execute it with the checkout-local fake `gh` pattern owned by
  [`tools/test_deep_review_contract.py`](../../tools/test_deep_review_contract.py); never contact
  GitHub during QA. For parallel execution, use the setup, dry-run, public executor
  `start`/`status`/`resume`, lifecycle-check, and cleanup sequence in
  [the E2E-001 handoff](../../.specs/features/parallel-slice-executor/qa-pilot.md); use the
  assisted probe's `dispatch`, `inspect`, and `cleanup` commands with fake providers for offline
  proof; do not replace a
  serial fallback or incomplete lifecycle with a simulated success.
- Installed QA tooling discovered: Bun's `bun:test` is declared by [`package.json`](../../package.json)
  for structural checks; it is not a real-user runner. Python standard-library checks live in
  [`scripts/test_adopt.py`](../../scripts/test_adopt.py).

The workflow does not install a framework or invent commands when a runner is absent.

## Build, start, and health

- Build authority: none; this package has no build script or runtime artifact.
- Production-parity start authority: not applicable; no server or application process exists.
- Health signal: resolution exits successfully with matching JSON stdout and feature snapshot;
  adoption exits successfully and its disposable target contains the expected workflow assets;
  the parallel pilot dry-run validates exactly two resource-free lanes, and its lifecycle-check
  accepts only two correlated terminal read-before-ack-before-release receipts.
- Environment and checkout isolation: each QA run uses a target directory owned by the active
  checkout; [`scripts/test_adopt.py`](../../scripts/test_adopt.py) demonstrates isolated temporary
  targets and cleanup.
- Automated gate authority: the `test` script in [`package.json`](../../package.json).

## Authentication and test data

- Test identity or session setup: none; adoption and repository inspection require no identity.
- Fixtures or seed authority: disposable empty and pre-populated directories created by
  [`scripts/test_adopt.py`](../../scripts/test_adopt.py), plus the two-lane resource-free Git fixture
  created by [`tools/qa_parallel_pilot.py`](../../tools/qa_parallel_pilot.py).
- Cleanup and teardown authority: remove only the disposable target created for the active QA run;
  adoption owns its temporary-directory teardown, while the parallel pilot's public cleanup
  requires its exact ownership attestation and completed lifecycle check.
- Residue check: source checkout status remains unchanged apart from planned durable QA artifacts,
  and no disposable target remains.

## Evidence and limitations

- Raw evidence path: `docs/qa/evidence/` (disposable and ignored by this repository).
- Durable reports and statuses: `docs/qa/`.
- Known limitations or unreachable surfaces: Orca can prove two resource-free worktrees and worker
  lifecycles concurrently, but this repository has no product runtime, port allocator, database, or
  configured consumer resource provider. Resource-bearing lanes therefore must serialize here;
  each consuming product must separately adopt and QA its provider. No browser, API, mobile, auth,
  server, or production health path exists. The CLI/manual adapter can observe refusal, success,
  target bytes, lifecycle receipts, lock metadata, and installed links, but hostile staged-file,
  process-race, exact Git checkpoint mutation, provider receipt spoofing, and interrupted-publication
  controls remain technical-verification surfaces.
- External dependencies requiring a human: installing the three pinned external security skills is
  an explicit, networked authorization step printed by [`scripts/adopt.py`](../../scripts/adopt.py);
  QA must not run it implicitly. The adapter requires Python 3 for adoption and Bun 1.4.x for the
  workflow gates, with network access only when the QA packet authorizes the installer command.

`qa-plan` reads this profile before mapping promises. `qa-execute` uses the CLI/manual adapter,
records its exact target and evidence, and leaves product fixes to an Implementer.

## Parallel-slice terminal QA index

Canonical terminal report: [`2026-08-25-parallel-slice-executor-final`](reports/2026-08-25-parallel-slice-executor-final.md).

| Area | Terminal state | Durable owner |
| --- | --- | --- |
| Configuration/planning | `pass` — frozen resolver, deterministic planner, and safe provider-free boundary | [`J-configure-feature-workflow`](journeys/J-configure-feature-workflow.md); [`CFG-freeze-feature-workflow`](scenarios/CFG-freeze-feature-workflow.md); [`CFG-plan-parallel-slice-dispatch`](scenarios/CFG-plan-parallel-slice-dispatch.md) |
| Fallback | `pass` — disabled, unsupported, and missing-provider paths produce zero effects/residue | [`CFG-fallback-unproven-parallel-execution`](scenarios/CFG-fallback-unproven-parallel-execution.md); [`R18`](reports/2026-08-25-parallel-slice-executor-r18.md); [`R19`](reports/2026-08-25-parallel-slice-executor-r19.md) |
| Convergence | `pass` — independent fingerprints; third failed remediation halts at 3 | [`QAS-bound-verifier-remediation-per-blocker`](scenarios/QAS-bound-verifier-remediation-per-blocker.md); [`R19`](reports/2026-08-25-parallel-slice-executor-r19.md) |
| Real Orca/Codex worker lifecycle | `blocked-verify` — v0.6.0 fresh safe retest reproduced external stop boundary; not pass/fail/untested | [`J-execute-parallel-slices`](journeys/J-execute-parallel-slices.md); [`QAS-run-resource-free-parallel-orca-slices`](scenarios/QAS-run-resource-free-parallel-orca-slices.md); [`v0.6.0 safe retest`](reports/2026-08-25-parallel-slice-executor-v060-safe-retest.md) |
| Completed-pilot cleanup | `blocked-verify` — fresh lifecycle never authorized; no automatic cleanup claim | [`QAS-clean-owned-parallel-slice-pilot`](scenarios/QAS-clean-owned-parallel-slice-pilot.md); [`BUG-20260824-parallel-pilot-cleanup-allows-incomplete-lifecycle`](bugs/BUG-20260824-parallel-pilot-cleanup-allows-incomplete-lifecycle.md) |

Open bug boundaries: [`BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree`](bugs/BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree.md)
and [`BUG-20260824-parallel-pilot-cleanup-allows-incomplete-lifecycle`](bugs/BUG-20260824-parallel-pilot-cleanup-allows-incomplete-lifecycle.md).
Product parsing/recovery/preflight root causes are technically fixed; live retests remain open and
blocked by Orca/Codex behavior. R14 user-takeover residue, R15/R17 live-terminal residue, and older
R8–R11 `identity_unproven` residue were later removed manually by the operator. That operator-forced
cleanup is recorded only as a physical baseline reset and is not automatic-cleanup evidence. The
fresh v0.6.0 retest retained its own exact A/T1 worktree and live terminal after the same external
boundary; no zero-residue claim exists for the real worker journey.
