# QA Execute — preserve consumer AD index

- **Date:** 2026-08-22
- **Scope:** Fresh adoption and re-adoption preservation of consumer-owned `tools/ad-index.py`
- **Environment:** `fix/preserve-consumer-ad-index` at `66cd1ae`, active checkout, macOS, CLI/manual adapter
- **Adapter:** `scripts/adopt.py` against a checkout-owned disposable Git target; independent byte and filesystem reads
- **Preflight gate:** `npm test` — 10 files passed; 138 tests passed; 0 failed; 0 skipped
- **Raw evidence:** `docs/qa/evidence/2026-08-22-preserve-consumer-ad-index/session.md`
- **Limitations:** No browser, API, mobile, auth, server, or live agent-execution harness exists.

## Matrix

| Charter | Scenario | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `CH-preserve-consumer-ad-index-2026-08-22` | `ADP-adopt-workflow-safely` | pass | Fresh target matched the pack AD-index hash; the consumer sentinel retained the same SHA-256 after re-adoption, executed successfully, and adjacent bundled-skill/release checks passed. | `docs/qa/evidence/2026-08-22-preserve-consumer-ad-index/session.md` |

## Charter debrief

**Verdict: pass.** Fresh adoption created `tools/ad-index.py` with the same SHA-256 as the pack.
After the consumer replaced it, re-adoption returned `0` and retained the exact pre-run SHA-256.
The preserved sentinel executed successfully. Independent reads confirmed the adopted TLC and Deep
Review assets, Claude link, current `0.3.4` package metadata, and separate security-install boundary.

## Edge probes and lenses

1. Empty Git target — pass; fresh adoption installed `tools/ad-index.py`.
2. Source equality — pass; fresh target and pack source shared SHA-256 `53431a...e82`.
3. Consumer replacement — pass; sentinel SHA-256 captured before re-adoption.
4. Re-adoption — pass; command exited `0` and sentinel SHA-256 remained `f7c725...d45`.
5. Independent execution — pass; preserved sentinel printed `consumer ad index`.
6. Managed assets — pass; TLC, Deep Review, QA profile and Claude TLC link remained present.
7. Release canary — pass; package and lock roots agreed on `0.3.4`, and README retained the
   separate external-security authorization contract.

Comprehension, recovery and trust passed through explicit CLI output and byte-preservation proof.
Speed and language presented no divergence. Accessibility has no separate modality for this CLI.

## Findings

No new product defect. Issue #36's reported overwrite did not reproduce at `66cd1ae`.

## Final gate

`python3 scripts/test_adopt.py` returned `ok`. `npm test` passed 10 test files and 138 tests with
zero failures or skips. `git diff --check` returned `0`. The disposable nested Git target was moved
to `/Users/antoniofulg/.Trash/my-workflow-qa36-target-20260822`; it remains recoverable until Trash
is emptied. Ignored raw evidence remains at
`docs/qa/evidence/2026-08-22-preserve-consumer-ad-index/session.md`. No report row remains pending.
