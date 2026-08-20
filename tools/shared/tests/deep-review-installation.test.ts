import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const repositoryRoot = process.cwd();
const skillDirectory = join(repositoryRoot, ".agents", "skills", "deep-review");

function readJson(path: string): unknown {
  return JSON.parse(readFileSync(path, "utf8"));
}

describe("deep-review installation", { timeout: 30_000 }, () => {
  it("keeps the skill, lock metadata, release version, and project discovery aligned", () => {
    expect(existsSync(join(skillDirectory, "SKILL.md"))).toBe(true);

    const lock = readJson(join(repositoryRoot, "skills-lock.json")) as {
      skills?: Record<string, unknown>;
    };
    expect(lock.skills?.["deep-review"]).toEqual({
      source: "pedronauck/skills",
      sourceType: "github",
      skillPath: "skills/mine/deep-review/SKILL.md",
      computedHash: "f87524f4e50f1311ebd14a8590bfffac2866a8e333fd4813e12aa2f5803bfe75",
    });

    const packageManifest = readJson(join(repositoryRoot, "package.json")) as {
      version?: string;
    };
    const packageLock = readJson(join(repositoryRoot, "package-lock.json")) as {
      version?: string;
      packages?: Record<string, { version?: string }>;
    };
    expect(packageManifest.version).toBe("0.2.2");
    expect(packageLock.version).toBe("0.2.2");
    expect(packageLock.packages?.[""]?.version).toBe("0.2.2");

    const discovered = JSON.parse(
      execFileSync("npx", ["--yes", "skills", "list", "--json"], {
        cwd: repositoryRoot,
        encoding: "utf8",
      }),
    ) as Array<Record<string, unknown>>;
    expect(discovered).toContainEqual({
      name: "deep-review",
      path: skillDirectory,
      scope: "project",
      agents: expect.any(Array),
      source: "pedronauck/skills",
      sourceUrl: null,
      sourceType: "github",
    });
  });
});
