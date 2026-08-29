# Bun Tooling Runtime Test Contract

## Unit

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| UT-001 | Reject unsupported Bun | Preload observes a version outside 1.4.x | Gate exits non-zero before suites run |
| UT-002 | Parse frontmatter natively | Valid, missing, malformed, scalar, and nested YAML inputs | Existing frontmatter outcomes remain exact through `Bun.YAML` |
| UT-003 | Build locked Bun executable argv | Security installer prepares the skills CLI command | Exact `bunx --bun --no-install` argv, no npm/npx fallback |

## Integration

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| IT-001 | Install frozen Bun graph | Clean checkout runs `bun install --frozen-lockfile` | Lock stays byte-identical and install exits 0 |
| IT-002 | Discover structural suites | Checkout runs `bun test` | Only canonical tests under `tools/` run |
| IT-003 | Run full gate | Checkout runs `bun run test:all` | Bun suites and all Python suites pass |
| IT-004 | Inspect package through Bun | Package check runs in a disposable destination | Required files present; excluded files absent; no checkout tarball |
| IT-005 | Adopt Bun runtime boundary | Disposable consumer is adopted and re-adopted | Runtime files byte-identical; TS tests absent; knowledge CLI runs with Bun |
| IT-006 | Preserve historical commands | Authority scan classifies npm/Vitest text | Only dated evidence or superseded feature artifacts are allowed |
| IT-007 | Fail without locked external CLI | Local executable is unavailable | Security installer exits non-zero without fetch or npm/npx |

## End-to-end

| ID | Journey | Steps | Expected |
| --- | --- | --- | --- |
| E2E-001 | Maintainer validates Bun-only workflow | Frozen install, full gate, package inspection, disposable adoption | Every stage passes and checkout residue is zero |

## Security

| ID | Abuse case | Attempt | Expected |
| --- | --- | --- | --- |
| SEC-001 | Reintroduce an unpinned package runner | Replace locked bunx argv with npm/npx or install fallback | Canonical test rejects command before execution |
| SEC-002 | Redirect package output into checkout | Pack destination resolves inside managed source paths | Check rejects or cleans exact artifact; source porcelain unchanged |

## Requirement Mapping

| Requirement | Cases |
| --- | --- |
| BUN-01, BUN-02 | IT-001 |
| BUN-03, BUN-05 | IT-002 |
| BUN-04, BUN-17 | UT-001 |
| BUN-06, BUN-07 | UT-002, IT-005 |
| BUN-08 | IT-003 |
| BUN-09, BUN-10 | UT-003, IT-007, SEC-001 |
| BUN-11, BUN-18 | IT-004, SEC-002 |
| BUN-12, BUN-13 | IT-005 |
| BUN-14, BUN-16 | IT-006 |
| BUN-15 | E2E-001 |

