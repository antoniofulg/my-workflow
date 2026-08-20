# Project decision index

One line per `AD-NNN`. The append-only body lives in `.specs/STATE.md`.

Body: `rg -A 20 '^### AD-NNN' .specs/STATE.md`. Resume: `rg -A 20 '^## Handoff' .specs/STATE.md`.
When recording an `AD-NNN`, run `python3 tools/ad-index.py` in the same commit.

| ID | Status | Decision |
| --- | --- | --- |
| `AD-001` | active | Agent always-on is a thin `AGENTS.md` (contract + pointers). |
