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

describe("QA workflow artifact policy", () => {
  it("IT-007 ignores generated Deep Review output but keeps learnings eligible", () => {
    const gitignore = readRepositoryFile(".gitignore");

    expect(gitignore).toContain(".deep-review/*");
    expect(gitignore).toContain("!.deep-review/learnings.md");
    expect(isIgnored(".deep-review/findings.md")).toBe(true);
    expect(isIgnored(".deep-review/qa-skills-t1/agents/cohort-c01.json")).toBe(true);
    expect(isIgnored(".deep-review/learnings.md")).toBe(false);
  });

  it("IT-014 ignores feature planning while preserving durable decisions", () => {
    expect(isIgnored(".specs/features/qa-skills/spec.md")).toBe(true);
    expect(isIgnored(".specs/STATE.md")).toBe(false);
    expect(isIgnored(".specs/AD-INDEX.md")).toBe(false);
    expect(tracked(".specs/STATE.md")).toBe(".specs/STATE.md");
    expect(tracked(".specs/AD-INDEX.md")).toBe(".specs/AD-INDEX.md");
  });

  it("IT-015 treats the local task state as the commit precondition", () => {
    const agents = readRepositoryFile("AGENTS.md");
    const loop = readRepositoryFile("docs/workflow/loop.md");
    const specDriven = readRepositoryFile(".agents/skills/tlc-spec-driven/SKILL.md");
    const implementer = readRepositoryFile(".agents/skills/tlc-spec-driven/references/implement.md");
    const providerPackets = [
      readRepositoryFile(".cursor/agents/implementer.md"),
      readRepositoryFile(".claude/agents/implementer.md"),
      readRepositoryFile(".codex/agents/implementer.toml"),
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
    expect(implementer).toContain("close the task record **before** creating the commit");
    expect(implementer).toContain("If `tasks.md` is present, mark the task complete in `tasks.md`.");
    expect(implementer).toMatch(
      /If Tasks was skipped, mark the\s+current inline execution-plan step complete/,
    );
    expect(implementer.indexOf("close the task record **before** creating the commit")).toBeLessThan(
      implementer.indexOf("Create **one** atomic commit"),
    );
    expect(implementer).not.toContain("include those status/traceability updates");
    expect(implementer).not.toContain("plus the `tasks.md` / `spec.md` status updates");
    for (const packet of providerPackets) {
      expect(packet).toContain("when present, or the");
      expect(packet).toContain("inline execution plan when Tasks is skipped");
      expect(packet).not.toContain("traceability in the same commit");
    }
    expect(tracked(".specs/features/qa-skills/tasks.md")).toBe("");
  });

  it("IT-016 leaves no disposable feature artifacts tracked", () => {
    expect(tracked(".specs/features")).toBe("");
  });
});
