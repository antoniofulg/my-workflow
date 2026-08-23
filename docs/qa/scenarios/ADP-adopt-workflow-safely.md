---
id: ADP-adopt-workflow-safely
area: ADP
title: Adopt the workflow without replacing consumer-owned state
persona: Workflow adopter
journey: J-adopt-workflow
expected: A fresh target receives the workflow resolver, tools/ad-index.py, and a workflow tour without the pack-only guide or dead links; its instructions keep Ponytail active from workflow start through the full cycle; re-adoption preserves consumer-owned state; and projects using worktree handoffs or spec-reading gates are told to version their relevant feature specs.
entry_points: README.md#adopt-the-workflow; docs/guidelines/ARTIFACT-LIFECYCLE.md; scripts/adopt.py; .my-workflow.toml
qa_status: pass
bug_ids: BUG-20260822-deep-review-learnings-untrackable
fix_status: fixed
retest_status: pass
fix_commits: 0413862
evidence: docs/qa/evidence/2026-08-22-preserve-consumer-ad-index/session.md; docs/qa/evidence/2026-08-22-source-only-pack-guide/session.md; docs/qa/evidence/2026-08-22-version-feature-specs-handoff/session.md; docs/qa/evidence/2026-08-22-validate-generated-feature-contracts/session.md; docs/qa/evidence/2026-08-22-ponytail-full-cycle/session.md; docs/qa/evidence/2026-08-22-authoritative-validation-verdict/session.md; docs/qa/evidence/2026-08-22-deep-review-learnings-retest/session.md
last_report: docs/qa/reports/2026-08-22-deep-review-learnings-retest.md
overlaps:
---

Covers `CWF-ADOPT-1` through `CWF-ADOPT-3`: resolver installation, safe capability discovery,
managed-path review, initial profile creation, preservation of `.my-workflow.toml`, and the installed
hierarchy/resolution instructions when the workflow is adopted again.

For issue #36, fresh adoption must install `tools/ad-index.py`; after the consumer changes that file,
re-adoption must preserve its bytes.

For issue #37, `docs/workflow/pack.md` remains source-only. Fresh adoption receives the other tour
pages, and its copied index omits the pack-only links when the guide is absent.

QA on 2026-08-22 confirmed the source guide and its two links remain in the pack, fresh adoption
omits the guide and both links without losing the other five pages, all remaining local links
resolve, and re-adoption preserves a consumer-owned sentinel byte-for-byte.

QA on 2026-08-22 confirmed fresh installation and identical SHA-256 before and after re-adoption of
a consumer-modified `tools/ad-index.py`. The bundled-skill and release-contract canaries also passed.

QA for issue #39 confirmed initial adoption and re-adoption install byte-identical TLC validator
CLIs while preserving consumer-owned `.my-workflow.toml` and `docs/qa/README.md` byte-for-byte.

For issue #41, adoption documents Ponytail activation at workflow start and points to `AGENTS.md`
for the full-cycle persistence rule. QA on 2026-08-22 confirmed the installed `AGENTS.md`, Ponytail
skill, and workflow loop keep that contract through every TLC and review stage, preserve the two
explicit exits, and survive re-adoption without an implementation-only competing rule.

For issue #38, the adoption contract keeps `.specs/features/` ignored by default. A consuming
project that hands work off through Git worktrees or has a gate/CI job read the specs must remove
the managed ignore entry and version the relevant feature tree; adoption does not detect or migrate
that choice. QA on 2026-08-22 confirmed the default ignore, manual unignore, versioned spec handoff
to a sibling worktree, and a clean clone's independent read.

QA for issue #27 confirmed adoption and re-adoption install a validator byte-identical to the source
while preserving a consumer-owned `.my-workflow.toml` byte-for-byte.

Issue #28 requires a fresh adoption against a target that already ignores `.deep-review/`: the
durable `.deep-review/learnings.md` must be eligible for Git while other Deep Review artifacts stay
ignored, and re-adoption must remain idempotent. The canonical smoke test covers the Git contract;
QA on 2026-08-22 confirmed that contract through fresh adoption and byte-identical re-adoption.
