# Configurable Test Lock — QA Plan

**Date:** 2026-08-31
**Phase:** QA Plan
**Spec:** `.specs/features/configurable-test-lock/spec.md`
**Diff range:** `origin/main..8a7730b`
**Profile:** `docs/qa/README.md`
**Adapter:** Checkout-local CLI/manual; no browser, server, live Orca, network, or real consumer repository
**Technical prerequisite:** PASS in `.specs/features/configurable-test-lock/validation.md` (14/14 requirements; 1/1 mutant killed)
**Deep Review prerequisite:** Round 2 `SHIP` in `.deep-review/configurable-test-lock/review.md`; final remediation is included at HEAD

## Criterion disposition

| Requirement | Disposition | Canonical QA coverage |
| --- | --- | --- |
| `CTL-01` | Public CLI: same project resource queues across linked worktrees | `J-execute-parallel-slices` -> `QAS-serialize-heavy-test-resources` |
| `CTL-02` | Public CLI: machine resource queues across repositories | `J-execute-parallel-slices` -> `QAS-serialize-heavy-test-resources` |
| `CTL-03` | Public CLI: different resources remain concurrent | `J-execute-parallel-slices` -> `QAS-serialize-heavy-test-resources` |
| `CTL-04` | Public CLI: omitted scope means project scope | `J-execute-parallel-slices` -> `QAS-serialize-heavy-test-resources` |
| `CTL-05` | Public CLI: wrapped exit status is preserved | `J-execute-parallel-slices` -> `QAS-serialize-heavy-test-resources` |
| `CTL-06` | Public CLI: timeout refuses before child start | `J-execute-parallel-slices` -> `QAS-serialize-heavy-test-resources` |
| `CTL-07` | Public CLI lifecycle: holder exit and waiter interruption preserve safe recovery | `J-execute-parallel-slices` -> `QAS-serialize-heavy-test-resources` |
| `CTL-08` | Public CLI configuration, validation, literal separator, and direct argv | `J-execute-parallel-slices` -> `QAS-serialize-heavy-test-resources` |
| `CTL-09` | Public adoption: parallel installs/tracks the inert wrapper; core omits it and commands remain unchanged | `J-execute-parallel-slices` -> `QAS-serialize-heavy-test-resources`; overlap canary `ADP-layered-workflow-adoption` |
| `CTL-10` | Public, deferred pending fresh 0.8.0 release QA after Deep Review | Technical contract `IT-009` only until fresh release QA walks the public first-use cross-project probe |
| `SEC-001` | Public CLI safety observable: metacharacters remain literal argv | `J-execute-parallel-slices` -> `QAS-serialize-heavy-test-resources` |
| `SEC-002` | Public invalid-resource refusal observable before mutation | `J-execute-parallel-slices` -> `QAS-serialize-heavy-test-resources` |
| `SEC-003` | Internal filesystem/race hardening; no user-level walk can discriminate it without replacing implementation internals | Technical PASS in `.specs/features/configurable-test-lock/validation.md`; excluded from QA Execute |
| `SEC-004` | Public diagnostic privacy observable while waiting | `J-execute-parallel-slices` -> `QAS-serialize-heavy-test-resources` |

Every one of 14 requirements has one explicit disposition: 12 public-observable mappings, one
public-but-deferred mapping (`CTL-10`), and one technical-only security mapping. `CTL-10` currently
has technical `IT-009` evidence only; fresh 0.8.0 release QA after Deep Review owns the public
first-use cross-project probe. The scenario remains `untested` until a fresh QA Execute session
walks the public interfaces.

## QA context and outputs

- Persona: `Workflow operator` from `docs/qa/personas.md`.
- Canonical journey updated: `docs/qa/journeys/J-execute-parallel-slices.md`.
- Canonical scenario updated: `docs/qa/scenarios/QAS-serialize-heavy-test-resources.md`.
- New immutable charter: `docs/qa/charters/CH-serialize-heavy-test-resources-2026-08-31.md`.
- Adjacent canary: `J-configure-feature-workflow` -> `CFG-plan-parallel-slice-dispatch`, retaining its
  existing verdict unless new observation invalidates it.
- Adoption overlap: `ADP-layered-workflow-adoption`, retained as historical layer behavior; this
  cycle's new file-level promise is owned by the configurable-lock scenario.

## Execution handoff

Dispatch a fresh Verifier with `phase: qa-execute`. It must invoke canonical `qa-execute`, read
`docs/qa/README.md`, use only the checkout-local CLI/manual adapter, and follow
`docs/qa/charters/CH-serialize-heavy-test-resources-2026-08-31.md`. Record raw evidence at
`docs/qa/evidence/2026-08-31-configurable-test-lock/` and the durable report at
`docs/qa/reports/2026-08-31-configurable-test-lock.md`; update the canonical scenario and canary only
from observed evidence. No live Orca, network, product fix, real consumer write, or internal race
injection is authorized in QA Execute.
