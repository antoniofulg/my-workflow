# QA report — source-only pack guide — 2026-08-22

## Session

- **Adapter:** CLI/manual filesystem inspection
- **Entry point:** `README.md` → **Adopt the workflow** → `python3 scripts/adopt.py <target>`
- **Environment:** active checkout `fix/keep-pack-source-only`; checkout-local disposable target
- **Raw evidence:** `docs/qa/evidence/2026-08-22-source-only-pack-guide/session.md`
- **Initial gate:** `npm test` — pass, 10 files and 139 tests

## Matrix

| Charter | Scenario | Verdict | Observable | Evidence |
| --- | --- | --- | --- | --- |
| `CH-adopt-source-only-pack-guide-2026-08-22` | `ADP-adopt-workflow-safely` | pass | Fresh adoption omitted `pack.md` and its links, retained the other five tour pages, and re-adoption preserved consumer-owned bytes. | `docs/qa/evidence/2026-08-22-source-only-pack-guide/session.md` |
| Adjacent provenance canary | `DOC-read-explicit-workflow-provenance` | pass | Source `pack.md` and both source-tour links remained valid; the guide still identifies the security skills as external dependencies. | `docs/qa/evidence/2026-08-22-source-only-pack-guide/session.md` |

## Results

**Verdict: pass.** The source checkout retained `docs/workflow/pack.md`, both source-tour links
resolved to it, and its external-security-skill provenance statement remained present. Fresh
adoption through the documented CLI omitted the guide and both links while retaining `purpose.md`,
`loop.md`, `reviews.md`, `decisions.md`, and `guidelines.md`.

Every remaining local link in the adopted tour resolved. A second adoption preserved the
consumer-owned `.my-workflow.toml` sentinel and the filtered tour byte-for-byte. No product defect
was found.

## Final gate

- `python3 scripts/test_adopt.py` — pass (`ok`)
- `npm test` — pass, 10 files and 139 tests
- `git diff --check` — pass

The checkout-local disposable target was moved to Trash after evidence capture; no target residue
remains in the active checkout.
