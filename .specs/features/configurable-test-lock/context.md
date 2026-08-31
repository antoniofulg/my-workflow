# Configurable Test Lock Context

**Gathered:** 2026-08-30
**Spec:** `.specs/features/configurable-test-lock/spec.md`
**Status:** Ready for design

## Feature Boundary

Ship a portable command-level resource lock with the existing `parallel` adoption layer. Consumers
explicitly wrap only heavy test commands and choose `project` or `machine` scope for each named
resource.

## Implementation Decisions

### Scope

- `project` is the default and coordinates linked worktrees of one Git repository.
- `machine` coordinates different projects that opt into the same resource name.
- Scope is selected per command so a project can keep its database local while sharing a browser lane.

### Granularity

- The lock names the contested resource, such as `browser`, `database`, `containers`, or `media`.
- Unit tests, lint, and typecheck remain parallel unless the consumer explicitly wraps them.
- The wrapper holds the lock only for the command, not for the whole implementation slice.

### Adoption

- The existing `parallel` layer installs the tool.
- Installation is inert; adoption does not rewrite `package.json`, Makefiles, or gates.
- A separate `--modules` catalog is deferred because it would duplicate the current layered selector.

### Agent's Discretion

- Exact private temporary-directory layout and hashed project identifier.
- Diagnostic formatting, provided it is bounded and secret-free.
- Internal Python function boundaries and test helpers.

### Declined / Undiscussed Gray Areas → Assumptions

- A 45-minute default timeout follows the proven CRM behavior and remains overridable per invocation.
- Unix kernel file locks are the supported primitive; Windows is outside the current workflow runtime.

## Specific References

- CRM `tools/machine-lock.py` proves bounded kernel locking, holder diagnostics, and crash release.
- Creatista `tools/test-lock/run.sh` proves project-wide worktree serialization for shared test resources.

## Deferred Ideas

- Automatic gate timing or cache integration.
- Automatic affected-test selection.
- Capacity greater than one per resource.
- A standalone adoption-module selector.
