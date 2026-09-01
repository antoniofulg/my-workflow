---
id: CFG-keep-the-gate-cache-out-of-git
area: CFG
title: Keep gate cache records and logs out of Git
persona: Workflow adopter
journey: J-run-project-gates
expected: Running a gate through the cache leaves records and logs in the checkout that Git never reports as changes and a package never carries.
entry_points: .gitignore; .gate-cache/; python3 tools/gate_cache.py run --gate scoped -- <gate command>
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-09-01-gate-cache-tool/gitvis/git-visibility.log; docs/qa/evidence/2026-09-01-gate-cache-tool/gitvis/package-and-clone.log
last_report: docs/qa/reports/2026-09-01-gate-cache-tool.md
overlaps: CFG-keep-local-artifacts-out-of-git
---

New promise from the gate result cache. `.gate-cache/` holds one JSON record and one log per run,
both keyed by fingerprint, and both must stay invisible to Git and absent from any package.

`CFG-keep-local-artifacts-out-of-git` owns the same promise for the runtimes that predate this
directory. It is frozen historical evidence under the baseline that `IT-006` enforces, so this cycle
mints a separate id rather than resetting that verdict.

Walked on 2026-09-01 at `aa2fbc6`. `.gitignore:23` carries `.gate-cache/`. A gate run through the
cache under a fresh label wrote a record and a log into `.gate-cache/`, after which Git reported
nothing through four independent read paths — `git status --porcelain`, `git status --porcelain
-uall`, `git ls-files`, and `git check-ignore -v .gate-cache` resolving to `.gitignore:23` — while
`git status --ignored --porcelain` listed `!! .gate-cache/`, so Git sees the directory and classifies
it as ignored rather than merely missing it. `bun pm pack --dry-run` listed 522 entries with nothing
under `.gate-cache/` and no fingerprint-named file, and a clean local clone contained no
`.gate-cache/` and reported a clean status.
