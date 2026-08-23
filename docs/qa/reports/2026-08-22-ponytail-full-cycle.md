# QA Execute — Ponytail full cycle

- **Date:** 2026-08-22
- **Scope:** issue #41, full-cycle Ponytail activation after adoption
- **Adapter:** CLI/manual via `python3 scripts/adopt.py <target>` plus filesystem inspection
- **Environment:** active checkout `docs/ponytail-full-cycle`; checkout-local disposable Git target
- **Initial gate:** `npm test` — PASS, 10 files and 140 tests
- **Raw evidence:** `docs/qa/evidence/2026-08-22-ponytail-full-cycle/`
- **Limitation:** installed contracts are observable; live model compliance remains manual observation

## Matrix

| Charter | Scenario | Verdict | Evidence |
| --- | --- | --- | --- |
| `CH-adopt-ponytail-full-cycle-2026-08-22` | `ADP-adopt-workflow-safely` | pass | `docs/qa/evidence/2026-08-22-ponytail-full-cycle/session.md` |
| Adjacent provenance/security canary | `DOC-read-explicit-workflow-provenance` | pass | `docs/qa/evidence/2026-08-22-ponytail-full-cycle/session.md` |

## Results

- Public README activates Ponytail `full` at workflow start and delegates full-cycle scope and exits
  to the installed authorities.
- Fresh adoption exited 0. Installed `AGENTS.md` covers Specify, Design, Tasks, Execute, subagent
  prompts, fixes, and reviews.
- Installed Ponytail skill owns `ACTIVE EVERY RESPONSE` and the two exits: `stop ponytail` and
  `normal mode`.
- Installed workflow loop summarizes the authority split and carries no competing
  implementation-only activation rule.
- Re-adoption exited 0, preserved the three installed authority hashes, and preserved a
  consumer-owned QA-profile marker byte-for-byte.
- Bundled-versus-external security-skill language and QA-skill provenance remained intact.

## Debrief

Expected and observed results matched. No product defect found. Live model compliance remains a
manual observation outside this repository's CLI/manual adapter.

## Final gate

- Relevant: `npx vitest run tools/shared/tests/qa-skills.test.ts` — PASS, 1 file and 22 tests.
- Full: `npm test` — PASS, 13 files and 178 tests.
- Diff hygiene: `git diff --check` — PASS.
