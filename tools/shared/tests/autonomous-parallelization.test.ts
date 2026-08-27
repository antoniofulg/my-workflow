import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

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

  it("IT-005 covers the explicitly authorized coordinator-assisted Orca lifecycle", () => {
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
    expect(policy).toContain("explicitly authorized operator path");
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
    expect(spec).toMatch(/\| AST-01 \|[\s\S]*?Contract verified; E2E pending/);
    expect(implementer.provider).toBeTruthy();
    expect(implementer.model).toBeTruthy();
    expect(implementer.effort).toBeTruthy();
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
    expect(normalizedPolicy).toContain("complete slice packet");
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
    expect(policy).toContain("exec <validated-frozen-agent-command>");
    expect(policy).toContain("orca terminal read --terminal <startupTerminal.handle> --screen");
    expect(policy).toContain("source=screen");
    expect(policy).toMatch(/provider, model, and\s+effort\s+all present and\s+matching/);
    expect(policy).toContain("screen-unavailable");
    expect(policy).toContain("matching the frozen tuple");
    expect(policy).toMatch(/Do not\s+edit `tasks\.md`/);
    expect(normalizedPolicy).toMatch(
      /Prove that the exact `startupTerminal\.handle` was newly created by this worktree operation, is uniquely owned by this just-created worktree, is an unused shell, and has no agent\/default-task activity\./,
    );
    const lifecycleMarkers = [
      "Record an immutable ownership receipt immediately from the create result",
      "Before any terminal send, inspect that exact handle",
      "Prove that the exact `startupTerminal.handle`",
      "Apply `shq` to every value that crosses a shell boundary and build the fixed provider command only after that proof",
      "Construct `exec_payload` as the complete `exec <validated-frozen-agent-command>` string",
      "orca terminal send --terminal <startupTerminal.handle> \\ --text <shq(exec_payload)>",
      "orca terminal wait --terminal <startupTerminal.handle> --for tui-idle",
      "orca terminal read --terminal <startupTerminal.handle> --screen",
      "After the screen proof matches the frozen route, construct `task_payload` as the complete slice",
      "orca terminal send --terminal <startupTerminal.handle> --text <shq(task_payload)>",
    ];
    lifecycleMarkers.splice(2, 0, "orca terminal show --terminal <startupTerminal.handle> --json");
    const lifecyclePositions = lifecycleMarkers.map((marker) => normalizedPolicy.indexOf(marker));
    expect(lifecyclePositions.every((position) => position >= 0)).toBe(true);
    for (let index = 1; index < lifecyclePositions.length; index += 1) {
      expect(lifecyclePositions[index]).toBeGreaterThan(lifecyclePositions[index - 1]);
    }
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
    expect(dx).toContain("wait for `tui-idle`, then run");
    expect(dx).toContain("terminal read --terminal <handle> --screen --json");
    expect(dx).toContain("Always use the two-step");
    expect(dx).toContain("startup-shell promotion");
    expect(dx).toContain("Never open a second");
    expect(dx).toContain("terminal send");
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
    expect(threatModel).toMatch(/Exact create receipt, Orca\/Git identity revalidation, integrated ancestor, ordered stop\/detach\/branch-delete\/ref-proof\/remove, and absence proof; SEC-008/);
    expect(threatModel).toMatch(/only clean, integrated,\s+coordinator-owned worktrees are removable/);
  });
});
