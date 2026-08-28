# T11 task memory

- Heavy gates use `ResourceProvider.acquire`/`release` with gate-specific correlated action keys;
  no lock file, daemon, or second dependency was introduced.
- `heavy_gates` state rejects a different lane or resource set for an existing gate and parks a
  competing resource claimant without calling the provider; release requires the owning lane.
