# T7 remediation memory

- T7R4 requires cleanup to independently derive the disposable repository HEAD and compare it with both the frozen workflow source head and ownership source head before any destructive effect.
- T7R4 persists an external cleanup tombstone with exact bounded residual paths. Restarted cleanup re-evaluates those paths and returns `cleaned: false` until no derived-sibling residual remains; only then is idempotent success valid.
- T7R4 canonical tests cover source-head-only attestation tampering and residual retry/sentinel survival. Real Orca remains fresh-QA-only and untested by the author.
