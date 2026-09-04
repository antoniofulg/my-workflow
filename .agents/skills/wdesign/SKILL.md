---
name: wdesign
description: "Design phase - define HOW to build a specified feature: architecture, components, interfaces, data models, reuse, and risks. Argument: the feature slug. Pulled on demand by the planner agent; enter with /wdesign."
argument-hint: "<feature-or-slice>"
context: fork
agent: planner
background: false
---

# Design

Slash argument: $ARGUMENTS — when this skill was entered with /wdesign and the argument is empty, stop and ask for the feature or slice; when preloaded into an agent, the packet names the slice and this line is informational.

**Goal**: Define HOW to build it. Architecture, components, what to reuse.

**Skip this phase when:** The change is straightforward - no architectural decisions, no new patterns, no component interactions to plan. For simple features, design happens inline during Execute.

## Process

### 1. Load Context

Read `.specs/features/[feature]/spec.md` before designing. When `.specs/features/[feature]/uiux.md` exists, load it and dispatch the `designer` agent before internal design (the planner keeps the architecture half of `design.md`). If `.specs/features/[feature]/context.md` exists, load it too - it contains implementation decisions that constrain the design (layout choices, behavior preferences, interaction patterns). Decisions marked as "Agent's Discretion" are yours to decide.

**Read `.specs/STATE.md` `## Decisions` before any architectural choice.** Every `active` `AD-NNN` entry is a project-level constraint this design must conform to. If a decision from a prior feature conflicts with what is best for this feature, you have two options - both require an explicit choice:

1. **Conform** - Design within the active constraint.
2. **Supersede** - Append a new `AD-NNN` entry to `.specs/STATE.md` `## Decisions` that supersedes the old one (set the old entry's `status` to `superseded by AD-NNN`) and document the reason. The new decision becomes the project standard going forward. Silently ignoring an active decision creates invisible inconsistency across features.

**Also load confirmed lessons** relevant to this feature: `python3 .agents/skills/workflow-spec-driven/scripts/lessons.py list --status confirmed` (filter with `--scope`/`--query`). These are past verification failures distilled into guidance - apply them while designing. Load only `confirmed`. Skip silently if no store or no code tool. See [lessons.md](.agents/skills/workflow-spec-driven/references/lessons.md).

### 1.5. Research (Optional but Recommended)

If the feature involves unfamiliar technology, patterns, or integrations, research before designing. Document findings briefly in the design doc or as inline notes. This prevents incorrect assumptions from propagating into tasks.

Follow the **Knowledge Verification Chain** in the `workflow-spec-driven` router SKILL.md; its last step, flagging uncertainty, is the answer when the chain finds nothing.

Good triggers for research: new libraries, unfamiliar APIs, performance-sensitive features, security-sensitive features, patterns you haven't used in this codebase before.

**Concern flagging (while reading code):** While walking the codebase via the Knowledge Verification Chain, flag any concerns you encounter in the areas this feature touches. Capture each finding in the `## Risks & Concerns` section of `design.md`:

- **Fragile code** - tight coupling, large functions, implicit state
- **Tech debt** - hacks, workarounds, deprecated APIs
- **Security risks** - unvalidated input, auth gaps, exposed secrets
- **Performance bottlenecks** - N+1 queries, unbounded loops, missing indexes
- **Test coverage gaps** - untested paths the feature depends on

Every flagged concern carries a mitigation - how the design (or a follow-up task) addresses it.

### 2. Define Architecture

**Large/Complex only - approach exploration:** Before committing to a single architecture, present 2-3 viable approaches with trade-offs and a recommendation. Lead with the recommendation to avoid analysis paralysis. All approaches must deliver the same scoped thing (no alternative scopes). Confirm the chosen approach with the user before detailing components. Medium features: skip - design inline.

Overview of how components interact. Use mermaid diagrams when helpful.

### 3. Identify Code Reuse

What existing code can we leverage? Reuse keeps the diff small and the behaviour consistent with the codebase.

Flag any concerns found here per step 1.5 into `## Risks & Concerns`.

### 4. Define Components and Interfaces

Each component: Purpose, Location, Interfaces, Dependencies, What it reuses.

### 5. Define Data Models

If the feature involves data, define models before implementation.

## Template

Write `.specs/features/[feature]/design.md` from `references/design-template.md`.

## Tips

- **Load context first** - If context.md exists, decisions there are locked
- **Research when uncertain** - 5 minutes of research prevents hours of rework
- **Reuse is king** - Every component should reference existing patterns
- **Interfaces first** - Define contracts before implementation
- **Keep it visual** - Diagrams save 1000 words
- **Small components** - If component does 3+ things, split it
- **Flag concerns inline** - Risks found during research go in Risks & Concerns with a mitigation
- **Confirm before Tasks** - User approves design before breaking into tasks
