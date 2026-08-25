import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join, relative, sep } from "node:path";
import { describe, expect, it } from "vitest";

const repositoryRoot = process.cwd();
const skillDirectory = join(repositoryRoot, ".agents", "skills", "deep-review");

function readJson(path: string): unknown {
  return JSON.parse(readFileSync(path, "utf8"));
}

function hashSkillTree(directory: string): string {
  const files: Array<{ relativePath: string; content: Buffer }> = [];

  function collect(currentDirectory: string): void {
    for (const entry of readdirSync(currentDirectory, { withFileTypes: true })) {
      const fullPath = join(currentDirectory, entry.name);
      if (entry.isDirectory()) {
        if (entry.name !== ".git" && entry.name !== "node_modules" && entry.name !== "__pycache__") {
          collect(fullPath);
        }
      } else if (entry.isFile() && !entry.name.endsWith(".pyc")) {
        files.push({
          relativePath: relative(directory, fullPath).split(sep).join("/"),
          content: readFileSync(fullPath),
        });
      }
    }
  }

  collect(directory);
  files.sort((left, right) => left.relativePath.localeCompare(right.relativePath));

  const hash = createHash("sha256");
  for (const file of files) {
    hash.update(file.relativePath);
    hash.update(file.content);
  }
  return hash.digest("hex");
}

describe("deep-review installation", { timeout: 30_000 }, () => {
  it("keeps the skill, lock metadata, release version, and project discovery aligned", () => {
    expect(existsSync(join(skillDirectory, "SKILL.md"))).toBe(true);

    const lock = readJson(join(repositoryRoot, "skills-lock.json")) as {
      skills?: Record<string, unknown>;
    };
    const lockEntry = lock.skills?.["deep-review"] as
      | { source?: string; sourceType?: string; skillPath?: string; computedHash?: string }
      | undefined;
    expect(lockEntry).toEqual({
      source: "pedronauck/skills",
      sourceType: "github",
      skillPath: "skills/mine/deep-review/SKILL.md",
      computedHash: "d14552d1e263be76e903a34b232cd0336d9ea279d91cdc3c89ccfaed10a055c4",
    });
    expect(hashSkillTree(skillDirectory)).toBe(lockEntry?.computedHash);

    const packageManifest = readJson(join(repositoryRoot, "package.json")) as {
      version?: string;
      devDependencies?: Record<string, string>;
    };
    const packageLock = readJson(join(repositoryRoot, "package-lock.json")) as {
      version?: string;
      packages?: Record<string, { version?: string; devDependencies?: Record<string, string> }>;
    };
    expect(packageManifest.version).toBe("0.6.0");
    expect(packageLock.version).toBe("0.6.0");
    expect(packageLock.packages?.[""]?.version).toBe("0.6.0");
    expect(packageManifest.devDependencies?.skills).toBe("1.5.23");
    expect(packageLock.packages?.[""]?.devDependencies?.skills).toBe("1.5.23");
    expect(packageLock.packages?.["node_modules/skills"]?.version).toBe("1.5.23");
    expect(
      (readJson(join(repositoryRoot, "node_modules", "skills", "package.json")) as {
        version?: string;
      }).version,
    ).toBe("1.5.23");

    const discovered = JSON.parse(
      execFileSync(join(repositoryRoot, "node_modules", ".bin", "skills"), ["list", "--json"], {
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
