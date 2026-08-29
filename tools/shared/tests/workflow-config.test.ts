import { cpSync, existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { describe, expect, it } from "bun:test";

const repositoryRoot = process.cwd();
const skillPath = ".agents/skills/workflow-config/SKILL.md";
const roles = ["implementer", "verifier", "explorer", "deep-reviewer"] as const;
const resolverRoles = ["implementer", "verifier", "explorer", "deep_reviewer"] as const;
const providers = ["claude", "cursor", "codex"] as const;

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

function packagedFiles(): string[] {
  const destination = mkdtempSync(join(tmpdir(), "workflow-package-"));
  const tarball = join(destination, "workflow.tgz");
  try {
    execFileSync("bun", ["pm", "pack", "--filename", tarball, "--ignore-scripts"], {
      cwd: repositoryRoot,
      encoding: "utf8",
    });
    return execFileSync("tar", ["-tzf", tarball], { encoding: "utf8" })
      .trim()
      .split("\n")
      .filter(Boolean)
      .map((path) => path.replace(/^package\//, ""));
  } finally {
    rmSync(destination, { recursive: true, force: true });
  }
}

describe("workflow configuration skill", () => {
  it("defines resolution, resume, refresh, and explicit provider failure", () => {
    const skill = readRepositoryFile(skillPath);

    expect(skill).toMatch(/^---\nname: workflow-config\ndescription: .+\n---/);
    expect(skill).toContain("python3 .agents/skills/workflow-config/scripts/workflow_config.py");
    expect(skill).toContain("--refresh");
    expect(skill).toContain("Read the existing feature snapshot before dispatch");
    expect(skill).toMatch(/Halt with the\s+provider and role named/);
    expect(skill).toContain("without merging definitions or silently");
    expect(skill).not.toContain("deep-review after every slice");
  });

  it("identifies a complete agent definition for every supported role and provider", () => {
    for (const provider of providers) {
      for (const role of roles) {
        const extension = provider === "codex" ? "toml" : "md";
        const path = `templates/agents/${provider}/${role}.${extension}`;
        expect(existsSync(join(repositoryRoot, path)), path).toBe(true);
        expect(readRepositoryFile(path).trim(), path).not.toBe("");
      }
    }
  });

  it("keeps local config/runtimes ignored and packages only example/templates", () => {
    expect(execFileSync("git", ["ls-files", "--", ".my-workflow.toml"], {
      cwd: repositoryRoot,
      encoding: "utf8",
    }).trim()).toBe("");
    expect(execFileSync("git", ["ls-files", "--", ".my-workflow.toml.example", "templates/agents"], {
      cwd: repositoryRoot,
      encoding: "utf8",
    })).toContain(".my-workflow.toml.example");
    for (const relativePath of [
      ".my-workflow.toml",
      ".claude/agents/planner.md",
      ".codex/agents/planner.toml",
      ".cursor/agents/planner.md",
    ]) {
      expect(isIgnored(relativePath), relativePath).toBe(true);
    }
    const packaged = packagedFiles();
    expect(packaged).toContain(".my-workflow.toml.example");
    expect(packaged).toContain("templates/agents/claude/planner.md");
    expect(packaged).toContain("templates/agents/codex/planner.toml");
    expect(packaged).toContain("templates/agents/cursor/planner.md");
    expect(packaged).not.toContain(".my-workflow.toml");
    expect(packaged.some((path) => path.startsWith(".claude/agents/"))).toBe(false);
    expect(packaged.some((path) => path.startsWith(".codex/agents/"))).toBe(false);
    expect(packaged.some((path) => path.startsWith(".cursor/agents/"))).toBe(false);
  }, 30_000);

  it("resolves the shipped mixed profile to its exact provider routes", () => {
    const example = readRepositoryFile(".my-workflow.toml.example");
    expect(example).toContain(
      "[profiles.mixed]\nimplementer = \"claude\"\nverifier = \"codex\"\nexplorer = \"cursor\"\ndeep_reviewer = \"codex\"",
    );

    const temporaryRoot = mkdtempSync(join(tmpdir(), "workflow-profile-"));
    try {
      cpSync(join(repositoryRoot, "templates"), join(temporaryRoot, "templates"), { recursive: true });
      cpSync(join(repositoryRoot, ".my-workflow.toml.example"), join(temporaryRoot, ".my-workflow.toml.example"));
      execFileSync("git", ["init", "-q"], { cwd: temporaryRoot });
      execFileSync(
        "git",
        ["-c", "user.email=test@example.com", "-c", "user.name=Test", "commit", "--allow-empty", "-qm", "seed"],
        { cwd: temporaryRoot },
      );
      const resolver = join(
        repositoryRoot,
        ".agents/skills/workflow-config/scripts/workflow_config.py",
      );
      execFileSync("python3", [resolver, "--root", temporaryRoot, "--sync-agents"], { encoding: "utf8" });
      const snapshot = JSON.parse(
        execFileSync(
          "python3",
          [
            resolver,
            "--root",
            temporaryRoot,
            "--feature",
            "mixed-profile-contract",
            "--slices",
            "1",
            "--native-provider",
            "cursor",
            "--profile",
            "mixed",
          ],
          { encoding: "utf8" },
        ),
      ) as { roles: Record<string, { provider: string }> };
      expect(snapshot.roles).toMatchObject({
        implementer: { provider: "claude" },
        verifier: { provider: "codex" },
        explorer: { provider: "cursor" },
        deep_reviewer: { provider: "codex" },
      });
    } finally {
      rmSync(temporaryRoot, { recursive: true, force: true });
    }
  }, 30_000);

  it("asserts resolver-returned agent files for every non-native provider route", () => {
    const temporaryRoot = mkdtempSync(join(tmpdir(), "workflow-config-"));
    try {
      cpSync(join(repositoryRoot, "templates"), join(temporaryRoot, "templates"), { recursive: true });
      cpSync(join(repositoryRoot, ".my-workflow.toml.example"), join(temporaryRoot, ".my-workflow.toml.example"));
      execFileSync("git", ["init", "-q"], { cwd: temporaryRoot });
      execFileSync(
        "git",
        [
          "-c",
          "user.email=test@example.com",
          "-c",
          "user.name=Test",
          "commit",
          "--allow-empty",
          "-qm",
          "seed",
        ],
        { cwd: temporaryRoot },
      );

      const resolver = join(
        repositoryRoot,
        ".agents/skills/workflow-config/scripts/workflow_config.py",
      );
      execFileSync("python3", [resolver, "--root", temporaryRoot, "--sync-agents"], {
        encoding: "utf8",
      });
      const agentNames: Record<string, string> = {
        implementer: "implementer",
        verifier: "verifier",
        explorer: "explorer",
        deep_reviewer: "deep-reviewer",
      };
      for (const provider of providers) {
        const nativeProvider = provider === "codex" ? "claude" : "codex";
        for (const role of resolverRoles) {
          const snapshot = JSON.parse(
            execFileSync(
              "python3",
              [
                resolver,
                "--root",
                temporaryRoot,
                "--feature",
                `it003-${provider}-${role.replaceAll("_", "-")}`,
                "--slices",
                "1",
                "--native-provider",
                nativeProvider,
                "--override",
                `${role}=${provider}`,
              ],
              { encoding: "utf8" },
            ),
          ) as { roles: Record<string, { provider: string; agent_file: string }> };
          const route = snapshot.roles[role];
          expect(route.provider).toBe(provider);
          const extension = provider === "codex" ? "toml" : "md";
          const expectedAgentFile = `.${provider}/agents/${agentNames[role]}.${extension}`;
          expect(route.agent_file).toBe(expectedAgentFile);
          expect(existsSync(join(temporaryRoot, route.agent_file))).toBe(true);
        }
      }
    } finally {
      rmSync(temporaryRoot, { recursive: true, force: true });
    }
  }, 30_000);
});
