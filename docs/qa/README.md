# QA operational profile

This repository distributes an agent workflow, not a running application. Its public surfaces are
the adoption CLI, the installed agent-facing files, the repository documentation, and package
metadata. Command facts remain in the linked executable authorities.
For consuming projects, those authorities are their executable manifests or CI jobs.

## Public interfaces and area codes

| Area | Interface | Entry point | Authority |
| --- | --- | --- | --- |
| `ADP` | CLI and generated filesystem | `scripts/adopt.py` with a disposable target | [README adoption contract](../../README.md#adopt-the-workflow), [`scripts/adopt.py`](../../scripts/adopt.py) |
| `QAS` | Manual agent-file inspection | `.agents/skills/qa-plan/`, `.agents/skills/qa-execute/`, provider Verifier packets | [Skills contract](../../README.md#skills) |
| `DOC` | Documentation | `README.md` | [`README.md`](../../README.md) |
| `CFG` | Git-visible workflow configuration | `.gitignore`, `.specs/`, adopted target files | [Artifact lifecycle](../guidelines/ARTIFACT-LIFECYCLE.md) |
| `REL` | Package metadata | `package.json`, `package-lock.json` | [`package.json`](../../package.json) |

No browser, API, or mobile surface exists in this repository.

## Runner and adapter

- Existing runner or adapter: CLI/manual, using the public adoption script and filesystem inspection.
- Manifest or CI authority: [`package.json`](../../package.json) owns the structural gate;
  [`scripts/test_adopt.py`](../../scripts/test_adopt.py) owns the disposable adoption smoke path.
- Exact path used by `qa-execute`: invoke [`scripts/adopt.py`](../../scripts/adopt.py) against a
  checkout-local disposable target, then inspect that target and the repository files named by each
  charter.
- Installed QA tooling discovered: Vitest is declared in [`package.json`](../../package.json) for
  structural checks; it is not a real-user runner. Python standard-library checks live in
  [`scripts/test_adopt.py`](../../scripts/test_adopt.py).

The workflow does not install a framework or invent commands when a runner is absent.

## Build, start, and health

- Build authority: none; this package has no build script or runtime artifact.
- Production-parity start authority: not applicable; no server or application process exists.
- Health signal: adoption exits successfully and the disposable target contains the expected
  workflow assets; the smoke-test assertions define those assets.
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
  exists.
- External dependencies requiring a human: none for the planned CLI/manual journeys.

`qa-plan` reads this profile before mapping promises. `qa-execute` uses the CLI/manual adapter,
records its exact target and evidence, and leaves product fixes to an Implementer.
