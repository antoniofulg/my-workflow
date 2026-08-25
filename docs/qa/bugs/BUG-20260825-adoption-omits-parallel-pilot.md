# BUG-20260825-adoption-omits-parallel-pilot

- **Status:** fixed
- **Severity:** major
- **Scenarios:** `REL-report-current-workflow-release`; `ADP-adopt-workflow-safely`
- **Expected:** Fresh adoption and re-adoption install the public `tools/qa_parallel_pilot.py`
  entry point needed by the shipped parallel-executor QA/lifecycle contract, while preserving
  consumer-owned local configuration.
- **Observed:** The package contains `tools/qa_parallel_pilot.py`, but `scripts/adopt.py` omits it
  from every managed/copy path. A fresh adopted target contains the executor, Orca/Git adapters,
  planner, convergence helper, and QA profile, but
  `target/tools/qa_parallel_pilot.py` does not exist. Re-adoption leaves it absent.
- **Adapter:** CLI/manual through `scripts/adopt.py` and independent filesystem reads.
- **Exact path:** `python3 scripts/adopt.py <disposable-target>` -> reload adopted files -> repeat
  adoption -> reload `tools/qa_parallel_pilot.py`.
- **Evidence:** `docs/qa/evidence/2026-08-25-release-0-6-0/session.md`

## Reproduction

1. Create an empty checkout-owned disposable directory.
2. Run `python3 scripts/adopt.py <target>` from release candidate `0.6.0`.
3. Confirm the adopted parallel executor and adapters exist.
4. Read `<target>/tools/qa_parallel_pilot.py`; the path is absent.
5. Re-run adoption and read the path again; it remains absent.

## Remediation recommendation

Install `tools/qa_parallel_pilot.py` through the adoption manifest, preserving source bytes and
consumer-owned files. Extend the canonical adoption test to assert fresh installation,
source-identical bytes, and byte-idempotent re-adoption. A fresh Verifier must rerun the affected
release journey plus the adoption canary after the fix.

## Fix and retest

- **Fix commit:** `816afd6`
- **Independent technical verification:** `6a9d7d4` — PASS.
- **Fresh QA retest:** PASS on 2026-08-25. Fresh adoption installed the pilot with the exact source
  SHA-256, re-adoption repaired an intentionally stale managed copy, two re-adoptions preserved the
  consumer-owned config byte-for-byte, and the adjacent package/release canaries passed.
- **Evidence:** `docs/qa/evidence/2026-08-25-release-0-6-0/session.md`
- **Report:** `docs/qa/reports/2026-08-25-release-0-6-0.md`
