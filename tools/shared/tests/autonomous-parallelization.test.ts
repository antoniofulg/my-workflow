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

    // AST-01: assisted execution is separate from automatic compatibility.
    expect(policy).toContain("explicitly authorized operator path");
    expect(policy).toContain("does not write a compatibility PASS");
    expect(policy).toMatch(/automatic execution remains\s+unsupported and serial/);
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
    // AST-06: deterministic integration and owned cleanup with residue proof.
    expect(policy).toContain("integrated in deterministic slice order");
    expect(policy).toContain("clean, integrated, coordinator-owned worktree and branch");
    expect(policy).toMatch(/Prove zero owned\s+worker\/worktree residue/);
    // AST-07: existing TLC and readiness stages stay intact.
    expect(policy).toContain("one atomic commit and scoped gate per task");
    expect(policy).toMatch(/one Technical Verifier per\s+code-changing slice/);
    expect(policy).toContain("frozen grouped deep-review cadence, final QA, and one full gate");
    expect(policy).toContain("no change to TLC task order");
    // Route selection is part of the user-facing adoption contract.
    expect(dx).toContain("worktree create --agent --prompt");
    expect(dx).toContain("terminal create` with the exact frozen command");
    expect(dx).toContain("terminal wait --for tui-idle");
    expect(dx).toContain("terminal send");
  });

  it("SEC-006 enforces coordinator ownership before assisted cleanup", () => {
    const policy = readRepositoryFile(
      ".agents/skills/autonomous/references/parallelization.md",
    );
    const threatModel = readRepositoryFile(
      ".specs/features/host-agnostic-slice-parallelization/threat-model.md",
    );

    expect(policy).toContain("only its clean, integrated, coordinator-owned worktree and branch");
    expect(policy).toMatch(/missing ownership or residue proof stops\s+deletion/);
    expect(threatModel).toContain("Assisted cleanup -> Git/Orca resource");
    expect(threatModel).toContain("Ownership, integrated commit, clean state, and residue proof; SEC-008");
    expect(threatModel).toMatch(/only clean, integrated,\s+coordinator-owned worktrees are removable/);
  });
});
