# E2E-001 QA handoff — parallel Orca slices

**Status:** untested
**Owner:** fresh QA Verifier / QA Execute session
**Author pilot:** not run

Run from the repository root only after the QA packet authorizes Orca runtime access:

```bash
python3 .agents/skills/workflow-config/scripts/parallel_plan.py \
  --root . --feature parallel-slice-executor
python3 .agents/skills/autonomous/scripts/parallel_execute.py start \
  --root . --feature parallel-slice-executor --adapter auto
```

The journey must observe two `Resources: none` lanes with distinct validated worktree, branch,
dispatch, and terminal receipts active in one run; correlated `worker_done` deliveries; read-before-
ack-before-release ordering; clean waiter end and same-terminal dependency follow-up; deterministic
checkpoint/gate or no-op evidence; and owned worker/worktree cleanup. Record command output and
receipt identities without transcripts, environment values, or credentials. Abort the pilot rather
than substituting a fake result if the capability gate returns serial fallback.
