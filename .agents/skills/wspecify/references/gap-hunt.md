# Gap Hunt

Stress-test an approved specification for hidden assumptions, domain omissions, and unhandled unhappy paths before design and execution begin.

## Sizing & Invocation

Offered at plan approval (after the closure gate passes):
- **Small:** Skipped entirely.
- **Medium & Large:** Asked conversationally at plan approval.
- **Complex:** Recommended strongly at plan approval.
- **Autonomous mode:** Run only for Complex features; for Small, Medium, and Large, record the skip in `decisions.md`.

## Procedure

When accepted (or when required under autonomous mode):

### 1. Dispatch Two Explorers

Launch two read-only explorer subagents in parallel:
1. **Unhappy paths explorer:** Traces current application behaviour, failure modes, and existing QA scenarios covering the affected surface.
2. **Domain & data gaps explorer:** Inspects data models, schema constraints, entity relationships, and edge cases (empty states, concurrency, partial failures).

If the explorers find nothing, state in one line: `Gap hunt complete: no domain or unhappy-path gaps found.` and proceed.

### 2. Frontier Rounds

Present questions to the human in frontier rounds. Ask the entire frontier in one round with numbered questions, each providing a concrete recommended answer:

```
❓ **Q1** - **<question title>**: <question body, trade-offs, or multiple choices>

➡️ <your recommended answer with brief rationale>
```

Wait for answers before opening the next round. Recompute the frontier as decisions settle.

### 3. Settlement

Every settled finding MUST be recorded as:
- An **acceptance criterion** in `spec.md` (EARS notation with SHALL)
- An explicit decision in `context.md`

Never leave a settled finding as an informal note.
