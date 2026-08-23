# Shared feature memory

- Canonical skill packages live only under `.agents/skills`; provider packets consume them by name.
- QA remains stack-agnostic: the consuming project's `docs/qa/README.md` selects an existing
  browser, API, CLI, mobile, or manual adapter and points at executable manifests or CI.
- The QA skills use clean-room wording and preserve explicit attribution to their corresponding
  Pedro Nauck inspirations.
