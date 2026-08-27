# Host-Agnostic Slice Parallelization Threat Model

## Scope

Adapter discovery, local compatibility receipts, Orca canary effects, Maestri capability
inspection, and explicitly authorized coordinator-assisted Orca worktrees. The existing scheduler
and consumer resource provider remain covered by the parallel slice executor threat model; this
feature adds the assisted coordinator's ownership and recovery boundary.

## Trust boundaries and abuse paths

| Boundary | Abuse path | Required outcome | Control/evidence |
| --- | --- | --- | --- |
| Host runtime -> scheduler | Capability is advertised while lifecycle remains broken | Adapter stays disabled until canary PASS | Version-aware probe and IT-001/IT-002 |
| Compatibility cache -> another checkout | Foreign PASS is copied or reused after update | Receipt invalidates before any worker effect | Repository/runtime/executable identity binding and UT-004/SEC-002 |
| Adapter -> subprocess | Host value reaches a shell or changes argv shape | No shell expansion | Fixed argv, bounded timeout, SEC-003 |
| Canary -> cleanup | Worker starts but release or checkout removal fails | No compatible receipt; retained identity reported | Staged cleanup and IT-002/SEC-005 |
| Maestri text -> ownership state | Human output is parsed as a receipt | Adapter refuses execution | Structured-output requirement and UT-005/IT-004 |
| Diagnostics -> local state | Host returns tokens, env, or transcript | Values never persist | Existing recursive redaction and SEC-004 |
| Coordinator -> assisted worker | Unverifiable default, stale pre-send idle, one-screen acceptance, second terminal, or ambiguous send effect launches or adopts the wrong frozen route | Lane stops before task edit or prompt, or retains exact recovery; automatic adapter remains unsupported | Explicit authorization, frozen provider/model/effort argv, unused startup-shell proof, bounded machine-only repeated 250 ms / 60000 ms two-screen `source=screen` proof on a connected exact handle with reset-on-nonmatch, exact-handle continuity, one-send receipt/effect reconciliation at 250 ms / 300000 ms with a unique phase marker and full state/gate proof, and AST-01 |
| Create timeout -> late Orca effect | Missing create receipt is blindly retried, or a concurrent/late effect is adopted without exact identity | No replacement create; the cumulative observed set is filtered by exact repository plus unique logical name every 250 ms for at most 60000 ms, nonmatching entries are foreign and never adopted or cleaned, the deadline receives a final audit, and zero/multiple/ambiguous matching candidates serialize with only matching provably owned late effects cleaned | One mutating create, exact before inventory, cumulative `current - before_inventory` observation window, unique logical name, exact repository correlation, deadline final audit, immutable receipt/ownership proof, and SEC-008 |
| Parked checkpoint -> follow-up | Stale or ambiguous comment resumes the wrong task or head | Lane serializes without follow-up or replacement worker | Reconcile comment with `tasks.md` and Git; AST-03–AST-05 |
| Terminal send -> effect | `agent_prompt_stalled` or missing receipt hides a completed turn, prompting a blind resend, foreign/reset adoption, or commit-only acceptance | No retry or replacement; same-handle effect is accepted only after one unique marker, pre-head ancestry, exact commit count/identities, packet path allowlist, and conditional parked-comment proof | One-send turn ledger, bounded 250 ms / 300000 ms machine-only reconciliation, connected screen/tui-idle frames, HEAD/status/commit/gate/comment correlation, `git merge-base --is-ancestor` ancestry, changed-path subset, and serial recovery |
| Assisted cleanup -> Git/Orca resource | Foreign, dirty, or unintegrated resource is removed | No deletion; exact owned path remains for serial recovery | Exact create receipt, Orca/Git identity revalidation, integrated ancestor, ordered stop/detach/branch-delete/ref-proof/remove, and absence proof; SEC-008 |

## Attacker assumptions

- A local host runtime may be stale, partially upgraded, or return malformed data.
- A local compatibility receipt may be copied between repositories.
- A failed canary may leave a real host resource that must not be deleted without ownership proof.
- A worker or stale worktree comment may be incomplete, duplicated, or out of date at resume time.
- A producer checkpoint may conflict with or fail the dependent lane's affected gate.
- An Orca default terminal may hide a provider/model/effort mismatch with the frozen route.
- A worktree identity or integration ancestry may change between the create receipt and cleanup.
- The startup shell may already contain agent/default-task activity or more than one owned handle.
- The initial handle may be replaced by an accidental second terminal or lose identity continuity.
- A route may render after an initial idle signal.
- A create invocation may materialize a late duplicate after its receipt timed out.
- A terminal send may return an error or no receipt after applying exactly one effect, or may expose
  conflicting/multiple marker SHAs; reconciliation must never retry or infer success from a commit.

## Residuals

- Orca does not expose a build SHA in `status`; actual installed behavior is proven by canary, while
  release ancestry remains release-process evidence.
- Current Maestri cannot be certified for automatic execution because floor deletion and structured
  lifecycle receipts are unavailable through its documented CLI.
- Assisted Orca cleanup is intentionally fail-closed under **SEC-008**: only clean, integrated,
  coordinator-owned worktrees are removable, and missing ownership or residue proof retains the
  resource for serial recovery. Cleanup uses the exact full worktree id, never a name or branch.
