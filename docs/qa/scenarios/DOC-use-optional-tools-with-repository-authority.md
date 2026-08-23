---
id: DOC-use-optional-tools-with-repository-authority
area: DOC
title: Use optional tools without surrendering repository authority
persona: Repository reader
journey: J-review-workflow-release
expected: The workflow recommends Graft and OpenDesign without installing or requiring them, preserves repository fallback and explicit approved-handoff precedence, bounds external writes non-destructively, and omits operational tool setup from public guidance.
entry_points: README.md#optional-integrations; docs/guidelines/UI-UX.md#optional-design-tooling; docs/guidelines/SECURITY.md#external-filesystem-writers; .specs/AD-INDEX.md; .specs/STATE.md
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
overlaps:
---

Covers the public part of `AD-006`: optional capability recommendations do not become adoption
dependencies, the repository remains authoritative when tools are absent or fail, approved visual
artifacts follow the documented precedence, and filesystem-writing integrations preserve
destination-only files without automatic deletion. Concrete installation, daemon, port, CLI, and
version details remain outside the public guidance and route to the relevant integration skill.
