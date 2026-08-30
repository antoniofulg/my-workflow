# T3 — Locked Bun security-skill installer

- The external security installer resolves only a trusted `bunx` executable.
- Every skills CLI invocation starts with `bunx --bun --no-install`; no npm/npx fallback exists.
- Existing staging, provenance, rollback, target-lock, and environment-scrubbing controls remain unchanged.
- The canonical security installer suite uses fake `bunx` executables and verifies exact argv plus fail-closed missing-tool behavior.
