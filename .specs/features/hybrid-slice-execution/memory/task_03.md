# T3 task memory

- Public config and frozen snapshots now require version 3. The only modes are `assisted` and
  `disabled`; omitted settings resolve to `assisted` and `max_workers = "auto"`.
- Snapshots freeze automatic baseline 2 and ceiling 4. Version 1/2 active snapshots fail with the
  documented refresh instruction and are never rewritten by resume.
- The feature snapshot was explicitly refreshed with the resolver before this task commit. Its
  route remains `disabled`, `auto`, baseline 2, ceiling 4, and no resource provider.
- Planner and executor readers consume the same v3 parallelization keys. Runtime state remains an
  internal version-1 artifact.
