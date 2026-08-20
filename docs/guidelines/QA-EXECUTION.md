# QA Execution

**Read when:** a diff changes public, user-observable behaviour or the feature reaches its final QA
session.

`qa-plan` and `qa-execute` own the procedures. This guideline only decides when QA runs, dispatches
the existing Verifier, and points to the authorities that keep the contract stable.

## Trigger

Run QA when a diff changes an observable UI, API, CLI, mobile surface, public configuration, adoption
flow, docs-as-interface, or user-facing copy. Purely internal refactors receive technical
verification only. Record `no user-visible change` when no public promise changed.

## Dispatch

Use the provider's existing `verifier` with one phase per packet:

1. Send a fresh `phase: qa-plan` packet to invoke `qa-plan` and create or refresh durable journeys,
   scenarios, and charters.
2. Send a distinct fresh `phase: qa-execute` packet to invoke `qa-execute` and walk those journeys.

The QA Plan session ends before the product starts. The QA Execute session does not write product
code. A defect returns to an Implementer; after the fix, a fresh Verifier reruns the technical gate,
retests the affected journey, and resumes the cycle.

## Authorities and adapters

- `docs/guidelines/QA-SCENARIOS.md` owns scenario fields, ids, statuses, and flag/reset rules.
- `docs/qa/README.md` owns the consuming project's public interfaces, existing adapter, setup,
  authentication, fixtures, cleanup, and limitations.
- `qa-execute` selects the declared browser, API, CLI, mobile, or manual adapter. It records the
  exact path, evidence, and limitation. It does not install tooling or invent commands.
- Each checkout owns its runtime and raw evidence. Keep durable reports and statuses in `docs/qa/`
  and keep generated evidence in the consuming project's disposable evidence path.

Read the two skills and `QA-SCENARIOS.md` for the active branch; this bridge deliberately carries no
duplicate scenario schema or live-walk protocol.
