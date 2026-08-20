# QA capability profile

Read this reference in full when `docs/qa/README.md` is absent or lacks the capability needed to
plan a changed surface.

## Discover

Inspect the repository read-only. Find the package or build manifest, declared gates, CI workflows,
production-parity start and health path, public browser/API/CLI/mobile entry points, authentication
setup, fixtures or seed path, cleanup path, installed QA runners, and known unavailable surfaces.
Use the actual directory and command names found in manifests or CI.

Record each capability under the matching heading in `docs/qa/README.md`:

- Public interfaces and area codes
- Runner or adapter, linked to its manifest, CI job, or documented entry point
- Build/start path and health signal
- Authentication and session setup
- Fixtures, seed, cleanup, and residue check
- Limitations and unavailable surfaces

Keep executable command strings in their manifest or CI authority. Link to that authority instead of
copying a command that can drift.

**Done when:** `docs/qa/README.md` names every required capability, its source of truth, and every
known limitation needed by the QA plan.

## Choose the next step

If an existing adapter can reach the changed surface, record it for `qa-execute`. If no runner is
adopted, record the closest public interface and the limitation. Framework installation is a
separate planned change; the profile remains useful without it.

**Done when:** the handoff identifies one existing adapter or an explicit reachability limitation
for every affected public surface.
