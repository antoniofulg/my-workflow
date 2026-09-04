---
name: wimplement
description: "Execute phase - implement one task at a time with spec-derived tests, a deterministic gate, an atomic Conventional Commit, and slice-level verification. Argument: the feature or slice. Preloaded by the implementer agent; enter with /wimplement."
argument-hint: "<feature-or-slice>"
context: fork
agent: implementer
background: false
---

# Execute

Slash argument: $ARGUMENTS — when this skill was entered with /wimplement and the argument is empty, stop and ask for the feature or slice; when preloaded into an agent, the packet names the slice and this line is informational.

**Goal**: Implement one task at a time. Surgical changes. Verify. Commit. Repeat.

This is where code gets written. Every task follows the same cycle: plan → implement → verify → commit. Verification is built into every task, not a separate phase.

Read [coding-principles.md](.agents/skills/workflow-spec-driven/references/coding-principles.md). Step 3 below records the task's assumptions, files, and success criteria; that record is the scope the task is held to.

## Process

**Slice worker context:** A worker receives only the current slice task definitions, cited acceptance
criteria, assigned test IDs, gate, required design excerpt, and compact slice memory. It does not
receive the planning transcript, whole feature state, unrelated slices, or a global task summary.
The coordinator owns inter-slice dispatch and the clean integration checkout. Concurrent writing
slices use isolated worktrees; tasks inside one slice remain sequential. See
[sub-agents.md](.agents/skills/workflow-spec-driven/references/sub-agents.md) for the lifecycle and recovery contract.

### 0. List Atomic Steps (when the Tasks phase was skipped)

If there is no `tasks.md` for this feature, list the atomic steps before writing any code. With Tasks skipped, this inline plan is the task record that step 7 updates before each commit and that resume reads, so it has to exist before the first edit. Use the plan block in `references/execution-template.md`.

**Each step must be:** one deliverable, independently verifiable, and independently committable.

If listing steps reveals >5 steps or complex dependencies, STOP and create a formal `tasks.md` instead. The Tasks phase was wrongly skipped.

### 1. Pick Task

From tasks.md (if exists) or from the execution plan above. User specifies or take next available.

### 2. Verify Dependencies

If tasks.md exists, check dependencies. If using inline plan, follow the order listed.

If a dependency is not done, say which one and propose doing it first.

### 3. State Implementation Plan

Before writing code, record the scope the task is held to, using the record block in `references/execution-template.md`.

### 4. Write Tests (derived from spec, not from implementation)

If the task includes tests (per the Tests field and **Test Coverage Matrix** in `tasks.md` when
present, or the inline execution plan when Tasks was skipped):

1. Write the test file(s) covering the task's acceptance criteria.
2. Tests MUST be derived from the task's "Done when" criteria and `spec.md` ACs - **not** from the implementation. Each test encodes what the spec requires; never write tests by reading the code and asserting what it currently does.
3. Each acceptance criterion from "Done when" maps to at least one test assertion whose asserted value matches the **spec-defined expected outcome**. Where the spec does not define a precise outcome, note it as a **spec-precision gap** rather than writing a vague assertion and passing silently.
4. Edge cases from spec.md that apply to this task get test cases too.

**Test integrity:** assertions are not weakened, and test cases are not deleted, skipped, or disabled to get a pass; a failing test is a signal, not noise. If a test is genuinely wrong (tests the wrong behavior per spec), ask the user before modifying it.

If the task does NOT include tests (e.g., entity-only, config-only), skip to Step 4b.

### 4b. Implement

Write the minimum implementation needed to satisfy the task's success criteria: pass all relevant tests (when present) and meet the defined verification/gate checks when there are no direct tests.

The test-integrity rule from step 4 still holds: the tests are the spec, and implementation conforms to them. Write the minimum code to pass; save structural improvements for a refactor task.

Follow [coding-principles.md](.agents/skills/workflow-spec-driven/references/coding-principles.md):

- Simplest code that works
- Touch only listed files
- No scope creep

### 5. Gate Check

Run the gate check command from the task definition or inline execution plan.

1. When `tasks.md` is present, look up the command for the task's Gate level (quick/full/build) in
   its **Gate Check Commands** section. When Tasks was skipped, run the `verify` command recorded
   for the current step in the inline execution plan.
2. Non-zero exit code: fix the failure and re-run. The task does not proceed until it passes.
3. Confirm the test count matches expectations (no tests were silently deleted or skipped)

**Tiered gates (from the Gate Check Commands section of `tasks.md` when present, or the inline
execution plan when Tasks was skipped):**

| Task includes                    | Gate level | What runs                |
| -------------------------------- | ---------- | ------------------------ |
| Unit tests only                  | Quick      | Unit test command        |
| E2E or integration tests         | Full       | Unit + E2E commands      |
| Last task in a phase             | Build      | Build + lint + all tests |
| No tests (config, entities, etc) | Build      | Build + lint only        |

The gate check is deterministic. The test runner decides if the code is correct,
not the agent's self-assessment.

### 6. Post-Gate Review

After the gate check passes:

1. Verify test count: Are there at least as many test cases as before? (prevents silent deletion)
2. Verify no SPEC_DEVIATION: If implementation diverged from spec/design, add a marker:

```
// SPEC_DEVIATION: [what diverged]
// Reason: [why the deviation was necessary]
```

3. Quick complexity check: "Would senior engineer flag this as overcomplicated?"
   - Yes → Simplify, re-run gate
   - No → Proceed

4. **Test Adequacy Review (hard gate).** Run checks A-D and the anti-pattern table in `references/execution-template.md`; a task cannot be committed or marked done until all four pass. That file also carries the plan blocks, the commit-message format, the execution template, and the pause procedure.

### 7. Status + Atomic Commit

After the gate is green, close the task record **before** creating the commit. When `tasks.md` is
present, it is the resume source; when Tasks was skipped, the inline execution plan is the local
state to update and verify. Feature files under `.specs/features/` are versioned workflow state and
their task/status updates belong in the atomic commit. Never leave the local task state open after a successful task commit - a
crash between those steps is how resume redoes finished work.

1. If `tasks.md` is present, mark the task complete in `tasks.md`. If Tasks was skipped, mark the
   current inline execution-plan step complete and record its gate result. Update requirement
   traceability in `spec.md` if requirement IDs are used.
2. Create **one** atomic commit that includes the implementation and its tests; verify the local
   status/traceability updates before committing.

Each task gets its own commit immediately after verification. Never dispatch multiple tasks into one commit.


**Rules:**

- One task = one commit
- Description references what was DONE, not what was planned
- Include only files listed in the task; keep ignored planning state out of the commit
- Never sneak in "while I'm here" changes
- If tests are part of the task, include them in the same commit

**Deterministic check.** Validate the message before committing: `python3 .agents/skills/workflow-spec-driven/scripts/check_commit.py --message "<your message>"`. A non-zero exit means fix the format first. This makes the format rule enforceable instead of memory-dependent.

### 8. Scope Guardrail

During implementation, you will notice things that could be improved, refactored, or added. **Do not act on them.** Instead:

- If you discover an unrelated bug outside an active, approved review loop: surface it to the user
  (or capture it as a separate task). Findings inside that loop follow `REVIEW-ROUNDS.md`.
- If it's an improvement: add it to the feature's `context.md` under "Deferred Ideas" (or surface it to the user if there is no `context.md`)
- If it's related to the current task: only include it if it's in the "Done when" criteria

**The heuristic:** "Is this in my task definition?" If no, don't touch it.

**Blast radius (approval ≠ remote authority):** Approving a spec or tasks authorizes local implementation and local commits only. Before `git push`, force-push, deploy, production DB migration, or any other remote / externally visible / destructive operation, stop and get an explicit go-ahead for that action - even if Execute was already approved.

### 9. Slice-Level Validation (after each code-changing slice)

When the current slice reaches its checkpoint, the coordinator dispatches a fresh Technical
Verifier before any dependent slice consumes that checkpoint. Validation is automatic and does not
wait for a separate approval; a slice's commit does not unblock dependent work without this proof.

**Author ≠ verifier.** An author checking their own work reapplies the mental model that may have produced the gaps. The Verifier is a fresh sub-agent that re-derives coverage from the spec independently - this separation is the quality gate, not a style preference.

**Layering:**
- Per-task adequacy self-check (steps 5-6): cheap, always runs, author does it, confirms each task in isolation.
- Slice-level validation (step 9): one trustworthy independent gate at each code-changing checkpoint,
  always-on, performed by a fresh Verifier session.

**How to delegate to the Verifier:**
Dispatch a fresh sub-agent following the **Verifier** role described in [sub-agents.md](.agents/skills/workflow-spec-driven/references/sub-agents.md). Provide it with:
- `spec.md` (ACs = source of truth)
- The git diff surface for this feature (commit range)
- The test files in scope
- the `wverify` skill as its operating checklist

**What the Verifier does** (full procedure in [sub-agents.md](.agents/skills/workflow-spec-driven/references/sub-agents.md); operating checklist in the `wverify` skill): a spec-anchored coverage check (evidence-or-zero, each asserted value matched to the spec outcome) plus a discrimination sensor (behavior-level mutations run in a scratch state and then discarded), after which it writes `.specs/features/[feature]/validation.md` (PASS/FAIL, per-AC evidence, sensor result, diff range) and returns a compact verdict + ranked gaps in chat. It runs read-only over the real tree and does NOT fix.

If the Verifier returns FAIL, record the fingerprinted result with the stdlib convergence script, route the ranked gaps back to an implementer, and re-dispatch the Verifier using the accounting in `docs/guidelines/REVIEW-ROUNDS.md`; count the failed Verifier result in cumulative history even when the scoped build gate is green, and halt only when the live consecutive-stall threshold is reached.

The final integrated tree still receives the separately routed Deep Review and fresh QA sessions.
The last Implementer writes only a compact handoff and never certifies the integrated result.

## Tips

- **Commit per task** - Clean git history enables bisect and rollback
- **Learn from mistakes** - If something goes wrong, surface it to the user so it informs the next task
- **Plain voice in prose** - Lead with what changed, no filler per [coding-principles.md](.agents/skills/workflow-spec-driven/references/coding-principles.md)
