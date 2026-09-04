# Right-size UI Corrections Specification

**Size:** Medium

## Problem Statement

The planner can promote an exact UI component substitution or reference-driven UI refactor to
feature work because sizing exists only as broad prose. Once promoted, public-surface rules cascade
into impact explorers, Technical Verifiers, QA Plan, QA Execute, repeated deep reviews, and a full
end-to-end gate.

Two behavior-preserving CRM changes exposed the problem. Replacing a fixed email-verification banner
with the existing shadcn toast took six to seven hours. Updating a data table using TanStack Table
and the shadcn data-table implementation as the model triggered the same disproportionate workflow.

## Goals

- [ ] Route an exact, bounded UI component substitution or reference-driven UI refactor through the
      direct-correction path when it changes no product contract or implicit-risk surface.
- [ ] Select the cheapest check that can disprove the correction without running the full end-to-end
      gate solely because the change touches UI or lacks a feature selector.
- [ ] Preserve the current feature workflow for changes that alter journeys, business behavior, or
      cross-cutting surfaces.
- [ ] Give developers a small request vocabulary that guides classification without allowing a label
      to hide contradictory repository evidence.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Executable or persisted classifier | Planner instructions are the current routing mechanism; adding a runtime and schema is unnecessary. |
| New product test framework or gate command | Consuming projects own their commands and selectors. |
| Removal of feature verification or QA | These remain required when the correction predicate does not hold. |
| Backward-compatibility layer | The policy changes in place. |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| A component substitution can change presentation while preserving the product contract. | Treat one-surface reuse of an existing component as a direct correction when the requested presentation is exact and no listed escalation surface changes. | Banner-to-toast is observable, but its email-verification trigger and meaning remain unchanged. | y |
| A reference-driven table refactor can preserve product behavior. | Treat adoption of TanStack Table using the shadcn data-table model as a direct correction when columns, data, actions, navigation, sorting, filtering, pagination, and selection semantics remain unchanged. | Reusing established primitives changes implementation and presentation without creating a new product journey. | y |
| Existing component behavior should not be re-proven by the consuming project. | Validate only project-specific composition, data wiring, and preserved interactions unless the project changes or wraps the component behavior. | shadcn and TanStack own their component and library behavior; this workflow owns the integration seam. | y |
| Missing feature-scoped browser selection should not force the entire end-to-end suite for a direct correction. | Use the narrowest available component, render, unit, type, lint, build, or single-scenario check; report any remaining coverage limit. | Full e2e is poor evidence for a bounded presentation correction and creates the reported cost. | y |
| Planner output needs an auditable routing decision. | Require one line naming the tier, decisive facts, and selected validation layer. | A short decision record prevents silent promotion without adding a classifier service. | y |
| Developer wording should guide rather than mechanically decide classification. | Use `direct correction`, `UI-only correction`, `feature`, and `cross-feature change` as canonical intent signals; keep `issue` neutral. | Linear uses “issue” for work of every size, while explicit feature language should raise the workflow floor. | y |

**Open questions:** none - all unresolved choices use the defaults above pending spec approval.

---

## Impact

- Affected features: planner sizing and direct-correction routing; gate selection; QA and review
  routing for bounded UI corrections; full feature routing remains unchanged
- Affected pages & routes: none
- Affected jobs, events, data models, schemas, or APIs: none
- QA scenario ids to rerun: `QAS-enforce-spec-anchored-qa-contracts`,
  `QAS-write-specify-impact-and-uiux`, `QAS-offer-gap-hunt-at-plan-approval`
- Provider surfaces: Codex, Claude, and Cursor planner templates; generated runtime packets are
  synchronized from those templates

---

## User Stories

### P1: Route bounded UI substitutions directly

**User Story**: As a workflow operator, I want the planner to recognize a bounded component
substitution so that the change receives proportional planning and validation.

**Why P1**: Misclassification creates hours of avoidable agent work before implementation can close.

**Acceptance Criteria**:

1. **RSG-01**: WHEN an exact request substitutes an existing UI component or applies a named reference implementation on one bounded surface, introduces no unresolved product choice, and changes no journey, navigation, product-state transition, data, API, auth, persistence, copy meaning, shared design token, dependency, build configuration, or architecture boundary THEN the planner SHALL classify it as a direct correction.
2. **RSG-02**: WHEN a UI substitution meets the direct-correction predicate THEN the workflow SHALL use inspect, implement, scoped validation, and one atomic commit without a spec, tasks, workflow snapshot, impact explorers, Technical Verifier, QA Plan, QA Execute, deep review, or feature-close full gate.
3. **RSG-03**: WHEN the planner selects any workflow tier THEN it SHALL state the tier, the decisive classification facts, and the intended validation layer before invoking phase or gate rules.

**Independent Test**: Given the request “replace the existing CRM banner with the existing shadcn
toast without changing message semantics or trigger behavior,” the planner selects Direct correction
and names a targeted validation layer. Given the request “update the existing table using TanStack
Table and the shadcn data-table implementation as the model without changing table behavior,” it
makes the same selection.

### P1: Prevent UI-only full-gate escalation

**User Story**: As a workflow operator, I want validation selected by the changed invariant so that a
component correction does not run unrelated browser journeys.

**Why P1**: UI presence and missing selectors currently allow a full e2e escalation despite the
existing cheapest-layer policy.

**Acceptance Criteria**:

1. **RSG-04**: WHEN a request changes UI or a component THEN the workflow SHALL NOT infer an integration test, end-to-end test, or full gate from that fact alone.
2. **RSG-05**: WHEN a direct UI correction has no feature-scoped browser selector THEN the workflow SHALL choose the narrowest available component, render, unit, type, lint, build, or single-scenario check and SHALL NOT escalate to the full end-to-end gate solely because the selector is absent.
3. **RSG-06**: IF a browser-only invariant is explicitly changed or an existing targeted browser scenario owns the affected promise THEN the workflow SHALL run that targeted scenario without creating a new feature QA cycle.
4. **RSG-09**: WHEN a direct UI correction reuses an established component, library, or named reference implementation THEN the workflow SHALL validate the consuming project's composition and wiring without recreating tests for upstream component internals.
5. **RSG-10**: WHEN scoped validation passes for a direct UI correction THEN the workflow SHALL close it without dispatching a Technical Verifier, QA verifier, deep reviewer, or another validation round.

**Independent Test**: The gate contract for the banner-to-toast and data-table examples selects a
component/render check or one named browser scenario, tests only project-owned integration behavior,
and rejects repeated review agents and the full e2e suite as defaults.

### P1: Preserve escalation for real feature risk

**User Story**: As a maintainer, I want risky UI changes to keep the feature path so that efficiency
does not remove evidence needed for behavioral or cross-cutting changes.

**Why P1**: The fast path must remain bounded by behavior and blast radius, not by a “frontend” label.

**Acceptance Criteria**:

1. **RSG-07**: IF a UI request changes a journey, navigation, product-state transition, data, API, auth, persistence, copy meaning, shared design token, dependency, build configuration, architecture boundary, or leaves a product choice unresolved THEN the planner SHALL select the smallest applicable feature tier and retain its existing verification, QA, review, and feature-close gate rules.
2. **RSG-08**: WHEN a change falls outside the direct-correction predicate THEN the workflow SHALL preserve its existing sizing, verification, QA, review, and full-gate behavior.

**Independent Test**: Requests that add a route, change notification trigger state, alter auth, or
modify shared design tokens do not select Direct correction.

### P1: Use developer intent without keyword traps

**User Story**: As a developer, I want a small vocabulary for describing work so that the planner
starts at the intended workflow tier without treating every Linear issue as a feature.

**Why P1**: Natural-language intent should reduce correction overhead while repository evidence
still protects risky changes.

**Acceptance Criteria**:

1. **RSG-11**: WHEN a developer says `direct correction` or `UI-only correction` and the direct-correction risk predicate passes THEN the planner SHALL select Direct correction.
2. **RSG-12**: WHEN a developer calls the requested capability a `feature` THEN the planner SHALL select at least the Small feature tier and SHALL size upward from ambiguity, behavior, and blast radius.
3. **RSG-13**: WHEN a developer says `cross-feature change` THEN the planner SHALL select at least the Medium feature tier and SHALL map every affected product promise before implementation.
4. **RSG-14**: WHEN a request is called an `issue`, `bug`, `refactor`, `small change`, or `UI change` without an explicit behavior-preserving qualifier THEN the planner SHALL treat the word as supporting context and classify from the requested outcome and repository evidence.
5. **RSG-15**: IF repository evidence contradicts an explicitly requested fast path THEN the planner SHALL name the concrete conflicting surface before escalating the workflow tier.
6. **RSG-16**: WHEN developer wording and repository evidence agree on a workflow tier THEN the planner SHALL keep that classification unless newly discovered evidence is stated before reclassification.

**Independent Test**: `UI-only correction` selects Direct correction when behavior is preserved;
`feature` selects at least Small; `cross-feature change` selects at least Medium; `issue` alone does
not select a tier; contradictory auth or state evidence produces an explained escalation.

---

## Edge Cases

- IF the requested component is not already available in the consuming project THEN the planner
  SHALL evaluate dependency and design-system impact before selecting Direct correction.
- IF the request names a visual component but leaves timing, dismissal, message meaning, or trigger
  behavior undecided THEN the planner SHALL treat those unresolved choices as feature ambiguity.
- WHEN a correction touches several files that all implement the same bounded surface and no
  escalation predicate holds THEN the planner SHALL classify by behavior and blast radius rather
  than promote it solely because of file count.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| RSG-01 | Route bounded UI substitutions directly | Execute | Verified |
| RSG-02 | Route bounded UI substitutions directly | Execute | Verified |
| RSG-03 | Route bounded UI substitutions directly | Execute | Verified |
| RSG-04 | Prevent UI-only full-gate escalation | Execute | Verified |
| RSG-05 | Prevent UI-only full-gate escalation | Execute | Verified |
| RSG-06 | Prevent UI-only full-gate escalation | Execute | Verified |
| RSG-07 | Preserve escalation for real feature risk | Execute | Verified |
| RSG-08 | Preserve escalation for real feature risk | Execute | Verified |
| RSG-09 | Prevent UI-only full-gate escalation | Execute | Verified |
| RSG-10 | Prevent UI-only full-gate escalation | Execute | Verified |
| RSG-11 | Use developer intent without keyword traps | Execute | Verified |
| RSG-12 | Use developer intent without keyword traps | Execute | Verified |
| RSG-13 | Use developer intent without keyword traps | Execute | Verified |
| RSG-14 | Use developer intent without keyword traps | Execute | Verified |
| RSG-15 | Use developer intent without keyword traps | Execute | Verified |
| RSG-16 | Use developer intent without keyword traps | Execute | Verified |

**Coverage:** 16 total, 0 mapped to formal tasks, 16 covered by the implicit execution plan.

---

## Success Criteria

- [ ] The banner-to-toast example resolves to Direct correction with no full e2e gate by default.
- [ ] The TanStack/shadcn data-table refactor resolves to Direct correction when its behavior contract
      remains unchanged.
- [ ] Direct corrections validate only project-owned composition and wiring, then close without
      independent review agents or repeated validation rounds.
- [ ] UI presence and missing feature selector cannot independently select full e2e.
- [ ] Behavioral, security, data, dependency, shared-token, build, and architecture changes still
      select the smallest applicable feature tier.
- [ ] Canonical developer wording sets a workflow floor, `issue` remains neutral, and conflicting
      repository evidence is named before the planner escalates.
- [ ] All provider planner instructions carry the same routing contract.
