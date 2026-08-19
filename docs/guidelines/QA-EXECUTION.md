# QA Execution

**Read when:** running the QA pass at the end of a feature.

QA the product the way a real person meets it: a **persona** walks a journey through the interfaces a
real user can reach, feels the friction, hits the edges, and reports what happened.

This is dogfooding, not a scripted test pass. The automated suite already ran — it is a
**precondition** here, not the work. This pass exists to find what a green suite cannot: a product
that passes every test and still fails its user.

## What this is not

It does not author permanent tests. Permanent e2e specs come from `E2E-` ids in
`docs/guidelines/TEST-CONTRACT.md` and are written inside implementation tasks. When a session finds
something worth automating, it drops an intent file in `docs/qa/automation-backlog/` for later — it
does not stop to write the test.

## Three non-negotiables

1. **In persona.** Every interaction and every verification goes through a surface a real user can
   reach. No dev-tools shortcut, no reading the code to decide what should happen, no patching past a
   stall.
2. **Proof, not optimism.** A `pass` is the expected observable seen, confirmed through an independent
   read path, surviving a reload, with evidence captured. Optimistic UI is not confirmation.
3. **Write back or it did not happen.** Every session updates scenario verdicts, the bug registry, and
   the dated report.

## The two tasks

Every feature's task list ends with these two, appended automatically. They are not optional and not a
judgment call.

### Task N-1 — QA Plan and Session Charters

Writes no code. Produces:

- Journey maps updated in `docs/qa/journeys/`
- Scenario files minted or reset in `docs/qa/scenarios/`, covering every public surface this feature
  touched — routes, screens, config keys, copy
- Session charters in `docs/qa/charters/` for this cycle: persona × journey × tour × time-box

Scope is the feature's user-visible diff **plus one adjacent canary journey**. A feature with no
user-visible change reports that and stops.

### Task N — Real-User QA Execution

Runs the walk. Steps below.

## The walk

**1. Resolve scope and preconditions.** Read `docs/qa/README.md`, the in-scope scenario files, open
bugs, and this cycle's charters. Confirm the automated suite is green and the product is reachable in
a production-parity build — real local stack, real auth, no mocks. Not reachable means name the exact
gap and stop.

**2. Create the report before the first session.** `docs/qa/reports/<YYYY-MM-DD>-<scope>.md`, carrying
the full matrix with every row `Pending`. This file is the source of truth for resuming — update it
after every session, never only at the end.

**3. Walk each journey in persona.** Read `docs/qa/protocol.md` in full before the first charter — it
owns the enter/act/verify/capture loop, the four-condition evidence standard, and what to do when a
flow stalls. Adopt the persona from `docs/qa/personas.md`, enter through the real entry point, and
walk to the true end state.

**Done when:** every charter has a recorded verdict, evidence exists at each checkpoint and each
divergence, and the debrief is written.

**4. Run the tour and the edge probes.** Each charter names one tour from `docs/qa/tours.md`; that
tour is the lens for the whole box. Then attempt 5–10 edges from `docs/qa/edge-cases.md`, chosen for
the surface and the persona.

**Done when:** the tour is run and every chosen edge is attempted and recorded — attempted-and-clean
is a result, not a blank.

**5. Lens pass.** Take the two journeys covering the largest changed surface and re-walk them in a
45-minute box holding each lens, recording `pass` / `friction` / `fail`:

| Lens | Asks |
| --- | --- |
| Comprehension | Does the user understand what just happened? |
| Recovery | Can they undo or retry without losing work? |
| Trust | Does anything make them doubt the system? |
| Speed | Does any step feel slower than it should? |
| Accessibility | Keyboard only, screen reader, reduced motion |
| Language | Is the copy natural, correct, consistent in the product's language? |

**6. File findings.** Deduplicate first: search `docs/qa/bugs/` and the affected scenarios' `bug_ids`.
Re-found appends a `## Re-found` section; regressed reopens with `## Regressed`; only a genuinely new
symptom mints a new id. File the bug, then link the id into the affected scenario files.

**7. Fix loop — governed.** Judge each fix **before editing**:

| Auto-fix when all hold | Escalate otherwise |
| --- | --- |
| The change is contained to one module | Anything touching a boundary, schema or contract |
| The correct behaviour is unambiguous | Any product or design judgment |
| A regression test can prove it, red before and green after | Anything requiring a spec change |

Every auto-fix ships that regression test and re-walks its impacted and adjacent journeys in persona.
Everything else goes to the report's **Decisions for a Human** with options and a recommendation.

This governor is what keeps a QA pass from turning into an unplanned refactor.

**8. Close the round.** Zero rows `Pending`. Scenario verdicts and bug statuses current. Every session
debriefed in the report. Re-run the full gate and record the result verbatim — **a green matrix over a
red suite is not ready**, and the report's Final Status must say so.

## Error handling

- **Browser tooling unavailable** — leave those scenarios `untested`, name the missing prerequisite in
  each body and in the report, and continue with the journeys still walkable. `untested` is the only
  status that is not terminal, so the next cycle picks them up without anyone remembering to.
  `blocked-verify` is for a leg no session will ever complete — a real payment, a real SMS — and
  spending it on a browser that was merely switched off records a twenty-minute gap as a permanent
  one, which is how a promise nobody checked comes to read as settled.
- **A flow hangs** — close the session, record it, retry once from a clean session, then mark it
  blocked. A stall is a finding to file, never something to nudge past.
- **Matrix larger than the time available** — cut by risk, mark the cut rows `skipped` with reasoning,
  and disclose it in Final Status. Coverage shrinks visibly or not at all.
