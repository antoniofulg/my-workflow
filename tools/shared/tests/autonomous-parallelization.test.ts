import { execFileSync } from "node:child_process";
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { describe, expect, it } from "bun:test";

const repositoryRoot = process.cwd();

function readRepositoryFile(relativePath: string): string {
  return readFileSync(join(repositoryRoot, relativePath), "utf8");
}

describe("autonomous parallel slice dispatch contract", () => {
  it("IT-007 binds the executor capability gate and preserves every lifecycle boundary", () => {
    const executor = readRepositoryFile(
      ".agents/skills/autonomous/scripts/parallel_execute.py",
    );
    const adapter = readRepositoryFile(
      ".agents/skills/autonomous/scripts/orca_adapter.py",
    );
    const maestri = readRepositoryFile(
      ".agents/skills/autonomous/scripts/maestri_adapter.py",
    );
    const policy = readRepositoryFile(
      ".agents/skills/autonomous/references/parallelization.md",
    );
    const qa = readRepositoryFile(
      ".specs/features/parallel-slice-executor/qa-pilot.md",
    );

    expect(executor).toContain('parser.add_argument("--adapter", choices=("auto", "orca", "maestri")');
    expect(executor).toContain('parser.add_argument("command", choices=("start", "resume", "status", "preflight"))');
    expect(executor).toContain('parser.add_argument("--technical-verifier-receipt"');
    expect(executor).toContain('"unsupported-adapter"');
    expect(executor).toContain("resource_provider");
    expect(executor).toContain("gate_required");
    expect(adapter).toContain('CAPABILITY = "orchestration.contract.v1"');
    expect(adapter).toContain("KNOWN_INCOMPATIBLE_VERSIONS");
    expect(maestri).toContain("REQUIRED_CAPABILITIES");
    expect(maestri).toContain("structured_completion_events");
    expect(policy).toContain("orchestration.contract.v1");
    expect(policy).toContain("lifecycle canary");
    expect(policy).toContain("proof.cleanup=clean");
    expect(policy).toContain("maestri_adapter.py");
    expect(policy).toContain("check --run <run> --wait");
    expect(policy).toContain("ack");
    expect(policy).toContain("same terminal");
    expect(policy).toContain("merge");
    expect(policy).toContain("Resources: none");
    expect(policy).toContain("E2E-001 as terminal `BLOCKED-VERIFY`");
    expect(qa).toContain("**Status:** blocked-verify");
    expect(qa).toContain("--adapter auto");
  });

  it("IT-006 preserves safe orchestration and every existing evidence gate", () => {
    const autonomous = readRepositoryFile(".agents/skills/autonomous/SKILL.md");
    const policy = readRepositoryFile(
      ".agents/skills/autonomous/references/parallelization.md",
    );

    expect(autonomous).toContain(
      ".agents/skills/autonomous/references/parallelization.md",
    );
    expect(policy.indexOf("Resolve the feature workflow")).toBeLessThan(
      policy.indexOf("Read the frozen `workflow.json` before planning"),
    );
    expect(policy.indexOf("Read the frozen `workflow.json` before planning")).toBeLessThan(
      policy.indexOf("python3 .agents/skills/workflow-config/scripts/parallel_plan.py"),
    );
    expect(policy).toContain("Read the frozen `workflow.json` before planning");
    expect(policy).toContain("python3 .agents/skills/workflow-config/scripts/parallel_plan.py");
    expect(policy).toContain("no capable isolated executor");
    expect(policy).toContain("existing serial path");
    expect(policy).toContain("without creating a worker or worktree");
    expect(policy).toContain("one worker per slice");
    expect(policy).toContain("Tasks inside a slice remain sequential");
    expect(policy).toContain("must first leave a clean committed checkpoint");
    expect(policy).toContain("report the exact dependency and current head");
    expect(policy).toContain("end the clean worker turn");
    expect(policy).toContain("dependency completion event");
    expect(policy).toContain("does not poll");
    expect(policy).toContain("If the worker is dirty");
    expect(policy).toContain("not a valid waiter");
    expect(policy).toMatch(/use the existing serial recovery\s+path/i);
    expect(policy).toMatch(
      /Synchronize at declared dependency checkpoints\s+before the dependent task consumes a newer\s+upstream commit/,
    );
    expect(policy).toMatch(/do(?:es not| not) rebase after every task/i);
    expect(policy).toContain("final reconciliation");
    expect(policy).toMatch(
      /If the consumed checkpoint already equals\s+the final base, final reconciliation is a no-op/,
    );
    expect(policy).toContain("Use the exact upstream commit recorded by the dependency event");
    expect(policy).toMatch(/run the affected gate before\s+continuing/);
    expect(policy).toContain("invalidate every affected gate, Verifier, and deep-review verdict");
    expect(policy).toContain(
      "Repeat the affected gate on the resulting tree before the next task or review stage",
    );
    expect(policy).toContain("one atomic commit and scoped gate per task");
    expect(policy).toContain("one technical Verifier per code-changing slice");
    expect(policy).toContain("deep-review at the frozen groups");
    expect(policy).toContain("final QA");
    expect(policy).toContain("one full gate on the final tree");
    expect(policy).toContain("TLC remains unchanged");
    expect(policy).toMatch(/uncertainty or failure\s+serializes safely/i);
  });

  it("IT-005 covers the standard coordinator-assisted Orca lifecycle", () => {
    const policy = readRepositoryFile(
      ".agents/skills/autonomous/references/parallelization.md",
    );
    const dx = readRepositoryFile(
      ".specs/features/host-agnostic-slice-parallelization/dx.md",
    );
    const spec = readRepositoryFile(
      ".specs/features/host-agnostic-slice-parallelization/spec.md",
    );
    const tasks = readRepositoryFile(
      ".specs/features/host-agnostic-slice-parallelization/tasks.md",
    );
    const charter = readRepositoryFile(
      "docs/qa/charters/CH-coordinate-assisted-orca-slices-2026-08-26.md",
    );
    const scenario = readRepositoryFile(
      "docs/qa/scenarios/QAS-coordinate-assisted-orca-slices.md",
    );
    const workflow = JSON.parse(
      readRepositoryFile(
        ".specs/features/host-agnostic-slice-parallelization/workflow.json",
      ),
    ) as { roles: { implementer: { provider: string; model: string; effort: string } } };
    const implementer = workflow.roles.implementer;
    const normalizedPolicy = policy.replace(/\s+/g, " ");
    const providerCommandPatterns: Record<string, RegExp> = {
      codex: /codex --model <shq\(model\)> -c <shq\(model_reasoning_effort=<effort>\)>/,
      claude: /claude --model <shq\(model\)> --effort <shq\(effort\)>/,
      cursor: /cursor agent --model <shq\(model\[effort=<effort>\]\)>/,
    };

    // AST-01: assisted execution is separate from automatic compatibility and honors frozen route.
    expect(policy).toContain("standard path for useful overlap");
    expect(policy).toContain("does not write a compatibility PASS");
    expect(policy).toMatch(/automatic execution remains\s+unsupported and serial/);
    const contracts = [
      ["policy", policy],
      ["dx", dx],
      ["spec", spec],
      ["tasks", tasks],
    ] as const;
    for (const [name, contract] of contracts) {
      expect(contract, name).not.toContain("worktree create --agent");
      expect(contract, name).not.toContain("terminal create --command");
    }
    expect(implementer.provider).toBe("claude");
    expect(implementer.model).toBe("sonnet");
    expect(implementer.effort).toBe("medium");
    expect(charter).toContain(
      "frozen implementer route `claude` / `sonnet` / `medium`",
    );
    expect(charter).toContain(
      "`claude` / `sonnet` / `medium` exactly",
    );
    expect(scenario).toContain(
      "frozen implementer route `claude` / `sonnet` / `medium`",
    );
    expect(providerCommandPatterns[implementer.provider]).toBeDefined();
    expect(policy).toMatch(providerCommandPatterns[implementer.provider]);
    for (const pattern of Object.values(providerCommandPatterns)) {
      expect(policy).toMatch(pattern);
    }
    expect(policy).toContain("roles.implementer.provider");
    expect(policy).toContain("roles.implementer.model");
    expect(policy).toContain("roles.implementer.effort");
    expect(policy).toContain("shq(value)");
    expect(policy).toContain("actual POSIX-shell quoting");
    expect(policy).toContain("fixed-argv/no-shell wrapper");
    expect(normalizedPolicy).toContain("complete `exec <validated-frozen-agent-command>` string");
    // AST-04: the slice packet body is delivered by coordinator-owned file, never inline.
    expect(normalizedPolicy).toContain(
      "write the complete slice packet, including its required `TURN_DONE <phase> head=<40-hex-sha>` marker, to a coordinator-owned `packet_file` outside every slice worktree",
    );
    expect(normalizedPolicy).toContain(
      "so it can never dirty a worktree or appear in a changed-path allowlist",
    );
    expect(normalizedPolicy).toContain(
      "Construct `task_payload` as the short fixed-shape pointer `read <packet_file> and execute it as your packet`",
    );
    expect(normalizedPolicy).toContain("The packet body never crosses `terminal send`");
    expect(normalizedPolicy).toContain(
      "The worker must be able to read `packet_file` from outside its own worktree and report an unreadable path at once",
    );
    expect(normalizedPolicy).toContain(
      "`packet_file` crosses the shell boundary inside that pointer and is covered by that single `shq(payload)`; never quote it twice",
    );
    expect(normalizedPolicy).toContain("does not make the host transport reliable");
    expect(normalizedPolicy).toContain(
      "a truncated pointer cannot produce a valid marker, so truncation still fails closed instead of silently half-executing",
    );
    // AST-04: pointer delivery is unconditional. No conditional, threshold, fallback, or branch
    // may let the packet body cross `terminal send`. Pinned as a concept, not as one wording:
    // no size threshold may exist anywhere in the contract, and every sentence that mentions the
    // packet must be free of conditional or alternative-delivery language.
    expect(normalizedPolicy).not.toContain(
      "construct `task_payload` as the complete slice packet",
    );
    expect(
      normalizedPolicy.match(/[^.;:]*\d[\d,]*\s*(characters?|chars?|bytes?|[kmg]i?b)\b[^.;:]*/i),
      "no size threshold may gate packet delivery",
    ).toBeNull();
    const conditionalDelivery =
      /\b(if|unless|whenever|otherwise|instead of|fall ?backs?|falls? back|threshold|shorter|longer|smaller|larger|bigger|less than|more than|fewer than|below|above|exceeds?|optional|optionally|may be sent|can be sent|inline|directly|skip the packet file)\b/i;
    const packetSentences = normalizedPolicy
      .split(/(?<=[.:;])\s+/)
      .filter((sentence) => /packet/i.test(sentence));
    expect(packetSentences.length).toBeGreaterThan(3);
    for (const sentence of packetSentences) {
      expect(
        sentence,
        "packet delivery must stay unconditional: no threshold, fallback, or alternative path",
      ).not.toMatch(conditionalDelivery);
    }
    expect(normalizedPolicy).toContain("apply `shq(payload)` once to that complete payload");
    expect(normalizedPolicy).toContain("Never wrap either payload in literal outer double quotes");
    expect(policy).not.toContain('--text "exec <validated-frozen-agent-command>"');
    expect(policy).not.toContain('--text "<slice task packet>"');
    expect(policy).toContain("orca worktree create --name <slice> --base-branch <base-branch> --setup inherit --json");
    expect(policy).not.toContain("orca worktree create --name <slice> --no-parent");
    expect(policy).toContain("terminal read");
    expect(policy).toContain("startupTerminal.handle");
    expect(policy).toMatch(/an\s+unused shell/);
    expect(policy).toMatch(/no agent\/default-task\s+activity/);
    expect(policy).toMatch(/exactly one\s+coordinator-owned startup\s+handle/i);
    expect(policy).toContain("snapshot the exact repository worktree and terminal inventory");
    expect(normalizedPolicy).toContain("before_inventory");
    expect(normalizedPolicy).toContain("after_inventory - before_inventory");
    expect(policy).toContain("generate a unique logical slice name");
    expect(policy).toContain("exactly one create");
    expect(policy.match(/orca worktree create --name <slice>/g)?.length).toBe(1);
    expect(normalizedPolicy).toContain("never retried blindly");
    expect(policy).toContain("SETTLE WINDOW");
    expect(normalizedPolicy).toContain("re-listing the exact repository worktree and terminal inventories every `interval_ms=250`");
    expect(normalizedPolicy).toContain("computing the cumulative `current - before_inventory` difference");
    expect(normalizedPolicy).toContain("computing the cumulative observed set `current - before_inventory`");
    expect(normalizedPolicy).toContain("Filter that cumulative set by the exact repository and generated unique logical slice name");
    expect(normalizedPolicy).toContain("entries that do not match both are foreign and are never adopted or cleaned");
    expect(normalizedPolicy).toContain("At the deadline, perform one final inventory/audit after the last re-list");
    expect(normalizedPolicy).toContain("only a proven zero-candidate result may serialize as zero effect");
    expect(normalizedPolicy).toContain("never retry or issue a second create");
    expect(normalizedPolicy).toMatch(/zero, multiple, or ambiguous candidates serialize/i);
    expect(normalizedPolicy).toContain("complete immutable receipt and ownership proof");
    expect(policy).toContain("exec <validated-frozen-agent-command>");
    expect(policy).toContain("orca terminal read --terminal <startupTerminal.handle> --screen");
    expect(policy).toContain("source=screen");
    expect(normalizedPolicy).toMatch(/provider, model, and\s+effort\s+all present and\s+matching/);
    expect(policy).toContain("bounded machine-only TUI materialization probe");
    expect(policy).toContain("timeout_ms=60000");
    expect(policy).toContain("interval_ms=250");
    expect(policy).toContain("two consecutive screen reads");
    expect(policy).toContain("handle must remain connected");
    expect(policy).toContain("one screen or");
    expect(policy).toContain("one pre-send `tui-idle` result is never sufficient");
    expect(policy).toContain("This probe is not the dependency waiter");
    expect(policy).toContain("performs no model turns");
    expect(policy).toContain("screen-unavailable");
    expect(policy).toContain("matching the frozen tuple");
    expect(normalizedPolicy).toContain("each iteration performs the exact-handle `orca terminal show --terminal <startupTerminal.handle> --json` plus `orca terminal read --terminal <startupTerminal.handle> --screen --json`");
    expect(normalizedPolicy).toContain("Count two CONSECUTIVE matching frames; any nonmatch resets the count to zero");
    expect(normalizedPolicy).toContain("for no more than `timeout_ms=60000`");
    expect(normalizedPolicy).not.toContain("one screen read before");
    expect(normalizedPolicy).not.toContain("one immediate second read");
    expect(normalizedPolicy).not.toContain("one after-inventory snapshot");
    expect(normalizedPolicy).not.toContain("single after_inventory");
    expect(normalizedPolicy).not.toMatch(/\bretry(?:ing)?\s+(?:the\s+)?create\b/i);
    expect(normalizedPolicy).not.toContain("retry the create");
    expect(policy).toMatch(/Do not\s+edit `tasks\.md`/);
    expect(normalizedPolicy).toMatch(
      /Prove that the exact `startupTerminal\.handle` was newly created by this worktree operation, is uniquely owned by this just-created worktree, is an unused shell, and has no agent\/default-task activity\./,
    );
    const lifecycleMarkers = [
      "orca worktree create --name <slice> --base-branch <base-branch> --setup inherit --json",
      "Record an immutable ownership receipt immediately from the create result or the one reconciled candidate",
      "Before any terminal send, inspect that exact handle",
      "Prove that the exact `startupTerminal.handle`",
      "Apply `shq` to every value that crosses a shell boundary and build the fixed provider command only after that proof",
      "Construct `exec_payload` as the complete `exec <validated-frozen-agent-command>` string",
      "orca terminal send --terminal <startupTerminal.handle> \\ --text <shq(exec_payload)>",
      "Then run the bounded machine-only TUI materialization probe loop on that same handle",
      "each iteration performs the exact-handle `orca terminal show --terminal <startupTerminal.handle> --json` plus `orca terminal read --terminal <startupTerminal.handle> --screen --json`",
      "After the route loop reaches two consecutive matching frames, write the complete slice packet,",
      "orca terminal send --terminal <startupTerminal.handle> --text <shq(task_payload)>",
    ];
    let previousLifecyclePosition = -1;
    const lifecyclePositions = lifecycleMarkers.map((marker) => {
      const position = normalizedPolicy.indexOf(marker, previousLifecyclePosition + 1);
      previousLifecyclePosition = position;
      return position;
    });
    expect(lifecyclePositions.every((position) => position >= 0)).toBe(true);
    expect(lifecyclePositions[0]).toBeGreaterThan(normalizedPolicy.indexOf("exactly one create"));
    for (let index = 1; index < lifecyclePositions.length; index += 1) {
      expect(lifecyclePositions[index]).toBeGreaterThan(lifecyclePositions[index - 1]);
    }
    const routeLoopStart = normalizedPolicy.indexOf(
      "Then run the bounded machine-only TUI materialization probe loop",
    );
    const taskPayloadStart = normalizedPolicy.indexOf(
      "After the route loop reaches two consecutive matching frames",
    );
    const routeLoop = normalizedPolicy.slice(routeLoopStart, taskPayloadStart);
    expect(routeLoop.match(/orca terminal show --terminal <startupTerminal\.handle>/g)?.length).toBe(1);
    expect(routeLoop.match(/orca terminal read --terminal <startupTerminal\.handle>/g)?.length).toBe(1);
    expect(routeLoop).not.toContain("orca terminal wait --terminal");
    expect(routeLoop).toContain("Every `interval_ms=250`");
    expect(routeLoop).toContain("any nonmatch resets the count to zero");
    expect(routeLoop.indexOf("tui-idle")).toBeGreaterThan(
      routeLoop.indexOf("Count two CONSECUTIVE matching frames"),
    );
    // AST-02: one worker per ready slice and sequential tasks to the first dependency.
    expect(policy).toContain("Start at most one worker for each planner-ready slice");
    expect(policy).toMatch(/sequential TLC tasks and stops at the\s+first unmet task dependency/);
    // AST-03: exact parked checkpoint and no polling.
    expect(policy).toMatch(
      /slice=<id>; state=parked; completed_through=<task>; next=<task>;\s+blocked_on=<slice:task>; head=<sha>/,
    );
    expect(policy).toContain("does not poll, spin, or spend model turns checking unchanged state");
    // AST-04: exact producer sync, affected gate, and same-terminal follow-up.
    expect(policy).toContain("Synchronize the exact producer commit");
    expect(policy).toMatch(/rerun the\s+affected gate, then follow up the same worker terminal/);
    expect(policy).toMatch(/reacquire its sole worker handle; never dual-send or launch a replacement/);
    // AST-05: ambiguity and conflicts use serial recovery without resolution.
    expect(policy).toContain("ambiguous ownership/dependency, sync conflict, or affected-gate");
    expect(policy).toContain("existing serial recovery path");
    expect(policy).toMatch(/does not\s+resolve conflicts automatically/);
    // AST-06: deterministic integration and owned cleanup with receipt/revalidation/absence proof.
    expect(policy).toContain("integrated in deterministic slice order");
    expect(policy).toContain("Record an immutable ownership receipt");
    expect(policy).toContain("repository, complete worktree id");
    expect(policy).toContain("gitdir, branch, `pre_head`");
    expect(policy).toContain("Record mutable `current_head`");
    expect(policy).toContain("current_handle` separately");
    expect(policy).toContain("immediately revalidate\n   the immutable ownership receipt before cleanup");
    expect(policy).toContain("orca worktree show`/`list`");
    expect(policy).toContain("no symlink");
    expect(policy).toContain("no merge/rebase/cherry-pick/revert in\n   progress");
    expect(policy).toContain("current_head` must be current");
    expect(policy).toMatch(/the same\s+startup handle remains the\s+worker handle/);
    expect(policy).toMatch(/recorded branch tip\s+must equal `current_head`/);
    expect(policy).toContain("git merge-base --is-ancestor <slice-head> <integration-head>");
    expect(policy).toContain("Do not require\n   `current_head` to equal `pre_head`");
    expect(policy).toContain("Stop the exact startup/current worker handle");
    expect(policy).toContain("git branch --delete <branch>");
    expect(policy).toContain("git show-ref --verify --quiet refs/heads/<branch>");
    expect(policy).toContain("detach it at `current_head`");
    expect(policy).toContain("if removal already succeeded, record the exact receipt and identifiers");
    expect(normalizedPolicy).toContain("without claiming that the removed path remains");
    expect(policy).toContain("Remove only by the complete worktree id");
    expect(normalizedPolicy).toContain("Prove Orca, Git, path, branch ref, and terminal absence");
    expect(normalizedPolicy).toMatch(/Never select cleanup by name or\s+branch/);
    expect(policy).toContain("zero owned residue");

    // Ambiguous terminal sends reconcile one effect on the same handle; they never retry or adopt
    // a commit without the complete machine-observable turn proof.
    expect(normalizedPolicy).toContain("Before every logical packet");
    expect(normalizedPolicy).toContain("unique turn ID/phase");
    expect(normalizedPolicy).toContain("`TURN_DONE <phase> head=<40-hex-sha>` (exactly one SHA)");
    expect(normalizedPolicy).toContain("Issue exactly one send for that packet");
    expect(normalizedPolicy).toContain("never retry after a success, error, missing receipt, or `agent_prompt_stalled`");
    expect(normalizedPolicy).toContain("never launch a replacement worker");
    expect(normalizedPolicy).toContain("normal 300-second worker-turn barrier");
    expect(normalizedPolicy).toContain("bounded machine-only effect reconciliation on the same exact startup/current handle");
    expect(normalizedPolicy).toContain("`interval_ms=250`");
    expect(normalizedPolicy).toContain("`timeout_ms=300000`");
    expect(normalizedPolicy).toContain("no model turns");
    expect(normalizedPolicy).toContain("exactly one expected turn is proven end-to-end");
    expect(normalizedPolicy).toContain("two fresh non-Working `source=screen` frames");
    expect(normalizedPolicy).toContain("a `tui-idle` reading agree");
    expect(normalizedPolicy).toContain("receipt/effect divergence");
    expect(normalizedPolicy).toContain("continue without resending");
    expect(normalizedPolicy).toContain("conflicting or multiple marker SHAs");
    expect(normalizedPolicy).toContain("Never clean or adopt a foreign effect");
    expect(normalizedPolicy).toContain("never report success from a commit alone");
    expect(normalizedPolicy).toContain("not a dependency waiter or watchdog");
    expect(normalizedPolicy).toContain("dependency waiting remains event-driven");

    const packetContractAt = policy.indexOf("Before every logical packet");
    const createAt = policy.indexOf("Before the one mutating create");
    const reconciliationAt = policy.indexOf("A successful send follows the normal 300-second worker-turn barrier");
    const serialRecoveryAt = policy.indexOf("No effect by the deadline");
    expect(packetContractAt).toBeGreaterThan(-1);
    expect(createAt).toBeGreaterThan(packetContractAt);
    expect(reconciliationAt).toBeGreaterThan(packetContractAt);
    expect(serialRecoveryAt).toBeGreaterThan(reconciliationAt);

    const packetContractEndAt = policy.indexOf("Before the one mutating create");
    const normalizedPacketContract = policy.slice(packetContractAt, packetContractEndAt).replace(/\s+/g, " ");
    expect(packetContractEndAt).toBeGreaterThan(serialRecoveryAt);
    expect(normalizedPacketContract).toContain("Issue exactly one send for that packet");
    expect(normalizedPacketContract).toContain("never retry after a success, error, missing receipt");
    expect(normalizedPacketContract).toContain("same handle remains connected");
    expect(normalizedPacketContract).toContain("same exact startup/current handle");
    expect(normalizedPacketContract).toContain("different handle");
    expect(normalizedPacketContract).toContain("exact expected task IDs");
    expect(normalizedPacketContract).toContain("expected task-commit count");
    expect(normalizedPacketContract).toContain("allowed changed paths including the task-status path");
    expect(normalizedPacketContract).toContain("exactly one expected turn is proven end-to-end");
    expect(normalizedPacketContract).toContain("inspect it every `interval_ms=250` for at most `timeout_ms=300000`");
    expect(normalizedPacketContract).toContain("with no model turns");
    expect(normalizedPacketContract).toContain("Git HEAD equals that marker");
    expect(normalizedPacketContract).toContain("required task statuses, atomic commits");
    expect(normalizedPacketContract).toContain("gates match");
    expect(normalizedPacketContract).toContain(
      "the marker HEAD is a descendant of the exact `pre_head` proven with `git merge-base --is-ancestor <pre_head> <marker-head>`",
    );
    expect(normalizedPacketContract).toContain(
      "commits in `<pre_head>..<marker-head>` equal the expected task-commit count and identities",
    );
    expect(normalizedPacketContract).toContain(
      "changed paths are a subset of the packet-declared changed-path allowlist, including its task-status path",
    );
    expect(normalizedPacketContract).toContain("A reset, foreign or unrelated commit, extra commit, out-of-scope path, or status mismatch is ambiguous and fails closed");
    expect(normalizedPacketContract).toContain(
      "Only a turn whose phase is exactly `B_PARKED` requires the exact parked-B checkpoint comment",
    );
    expect(normalizedPacketContract).toContain(
      "route, A, and other nonparked turns do not",
    );
    expect(normalizedPacketContract).toContain("continue without resending");
    expect(normalizedPacketContract).toContain("No effect by the deadline");
    expect(normalizedPacketContract).toContain("partial state");
    expect(normalizedPacketContract).toContain("conflicting or multiple marker SHAs");
    expect(normalizedPacketContract).toContain("dirty state");
    expect(normalizedPacketContract).toContain("gate failure");
    expect(normalizedPacketContract).toContain("wrong handle");
    expect(normalizedPacketContract).toContain("ambiguity serializes the lane");
    expect(normalizedPacketContract).toContain("retains it for exact recovery");
    expect(normalizedPacketContract).toContain("Never clean or adopt a foreign effect");
    expect(normalizedPacketContract).toContain("never report success from a commit alone");
    expect(normalizedPacketContract).toContain("not a dependency waiter or watchdog");
    expect(normalizedPacketContract).toContain("dependency waiting remains event-driven");
    expect(normalizedPacketContract).not.toContain("retry the send");
    expect(normalizedPacketContract).not.toContain("accept the commit");
    expect(normalizedPacketContract).toContain(
      "dependency waiting remains event-driven and spends no model turns polling unchanged state",
    );

    const normalizedDxContract = dx.replace(/\s+/g, " ");
    expect(normalizedDxContract).toContain("Before every logical packet");
    expect(normalizedDxContract).toContain("`TURN_DONE <phase> head=<40-hex-sha>`");
    expect(normalizedDxContract).toContain("never retry a success, error, missing receipt, or `agent_prompt_stalled`");
    expect(normalizedDxContract).toContain("same exact startup/current handle; a different handle is rejected; every `interval_ms=250` for at most `timeout_ms=300000`");
    expect(normalizedDxContract).toContain("exactly one expected turn is proven end-to-end");
    expect(normalizedDxContract).toContain("two fresh non-Working `source=screen` frames plus `tui-idle`");
    expect(normalizedDxContract).toContain("a commit alone is never success");
    expect(normalizedDxContract).toContain("dependency waiting remains event-driven");

    const receiptAt = policy.indexOf("Record an immutable ownership receipt");
    const revalidateAt = policy.indexOf("immediately revalidate\n   the immutable ownership receipt before cleanup");
    const stopAt = policy.indexOf("Stop the exact startup/current worker handle");
    const branchDeleteAt = policy.indexOf("git branch --delete <branch>");
    const removeAt = policy.indexOf("Remove only by the complete worktree id");
    const absenceAt = normalizedPolicy.indexOf("Prove Orca, Git, path, branch ref, and terminal absence");
    expect(receiptAt).toBeGreaterThan(-1);
    expect(revalidateAt).toBeGreaterThan(receiptAt);
    expect(stopAt).toBeGreaterThan(revalidateAt);
    expect(branchDeleteAt).toBeGreaterThan(stopAt);
    expect(removeAt).toBeGreaterThan(branchDeleteAt);
    expect(absenceAt).toBeGreaterThan(branchDeleteAt);
    // AST-07: existing TLC and readiness stages stay intact.
    expect(policy).toContain("one atomic commit and scoped gate per task");
    expect(policy).toMatch(/one Technical Verifier per\s+code-changing slice/);
    expect(policy).toContain("frozen grouped deep-review cadence, final QA, and one full gate");
    expect(policy).toContain("no change to TLC task order");
    // Route selection is part of the user-facing adoption contract.
    expect(dx).toContain("roles.implementer.provider/model/effort");
    expect(dx).toContain("always launch an explicit command, never trust an");
    expect(dx).toContain("codex --model <shq(model)>");
    expect(dx).toContain("claude --model <shq(model)> --effort <shq(effort)>");
    expect(dx).toContain("cursor agent");
    expect(dx).toContain("--help`/availability check");
    expect(dx).toContain("send the complete `exec` payload once");
    expect(dx).toContain("terminal read --terminal <handle> --screen --json");
    expect(dx).toContain("two consecutive screen reads");
    expect(dx).toContain("timeout and small interval");
    expect(dx).toContain("not the dependency waiter");
    expect(dx).toContain("never retried blindly");
    expect(dx).toContain("before/after inventory difference");
    const normalizedDx = dx.replace(/\s+/g, " ");
    expect(normalizedDx).toContain("cumulative observed set `current - before_inventory`");
    expect(normalizedDx).toContain("filter candidates by the exact repository and generated unique logical slice name");
    expect(normalizedDx).toContain("Nonmatching entries are foreign and are never adopted or cleaned");
    expect(normalizedDx).toContain("Perform a final audit at the deadline");
    expect(normalizedDx).not.toContain("one bounded before/after inventory difference");
    expect(dx).toContain("Zero, multiple, or ambiguous");
    expect(dx).toContain("Always use the two-step");
    expect(dx).toContain("startup-shell promotion");
    expect(dx).toContain("Never open a second");
    expect(dx).toContain("terminal send");
  });

  it("IT-010 resolves the adopted default to assisted and honors disabled serialization", () => {
    const root = mkdtempSync(join(tmpdir(), "assisted-contract-"));
    const featureDir = join(root, ".specs", "features", "fixture");
    const adopt = join(repositoryRoot, "scripts", "adopt.py");
    const resolver = join(root, ".agents", "skills", "workflow-config", "scripts", "workflow_config.py");
    const planner = join(root, ".agents", "skills", "workflow-config", "scripts", "parallel_plan.py");
    const executor = join(root, ".agents", "skills", "autonomous", "scripts", "parallel_execute.py");

    try {
      execFileSync("python3", [adopt, root], { encoding: "utf8" });
      execFileSync("git", ["init", "-q"], { cwd: root });
      execFileSync("git", ["config", "user.email", "test@example.com"], { cwd: root });
      execFileSync("git", ["config", "user.name", "Contract Test"], { cwd: root });
      writeFileSync(join(root, "seed"), "seed\n", "utf8");
      execFileSync("git", ["add", "seed"], { cwd: root });
      execFileSync("git", ["commit", "-qm", "seed"], { cwd: root });
      mkdirSync(featureDir, { recursive: true });
      writeFileSync(
        join(featureDir, "tasks.md"),
        [
          "## Vertical Slice Closure",
          "| Slice | Observable outcome | Independent gate | Merge if later slices are cancelled? | Why |",
          "| --- | --- | --- | --- | --- |",
          "| A | first | true | yes | independent |",
          "| B | second | true | yes | independent |",
          "",
          "## Tasks",
          "",
          "### T1: first",
          "**Status:** pending",
          "**Slice:** A",
          "**Where:** src/a.py",
          "**Depends on:** None",
          "**Resources:** none",
          "",
          "### T2: second",
          "**Status:** pending",
          "**Slice:** B",
          "**Where:** src/b.py",
          "**Depends on:** None",
          "**Resources:** none",
          "",
        ].join("\n"),
        "utf8",
      );

      const adoptedConfigPath = join(root, ".my-workflow.toml");
      const adoptedExamplePath = join(root, ".my-workflow.toml.example");
      expect(readFileSync(adoptedConfigPath, "utf8")).toContain('mode = "assisted"');
      const explicit = JSON.parse(
        execFileSync(
          "python3",
          [resolver, "--root", root, "--feature", "fixture", "--slices", "2", "--native-provider", "codex"],
          { encoding: "utf8" },
        ),
      ) as { parallelization: { mode: string } };
      expect(explicit.parallelization.mode).toBe("assisted");

      for (const configPath of [adoptedConfigPath, adoptedExamplePath]) {
        const config = readFileSync(configPath, "utf8").replace(/^mode = "assisted".*\n/m, "");
        writeFileSync(configPath, config, "utf8");
      }
      const resolved = JSON.parse(
        execFileSync(
          "python3",
          [resolver, "--root", root, "--feature", "fixture", "--slices", "2", "--native-provider", "codex"],
          { encoding: "utf8" },
        ),
      ) as { parallelization: { mode: string } };
      expect(resolved.parallelization.mode).toBe("assisted");

      const adoptedAgents = readFileSync(join(root, "AGENTS.md"), "utf8");
      const adoptedAutonomous = readFileSync(join(root, ".agents", "skills", "autonomous", "SKILL.md"), "utf8");
      const adoptedPolicy = readFileSync(join(root, ".agents", "skills", "autonomous", "references", "parallelization.md"), "utf8");
      const normalizedAgents = adoptedAgents.replace(/\s+/g, " ");
      const normalizedAutonomous = adoptedAutonomous.replace(/\s+/g, " ");
      const normalizedPolicy = adoptedPolicy.replace(/\s+/g, " ");
      expect(normalizedAgents).toContain("use coordinator-assisted inter-slice dispatch by default");
      expect(normalizedAgents).toContain("Use serial execution only for explicit");
      expect(normalizedAgents).not.toContain("serial execution as the default");
      expect(normalizedAutonomous).toContain("Coordinator-assisted dispatch is the default when the plan exposes safe independent slices");
      expect(normalizedPolicy).toContain("makes coordinator-assisted concurrency the default between safe independent slices");
      expect(normalizedPolicy).not.toContain("serial fallback remains the default");

      const plan = JSON.parse(
        execFileSync("python3", [planner, "--root", root, "--feature", "fixture"], {
          encoding: "utf8",
        }),
      ) as { mode: string; fallback: boolean; lanes: Array<{ id: string; status: string }> };
      expect(plan.mode).toBe("assisted");
      expect(plan.fallback).toBe(false);
      expect(plan.lanes).toEqual([
        { id: "slice-A", slice: "A", task: "T1", status: "ready", sync_after: [], declared_paths: ["src/a.py"], resources: [] },
        { id: "slice-B", slice: "B", task: "T2", status: "ready", sync_after: [], declared_paths: ["src/b.py"], resources: [] },
      ]);

      const assisted = JSON.parse(
        execFileSync("python3", [executor, "start", "--root", root, "--feature", "fixture"], {
          encoding: "utf8",
        }),
      ) as { mode: string; fallback: boolean; reason: string; lanes: Array<{ id: string }> };
      expect(assisted.mode).toBe("assisted");
      expect(assisted.fallback).toBe(true);
      expect(assisted.reason).toMatch(/^assisted-capability:/);

      const workflowPath = join(featureDir, "workflow.json");
      const workflow = JSON.parse(readFileSync(workflowPath, "utf8")) as Record<string, unknown>;
      workflow.parallelization = { mode: "disabled", resource_provider: null };
      writeFileSync(
        workflowPath,
        JSON.stringify(workflow, null, 2) + "\n",
        "utf8",
      );
      const disabled = JSON.parse(
        execFileSync("python3", [executor, "start", "--root", root, "--feature", "fixture"], {
          encoding: "utf8",
        }),
      ) as { mode: string; fallback: boolean; reason: string; lanes: Array<{ id: string }> };
      expect(disabled.mode).toBe("disabled");
      expect(disabled.fallback).toBe(true);
      expect(disabled.reason).toBe("disabled-mode");
      expect(disabled.lanes).toEqual([{ id: "serial", slice: null, task: null, status: "ready", sync_after: [] }]);
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });

  it("SEC-006 enforces coordinator ownership before assisted cleanup", () => {
    const policy = readRepositoryFile(
      ".agents/skills/autonomous/references/parallelization.md",
    );
    const threatModel = readRepositoryFile(
      ".specs/features/host-agnostic-slice-parallelization/threat-model.md",
    );

    expect(policy).toContain("Remove only by the complete worktree id");
    expect(policy).toMatch(/missing\s+ownership/);
    expect(policy).toContain("retains the exact");
    expect(threatModel).toContain("Assisted cleanup -> Git/Orca resource");
    expect(threatModel).toContain("every 250 ms for at most 60000 ms");
    expect(threatModel).toContain("cumulative observed set");
    expect(threatModel).toContain("nonmatching entries are foreign and never adopted or cleaned");
    expect(threatModel).toContain("deadline receives a final audit");
    expect(threatModel).not.toContain("one-shot before/after snapshot");
    expect(threatModel).not.toContain("Before/after exact inventory");
    expect(threatModel).toMatch(/Exact create receipt, Orca\/Git identity revalidation, integrated ancestor, ordered stop\/detach\/branch-delete\/ref-proof\/remove, and absence proof; SEC-008/);
    expect(threatModel).toMatch(/only clean, integrated,\s+coordinator-owned worktrees are removable/);
  });
});
