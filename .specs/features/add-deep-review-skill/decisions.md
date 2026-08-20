# Feature decisions

These decisions are local to `add-deep-review-skill`. Human decisions are separated from choices
made during implementation.

## Human decisions

### Install the upstream skill and release 0.2.2

- **Choice:** Install `deep-review` from `pedronauck/skills` and release the project as `0.2.2`.
- **Reason:** Make the referenced Deep Review workflow available in the repository and associate it
  with the requested release.
- **Alternatives rejected:** Keep the skill as a global dependency, copy only `SKILL.md`, or defer
  the release version update. Those options would leave fresh checkouts without the complete skill or
  without the requested release metadata.
- **Cost to change now:** Reinstalling from another source or changing the release version requires
  updating the vendored files, lock metadata, manifests, tests, and release notes.
- **Cost to the user today:** A consumer gets a reproducible skill bundle and versioned release
  metadata instead of relying on local installation state.

### Authorize the post-cap fix and delivery

- **Choice:** After the two-round Deep Review cap, authorize the fix for the single remaining Major
  finding without opening a third round, then proceed with push, PR, merge, and release.
- **Reason:** The finding was narrow, the fix was explicitly approved, and the review cap prevents an
  unbounded loop.
- **Alternatives rejected:** Open a third Deep Review round, leave the Major unresolved, or stop
  before delivery. The first breaks the round cap; the others leave an approved blocking issue or an
  unfinished release.
- **Cost to change now:** Reopening the review policy would require another review pass and a new
  validation report before delivery.
- **Cost to the user today:** The approved fix ships within the bounded workflow, with the final
  validation evidence available before release.

## Agent decisions

### Preserve upstream content without a local fork

- **Choice:** Keep `.agents/skills/deep-review/**` as the upstream-installed content and do not fork
  or edit it locally.
- **Reason:** The repository should track the source supplied by Pedro Nauck and make future updates
  attributable to that source.
- **Alternatives rejected:** Patch the skill in place, fork it into project-owned code, or add a
  compatibility copy. Those choices split ownership and make upstream updates harder to audit.
- **Cost to change now:** A local behavior change must be proposed upstream or introduced as a
  separate project-owned integration layer.
- **Cost to the user today:** The user receives the upstream behavior unchanged, with fewer local
  maintenance obligations.

### Protect the integration at the project boundary

- **Choice:** Pin `skills@1.5.23`, invoke the project-local CLI offline, and verify the complete
  installed skill tree against `skills-lock.json`.
- **Reason:** The integration needs deterministic discovery and a lock-backed guarantee that the
  installed content matches the recorded source hash.
- **Alternatives rejected:** Invoke `npx` at test time, use an unpinned CLI, assert only that
  `SKILL.md` exists, or compare a hard-coded hash without recomputing the tree. Those alternatives
  allow network drift, version drift, or undetected content changes.
- **Cost to change now:** Updating the CLI requires changing the dependency lock, version assertions,
  and the integration test; changing the skill requires regenerating and reviewing its lock hash.
- **Cost to the user today:** Tests run without network access and fail close to the integration
  boundary when the install, CLI, or content diverges.

### Exclude only generated Python caches from the gate hash

- **Choice:** Ignore `__pycache__` directories and `*.pyc` files while hashing the installed tree;
  keep all other files in the hash.
- **Reason:** Python execution can create ignored bytecode beside the upstream skill. Those generated
  files are not release content and should not change the recorded hash.
- **Alternatives rejected:** Ignore the whole `scripts/` directory, ignore all untracked files, or
  skip tree hashing. Those choices would hide meaningful upstream changes or remove the integrity
  check entirely.
- **Cost to change now:** Any new generated-artifact type requires a narrowly scoped hash rule and a
  regression probe; broadening exclusions risks weakening the gate.
- **Cost to the user today:** Routine Python execution no longer causes false hash failures, while
  edits to tracked skill content still fail the test.
