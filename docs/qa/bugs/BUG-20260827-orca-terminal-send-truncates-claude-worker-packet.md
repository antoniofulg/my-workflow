# BUG-20260827-orca-terminal-send-truncates-claude-worker-packet

- **Status:** open — the host transport defect remains open upstream. The assisted contract's route-around was retested end to end and passed (Retest 12); the host defect itself is unfixed and did not reproduce in that run's single characterization
- **Severity:** critical
- **Scenario:** `QAS-coordinate-assisted-orca-slices`
- **Expected:** The assisted contract's one mandated transport — exactly one `orca terminal send --text <shq(task_payload)> --enter` per logical packet, never retried — delivers the complete packet to the frozen-route worker, or reports a failure the coordinator can act on.
- **Observed:** `orca terminal send` returns `ok=true`, `accepted=true` and the full `bytesWritten`, while the Claude Code TUI worker receives only a mangled tail fragment of the payload. Loss is timing-dependent, not a fixed cap: a 39-char route payload and a 1225-char task packet arrived intact; 1354-char and 1677-char task packets did not; a 2081-char characterization payload delivered 36 characters (98.3 % lost).
- **Adapter:** Installed Orca CLI/manual assisted flow, `orca terminal send --text … --enter`, frozen route `claude` / `sonnet` / `low`
- **Exact path:** `orca worktree create` → startup-handle ownership proof → `exec claude --model sonnet --effort low` → rendered `source=screen` route proof → `orca terminal send --terminal <handle> --text <packet> --enter --json`
- **Evidence:** `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-10/session.md`; `.../retest-10/a-turns.jsonl`; `.../retest-10/b-turns.jsonl`; `.../retest-10/truncation-probe.jsonl`; `.../retest-10/truncation-payload.txt`

## Reproduction

1. Create an Orca worktree and promote its startup shell with `exec claude --model sonnet --effort low`.
2. Prove the rendered route (`Claude Code`, `Sonnet 5`, `with low effort`) on two consecutive `source=screen` frames.
3. Send a single-line payload of ~2000 characters with `orca terminal send --terminal <handle> --text <payload> --enter --json`.
4. Read the rendered screen. The receipt reports `bytesWritten` equal to the payload; the agent's transcript begins mid-word and the agent reports that the message was cut off.

Observed reply from the receiving agent, unprompted:
`got no real ask here. msg cut off, only tail text showed up. what u need?`

## Impact

This defeats the assisted-Orca contract on the Claude route. The contract mandates exactly one send
per logical packet and forbids retry after a success receipt, a replacement worker, or a second
terminal for a slice. A silent, non-deterministic truncation that still reports success therefore
burns the slice lane irrecoverably: the coordinator cannot detect the loss from the receipt, and
once the worker has acted on a fragment it may neither resend nor replace the worker.

Retest 10 lost both remaining task packets this way. The fail-closed machinery worked exactly as
specified — `A_FINAL`'s zero-work effect was rejected on `commit_count`, `commit_subjects` and
`tasks`; `B_PARKED` reached its 300 s deadline at `marker-count=0`; neither was resent; cleanup
returned the exact two-worktree baseline with zero residue — but the successful-parallel journey
cannot complete.

This is the same class as `BUG-20260827-assisted-orca-tui-idle-before-route-proof` and retest 5's
`agent_prompt_stalled` divergence (receipt contradicts effect) but a distinct symptom: the receipt
reports a **complete** write that the agent never receives.

`orca terminal send --help` exposes no chunking, paste, stdin or fragmentation mode, so `--text` is
the only expressible transport. Shortening packets is not a fix: loss is timing-dependent, so a
smaller packet is only less likely to be truncated, never proven intact, and the contract's no-retry
rule means "less likely" is not a delivery guarantee.

A second, weaker observation is recorded in the session but not claimed as proven: while two
concurrent sends to two different handles were in flight, the string `start B:T9` — not verbatim in
any packet — appeared as unsubmitted input in the other slice's terminal.

## Required fix and retest

The assisted contract needs a delivery proof the coordinator can act on before the worker turn
begins. Any of these would close it, and the choice belongs to the contract owner, not to QA:

- an Orca `terminal send` mode that acknowledges what the receiving TUI actually accepted; or
- a normative post-send, pre-barrier readback that proves the rendered packet matches the sent
  payload and fails closed before the worker acts on a fragment; or
- a packet transport that does not cross the TUI input at all (a file the worker is told to read,
  with only the short path sent through `terminal send`).

Retest must re-walk `QAS-coordinate-assisted-orca-slices` end to end and prove packet delivery
before each task turn. No automatic Orca compatibility claim is made or implied by this record.

## Resolution

The contract owner took the third option above: a packet transport that does not cross the TUI
input. `AD-018` removes the inline-payload path from
`.agents/skills/autonomous/references/parallelization.md`. The coordinator now writes the complete
slice packet — marker requirement included — to a coordinator-owned file outside every slice
worktree, and the one mandated `orca terminal send` carries only a short fixed-shape pointer to that
file. There is no fallback and no length threshold that selects between inline and file delivery.
`exec_payload` and the pre-packet recording obligations are unchanged, as are the one-send,
no-retry, no-replacement-worker, bounded same-handle reconciliation, fail-closed acceptance, and
`TURN_DONE <phase> head=<40-hex-sha>` marker rules.

Contract, `AST-04`, `IT-005`, the charter, and this scenario changed in commits `5bc9e31`,
`d4de714`, `88ba1fa`, and `92ac013` on `feat/host-agnostic-slice-parallelization`.

**This does not fix the host transport.** `orca terminal send --text` still reports a complete write
that the receiving TUI may not receive, and that defect belongs upstream. The change reduces the
mandated payload to a size at which the observed loss did not occur; it does not prove delivery.
Because a truncated pointer cannot produce a valid marker, truncation still fails closed instead of
silently half-executing. This record stays open against the host until
`QAS-coordinate-assisted-orca-slices` is re-walked end to end on the pointer transport.

## Retest 12 — route-around retested and passed; host defect still open

The retest this record was waiting for has now happened, and it separates cleanly into two results.

**The workflow-side remediation passes.** Under AD-018 every mandated packet crossed
`orca terminal send` as a short pointer and none carried a body. Eight logical packets — bodies of
1226, 1355, 1635, 1644, 1523, 1627, 1678 and 2077 characters — were delivered as **177-190 character
pointers**, each sent exactly once, each `ok=true`, and each honoured packet-exactly. `A_FINAL` and
`B_PARKED`, the two packets Retest 10 lost at 1354 and 1677 characters, both arrived and were
executed exactly. The full scenario reached grouped Deep Review `SHIP`, final persona QA, and exact
cleanup.

**The host defect is not cleared.** One bounded characterization ran on the coordinator's ground
(non-slice) shell, the same place Retest 10 measured it:

| Fact | Retest 10 | Retest 12 |
| --- | --- | --- |
| Inline payload | 2081 chars | **2012 chars** |
| Receipt | `ok=true`, full `bytesWritten` | `ok=true`, `accepted=true`, `bytesWritten: 2013` |
| Received by the agent | 36 chars (98.3 % lost) | **the complete payload** — replied `TRUNC first=Q000 last=Q339 total=340` |

This does **not** close the bug, and Retest 12 does not claim it does. The record's own finding is
that loss is timing-dependent rather than a fixed cap, so a single clean sample disproves an
intermittent defect no more than a single dirty sample proves it. Nothing in Orca changed between the
two runs — both ran on `1.4.190` — and `orca terminal send --help` still exposes no acknowledgement
mode, so a coordinator still cannot distinguish a complete write from a lost one by its receipt.

The bug therefore stays **open** against the host. What changed is that the assisted contract no
longer depends on the answer: the mandated payload is a ~180-character pointer, a size at which no
loss has been observed across Retests 10, 11 and 12, and a truncated pointer cannot produce a valid
marker, so truncation still fails closed instead of half-executing. Closing this record requires an
upstream `terminal send` acknowledgement mode, not another QA cycle.

Evidence: `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-12/truncation-disposition.md`;
`.../retest-12/truncation-probe.jsonl`; `.../retest-12/truncation-payload.txt`;
`.../retest-12/session.md`.
