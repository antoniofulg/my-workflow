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
- On each commit: `python3 <skill-dir>/scripts/check_commit.py --message "<msg>"` (Conventional Commits). Optionally wire it as a git `commit-msg` guard (git only, no agent dependency) - see the `wimplement` skill.
- Before declaring a feature done: `python3 <skill-dir>/scripts/validate_state.py <feature>` (completion gate: the Verifier's `validation.md` exists, its verdict is filled to PASS, and it cites `file:line` evidence - a missing, FAIL, placeholder, or evidence-free report fails). The closing step of Execute runs this automatically, the same way the lessons layer runs at distillation; it is not a manual step.

A non-zero exit means stop and fix before proceeding. Skip a script only when no code-execution tool is available; then perform the same checks by reading the artifact.

**Before Execute (feature work):** read the `wimplement` skill completely. When a formal `tasks.md` exists, run `<skill-dir>/scripts/validate_tasks.py` against it and resolve the frozen workflow route. The coordinator dispatches safe independent slices by default and uses serial execution only for an explicit `disabled` route or a fail-closed condition. When Tasks was skipped, verify the inline execution plan instead: every step must name one deliverable, a gate command, and one atomic commit.

## Auto-Sizing: The Core Principle

**The complexity determines the depth, not a fixed pipeline.** Before starting any feature, assess its scope and apply only what's needed:

### Request vocabulary and classification
Use developer words as intent signals, then confirm them against repository evidence. State the selected tier, decisive facts, and validation layer before dispatching any phase or gate.
Evidence wins when it contradicts a requested fast path; name the concrete surface before reclassifying.
- `cross-feature change` sets a **Medium feature** floor and requires mapping every affected product promise.
- `feature` sets a **Small feature** floor; size upward for ambiguity, behavior, or blast radius.
- `direct correction` and `UI-only correction` request the fast path, subject to the direct-correction predicate below.
- `issue`, `bug`, `refactor`, `small change`, and `UI change` are neutral; classify from the outcome and evidence.
The strongest explicit feature floor wins: `feature` or `cross-feature change` cannot be silently reduced to a direct correction. Escalate a direct/UI-only request only when newly discovered, named evidence fails its predicate; do not reclassify for file count alone.

| Scope | What | Specify (`wspecify`) | Design (`wdesign`) | Tasks (`wtasks`) | Execute (`wimplement`) |
| ----------- | ------------------------ | ------------------------------------------------------- | ----------------------------------------------- | ----------------------------- | ----------------------------------------------------- |
| **Direct correction** | Exact human-defined single invariant; no product ambiguity or implicit-requirement surface | Skip | Skip | Skip | Inspect → implement → scoped validation → commit |
| **Small**   | ≤3 files, one sentence   | One-liner spec (inline)                                 | Skip                                            | Skip                          | Implement + verify inline                             |
| **Medium**  | Clear feature, <10 tasks | Spec (brief)                                            | Skip - design inline                            | Skip - tasks implicit         | Implement + verify                                    |
| **Large**   | Multi-component feature  | Full spec + requirement IDs                             | Architecture + components                       | Full breakdown + dependencies | Implement + verify per task                           |
| **Complex** | Ambiguity, new domain    | Full spec + discuss gray areas (`wspecify`) | Research (`wdesign`) + architecture | Breakdown + phase plan | Implement + interactive UAT (`wverify`) |

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

For a UI-only correction, require one bounded surface, an existing component/library or named reference implementation, and unchanged journey, navigation, product-state, data/API, auth, persistence, copy meaning, shared token, dependency, build, and architecture semantics. Validate consuming-project composition and wiring at the cheapest discriminating layer; do not retest upstream shadcn/TanStack internals. UI presence or a missing feature browser selector alone never selects integration, end-to-end, or the full gate. If a browser-only invariant is explicitly changed, run its existing targeted scenario without creating a QA cycle. Once scoped validation passes, close without a Verifier, QA Plan/Execute, deep review, or another validation round.
Examples: CRM banner → existing shadcn toast and existing table → TanStack/shadcn data table are direct corrections when their trigger, message, and table semantics stay unchanged.

**Safety valve:** For feature work with Tasks skipped, Execute starts by listing atomic steps inline (see the `wimplement` skill). If that listing reveals >5 steps or complex dependencies, stop and create a formal `tasks.md` - the Tasks phase was wrongly skipped.

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
