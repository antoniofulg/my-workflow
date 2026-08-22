# BUG-20260822-security-installer-rejects-active-npx

- **Status:** fixed
- **Severity:** major
- **Scenario:** `ADP-install-pinned-external-security-skills`
- **Expected:** The documented authorized command uses the installed Node/npm/npx toolchain to fetch and install the three pinned security skills into the disposable target.
- **Observed:** Node, npm, and npx are installed and active through mise, but the installer searches only `/opt/homebrew/bin`, `/usr/local/bin`, `/usr/bin`, and `/bin`; it exits `1` with `trusted npx executable unavailable` before network access or installation.
- **Adapter:** public external-security installer CLI plus independent executable and filesystem inspection
- **Exact path:** `python3 scripts/install_security_skills.py docs/qa/evidence/2026-08-22-external-security-skills/targets/adopt-target --yes`
- **Evidence:** `docs/qa/evidence/2026-08-22-external-security-skills/session.md`
- **Fix commit:** `1fa087d`; `7795295`
- **Retest:** pass at `11de55a`; the exact public command used the active mise npx, returned `0`, and installed all three pinned trees with matching hashes and links

## Reproduction

1. Use the repository's active mise Node 22 toolchain, where `node`, `npm`, and `npx` resolve under
   `/Users/antoniofulg/.local/share/mise/` and `npx --version` returns `10.9.8`.
2. Adopt into a checkout-local disposable target and review the printed command.
3. Run that exact command with explicit `--yes` authorization.
4. Reload the target and inspect the exit, installed trees, locks, and transaction residue.

At `b9024ea`, the command exited `1` before network access and installed no external skill. Rollback
did work: the whole-target digest, unrelated lock bytes, consumer skill bytes, and Claude link
remained exact; no transaction or target-lock residue remained.

## Retest

A fresh Verifier reran the affected journey and adjacent adoption canary at `11de55a`. The active
mise shim at `/Users/antoniofulg/.local/share/mise/shims/npx` remained the selected executable, the
authorized command exited `0`, and independent filesystem reads confirmed all three lock hashes and
Claude links. See
`docs/qa/evidence/2026-08-22-external-security-skills/session.md`.

## Smallest remediation

Provide a secure, documented way for the public installer to resolve the project's active npx
executable without requiring a machine-global system-directory installation. Keep executable trust
validation and environment scrubbing. Add a public-command regression case using an isolated
non-system Node toolchain path.
