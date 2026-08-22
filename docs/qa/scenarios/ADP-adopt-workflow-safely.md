---
id: ADP-adopt-workflow-safely
area: ADP
title: Adopt the workflow without replacing consumer-owned state
persona: Workflow adopter
journey: J-adopt-workflow
expected: A fresh target receives the workflow resolver, tools/ad-index.py, and the workflow tour without the pack-only guide or dead links, while re-adoption preserves its workflow config, QA profile, model pins, consumer-modified tools/ad-index.py, and unrelated ignore entries byte-for-byte.
entry_points: README.md#adopt-the-workflow; scripts/adopt.py; .my-workflow.toml
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-22-source-only-pack-guide/session.md
last_report: docs/qa/reports/2026-08-22-source-only-pack-guide.md
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
