# R3 — Exercise Three Technical Cohorts

- Assumptions: technical phase/cohort headings organize the same five primary tasks; only the
  validated merge-alone closure determines the slice count.
- Files: the one-slice validator fixture, canonical validator and resolver assertions, this memory,
  `tasks.md`, `validation.md`, and `.specs/STATE.md`.
- Success: the fixture has exactly three phases, five primary tasks, one complete closure, and the
  resolver still derives one slice; a cohort-counting implementation would fail the assertions.
- Gates: `python3 tools/test_tlc_validators.py` (17 passed), `python3 tools/test_workflow_config.py`
  (54 passed), and `python3 tools/test_parallel_plan.py` (20 passed).
- Adequacy: `tools/test_tlc_validators.py` counts canonical `Phase` headings and primary task
  headings before asserting one validated slice; the existing MAS-IT-001 resolver test now reads
  the same fixture and asserts one review group. No production implementation changed.
- Status: complete; full gate and fresh independent verification remain pending.
