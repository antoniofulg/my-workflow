## Plan blocks (steps 0 and 3)

```
## Execution Plan

1. [Step] → files: [list] → verify: [how] → commit: [message]
2. [Step] → files: [list] → verify: [how] → commit: [message]
3. [Step] → files: [list] → verify: [how] → commit: [message]
```

```
Assumptions: [what you are assuming, and what is uncertain]
Files: [only the files this task requires]
Approach: [brief description]
Success: [how to verify]
```

4. **Test Adequacy Review (hard gate).**

   A task cannot be committed or marked done until all four checks below pass. Tests must be both **necessary** (every test traces to a requirement) and **sufficient** (every requirement is covered). The scope boundary is the feature spec - do not test beyond it.

   **Check A - Sufficient coverage (per-layer depth).** Build and output this table:

   | Done-when criterion / spec AC / listed edge case | `file:line` + assertion expression | Spec-defined outcome | Covered? |
   | ------------------------------------------------- | ---------------------------------- | -------------------- | -------- |
   | [criterion from task or spec] | `path/to/test.ts:42` - `expect(result.field).toBe(expected)` | [expected value from spec] | ✅ Yes / ❌ No / ⚠️ Spec-precision gap |

   **Evidence-or-zero rule:** Each covered cell MUST cite the exact `file:line` where the assertion lives AND reproduce the assertion expression (not just the `describe`/`it` name). A criterion with no located `file:line` evidence counts as **NOT covered**; the task cannot be marked done. Do not declare a criterion absent without first searching the test files - show the search before concluding it is missing (mirror: evidence or zero, never a guess).

   **Spec-anchored outcome check:** For each covered criterion, derive the expected outcome from `spec.md` (or the task's "Done when" field) and confirm the test's asserted value matches it - not just that an assertion exists. Where the spec defines a precise outcome (e.g., a specific status code, a specific field value, a specific error message), the test assertion MUST target that exact outcome. Where the spec does not define a precise outcome, mark the cell as **⚠️ Spec-precision gap** and add a note; do NOT silently pass a vague assertion as if it were covered.

   Every "Done when" criterion, every spec.md acceptance criterion, and every listed edge case that applies to this task must map to at least one concrete test assertion. Enforce the layer's Coverage Expectation from the Test Coverage Matrix:

   - Domain / service layer: assertions map 1:1 to spec ACs; every listed edge case has a dedicated test.
   - Route / controller / e2e layer: every route the task adds or modifies must have a happy-path test, a test for each listed edge case, and a test for each documented error/failure path.

   No criterion left unverified.

   **Check B - Non-shallow litmus.** Reject each of the following shallow patterns:
   - Assertion-free tests or `expect(true)` / `expect(1).toBe(1)` style tautologies
   - "No error thrown" as the only assertion - unless not-throwing IS the specified behavior
   - Asserting only on mock call counts when the actual output/state is what the criterion demands
   - Happy-path only when the task's "Done when" or spec.md lists edge cases

   **Payload/conjunction rule.** For each named field in an emitted event, returned object, or persisted record, apply a separate check:
   1. Open the constructed object at its `file:line` and confirm the field is present in the assertion.
   2. Confirm the assertion targets the field's **value or state**, not just the call that produced it.
   3. A present `emit(...)` / `return ...` / `save(...)` call does NOT prove the field - only an assertion on the result does.
   4. Asserting a method was called (spy/mock) != asserting the resulting state. Both may be needed; neither substitutes for the other.

   Apply this check to every payload-bearing criterion before marking it covered.

   **Stack-agnostic litmus:** An assertion is shallow if it would still pass under a plausible *wrong* implementation. If so, strengthen it before committing.

   **Check C - Necessary (no tests beyond the spec).** Reverse-map every test back to a spec AC, a listed edge case, or a "Done when" criterion. Build this table:

   | `file:line` + assertion expression | Maps to (AC / edge case / Done-when criterion) | Keep? |
   | ---------------------------------- | ---------------------------------------------- | ----- |
   | `path/to/test.ts:42` - `expect(result.field).toBe(expected)` | [requirement ID or criterion text] | ✅ Keep / ❌ Remove |

   Any test that maps to nothing → remove it. A test with no requirement is scope creep - it proves nothing about the feature and expands scope beyond the spec. Do not write speculative "what if" tests, do not test framework or library behavior, and do not duplicate an assertion that is already covered at another layer for the same scenario.

   **Check D - Guideline conformance.** If project quality/testing guidelines were found in step 0
   of `tasks.md` step 1.5, or in the inline plan's setup notes when Tasks was skipped, verify this
   task's tests conform to them (naming conventions, file locations, coverage thresholds, etc.).
   Note the guideline file followed.

   **Bound:** Tests prove the work; they do not expand it. Thoroughness is scoped to the feature + spec. Repo depth is a floor (never less thorough than existing tests for the same layer); the spec is the ceiling. Do not invent requirements or tests that have no spec anchor.

   **Anti-patterns - known verification cheats (treat any of these as an automatic Check failure):**

   | Anti-pattern | Why it fails |
   | ------------ | ------------ |
   | Committing before the gate check passes | Skips the deterministic verifier - the gate is not optional |
   | Asserting call count / spy invocation instead of the resulting state | Proves the method ran, not that it did the right thing |
   | Marking a criterion covered without a `file:line` citation | Violates evidence-or-zero; suspicion of coverage is not coverage |
   | Weakening an assertion (making it less specific) to force a pass | Moves the goalposts instead of fixing the code |
   | Deleting or skipping a test to make the suite pass | Destroys coverage permanently; a failing test is a signal, not noise |
   | "Tested elsewhere" deferral without citing where | Coverage gaps hide behind vague claims; cite the file:line or it doesn't count |
   | Speculative "what if" tests with no spec anchor | Expands scope beyond the ceiling; remove them in Check C |
   | Testing framework or library behavior | Tests a dependency, not the feature; remove them in Check C |

   **On any failure** → rewrite or remove the affected test(s), re-run the gate, then re-run this review.

   *Honest caveat:* This is an inspection-based review (model judgment), complementary to - not a replacement for - the deterministic gate. The gate confirms the test suite runs; the slice discrimination sensor (step 9) confirms the tests can detect regressions. This review confirms the suite is meaningful and bounded.

   Add the two mapping tables and a one-line adequacy verdict to the Execution Template's Post-Gate section.

**Format ([Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)):**

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**

| Type       | When to use                                             |
| ---------- | ------------------------------------------------------- |
| `feat`     | New feature or capability                               |
| `fix`      | Bug fix                                                 |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `docs`     | Documentation only                                      |
| `test`     | Adding or correcting tests                              |
| `style`    | Formatting, missing semicolons, etc. (no code change)   |
| `perf`     | Performance improvement                                 |
| `build`    | Build system or external dependencies                   |
| `ci`       | CI configuration files and scripts                      |
| `chore`    | Maintenance tasks that don't modify src or test files   |

**Scope:** Feature name or module area, lowercase, e.g., `auth`, `cart`, `api`

**Description rules:**

- Imperative mood ("add", not "added" or "adds")
- Lowercase first letter
- No period at the end
- Complete the sentence: "If applied, this commit will _[your description]_"

**Breaking changes:** Append `!` after type/scope AND add `BREAKING CHANGE:` footer:

```
feat(api)!: change authentication endpoint response format

BREAKING CHANGE: login endpoint now returns JWT in body instead of cookie
```

**Examples:**

```
feat(auth): add email validation to login form
```

```
fix(cart): prevent negative quantity on item decrement
```

```
refactor(api): extract token refresh logic into service

Move token refresh from inline handler to dedicated AuthTokenService
for reuse across multiple endpoints.
```

**Rules:**

- One task = one commit
- Description references what was DONE, not what was planned
- Include only files listed in the task; keep ignored planning state out of the commit
- Never sneak in "while I'm here" changes
- If tests are part of the task, include them in the same commit

**Deterministic check.** Validate the message before committing: `python3 .agents/skills/workflow-spec-driven/scripts/check_commit.py --message "<your message>"`. A non-zero exit means fix the format first. This makes the format rule enforceable instead of memory-dependent.

**Optional git-level guard (git only, no agent dependency).** In a git repo the same check can run on every commit by wiring it as a `commit-msg` hook, so a malformed message is rejected regardless of who or what drives the commit:

```bash
# from the repo root, one time (the path below is the workflow-spec-driven skill directory):
ln -sf .agents/skills/workflow-spec-driven/scripts/check_commit.py .git/hooks/commit-msg && chmod +x .git/hooks/commit-msg
```

This is a plain git hook, not tied to any editor or assistant. Skip it if the project manages hooks its own way (for example a pre-commit framework); the manual check above still applies.

## Execution Template

```markdown
## Implementing T[X]: [Task Title]

**Reading**: task definition from `tasks.md` when present, otherwise the current inline execution-plan step
**Dependencies**: [All done? ✅ | Blocked by: TY, or next inline step]
**Tests**: [unit/e2e/integration/none]
**Gate**: [quick/full/build, or inline-plan verify command]

### Pre-Implementation

- **Assumptions**: [state explicitly]
- **Files to touch**: [only these]
- **Success criteria**: [how to verify]

### Tests: Write tests derived from spec ACs

- Test file(s): [paths]
- Test count: [N test cases]
- Spec-derived: each test's asserted value maps to spec-defined outcome (or gap flagged)

### Implement

[Write minimum code to pass tests]

- Tests modified: None
- Tests skipped/deleted: None

### VERIFY: Gate Check

- Command: [gate check command]
- Result: [X passed, 0 failed]
- Test count: [N - matches planned test count]

### Post-Gate

- [x] No SPEC_DEVIATION (or markers added)
- [x] No unnecessary changes made
- [x] Matches existing patterns

**Test Adequacy Review:**

*Check A - Sufficient (coverage mapping):*

| Done-when criterion / spec AC / listed edge case | `file:line` + assertion expression | Spec-defined outcome | Covered? |
| ------------------------------------------------- | ---------------------------------- | -------------------- | -------- |
| [criterion] | `path/to/test.ts:42` - `expect(result.field).toBe(expected)` | [spec value] | ✅ Yes / ⚠️ Gap |

*Check C - Necessary (reverse mapping):*

| `file:line` + assertion expression | Maps to (AC / edge case / Done-when criterion) | Keep? |
| ---------------------------------- | ---------------------------------------------- | ----- |
| `path/to/test.ts:42` - `expect(result.field).toBe(expected)` | [requirement or criterion text] | ✅ Keep |

- [ ] Check A: every criterion covered with `file:line` evidence; spec-defined outcomes matched or gap flagged; per-layer depth met
- [ ] Check B: no shallow assertions; payload/conjunction rule applied to every payload-bearing criterion
- [ ] Check C: every test maps to a requirement - no speculative or unclaimed tests
- [ ] Check D: guideline conformance - [guideline file followed, or "none - strong defaults applied"]

**Verdict**: [All criteria covered, spec outcomes matched, no shallow assertions, all tests necessary] / [Rewritten: describe what was fixed]

**Status**: ✅ Complete | ❌ Blocked | ⚠️ Partial
```

**After each code-changing slice:** dispatch the fresh Technical Verifier (see step 9 and
[sub-agents.md](.agents/skills/workflow-spec-driven/references/sub-agents.md)) for independent slice validation, including the spec-anchored check
and discrimination sensor. The integrated feature then follows its configured Deep Review and fresh
QA route; the last Implementer does not perform those roles.


## Pause / End of Session

When work is interrupted, paused, or a session ends before the feature is complete:

1. Open `.specs/STATE.md`.
2. Locate the `## Handoff` section.
3. **Replace only that section's body** with the current snapshot (feature, phase/task, completed, in-progress `file:line`, next step, blockers, uncommitted files, branch). See [memory.md](.agents/skills/workflow-spec-driven/references/memory.md) for the exact format.
4. Do NOT touch the `## Decisions` section above it - decisions are written only during Design.

**Section-scoped write (critical):** Replace the content between the `## Handoff` header and the next `##` header (or end of file). Never overwrite the full file - doing so silently destroys the Decisions log.
