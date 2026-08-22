# QA operational profile

This repository distributes an agent workflow, not a running application. Its public surfaces are
the adoption CLI, the installed agent-facing files, the repository documentation, and package
metadata. Command facts remain in the linked executable authorities.
For consuming projects, those authorities are their executable manifests or CI jobs.

## Public interfaces and area codes

| Area | Interface | Entry point | Authority |
| --- | --- | --- | --- |
| `ADP` | Adoption and external-skill CLI plus generated filesystem | `scripts/adopt.py`; `scripts/install_security_skills.py` with a disposable target | [README adoption contract](../../README.md#adopt-the-workflow), [`scripts/adopt.py`](../../scripts/adopt.py), [`scripts/install_security_skills.py`](../../scripts/install_security_skills.py) |
| `QAS` | Manual agent-file inspection | `.agents/skills/qa-plan/`, `.agents/skills/qa-execute/`, provider Verifier packets | [Skills contract](../../README.md#skills) |
| `DOC` | Documentation | `README.md` | [`README.md`](../../README.md) |
| `CFG` | Workflow configuration, generated state, and Git visibility | `.my-workflow.toml`; `.agents/skills/workflow-config/scripts/workflow_config.py`; `.gitignore`; `.specs/` | [README configuration contract](../../README.md#adopt-the-workflow), [`workflow-config` skill](../../.agents/skills/workflow-config/SKILL.md), [artifact lifecycle](../guidelines/ARTIFACT-LIFECYCLE.md) |
| `REL` | Package metadata | `package.json`, `package-lock.json` | [`package.json`](../../package.json) |

No browser, API, or mobile surface exists in this repository.

## Runner and adapter

- Existing runner or adapter: CLI/manual, using the public workflow resolver, adoption script, and
  filesystem inspection.
- Manifest or CI authority: [`package.json`](../../package.json) owns the structural gate;
  [`scripts/test_adopt.py`](../../scripts/test_adopt.py) owns the disposable adoption smoke path.
- Exact path used by `qa-execute`: invoke the command documented by the
  [`workflow-config` skill](../../.agents/skills/workflow-config/SKILL.md) inside a checkout-local
  disposable Git repository; invoke [`scripts/adopt.py`](../../scripts/adopt.py) against a separate
  checkout-local disposable target; inspect its printed external-skill command before invoking
  [`scripts/install_security_skills.py`](../../scripts/install_security_skills.py) only when the
  QA packet explicitly authorizes network access and target writes; then inspect the targets and
  repository files named by each charter.
- Installed QA tooling discovered: Vitest is declared in [`package.json`](../../package.json) for
  structural checks; it is not a real-user runner. Python standard-library checks live in
  [`scripts/test_adopt.py`](../../scripts/test_adopt.py).

The workflow does not install a framework or invent commands when a runner is absent.

## Build, start, and health

- Build authority: none; this package has no build script or runtime artifact.
- Production-parity start authority: not applicable; no server or application process exists.
- Health signal: resolution exits successfully with matching JSON stdout and feature snapshot;
  adoption exits successfully and its disposable target contains the expected workflow assets.
- Environment and checkout isolation: each QA run uses a target directory owned by the active
  checkout; [`scripts/test_adopt.py`](../../scripts/test_adopt.py) demonstrates isolated temporary
  targets and cleanup.
- Automated gate authority: the `test` script in [`package.json`](../../package.json).

## Authentication and test data

- Test identity or session setup: none; adoption and repository inspection require no identity.
- Fixtures or seed authority: disposable empty and pre-populated directories created by
  [`scripts/test_adopt.py`](../../scripts/test_adopt.py).
- Cleanup and teardown authority: remove only the disposable target created for the active QA run;
  the smoke test owns its temporary-directory teardown.
- Residue check: source checkout status remains unchanged apart from planned durable QA artifacts,
  and no disposable target remains.

## Evidence and limitations

- Raw evidence path: `docs/qa/evidence/` (disposable and ignored by this repository).
- Durable reports and statuses: `docs/qa/`.
- Known limitations or unreachable surfaces: no automated agent-execution harness; skill behavior
  is reachable through the installed contracts and provider packets, while live model behavior
  remains a manual observation. No browser, API, mobile, auth, server, or production health path
  exists. The CLI/manual adapter can observe refusal, success, target bytes, lock metadata, and
  installed links, but hostile staged-file, process-race, and interrupted-publication controls
  remain technical-verification surfaces.
- External dependencies requiring a human: installing the three pinned external security skills is
  an explicit, networked authorization step printed by [`scripts/adopt.py`](../../scripts/adopt.py);
  QA must not run it implicitly. The adapter requires Python 3 for adoption and Node/npm for the
  workflow gates, with network access only when the QA packet authorizes the installer command.

`qa-plan` reads this profile before mapping promises. `qa-execute` uses the CLI/manual adapter,
records its exact target and evidence, and leaves product fixes to an Implementer.
