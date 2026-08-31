# Configurable Test Lock Tasks

## Execution Protocol

Implement these tasks with the `workflow-spec-driven` skill. Each task closes its state before one
atomic Conventional Commit. Every code-changing slice receives a fresh Technical Verifier before a
dependent slice consumes it.

**Design**: `.specs/features/configurable-test-lock/design.md`
**Status**: Complete — final integrated Technical Verification R2 PASS

## Test Coverage Matrix

> Generated from `AGENTS.md`, `docs/guidelines/TEST-CONTRACT.md`, `docs/guidelines/SECURITY.md`,
> `package.json`, and the existing `tools/test_*.py` and `scripts/test_*.py` suites.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Command lock and process boundary | integration + security | Every CLI branch, contention scope, timeout, lifecycle, and listed abuse case | `tools/test_parallel_resource_lock.py` | `rtk python3 tools/test_parallel_resource_lock.py` |
| Adoption inventory | integration | Parallel installs and tracks the tool; core omits it | `scripts/test_adopt.py` | `rtk python3 scripts/test_adopt.py` |
| Public documentation and agent pointer | none | Build and canonical structural gates only | `README.md`, `templates/adoption/agents/parallel.md` | Build gate only |

## Gate Check Commands

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | Command-lock task | `rtk python3 tools/test_parallel_resource_lock.py` |
| Full | Adoption task | `rtk python3 tools/test_parallel_resource_lock.py && rtk python3 scripts/test_adopt.py` |
| Build | Slice checkpoint and documentation | `npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check origin/main...HEAD` |

## Execution Plan

### Slice S1: Command-level resource lock

**Status:** complete

```text
T1
```

### Slice S2: Parallel adoption and guidance

**Status:** complete

```text
T1 -> T2 -> T3 -> T4
```

## Task Breakdown

### T1: Implement the portable command lock

**Slice**: S1
**Status**: complete
**What**: Add the command wrapper and its subprocess-level contract test.
**Where**: `tools/resource_lock.py`
**Depends on**: None
**Reuses**: CRM holder diagnostics and inherited-descriptor behavior; repository Python test runner.
**Requirements**: CTL-01, CTL-02, CTL-03, CTL-04, CTL-05, CTL-06, CTL-07, CTL-08,
SEC-001, SEC-002, SEC-003, SEC-004

**Tools**:

- MCP: none
- Skills: `ponytail`

**Done when**:

- [x] Same-resource commands serialize at project and machine scope.
- [x] Different resources remain concurrent.
- [x] Timeout, abnormal holder exit, direct argv, exact exit status, and secret-free diagnostics match `dx.md`.
- [x] Unsafe resource and filesystem inputs fail before the wrapped command.
- [x] Quick and Build gates exit zero after verification remediation.

**Tests**: UT-001, UT-002, UT-003, UT-004, IT-001, IT-002, IT-003, IT-004, IT-005,
IT-006, IT-007, SEC-001, SEC-002, SEC-003, SEC-004
**Gate**: Build
**Commit**: `feat(parallel): add configurable test resource lock`

### T2: Install the lock through parallel adoption

**Slice**: S2
**Status**: complete — `rtk python3 scripts/test_adopt.py` (65 tests passed); Build gate exit 0
**What**: Add the wrapper to the parallel inventory and extend the adoption-owned integration suite.
**Where**: `scripts/adopt.py`
**Depends on**: T1
**Reuses**: `PARALLEL_PATHS`, fixed layer closure, and schema-1 ownership manifest.
**Requirements**: CTL-09

**Tools**:

- MCP: none
- Skills: `ponytail`

**Done when**:

- [x] `core` adoption omits the wrapper.
- [x] `parallel` adoption installs and tracks the wrapper.
- [x] Re-adoption preserves the existing ownership and conflict contract.
- [x] Full and Build gates exit zero (`npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check origin/main...HEAD`).

**Tests**: IT-008
**Gate**: Build
**Commit**: `feat(adopt): install test resource lock with parallel`

### T3: Document resource-scoped activation

**Slice**: S2
**Status**: complete — Build gate exit 0 (`123` Bun tests; Python suites pass; knowledge 0 errors)
**What**: Add the public usage contract for heavy gates.
**Where**: `README.md`
**Depends on**: T2
**Reuses**: Existing layered-adoption section.
**Requirements**: CTL-09

**Tools**:

- MCP: none
- Skills: `writing-for-agents`, `ponytail`

**Done when**:

- [x] README shows project and machine examples and states that activation is explicit.
- [x] The examples wrap only declared heavy commands and leave light tests concurrent.
- [x] CLI help remains the authority for flag details.
- [x] Build gate exits zero.

**Tests**: none - documentation layer has no behavioral test requirement
**Gate**: Build
**Commit**: `docs(parallel): explain resource-scoped test locks`

### T4: Route adopted agents to the lock contract

**Slice**: S2
**Status**: complete — Build gate exit 0 (`123` Bun tests; Python suites pass; knowledge 0 errors)
**What**: Add one on-demand pointer for resource-contended gates to the adopted parallel block.
**Where**: `templates/adoption/agents/parallel.md`
**Depends on**: T3
**Reuses**: Existing parallel managed block and public README contract.
**Requirements**: CTL-09

**Tools**:

- MCP: none
- Skills: `writing-for-agents`, `ponytail`

**Done when**:

- [x] Agents are directed to the wrapper only when a gate declares a contested resource.
- [x] The pointer names the public contract without duplicating CLI flags or implementation details.
- [x] Build gate exits zero.

**Tests**: none - agent-instruction prose has no behavioral test requirement
**Gate**: Build
**Commit**: `docs(parallel): route agents to test resource locks`

## Dependency Execution Map

```text
S1          S2

T1 ------> T2 ------> T3 ------> T4
```

## Task Granularity Check

| Task | Scope | Status |
| --- | --- | --- |
| T1 | One executable component plus its co-located contract test | Granular |
| T2 | One adoption boundary plus its canonical integration assertion | Granular |
| T3 | One public documentation surface | Granular |
| T4 | One adopted agent pointer | Granular |

## Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | No incoming edge | Match |
| T2 | T1 | T1 -> T2 | Match |
| T3 | T2 | T2 -> T3 | Match |
| T4 | T3 | T3 -> T4 | Match |

## Test Co-location Validation

| Task | Code Layer | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1 | Command/process boundary | integration + security | UT-001-004, IT-001-007, SEC-001-004 | Match |
| T2 | Adoption inventory | integration | IT-008 | Match |
| T3 | Documentation | none | none | Match |
| T4 | Agent instruction | none | none | Match |

## Test Assignment Audit

| Test Contract IDs | Owning Task | Status |
| --- | --- | --- |
| UT-001-004, IT-001-007, SEC-001-004 | T1 | Assigned once |
| IT-008 | T2 | Assigned once |

**Coverage:** 13 requirements mapped; 16 test cases assigned once; 0 orphaned; 0 duplicated.
