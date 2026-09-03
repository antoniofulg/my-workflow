import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "bun:test";

const repositoryRoot = process.cwd();
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

function readRepositoryFile(relativePath: string): string {
  return readFileSync(join(repositoryRoot, relativePath), "utf8");
}

type RoleRoute = {
  stage: string;
  owner: string;
  authorRelation: string;
  tree: string;
  cardinality: string;
};

function parseRoleRoute(policy: string): RoleRoute[] {
  const section = policy.match(
    /<!-- role-route:v1 -->([\s\S]*?)<!-- \/role-route:v1 -->/,
  )?.[1];
  expect(section).toBeDefined();

  const rows = section
    ?.split("\n")
    .filter((line) => /^\|/.test(line.trim()) && !/^\|\s*-/.test(line.trim()))
    .map((line) => line.split("|").slice(1, -1).map((cell) => cell.trim())) ?? [];
  expect(rows.length).toBeGreaterThan(1);

  const [headers, ...data] = rows;
  expect(headers).toEqual(["stage", "owner", "author relation", "tree", "cardinality"]);
  return data.map(([stage, owner, authorRelation, tree, cardinality]) => ({
    stage,
    owner,
    authorRelation,
    tree,
    cardinality,
  }));
}

function routeOwnerForPacket(role: "implementer" | "verifier" | "deep-reviewer"): string[] {
  if (role === "implementer") return ["implementer", "last-implementer"];
  if (role === "verifier") return ["technical-verifier", "qa-plan", "qa-execute"];
  return ["deep-reviewer"];
}

function packetPathsForRole(role: "implementer" | "verifier" | "deep-reviewer"): string[] {
  if (role === "implementer") return implementerPacketPaths;
  if (role === "verifier") return verifierPacketPaths;
  return deepReviewPacketPaths;
}

function expectedRoute(route: RoleRoute[], stage: string): RoleRoute {
  const row = route.find((candidate) => candidate.stage === stage);
  expect(row, `missing role-route stage: ${stage}`).toBeDefined();
  return row as RoleRoute;
}

function treeFor(row: RoleRoute, slice: { id: string; ref: string } | undefined): string {
  if (row.tree === "private-slice" || row.tree === "private-checkpoint") {
    expect(slice).toBeDefined();
    return `private:${slice?.id}@${slice?.ref}`;
  }
  if (row.tree === "integrated-head") return "integrated@i1";
  throw new Error(`unsupported role-route tree: ${row.tree}`);
}

describe("autonomous parallel slice dispatch contract", () => {
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

  it("IT-012 derives the proof trace from the shipped role-route table", () => {
    const policy = readRepositoryFile(
      ".agents/skills/autonomous/references/parallelization.md",
    );
    const route = parseRoleRoute(policy);
    const stageOrder = route.map(({ stage }) => stage);
    expect(stageOrder).toEqual([
      "implement",
      "technical",
      "integrate",
      "deep-review",
      "qa-plan",
      "qa-execute",
      "handoff",
    ]);

    expect(expectedRoute(route, "implement")).toMatchObject({
      owner: "implementer",
      authorRelation: "author-only",
      tree: "private-slice",
      cardinality: "per-slice",
    });
    expect(expectedRoute(route, "technical")).toMatchObject({
      owner: "technical-verifier",
      authorRelation: "fresh-not-author",
      tree: "private-checkpoint",
      cardinality: "per-slice",
    });
    expect(expectedRoute(route, "deep-review")).toMatchObject({
      owner: "deep-reviewer",
      authorRelation: "fresh-not-author",
      tree: "integrated-head",
      cardinality: "per-group",
    });
    for (const stage of ["qa-plan", "qa-execute"]) {
      expect(expectedRoute(route, stage)).toMatchObject({
        owner: stage,
        authorRelation: "fresh-not-author",
        tree: "integrated-head",
        cardinality: "once",
      });
    }
    expect(expectedRoute(route, "handoff")).toMatchObject({
      owner: "last-implementer",
      authorRelation: "author-only-no-proof",
      tree: "private-checkpoint",
      cardinality: "last-implementer",
    });

    const slices = [
      { id: "S1", ref: "a1" },
      { id: "S2", ref: "b1" },
    ];
    const trace = route.flatMap((row) => {
      if (row.cardinality === "per-slice") {
        return slices.map((slice) => ({
          phase: row.stage,
          actor: `${row.owner}-${slice.id}`,
          tree: treeFor(row, slice),
        }));
      }
      if (row.cardinality === "per-group") {
        return [{ phase: row.stage, actor: `${row.owner}-G1`, tree: treeFor(row, undefined) }];
      }
      if (row.cardinality === "last-implementer") {
        return [{
          phase: row.stage,
          actor: `${row.owner}-${slices.at(-1)?.id}`,
          tree: treeFor(row, slices.at(-1)),
        }];
      }
      return [{ phase: row.stage, actor: row.owner, tree: treeFor(row, undefined) }];
    });

    const authors = new Set(
      trace.filter(({ phase }) => phase === "implement").map(({ actor }) => actor),
    );
    const proofActors = new Set(
      trace
        .filter(({ phase }) => ["technical", "deep-review", "qa-plan", "qa-execute"].includes(phase))
        .map(({ actor }) => actor),
    );
    expect([...authors].every((author) => !proofActors.has(author))).toBe(true);
    expect(trace.filter(({ phase }) => phase === "technical").map(({ tree }) => tree)).toEqual(
      slices.map((slice) => treeFor(expectedRoute(route, "technical"), slice)),
    );
    expect(
      trace
        .filter(({ phase }) => ["deep-review", "qa-plan", "qa-execute"].includes(phase))
        .map(({ tree }) => tree),
    ).toEqual(
      ["deep-review", "qa-plan", "qa-execute"].map((stage) =>
        treeFor(expectedRoute(route, stage), undefined),
      ),
    );
    expect(trace.at(-1)).toEqual({
      phase: expectedRoute(route, "handoff").stage,
      actor: `${expectedRoute(route, "handoff").owner}-${slices.at(-1)?.id}`,
      tree: treeFor(expectedRoute(route, "handoff"), slices.at(-1)),
    });
    expect(stageOrder.indexOf("integrate")).toBeLessThan(stageOrder.indexOf("deep-review"));
    expect(stageOrder.indexOf("deep-review")).toBeLessThan(stageOrder.indexOf("qa-plan"));

    const packetRoles: Array<"implementer" | "verifier" | "deep-reviewer"> = [
      "implementer",
      "verifier",
      "deep-reviewer",
    ];
    for (const role of packetRoles) {
      const owners = routeOwnerForPacket(role);
      const ownedStages = route.filter(({ owner }) => owners.includes(owner));
      expect(ownedStages.length, `no route rows for ${role}`).toBeGreaterThan(0);
      for (const relativePath of packetPathsForRole(role)) {
        const packet = readRepositoryFile(relativePath);
        for (const row of ownedStages) {
          if (row.stage === "implement") {
            expect(packet).toMatch(/one implementer owns exactly one slice/i);
            expect(packet).toMatch(/tasks inside the slice remain sequentially/i);
          }
          if (row.stage === "technical") {
            expect(packet).toMatch(/fresh Technical Verifier/i);
            expect(packet).toMatch(/private writer (?:tree|worktree|checkpoint)/i);
          }
          if (row.stage === "deep-review") {
            expect(packet).toMatch(/fresh/i);
            expect(packet).toMatch(/integrated commit range|integrated tree/i);
            expect(packet).toMatch(/(?:not|never) (?:a |the )?private writer tree/i);
          }
          if (row.stage === "qa-plan" || row.stage === "qa-execute") {
            expect(packet).toMatch(/fresh QA Plan.*fresh QA Execute/is);
            expect(packet).toMatch(/integrated final tree/i);
            expect(packet).toMatch(/do not\s+read a private writer tree/i);
          }
          if (row.stage === "handoff") {
            expect(packet).toContain("compact handoff");
            expect(packet).not.toMatch(/certif(?:y|ies) downstream proof/i);
          }
        }
      }
    }
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
    expect(policy).toContain("Exactly one ready slice is a serial-integration lane");
    expect(policy).toContain("Persistent writer worktrees are admitted only when at least two");
    expect(policy).toContain("slices are selected");
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
    expect(policy).toMatch(/workflow-spec-driven\s+skill is slice-native/i);
    expect(policy).toMatch(/independent slices may run concurrently/i);
    expect(policy).toMatch(/tasks inside one slice\s+remain sequential in its worker\/worktree/i);
    expect(policy).toMatch(/uncertainty or failure\s+serializes safely/i);
    expect(autonomous).toContain(
      "serial execution is used when exactly one ready slice exists, explicit `disabled` mode, or any",
    );
    expect(autonomous).toContain(
      "fail-closed condition; concurrent isolated writer worktrees require at least two compatible ready",
    );
    expect(autonomous).not.toContain(
      "serial execution is reserved for explicit `disabled` mode or a fail-closed condition",
    );

    const validation = [
      readRepositoryFile(".agents/skills/wverify/SKILL.md"),
      readRepositoryFile(".agents/skills/wverify/references/validation-template.md"),
    ].join("\n");
    expect(validation).toContain("validation-[slice].md");
    expect(validation).toContain("`validation.md` only for final integrated validation");
  });
});
