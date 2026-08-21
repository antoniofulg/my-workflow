import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const repositoryRoot = process.cwd();
const skillPath = ".agents/skills/workflow-config/SKILL.md";
const roles = ["implementer", "verifier", "explorer", "deep-reviewer"] as const;
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
});
