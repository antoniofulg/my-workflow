---
id: QAS-run-the-gate-when-the-cache-cannot-vouch
area: QAS
title: Run the gate whenever the cache cannot vouch for the tree
persona: Workflow operator
journey: J-run-project-gates
expected: Whenever no record honestly proves this tree passed, the gate command runs and its real exit status is what the operator sees.
entry_points: python3 tools/gate_cache.py run --gate scoped -- <gate command>; python3 tools/gate_cache.py run --gate full -- <gate command>; .gate-cache/
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-09-01-gate-cache-tool/refusal/walk.log; docs/qa/evidence/2026-09-01-gate-cache-tool/refusal/step10-redo.log; docs/qa/evidence/2026-09-01-gate-cache-tool/refusal/interrupt.log
last_report: docs/qa/reports/2026-09-01-gate-cache-tool.md
overlaps:
---

New promise from the gate result cache, covering `GRC-04` (a failing record is kept for diagnosis
and never short-circuits), `GRC-05` (no computable tree object means run the gate and store nothing),
and the spec's edge cases: an unreadable record, an unexpected schema version, a record whose log
file is gone, a record that does not parse completely, and a missing command after `--`.

Split from `QAS-reuse-gate-result-for-unchanged-tree` because the operator's promise here is the
opposite one: the cache is allowed to lose its own value, never the gate's. The failure the walk
exists to catch is a cache that raises instead of falling back — an earlier build of this tool exited
non-zero on a record that was valid JSON but not an object, which means the cache blocked a gate
rather than running it. A non-zero exit that is not the command's own exit status is a defect here,
whatever the message says.

The damaged-record legs must be walked with the record file mutated by hand, not with the tool's own
writer, because the tool only ever writes well-formed records.

A fresh Verifier walked the refusal tour on 2026-09-01 at `aa2fbc6`. Twenty legs, every one capturing
stdout, stderr and the exit status: a failing gate exited 7 and recorded `status: "fail"`, and an
identical rerun executed again while the record still named a readable log. Twelve hand-damaged
records — truncated mid-object, `[]`, a bare string, literal `null`, a bare number, non-JSON, `true`,
an unexpected schema version, a deleted log, a missing `log` field, a null `log` field, and mode
`000` — were each treated as absent: the gate executed and the process exited with the command's own
status. No leg produced a traceback, and no leg produced a non-zero exit the gate command did not
itself produce; the historic `AttributeError` on `null` did not reproduce. With `--root` outside
every Git repository, and with `git` absent from `PATH`, the wrapper reported `NOCACHE`, ran the
command, returned its status and wrote nothing. Invoking with no command after `--`, and with no `--`
at all, refused with exit 2 and left the cache byte-identical. A closing clean run then rerun still
earned an honest hit.

The interrupted-command edge is unwalked. One attempt was made; the signal never reached the run —
a non-interactive background `SIGINT` is not the operator's foreground Ctrl-C, and the wrapper
completed normally — so the adapter cannot deliver it deterministically. The leg was not simulated
and no verdict was inferred from it.
