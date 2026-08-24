import { cpSync, existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { describe, expect, it } from "vitest";

const repositoryRoot = process.cwd();
const skillPath = ".agents/skills/workflow-config/SKILL.md";
const roles = ["implementer", "verifier", "explorer", "deep-reviewer"] as const;
const resolverRoles = ["implementer", "verifier", "explorer", "deep_reviewer"] as const;
const providers = ["claude", "cursor", "codex"] as const;

function readRepositoryFile(relativePath: string): string {
  return readFileSync(join(repositoryRoot, relativePath), "utf8");
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
        const path = `.${provider}/agents/${role}.${extension}`;
        expect(existsSync(join(repositoryRoot, path)), path).toBe(true);
        expect(readRepositoryFile(path).trim(), path).not.toBe("");
      }
    }
  });

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
