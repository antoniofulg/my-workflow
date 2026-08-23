# LESSONS - auto-maintained by scripts/lessons.py

> Machine-owned. Do NOT hand-edit. Changes are overwritten on the next `lessons.py` write.
> Canonical state lives in `.specs/lessons.json`. Edit lessons only via the script.
> promote_threshold=2 distinct features · window_days=45 · quarantine_threshold=2

## Confirmed (load these at Specify/Design)

Corroborated across multiple features. Safe to apply as guidance.

_none_

## Candidates (under observation - do NOT load as guidance yet)

Seen once or not yet corroborated. Tracked, not trusted.

### L-001 - Scope canonical test discovery so ignored QA evidence cannot change the gate.
- signal: `gate_fail` · recurrence: 1 feature(s) · scope: `release` · harmful: 0
- features: release-0.3.6
- evidence: .specs/features/release-0.3.6/validation.md:65 (release)
- last seen: 2026-08-23T06:43:47Z

### L-002 - Run diff hygiene across the full release range after previously ignored artifacts become tracked.
- signal: `gate_fail` · recurrence: 1 feature(s) · scope: `release` · harmful: 0
- features: release-0.3.6
- evidence: .specs/features/release-0.3.6/validation.md:66 (release)
- last seen: 2026-08-23T06:43:47Z

## Quarantined (failed when applied - ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
