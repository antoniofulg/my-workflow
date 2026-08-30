# T1–T4 slice handoff

- T1 model is implemented in `scripts/adopt.py`; T1 tests are in `scripts/test_adopt.py`.
- T1, T2, T3 and T4 are implemented in the S1 worktree; the parent must run independent Technical Verification.
- Scratch `workflow_config.sync_agents` rendering validates config/templates before apply writes.
