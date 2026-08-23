# Task 05 memory

- Phase: `qa-plan`; no public interface was executed and no product code changed.
- Profile: `docs/qa/README.md`; adapter candidate is CLI/manual through `scripts/adopt.py`, with
  structural preflight owned by `package.json` and `scripts/test_adopt.py`.
- Criterion disposition: QA-01–QA-07, QA-16, QA-18 →
  `QAS-discover-independent-qa-skills`; QA-08–QA-11 →
  `DOC-read-explicit-workflow-provenance`; QA-12, QA-19–QA-21 →
  `CFG-keep-local-artifacts-out-of-git`; QA-13–QA-15, QA-17 →
  `ADP-adopt-workflow-safely`; QA-22 → `REL-report-capability-version-0-3-0`.
- Next session: a fresh Verifier runs `qa-execute` over both dated charters, using a checkout-local
  disposable target and `docs/qa/evidence/`; no browser, API, mobile, auth, server, or live agent
  harness exists.
- Plan gates: scoped structural suite 16/16; five scenario files match the canonical field order,
  stable ids, personas, journeys, and `untested` status; diff check passed.
