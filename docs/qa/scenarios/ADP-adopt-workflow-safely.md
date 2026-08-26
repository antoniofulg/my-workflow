---
id: ADP-adopt-workflow-safely
area: ADP
title: Adopt the workflow without replacing consumer-owned state
persona: Workflow adopter
journey: J-adopt-workflow
expected: A fresh target receives the workflow resolver, tracked example/templates, initialized local config, generated runtime packets, tools/ad-index.py, and a valid workflow tour; re-adoption preserves consumer-owned local state, creates no removed integration artifacts, and leaves host-boundary sentinels unchanged.
entry_points: README.md#adopt-the-workflow; docs/guidelines/ARTIFACT-LIFECYCLE.md; scripts/adopt.py; .my-workflow.toml.example; .my-workflow.toml; templates/agents/
qa_status: pass
bug_ids: BUG-20260822-deep-review-learnings-untrackable; BUG-20260822-feature-specs-ignored; BUG-20260822-feature-state-gate-conflicts; BUG-20260825-scenario-pass-report-field; BUG-20260825-adoption-omits-parallel-pilot
fix_status: fixed
retest_status: pass
fix_commits: 0413862; a7397d2; 43e9910; a3fc718; 5b5474e; 816afd6; 1593299
evidence: docs/qa/evidence/2026-08-25-release-0-6-0/session.md; docs/qa/evidence/2026-08-25-release-0-6-0/retest-adoption.json; docs/qa/evidence/2026-08-25-release-0-6-0/retest-contracts.json; docs/qa/evidence/2026-08-25-release-0-6-0/retest-package-summary.json; docs/qa/evidence/2026-08-25-release-0-6-0/retest-protected-history.json; docs/qa/evidence/2026-08-25-release-0-6-0/retest-reference-scan.json
last_report: docs/qa/reports/2026-08-25-release-0-6-0.md
overlaps:
---

QA retest on 2026-08-25 after fix `1593299` passed the v0.6.0 host-neutral adoption walk. Two
public CLI runs against a disposable project produced stable managed bytes, preserved project and
host sentinels, generated all six fresh reviewer packets, and created zero removed integration
artifacts or source markers. Independent JSON reloads back the verdict; see the dated release
report and retest evidence above.

Covers `CWF-ADOPT-1` through `CWF-ADOPT-3`: resolver installation, tracked-source discovery,
managed-path review, initial profile creation, preservation of `.my-workflow.toml` and templates,
runtime regeneration, and the installed hierarchy/resolution instructions when adopted again.

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

QA for issue #27 confirmed adoption and re-adoption install a validator byte-identical to the source
while preserving a consumer-owned `.my-workflow.toml` byte-for-byte.

Issue #28 requires a fresh adoption against a target that already ignores `.deep-review/`: the
durable `.deep-review/learnings.md` must be eligible for Git while other Deep Review artifacts stay
ignored, and re-adoption must remain idempotent. The canonical smoke test covers the Git contract;
QA on 2026-08-22 confirmed that contract through fresh adoption and byte-identical re-adoption.

Issue #31 replaces the former opt-in handoff policy: `.specs/features/` is always versioned workflow
state. Fresh adoption must leave it visible to Git; migration removes only exact legacy ignore
entries, preserves unrelated target lines, and does not stage or commit consumer files.

QA on 2026-08-22 confirmed fresh visibility, exact legacy migration, byte-idempotent re-adoption,
unchanged `HEAD` and index, and feature-state handoff through a sibling worktree and clean clone.

QA on 2026-08-25 retained this verdict as an adjacent canary: fresh adoption included the tracked
remediation example, re-adoption preserved a consumer-owned local config byte-for-byte, and only
printed the external security installer command without invoking it.

QA on 2026-08-25 reconfirmed the retained verdict for Parallel Deep Review: package membership
included all changed Deep Review surfaces; two adoptions installed source-identical files,
preserved consumer-owned bytes, retained tracked lock provenance, and only printed the external
installer command.

QA on 2026-08-25 found the `0.6.0` adoption regression: executor and adapter files install, but the
public `tools/qa_parallel_pilot.py` lifecycle entry point does not. See
`BUG-20260825-adoption-omits-parallel-pilot`.

Fresh QA after `816afd6` passed the affected adoption journey. The pilot installed with exact source
bytes, an intentionally stale managed copy was repaired, two re-adoptions preserved consumer-owned
configuration byte-for-byte, and all 15 generated provider packets remained unchanged. The linked
release/package canary also passed; see the current report.
