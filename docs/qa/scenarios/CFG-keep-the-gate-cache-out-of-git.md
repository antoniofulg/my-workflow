---
id: CFG-keep-the-gate-cache-out-of-git
area: CFG
title: Keep gate cache records and logs out of Git
persona: Workflow adopter
journey: J-run-project-gates
expected: Running a gate through the cache leaves records and logs in the checkout that Git never reports as changes and a package never carries.
entry_points: .gitignore; .gate-cache/; python3 tools/gate_cache.py run --gate scoped -- <gate command>
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
overlaps: CFG-keep-local-artifacts-out-of-git
---

New promise from the gate result cache. `.gate-cache/` holds one JSON record and one log per run,
both keyed by fingerprint, and both must stay invisible to Git and absent from any package.

`CFG-keep-local-artifacts-out-of-git` owns the same promise for the runtimes that predate this
directory. It is frozen historical evidence under the baseline that `IT-006` enforces, so this cycle
mints a separate id rather than resetting that verdict.
