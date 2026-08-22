import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  existsSync,
  lstatSync,
  mkdirSync,
  mkdtempSync,
  symlinkSync,
  readFileSync,
  writeFileSync,
  rmSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const repositoryRoot = process.cwd();
const securitySkills = {
  "security-best-practices": {
    source: "openai/skills",
    skillPath: "skills/.curated/security-best-practices/SKILL.md",
    ref: "49f948faa9258a0c61caceaf225e179651397431",
    computedHash: "7bd6c2cc8083d90f5d5489c80887ed5399e167d3e7323c7f294035e1e586b689",
  },
  "security-threat-model": {
    source: "openai/skills",
    skillPath: "skills/.curated/security-threat-model/SKILL.md",
    ref: "49f948faa9258a0c61caceaf225e179651397431",
    computedHash: "a262f878637565892051aa945c88e8748e743896c20925b59c5c2d7d79e061a7",
  },
  "security-review": {
    source: "github/awesome-copilot",
    skillPath: "skills/security-review/SKILL.md",
    ref: "83561bd7d8a46fcda0581aedabdf8eac7cb196b6",
    computedHash: "a0fc25587c016178c9cf6238ac8702695fa761694965192472487f92093db571",
  },
} as const;

function runInstaller(target: string, args: string[] = [], env: NodeJS.ProcessEnv = {}) {
  return spawnSync(
    "python3",
    [join(repositoryRoot, "scripts/install_security_skills.py"), target, ...args],
    { cwd: repositoryRoot, encoding: "utf8", env: { ...process.env, ...env } },
  );
}

function writeFakeCli(directory: string, content = "fixture\n"): string {
  const cli = join(directory, "fake-skills-cli.py");
  writeFileSync(
    cli,
    `#!/usr/bin/env python3
import os, pathlib, sys
skill = sys.argv[sys.argv.index("--skill") + 1]
root = pathlib.Path.cwd()
installed = root / ".agents" / "skills" / skill
installed.mkdir(parents=True, exist_ok=True)
(installed / "SKILL.md").write_text(${JSON.stringify(content)})
claude = root / ".claude" / "skills" / skill
claude.parent.mkdir(parents=True, exist_ok=True)
if claude.exists() or claude.is_symlink(): claude.unlink()
claude.symlink_to(pathlib.Path("../../.agents/skills") / skill)
log = os.environ.get("FAKE_SKILLS_LOG")
if log:
    pathlib.Path(log).open("a").write(" ".join(sys.argv[1:]) + " env=" + os.environ.get("MY_WORKFLOW_TARGET", "<missing>") + "\\n")
if os.environ.get("FAKE_SKILLS_SLEEP"):
    import time
    time.sleep(float(os.environ["FAKE_SKILLS_SLEEP"]))
`,
    { mode: 0o755 },
  );
  return cli;
}

function writePack(directory: string, lock: object): string {
  const pack = join(directory, "pack");
  mkdirSync(join(pack, "scripts"), { recursive: true });
  writeFileSync(
    join(pack, "scripts/install_security_skills.py"),
    readFileSync(join(repositoryRoot, "scripts/install_security_skills.py")),
  );
  writeFileSync(join(pack, "skills-lock.json"), JSON.stringify(lock));
  return pack;
}

function runPackInstaller(pack: string, target: string, cli: string, extraEnv: NodeJS.ProcessEnv = {}) {
  return spawnSync(
    "python3",
    [join(pack, "scripts/install_security_skills.py"), target, "--yes", "--skills-cli", cli],
    { cwd: repositoryRoot, encoding: "utf8", env: { ...process.env, ...extraEnv } },
  );
}

function validLock(content = "fixture\n") {
  const skills: Record<string, Record<string, string>> = {
    unrelated: { source: "consumer/local", sourceType: "local" },
  };
  for (const [name, expected] of Object.entries(securitySkills)) {
    skills[name] = {
      source: expected.source,
      sourceType: "github",
      skillPath: expected.skillPath,
      ref: expected.ref,
      computedHash: fixtureHash(content),
    };
  }
  return { version: 1, skills };
}

function fixtureHash(content: string): string {
  return createHash("sha256").update("SKILL.md").update(content).digest("hex");
}

describe("external security skill installation", { timeout: 30_000 }, () => {
  it("keeps external provenance documented without vendoring security trees", () => {
    const readme = readFileSync(join(repositoryRoot, "README.md"), "utf8");
    expect(readme).toContain("external security skills");
    expect(readme).toContain("explicit authorization");
    expect(readme).toContain("skills-lock.json");
    expect(readme).not.toContain("bundle also includes three security skills");
  });

  it("adopts bundled workflow without security trees and prints the authorized second step", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-adopt-"));
    try {
      const result = spawnSync("python3", [join(repositoryRoot, "scripts/adopt.py"), fixture], {
        cwd: repositoryRoot,
        encoding: "utf8",
      });
      expect(result.status).toBe(0);
      for (const name of Object.keys(securitySkills)) {
        expect(existsSync(join(fixture, ".agents/skills", name))).toBe(false);
      }
      expect(result.stdout).toContain("install_security_skills.py");
      expect(result.stdout).toContain(`${fixture} --yes`);
      expect(result.stdout).toContain("security gate remains uncovered");
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("keeps only pinned external provenance and no vendored security trees", () => {
    const lock = JSON.parse(readFileSync(join(repositoryRoot, "skills-lock.json"), "utf8"));
    for (const [name, expected] of Object.entries(securitySkills)) {
      expect(lock.skills[name]).toMatchObject({ ...expected, sourceType: "github" });
      expect(expected.ref).toMatch(/^[0-9a-f]{40}$/);
      expect(expected.computedHash).toMatch(/^[0-9a-f]{64}$/);
      expect(existsSync(join(repositoryRoot, ".agents/skills", name))).toBe(false);
    }
  });

  it("does not access the network or write the target without authorization", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-plan-"));
    const log = join(fixture, "cli.log");
    const cli = writeFakeCli(fixture);
    writeFileSync(join(fixture, "consumer.txt"), "keep\n");
    try {
      const result = runInstaller(fixture, [], {
        MY_WORKFLOW_SKILLS_CLI: cli,
        FAKE_SKILLS_LOG: log,
      });
      expect(result.status).toBe(2);
      expect(result.stdout).toContain("no network access and no target writes");
      expect(result.stdout).toContain("49f948faa9258a0c61caceaf225e179651397431");
      expect(existsSync(join(fixture, ".agents"))).toBe(false);
      expect(existsSync(log)).toBe(false);
      expect(readFileSync(join(fixture, "consumer.txt"), "utf8")).toBe("keep\n");
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("uses pinned add commands, installs the shared tree, links Claude, and preserves lock entries", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-install-"));
    const fakePack = join(fixture, "pack");
    const target = join(fixture, "target");
    const log = join(fixture, "cli.log");
    const content = "fixture\n";
    mkdirSync(join(fakePack, "scripts"), { recursive: true });
    mkdirSync(target, { recursive: true });
    writeFileSync(join(fakePack, "scripts/install_security_skills.py"), readFileSync(join(repositoryRoot, "scripts/install_security_skills.py")));
    const lockSkills: Record<string, Record<string, string>> = {
      unrelated: { source: "consumer/local", sourceType: "local" },
    };
    for (const [name, expected] of Object.entries(securitySkills)) {
      lockSkills[name] = {
        source: expected.source,
        sourceType: "github",
        skillPath: expected.skillPath,
        ref: expected.ref,
        computedHash: fixtureHash(content),
      };
    }
    writeFileSync(join(fakePack, "skills-lock.json"), JSON.stringify({ version: 1, skills: lockSkills }));
    const cli = writeFakeCli(fixture, content);
    const originalLock = { version: 1, skills: { unrelated: { source: "consumer", sourceType: "local" } } };
    writeFileSync(join(target, "skills-lock.json"), JSON.stringify(originalLock));
    try {
      const result = spawnSync("python3", [join(fakePack, "scripts/install_security_skills.py"), target, "--yes", "--skills-cli", cli], {
        cwd: repositoryRoot,
        encoding: "utf8",
        env: { ...process.env, FAKE_SKILLS_LOG: log },
      });
      expect(result.status).toBe(0);
      const installedLock = JSON.parse(readFileSync(join(target, "skills-lock.json"), "utf8"));
      expect(installedLock.skills.unrelated).toEqual(originalLock.skills.unrelated);
      for (const name of Object.keys(securitySkills)) {
        const installed = join(target, ".agents/skills", name);
        expect(readFileSync(join(installed, "SKILL.md"), "utf8")).toBe(content);
        expect(lstatSync(join(target, ".claude/skills", name)).isSymbolicLink()).toBe(true);
        expect(installedLock.skills[name].computedHash).toBe(fixtureHash(content));
      }
      const commands = readFileSync(log, "utf8").trim().split("\n");
      expect(commands).toHaveLength(3);
      for (const command of commands) {
        expect(command).toContain("add");
        expect(command).toMatch(/#[0-9a-f]{40}/);
        expect(command).toContain("--skill");
        expect(command).toContain("--yes");
        expect(command).not.toContain("latest");
        expect(command).not.toContain("experimental_install");
      }
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("fails closed on an incorrect hash and preserves unrelated state", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-integrity-"));
    const cli = writeFakeCli(fixture, "tampered\n");
    writeFileSync(join(fixture, "consumer.txt"), "before\n");
    writeFileSync(join(fixture, "skills-lock.json"), JSON.stringify({ version: 1, skills: { unrelated: { source: "consumer" } } }));
    try {
      const result = runInstaller(fixture, ["--yes", "--skills-cli", cli]);
      expect(result.status).toBe(1);
      expect(result.stderr).toContain("Security skills unavailable");
      expect(result.stderr).toContain("gate remains uncovered");
      expect(existsSync(join(fixture, ".agents"))).toBe(false);
      expect(readFileSync(join(fixture, "consumer.txt"), "utf8")).toBe("before\n");
      expect(JSON.parse(readFileSync(join(fixture, "skills-lock.json"), "utf8")).skills.unrelated).toEqual({ source: "consumer" });
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("recovers a dead target lock and removes it after a successful transaction", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-stale-lock-"));
    const cli = writeFakeCli(fixture);
    const pack = writePack(fixture, validLock());
    mkdirSync(join(fixture, ".my-workflow-security-skills.lock"));
    writeFileSync(
      join(fixture, ".my-workflow-security-skills.lock", "owner"),
      "pid=999999\ntoken=stale\n",
    );
    try {
      const result = runPackInstaller(pack, fixture, cli);
      expect(result.status).toBe(0);
      expect(existsSync(join(fixture, ".my-workflow-security-skills.lock"))).toBe(false);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("rejects a managed symlink before touching its external referent", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-symlink-"));
    const external = mkdtempSync(join(tmpdir(), "my-workflow-external-"));
    const cli = writeFakeCli(fixture);
    const sentinel = join(external, "sentinel.txt");
    writeFileSync(sentinel, "untouched\n");
    mkdirSync(join(fixture, ".agents"));
    symlinkSync(join(external, "skills"), join(fixture, ".agents", "skills"));
    try {
      const result = runInstaller(fixture, ["--yes", "--skills-cli", cli]);
      expect(result.status).toBe(1);
      expect(readFileSync(sentinel, "utf8")).toBe("untouched\n");
      expect(lstatSync(join(fixture, ".agents", "skills")).isSymbolicLink()).toBe(true);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
      rmSync(external, { recursive: true, force: true });
    }
  });

  it("scrubs the inherited target variable before invoking the external CLI", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-env-"));
    const log = join(fixture, "cli.log");
    const cli = writeFakeCli(fixture);
    const pack = writePack(fixture, validLock());
    try {
      const result = runPackInstaller(pack, fixture, cli, {
        MY_WORKFLOW_TARGET: "/outside/target",
        FAKE_SKILLS_LOG: log,
      });
      expect(result.status).toBe(0);
      expect(readFileSync(log, "utf8")).not.toContain("/outside/target");
      expect(readFileSync(log, "utf8")).toContain("env=<missing>");
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("rejects substituted provenance before publishing any managed tree", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-provenance-"));
    const target = join(fixture, "target");
    mkdirSync(target);
    const cli = writeFakeCli(fixture);
    const lock = validLock();
    (lock.skills as Record<string, Record<string, string>>)["security-review"].source = "attacker/skills";
    const pack = writePack(fixture, lock);
    try {
      const result = runPackInstaller(pack, target, cli);
      expect(result.status).toBe(1);
      expect(existsSync(join(target, ".agents"))).toBe(false);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("rejects latest and non-commit refs in the lock", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-ref-"));
    const target = join(fixture, "target");
    mkdirSync(target);
    const cli = writeFakeCli(fixture);
    const lock = validLock();
    (lock.skills as Record<string, Record<string, string>>)["security-review"].ref = "latest";
    const pack = writePack(fixture, lock);
    try {
      const result = runPackInstaller(pack, target, cli);
      expect(result.status).toBe(1);
      expect(existsSync(join(target, ".agents"))).toBe(false);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("serializes concurrent installers so a completed winner is not rolled back", async () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-concurrent-"));
    const cli = writeFakeCli(fixture);
    const pack = writePack(fixture, validLock());
    const first = spawn(
      "python3",
      [join(pack, "scripts/install_security_skills.py"), fixture, "--yes", "--skills-cli", cli],
      { cwd: repositoryRoot, env: { ...process.env, FAKE_SKILLS_SLEEP: "0.2" }, encoding: "utf8" },
    );
    await new Promise((resolve) => setTimeout(resolve, 60));
    const second = spawnSync(
      "python3",
      [join(pack, "scripts/install_security_skills.py"), fixture, "--yes", "--skills-cli", cli],
      { cwd: repositoryRoot, env: process.env, encoding: "utf8" },
    );
    const firstStatus = await new Promise<number>((resolve) => first.on("close", resolve));
    try {
      expect(second.status).toBe(1);
      expect(firstStatus).toBe(0);
      expect(existsSync(join(fixture, ".agents/skills/security-best-practices/SKILL.md"))).toBe(true);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });
});
