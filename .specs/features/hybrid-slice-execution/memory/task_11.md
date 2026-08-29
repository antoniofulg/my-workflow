# T11 task memory

- Heavy gates use `ResourceProvider.acquire`/`release` with gate-specific correlated action keys;
  no lock file, daemon, or second dependency was introduced.
- `heavy_gates` state rejects a different lane or resource set for an existing gate and parks a
  competing resource claimant without calling the provider; release requires the owning lane.
- Resumed scheduler capacity is re-derived from the frozen cap: explicit caps clamp persisted
  capacity, automatic caps must remain inside the baseline/ceiling, and malformed state fails
  before adapter, worktree, or provider effects.
- Persisted heavy-gate leases carry exact feature/slice/task/gate/action/request identity. Their
  acquire and release actions must correlate before a provider call; forged or foreign state fails
  closed with zero release effect.
