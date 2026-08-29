# T5 task memory

- Shipped `tools/orca_assisted_probe.py` is stdlib-only and import-inert behind the `__name__` guard.
- Public `dispatch` persists the complete packet before sending one pointer; `inspect` performs a
  same-handle read. Existing lifecycle subcommands remain available for later effect/cleanup work.
- Focused probe contract: 5/5. Full offline gate: 111 Vitest tests and all Python suites passed.
