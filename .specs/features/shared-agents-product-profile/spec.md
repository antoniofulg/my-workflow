# Shared Agents and Selective Product Context

**Size:** Medium

## Problem Statement

CRM and Creatista need the same workflow instructions while retaining different product rules.
Loading a whole product description, history, or flow catalogue for a button-color correction wastes
context. Fresh implementers need the approved slice and applicable constraints, while planners need
enough product context to specify the affected capability and its dependencies.

## Goals

- Keep the shared AGENTS.md product-neutral.
- Select product references by both role and task, with critical constraints always discoverable.
- Preserve the consuming project's context through workflow adoption and updates.

## Out of Scope

| Item | Reason |
| --- | --- |
| CRM or Creatista migration | This change prepares the reusable workflow; neither product checkout is modified. |
| New context service, indexing engine, or token telemetry | Markdown routing and existing bounded packets are sufficient. |
| QA/review execution, remote authority, or release work beyond proportional selection | This update defines proportional validation and explicit-skip routing, but runs no QA/deep-review/full gate and grants no new permission. |
| Bulk rewriting product knowledge or old workflow snapshots | Existing product content remains consumer-owned. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Product entry point | docs/product/AGENT-CONTEXT.md | Stable path shared across products; holds a brief identity, essential constraints, and a routing table. | y |
| Detailed references | Existing product-owned files, with optional headings | Each project can route to its existing brand, design, architecture, or operational docs without duplicating them. | y |
| Scope selection | Small index is read before work; referenced documents load only for the assigned role and task | Even a planner expands by affected capability; a button-color task does not need product history. | y |
| Installation | Initialize a missing index from a neutral template and preserve an existing index byte-for-byte | Source-pack product identity must never become consumer identity. | y |
| Legacy instructions | Preserve existing AGENTS prose and explain deliberate extraction into the index before replacement | Automatic deletion or guessing at the user's product rules is outside this feature. | y |

**Open questions:** none. User requested implementation; these defaults make the proposed separation concrete.

## Impact

- Affected features: adoption, shared agent instructions, provider role packets, bounded slice packets,
  and review context routing. Existing adoption preservation and dispatch budget guarantees remain.
- Affected pages/routes: none.
- Public surfaces: adoption CLI output/files and the installed instructions read by agents.
- QA scenarios: ADP-adopt-workflow-safely, CFG-preload-agent-skills-in-packets; extend an existing
  owning scenario or add one selective-context promise only if neither covers the behavior.
  Existing adoption and packet scenarios remain the owning promises; this update does not add a QA
  scenario or manufacture a QA verdict.
- Security surface: existing file-preservation/path safety in adoption and packet writing; no new
  network call, permission, credential handling, or executable consumer input.

## Security Surfaces

| ID | Surface | Control | Requirements |
| --- | --- | --- | --- |
| S6 | Adoption profile destination and source/template paths | Validate containment and no-follow symlinks before writes; preserve destination-only bytes | SEC-001 |

## User Stories

### P1: Share the workflow without sharing product identity

As a maintainer, I want the same workflow AGENTS.md across projects so an upgrade preserves product rules.

1. WHEN a project adopts core or a layer including core THEN adoption SHALL initialize a missing docs/product/AGENT-CONTEXT.md from a product-neutral template.
2. IF that context index already exists THEN adoption SHALL preserve its bytes and record consumer ownership on apply and reapply.
3. WHEN two fresh projects adopt the same layers from the same source THEN their AGENTS.md files SHALL be identical and contain a pointer to the product index rather than a product-stencil paragraph.
4. WHEN adoption updates a project with existing instruction prose or --skip-agents THEN it SHALL preserve that prose and the existing skip-agent guarantees; the upgrade guide SHALL explain extracting product rules before deliberately replacing an older AGENTS.md.

**Independent test:** Adopt disposable projects with distinct context markers. Compare shared AGENTS
bytes, verify profile/template separation, reapply, and confirm both product markers survive.

### P1: Load only the context needed to perform the assigned work

As a developer, I want an agent's context to reflect its role and task so a visual correction stays small.

5. WHEN an agent begins work THEN its instructions SHALL require the small context index and its critical constraints, select only references matching the role and task, and treat missing required context as a named gap rather than recursively loading product/history directories.
6. WHEN a planner specifies a feature THEN it SHALL load the product overview and affected capabilities/journeys; WHEN an implementer executes an approved slice THEN it SHALL use the cited requirements/task and relevant architecture/design constraints without the planning transcript or unrelated product learnings.
7. WHEN a task only changes a button's color THEN the context contract SHALL select applicable design/accessibility guidance without loading customer voice, whole product flows, or historical learnings; WHEN it changes customer-facing copy THEN it SHALL select the voice reference; WHEN it changes a boundary THEN it SHALL select that boundary's architecture reference.
8. WHEN a fresh worker or reviewer is dispatched THEN its provider instructions and materialized prompt SHALL expose the product context entry point and task scope, using existing packet fields for selected reference citations and preserving the existing packet schema and size budgets.
9. WHILE applying context selection, the workflow SHALL retain current task classification, QA/review requirements, role separation, and explicit permission boundaries; project constraints may strengthen safeguards and conflicts SHALL be surfaced before the affected action.
10. WHEN design work is required THEN the Designer SHALL state constraints first, inspect selected references and existing components read-only, use three alternatives only for a genuinely new screen or meaningful redesign, subtract redundant UI without harming accessibility, and stop after one exploration and one refinement unless a named choice remains.
11. WHEN validation is selected THEN the workflow SHALL classify the resulting diff as documentation maintenance, instruction change, or mixed executable change, run only the canonical owning checks for that class, escalate only for named concrete risk or changed public promise, and honor explicit user skips with a recorded narrow limitation.

**Independent test:** Exercise the existing packet renderer and provider generation, then walk the
installed reference routes for a color correction, customer copy, feature specification, and a
bounded implementation. Source/consumer sentinels must not leak into unrelated context payloads.

## Edge Cases

- A legacy project's current product paragraph stays intact until the operator explicitly relocates it.
- An untouched starter index makes its unfilled product routes explicit; the agent asks only for context
  necessary to the current task and may continue independent inspection.
- Brand/design/architecture documentation is not scaffolded as empty files; projects route existing
  files and create references when there is real content to write.
- Paths and headings are citations for selective reads, not a new automatic import or execution format.
- Unknown scope or a discovered dependency widens the selected context with an explicit reason.

## Requirement Traceability

| Requirement ID | Criterion | Status |
| --- | --- | --- |
| SCP-01 | Neutral missing-index initialization | Complete |
| SCP-02 | Consumer-owned preservation | Complete |
| SCP-03 | Identical shared instructions | Complete |
| SCP-04 | Legacy/skip-agent preservation and upgrade guidance | Complete |
| SCP-05 | Small index and conditional references | Complete |
| SCP-06 | Role-specific scope | Complete |
| SCP-07 | Task-specific selection examples | Complete |
| SCP-08 | Fresh role/packet reachability and budgets | Complete |
| SCP-09 | Existing safeguards and task classification | Complete |
| SCP-10 | Constraint-first, selective, bounded Designer process and approved handoff | Complete |
| SCP-11 | Proportional validation classification, owning checks, and explicit skips | Complete |

## Execution Plan

1. Implement selective context from adoption through fresh agent dispatch, with consumer-owned
   profile template, shared instructions, applicable packet pointers, operator guidance, and tests.
   Files: AGENTS.md, template/index assets, scripts/adopt.py and scripts/test_adopt.py, affected
   provider templates and packet/context sources, existing canonical contract tests, README.md and
   docs/adoption-prompt.md, and this feature's state.
   Verify: python3 scripts/test_adopt.py; python3 tools/test_workflow_spec_driven.py;
   python3 tools/test_phase_skills.py; bun test tools/shared/tests/qa-skills.test.ts
   tools/shared/tests/deep-review-installation.test.ts.
   Commit: feat(context): route product references by role and task.
   Status: implementation complete; 88 adoption, 5 packet, 19 phase, and 33 Bun tests passed.

One integrated slice; Design and Tasks files are skipped. Independent verification uses the same
scoped commands. Explicit user skip means no deep review, full repository gate, QA Plan/Execute, or
manufactured QA PASS for this update.

## Success Criteria

- Shared workflow instructions install consistently while consumer product references survive updates.
- The color, copy, planner, and implementer examples select distinct appropriate context.
- No new context runtime, blanket product read, or test framework is introduced.
