# T12 task memory

- Adoption now copies `tools/orca_assisted_probe.py` beside the existing pilot and installs only
  the workflow-owned `workflow-spec-driven` authority; both old TLC paths are removed on re-adopt.
- Adoption preflights every managed destination and fails before any write when a managed path is a
  symlink, protecting consumer-owned files and external targets.
- The canonical adoption suite covers v3 config, byte identity, consumer config/QA preservation,
  import-time zero Orca calls, QA registry truth, and unsafe destination refusal.
- Public adoption/configuration scenarios were reset to `untested` for fresh QA after the v3
  behavior change. The real Orca scenario remains `blocked-verify`; fake-provider checks do not
  convert that live-host status.
