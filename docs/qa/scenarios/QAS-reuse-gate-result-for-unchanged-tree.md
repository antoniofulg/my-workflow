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
evidence: docs/qa/evidence/2026-09-01-gate-result-cache/reuse/walk.log; docs/qa/evidence/2026-09-01-gate-result-cache/reuse/scope-binding.log; docs/qa/evidence/2026-09-01-gate-result-cache/docs/wired-documents.log
last_report: docs/qa/reports/2026-09-01-gate-result-cache.md
overlaps:
---

New promise from the gate result cache. This scenario owns the reuse half: `GRC-01` (a miss executes
and records), `GRC-02` (a matching passing record short-circuits), `GRC-03` (the key is tree content
plus gate label plus exact command), and `GRC-06` (the documented gate steps name the cached
invocation).

Reuse is only true if invalidation is true, so the same walk must show that a tracked edit, a staged
change, an untracked file, a different gate label, and a different command each force execution,
while a commit that changes no worktree content does not.

`AD-021` makes a matching passing record admissible readiness evidence at every gate scope, so the
walk must confirm scope binding directly: a record written under `scoped` must not satisfy a claim
that the full gate passed. The observable is a different fingerprint, not a different verdict.

The refusal half — a failing gate, a damaged record, an absent log, an uncomputable tree — is
`QAS-run-the-gate-when-the-cache-cannot-vouch`. Split because they are two different promises to the
operator: this one says the cache saves a run, that one says the cache can never cost one.

QA on 2026-09-01 walked the reuse tour twice in a checkout-local disposable repository with a
counting stand-in gate, reading every verdict from the counter, the record and the log. Both walks
produced identical fingerprints. A miss executed and recorded `status: "pass"`; two identical reruns
hit without advancing the counter. A tracked edit, a staged-but-uncommitted change and a new
untracked unignored file each produced a distinct fingerprint and executed; reverting each restored
the original hit. An ignored file and an `--allow-empty` commit left fingerprint and counter alone.
A second `--gate` label and an altered command each wrote their own record. Scope binding was walked
on a fresh tree: a `scoped` pass did not satisfy `--gate full`, which executed under its own
fingerprint. `GATES.md`, `autonomous`, `implement.md` and `qa-execute` each name the cached
invocation, and the `autonomous` readiness row requires gate scope and fingerprint to match.
