
- S1 migrates the active TypeScript runner to Bun 1.4.x; historical evidence remains unchanged.
- Bun 1.4.0 is installed in this environment; structural tests use Bun's Jest-compatible `bun:test` API.
- T1 leaves `tsx` and `yaml` installed for the T2 knowledge-boundary transition; Vitest and npm's lockfile are removed.
