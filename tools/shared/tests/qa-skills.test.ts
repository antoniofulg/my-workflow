import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "bun:test";

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

function trackedFiles(): string[] {
  return execFileSync("git", ["ls-files", "-z"], {
    cwd: repositoryRoot,
    encoding: "utf8",
  }).split("\0").filter((relativePath) =>
    relativePath && existsSync(join(repositoryRoot, relativePath)) && statSync(join(repositoryRoot, relativePath)).isFile(),
  );
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
  "templates/agents/cursor/verifier.md",
  "templates/agents/claude/verifier.md",
  "templates/agents/codex/verifier.toml",
] as const;

const deepReviewerPacketPaths = [
  "templates/agents/cursor/deep-reviewer.md",
  "templates/agents/claude/deep-reviewer.md",
  "templates/agents/codex/deep-reviewer.toml",
] as const;

describe("host-owned session continuation removal contract", () => {
  it("HSC-01/HSC-04 removes every repository and package artifact", () => {
    const integrationName = ["ai", "memory"].join("-");
    const integrationModule = ["ai", "memory"].join("_");
    const removedPaths = [
      `scripts/${integrationName}.zsh`,
      `scripts/test_${integrationModule}.py`,
      `docs/workflow/${integrationName}.md`,
      `docs/qa/scenarios/WFL-${integrationName}-handoff.md`,
      `.specs/features/${integrationName}-handoff/`,
    ];

    for (const relativePath of removedPaths) {
      expect(existsSync(join(repositoryRoot, relativePath))).toBe(false);
    }

    const packagePaths = execFileSync(
      "rg",
      ["--files", "--hidden", "--glob", "!.git/**", "--glob", "!node_modules/**"],
      { cwd: repositoryRoot, encoding: "utf8" },
    ).trim().split(/\r?\n/);

    expect(
      packagePaths.filter((packagePath) =>
        removedPaths.some(
          (removedPath) =>
            packagePath === removedPath ||
            (removedPath.endsWith("/") && packagePath.startsWith(removedPath)),
        ),
      ),
    ).toEqual([]);
  });

  it("HSC-05/HSC-07/HSC-08 publishes host ownership and fresh reviewer packets", () => {
    const readme = readRepositoryFile("README.md");
    const workflowIndex = readRepositoryFile("docs/workflow/README.md");
    const reviewGuideline = readRepositoryFile("docs/guidelines/REVIEW-ROUNDS.md");
    const reviewerPackets = [...verifierPacketPaths, ...deepReviewerPacketPaths].map((relativePath) =>
      readRepositoryFile(relativePath),
    );
    const hostRule =
      "Cross-provider session continuation is owned by the host. Repository files, Git state, feature artifacts, and explicit handoff prompts remain the durable semantic context.";

    expect(readme.replace(/\s+/g, " ")).toContain(hostRule);
    expect(workflowIndex.replace(/\s+/g, " ")).toContain(hostRule);
    expect(reviewGuideline.replace(/\s+/g, " ")).toContain(
      "Verifier and Deep Reviewer receive fresh role packets. They do not inherit the Implementer's transcript or operator handoff. Their conclusions must come from the spec, diff, tests, and assigned evidence.",
    );
    for (const packet of reviewerPackets) {
      const normalized = normalizePacket(packet);
      expect(normalized).toContain("fresh role packet, exclude author and operator context");
      expect(normalized).toContain("Implementer's transcript");
      expect(normalized).toContain("operator handoff");
      for (const evidenceSource of ["spec", "diff", "tests", "assigned evidence"]) {
        expect(normalized.toLowerCase()).toContain(evidenceSource);
      }
    }

    const removedIntegration = ["ai", "memory"].join("-");
    const removedIntegrationModule = ["ai", "memory"].join("_");
    const removedPhrases = [
      removedIntegration,
      removedIntegrationModule,
      ["memory", "handoff"].join(" "),
      ["cross-provider", "handoff"].join(" "),
      ["install", "hooks"].join("-"),
      ["finalize", "session"].join("-"),
    ];
    for (const source of [readme, workflowIndex, reviewGuideline, ...reviewerPackets]) {
      expect(removedPhrases.some((phrase) => source.toLowerCase().includes(phrase))).toBe(false);
      expect(source).not.toMatch(/\bOrca\b/);
    }
  });

  it("CT-001/CT-004 scans references with an explicit historical allowlist", () => {
    const integrationName = ["ai", "memory"].join("-");
    const integrationModule = ["ai", "memory"].join("_");
    const spacedIntegration = ["ai", "memory"].join(" ");
    const referenceTerms = [
      integrationName,
      integrationModule,
      spacedIntegration,
      ["memory", "handoff"].join(" "),
      ["cross-provider", "handoff"].join(" "),
      ["install", "hooks"].join("-"),
      ["finalize", "session"].join("-"),
      ["session", "memory"].join(" "),
      ["session", "memory"].join("-"),
      ["handoff", "payload"].join(" "),
      ...[
        "install",
        "enable",
        "source",
        "disable",
        "re-enable",
        "purge",
        "isolate",
        "detect",
        "test",
        "use",
      ].flatMap((verb) => [`${verb} ${integrationName}`, `${verb} ${integrationModule}`]),
    ];
    const historicalMemoryCharter = [
      "docs/qa/charters/CH",
      integrationName,
      "handoff-2026-08-24.md",
    ].join("-");
    const historicalMemoryReport = [
      "docs/qa/reports/2026-08-24",
      "-",
      integrationName,
      "-handoff.md",
    ].join("");
    const allowlist = new Map<string, string>([
      ["CHANGELOG.md", "historical changelog"],
      [".specs/features/agent-model-routing/validation.md", "immutable historical QA/release-certification evidence"],
      [".specs/features/parallel-slice-dispatch/validation.md", "immutable historical QA/release-certification evidence"],
      [".specs/features/release-0.4.0/validation.md", "immutable historical QA/release-certification evidence"],
      [historicalMemoryCharter, "immutable historical QA/release-certification evidence"],
      [historicalMemoryReport, "immutable historical QA/release-certification evidence"],
      ["docs/qa/bugs/BUG-20260824-noninteractive-codex-finalizes-open-session.md", "immutable historical QA/release-certification evidence"],
      ["docs/qa/bugs/BUG-20260824-release-overstates-lifecycle-qa.md", "immutable historical QA/release-certification evidence"],
      ["docs/qa/charters/CH-agent-model-routing-adoption-boundary-2026-08-24.md", "immutable historical QA/release-certification evidence"],
      ["docs/qa/charters/CH-review-release-0-4-0-2026-08-24.md", "immutable historical QA/release-certification evidence"],
      ["docs/qa/charters/CH-review-release-0-5-0-2026-08-25.md", "immutable historical QA/release-certification evidence"],
      ["docs/qa/reports/2026-08-24-agent-model-routing-local-state.md", "immutable historical QA/release-certification evidence"],
      ["docs/qa/reports/2026-08-24-agent-model-routing.md", "immutable historical QA/release-certification evidence"],
      ["docs/qa/reports/2026-08-24-release-0-4-0.md", "immutable historical QA/release-certification evidence"],
      ["docs/qa/reports/2026-08-25-release-0-5-0.md", "immutable historical QA/release-certification evidence"],
      [".specs/features/host-owned-session-continuation/design.md", "v0.6 removal-note artifact"],
      [".specs/features/host-owned-session-continuation/spec.md", "v0.6 removal-note artifact"],
      [".specs/features/host-owned-session-continuation/tasks.md", "v0.6 removal-note artifact"],
      [".specs/features/host-owned-session-continuation/validation.md", "v0.6 removal-note artifact"],
    ]);
    const matches = trackedFiles().flatMap((relativePath) => {
      const source = readRepositoryFile(relativePath);
      return referenceTerms
        .filter((term) => source.toLowerCase().includes(term.toLowerCase()))
        .map((term) => ({ relativePath, term, classification: allowlist.get(relativePath) }));
    });
    const unexpected = matches.filter((match) => !match.classification);

    expect(
      unexpected,
      `non-allowlisted references (all matches and classifications):\n${JSON.stringify(matches, null, 2)}`,
    ).toEqual([]);
    expect(
      matches.every((match) => match.classification),
      `every reference must be classified:\n${JSON.stringify(matches, null, 2)}`,
    ).toBe(true);
  }, 30_000);

  it("HSC-09 keeps changed QA scenarios fresh until v0.6 evidence exists", () => {
    const changedScenarios = [
      "docs/qa/scenarios/ADP-adopt-workflow-safely.md",
      "docs/qa/scenarios/REL-report-current-workflow-release.md",
    ];
    const freshEvidence = /v?0[._-]6[._-]0/i;

    for (const relativePath of changedScenarios) {
      const source = readRepositoryFile(relativePath);
      const status = source.match(/^qa_status:\s*(\S+)$/m)?.[1];

      expect(status, `${relativePath} must declare qa_status`).toBeDefined();
      if (status === "pass") {
        const evidence = source.match(/^evidence:\s*(.+)$/m)?.[1] ?? "";
        const report = source.match(/^last_report:\s*(.+)$/m)?.[1] ?? "";
        expect(evidence, `${relativePath} pass requires evidence`).toMatch(freshEvidence);
        expect(report, `${relativePath} pass requires a v0.6 report`).toMatch(freshEvidence);
      } else {
        expect(["untested", "fail", "blocked-verify", "blocked-decision", "skipped"]).toContain(status);
      }
    }
  });
});

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
      readRepositoryFile("templates/agents/cursor/implementer.md"),
      readRepositoryFile("templates/agents/claude/implementer.md"),
      readRepositoryFile("templates/agents/codex/implementer.toml"),
    ];
    const plannerPackets = [
      readRepositoryFile("templates/agents/cursor/planner.md"),
      readRepositoryFile("templates/agents/claude/planner.md"),
      readRepositoryFile("templates/agents/codex/planner.toml"),
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

    const reviewRounds = readRepositoryFile("docs/guidelines/REVIEW-ROUNDS.md");
    expect(reviewRounds).toContain("fingerprint = requirement + root cause + failure path");
    expect(reviewRounds).toContain("independent failed-remediation counter for each fingerprint");
    expect(reviewRounds).toContain("third failed remediation of the same fingerprint");
    expect(reviewRounds).toContain("every failed post-fix Verifier result, whether or not the build gate is green");
    expect(reviewRounds).toContain("Rewording or reopening a finding preserves its fingerprint and counter");
    expect(reviewRounds).toContain("A distinct blocker starts at count zero and does not consume another fingerprint's counter");
    expect(reviewRounds).not.toMatch(/one global (?:remediation|blocker) counter/i);

    for (const relativePath of [
      ".agents/skills/tlc-spec-driven/SKILL.md",
      ".agents/skills/tlc-spec-driven/references/validate.md",
      ".agents/skills/tlc-spec-driven/references/sub-agents.md",
      ".agents/skills/tlc-spec-driven/references/implement.md",
      ".agents/skills/autonomous/SKILL.md",
      "docs/workflow/reviews.md",
      "docs/workflow/README.md",
      "docs/workflow/purpose.md",
    ]) {
      const source = readRepositoryFile(relativePath);
      expect(source).toContain("REVIEW-ROUNDS.md");
      expect(source).toContain("fingerprint");
    }
    expect(readRepositoryFile(".agents/skills/tlc-spec-driven/references/validate.md")).toContain(
      "diagnostic cap is per issue and separate from review-remediation fingerprint accounting",
    );
    const convergence = readRepositoryFile(".agents/skills/tlc-spec-driven/scripts/review_convergence.py");
    expect(convergence).toContain("failed_remediations");
    expect(convergence).toContain("os.replace");
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
    const workflowConfig = readRepositoryFile(".agents/skills/workflow-config/SKILL.md");
    const autonomous = readRepositoryFile(".agents/skills/autonomous/SKILL.md");

    expect(reviewRounds).toContain("The provider `verifier` executes exactly one phase per packet");
    expect(reviewRounds).toContain("Deep-review is a separate orchestrator stage, not a Verifier phase");
    expect(reviewRounds).not.toContain("The existing provider `verifier` performs all stages");
    expect(reviewRounds).not.toMatch(/provider `verifier`[^.]*deep-review/i);
    expect(readRepositoryFile("docs/workflow/reviews.md")).toContain(
      "Deep-review is a separate stage, not a Verifier phase.",
    );
    expect(workflowConfig).toContain("[remediation]` table");
    const remediation = reviewRounds.slice(
      reviewRounds.indexOf("When a cap is reached"),
      reviewRounds.indexOf("## Requirement and contract parity"),
    );
    expect(remediation).toContain("run its scoped gate after every attempt");
    expect(remediation).toContain(
      "stable signature from sorted failing-test identifiers after removing timings, absolute paths, and line numbers",
    );
    expect(remediation).toContain(
      "current failing-test set that is a strict subset of the running minimum failing-test set resets the counter",
    );
    expect(remediation).toContain("equal-size set, including one with different members");
    expect(remediation).toContain("a larger set increments it");
    expect(remediation).toContain("`stall_attempts = 0` is unbounded");
    expect(remediation).toContain(
      "when a nonzero threshold is reached, halt with the repeated signature, attempt count, and fixes tried",
    );
    expect(remediation).toContain(
      "If the gate is unavailable, halt immediately without another deep-review round",
    );
    expect(remediation).toContain("never starts round 3");
    expect(remediation.indexOf("run its scoped gate after every attempt")).toBeLessThan(
      remediation.indexOf("stable signature from sorted failing-test identifiers"),
    );
    expect(remediation.indexOf("stable signature from sorted failing-test identifiers")).toBeLessThan(
      remediation.indexOf("strict subset of the running minimum"),
    );
    expect(remediation.indexOf("strict subset of the running minimum")).toBeLessThan(
      remediation.indexOf("when a nonzero threshold is reached"),
    );
    expect(remediation.indexOf("a larger set increments it")).toBeGreaterThan(
      remediation.indexOf("strict subset of the running minimum"),
    );
    const autonomousHalt = normalizePacket(
      autonomous.slice(autonomous.indexOf("## Halt conditions")),
    );
    expect(autonomousHalt).toContain(
      "The post-cap scoped gate is unavailable, or the configured remediation stall threshold is reached under docs/guidelines/REVIEW-ROUNDS.md; an open blocker alone does not halt while attempts are establishing new failure-set minima",
    );
    expect(autonomousHalt).not.toContain("leaves a blocker open");
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
      "configured stall threshold is reached",
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

describe("optional integration policy", () => {
  it("IT-023 keeps optional tools stack-agnostic, repository-authoritative, and non-destructive", () => {
    const readme = readRepositoryFile("README.md");
    const uiux = readRepositoryFile("docs/guidelines/UI-UX.md");
    const security = readRepositoryFile("docs/guidelines/SECURITY.md");
    const state = readRepositoryFile(".specs/STATE.md");
    const normalizedUiux = uiux.replace(/\s+/g, " ");
    const normalizedSecurity = security.replace(/\s+/g, " ");

    expect(readme).toContain("The workflow stays stack- and tool-agnostic");
    expect(readme).toContain("Graft");
    expect(readme).toContain("OpenDesign");
    expect(readme).toContain("No integration is mandatory or installed by adoption");
    expect(normalizedUiux).toContain("repository stores only the approved handoff");
    expect(normalizedUiux).toContain("`spec.md` → `uiux.md` → approved design");
    expect(normalizedUiux).toContain("tool or plugin output, then legacy mockup");
    expect(normalizedUiux).toContain("tool absence or failure falls back to the normal repository artifacts");
    expect(normalizedSecurity).toContain("isolated environment or with explicitly allowed directories");
    expect(normalizedSecurity).toContain("Validate destination paths and symlinks before the first write");
    expect(normalizedSecurity).toContain("never delete them automatically");
    expect(state).toContain("### AD-006");
    expect(state).toContain("stack- and tool-agnostic");
    expect(state).toContain("Graft");
    expect(state).toContain("OpenDesign");
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

    const config = readRepositoryFile(".my-workflow.toml.example");
    const settings = new Map<string, { model: string; effort: string }>();
    const section = /\[models\.(claude|codex|cursor)\.(planner|implementer|verifier|explorer|deep_reviewer)\]\s+model = "([^"]+)"\s+effort = "([^"]+)"/g;
    for (const match of config.matchAll(section)) {
      settings.set(`${match[1]}.${match[2]}`, { model: match[3], effort: match[4] });
    }
    expect(settings.size).toBe(15);

    for (const provider of ["claude", "codex", "cursor"] as const) {
      for (const role of ["planner", "implementer", "verifier", "explorer", "deep_reviewer"] as const) {
        const agentName = role === "deep_reviewer" ? "deep-reviewer" : role;
        const extension = provider === "codex" ? "toml" : "md";
        const format = provider === "codex" ? "toml" : "frontmatter";
        const relativePath = `templates/agents/${provider}/${agentName}.${extension}`;
        const source = readRepositoryFile(relativePath);
        const expected = settings.get(`${provider}.${role}`)!;
        expect(value(source, format, "name")).toBe(agentName);
        if (provider === "cursor") {
          expect(value(source, format, "model")).toBe(`${expected.model}[effort=${expected.effort}]`);
        } else {
          expect(value(source, format, "model")).toBe(expected.model);
          const effortKey = provider === "codex" ? "model_reasoning_effort" : "effort";
          expect(value(source, format, effortKey)).toBe(expected.effort);
        }
        if (role === "deep_reviewer") {
          expect(source).toContain("Do not edit source, tests, or configuration.");
          expect(source).toMatch(/one materialized Deep Review job/i);
          expect(source).toMatch(/one output artifact/i);
          expect(source).toMatch(/findings through .*schema/i);
        }
      }
    }

    expect(readRepositoryFile("templates/agents/claude/deep-reviewer.md")).toMatch(
      /^tools:\s*Read, Grep, Glob, Bash$/m,
    );
    const cursorDeepReviewer = readRepositoryFile("templates/agents/cursor/deep-reviewer.md");
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
    const prompt = readRepositoryFile("docs/adoption-prompt.md");
    const adopt = readRepositoryFile("scripts/adopt.py");

    expect(readme).toContain("docs/adoption-prompt.md");
    expect(readme).toContain("managed paths");
    expect(prompt).toContain("git status --short");
    expect(prompt).toContain("read-only");
    expect(prompt).toContain("package and build");
    expect(prompt).toContain("manifests");
    expect(prompt).toContain("CI jobs");
    expect(prompt).toContain("managed paths");
    expect(prompt).toContain("complete diff");
    expect(prompt).toContain("declared full gate");
    expect(prompt).toContain("If `docs/qa/README.md` is absent, create it");
    expect(prompt).toContain("If it exists, merge only newly discovered facts");
    expect(prompt).toContain("never overwrite existing content");
    expect(prompt).toContain("qa-plan");
    expect(prompt).toContain("qa-execute");
    expect(prompt).toContain("purely internal refactor");
    expect(prompt).toContain("no user-visible change");
    expect(adopt).toContain('".agents/skills/qa-plan"');
    expect(adopt).toContain('".agents/skills/qa-execute"');
    expect(adopt).toContain('".my-workflow.toml.example"');
    expect(adopt).toContain('"templates/agents"');
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
    const prompt = readRepositoryFile("docs/adoption-prompt.md");
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
    expect(prompt).toContain(
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

  it("CT-003 / BTR-IT-007 / BTR-IT-008 reports release history and pending version consistently", () => {
    const manifest = JSON.parse(readRepositoryFile("package.json")) as {
      version?: string;
      scripts?: { test?: string };
    };
    const lockfile = JSON.parse(readRepositoryFile("package-lock.json")) as {
      version?: string;
      packages?: { ""?: { version?: string } };
    };
    const changelog = readRepositoryFile("CHANGELOG.md");
    const releaseScenario = readRepositoryFile("docs/qa/scenarios/REL-report-current-workflow-release.md");
    const integrationName = ["ai", "memory"].join("-");
    const publishedHeading = changelog.match(/^## \[(\d+\.\d+\.\d+)\]/m)?.[1];
    const unreleasedStart = changelog.indexOf("## [0.7.0] - Unreleased");
    const releaseStart = changelog.indexOf(`## [${manifest.version}]`);
    const nextRelease = changelog.indexOf("\n## [", releaseStart + 1);
    const latestRelease = changelog.slice(releaseStart, nextRelease === -1 ? undefined : nextRelease);
    const pendingRelease = changelog.slice(unreleasedStart, releaseStart);
    const publishedChangelog = execFileSync("git", ["show", "v0.6.0:CHANGELOG.md"], {
      cwd: repositoryRoot,
      encoding: "utf8",
    });
    const section = (source: string, version: string): string => {
      const start = source.indexOf(`## [${version}]`);
      const next = source.indexOf("\n## [", start + 1);
      return source.slice(start, next === -1 ? undefined : next);
    };

    expect(manifest.version).toBe("0.6.0");
    expect(manifest.scripts?.test).toBe("bun test");
    expect(lockfile.version).toBe("0.6.0");
    expect(lockfile.packages?.[""]?.version).toBe("0.6.0");
    expect(publishedHeading).toBe("0.7.0");
    expect(unreleasedStart).toBeGreaterThanOrEqual(0);
    expect(releaseStart).toBeGreaterThan(unreleasedStart);
    expect(section(changelog, "0.6.0")).toBe(section(publishedChangelog, "0.6.0"));
    expect(releaseScenario).toContain("expected: Unreleased v0.7.0 notes identify Bun 1.4 structural tests rooted at tools");
    expect(pendingRelease).toContain("Bun 1.4");
    expect(pendingRelease).toContain(`Removed the optional ${integrationName} integration`);
    expect(pendingRelease).toContain("Session continuation is now a host responsibility");
    expect(pendingRelease).toContain("versioned repository artifacts and explicit prompts");
    expect(pendingRelease).toContain("adoption never removes external operator state");
    expect(pendingRelease).toContain("v0.5.0 tagged guide");
    expect(pendingRelease).toContain(`https://github.com/antoniofulg/my-workflow/blob/v0.5.0/docs/workflow/${integrationName}.md`);
    expect(latestRelease).not.toContain(`Removed the optional ${integrationName} integration`);
    expect(latestRelease).toContain("opt-in parallel slice executor");
    expect(latestRelease).toContain("resource preflight");
    expect(latestRelease).toContain("BLOCKED-VERIFY");
  });

  it("BTR-IT-003 keeps active runner contracts on Bun", () => {
    const retiredRunner = ["vit", "est"].join("");
    const currentContracts = [
      "README.md",
      "docs/workflow/README.md",
      "docs/workflow/decisions.md",
      "docs/workflow/guidelines.md",
      "docs/workflow/loop.md",
      "docs/workflow/pack.md",
      "docs/workflow/purpose.md",
      "docs/workflow/reviews.md",
      "docs/qa/README.md",
      "docs/qa/journeys/J-adopt-workflow.md",
      "docs/qa/journeys/J-configure-feature-workflow.md",
      "docs/qa/journeys/J-enable-external-security-skills.md",
      "docs/qa/journeys/J-execute-parallel-slices.md",
      "docs/qa/journeys/J-review-workflow-release.md",
      "docs/qa/journeys/J-run-deep-review.md",
      "docs/qa/scenarios/REL-report-current-workflow-release.md",
      "package.json",
      "package-lock.json",
      "tsconfig.json",
      "bunfig.toml",
    ];
    const matches = currentContracts.flatMap((relativePath) => {
      const source = readRepositoryFile(relativePath);
      return source.toLowerCase().includes(retiredRunner) ? [relativePath] : [];
    });

    expect(matches, `retired runner wording in active contracts: ${matches.join(", ")}`).toEqual([]);
  });

  it("CT-004 preserves v0.5.0 historical evidence and the v0.4.0 changelog section", () => {
    const historicalEvidencePaths = execFileSync(
      "git",
      [
        "ls-tree",
        "-r",
        "--name-only",
        "v0.5.0",
        "--",
        "docs/qa/reports",
        "docs/qa/charters",
        "docs/qa/bugs",
      ],
      { cwd: repositoryRoot, encoding: "utf8" },
    )
      .trim()
      .split(/\r?\n/)
      .filter(Boolean);
    const releaseValidationPaths = [
      ".specs/features/agent-model-routing/validation.md",
      ".specs/features/release-0.4.0/validation.md",
    ].filter((relativePath) => {
      try {
        execFileSync("git", ["cat-file", "-e", `v0.5.0:${relativePath}`], {
          cwd: repositoryRoot,
          stdio: "ignore",
        });
        return true;
      } catch {
        return false;
      }
    });
    const protectedHistoricalPaths = [...historicalEvidencePaths, ...releaseValidationPaths];

    expect(protectedHistoricalPaths.length).toBeGreaterThan(0);
    for (const relativePath of protectedHistoricalPaths) {
      const tagged = execFileSync("git", ["show", `v0.5.0:${relativePath}`], {
        cwd: repositoryRoot,
        encoding: "buffer",
      });
      expect(existsSync(join(repositoryRoot, relativePath))).toBe(true);
      expect(readFileSync(join(repositoryRoot, relativePath)).equals(tagged), relativePath).toBe(true);
    }

    const historicalChangelog = execFileSync("git", ["show", "v0.5.0:CHANGELOG.md"], {
      cwd: repositoryRoot,
      encoding: "utf8",
    });
    const section = (source: string, version: string): string => {
      const start = source.indexOf(`## [${version}]`);
      const next = source.indexOf("\n## [", start + 1);
      return source.slice(start, next === -1 ? undefined : next);
    };
    expect(section(readRepositoryFile("CHANGELOG.md"), "0.4.0")).toBe(
      section(historicalChangelog, "0.4.0"),
    );
  }, 30_000);
});
