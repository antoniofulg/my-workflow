# Legacy Adoption Resolution Context

**Gathered:** 2026-08-31
**Spec:** `.specs/features/legacy-adoption-resolution/spec.md`
**Status:** Ready for implementation

## Feature Boundary

Provide one explicit, recoverable ownership transition for clean Git projects that contain legacy
workflow files but no adoption manifest. Normal `plan`, `apply`, and `status` semantics remain
unchanged.

## Implementation Decisions

### Ownership authorization

- The maintainer repeats `--replace PATH` for each reviewed file conflict.
- The command has no bulk confirmation flag.
- The complete current file-conflict set must be authorized in one transaction.

### Recovery and state

- Resolve requires a Git repository with `HEAD` and an empty porcelain status.
- Resolve rejects targets that already contain `.my-workflow/adoption.json`.
- Existing staging, rollback, agent synchronization, links, cleanup, and manifest-last publication are reused.

### Conflict boundaries

- Only catalog-managed file conflicts are replaceable.
- Managed instruction-block conflicts require manual repair.
- `--skip-agents` is the recommended existing-project path.

### Agent's Discretion

- Exact internal helper shape and concise error wording may follow existing adopter conventions.

### Declined / Undiscussed Gray Areas → Assumptions

- Historical automatic recognition is omitted because the observed match rate cannot finish either real adoption.
- Non-Git, dirty, and manifest-backed targets remain outside this one-time bootstrap.

## Specific References

- CRM canary: 32 current conflicts; 7 matched historical workflow blobs.
- Creatista canary: 40 current conflicts; 21 matched historical workflow blobs.
- Both active project checkouts must remain untouched during validation.

## Deferred Ideas

None. The command deliberately avoids a general migration framework.
