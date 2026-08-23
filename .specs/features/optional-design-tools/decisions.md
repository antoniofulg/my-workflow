# Optional Design Tools Decisions

## Human decisions

### Workflow boundary

- **What**: Keep the workflow stack- and tool-agnostic, even though Antonio is its principal user.
- **Why**: The same contracts must work across different technologies and consuming projects.
- **Rejected**: Make Antonio's current toolchain mandatory; that would turn personal preference into a
  product constraint.
- **Cost to change now**: Rework the public contract, adoption behavior, and integration guidance.
- **Cost to the user today**: Tool-specific setup remains an explicit choice for each project.

### Optional recommendations

- **What**: Recommend Graft for deep-review context and OpenDesign for visual iteration. OpenDesign is
  an optional iteration surface; the repository owns the approved handoff.
- **Why**: These capabilities improve context or visual exploration without changing the workflow's
  authority or requiring a particular stack.
- **Rejected**: Require installation or use of either tool; absence and failure must have an honest
  repository fallback.
- **Cost to change now**: Promote optional guidance into mandatory installation, configuration, and
  gate behavior across the pack.
- **Cost to the user today**: Projects without either tool use the normal repository artifacts and
  inspection path.

### Remote delivery boundary

- **What**: PR creation is authorized for this feature; merge remains withheld pending human review.
- **Why**: The human owns the final integration decision.
- **Rejected**: Treat readiness or PR creation as merge authorization; that would collapse two distinct
  remote actions.
- **Cost to change now**: Reopen the delivery boundary and potentially undo an unauthorized merge.
- **Cost to the user today**: The completed branch waits for explicit merge confirmation.

## Run decisions

### Documentation placement

- **What**: Extend the existing `README.md`, `UI-UX.md`, and `SECURITY.md` instead of creating a new
  guideline.
- **Why**: Each document already owns the relevant discovery, visual-handoff, or writer-safety
  contract.
- **Rejected**: Add an integrations guideline; it would create another context pointer and split
  ownership without a distinct rule set.
- **Cost to change now**: Move text, add dispatch guidance, and update adoption and contract tests.
- **Cost to the user today**: Optional integration guidance is found through the existing documents.

### Operational detail scope

- **What**: Keep OpenDesign installation, configuration, daemon, CLI, port, and version details out of
  the README and guidelines; place them in an integration skill when one exists.
- **Why**: Operational details are tool-specific and would make the workflow less portable and more
  expensive to load.
- **Rejected**: Copy antclips paths, design-system choices, or synchronization implementation; those
  are consuming-project details, not workflow contracts.
- **Cost to change now**: Add and maintain a tool-specific skill plus its installation and update
  contract.
- **Cost to the user today**: An adopter must consult or create the relevant integration skill before
  operating a concrete tool.

### External writer safety

- **What**: Require isolation or explicit allowed directories, path and symlink validation before the
  first write, preservation of destination-only files, and no automatic deletion.
- **Why**: Optional filesystem-writing tools must not turn iteration into uncontrolled repository
  mutation.
- **Rejected**: Trust a tool's default workspace or use destructive synchronization; neither proves
  destination safety.
- **Cost to change now**: Relaxing these controls would require revisiting the security contract and
  its tests.
- **Cost to the user today**: Imports may require an explicit review or adapter, and stale destination
  files remain for deliberate cleanup.

### Durable decision

- **What**: Record the agnostic/optional integration trade-off in `AD-006`; keep the prior `AD-003`
  contradiction out of this slice and address it in a separate issue.
- **Why**: The new decision is durable knowledge, while the prior contradiction is unrelated scope.
- **Rejected**: Rewrite or reconcile `AD-003` here; that would silently alter historical project state
  and broaden the feature.
- **Cost to change now**: Re-index or revise the decision log and rerun its integrity checks.
- **Cost to the user today**: `AD-003` remains visibly contradictory until its separate issue is
  resolved.

### Deep-review SHIP follow-ups

- **What**: Keep the deep-review SHIP follow-ups as explicit, nonblocking items; do not silently fix
  them in this reporting commit. The review found no open Critical or Major finding.
- **Why**: Preserving the review's provenance keeps the PR auditable and respects the requested
  one-file reporting scope.
- **Rejected**: Fold follow-up remediation into this commit; that would change reviewed files after
  verification and obscure which work was human-approved.
- **Cost to change now**: Add a remediation commit, rerun the scoped gate, and obtain a fresh review
  and QA evidence where applicable.
- **Cost to the user today**: The following Minor/Nitpick gaps remain visible and actionable, but do
  not block SHIP:
  - Add a negative contract scan rejecting concrete OpenDesign daemon, port, CLI, or version details
    in README and guidelines.
  - Assert `AD-006` in the index and the Codex deep-reviewer route in the frozen snapshot.
  - Clarify the validation report's implementation range versus its evidence-commit range.
  - Qualify README routing as applying when an integration skill exists.
