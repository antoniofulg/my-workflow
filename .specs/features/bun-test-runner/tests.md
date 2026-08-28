# Bun Test Runner Test Contract

## Unit

No unit cases. This feature changes the structural test runtime, release contract, and CLI boundary.

## Integration

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| BTR-IT-001 | Bun discovery stays canonical | `bun test` runs from repository root while ignored QA evidence contains copied tests | Exactly the eight tracked test files under `tools` execute; evidence copies do not execute. |
| BTR-IT-002 | npm delegates structural tests to Bun | `npm test` runs with Bun 1.4 | Bun executes 115 tests across eight files with zero failures. |
| BTR-IT-003 | Native Bun API owns test sources | Scan tracked `tools/**/*.test.ts` imports | Every runner import is `bun:test`; zero active `vitest` imports remain. |
| BTR-IT-004 | Targeted filtering remains available | Run one canonical file with `-t` and a unique full-name pattern | Only the matching test executes and the command exits zero. |
| BTR-IT-005 | Vitest dependency graph is removed | Inspect `package.json`, `package-lock.json`, and `npm ls --all` | No Vitest direct or transitive package remains; npm dependency tree is valid. |
| BTR-IT-006 | Full mixed-language gate stays green | Run `npm run test:all` | Bun structural tests and every registered Python suite exit zero. |
| BTR-IT-007 | Published release history stays immutable | Compare the v0.6.0 changelog section at HEAD with tag `v0.6.0` | Sections are byte-for-byte equal. |
| BTR-IT-008 | Pending changes belong to v0.7.0 | Inspect current changelog and version assertions | `0.7.0 - Unreleased` contains Bun and removal notes; package/lock remain 0.6.0. |
| BTR-IT-009 | Adoption does not mutate host tooling | Adopt twice into disposable project/host fixtures | No Bun installation, host setting edit, Bun lockfile, or second-run drift occurs. |
| BTR-IT-010 | Package stays clean | Run `npm pack --dry-run --json` | Package excludes ignored QA evidence and contains no Vitest artifact. |

## End-to-end

| ID | Journey | Steps | Expected |
| --- | --- | --- | --- |
| BTR-E2E-001 | Maintainer runs the supported release gate | Follow `J-review-workflow-release` through `npm run test:all`, adoption, and pack dry-run | Current QA scenario records pass with dated evidence and no release action. |

## Security

No security cases. The feature adds no trust boundary and does not install or execute remote code
beyond the existing operator-provided Bun runtime and npm dependency workflow.
