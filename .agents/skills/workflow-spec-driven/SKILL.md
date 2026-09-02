---
name: workflow-spec-driven
description: Feature planning and implementation with 4 adaptive phases (Specify, Design, Tasks, Execute). Auto-sizes depth by complexity. Writes testable requirements in EARS notation, atomic tasks, atomic Conventional Commits, and requirement traceability. Ships deterministic Python validation scripts so structural gates are enforced by code, not memory. Features an independent Verifier (author != verifier, evidence-or-zero), a discrimination sensor, a decision log (STATE.md), a test-coverage matrix, and a self-improving lessons layer. Stack-agnostic and tool-agnostic. Use when (1) planning features, (2) implementing with verification and atomic commits, (3) validating an implementation against a spec. Triggers on "specify feature", "discuss feature", "design", "tasks", "implement", "validate", "verify work", "UAT", "record decision", "pause work", "resume work". Do NOT use for pure architecture decomposition analysis or standalone technical design documents.
license: CC-BY-4.0
metadata:
  author: Felipe Rodrigues - github.com/felipfr
  version: 3.3.0
---

# Workflow-owned slice-driven development

Plan and implement features with precision. Granular tasks. Clear dependencies. Right tools. Zero ceremony.

```
┌──────────┐   ┌──────────┐   ┌─────────┐   ┌─────────┐
│ SPECIFY  │ → │  DESIGN  │ → │  TASKS  │ → │ EXECUTE │
└──────────┘   └──────────┘   └─────────┘   └─────────┘
   required      optional*      optional*     required

* Agent auto-skips when scope doesn't need it
```

## Critical Rules (read before acting)

Rules 1–4 below govern feature work; direct corrections use the exception in Auto-Sizing.

**Loading this skill's files.** Reference files live under `references/` in this skill's own directory (where this `SKILL.md` resides). Resolve them relative to the skill directory - never the workspace root - and load them through the active skill by name; never assume a fixed install path. When a step tells you to read a reference, **read it completely (to EOF)** before acting - never act on a partial/truncated read.

**Running this skill's scripts.** Every `scripts/*.py` shipped with this skill lives under that same skill directory. Resolve the skill directory first, then invoke `python3 <skill-dir>/scripts/<name>.py ...`. Never run `python3 scripts/...` from the consuming project root - that looks for a project-local `scripts/` tree that is not this skill. Project data under `.specs/` is still read/written relative to the project root (pass `--root` when the cwd is elsewhere). Below, `<skill-dir>` means the directory that contains this `SKILL.md`.

**Execution contract - every task, non-negotiable (holds even if you do not open the reference files):**

1. Tests derive from the spec's acceptance criteria and assert spec-defined outcomes - they never mirror the implementation.
2. The gate must pass (tests pass) before a task is done - the test runner decides, not self-assessment.
3. One atomic commit per task. When `tasks.md` is present, mark the task complete there (and update spec traceability when used) **before** that commit; when Tasks is skipped, update and verify the inline execution plan before committing. Feature files under `.specs/features/` are versioned workflow state and may be part of that atomic commit. Never combine task commits; never weaken, skip, or delete tests to make them pass.
4. After each code-changing slice, a fresh **Technical Verifier** runs automatically (author ≠ verifier) - spec-anchored outcome check + discrimination sensor. Direct corrections use the path below and do not dispatch a Verifier.
5. **Blast radius:** approving a spec or tasks authorizes local implementation and local commits only. `git push`, force-push, deploy, production DB changes, and other remote / externally visible / destructive operations require an explicit go-ahead for that action.

**Deterministic gates run before human review - not from memory.** The structural gates for the spec and tasks are enforced by scripts in this skill's `scripts/` directory, so they cannot silently drift when the model forgets a step:

- Before confirming a spec: `python3 <skill-dir>/scripts/validate_spec.py <spec-path-or-feature>` (closure gate: EARS-shaped ACs, filled assumptions, well-formed requirement IDs, required sections).
- Before presenting tasks for approval: `python3 <skill-dir>/scripts/validate_tasks.py <tasks-path-or-feature>` (granularity smell, diagram-vs-`Depends on` parity within a phase, no forward-phase dependency, every task carries `Tests` + `Gate`).
- On each commit: `python3 <skill-dir>/scripts/check_commit.py --message "<msg>"` (Conventional Commits). Optionally wire it as a git `commit-msg` guard (git only, no agent dependency) - see [implement.md](references/implement.md).
- Before declaring a feature done: `python3 <skill-dir>/scripts/validate_state.py <feature>` (completion gate: the Verifier's `validation.md` exists, its verdict is filled to PASS, and it cites `file:line` evidence - a missing, FAIL, placeholder, or evidence-free report fails). The closing step of Execute runs this automatically, the same way the lessons layer runs at distillation; it is not a manual step.

A non-zero exit means stop and fix before proceeding. Skip a script only when no code-execution tool is available; then perform the same checks by reading the artifact.

**Before Execute (feature work):** read [implement.md](references/implement.md) completely. When a formal `tasks.md` exists, run `<skill-dir>/scripts/validate_tasks.py` against it and resolve the frozen workflow route. The coordinator dispatches safe independent slices by default and uses serial execution only for an explicit `disabled` route or a fail-closed condition. When Tasks was skipped, verify the inline execution plan instead: every step must name one deliverable, a gate command, and one atomic commit.

## Auto-Sizing: The Core Principle

**The complexity determines the depth, not a fixed pipeline.** Before starting any feature, assess its scope and apply only what's needed:

| Scope       | What                     | Specify                                                 | Design                                          | Tasks                         | Execute                                               |
| ----------- | ------------------------ | ------------------------------------------------------- | ----------------------------------------------- | ----------------------------- | ----------------------------------------------------- |
| **Direct correction** | Exact human-defined single invariant; no product ambiguity or implicit-requirement surface | Skip | Skip | Skip | Inspect → implement → scoped validation → commit |
| **Small**   | ≤3 files, one sentence   | One-liner spec (inline)                                 | Skip                                            | Skip                          | Implement + verify inline                             |
| **Medium**  | Clear feature, <10 tasks | Spec (brief)                                            | Skip - design inline                            | Skip - tasks implicit         | Implement + verify                                    |
| **Large**   | Multi-component feature  | Full spec + requirement IDs                             | Architecture + components                       | Full breakdown + dependencies | Implement + verify per task                           |
| **Complex** | Ambiguity, new domain    | Full spec + [discuss gray areas](references/discuss.md) | [Research](references/design.md) + architecture | Breakdown + phase plan        | Implement + [interactive UAT](references/validate.md) |

**Rules:**

- **For feature work, Specify and Execute are always required** - you always need to know WHAT and DO it
- **Design is skipped** when the change is straightforward (no architectural decisions, no new patterns)
- **Tasks is skipped** when there are ≤3 obvious steps (they become implicit in Execute)
- **Discuss is triggered within Specify** when the agent detects ambiguous gray areas that need user input, or when the feature has any implicit-requirement dimension present (persistence/state, external calls, auth, payments, concurrency, state transitions)
- **Interactive UAT is triggered within Execute** only for user-facing features with complex behavior

**Direct correction:** An exact human-defined single invariant with no product ambiguity, schema,
persistence, security, concurrency, or external integration runs `inspect → implement → scoped
validation → commit`. It creates no spec, AD, or workflow snapshot and skips a fresh Verifier,
deep-review, and QA. `ponytail` governs this process choice; if any predicate fails, use the
smallest feature tier.

**Safety valve:** For feature work with Tasks skipped, Execute starts by listing atomic steps inline (see [implement.md](references/implement.md)). If that listing reveals >5 steps or complex dependencies, stop and create a formal `tasks.md` - the Tasks phase was wrongly skipped.

## .specs Structure

```
.specs/
├── STATE.md            # Project memory: Decisions log (AD-NNN) + Handoff snapshot
├── LESSONS.md          # Self-improving lessons playbook (rendered by scripts/lessons.py - do not hand-edit)
├── lessons.json        # Canonical lessons state (machine-owned)
└── features/           # Feature specifications
    └── [feature]/
        ├── spec.md         # Requirements with traceable IDs
        ├── context.md      # User decisions for gray areas (only when discuss is triggered)
        ├── design.md       # Architecture & components (only for Large/Complex)
        ├── tasks.md        # Atomic tasks with verification (only for Large/Complex)
        └── validation.md   # Verifier report: PASS/FAIL, per-AC evidence, sensor result, diff range
```

**Create artifacts lazily.** Write each file only when its phase actually produces content - never scaffold empty `context.md`, `design.md`, or `tasks.md` up front. An empty file signals a phase happened when it did not; absence is the correct state for a skipped phase. The deterministic validators (`scripts/validate_spec.py`, `scripts/validate_tasks.py`, `scripts/check_commit.py`, `scripts/validate_state.py`) ship inside this skill's own `scripts/` directory, alongside `lessons.py`.

## Workflow

**New feature:**

Before dispatching providers for a new feature, resolve `.agents/skills/workflow-config/SKILL.md`
and use its frozen route.

1. Specify → (Design) → (Tasks) → Execute (depth auto-sized)

**Resume work:**

Before dispatching providers for a resumed feature, read its `workflow.json` snapshot and use the
frozen route.

1. Read `.specs/STATE.md` (Handoff + Decisions).
2. Reconcile Handoff against git (`branch`, `status --porcelain`, recent commits) and, when present, `tasks.md`; when Tasks was skipped, reconcile the inline execution plan instead. Evidence wins over a stale snapshot. Full procedure: [memory.md](references/memory.md).
3. Propose the reconciled next step before writing code.

## Context Loading Strategy

**On-demand load (only what the current task needs):**

- `.specs/STATE.md` - Decisions section (read at Design, re-read on resume); Handoff section (read on resume only)
- confirmed lessons - load at Specify and Design via `python3 <skill-dir>/scripts/lessons.py list --status confirmed` ([lessons.md](references/lessons.md)); confirmed only, never candidates
- spec.md (when working on a specific feature)
- context.md (when designing or implementing from user decisions)
- design.md (when implementing from design)
- tasks.md (when executing tasks)

**Never load simultaneously:**

- Multiple feature specs
- Multiple architecture docs

Load the smallest set that answers the current step; the on-demand list above is a ceiling, not a checklist.

## Coordinator-assisted slice dispatch

The coordinator dispatches every safe independent slice whose route is ready. It does not wait for
an extra approval response. The frozen route decides whether execution is `assisted` or explicitly
`disabled`; a fail-closed runtime condition also falls back to serial execution.

The Planner and coordinator remain on the clean integration checkout. Only concurrent Implementers
receive persistent worktrees. A single ready slice runs serially in the integration checkout. Two
compatible ready slices start in isolated writer worktrees; each worker receives only its own bounded
slice packet and executes its tasks sequentially. The coordinator recomputes readiness after each
verified checkpoint and refills a free lane from dependency-, path-, and resource-compatible work.

Automatic admission starts at two lanes. A healthy settle window admits at most one additional lane,
up to four. Missing, malformed, stale, or unhealthy evidence never admits a lane above two. The
explicit integer cap is always respected and does not bypass health proof. See
[sub-agents.md](references/sub-agents.md) for lifecycle, recovery, and role boundaries.

**Technical Verifier (always-on):** After each code-changing slice reaches its checkpoint, the coordinator dispatches a fresh Verifier automatically. It re-derives spec evidence, runs the discrimination sensor in an isolated scratch, writes the slice validation report, and never fixes the inspected tree. Dependent slices consume only verified checkpoints. Deep Review and QA are separate fresh roles on the integrated tree. Review remediation uses the immutable finding `fingerprint` and `docs/guidelines/REVIEW-ROUNDS.md`.

**Model and effort per role are configuration, not a per-dispatch judgment.** The frozen workflow route from `.agents/skills/workflow-config/SKILL.md` carries each role's model and effort; spawn the named agent and do not override them.

**Standalone fallback:** Without sub-agents, run `validate.md` as an independent fresh-eyes pass after the final commit - including the spec-anchored check and discrimination sensor.

Full mechanics (slice packet, lane admission, failure handling, coordinator contract): [sub-agents.md](references/sub-agents.md). The Verifier report format is in [validate.md](references/validate.md).

## Commands

**Feature-level (auto-sized):**
| Trigger Pattern | Reference |
|----------------|-----------|
| Specify feature, define requirements | [specify.md](references/specify.md) |
| Discuss feature, capture context, how should this work | [discuss.md](references/discuss.md) |
| Design feature, architecture | [design.md](references/design.md) |
| Break into tasks, create tasks | [tasks.md](references/tasks.md) |
| Implement task, build, execute | [implement.md](references/implement.md) |
| Validate, verify, test, UAT, walk me through it | [validate.md](references/validate.md) |

**Memory:**
| Trigger Pattern | Reference |
|----------------|-----------|
| Record decision, this is a project-level decision | [memory.md](references/memory.md) |
| Pause work, end session, I need to stop | [memory.md](references/memory.md) |
| Resume work, continue, pick up where we left off | [memory.md](references/memory.md) |
| Load lessons, what have we learned, apply past lessons | [lessons.md](references/lessons.md) |
| Record lesson, distill lessons (auto-runs after validation) | [lessons.md](references/lessons.md) |

## Knowledge Verification Chain

When researching, designing, or making any technical decision, work down this chain; each step is cheaper and more authoritative than the one below it.

```
Step 1: Codebase → check existing code, conventions, and patterns already in use
Step 2: Project docs → README, docs/, inline comments, `.specs/STATE.md` (Decisions)
Step 3: Context7 MCP → resolve library ID, then query for current API/patterns
Step 4: Web search → official docs, reputable sources, community patterns
Step 5: Flag as uncertain → "I'm not certain about X - here's my reasoning, but verify"
```

Step 5 is reached only after Steps 1-4 come up empty, and what it produces is presented as uncertain, never as fact. An invented API, pattern, or behavior propagates through design, tasks, and implementation before anyone notices, so "I couldn't find documentation for this" is the correct answer when the chain finds nothing.

## Output Behavior

**Progress updates name artifacts and decisions.** "spec.md drafted; two gray areas need your call" is a progress update; a phase name on its own is not.

**Write generated artifacts in a plain, decided voice.** Specs, ADRs, validation reports, commit messages, and chat summaries follow the writing rules in [coding-principles.md](references/coding-principles.md): lead with the verdict, state decisions definitively, cut filler and mechanical hedging.

## Code Analysis

Use available tools with graceful degradation. See [code-analysis.md](references/code-analysis.md).
