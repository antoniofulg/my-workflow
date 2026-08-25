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
    const policy = readRepositoryFile(
      ".agents/skills/autonomous/references/parallelization.md",
    );
    const qa = readRepositoryFile(
      ".specs/features/parallel-slice-executor/qa-pilot.md",
    );

    expect(executor).toContain('parser.add_argument("--adapter", choices=("auto", "orca")');
    expect(executor).toContain('parser.add_argument("--technical-verifier-receipt"');
    expect(executor).toContain('"unsupported-adapter"');
    expect(executor).toContain("resource_provider");
    expect(executor).toContain("gate_required");
    expect(adapter).toContain('CAPABILITY = "orchestration.contract.v1"');
    expect(policy).toContain("orchestration.contract.v1");
    expect(policy).toContain("check --run <run> --wait");
    expect(policy).toContain("ack");
    expect(policy).toContain("same terminal");
    expect(policy).toContain("merge");
    expect(policy).toContain("Resources: none");
    expect(policy).toContain("E2E-001 remains untested");
    expect(qa).toContain("**Status:** untested");
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
});
