# T13 task memory

- Convergence state now validates and normalizes legacy flat entries into append-only generations;
  persisted state uses version 2 while retaining cumulative top-level fields.
- A halted fingerprint can advance only through `resume(...)` with a relative anchor reference.
  Generation 1 and its halt event remain immutable; generation 2 starts at local count zero.
- Resumed closure requires `independent=True`, a green gate, and a repository-relative evidence
  reference. Failed and non-qualifying results leave the generation open; three failures halt it.
- The real halted CP-S4 fingerprint still requires the exact authorization anchor from
  `decisions.md`; T14 must invoke the CLI resume operation before mutation work.
