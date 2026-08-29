
- T1 scope: manifest/lock/config/version preload and eight canonical `.test.ts` suites.
- T1 keeps `tsx` and `yaml` temporarily; T2 owns direct knowledge execution and native YAML parsing.
- Existing release-contract assertions referencing npm/Vitest/package-lock must track the new Bun contract.
- `bun install --frozen-lockfile && bun test` passed 114 tests; the full Bun/Python gate also completed successfully before commit.
