---
id: ADP-resolve-legacy-adoption-conflicts
area: ADP
title: Resolve reviewed legacy adoption conflicts safely
persona: Workflow adopter
journey: J-adopt-workflow
expected: A clean legacy Git project replaces exactly its reviewed workflow file conflicts, preserves project instructions, reaches clean managed status, and rejects incomplete or unsafe ownership transfers without writes.
entry_points: README.md#resolve-a-legacy-no-manifest-conflict; docs/adoption-prompt.md; scripts/adopt.py resolve
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
overlaps: ADP-layered-workflow-adoption; ADP-adopt-workflow-safely
---

Covers the public `resolve` ownership transition for projects copied from an older workflow release
before adoption manifests existed. The maintainer must review and repeat every current file conflict,
usually preserve `AGENTS.md` and `CLAUDE.md` with `--skip-agents`, and confirm clean status after the
one-time resolution.

The same disposable target must prove that omitted, extra, duplicate, absolute, escaping,
managed-block, dirty-target, non-Git, missing-`HEAD`, manifest-backed, and symlink-redirection cases
refuse before writes. Exact injected-failure rollback and direct-argv implementation mechanics stay
with technical verification; QA observes their public atomicity and no-unexpected-effect boundary.
