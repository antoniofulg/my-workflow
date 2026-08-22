# BUG-20260822-adoption-omits-graft-ignores

- **Status:** fixed — retest passed
- **Severity:** major
- **Scenario:** `CFG-keep-local-artifacts-out-of-git`
- **Expected:** Adoption installs the Graft ignore contract so `graft/.cache/` and `graft/.graph/` stay out of Git while generated cards remain searchable.
- **Observed:** `scripts/adopt.py` preserves consumer ignores and installs the Deep Review/spec entries, but adds no Graft Git/search-ignore entries. Both cache paths remain Git-eligible in a freshly adopted target.
- **Adapter:** adoption CLI plus Git/filesystem inspection
- **Exact path:** `python3 scripts/adopt.py docs/qa/evidence/2026-08-22-deep-review-metrics-graft/hygiene-target`, then `git -C <target> check-ignore -v graft/.cache/index.json graft/.graph/wiring.json`
- **Evidence:** `docs/qa/evidence/2026-08-22-deep-review-metrics-graft/session.md`
- **Fix commit:** `b509b10`
- **Retest:** PASS on 2026-08-22 through a fresh disposable adoption target; adjacent Graft canary also passed.

## Reproduction

1. Initialize an empty disposable Git repository with an unrelated consumer `.gitignore` entry.
2. Run the public adoption CLI against it.
3. Create `graft/.cache/index.json`, `graft/.graph/wiring.json`, and a generated Graft card.
4. Run `git check-ignore -v` for those paths.

The cache and graph files are reported `ELIGIBLE`. The unrelated consumer entries survive, and
Deep Review/spec disposable paths are ignored correctly.

## Smallest remediation

Make adoption install the same Graft Git/search-ignore contract shipped by the pack without
overwriting unrelated consumer entries. Extend the canonical adoption smoke test with cache,
graph, card-search, and consumer-ignore assertions.

## Fix and retest

`b509b10` installs the managed Git/search-ignore entries without replacing consumer-owned lines.
Fresh adoption ignored `graft/.cache/index.json` and `graft/.graph/wiring.json`, kept the generated
card searchable, preserved both consumer sentinels, and retained durable workflow files as
reviewable. The original reproduction no longer reproduces.
