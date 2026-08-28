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
| Feature slug is `hybrid-slice-execution`; skill name remains provisional until implementation starts. | The slug names the observable scheduling behavior while leaving the public skill name reviewable. | Use an implementation-only slug such as `tlc-fork`. | Rename the local feature directory and branch. | None; no implementation has started. |
| Rebase the feature onto `origin/main` and exclude the 150 unpublished local commits. | The human explicitly chose rebase so this PR contains only the hybrid-slice feature. | Push local `main`; append all work to PR #72. | Required re-grounding against the older remote code surface. | The feature must reintroduce only the dependencies it actually needs instead of inheriting local backlog. |

## Rebase resolution

- Feature base: `origin/main` at `2ab4cec`.
- Excluded local source: `main` at `3ce7a2e` and its 150 unpublished commits.
- Existing PR: `#72`, remote head `836f9d3`.
- Delivery scope: one new feature branch and pull request containing only work grounded on the
  remote base. The prior PR and local backlog remain untouched.
