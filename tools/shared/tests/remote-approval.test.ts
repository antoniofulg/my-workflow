import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const repositoryRoot = process.cwd();
const boundary = "Readiness is evidence, not authorization";
const remoteActions = ["push", "pull request", "merge"] as const;

function readRepositoryFile(relativePath: string): string {
  return readFileSync(join(repositoryRoot, relativePath), "utf8");
}

describe("remote approval boundary", () => {
  it("keeps readiness separate from remote authority across canonical sources", () => {
    const sources = [
      "AGENTS.md",
      ".agents/skills/autonomous/SKILL.md",
      "docs/workflow/pack.md",
      "docs/workflow/loop.md",
      "README.md",
    ];

    for (const source of sources) {
      const text = readRepositoryFile(source);
      const normalized = text.toLowerCase();
      expect(text, source).toContain(boundary);
      for (const action of remoteActions) {
        expect(normalized, `${source}: ${action}`).toContain(action);
      }
    }
  });

  it("does not turn autonomous readiness into an implicit merge", () => {
    const autonomous = readRepositoryFile(".agents/skills/autonomous/SKILL.md");

    expect(autonomous).not.toContain("Merge with `gh pr merge");
    expect(autonomous).not.toContain("**pass** — merge.");
    expect(autonomous).toContain("Each remote action needs its own explicit");
    expect(autonomous).toContain("If the exact next action is not authorized, stop");
    expect(autonomous).toContain("does not explicitly authorize the next remote action");
  });
});
