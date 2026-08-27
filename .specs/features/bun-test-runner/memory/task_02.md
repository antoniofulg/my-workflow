# T2 task memory

- T2 migrates the eight structural TypeScript suites to `bun:test` and makes `npm test` invoke Bun.
- The native Bun run passes 115 tests across eight files with no fallback runner.
- Changed files: the eight `tools/**/*.test.ts` suites, `package.json`, and T2 traceability state.
