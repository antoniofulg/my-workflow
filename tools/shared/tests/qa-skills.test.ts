import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const repositoryRoot = process.cwd();

function readRepositoryFile(relativePath: string): string {
  return readFileSync(join(repositoryRoot, relativePath), "utf8");
}

function isIgnored(relativePath: string): boolean {
  try {
    execFileSync("git", ["check-ignore", "--no-index", "--quiet", "--", relativePath], {
      cwd: repositoryRoot,
      stdio: "ignore",
    });
    return true;
  } catch {
    return false;
  }
}

function tracked(relativePath: string): string {
  return execFileSync("git", ["ls-files", "--", relativePath], {
    cwd: repositoryRoot,
    encoding: "utf8",
  }).trim();
}

function parseSkillMetadata(source: string, relativePath: string): { name: string; description: string } {
  const frontmatter = source.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/)?.[1];
  const name = frontmatter?.match(/^name:\s*(.+)$/m)?.[1]?.trim();
  const description = frontmatter?.match(/^description:\s*(.+)$/m)?.[1]?.trim();

  if (!name || !description) {
    throw new Error(`Missing valid initial frontmatter in ${relativePath}`);
  }

  return { name, description };
}

function skillMetadata(relativePath: string): { name: string; description: string } {
  return parseSkillMetadata(readRepositoryFile(relativePath), relativePath);
}

function normalizePacket(source: string): string {
  return source.replaceAll("`", "").replace(/\s+/g, " ").trim();
}

const verifierPacketPaths = [
  ".cursor/agents/verifier.md",
  ".claude/agents/verifier.md",
  ".codex/agents/verifier.toml",
] as const;

describe("QA workflow artifact policy", () => {
  it("IT-007 ignores generated Deep Review output but keeps learnings eligible", () => {
    const gitignore = readRepositoryFile(".gitignore");

    expect(gitignore).toContain(".deep-review/*");
    expect(gitignore).toContain("!.deep-review/learnings.md");
    expect(isIgnored(".deep-review/findings.md")).toBe(true);
    expect(isIgnored(".deep-review/qa-skills-t1/agents/cohort-c01.json")).toBe(true);
    expect(isIgnored(".deep-review/learnings.md")).toBe(false);
  });

  it("IT-014 keeps feature workflow state versioned and documents legacy migration", () => {
    const readme = readRepositoryFile("README.md");
    const artifactLifecycle = readRepositoryFile("docs/guidelines/ARTIFACT-LIFECYCLE.md");

    expect(isIgnored(".specs/features/qa-skills/spec.md")).toBe(false);
    expect(isIgnored(".specs/STATE.md")).toBe(false);
    expect(isIgnored(".specs/AD-INDEX.md")).toBe(false);
    expect(tracked(".specs/STATE.md")).toBe(".specs/STATE.md");
    expect(tracked(".specs/AD-INDEX.md")).toBe(".specs/AD-INDEX.md");
    expect(readme.replace(/\s+/g, " ")).toContain(
      "Feature workflow state follows the [artifact lifecycle]",
    );
    const lifecycle = artifactLifecycle.replace(/\s+/g, " ");
    expect(lifecycle).toContain("`.specs/features/` is versioned workflow state");
    expect(lifecycle).toContain("exact legacy managed `.specs/features/` ignore line");
    expect(lifecycle).toContain("never stages or commits files");
  });

  it("IT-015 treats versioned task state as the commit precondition", () => {
    const agents = readRepositoryFile("AGENTS.md");
    const loop = readRepositoryFile("docs/workflow/loop.md");
    const specDriven = readRepositoryFile(".agents/skills/tlc-spec-driven/SKILL.md");
    const implementer = readRepositoryFile(".agents/skills/tlc-spec-driven/references/implement.md");
    const validator = readRepositoryFile(".agents/skills/tlc-spec-driven/references/validate.md");
    const memory = readRepositoryFile(".agents/skills/tlc-spec-driven/references/memory.md");
    const providerPackets = [
      readRepositoryFile(".cursor/agents/implementer.md"),
      readRepositoryFile(".claude/agents/implementer.md"),
      readRepositoryFile(".codex/agents/implementer.toml"),
    ];
    const plannerPackets = [
      readRepositoryFile(".cursor/agents/planner.md"),
      readRepositoryFile(".claude/agents/planner.md"),
      readRepositoryFile(".codex/agents/planner.toml"),
    ];

    expect(agents).toMatch(
      /update `tasks\.md`\s+when present, or the inline execution plan when Tasks is skipped, before committing/,
    );
    expect(loop).toMatch(
      /update `tasks\.md` when present, or the inline execution plan when Tasks is skipped, first/,
    );
    expect(specDriven).toContain("When `tasks.md` is present, mark the task complete there");
    expect(specDriven).toContain(
      "when Tasks is skipped, update and verify the inline execution plan before committing",
    );
    expect(specDriven).toContain(
      "When a formal `tasks.md` exists, run `<skill-dir>/scripts/validate_tasks.py` against it",
    );
    expect(specDriven).toContain(
      "When Tasks was skipped, verify the inline execution plan instead",
    );
    expect(specDriven).toContain(
      "Feature files under `.specs/features/` are versioned workflow state",
    );
    expect(agents).toContain("reconcile Handoff + git");
    expect(memory).toMatch(/when Tasks\s+was skipped,\s+the inline execution-plan completion/);
    expect(validator).toContain("When Tasks was skipped, run the gate command recorded in the inline execution plan");
    expect(implementer).toContain("close the task record **before** creating the commit");
    expect(implementer).toContain("their task/status updates belong in the atomic commit");
    expect(implementer.replace(/\s+/g, " ")).toContain(
      "verify the local status/traceability updates before committing",
    );
    expect(implementer).toContain("If `tasks.md` is present, mark the task complete in `tasks.md`.");
    expect(implementer).toContain("unrelated bug outside an active, approved review loop");
    expect(implementer).toContain("Findings inside that loop follow `REVIEW-ROUNDS.md`");
    expect(implementer).toMatch(
      /If Tasks was skipped, mark the\s+current inline execution-plan step complete/,
    );
    expect(implementer.indexOf("close the task record **before** creating the commit")).toBeLessThan(
      implementer.indexOf("Create **one** atomic commit"),
    );
    expect(implementer).not.toContain("Feature planning files under `.specs/features/` stay ignored");
    for (const packet of providerPackets) {
      expect(packet).toMatch(
        /tasks\.md`? when present,? or the task payload and inline execution plan/,
      );
      expect(packet).toContain("inline execution plan when Tasks is skipped");
      expect(packet).toContain("current local task/spec traceability");
    }
    for (const packet of plannerPackets) {
      expect(packet).toMatch(
        /tasks\.md`? when present or the\s+task payload and inline execution plan when Tasks is skipped/,
      );
    }
    expect(tracked(".specs/features/qa-skills/tasks.md")).toBe(
      ".specs/features/qa-skills/tasks.md",
    );
  });

});

describe("canonical QA skills", () => {
  const qaPlanPath = ".agents/skills/qa-plan/SKILL.md";
  const qaExecutePath = ".agents/skills/qa-execute/SKILL.md";

  it("IT-001 exposes model-invoked skills with matching names", () => {
    for (const [relativePath, expectedName, inspirationUrl] of [
      [qaPlanPath, "qa-plan", "https://github.com/pedronauck/skills/tree/main/skills/mine/qa-report"],
      [qaExecutePath, "qa-execute", "https://github.com/pedronauck/skills/tree/main/skills/mine/qa-execution"],
    ] as const) {
      const source = readRepositoryFile(relativePath);
      const metadata = skillMetadata(relativePath);

      expect(metadata.name).toBe(expectedName);
      expect(source).toContain("metadata:");
      expect(source).toContain("author: Antonio Fulgêncio");
      expect(source).toContain("## Provenance");
      expect(source).toContain("Pedro Nauck");
      expect(source).toContain("original project-owned adaptation");
      expect(source).toContain(inspirationUrl);
      expect(source).not.toMatch(/\b(?:copied verbatim|literal copy|copied literally)\b/i);
      expect(source).not.toContain("disable-model-invocation");
      expect(source).toContain("Use when");
      expect(source).toContain("Don't use for");
    }
  });

  it("IT-002 keeps planning separate from live execution", () => {
    const qaPlan = readRepositoryFile(qaPlanPath);
    const qaExecute = readRepositoryFile(qaExecutePath);

    expect(qaPlan).toContain("journeys, scenarios, and charters");
    expect(qaPlan).toContain("Leave live walks, evidence capture, defect remediation");
    expect(qaPlan).toContain("Maintain a criterion disposition for every changed acceptance criterion");
    expect(qaPlan).toContain("every changed acceptance criterion has one explicit disposition");
    expect(qaPlan).toContain("docs/qa/journeys/");
    expect(qaPlan).toContain("docs/qa/scenarios/");
    expect(qaPlan).toContain("docs/qa/charters/");
    expect(qaPlan).toContain("every changed criterion with its disposition");
    expect(qaPlan).toContain("End this skill before launching the product");
    expect(qaPlan).toContain("QA-SCENARIOS.md");
    expect(qaPlan).toContain("Done when:");
    expect(qaPlan).not.toContain("Create `docs/qa/reports/");

    expect(qaExecute).toContain("QA Plan handoff");
    expect(qaExecute).toContain("browser, API, CLI, mobile, or manual");
    expect(qaExecute).toContain("closest reachable public interface or a manual adapter");
    expect(qaExecute).toContain("Mark only an unreachable leg `untested`");
    expect(qaExecute).toContain("does not write product code, install a framework, invent a");
    expect(qaExecute).toContain("command, or replace the automated gate");
    expect(qaExecute).toContain("Report the exact adapter, path, evidence, and");
    expect(qaExecute).toContain("limitation. Keep raw evidence in the repository's disposable evidence");
    expect(qaExecute).toMatch(/and keep reports,\s+scenario\s+status, and bug records durable/);
    expect(qaExecute).toContain("fresh Verifier");
    expect(qaExecute).toContain("hand the defect to an Implementer");
    expect(qaExecute).toContain("close this Verifier session before remediation");
    expect(qaExecute).toContain("After a fix, start a fresh Verifier");
    expect(qaExecute).toContain("resume from the affected journey");
    expect(qaExecute).toContain("Done when:");
    expect(qaExecute).not.toContain("Create or update one charter");
    expect(qaExecute).not.toContain("Mint a stable, content-addressed scenario");
  });

  it("IT-008 keeps both descriptions within the authoring contract", () => {
    for (const relativePath of [qaPlanPath, qaExecutePath]) {
      const { name, description } = skillMetadata(relativePath);

      expect(name).toMatch(/^[a-z0-9]+(?:-[a-z0-9]+)*$/);
      expect(name.length).toBeLessThanOrEqual(64);
      expect(description.length).toBeLessThan(1024);
      expect(description).toMatch(/\bUse when\b/);
      expect(description).toMatch(/\bDon't use for\b/);
    }

    expect(() => parseSkillMetadata("name: qa-plan\ndescription: misplaced", "fixture")).toThrow(
      "Missing valid initial frontmatter",
    );
  });

  it("IT-003 dispatches all QA phases through each existing Verifier", () => {
    for (const relativePath of verifierPacketPaths) {
      const source = readRepositoryFile(relativePath);
      const normalized = normalizePacket(source);
      const routing = normalized.slice(normalized.indexOf("## Routing"), normalized.indexOf("## Result"));

      expect(normalized.match(/phase: exactly one of [^.]+\./)?.[0]).toBe(
        "phase: exactly one of technical, qa-plan, or qa-execute.",
      );
      expect(routing).toContain("Run exactly one phase per packet");
      expect(routing).toContain("For technical, check each AC against file:line assertions");
      expect(routing).toContain("For qa-plan, invoke the canonical qa-plan skill");
      expect(routing).toContain("For qa-execute, invoke the canonical qa-execute skill");
      expect(routing).not.toContain("For qa-plan, invoke the canonical qa-execute skill");
      expect(routing).not.toContain("For qa-execute, invoke the canonical qa-plan skill");
      expect(source).toContain("fresh Verifier session");
      expect(source).toContain("separate fresh Verifier");
      expect(source).toContain("purely internal refactor");
      expect(source).toMatch(/UI.*API.*CLI.*mobile.*adoption.*docs-as-interface/s);
      expect(source).not.toMatch(/separate QA reviewer/i);
    }

    const reviewRounds = readRepositoryFile("docs/guidelines/REVIEW-ROUNDS.md");

    expect(reviewRounds).toContain("The provider `verifier` executes exactly one phase per packet");
    expect(reviewRounds).toContain("Deep-review is a separate orchestrator stage, not a Verifier phase");
    expect(reviewRounds).not.toContain("The existing provider `verifier` performs all stages");
    expect(reviewRounds).not.toMatch(/provider `verifier`[^.]*deep-review/i);
    expect(readRepositoryFile("docs/workflow/reviews.md")).toContain(
      "Deep-review is a separate stage, not a Verifier phase.",
    );
  });

  it("IT-004 keeps QA scenario fields and statuses in one authoritative guideline", () => {
    const scenarioGuideline = readRepositoryFile("docs/guidelines/QA-SCENARIOS.md");
    const executionGuideline = readRepositoryFile("docs/guidelines/QA-EXECUTION.md");
    const reviewGuideline = readRepositoryFile("docs/guidelines/REVIEW-ROUNDS.md");

    expect(scenarioGuideline).toContain("Field rules");
    expect(scenarioGuideline).toContain("Status enums");
    expect(executionGuideline).toContain("QA-SCENARIOS.md");
    expect(executionGuideline).toContain("qa-plan");
    expect(executionGuideline).toContain("qa-execute");
    expect(executionGuideline).not.toMatch(/(?:^|\n)(?:id|qa_status|fix_status|retest_status):/);
    expect(executionGuideline).not.toContain("docs/qa/protocol.md");
    expect(executionGuideline).not.toContain("docs/qa/tours.md");
    expect(executionGuideline).not.toContain("docs/qa/edge-cases.md");
    expect(executionGuideline.split(/\r?\n/).length).toBeLessThanOrEqual(60);
    expect(reviewGuideline).toContain("QA-SCENARIOS.md");
    expect(reviewGuideline.trimEnd().split(/\r?\n/).length).toBeLessThanOrEqual(160);

    const approvedLoopRule =
      normalizePacket(reviewGuideline).match(/2\. \*\*Nitpicks never trigger a round\.\*.*?(?=3\. \*\*)/)?.[0] ?? "";
    for (const anchor of [
      "active, already-approved review loop",
      "fix blocking findings",
      "without new human approval",
      "through the applicable review cap",
      "scoped gate",
      "after each correction",
      "final deep-review round (round 2)",
      "corrected automatically in the same loop",
      "do not start round 3",
      "escalate only",
      "post-fix gate fails",
      "blocker remains reproducible",
      "remote actions retain separate approval requirements",
    ]) {
      expect(approvedLoopRule).toContain(anchor);
    }
    expect(approvedLoopRule.indexOf("without new human approval")).toBeLessThan(
      approvedLoopRule.indexOf("corrected automatically in the same loop"),
    );
    expect(approvedLoopRule.indexOf("scoped gate after each correction")).toBeLessThan(
      approvedLoopRule.indexOf("corrected automatically in the same loop"),
    );
    expect(approvedLoopRule.indexOf("corrected automatically in the same loop")).toBeLessThan(
      approvedLoopRule.indexOf("do not start round 3"),
    );
    expect(approvedLoopRule.indexOf("do not start round 3")).toBeLessThan(
      approvedLoopRule.indexOf("escalate only"),
    );
    expect(approvedLoopRule).not.toMatch(/ask(?: the human)? whether to fix/i);
    expect(readRepositoryFile(".agents/skills/deep-review/SKILL.md")).toContain(
      "FIX_BEFORE_SHIP` is actionable, not a prompt for approval",
    );

    for (const relativePath of verifierPacketPaths) {
      const packet = readRepositoryFile(relativePath);

      expect(packet).toContain("QA-SCENARIOS.md");
      expect(packet).not.toMatch(
        /(?:^|\n)\s*(?:id|area|title|persona|journey|expected|entry_points|qa_status|bug_ids|fix_status|retest_status|fix_commits|evidence|last_report|overlaps):/m,
      );
      expect(packet).not.toMatch(/(?:Field rules|Status enums|qa_status:\s*(?:untested|pass|fail))/i);
    }
  });

  it("IT-022 reconciles immutable QA charters, spec-anchored cases, and filed-issue QA", () => {
    const execution = readRepositoryFile("docs/guidelines/QA-EXECUTION.md");
    const qaPlan = readRepositoryFile(".agents/skills/qa-plan/SKILL.md");
    const testContract = readRepositoryFile("docs/guidelines/TEST-CONTRACT.md");
    const reviewRounds = readRepositoryFile("docs/guidelines/REVIEW-ROUNDS.md");

    for (const source of [execution, qaPlan]) {
      expect(source).toContain("new dated charter");
      expect(source).toMatch(/journeys? and\s+scenarios/i);
      expect(source).toMatch(/never (?:edit|update) an existing charter/i);
    }
    expect(execution).not.toContain("create or refresh durable journeys, scenarios, and charters");
    expect(qaPlan).not.toContain("Create or update one charter");

    expect(testContract).toContain("Every case maps to a spec acceptance criterion");
    expect(testContract).toContain("clarify the acceptance criterion before adding a case");
    expect(testContract).toContain("Never create a case solely because a");
    expect(testContract).not.toContain("Unit cases come from every component");
    expect(testContract).not.toContain("integration cases from every component boundary");

    const filedIssueRule = reviewRounds.slice(
      reviewRounds.indexOf("## Fixing a filed issue"),
      reviewRounds.indexOf("## Escalation"),
    );
    expect(filedIssueRule).toContain("If the fix changes user-visible behaviour");
    expect(filedIssueRule).toContain("flag its scenario");
    expect(filedIssueRule).toContain("walk it");
  });

  it("IT-013 records the selected QA adapter and checkout-local evidence", () => {
    const qaExecute = readRepositoryFile(".agents/skills/qa-execute/SKILL.md");

    expect(qaExecute).toContain("docs/qa/README.md");
    expect(qaExecute).toMatch(/Report the exact adapter, path, evidence, and\s+limitation/);
    expect(qaExecute).toMatch(/does not write product code, install a framework, invent a\s+command/);

    for (const relativePath of verifierPacketPaths) {
      const source = readRepositoryFile(relativePath);

      expect(source).toContain("docs/qa/README.md");
      expect(source).toContain("existing adapter");
      expect(source).toContain("exact path");
      expect(source).toContain("evidence");
      expect(source).toContain("limitation");
      expect(source).toMatch(/never install.*invent/s);
      expect(source).toContain("checkout-local");
    }
  });
});

describe("configurable review policy", () => {
  it("uses the canonical hierarchy and resolved deep-review groups", () => {
    const agents = readRepositoryFile("AGENTS.md");
    const reviewRounds = readRepositoryFile("docs/guidelines/REVIEW-ROUNDS.md");
    const reviews = readRepositoryFile("docs/workflow/reviews.md");
    const autonomous = readRepositoryFile(".agents/skills/autonomous/SKILL.md");
    const loop = readRepositoryFile("docs/workflow/loop.md");
    const tour = readRepositoryFile("docs/workflow/README.md");
    const readme = readRepositoryFile("README.md");

    expect(agents).toContain("Feature -> Vertical Slice -> Task");
    expect(agents).toContain(".agents/skills/workflow-config/SKILL.md");

    const reviewConfigPointer = ".agents/skills/workflow-config/SKILL.md";
    expect(reviewRounds).toContain(reviewConfigPointer);
    expect(reviewRounds.indexOf(reviewConfigPointer)).toBeLessThan(
      reviewRounds.indexOf("## The feature closing step"),
    );
    for (const repeatedCadenceText of [
      "`slice`, `feature`, or `grouped.N`",
      "absent config means",
      "four-slice feature",
      "3+1",
    ]) {
      expect(reviewRounds).not.toContain(repeatedCadenceText);
    }

    expect(reviews).toContain(reviewConfigPointer);
    expect(reviews.indexOf(reviewConfigPointer)).toBeLessThan(
      reviews.indexOf("## One Verifier role, several phases"),
    );
    expect(reviews).not.toContain("`slice`, `feature`, or balanced `grouped.N`");
    expect(reviews).not.toContain("absent config defaults to `grouped.3`");

    const autonomousPointer = ".agents/skills/workflow-config";
    expect(autonomous).toContain(autonomousPointer);
    expect(autonomous.indexOf(autonomousPointer)).toBeLessThan(
      autonomous.indexOf("Three rules an"),
    );

    const loopPointer = "Resolve cadence with `workflow-config` before dispatch.";
    expect(loop).toContain(loopPointer);
    expect(loop.indexOf(loopPointer)).toBeLessThan(loop.indexOf("## Stages"));

    const tourPointer = ".agents/skills/workflow-config/SKILL.md";
    expect(tour).toContain(tourPointer);
    expect(tour.indexOf(tourPointer)).toBeLessThan(tour.indexOf("A filed issue skips the ceremony"));
    expect(readme).toContain("The `cadence` controls the deep-review groups:");
    expect(readme).toContain("CLI override > profile > native provider");
    expect(readme).toContain(".specs/features/<feature>/workflow.json");
    expect(reviewRounds).toContain("deep-review** (resolved implementation groups)");
    expect(reviewRounds).not.toContain("deep-review** (every slice)");
    const finalGroupInstruction =
      "Before final QA, complete the final pending implementation deep-review group.";
    const qaHeading = "## The feature closing step";
    const remediationInstruction =
      "For QA code remediation, review only `reviewed_head..HEAD`, then re-walk affected scenario rows.";
    expect(reviewRounds).toContain(finalGroupInstruction);
    expect(reviewRounds.indexOf(finalGroupInstruction)).toBeLessThan(reviewRounds.indexOf(qaHeading));
    expect(reviewRounds).toContain(remediationInstruction);
    const deltaIndex = reviewRounds.indexOf("review only `reviewed_head..HEAD`");
    const rerunIndex = reviewRounds.indexOf("then re-walk affected scenario rows");
    expect(deltaIndex).toBeGreaterThan(-1);
    expect(deltaIndex).toBeLessThan(rerunIndex);
    expect(autonomous).toContain("every resolved");
    expect(loop).toContain("deep-review follows resolved");
    expect(tour).toContain("deep-review groups from workflow config");
  });

  it("bridges workflow resolution and feature-closing QA ordering", () => {
    const specDriven = readRepositoryFile(".agents/skills/tlc-spec-driven/SKILL.md");
    const qaScenarios = readRepositoryFile("docs/guidelines/QA-SCENARIOS.md");
    const gates = readRepositoryFile("docs/guidelines/GATES.md");
    const testContract = readRepositoryFile("docs/guidelines/TEST-CONTRACT.md");
    const normalizedTestContract = testContract.replace(/\s+/g, " ");
    const newFeatureBridge =
      "Before dispatching providers for a new feature, resolve `.agents/skills/workflow-config/SKILL.md`";
    const resumeBridge =
      "Before dispatching providers for a resumed feature, read its `workflow.json` snapshot";
    expect(specDriven).toContain(newFeatureBridge);
    expect(specDriven).toContain(resumeBridge);
    expect(specDriven.indexOf(newFeatureBridge)).toBeLessThan(specDriven.indexOf("1. Specify"));
    expect(specDriven.indexOf(resumeBridge)).toBeLessThan(
      specDriven.indexOf("1. Read `.specs/STATE.md`")
    );

    const closingQa =
      "The feature-closing QA session runs after the final implementation deep-review group";
    expect(qaScenarios).toContain(closingQa);
    expect(qaScenarios).not.toContain("The feature's last slice runs");
    expect(gates).toContain(
      "| Closing a task with a browser surface | The consuming project's browser scoped gate, filtered by `@feature:<slug>` |",
    );
    expect(normalizedTestContract).toContain(
      "The `@feature:<slug>` tag is the selector the consuming project's browser scoped gate uses",
    );
  });
});

describe("agent configuration", () => {
  it("IT-018 keeps the three harness matrices and dedicated Deep Review agents aligned", () => {
    const frontmatterValue = (source: string, key: string): string =>
      source.match(new RegExp(`^${key}:\\s*(.+)$`, "m"))?.[1]?.trim() ?? "";
    const tomlValue = (source: string, key: string): string =>
      source.match(new RegExp(`^${key}\\s*=\\s*"([^"]+)"$`, "m"))?.[1] ?? "";
    const value = (source: string, format: "frontmatter" | "toml", key: string): string =>
      format === "toml" ? tomlValue(source, key) : frontmatterValue(source, key);

    const matrix = [
      [".claude/agents/planner.md", "planner", "opus", "high", "frontmatter"],
      [".claude/agents/implementer.md", "implementer", "opus", "medium", "frontmatter"],
      [".claude/agents/verifier.md", "verifier", "opus", "medium", "frontmatter"],
      [".claude/agents/explorer.md", "explorer", "sonnet", "medium", "frontmatter"],
      [".cursor/agents/planner.md", "planner", "cursor-grok-4.6[effort=high]", "", "frontmatter"],
      [".cursor/agents/implementer.md", "implementer", "gpt-5.6-luna[effort=high]", "", "frontmatter"],
      [".cursor/agents/verifier.md", "verifier", "cursor-grok-4.6[effort=medium]", "", "frontmatter"],
      [".cursor/agents/explorer.md", "explorer", "gpt-5.6-luna[effort=medium]", "", "frontmatter"],
      [".codex/agents/planner.toml", "planner", "gpt-5.6-sol", "high", "toml"],
      [".codex/agents/implementer.toml", "implementer", "gpt-5.6-luna", "high", "toml"],
      [".codex/agents/verifier.toml", "verifier", "gpt-5.6-sol", "medium", "toml"],
      [".codex/agents/explorer.toml", "explorer", "gpt-5.6-luna", "medium", "toml"],
    ] as const;

    for (const [relativePath, expectedName, expectedModel, expectedEffort, format] of matrix) {
      const source = readRepositoryFile(relativePath);

      expect(value(source, format, "name")).toBe(expectedName);
      expect(value(source, format, "model")).toBe(expectedModel);
      if (format === "toml") {
        expect(value(source, format, "model_reasoning_effort")).toBe(expectedEffort);
      } else if (expectedEffort) {
        expect(value(source, format, "effort")).toBe(expectedEffort);
      }
    }

    const deepReviewers = [
      [".claude/agents/deep-reviewer.md", "sonnet", "high", "frontmatter"],
      [".cursor/agents/deep-reviewer.md", "gpt-5.6-luna[effort=high]", "", "frontmatter"],
      [".codex/agents/deep-reviewer.toml", "gpt-5.6-luna", "high", "toml"],
    ] as const;

    for (const [relativePath, expectedModel, expectedEffort, format] of deepReviewers) {
      const source = readRepositoryFile(relativePath);

      expect(value(source, format, "name")).toBe("deep-reviewer");
      expect(value(source, format, "model")).toBe(expectedModel);
      if (format === "toml") {
        expect(value(source, format, "model_reasoning_effort")).toBe(expectedEffort);
      } else if (expectedEffort) {
        expect(value(source, format, "effort")).toBe(expectedEffort);
      }
      expect(source).toContain("Do not edit source, tests, or configuration.");
      expect(source).toMatch(/one materialized Deep Review job/i);
      expect(source).toMatch(/one output artifact/i);
      expect(source).toMatch(/findings through .*schema/i);
    }

    expect(readRepositoryFile(".claude/agents/deep-reviewer.md")).toMatch(
      /^tools:\s*Read, Grep, Glob, Bash$/m,
    );
    const cursorDeepReviewer = readRepositoryFile(".cursor/agents/deep-reviewer.md");
    expect(cursorDeepReviewer).not.toMatch(/^readonly:\s*true$/m);

    const runtime = readRepositoryFile(".agents/skills/deep-review/references/subagent-runtimes.md");
    const orchestration = readRepositoryFile(".agents/skills/deep-review/references/orchestration.md");
    const deepReviewSkill = readRepositoryFile(".agents/skills/deep-review/SKILL.md");

    expect(deepReviewSkill).toMatch(
      /\| `--no-workflow` \|.*Named native `deep-reviewer` when the host supports it; role-free Workflow fallback/,
    );
    expect(deepReviewSkill).not.toContain("Workflow when available");
    expect(deepReviewSkill.indexOf("Named native `deep-reviewer`")).toBeLessThan(
      deepReviewSkill.indexOf("role-free Workflow fallback"),
    );
    expect(deepReviewSkill).toContain("Named native `deep-reviewer`");
    expect(orchestration).toContain("**Named native dispatch (default when host supports it).**");
    expect(orchestration).toContain("**Workflow fallback (when named native dispatch is unavailable).**");

    const codexRuntime = runtime.match(/^\|\s*`codex`\s*\|([^\n]+)$/m)?.[1] ?? "";
    expect(codexRuntime).toContain("gpt-5.6-luna");
    expect(codexRuntime).toContain("--reasoning-effort high");
    expect(codexRuntime).not.toContain("gpt-5.6-sol");
    expect(codexRuntime).not.toContain("xhigh");

    const native = orchestration.slice(
      orchestration.indexOf("**Named native dispatch"),
      orchestration.indexOf("**Workflow fallback"),
    );
    const workflow = orchestration.slice(
      orchestration.indexOf("**Workflow fallback"),
      orchestration.indexOf("**Agent fallback"),
    );
    const fallback = orchestration.slice(orchestration.indexOf("**Agent fallback"));

    expect(native).toMatch(/default when host supports it/i);
    expect(native).toContain('subagent_type: "deep-reviewer"');
    expect(native).toContain('subagentType: { custom: "deep-reviewer" }');
    expect(native).toMatch(/custom agent name\/type `deep-reviewer`/i);
    expect(workflow).toMatch(/fallback/i);
    expect(workflow).toMatch(/agent\(/);
    expect(workflow).toMatch(/role-free/i);
    expect(workflow).not.toMatch(/\(default\)/i);
    expect(fallback).toMatch(/named native selectors/i);
    expect(fallback).toMatch(/generic prompt-only subagent dispatch/i);
    expect(fallback).toMatch(/unsupported role\s+argument/i);
  });
});

describe("adoption and public setup", () => {
  it("IT-005 publishes provenance for TLC, Deep Review, and QA inspirations", () => {
    const readme = readRepositoryFile("README.md");

    expect(readme).toContain("Antonio Fulgêncio");
    expect(readme).toContain("Tech Leads Club");
    expect(readme).toContain(
      "https://github.com/tech-leads-club/agent-skills/tree/main/skills/tlc-spec-driven",
    );
    expect(readme).toContain("https://github.com/tech-leads-club/agent-skills/tree/main/skills");
    expect(readme).toContain("Pedro Nauck");
    expect(readme).toContain("https://github.com/pedronauck/skills/tree/main/skills/mine/deep-review");
    expect(readme).toContain("https://github.com/pedronauck/skills/tree/main/skills/mine/qa-report");
    expect(readme).toContain("https://github.com/pedronauck/skills/tree/main/skills/mine/qa-execution");
  });

  it("IT-006 keeps the public README product-neutral", () => {
    const readme = readRepositoryFile("README.md");

    expect(readme).toContain("stack-agnostic");
    expect(readme).not.toMatch(/Creatista|antclips|hono|drizzle|tanstack|shadcn|better-auth|graphile/);
  });

  it("IT-010 makes adoption reviewable and routes QA by observability", () => {
    const readme = readRepositoryFile("README.md");
    const adopt = readRepositoryFile("scripts/adopt.py");

    expect(readme).toContain("git status --short");
    expect(readme).toContain("read-only");
    expect(readme).toContain("package and build");
    expect(readme).toContain("manifests");
    expect(readme).toContain("CI jobs");
    expect(readme).toContain("managed paths");
    expect(readme).toContain("complete diff");
    expect(readme).toContain("declared full gate");
    expect(readme).toContain("If `docs/qa/README.md` is absent, create it");
    expect(readme).toContain("If it exists, merge only newly discovered facts");
    expect(readme).toContain("never overwrite existing content");
    expect(readme).toContain("qa-plan");
    expect(readme).toContain("qa-execute");
    expect(readme).toContain("purely internal refactor");
    expect(readme).toContain("no user-visible change");
    expect(adopt).toContain('".agents/skills/qa-plan"');
    expect(adopt).toContain('".agents/skills/qa-execute"');
    expect(adopt).toContain(
      'COPY_MISSING_PATHS = ["docs/qa/README.md", "tools/ad-index.py"]',
    );
  });

  it("IT-019 keeps README installation prerequisites and bundled skills authoritative", () => {
    const readme = readRepositoryFile("README.md");

    expect(readme).toContain("the target directory must already exist");
    expect(readme).toContain("`adopt.py` requires Python 3");
    expect(readme).toMatch(/Adoption\s+does not require a Git `HEAD`/);
    expect(readme).toMatch(/the target must be a Git\s+repository with at least one commit/);
    expect(readme).toMatch(/Node\.js and npm are needed only to validate this source pack's\s+gates/);
    expect(readme).toMatch(
      /`adopt\.py` installs and updates only the bundled TLC, Ponytail, Deep Review, QA, workflow-config,\s+and autonomous skills/,
    );
    expect(readme).toContain("The three external security skills are a separate authorized step");
    expect(readme).toContain("install_security_skills.py");
    expect(readme).not.toContain("@tech-leads-club/agent-skills install");
    expect(readme).not.toContain("skills add dietrichgebert/ponytail");
    expect(readme).not.toContain("Delete any .cursor/skills");
    expect(readme).not.toContain("extra .codex/.opencode copies");
  });

  it("IT-021 keeps Ponytail active from workflow start through the full cycle", () => {
    const agents = readRepositoryFile("AGENTS.md");
    const loop = readRepositoryFile("docs/workflow/loop.md");
    const readme = readRepositoryFile("README.md");
    const ponytail = readRepositoryFile(".agents/skills/ponytail/SKILL.md");

    expect(agents).toContain(
      "At the start of workflow work, activate `ponytail`\nat `full` and keep it active for the entire session",
    );
    expect(agents).toContain(
      "Specify, Design, Tasks, Execute, every\nsubagent prompt, fix, and review",
    );
    expect(agents).toContain("until the human explicitly says `stop ponytail` or `normal mode`");
    expect(loop).toContain("`AGENTS.md` carries the activation and session\npersistence rule");
    expect(loop).toContain("[Ponytail skill](../../.agents/skills/ponytail/SKILL.md)");
    expect(readme).toContain(
      "At the start of\nworkflow work, activate `ponytail` at `full`; `AGENTS.md` carries the full-cycle",
    );
    expect(ponytail).toContain("ACTIVE EVERY RESPONSE");
  });

  it("IT-020 keeps the pack guide source-only for adopted consumers", () => {
    const tour = readRepositoryFile("docs/workflow/README.md");
    const pack = readRepositoryFile("docs/workflow/pack.md");

    expect(tour).toContain("[Skills, knowledge, adopt](pack.md)");
    expect(pack).toContain("`python3 scripts/adopt.py <target>`");
  });

  it("IT-011 keeps stack-specific QA capabilities in the operational profile", () => {
    const profile = readRepositoryFile("docs/qa/README.md");

    for (const heading of [
      "## Public interfaces and area codes",
      "## Runner and adapter",
      "## Build, start, and health",
      "## Authentication and test data",
      "## Evidence and limitations",
    ]) {
      expect(profile).toContain(heading);
    }
    expect(profile).toContain("manifests or CI");
    expect(profile.toLowerCase()).toContain("fixtures or seed");
    expect(profile.toLowerCase()).toContain("cleanup");
    expect(profile.toLowerCase()).toContain("residue");
    expect(profile.toLowerCase()).toContain("raw evidence");
    expect(profile).toContain("does not install a framework or invent commands");
  });

  it("IT-012 leaves adapter choice with the consuming project", () => {
    const profile = readRepositoryFile("docs/qa/README.md");
    const qaExecute = readRepositoryFile(".agents/skills/qa-execute/SKILL.md");

    for (const adapter of ["browser", "API", "CLI", "mobile", "manual"]) {
      expect(profile.toLowerCase()).toContain(adapter.toLowerCase());
      expect(qaExecute.toLowerCase()).toContain(adapter.toLowerCase());
    }
    expect(qaExecute).toContain("existing browser, API, CLI, mobile, or manual adapter");
    expect(qaExecute).toContain("does not write product code, install a framework, invent a");
  });

  it("IT-017 reports release version 0.3.5 consistently", () => {
    const manifest = JSON.parse(readRepositoryFile("package.json")) as { version?: string };
    const lockfile = JSON.parse(readRepositoryFile("package-lock.json")) as {
      version?: string;
      packages?: { ""?: { version?: string } };
    };

    expect(manifest.version).toBe("0.3.5");
    expect(lockfile.version).toBe("0.3.5");
    expect(lockfile.packages?.[""]?.version).toBe("0.3.5");
  });
});
