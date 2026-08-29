# Hybrid Slice Execution — Autonomous Decisions

## Human decisions

| Decision | Why | Alternatives rejected | Cost to change now | User cost today |
| --- | --- | --- | --- | --- |
| Create a workflow-owned adaptation of `tlc-spec-driven`, provisionally named `workflow-spec-driven`, with CC BY 4.0 attribution. | The shipped TLC delegation model is sequential phase batching and conflicts with the adopted vertical-slice contract. | Keep patching the upstream-named skill indefinitely; retain both skills behind compatibility aliases. | Rename the skill, update adoption, templates, snapshots, tests, and every reference. | Agents can load contradictory delegation rules and unnecessary context. |
| Make context cleanup part of the feature foundation. | Slice workers need only their own tasks, ACs, tests, gate, design excerpt, and compact memory. | Optimize context after the scheduler ships. | Rework packets and tests after public behavior has frozen. | Repeated full skill/spec/task context increases token use. |
| Use hybrid assisted execution: only concurrent writers receive worktrees. | Read-only roles do not need filesystem isolation; concurrent implementers do. | A worktree for every role; all agents share one checkout. | Change scheduler admission and role packets. | Extra worktrees waste resources; shared concurrent writers contaminate commits and gates. |
| Start adaptive concurrency at two workers and allow healthy hosts to scale to four by default. | Two is a safe baseline; incremental admission captures more speed without unbounded load. | Fixed two lanes; unlimited ready-lane dispatch. | Change snapshot/config defaults and scheduler policy. | Fixed two may leave speed unused; unlimited dispatch can saturate the machine. |
| Keep Technical Verifier, Deep Review, and QA independent from implementers. | Author independence is a quality invariant. | Let the last implementer review and QA the feature. | Rewrite review packets and acceptance evidence. | Independent sessions add tokens but prevent self-certification. |

## Autonomous decisions

| Decision | Why | Alternatives rejected | Cost to change now | User cost today |
| --- | --- | --- | --- | --- |
| Feature slug is `hybrid-slice-execution`; public skill name is `workflow-spec-driven`. | The slug names the observable behavior; the human approved one workflow-owned skill with no compatibility alias. | Use an implementation-only slug such as `tlc-fork`; retain a provisional or upstream-owned public name. | Rename the feature, skill, adoption manifest, templates, snapshots, tests, and references. | None before implementation; high after adoption freezes the path. |
| Rebase the feature onto `origin/main` and exclude the 150 unpublished local commits. | The human explicitly chose rebase so this PR contains only the hybrid-slice feature. | Push local `main`; append all work to PR #72. | Required re-grounding against the older remote code surface. | The feature must reintroduce only the dependencies it actually needs instead of inheriting local backlog. |
| Use schema version `3` for both `.my-workflow.toml` and frozen feature snapshots, with no old reader. | The remote base writes v2 snapshots while `parallel_plan.py` still requires v1; one hard cut removes the mismatch and carries the new public fields coherently. | Patch the v1/v2 mismatch in place; add compatibility migration; version config and snapshot separately. | Refresh every active old feature snapshot and update config/adoption/tests in one release. | Active old snapshots stop with an explicit refresh instruction instead of dispatching ambiguously. |
| Keep automatic health internal and reuse the existing resource-provider lease protocol for heavy gates. | Host capacity is runtime evidence, not project configuration; a second lock system would duplicate correlation and cleanup. | Add a public health-provider plugin; create lock files or another daemon. | Replace the internal helper or extend the existing provider schema. | Unknown health caps concurrency at two; unavailable leases park only resource-bearing work. |
| Enforce 3,072-byte role and 10,240-byte slice packet limits with redacted JSON telemetry. | Existing instruction targets become machine-checkable and prevent whole-feature context from silently returning. | Keep advisory line-count guidance; estimate model tokens at runtime. | Change constants and canonical packet fixtures. | Oversized packets stop before dispatch and name exact byte counts. |
| Keep live Orca QA `blocked-verify`; fake Orca and adoption dry-run own automation. | The current transport limitation is upstream and gates must not depend on a live host. | Treat fake proof as live proof; leave scenario `untested`; run live Orca in CI. | Schedule a fresh external QA session when upstream support lands. | Merge can state the host limitation truthfully while deterministic workflow behavior remains proven. |

## Rebase resolution

- Feature base: `origin/main` at `2ab4cec`.
- Excluded local source: `main` at `3ce7a2e` and its 150 unpublished commits.
- Existing PR: `#72`, remote head `836f9d3`.
- Delivery scope: one new feature branch and pull request containing only work grounded on the
  remote base. The prior PR and local backlog remain untouched.

## Authorized CP-S4 resume — 2026-08-28

**Authorization reference:**
`.specs/features/hybrid-slice-execution/decisions.md#authorized-cp-s4-resume--2026-08-28`

- The human explicitly authorized a new autonomous run after the third-failure CP-S4 halt and asked
  it to continue until the feature is safe and delivered.
- Fingerprint `a83ca4d68afa5e45916eae7606c22e6dd57444470bea7b13cfb916684e98bbfd`
  remains the identity of the blocker. Its three failures and first halt remain audit history.
- Resume creates generation 2 under that fingerprint. It resets only generation 2's local failure
  count; cumulative failures remain three.
- No manual JSON reset, replacement fingerprint, or rewording may bypass the halt.
- CP-S4 remains blocked until a fresh independent Verifier returns PASS for the resumed generation.
