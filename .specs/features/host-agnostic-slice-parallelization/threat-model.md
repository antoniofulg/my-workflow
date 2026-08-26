# Host-Agnostic Slice Parallelization Threat Model

## Scope

Adapter discovery, local compatibility receipts, Orca canary effects, and Maestri capability
inspection. The existing scheduler, Git synchronization, and consumer resource provider remain
covered by the parallel slice executor threat model.

## Trust boundaries and abuse paths

| Boundary | Abuse path | Required outcome | Control/evidence |
| --- | --- | --- | --- |
| Host runtime -> scheduler | Capability is advertised while lifecycle remains broken | Adapter stays disabled until canary PASS | Version-aware probe and IT-001/IT-002 |
| Compatibility cache -> another checkout | Foreign PASS is copied or reused after update | Receipt invalidates before any worker effect | Repository/runtime/executable identity binding and UT-004/SEC-002 |
| Adapter -> subprocess | Host value reaches a shell or changes argv shape | No shell expansion | Fixed argv, bounded timeout, SEC-003 |
| Canary -> cleanup | Worker starts but release or checkout removal fails | No compatible receipt; retained identity reported | Staged cleanup and IT-002/SEC-005 |
| Maestri text -> ownership state | Human output is parsed as a receipt | Adapter refuses execution | Structured-output requirement and UT-005/IT-004 |
| Diagnostics -> local state | Host returns tokens, env, or transcript | Values never persist | Existing recursive redaction and SEC-004 |

## Attacker assumptions

- A local host runtime may be stale, partially upgraded, or return malformed data.
- A local compatibility receipt may be copied between repositories.
- A failed canary may leave a real host resource that must not be deleted without ownership proof.

## Residuals

- Orca does not expose a build SHA in `status`; actual installed behavior is proven by canary, while
  release ancestry remains release-process evidence.
- Current Maestri cannot be certified for automatic execution because floor deletion and structured
  lifecycle receipts are unavailable through its documented CLI.
