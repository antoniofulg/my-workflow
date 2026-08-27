# T4 task memory

- T4 restores the published v0.6.0 changelog section from its tag and moves pending removal and
  Bun runner notes into a v0.7.0 Unreleased section.
- The release contract compares exact v0.6.0 section bytes and keeps package metadata at 0.6.0.
- Changed files: `CHANGELOG.md`, the release assertion in `tools/shared/tests/qa-skills.test.ts`,
  and T4 traceability state.
