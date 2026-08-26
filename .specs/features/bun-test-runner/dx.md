# Bun Test Runner Surface Contract

## Commands

### `npm test`

- **Runtime:** Bun 1.4.x.
- **Discovery:** repository-local `bunfig.toml` limits discovery to `tools`.
- **Success:** eight files and 115 tests pass with exit code 0 at migration time.
- **Failure:** missing/incompatible Bun or any failed test exits non-zero; no fallback runner executes.

### `bun test`

- **Runtime:** Bun 1.4.x.
- **Discovery:** identical canonical `tools` root.
- **Filtering:** `-t` / `--test-name-pattern` filters the full nested test name.
- **Success and failure:** identical to `npm test`.

### `npm run test:all`

- **Order:** Bun structural suite, then every registered Python test suite.
- **Success:** every lane exits zero.
- **Failure:** the command stops non-zero at the failing lane.

### `npm pack --dry-run --json`

- **Runtime:** npm remains the package manager and publisher.
- **Success:** package metadata stays at 0.6.0 until the complete v0.7.0 release is authorized.

## Configuration

| Key | Type | Default | Effect |
| --- | --- | --- | --- |
| `test.root` in `bunfig.toml` | path | `./tools` | Restricts Bun test discovery to canonical tracked structural tests. |

## Prerequisites

- Bun 1.4.x is supplied by the developer or CI environment.
- npm remains available for dependency installation, packing, and publication.
- Adoption does not install either tool or edit host configuration.

## Removals

- Vitest test imports.
- The Vitest direct dependency and Vitest-only lockfile graph.
- Vitest-specific TypeScript globals.
- Active documentation and contracts that identify Vitest as the structural runner.

No compatibility alias, wrapper, fallback, or dual-run mode remains.
