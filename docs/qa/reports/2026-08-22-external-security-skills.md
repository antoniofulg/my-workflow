# QA Execute — external security skills

- **Date:** 2026-08-22
- **Scope:** Explicit external-security adoption, authorized installation, target preservation, and public provenance
- **Environment:** `feat/external-security-skills` resumed at `11de55a`, active checkout, macOS, CLI/manual adapter
- **Adapter:** `scripts/adopt.py` and `scripts/install_security_skills.py` against checkout-owned disposable targets; independent filesystem and repository reads
- **Preflight gate:** `npm test` — 10 files passed; 138 tests passed; 0 failed; 0 skipped
- **Raw evidence:** `docs/qa/evidence/2026-08-22-external-security-skills/session.md`
- **Limitations:** No browser, API, mobile, auth, server, or live agent-execution harness exists. Hostile staged-file, process-race, and interrupted-publication controls remain technical-verification surfaces.

## Matrix

| Charter | Scenario | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `CH-adopt-external-security-skills-2026-08-22` | `ADP-separate-external-security-skills` | pass | Reload found all three external trees and links absent; output matched the absolute pack installer, target, `--yes`, and gate warning. | `docs/qa/evidence/2026-08-22-external-security-skills/session.md` |
| `CH-adopt-external-security-skills-2026-08-22` | `ADP-adopt-workflow-safely` | pass | SHA-256 reloads matched for config, QA profile, model pin, and consumer sentinel; a second adoption left the merged ignore bytes unchanged. | `docs/qa/evidence/2026-08-22-external-security-skills/session.md` |
| `CH-enable-external-security-skills-2026-08-22` | `ADP-install-pinned-external-security-skills` | pass | Fresh retest used the active mise npx, returned `0`, and independently matched all three installed tree hashes and Claude links to the reviewed lock. | `docs/qa/evidence/2026-08-22-external-security-skills/session.md`; `BUG-20260822-security-installer-rejects-active-npx` |
| `CH-enable-external-security-skills-2026-08-22` | `ADP-preserve-security-install-target` | pass | Success preserved five consumer sentinels, the consumer link and unrelated lock bytes; plan-only and `latest` refusal preserved exact whole-target digests with no residue. | `docs/qa/evidence/2026-08-22-external-security-skills/session.md` |
| `CH-review-external-security-provenance-2026-08-22` | `DOC-read-explicit-workflow-provenance` | pass | README, pack guide, lock and installed trees agreed on the separate authorization boundary and all reviewed provenance fields. | `docs/qa/evidence/2026-08-22-external-security-skills/session.md` |
| `CH-review-external-security-provenance-2026-08-22` | `REL-report-capability-version-0-3-0` | skipped | The version-specific `0.3.0` promise is obsolete; the current package, lock root and root package independently agreed on `0.3.4`. | `docs/qa/evidence/2026-08-22-external-security-skills/session.md` |

## Charter debriefs

### CH-adopt-external-security-skills-2026-08-22

**Verdict: pass.** `python3 scripts/adopt.py <checkout-local-target>` printed the exact absolute
installer and target command with `--yes`, named the external-versus-bundled boundary, and warned
that the security gate remained uncovered. Independent reads found none of the three external names
under `.agents/skills/` or `.claude/skills/`. Re-adoption preserved consumer config, QA profile,
model pin, sentinel, and merged ignore bytes.

### CH-enable-external-security-skills-2026-08-22

**Original verdict: fail.** Plan-only execution returned `2`, printed exactly three `skills@1.5.23`
commands with reviewed refs, left the whole target unchanged, and created no lock. The explicitly
authorized command returned `1` before network access with `trusted npx executable unavailable`.
Independent inspection found active mise Node/npm/npx executables and npx `10.9.8`, but none under
the installer's four hard-coded trusted directories. Rollback preserved the whole target exactly
and left no lock, staging, snapshot, or external-skill residue. Execution stopped per the fix loop.

**Fresh retest verdict: pass.** At `11de55a`, the exact printed command kept the active mise shim,
returned `0`, and installed exactly three external skill trees. Independent path-plus-byte hashes
matched every `skills-lock.json` hash, and each Claude link resolved to its matching shared tree.
Success preserved the consumer config, QA profile, model pin, skill, sentinel, link, top-level lock
metadata, and unrelated lock-member bytes. A disposable-pack `latest` mutation returned `1`, named
the uncovered gate, preserved the whole-target digest exactly, and left no transaction residue.

### CH-review-external-security-provenance-2026-08-22

**Verdict: pass.** README, pack guide, `skills-lock.json`, installed trees and public adoption
output agreed on the three names, GitHub sources, canonical paths, CLI `1.5.23`, immutable refs,
hashes, and separate authorization boundary. Bundled source trees and `adopt.py` excluded the three
external skills. The release canary found all current metadata at `0.3.4`; the obsolete literal
`0.3.0` scenario was retired with `skipped` instead of carrying a false current promise.

## Edge probes and lenses

1. Missing `--yes` — pass; exit `2`, exact three-command plan, zero target mutation.
2. Active non-system npx path — pass; the mise shim executed the authorized install successfully.
3. Exact installed set — pass; three external trees and three matching links, with no fourth tree.
4. Installed provenance — pass; all path-plus-byte hashes and reviewed lock metadata matched.
5. Success preservation — pass; consumer files, link and unrelated lock bytes survived.
6. Moving metadata — pass; `latest` was refused before publication with exact target restoration.
7. External-tree absence before authorization — pass; all three agent and Claude paths were absent.
8. Re-adoption preservation — pass; config, profile, model pin, sentinel and ignore entries survived.

Comprehension, recovery, trust, speed and language passed through concise plan/output, deterministic
refusal, active-toolchain success, exact provenance, and clear gate warnings. Accessibility has no
separate modality for this CLI/manual surface. Hostile staged-file, race, and interrupted-publication
controls remain technical-verification surfaces as declared by the profile.

## Findings

`BUG-20260822-security-installer-rejects-active-npx` — major, fixed by `1fa087d` and `7795295`,
fresh retest passed at `11de55a`. The affected scenario and adjacent adoption canary both pass.

## Final gate

`npm test` — 10 test files passed; 138 tests passed; 0 failed; 0 skipped. `git diff --check`
returned `0`. The disposable target, nested Git repository, staging copy and refusal pack were moved
to Trash after their residue checks; they are recoverable until Trash is emptied. Ignored raw
evidence remains at `docs/qa/evidence/2026-08-22-external-security-skills/session.md`. No report row
remains pending, and the cycle is closed.
