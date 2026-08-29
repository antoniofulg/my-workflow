# T9 task memory

- `machine_health.py` exposes normalized stdlib evidence and `should_admit_lane`; tests inject
  readers and monotonic time so no host-specific data is needed.
- Admission caps are never raised by health: automatic ceiling is four, explicit caps remain exact,
  and health is required only when active writers are already at the two-writer baseline.
- Invalid, stale, future, pressured, and unknown evidence normalizes to non-admitting output with
  only enums, counts, monotonic timestamp, and booleans.
