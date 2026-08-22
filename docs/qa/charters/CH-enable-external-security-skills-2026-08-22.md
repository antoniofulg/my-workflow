# CH-enable-external-security-skills-2026-08-22

- **Date:** 2026-08-22
- **Time-box:** 30 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-enable-external-security-skills`](../journeys/J-enable-external-security-skills.md)
- **Tour:** Authorization, provenance, preservation, and refusal tour
- **Public entry point:** `scripts/adopt.py` output → `scripts/install_security_skills.py`
- **Adapter candidate:** CLI/manual through the public installer and independent filesystem reads
- **Scenarios:** `ADP-install-pinned-external-security-skills`, `ADP-preserve-security-install-target`

## Mission

Review the plan without authorization, then—only when the QA packet explicitly authorizes network
access and writes—run the printed command against a checkout-local disposable target. Confirm exact
pins, trees, links, preserved sentinels, and one safe public refusal from a disposable pack copy.

## Expected observable

Plan-only use returns `2` without mutation; authorized use installs exactly the three reviewed trees
and links while preserving unrelated bytes; rejected metadata returns non-zero, restores the target,
and leaves a clear gate-unavailable message.

## Planned probes

- Snapshot target bytes and Git state before every command; reload them through independent reads.
- Run without `--yes`; capture status, plan, zero target diff, and zero network-install residue.
- Compare each lock entry with the plan, installed tree, and Claude link after authorized execution.
- Confirm no fourth external tree appears and unrelated files and raw lock members retain their bytes.
- From a disposable pack copy, replace one reviewed ref with `latest`; confirm refusal occurs before
  publication and the pre-install target and gate-unavailable warning survive.
- Record the selected executable path, network authorization, cleanup, residue check, and any
  limitation reaching hostile staged-file, race, or interrupted-publication controls.
- Adjacent canary: recheck `ADP-adopt-workflow-safely` through the adoption charter.

End before product remediation. A confirmed defect returns to an Implementer.
