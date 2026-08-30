# Layered Workflow Adoption Tasks

## Execution Protocol

Use `workflow-spec-driven`. Tasks in the implementation slice are sequential because they share `scripts/adopt.py` and `scripts/test_adopt.py`. Every code-changing slice receives a fresh Technical Verifier.

**Design**: `.specs/features/layered-workflow-adoption/design.md`
**Status**: Approved

## Test Coverage Matrix

> Guidelines: `AGENTS.md`, `docs/guidelines/TEST-CONTRACT.md`, `SECURITY.md`, `DX.md`.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Pure layer/manifest/block rules | unit | every UT and invalid branch | `scripts/test_adopt.py` | `python3 scripts/test_adopt.py` |
| Public adoption CLI/filesystem | integration | every IT and SEC case; snapshot/residue proof | `scripts/test_adopt.py` | `python3 scripts/test_adopt.py` |
| Package and active authority | integration | full profile packaged; Bun boundary current | `tools/shared/tests/*.test.ts` | `bun test tools/shared/tests/workflow-config.test.ts tools/shared/tests/qa-skills.test.ts` |
| Existing-project adoption journey | e2e CLI | E2E-001 once through public CLI | `scripts/test_adopt.py` + QA charter | `bun run test:all` |

## Gate Check Commands

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | pure model/status task | `python3 scripts/test_adopt.py` |
| Full | apply/security/public CLI task | `bun run test:all` |
| Build | slice checkpoint/docs | `bun install --frozen-lockfile && bun run test:all && bun run knowledge && bun pm pack --dry-run --ignore-scripts` |

## Execution Plan

```text
S1: T1 -> T2 -> T3 -> T4
```

One ready writer means serial execution in the integration checkout. S2 is documentation/QA contract work after the public behavior is frozen.

## Task Breakdown

### T1: Model layers, plans, manifests, and status

**Status:** complete
**Slice:** S1
**What**: Replace the monolithic public model with the fixed catalog, pure resolver/inventory/action helpers, manifest validation, and read-only `plan`/`status` subcommands.
**Where:** scripts/adopt.py
**Test owner**: `scripts/test_adopt.py`
**Depends on:** None
**Resources:** none
**Reuses**: Existing path containment, hash, snapshot, CLI subprocess helpers.
**Requirement**: LAY-01, LAY-02, LAY-03, LAY-04, LAY-11, LAY-12, LAY-13, LAY-15, LAY-18

**Done when**:

- [x] Fixed catalog/DAG/full profile resolve deterministically.
- [x] Plan text/JSON and status codes match `dx.md` and perform zero writes/sync/Orca.
- [x] Manifest rejects malformed, duplicate, unknown, and escaping state.
- [x] Legacy positional invocation exits 2 with new-command guidance.

**Tests**: UT-001, UT-002, UT-003, UT-004, IT-001, IT-006, IT-011, SEC-002
**Gate**: quick
**Commit**: `feat(adopt): model layered workflow state`

### T2: Apply managed layers safely

**Status:** complete
**Slice:** S1
**What**: Implement additive apply, per-file ownership hashes, conflict preflight, managed instruction blocks, individual-file writes, idempotence, and safe agent synchronization.
**Where:** scripts/adopt.py
**Test owner**: `scripts/test_adopt.py`
**Assets**: `templates/adoption/agents/core.md`, `templates/adoption/agents/parallel.md`, `templates/adoption/agents/quality.md`
**Depends on:** T1
**Resources:** none
**Reuses**: Current ignore merge, legacy cleanup, skill links, workflow-config validation/sync.
**Requirement**: LAY-05, LAY-06, LAY-07, LAY-08, LAY-09, LAY-10, LAY-14, LAY-16, LAY-17

**Done when**:

- [x] Core and incremental layer applies preserve consumer files/prose and record deterministic ownership.
- [x] All conflicts and unsafe paths fail before writes; sync failure retains prior state.
- [x] Reapply is byte-stable and omitted installed layers remain.
- [x] Managed AGENTS/CLAUDE blocks and `--skip-agents` match `dx.md`.

**Tests**: UT-005, IT-002, IT-003, IT-004, IT-005, IT-007, IT-008, SEC-001, SEC-003, SEC-004
**Gate**: full
**Commit**: `feat(adopt): apply workflow layers safely`

### T3: Preserve full and Bun-native adoption

**Status:** complete
**Slice:** S1
**What**: Map every current adoption path to one layer, prove full-profile equivalence, update package/active-authority contracts, and run the existing-project journey.
**Where:** scripts/adopt.py
**Test owners**: `scripts/test_adopt.py`, `tools/shared/tests/workflow-config.test.ts`, `tools/shared/tests/qa-skills.test.ts`
**Depends on:** T2
**Resources:** none
**Reuses**: Current path inventory, Bun pack test, knowledge/probe adoption checks.
**Requirement**: LAY-14, LAY-15, LAY-16, LAY-17

**Done when**:

- [x] Full resolves the exact complete capability inventory and agent synchronization.
- [x] Adopted knowledge runs with Bun without changing consumer package metadata.
- [x] E2E-001 passes with zero Orca calls and zero disposable residue.
- [x] Full build gate passes.

**Tests**: IT-009, IT-010, E2E-001
**Gate**: build
**Commit**: `test(adopt): preserve complete Bun adoption`

### T4: Document layered adoption

**Status:** pending
**Slice:** S1
**What**: Replace monolithic public commands with layer selection, plan/apply/status examples, migration guidance for existing projects, and QA scenario/charter handoff.
**Where:** README.md
**Related docs**: `docs/adoption-prompt.md`, `docs/workflow/pack.md`, affected QA artifacts, task/spec traceability
**Depends on:** T3
**Resources:** none
**Reuses**: `dx.md` as the single command contract.
**Requirement**: LAY-02, LAY-11, LAY-14, LAY-15, LAY-18

**Done when**:

- [ ] Every active adoption command uses the new subcommands and fixed layers.
- [ ] Existing-project guide starts with read-only plan and explains conflict/no-removal semantics.
- [ ] QA scenario is flagged for fresh execution.
- [ ] Build gate and command-authority scan pass.

**Tests**: documentation contract extends existing adoption authority assertions; no prose-only duplicate suite
**Gate**: build
**Commit**: `docs(adopt): document layered workflow adoption`

## Dependency Cross-Check

| Task | Depends on | Diagram | Status |
| --- | --- | --- | --- |
| T1 | None | S1 start | Match |
| T2 | T1 | T1 -> T2 | Match |
| T3 | T2 | T2 -> T3 | Match |
| T4 | T3 | T3 -> T4 | Match |

## Test Co-location Validation

| Task | Layer | Matrix requires | Task says | Status |
| --- | --- | --- | --- | --- |
| T1 | pure/CLI read-only | unit + integration | UT/IT/SEC | OK |
| T2 | mutating filesystem CLI | integration + security | UT/IT/SEC | OK |
| T3 | package/e2e boundary | integration + e2e | IT/E2E | OK |
| T4 | docs/public contract | owning structural suite | existing suite | OK |
