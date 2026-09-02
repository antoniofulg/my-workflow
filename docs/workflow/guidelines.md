# Guidelines

Each file in `docs/guidelines/` is a **triggered** protocol. `AGENTS.md` dispatches; the guideline
states the rule once. Do not copy these paragraphs into `AGENTS.md`.

Every guideline now opens with **Why this exists** (the failure mode it prevents). This page is the
catalog. The longer walk-through stays in this folder.

## Instruction cost

| File | Why it exists |
| --- | --- |
| [CONTEXT-BUDGET.md](../guidelines/CONTEXT-BUDGET.md) | Instruction files load into prompts. A previous arrangement dumped more than a thousand mandatory lines before any task. Growing a file with restated prose is a defect. Dispatch by condition. |

## How work is cut and kept

| File | Why it exists |
| --- | --- |
| [BRANCHING.md](../guidelines/BRANCHING.md) | `type/slug` names the behaviour, never `main`, delete after merge. Isolated checkouts must not share a runtime. |
| [ARTIFACT-LIFECYCLE.md](../guidelines/ARTIFACT-LIFECYCLE.md) | Planning artifacts are finished when the code exists. Durable store is code, `AD-NNN`, `docs/qa/`, product/architecture/design. The inverted arrangement gated drift on documents nobody read. |
| [WORKFLOW-MEMORY.md](../guidelines/WORKFLOW-MEMORY.md) | Small slices are cheap to review and expensive to ramp. Shared memory is how reasoning survives the task boundary without becoming a second spec. |
| [GATES.md](../guidelines/GATES.md) | Scoped gate per slice; full gate once. It also owns the credential-free declarative agent-tool configuration path. Never skip a test to go green. Cached evidence only for the exact tree. |

## Proof

| File | Why it exists |
| --- | --- |
| [TEST-CONTRACT.md](../guidelines/TEST-CONTRACT.md) | “All branches covered” cannot be audited. `UT-001` assigned to one task can. Cases come from the spec; tests assert the contracted outcome. Coverage-only tests are forbidden. |
| [VERIFICATION-EVIDENCE.md](../guidelines/VERIFICATION-EVIDENCE.md) | Completion without a fresh command is a false report. Scope binds. Secrets in a diff are an absolute stop. |
| [REVIEW-ROUNDS.md](../guidelines/REVIEW-ROUNDS.md) | See [reviews.md](reviews.md). Caps, monotonic findings, filed issues. |
| [SECURITY.md](../guidelines/SECURITY.md) | Security that lives only in a review at the end is theatre. Eleven surfaces, declared at Specify, become `SEC-` cases. Review looks for what the table missed. The lock icon on this filename is an editor convention, not extra secrecy. |

## Surfaces people meet

| File | Why it exists |
| --- | --- |
| [UI-UX.md](../guidelines/UI-UX.md) | Internals designed first get redesigned when the screen moves. `uiux.md` enumerates states so a design agent can execute, and so QA knows the feature is UI-bearing. |
| [DX.md](../guidelines/DX.md) | Same idea one layer down: routes, config, CLI, exports — written as if already shipped, failures enumerated, then internals serve that contract. |
| [FRONTEND.md](../guidelines/FRONTEND.md) | Feature folders own capability; shared UI owns reuse. Routes compose, they do not draw layout. Keeps front-end organization portable (no framework names). |
| [MODELING.md](../guidelines/MODELING.md) | The domain must outlive the web, API, and persistence frameworks. One aggregate, one module; invariants in the transition, not only in SQL. |
| [QA-SCENARIOS.md](../guidelines/QA-SCENARIOS.md) | Feature verification dies with the feature. A scenario holds a verdict that survives, and goes stale when a diff invalidates it. Content-addressed ids so parallel branches do not collide. |
| [QA-EXECUTION.md](../guidelines/QA-EXECUTION.md) | A green automated suite can still fail its user. Persona, independent confirmation, dated report. Auto-fix only when the change is contained, unambiguous, and regression-tested. |

## Durable understanding

| File | Why it exists |
| --- | --- |
| [KNOWLEDGE-WIKI.md](../guidelines/KNOWLEDGE-WIKI.md) | Source documents cannot see each other. The wiki holds the graph and the contradictions. Source always wins. Harvest is explicit and per finished feature, never part of `make check`. |

## How to add a guideline

Do not. Extend an existing file, or justify why both must exist, in [CONTEXT-BUDGET.md](../guidelines/CONTEXT-BUDGET.md). A rule earns lines by preventing a defect that occurred, or by resolving an ambiguity an agent actually hit.
