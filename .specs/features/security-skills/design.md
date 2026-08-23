# External Security Skills Design

**Spec**: `.specs/features/security-skills/spec.md`
**Status**: Approved

## Architecture Overview

`adopt.py` continues copying bundled workflow assets, then prints the project-local installer command. The installer validates the lock, acquires a per-target lock, installs into staging through the pinned external CLI, verifies exact tree hashes and publishes only the three managed skills. Failure restores the original managed paths and lock.

## Code Reuse Analysis

| Component | Location | How to Use |
| --- | --- | --- |
| Current adoption flow | `scripts/adopt.py` | Add output only; preserve every current copy and validation path |
| Legacy hardened installer | `feat/security-skills:scripts/install_security_skills.py` | Port the final implementation onto current `main` |
| Current lock | `skills-lock.json` | Merge three external entries without replacing bundled entries |
| Canonical adoption tests | `scripts/test_adopt.py` | Add cases; never transplant the stale suite wholesale |

## Components

### Security skill installer

- **Purpose**: Authorize, stage, verify and publish pinned external skills.
- **Location**: `scripts/install_security_skills.py`
- **Interface**: `python3 scripts/install_security_skills.py [--yes] TARGET`
- **Dependencies**: pinned external CLI, Git, filesystem.

### Adoption integration

- **Purpose**: Tell adopters exactly how to run the optional authorized step.
- **Location**: `scripts/adopt.py`, `README.md`, `docs/workflow/pack.md`
- **Dependencies**: project-local installer.

## Error Handling Strategy

| Error Scenario | Handling | User Impact |
| --- | --- | --- |
| Missing authorization | Print plan, status 2, no writes | User chooses whether to continue |
| Invalid pin or output hash | Abort and restore snapshot | Gate remains unavailable |
| External/symlinked managed path | Reject before publication | External referent remains untouched |
| Concurrent installer | Serialize per target | One transaction cannot undo another |
| CLI failure or missing CLI | Restore original state | Existing project remains usable |

## Risks & Concerns

| Concern | Location | Impact | Mitigation |
| --- | --- | --- | --- |
| Legacy branch predates current adoption features | `feat/security-skills:scripts/adopt.py` | Whole-file port would regress shipped behavior | Port only the installer output and merge tests into current files |
| Child CLI can inherit a hostile target variable | `scripts/install_security_skills.py` | Writes outside the disposable staging target | Remove `MY_WORKFLOW_TARGET` from the child environment |
| Rollback can follow intermediate symlinks | managed target paths | External deletion or overwrite | Validate each component without following links and publish from staging |

## Tech Decisions

| Decision | Choice | Rationale |
| --- | --- | --- |
| Distribution | External, pinned installation after adoption | Keeps third-party skills reviewable and updateable without vendoring |
| Publication | Staging plus per-target lock and rollback | Prevents partial or concurrent corruption |
