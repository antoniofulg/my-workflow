# Release 0.8.0 Decisions

## Human Decisions

| Decision | Why | Cost to change now | User cost today |
| --- | --- | --- | --- |
| Release version is 0.8.0 | New modular adoption and locking capabilities warrant a minor release. | Rename release artifacts and version authorities before publication. | Features remain local until release completes. |
| Proceed through publication | The verified work must become consumable by other projects. | Stop before an external action and leave the release branch ready. | No stable tag exposes the work. |

## Run Decisions

| Decision | Why | Alternatives rejected | Cost to change now | User cost today |
| --- | --- | --- | --- | --- |
| Use GitHub tag and GitHub Release only | Package is private and 0.7.0 established this channel. | npm publication conflicts with `private: true` and lacks authentication. | Add a registry contract, credentials, and a separate release path. | None; adoption already consumes repository source. |
| Integrate only the legacy-adoption and remediation branch heads | They contain the approved post-0.7.0 work and share `origin/main`. | Local divergent `main` contains unrelated backlog; PR #72 is not the release source. | Prepare another candidate and repeat all gates. | Keeps release scope bounded and auditable. |
| Preserve live Orca as `blocked-verify` | The external transport fix is not available for a trustworthy live walk. | Claiming success from fake-provider QA would overstate evidence. | Rerun live QA after the host fix. | Assisted pointer fallback remains the supported path. |
| Treat `bun.lock` as dependency-graph metadata, not a package-version authority | Bun 1.4's lockfile records the root package name and resolved dependency graph, but it does not encode `package.json`'s root version. | Adding a synthetic version field or testing Bun internals would create a non-native contract. | Keep version checks on package/changelog/test/scenario and use `bun install --frozen-lockfile` for package/lock compatibility. | Version and dependency drift remain checked by their native authorities. |
| Document `flock` as a cooperative same-UID boundary | Kernel `flock` serializes clients that use the wrapper, but a same-UID process can bypass the wrapper or rewrite the lock namespace. | Inventing same-UID replacement protection would claim an OS guarantee the user-level wrapper cannot enforce. | Keep the existing ownership, mode, and temporary-parent race safeguards; rerun QA after any Orca or runtime change. | Hostile same-UID processes remain outside the lock guarantee. |
