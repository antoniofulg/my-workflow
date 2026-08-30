# CH-enable-bun-security-skills-2026-08-29

- **Date:** 2026-08-29
- **Scope:** `69914e831cb8..38796e825360` for `bun-tooling-runtime`
- **Time-box:** 20 minutes without network; 35 minutes when network/write is explicitly authorized
- **Persona:** Workflow adopter
- **Journey:** [`J-enable-external-security-skills`](../journeys/J-enable-external-security-skills.md)
- **Tour:** Locked Bun external-skill transaction and fail-closed refusal
- **Public entry point:** `scripts/adopt.py` output → `scripts/install_security_skills.py`
- **Adapter candidate:** CLI/manual through [`docs/qa/README.md`](../README.md)
- **Bun contract scenario:** [`REL-report-current-workflow-release`](../scenarios/REL-report-current-workflow-release.md)
- **Journey canaries:** [`ADP-install-pinned-external-security-skills`](../scenarios/ADP-install-pinned-external-security-skills.md); [`ADP-preserve-security-install-target`](../scenarios/ADP-preserve-security-install-target.md)
- **Adjacent adoption canary:** [`ADP-adopt-workflow-safely`](../scenarios/ADP-adopt-workflow-safely.md)

## Mission

Inspect the no-write plan and fail-closed Bun executable boundary in a disposable target. When the
QA Execute packet explicitly authorizes network and target writes, also confirm the successful
locked transaction. Never infer that authorization from this charter.

## Expected observable

The no-authorization path prints exactly three pinned `bunx --bun --no-install` add commands and
writes nothing; missing, unsafe, failing, or wrong-version local CLI preflight returns non-zero
before any add operation and preserves target bytes; an explicitly authorized success installs only
the three reviewed trees and links after one matching-version preflight.

## Planned walk

1. From a disposable adopted target, run the installer without `--yes`; reload the plan and confirm
   the fixed Bun argv, reviewed lock metadata, and zero target changes.
2. Exercise missing and wrong-version locally resolvable CLI preflights in disposable pack copies;
   confirm non-zero exit, zero add calls, no npm/npx/fetch fallback, and unchanged sentinels.
3. If and only if the packet explicitly authorizes network/write, run the printed command against a
   new disposable target; independently inspect the three trees, links, lock entries, one preflight,
   and one add per skill.
4. Re-run the adoption canary and confirm bundled workflow state remains independent from the
   external installation step.

## Boundaries

Without explicit network/write authorization, stop after step 2 and leave the successful-install
Bun contract in `REL-report-current-workflow-release` untested. Never point the installer at a real
project or substitute a fake success.
