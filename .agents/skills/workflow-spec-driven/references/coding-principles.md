# Coding Principles

Behavioral bias, not checklist. Read before every implementation.

---

## Before Coding

- State assumptions explicitly. If something is unclear, name what is confusing and ask.
- Multiple interpretations exist? Present all - don't pick silently.
- A simpler approach exists, or the requested approach looks wrong? Say so and push back.

---

## During Implementation

### Simplicity

- No features beyond what was asked
- No abstractions for single-use code
- No "flexibility" or "configurability" not requested
- No error handling for impossible scenarios
- 200 lines that could be 50? Rewrite it.

### Surgical Changes

- Leave adjacent code, comments, and formatting as they are; match the existing style even where you would choose differently.
- Remove only the imports, variables, and functions your own change orphaned. Pre-existing dead code gets a mention, not a deletion, unless the task asks for it.

### Test Integrity

- Tests are the spec: implementation conforms to tests, not the other way around. A failing test is a signal, not noise.
- So a test is never weakened, deleted, skipped, disabled, or edited after the fact to make an implementation pass.
- The one legitimate edit is fixing a test that is genuinely wrong per the spec; confirm with the user before making it.

### Goal-Driven

- Transform vague tasks into verifiable goals
- Every changed line must trace directly to user's request

---

## After Each Change

Ask: "Would senior engineer call this overcomplicated?"
If yes → simplify before proceeding.

---

## Writing Voice (specs, ADRs, reports, commits, summaries)

The artifacts this skill produces should read like a decided engineer wrote them, not like generated boilerplate.

- **Lead with the verdict.** Validation reports and chat summaries open with PASS/FAIL and the one thing that matters, not a warm-up paragraph.
- **Decisions are definitive.** An ADR or a recorded decision states what you chose: "we will", not "we might" or "we should probably". If it still hedges, it is not a decision yet.
- **Cut filler and mechanical hedging.** Reserve hedging for genuine uncertainty; a "may/might/could" on a claim you are sure about signals nothing.
- **One idea per sentence; short sentences.** Prefer the plain verb over the nominalization ("evaluated", not "performed an evaluation of"). Keep subject-verb-object near the front.
- **Avoid the em dash as a default connector.** A comma, colon, or two sentences usually read cleaner.
None of this means dumbing down the content - only the prose carrying it.
