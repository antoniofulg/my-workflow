# Optional design tools QA

- **Date:** 2026-08-23
- **Branch/head:** `docs/optional-design-tools` at `6e792ae`
- **Diff:** `origin/main..HEAD`
- **Adapter:** Manual repository inspection
- **Environment:** Checkout-local source tree; no OpenDesign or Graft installation/execution
- **Entry paths:** `README.md`, `docs/guidelines/UI-UX.md`, `docs/guidelines/SECURITY.md`, `.specs/AD-INDEX.md`, `.specs/STATE.md`, `.agents/skills/deep-review/`
- **Automated gate:** PASS — `npm test` reported 146/146 tests across 11 files
- **Raw evidence:** `docs/qa/evidence/2026-08-23-optional-design-tools/session.md`
- **Limitation:** No live agent-execution harness. This run observes the public documentation and installed agent contracts, not third-party tool runtime behaviour. The feature has an independently validated inline acceptance contract but no `spec.md`.

## Matrix

| Charter | Scenario | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `CH-review-optional-design-tools-2026-08-23` | `DOC-use-optional-tools-with-repository-authority` | pass | Reloaded every public source from `HEAD` with `git show`; README, guidelines, and `AD-006` remained consistent | `docs/qa/evidence/2026-08-23-optional-design-tools/session.md` |
| `CH-confirm-graft-fallback-2026-08-23` | `QAS-use-graft-context-with-plain-fallback` | pass | Reloaded Deep Review skill and Graft adapter from `HEAD`; missing, failed, stale-version, and dot-directory paths retained plain inspection | `docs/qa/evidence/2026-08-23-optional-design-tools/session.md` |

## Probe results

| Probe | Result | Observable |
| --- | --- | --- |
| P01 — optional discovery | PASS | README names Graft and OpenDesign as optional capabilities in an agnostic workflow. |
| P02 — adoption installs neither | PASS | `scripts/adopt.py` performs no external-tool installation; Graft occurrences only manage ignore policy. |
| P03 — approved handoff and fallback | PASS | README and UI-UX keep approved artifacts in the repository and retain normal artifacts when OpenDesign is absent or fails. |
| P04 — source precedence | PASS | UI-UX and `AD-006` agree: `spec.md` → `uiux.md` → approved artifact → tool/plugin output → legacy mockup. |
| P05 — bounded writers | PASS | SECURITY requires isolation or explicitly allowed directories plus path/symlink validation before writing. |
| P06 — non-destructive import | PASS | Destination-only files are preserved and automatic deletion is forbidden. |
| P07 — operational-detail boundary | PASS | Public guidance contains no OpenDesign daemon address, port value, executable command, or pinned version. |
| P08 — durable decision | PASS | `AD-006` is active, indexed, optional, and repository-authoritative. |
| P09 — missing/failed Graft | PASS | Missing CLI and build, map, symbol, or blast-radius failure paths explicitly retain plain inspection. |
| P10 — stale/partial Graft | PASS | Version mismatch becomes unavailable; dot-directories use plain inspection; available context remains orientation requiring checkout verification. |

The first P04 sensor attempt compared a wrapped decision as a byte-exact phrase and stopped. One clean
retry normalized whitespace, then all 10 probes passed through the independent `git show HEAD:<path>`
read path. This was a sensor correction, not a product retry.

## Closing gate

| Command | Result |
| --- | --- |
| `npm test` | PASS — 146/146 tests across 11 files |
| `python3 scripts/test_adopt.py` | PASS — `ok`; disposable targets cleaned by the suite |
| `python3 tools/ad-index.py --check` | PASS — index current |
| `python3 tools/test_ad_index.py` | PASS — `ok` |
| `python3 tools/test_workflow_config.py` | PASS — 11/11 |
| `python3 tools/test_tlc_validators.py` | PASS — 9/9 |
| `python3 tools/test_deep_review_token_metrics.py` | PASS — 19/19 |
| `npm run knowledge` | PASS — 0 errors; 13 non-gating harvest warnings |
| `git diff --check origin/main..HEAD` | PASS |

## Debrief

Both planned charters passed. Ten probes passed, including the adjacent Graft canary. No defect was
found and no bug record was created. No external tool, network operation, server, installation, or
product mutation occurred. Raw evidence is ignored; this report and both scenario verdicts are the
durable outputs.
