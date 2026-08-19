# Context Budget

**Read when:** editing `AGENTS.md` / `CLAUDE.md` or any file in this directory.

**Why this exists:** Instruction files compete with the work for the same window. A previous
arrangement loaded more than a thousand mandatory lines before any task, most of it irrelevant.
Dispatch by condition; growing a file with restated prose is a defect.

## Rules

1. **Growing an instruction file with restated or redundant prose is a defect.** Adding a rule means
   finding the one it replaces, or justifying why both must exist.
2. **`AGENTS.md` carries conditions and dispatch, not content.** If a rule applies only sometimes, it
   belongs in a guideline behind a trigger.
3. **One home per fact.** A guideline references `docs/` — it never copies from it. Two copies of a
   rule disagree eventually, and the disagreement is discovered by an agent following the wrong one.
4. **Each guideline states its trigger in its first line.** An agent must be able to decide whether to
   read it from the title and one sentence.
5. **Rules are stated once, in the imperative.** No "remember to", no restating the rule as a warning
   later in the same file, no summary section repeating what the sections said.
6. **Delete on sight.** A rule that no longer describes how the project works is worse than no rule,
   because agents follow it.

## Size targets

| File | Target |
| --- | --- |
| `AGENTS.md` | Under 200 lines |
| A rule guideline | Under 120 lines |
| A reference guideline — one carrying a schema, a surface list, or a protocol | Under 160 lines |
| All guidelines together | Under 1,500 lines, of which a typical task reads two or three |

A rule guideline states what must be true and can nearly always be shortened. A reference guideline
carries content that is irreducible — `SECURITY.md` owns the surface list, `QA-SCENARIOS.md` owns a
field schema, `KNOWLEDGE-WIKI.md` owns four operations. Cutting those does not save context, it just
moves the lookup somewhere else and costs a round trip.

These are targets, not gates. A file at its limit because nobody pruned it is the problem this
addresses; a file at its limit because the content is that size is fine.

## The test before adding anything

Ask, in order:

1. **Does a rule already cover this?** Then extend that rule rather than adding a second one.
2. **Will an agent behave differently because of this line?** If not, it is commentary. Cut it.
3. **Is this a condition or a rule?** Conditions go in the `AGENTS.md` dispatch table; rules go in the
   guideline the condition points at.
4. **Is this durable or is it about right now?** Anything about the current state of the work belongs
   in workflow memory or the pull request, never in an instruction file.

## What does not belong here

- Status, progress, or plans — those are branch and pull-request concerns
- History or rationale, except the one sentence needed to stop a rule being undone
- Anything the repository already states: file structure, available commands, code conventions the
  linter enforces
- Speculative rules for problems that have not happened

A rule earns its lines by preventing a defect that occurred, or by resolving an ambiguity an agent
actually hit.
