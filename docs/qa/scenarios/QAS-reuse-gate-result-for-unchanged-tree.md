---
id: QAS-reuse-gate-result-for-unchanged-tree
area: QAS
title: Reuse a passing gate result for an unchanged tree
persona: Workflow operator
journey: J-run-project-gates
expected: A gate that already passed on this exact tree finishes without running the command again and names the gate, fingerprint and log path that back the claim.
entry_points: python3 tools/gate_cache.py run --gate scoped -- <gate command>; python3 tools/gate_cache.py run --gate full -- <gate command>; docs/guidelines/GATES.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-09-01-gate-cache-tool/reuse/walk.log; docs/qa/evidence/2026-09-01-gate-cache-tool/reuse/real-gate-hit.log; docs/qa/evidence/2026-09-01-gate-cache-tool/docs/wired-documents.log
last_report: docs/qa/reports/2026-09-01-gate-cache-tool.md
overlaps:
---

New promise from the gate result cache. This scenario owns the reuse half: `GRC-01` (a miss executes
and records), `GRC-02` (a matching passing record short-circuits), and `GRC-03` (the key is tree
content plus gate label plus exact command).

Reuse is only true if invalidation is true, so the same walk must show that a tracked edit, a staged
change, an untracked file, a different gate label, and a different command each force execution,
while a commit that changes no worktree content does not.

`AD-021` makes a matching passing record admissible readiness evidence at every gate scope, so the
walk must confirm scope binding directly: a record written under `scoped` must not satisfy a claim
that the full gate passed. The observable is a different fingerprint, not a different verdict.

The refusal half — a failing gate, a damaged record, an absent log, an uncomputable tree — is
`QAS-run-the-gate-when-the-cache-cannot-vouch`. Split because they are two different promises to the
operator: this one says the cache saves a run, that one says the cache can never cost one.

A fresh Verifier walked the reuse tour on 2026-09-01 at `aa2fbc6` in a checkout-local disposable
repository with a counting stand-in gate, reading every verdict from the counter, the record and the
log. Fifteen invocations produced six executions. A miss executed and recorded `status: "pass"`; two
identical reruns hit without advancing the counter. A tracked edit, a staged-but-uncommitted change
and a new untracked unignored file each produced a distinct fingerprint and executed; reverting each
restored the original hit. An ignored file and an `--allow-empty` commit left fingerprint and counter
alone. A second `--gate` label and an altered command each wrote their own record. Scope binding
holds: the `scoped` record for tree `b13b384f…` did not satisfy `--gate full`, which fingerprinted
differently and executed. Against the real gate, `--gate full -- bun run test:all` on the unchanged
source checkout returned a hit on fingerprint `da698c7e…` in 0.61 s, confirmed by reading the record
and the tail of the log it cites, and again on a re-read.

Documentation wiring is narrower than an earlier draft of this file claimed. This delivery's spec
carries `GRC-01`–`GRC-05` only and records "Wiring depth: Tool only in this delivery"; its single
documentation criterion is that `GATES.md` names the invocation, which it does at line 58. The
`autonomous` readiness row, the `implement.md` reference and `qa-execute` do not name the cached
invocation and are not required to in this delivery.
