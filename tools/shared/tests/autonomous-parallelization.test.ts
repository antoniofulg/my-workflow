import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const repositoryRoot = process.cwd();

function readRepositoryFile(relativePath: string): string {
  return readFileSync(join(repositoryRoot, relativePath), "utf8");
}

describe("autonomous parallel slice dispatch contract", () => {
  const implementerPacketPaths = [
    "templates/agents/claude/implementer.md",
    "templates/agents/codex/implementer.toml",
    "templates/agents/cursor/implementer.md",
  ];
  const verifierPacketPaths = [
    "templates/agents/claude/verifier.md",
    "templates/agents/codex/verifier.toml",
    "templates/agents/cursor/verifier.md",
  ];
  const deepReviewPacketPaths = [
    "templates/agents/claude/deep-reviewer.md",
    "templates/agents/codex/deep-reviewer.toml",
    "templates/agents/cursor/deep-reviewer.md",
  ];

  it("UT-015 keeps tasks sequential inside one implementer slice", () => {
    for (const relativePath of implementerPacketPaths) {
      const packet = readRepositoryFile(relativePath);
      expect(packet).toMatch(/one slice/i);
      expect(packet).toMatch(/tasks? inside (?:the )?slice(?: remain| run)? sequentially/i);
      expect(packet).toContain("scoped gate");
      expect(packet).toContain("atomic commit");
      expect(packet).toContain("compact handoff");
      expect(packet).not.toMatch(/one implementer (?:at a time|globally)/i);
      expect(packet).not.toContain("Batch complete");
      expect(packet).not.toMatch(/final QA/i);
    }
  });

  it("UT-016 gives every proof phase a fresh, identity-separated tree boundary", () => {
    for (const relativePath of verifierPacketPaths) {
      const packet = readRepositoryFile(relativePath);
      expect(packet).toMatch(/fresh Technical Verifier/i);
      expect(packet).toMatch(/author(?:'s| and) .*verifier.*identit/i);
      expect(packet).toMatch(/private writer (?:tree|worktree|checkpoint)/i);
      expect(packet).toMatch(/integrated (?:commit range|final tree)/i);
      expect(packet).toMatch(/fresh QA Plan.*fresh QA Execute/is);
      expect(packet).toMatch(/does not fix|do not fix/i);
    }

    for (const relativePath of deepReviewPacketPaths) {
      const packet = readRepositoryFile(relativePath);
      expect(packet).toMatch(/fresh/i);
      expect(packet).toMatch(/integrated commit range|integrated tree/i);
      expect(packet).toMatch(/(?:not|never) (?:a |the )?private writer tree/i);
      expect(packet).toMatch(/read-only/i);
    }
  });

  it("IT-012 routes a two-slice trace through the intended trees and actors", () => {
    const trace = [
      { phase: "implement", actor: "implementer-S1", tree: "private:S1@a1" },
      { phase: "technical", actor: "verifier-S1", tree: "private:S1@a1" },
      { phase: "implement", actor: "implementer-S2", tree: "private:S2@b1" },
      { phase: "technical", actor: "verifier-S2", tree: "private:S2@b1" },
      { phase: "integrate", actor: "coordinator", tree: "integrated@i1" },
      { phase: "deep-review", actor: "deep-reviewer-G1", tree: "integrated@i1" },
      { phase: "qa-plan", actor: "qa-plan-Q1", tree: "integrated@i1" },
      { phase: "qa-execute", actor: "qa-execute-Q1", tree: "integrated@i1" },
      { phase: "handoff", actor: "implementer-S2", tree: "private:S2@b1" },
    ];
    const authors = new Set(["implementer-S1", "implementer-S2"]);
    const proofActors = new Set(
      trace
        .filter(({ phase }) => ["technical", "deep-review", "qa-plan", "qa-execute"].includes(phase))
        .map(({ actor }) => actor),
    );

    expect(trace.filter(({ phase }) => phase === "technical").map(({ tree }) => tree)).toEqual([
      "private:S1@a1",
      "private:S2@b1",
    ]);
    expect(trace.filter(({ phase }) => ["deep-review", "qa-plan", "qa-execute"].includes(phase)).map(({ tree }) => tree)).toEqual([
      "integrated@i1",
      "integrated@i1",
      "integrated@i1",
    ]);
    expect([...authors].every((author) => !proofActors.has(author))).toBe(true);
    expect(trace.at(-1)).toEqual({
      phase: "handoff",
      actor: "implementer-S2",
      tree: "private:S2@b1",
    });
    expect(trace.findIndex(({ phase }) => phase === "integrate")).toBeLessThan(
      trace.findIndex(({ phase }) => phase === "deep-review"),
    );
    expect(trace.findIndex(({ phase }) => phase === "deep-review")).toBeLessThan(
      trace.findIndex(({ phase }) => phase === "qa-plan"),
    );
  });

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
});
