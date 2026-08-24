# T3 Task Memory

- Objective: attach Orca workers to core-created Git worktrees and reconcile their lifecycle through correlated JSON receipts.
- Tests: IT-002–IT-004, SEC-005, SEC-006 in `tools/test_orca_adapter.py`.
- Gate: `python3 tools/test_orca_adapter.py` passed with 7 cases; `python3 tools/test_parallel_executor.py` passed with 27 regression cases.
- T3R1 gate: adapter passed with 10 cases and executor passed with 29 cases; live Run Delivery and separate worker-read schemas are correlated before acceptance/release through public resume.
- T3R2 gate: adapter passed with 13 cases and executor passed with 30 cases; nested Delivery redaction, waiter restart safety, strict receipt fields, and duplicate/missing recovery are covered.
- TDR1 gate: adapter, executor, convergence, shared, and full `npm run test:all` suites are required; TDR1 preserves the deep-review FAIL evidence and defers C/D implementation.
- Contract: the adapter uses fixed argv and `shell=False`, never creates a worktree, blocks on `check --wait`, reuses the same terminal only after a completed dependency event, and never retains transcript or environment values.
