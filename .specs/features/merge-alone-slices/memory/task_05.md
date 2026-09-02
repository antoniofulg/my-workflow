# Task 05 — Refresh Current QA and Release Promises

- Assumptions: this task edits only current promises, not dated QA evidence; no `qa-plan` or
  `qa-execute` session runs here. Changed scenarios reset to `untested` with empty current-cycle
  evidence fields.
- Files: existing workflow-configuration journey/scenarios, current Unreleased changelog, this
  memory, `tasks.md`, and `spec.md` traceability.
- Success: public expectations describe derived merge-alone slices, closure validation, and frozen
  resume; affected scenarios are fresh; the Unreleased notes record issue #71 without publication.
- Gate: `npm run test:all` — passed with zero failures (Bun/npm 116 tests, Python suites including
  workflow config 51 tests, parallel plan 19 tests, QA pilot 13 tests, and review convergence 6
  tests).
- Adequacy review: evidence covers all four changed CFG/ADP current scenarios, the two affected
  journeys, and the v0.7.0 Unreleased note; no dated QA evidence was edited and no QA execution was
  run. Closure: T5 is complete and ready for the atomic commit.
