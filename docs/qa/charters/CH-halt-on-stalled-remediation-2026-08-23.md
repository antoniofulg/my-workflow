# CH-halt-on-stalled-remediation-2026-08-23

- **Date:** 2026-08-23
- **Time-box:** 20 minutes
- **Persona:** Workflow operator
- **Journey:** [`J-run-deep-review`](../journeys/J-run-deep-review.md)
- **Tour:** Halt-rule drift — every surface that states or cites the rule
- **Public entry point:** `docs/guidelines/REVIEW-ROUNDS.md` → `## Escalation`
- **Adapter candidate:** Manual repository inspection (no agent-execution harness exists)
- **Scenarios:** `DOC-halt-remediation-only-on-a-stall`; canary `DOC-require-explicit-remote-action-approval`

## Mission

Read the halt rule the way an operator does when deciding whether a run can be left unattended. The
rule changed three times during this feature and three consumer surfaces were caught restating a
retired version, so the mission is drift: find any surface that still describes a halt this pack no
longer performs. Then confirm, as the adjacent canary, that the remote-authorization halt is
untouched.

## Expected observable

One rule, stated once in `docs/guidelines/REVIEW-ROUNDS.md` and cited — not restated — everywhere
else: remediation past the cap continues without new human authorization while an attempt's failing
set is strictly smaller than the fewest seen so far, and halts after `stall_attempts` consecutive
stalls or when the gate cannot be made to run. No surface halts on an open blocker alone. The
remote-authorization halt still stands verbatim.

## Planned probes

1. **The rule is stated once.** Read `docs/guidelines/REVIEW-ROUNDS.md` `## Escalation`. It must
   define the failure signature as the sorted set of failing test identifiers for the failing gate
   command, normalized to drop timings, absolute paths and line numbers, and must say the assertion
   message is diagnosis only and never compared.
2. **Progress is the running minimum, not the previous attempt.** The same section must define
   progress as strictly smaller than the fewest seen so far in this loop, and name same-count,
   larger, and different-set-same-size as stalls.
3. **The halt names what the operator needs.** It must name `stall_attempts`, the default `3`, `0`
   as unbounded, the unrunnable-gate halt, and a report carrying the repeated signature, the attempt
   count, every fix tried, and the recommended call.
4. **Round caps are untouched.** `≤3` fix rounds and `≤2` deep-review rounds still stand, and no new
   review round opens past a cap.
5. **Rule 2 points, it does not fork.** The escalation clause in rule 2 must route to the escalation
   section rather than state a second, possibly divergent, rule.
6. **The retired formulation survives nowhere.** Search the consumer surfaces —
   `docs/guidelines/REVIEW-ROUNDS.md`, `.agents/skills/autonomous/SKILL.md`,
   `.agents/skills/workflow-config/SKILL.md`, `README.md`, `.my-workflow.toml.example`, and the
   `docs/qa/` records — for "blocker remains reproducible", "leaves a blocker open", and any
   identical-signature phrasing. Every hit outside a decision record is a defect.
7. **The skill cites rather than restates.** `.agents/skills/autonomous/SKILL.md` halt conditions
   must name the stall and cite `docs/guidelines/REVIEW-ROUNDS.md`, and must not carry its own copy
   of `stall_attempts` or the default.
8. **Canary — the remote boundary.** Confirm the unauthorized-next-remote-action halt is present and
   unchanged in `.agents/skills/autonomous/SKILL.md`, and that readiness is still evidence rather
   than authorization. Confirm only; `DOC-require-explicit-remote-action-approval` stays `pass`
   unless this probe finds a defect.

Record each surface read and the exact line under
`docs/qa/evidence/2026-08-23-stall-based-halt/`.

## Declared limitation

No agent-execution harness exists in this repository, so a live unattended run cannot be driven to
the cap and observed continuing or halting. `docs/qa/README.md` declares live model behaviour a
manual observation. The published surface for this promise is the instruction text, which this
charter walks in full; nothing here is deferred to a session that could do more.

End before any product fix, guideline edit, or remote action.
