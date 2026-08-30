
- T1 scope: manifest/lock/config/version preload and eight canonical `.test.ts` suites.
- T1 keeps `tsx` and `yaml` temporarily; T2 owns direct knowledge execution and native YAML parsing.
- Existing release-contract assertions referencing npm/Vitest/package-lock must track the new Bun contract.
- `bun install --frozen-lockfile && bun test` passed 114 tests; the full Bun/Python gate also completed successfully before commit.
- T2 focused gate passed 114 tests; direct `bun run knowledge` completed with 32 warnings and exit 0, preserving the CLI's gap semantics.
- Verification remediation adds runtime-contract assertions and a temporary Bun 1.4 guard sensor; `.specs/features/bun-tooling-runtime/validation-s1.md` is verifier-owned and intentionally untouched.
