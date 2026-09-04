# Selective Context and Deliberate Design — Proposed Plan

Status: implementation complete; scoped verification pending independent verifier. No CRM or
Creatista migration is included.

## Outcome

One shared AGENTS.md governs workflow across projects. A small consumer-owned index routes each
agent to the product references needed for its assigned task. The Designer explores meaningful
alternatives for new screens and redesigns while exact UI corrections keep their short path.

Design source: the user-provided text of the Reactive Robot article about removing generic,
incoherent product design. No URL fetch or independent verification of its tool recommendations.

## Ownership and loading

| Artifact | Owner and purpose | Load condition |
| --- | --- | --- |
| AGENTS.md | Shared workflow entry point and routing rules | Every agent |
| docs/product/AGENT-CONTEXT.md | Brief identity, critical constraints, role/task reference index | Every agent; keep it short |
| Existing product overview and capability docs | Product intent, audiences, supported journeys | Relevant feature planning or a product ambiguity |
| docs/brand/VOICE.md, or existing equivalent | Tone, vocabulary, customer-copy examples | Copy or brand decisions |
| docs/design/SYSTEM.md, or existing equivalent | Approved visual principles, tokens, components, interaction conventions | UI/design task; relevant sections only |
| Existing architecture docs | Boundaries, data flow, engineering invariants | The task touches that boundary |
| Existing project operations docs | Gate entry points, environments, Linear and remote constraints | The matching operation |
| Current feature spec/task/uiux artifacts | Approved scope and exact implementation contract | Assigned feature/slice |
| Relevant decisions and lessons | Evidence for a named unresolved choice or failure | Search by scope; no automatic history dump |

Paths beyond the context index are examples, not a required new directory tree. Preserve and route
existing documents; create a file only when it has real content. Keep critical constraints visible
in the index. A product constraint cannot grant authority beyond the user's authorization.

Task-specific routes take precedence over role defaults. A planner doing a button-color correction
does not inherit the context load of a planner defining a new feature. Existing higher-priority
instructions remain binding. Missing necessary references become named gaps, not recursive reads.

## Expected agent context

| Work | Relevant context | Deliberately unnecessary context |
| --- | --- | --- |
| Local button color correction | Request, affected component, design tokens, accessibility constraints | Whole product flows, brand voice, historical lessons |
| Customer-facing copy | Intended message, audience, voice guide, applicable legal constraints | Unrelated architecture or product history |
| New feature specification | Product overview, affected capabilities/journeys and dependencies | Every past feature and every lesson |
| Approved implementation | Assigned task, cited acceptance criteria, selected architecture/design constraints, gate | Planning transcript or unrelated feature specs |
| Designer exploration | Design brief, affected workflows/states, selected system/brand references, existing components | Full source tree or unrelated backend internals |
| Verification/review | Assigned diff, canonical spec, tests, applicable constraints | Author's transcript |

Fresh agents receive reference paths/headings and their task scope. Use existing packet fields for
citations and preserve packet budgets; do not introduce a context service or new packet schema.
This improves explicit document selection; it does not control context the host injects automatically.

## Designer process derived from the article

1. **State the constraints.** Capture affected user goals, required states/actions, information
   hierarchy, accessibility, responsive behavior, runtime/data limits, brand principles, and existing
   components. Review the whole affected surface and its neighbours, not the entire product.
2. **Collect relevant references.** Use supplied screenshots, existing screens, or a few examples
   explaining which interaction/layout principle is useful. Reuse the project's design tools.
3. **Explore when a decision is open.** For a new screen or meaningful redesign, offer three distinct
   directions; a fourth only if it explores a real additional tradeoff. For a bounded component
   composition, start with the existing pattern. Exact color/copy/component corrections need no
   variants or mandatory Designer dispatch.
4. **Prototype before wiring.** Iterate in an available design tool or isolated HTML prototype.
   Keep exploratory variants out of production routes. Tool unavailability is not a blocker: a
   lightweight local prototype or existing component playground can provide the same decision aid.
5. **Subtract.** Give every label, icon, border, control, and decorative element a purpose. Remove
   redundancy while preserving discoverability, accessibility, required actions, and useful feedback.
6. **Choose and hand off.** The human selects a direction when alternatives materially differ.
   Record the chosen reference, reused components, necessary states/breakpoints, copy, and accepted
   tradeoffs in the existing feature UI contract. Architectures serve approved product behavior.
7. **Evaluate with representative data.** Use the local environment or an available preview. Capture
   human acceptance or precise remaining changes. Deploying a preview still follows project authority;
   use representative/sanitized fixtures unless real-data access is already authorized.

Feedback first asks whether a constraint changed. If it did, update the brief and affected variants;
otherwise perform the bounded correction. Keep vague preferences and future papercuts in an existing
design-feedback record. Confirmed deep-review bugs still follow the current in-run remediation rule.

Bound exploration: one alternatives pass and one refinement of the selected direction by default.
After that, state the unresolved design decision instead of automatically generating more rounds.
Fix concrete defects under the existing remediation policy; this bound governs exploration, not
permission to leave broken behavior.

Reusable component inspection must be allowed read-only for the Designer. Reuse an existing showcase
or story catalogue when available. Adding a new showcase or splitting frontend/backend PRs is not a
default requirement; keep vertical slices unless separate delivery is independently justified.

## Human QA and small UI work

Recognize explicit task-scoped instructions such as: "UI-only correction; I am doing manual QA."
Keep the established direct-correction path when its predicate holds. The agent reports the smallest
relevant wiring/type/render check; manual visual acceptance comes from the human, not an inferred
PASS. A later behavioral or security discovery is explained before changing the scope. Do not add
Designer variants, preview deployment, or another QA ceremony solely because the diff is visual.

## Proportional verification

The user explicitly excludes deep review and the full repository gate for this update. Use one
bounded final verification of the changed behavior; do not dispatch additional QA/review agents.

Classify verification from the resulting diff before applying generic feature or documentation rules:

- Pure documentation maintenance: inspect accuracy, affected links/headings, and whitespace. No
  new tests, spec/task validators, full gate, Technical Verifier, deep review, or QA cycle by default.
- Agent-instruction changes: compare affected instructions for consistency with the intended behavior;
  run an existing focused contract check only when it protects that changed contract. Do not test
  incidental prose wording or create a new checker solely because a document changed.
- Mixed documentation and executable changes: add the canonical targeted tests for the changed
  executable behavior. This plan changes adoption and packet rendering, so preservation, routing,
  and packet-budget checks remain relevant; the whole repository suite does not follow automatically.
- A new security/permission boundary or wider runtime impact requires concrete evidence and a stated
  validation need. File extension, file count, the word "feature", and missing selectors alone do not
  justify expanding validation. Report any coverage limit honestly and honor explicit exclusions.

Reconcile the classifier, GATES, REVIEW-ROUNDS, and phase/role bridges so the scoped selection takes
precedence over blanket "documentation uses normal review" and "last task runs all tests" rules.
Choose this route automatically for equivalent future work; do not require a magic phrase from the
developer. Context selection and verification scope are separate decisions.

## Implementation sequence

1. **Finish the context boundary.** Reconcile the existing draft: neutral shared AGENTS, consumer-owned
   starter index, safe adoption/re-adoption, task-over-role routing, provider/worker/reviewer pointers,
   and concise upgrade guidance. No product cleanup or new release in this step.
2. **Update Designer behavior.** Replace blanket design-directory loading and source-read prohibition;
   add constraints, selective references, scaled alternatives, subtraction, bounded refinement, and
   approved handoff. Put detailed procedure in one canonical reference and point role templates to it.
3. **Prove representative paths with scoped checks.** Extend existing adoption/packet tests for preservation and routing.
   Walk color correction, copy edit, feature planning, approved implementation, and redesign handoff.
   Verify applicable safety constraints remain intact and the exact UI correction stays small. Apply
   the proportional verification policy above instead of the generic full feature pipeline. Do not
   claim measured token savings or live model reliability from prose assertions.
4. **Adopt separately after source acceptance.** In CRM and Creatista, reconcile current branch/work
   state, inventory custom rules, relocate them without loss, preview adoption, resolve explicit
   ownership conflicts, synchronize packets, and verify each product's own rules. This is separate
   product work and requires its own scope; never erase a dirty checkout to obtain a clean install.

## Acceptance for this update

- Fresh projects receive identical workflow instructions and distinct product context.
- Re-adoption leaves consumer context and references intact.
- Color/copy tasks do not cause blanket product, architecture, or lesson loading.
- Fresh worker/reviewer prompts can reach required task context without a full transcript.
- Designer can inspect and reuse existing components and explores alternatives only when useful.
- Design review compares both contract conformance and coherent visual quality; neither substitutes
  for the other. Human taste feedback is attached to a concrete constraint or accepted tradeoff.
- No new mandatory design tool, showcase, preview deployment, split PR, or recurring checker.
- Equivalent documentation maintenance and bounded instruction changes automatically receive scoped
  verification. This update runs no deep review, full repository gate, or additional QA/review agents.

No additional implementation or publication is authorized by this plan artifact itself.
