# E2E-001 QA handoff — parallel Orca slices

**Status:** untested
**Owner:** fresh QA Verifier / QA Execute session
**Author pilot:** not run

Run from the repository root only after the QA packet authorizes Orca runtime access. The setup is
disposable and touches no product files:

```bash
FIXTURE_ROOT="$(python3 tools/qa_parallel_pilot.py setup | python3 -c 'import json,sys; print(json.load(sys.stdin)["root"])')"
python3 tools/qa_parallel_pilot.py dry-run --root "$FIXTURE_ROOT"
python3 .agents/skills/autonomous/scripts/parallel_execute.py start \
  --root "$FIXTURE_ROOT" --feature parallel-pilot --adapter auto
python3 tools/qa_parallel_pilot.py cleanup --root "$FIXTURE_ROOT"
```

The dry-run command must return `validated: true`, `mode: safe`, equal `source_git_head` and
`repository_head`, and exactly two ready
`Resources: none` lanes before QA mutates Orca. The journey must then observe two independent
lanes with distinct validated worktree, branch,
dispatch, and terminal receipts active in one run; correlated `worker_done` deliveries; read-before-
ack-before-release ordering; clean waiter end and same-terminal dependency follow-up; deterministic
checkpoint/gate or no-op evidence; and owned worker/worktree cleanup. Record command output and
receipt identities without transcripts, environment values, or credentials. Abort the pilot rather
than substituting a fake result if the capability gate returns serial fallback. Cleanup is attested
outside the disposable root and independently binds the ownership source HEAD to the fixture
repository and frozen workflow before deletion. A repeated cleanup returns idempotent success only
when the bounded derived sibling has no residual paths; an unowned residual returns `cleaned: false`
with exact paths until it is removed. Unmarked roots and tampered attestations are rejected.
The ownership attestation contract includes the fixture root, feature, and the ordered exact
`parallel-pilot/A-T1` and `parallel-pilot/B-T2` worktree list; missing, extra, duplicate, outside,
or reordered values must fail closed before cleanup effects.
