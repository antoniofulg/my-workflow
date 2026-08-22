import { execFileSync, spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  existsSync,
  lstatSync,
  mkdirSync,
  mkdtempSync,
  readlinkSync,
  symlinkSync,
  readFileSync,
  realpathSync,
  writeFileSync,
  rmSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { delimiter as pathDelimiter, dirname, join } from "node:path";
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
  const pack = writePack(
    target,
    JSON.parse(readFileSync(join(repositoryRoot, "skills-lock.json"), "utf8")),
  );
  return spawnSync(
    "python3",
    [join(pack, "scripts/install_security_skills.py"), target, ...args],
    {
      cwd: repositoryRoot,
      encoding: "utf8",
      env: {
        ...process.env,
        ...env,
        PATH: target + (process.platform === "win32" ? ";" : ":") + (process.env.PATH ?? ""),
      },
    },
  );
}

function writeFakeCli(directory: string, content = "fixture\n"): string {
  const cli = join(directory, "npx");
  writeFileSync(
    cli,
    `#!/usr/bin/env python3
import os, pathlib, sys
skill = sys.argv[sys.argv.index("--skill") + 1]
root = pathlib.Path.cwd()
installed = root / ".agents" / "skills" / skill
installed.mkdir(parents=True, exist_ok=True)
(installed / "SKILL.md").write_text(${JSON.stringify(content)})
link_target = os.environ.get("FAKE_SKILLS_SYMLINK")
if link_target:
    (installed / "escape").symlink_to(link_target)
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

function writeConfiguredNpx(
  directory: string,
  content = "fixture\n",
  options: {
    fail?: boolean;
    fifo?: boolean;
    symlinkTarget?: string;
    ignoredNames?: string[];
    hardlinkTarget?: string;
    invokeGit?: boolean;
    log?: string;
    sleep?: number;
  } = {},
): string {
  const npx = join(directory, "npx");
  const script = [
    "#!/usr/bin/env python3\n",
    "import os, pathlib, sys, subprocess\n",
    options.fail ? "sys.exit(7)\n" : "",
    'skill = sys.argv[sys.argv.index("--skill") + 1]\n',
    "root = pathlib.Path.cwd()\n",
    'installed = root / ".agents" / "skills" / skill\n',
    "installed.mkdir(parents=True, exist_ok=True)\n",
    "(installed / \"SKILL.md\").write_text(" + JSON.stringify(content) + ")\n",
    options.symlinkTarget
      ? '(installed / "escape").symlink_to(' + JSON.stringify(options.symlinkTarget) + ")\n"
      : "",
    ...(options.ignoredNames ?? []).map(
      (name) =>
        '(installed / ' + JSON.stringify(name) + ').mkdir(parents=True, exist_ok=True)\n' +
        '((installed / ' + JSON.stringify(name) + ') / "payload").write_text("ignored\\n")\n',
    ),
    options.hardlinkTarget
      ? 'os.link(' + JSON.stringify(options.hardlinkTarget) + ', installed / "linked")\n'
      : "",
    options.fifo ? '(installed / "special").parent.mkdir(parents=True, exist_ok=True)\nos.mkfifo(installed / "special")\n' : "",
    'claude = root / ".claude" / "skills" / skill\n',
    'claude.parent.mkdir(parents=True, exist_ok=True)\n',
    'if claude.exists() or claude.is_symlink(): claude.unlink()\n',
    'claude.symlink_to(pathlib.Path("../../.agents/skills") / skill)\n',
    options.invokeGit ? 'subprocess.run(["git", "--version"], check=True)\n' : "",
    options.log
      ? 'pathlib.Path(' + JSON.stringify(options.log) + ').open("a").write(" ".join(sys.argv[1:]) + " path=" + os.environ.get("PATH", "") + " env=" + os.environ.get("MY_WORKFLOW_TARGET", "<missing>") + " secrets=" + ",".join(name + "=" + str(name in os.environ) for name in ("GITHUB_TOKEN", "GH_TOKEN", "NPM_TOKEN", "AWS_SECRET_ACCESS_KEY")) + "\\n")\n'
      : "",
    options.sleep ? "import time\ntime.sleep(" + String(options.sleep) + ")\n" : "",
  ].join("");
  writeFileSync(npx, script, { mode: 0o755 });
  return npx;
}

function writeFakeGit(directory: string, marker: string): string {
  const git = join(directory, "git");
  writeFileSync(
    git,
    "#!/bin/sh\nprintf 'trusted-git\\n' > " + JSON.stringify(marker) + "\nexit 0\n",
    { mode: 0o755 },
  );
  return git;
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

function runPackInstaller(
  pack: string,
  target: string,
  npxDirectory: string,
  extraEnv: NodeJS.ProcessEnv = {},
) {
  return spawnSync(
    "python3",
    [join(pack, "scripts/install_security_skills.py"), target, "--yes"],
    {
      cwd: repositoryRoot,
      encoding: "utf8",
      env: {
        ...process.env,
        ...extraEnv,
        PATH:
          extraEnv.PATH ??
          dirname(npxDirectory) +
            (process.platform === "win32" ? ";" : ":") +
            (process.env.PATH ?? ""),
      },
    },
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
      cliVersion: "1.5.23",
      ref: expected.ref,
      computedHash: fixtureHash(content),
    };
  }
  return { version: 1, skills };
}

function fixtureHash(content: string): string {
  return createHash("sha256").update("SKILL.md").update(content).digest("hex");
}

function hardlinkFixtureHash(content: string): string {
  return createHash("sha256")
    .update("SKILL.md")
    .update(content)
    .update("linked")
    .update(content)
    .digest("hex");
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
      expect(lock.skills[name].cliVersion).toBe("1.5.23");
      expect(expected.ref).toMatch(/^[0-9a-f]{40}$/);
      expect(expected.computedHash).toMatch(/^[0-9a-f]{64}$/);
      expect(existsSync(join(repositoryRoot, ".agents/skills", name))).toBe(false);
    }
  });

  it("does not access the network or write the target without authorization", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-plan-"));
    writeFileSync(join(fixture, "consumer.txt"), "keep\n");
    try {
      const result = runInstaller(fixture);
      expect(result.status).toBe(2);
      expect(result.stdout).toContain("no network access and no target writes");
      expect(result.stdout).toContain("49f948faa9258a0c61caceaf225e179651397431");
      expect(existsSync(join(fixture, ".agents"))).toBe(false);
      expect(readFileSync(join(fixture, "consumer.txt"), "utf8")).toBe("keep\n");
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("does not expose a replacement CLI override", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-cli-contract-"));
    try {
      const result = runInstaller(fixture, ["--skills-cli", "replacement"]);
      expect(result.status).toBe(2);
      expect(result.stderr).toContain("unrecognized arguments");
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
    writeFileSync(
      join(fakePack, "scripts/install_security_skills.py"),
      readFileSync(join(repositoryRoot, "scripts/install_security_skills.py")),
    );
    const lockSkills: Record<string, Record<string, string>> = {
      unrelated: { source: "consumer/local", sourceType: "local" },
    };
    for (const [name, expected] of Object.entries(securitySkills)) {
      lockSkills[name] = {
        source: expected.source,
        sourceType: "github",
        skillPath: expected.skillPath,
        cliVersion: "1.5.23",
        ref: expected.ref,
        computedHash: fixtureHash(content),
      };
    }
    writeFileSync(join(fakePack, "skills-lock.json"), JSON.stringify({ version: 1, skills: lockSkills }));
    const cli = writeConfiguredNpx(fixture, content, { log });
    const originalLock = {
      version: 1,
      metadata: { skills: { note: "preserve nested bytes" } },
      skills: { unrelated: { source: "consumer", sourceType: "local" } },
    };
    const consumerBytes = Buffer.from([0, 1, 2, 255, 10]);
    writeFileSync(join(target, "consumer.bin"), consumerBytes);
    writeFileSync(join(target, "skills-lock.json"), JSON.stringify(originalLock, null, 2) + "\n");
    const originalLockBytes = readFileSync(join(target, "skills-lock.json"));
    const originalUnrelatedBytes =
      '"unrelated": {\n      "source": "consumer",\n      "sourceType": "local"\n    }';
    try {
      const result = spawnSync("python3", [join(fakePack, "scripts/install_security_skills.py"), target, "--yes"], {
        cwd: repositoryRoot,
        encoding: "utf8",
        env: {
          ...process.env,
          PATH: fixture + (process.platform === "win32" ? ";" : ":") + (process.env.PATH ?? ""),
        },
      });
      expect(result.status).toBe(0);
      const installedLock = JSON.parse(readFileSync(join(target, "skills-lock.json"), "utf8"));
      expect(installedLock.skills.unrelated).toEqual(originalLock.skills.unrelated);
      expect(installedLock.metadata.skills).toEqual(originalLock.metadata.skills);
      expect(readFileSync(join(target, "consumer.bin"))).toEqual(consumerBytes);
      expect(JSON.stringify(installedLock.skills.unrelated)).toBe(
        JSON.stringify(originalLock.skills.unrelated),
      );
      expect(readFileSync(join(target, "skills-lock.json"), "utf8")).toContain(
        originalUnrelatedBytes,
      );
      expect(originalLockBytes.toString()).toContain(originalUnrelatedBytes);
      expect(readFileSync(join(target, "skills-lock.json"), "utf8")).toContain(
        '"metadata": {\n    "skills": {\n      "note": "preserve nested bytes"\n    }\n  }',
      );
      for (const name of Object.keys(securitySkills)) {
        const installed = join(target, ".agents/skills", name);
        expect(readFileSync(join(installed, "SKILL.md"), "utf8")).toBe(content);
        expect(lstatSync(join(target, ".claude/skills", name)).isSymbolicLink()).toBe(true);
        expect(installedLock.skills[name].computedHash).toBe(fixtureHash(content));
      }
      const commands = readFileSync(log, "utf8")
        .trim()
        .split("\n")
        .map((line) => line.split(" path=")[0]);
      expect(commands).toHaveLength(3);
      expect(commands).toEqual(
        Object.entries(securitySkills).map(
          ([name, expected]) =>
            `--yes skills@1.5.23 add ${expected.source}#${expected.ref} --skill ${name} --agent universal --copy --yes`,
        ),
      );
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
      const result = runInstaller(fixture, ["--yes"]);
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

  it("fails closed when the external CLI is unavailable and preserves the target", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-cli-unavailable-"));
    const target = join(fixture, "target");
    mkdirSync(target);
    const pack = writePack(fixture, validLock());
    const consumerBytes = Buffer.from([3, 1, 4, 1, 5]);
    writeFileSync(join(target, "consumer.bin"), consumerBytes);
    const lockBytes = Buffer.from('{"version":1,"skills":{"consumer":{"source":"local"}}}\n');
    writeFileSync(join(target, "skills-lock.json"), lockBytes);
    try {
      const pathWithoutNpx = [
        join(fixture, "missing-cli"),
        ...(process.env.PATH ?? "")
          .split(pathDelimiter)
          .filter((directory) => !existsSync(join(directory, "npx"))),
      ].join(pathDelimiter);
      const result = runPackInstaller(pack, target, join(fixture, "missing-cli"), {
        PATH: pathWithoutNpx,
      });
      expect(result.status).toBe(1);
      expect(result.stderr).toContain("Security skills unavailable");
      expect(result.stderr).toContain("Security gate remains uncovered");
      expect(readFileSync(join(target, "consumer.bin"))).toEqual(consumerBytes);
      expect(readFileSync(join(target, "skills-lock.json"))).toEqual(lockBytes);
      expect(existsSync(join(target, ".agents"))).toBe(false);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("fails closed when the external CLI returns non-zero and preserves the target", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-cli-failure-"));
    const target = join(fixture, "target");
    mkdirSync(target);
    const pack = writePack(fixture, validLock());
    const cli = writeConfiguredNpx(fixture, "fixture\n", { fail: true });
    const consumerBytes = Buffer.from([9, 2, 6, 5, 3, 5]);
    writeFileSync(join(target, "consumer.bin"), consumerBytes);
    const lockBytes = Buffer.from('{"version":1,"skills":{"consumer":{"source":"local"}}}\n');
    writeFileSync(join(target, "skills-lock.json"), lockBytes);
    try {
      const result = runPackInstaller(pack, target, cli);
      expect(result.status).toBe(1);
      expect(result.stderr).toContain("Security skills unavailable");
      expect(result.stderr).toContain("Security gate remains uncovered");
      expect(readFileSync(join(target, "consumer.bin"))).toEqual(consumerBytes);
      expect(readFileSync(join(target, "skills-lock.json"))).toEqual(lockBytes);
      expect(existsSync(join(target, ".agents"))).toBe(false);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("recovers a dead target lock and removes it after a successful transaction", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-stale-lock-"));
    const target = join(fixture, "target");
    mkdirSync(target);
    const cli = writeFakeCli(fixture);
    const pack = writePack(fixture, validLock());
    mkdirSync(join(target, ".my-workflow-security-skills.lock"));
    writeFileSync(
      join(target, ".my-workflow-security-skills.lock", "owner"),
      "pid=999999\ntoken=stale\n",
    );
    try {
      const result = runPackInstaller(pack, target, cli);
      expect(result.status).toBe(0);
      expect(existsSync(join(target, ".my-workflow-security-skills.lock"))).toBe(false);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("rejects a managed symlink before touching its external referent", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-symlink-"));
    const external = mkdtempSync(join(tmpdir(), "my-workflow-external-"));
    const sentinel = join(external, "sentinel.txt");
    const cli = writeFakeCli(fixture);
    writeFileSync(sentinel, "untouched\n");
    mkdirSync(join(fixture, ".agents"));
    symlinkSync(join(external, "skills"), join(fixture, ".agents", "skills"));
    try {
      const result = runInstaller(fixture, ["--yes"]);
      expect(result.status).toBe(1);
      expect(readFileSync(sentinel, "utf8")).toBe("untouched\n");
      expect(lstatSync(join(fixture, ".agents", "skills")).isSymbolicLink()).toBe(true);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
      rmSync(external, { recursive: true, force: true });
    }
  });

  it("rejects an external skills lock symlink before touching its referent", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-lock-symlink-"));
    const external = mkdtempSync(join(tmpdir(), "my-workflow-lock-external-"));
    const cli = writeFakeCli(fixture);
    const externalLock = join(external, "skills-lock.json");
    writeFileSync(externalLock, "consumer lock bytes\n");
    symlinkSync(externalLock, join(fixture, "skills-lock.json"));
    try {
      const result = runInstaller(fixture, ["--yes"]);
      expect(result.status).toBe(1);
      expect(readFileSync(externalLock, "utf8")).toBe("consumer lock bytes\n");
      expect(lstatSync(join(fixture, "skills-lock.json")).isSymbolicLink()).toBe(true);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
      rmSync(external, { recursive: true, force: true });
    }
  });

  it("restores pre-existing managed skills, links, and lock after publication fails", async () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-rollback-publication-"));
    const target = join(fixture, "target");
    mkdirSync(target);
    const cli = writeFakeCli(fixture, "new\n");
    const pack = writePack(fixture, validLock("new\n"));
    const oldLock = join(target, "skills-lock-target.json");
    const before: Record<string, string | Buffer> = {};
    mkdirSync(join(target, ".agents/skills"), { recursive: true });
    mkdirSync(join(target, ".claude/skills"), { recursive: true });
    for (const name of Object.keys(securitySkills)) {
      const installed = join(target, ".agents/skills", name);
      mkdirSync(installed, { recursive: true });
      writeFileSync(join(installed, "SKILL.md"), `old-${name}\n`);
      const link = join(target, ".claude/skills", name);
      symlinkSync(join("../../.agents/skills", name), link);
      before[`skill:${name}`] = readFileSync(join(installed, "SKILL.md"));
      before[`link:${name}`] = readlinkSync(link);
    }
    writeFileSync(oldLock, "old lock bytes\n");
    symlinkSync("skills-lock-target.json", join(target, "skills-lock.json"));
    before.lock = readFileSync(join(target, "skills-lock.json"), "utf8");
    const publicationMarker = join(fixture, "publication-seen");
    const watcher = spawn(
      "python3",
      [
        "-c",
        "import pathlib, sys, time\n"
          + "path = pathlib.Path(sys.argv[1])\n"
          + "marker = pathlib.Path(sys.argv[2])\n"
          + "deadline = time.time() + 5\n"
          + "while time.time() < deadline:\n"
          + "    try:\n"
          + "        if path.read_text() == 'new\\n':\n"
          + "            marker.write_text('seen')\n"
          + "            break\n"
          + "    except OSError:\n"
          + "        pass\n"
          + "    time.sleep(0.001)\n",
        join(target, ".agents/skills/security-best-practices/SKILL.md"),
        publicationMarker,
      ],
      { stdio: "ignore" },
    );
    try {
      const result = runPackInstaller(pack, target, cli);
      await new Promise<number>((resolve) => watcher.on("close", resolve));
      expect(result.status).toBe(1);
      expect(readFileSync(publicationMarker, "utf8")).toBe("seen");
      for (const name of Object.keys(securitySkills)) {
        expect(readFileSync(join(target, ".agents/skills", name, "SKILL.md"))).toEqual(
          before[`skill:${name}`],
        );
        expect(readlinkSync(join(target, ".claude/skills", name))).toBe(
          before[`link:${name}`],
        );
      }
      expect(readFileSync(join(target, "skills-lock.json"), "utf8")).toBe(before.lock);
      expect(lstatSync(join(target, "skills-lock.json")).isSymbolicLink()).toBe(true);
      expect(readFileSync(oldLock, "utf8")).toBe("old lock bytes\n");
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("creates transaction snapshots on the target filesystem", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-transaction-fs-"));
    const target = join(fixture, "target");
    mkdirSync(target);
    try {
      const probe = execFileSync(
        "python3",
        [
          "-c",
          "import importlib.util, os, pathlib, shutil, sys\n"
            + "spec = importlib.util.spec_from_file_location('installer', sys.argv[2])\n"
            + "module = importlib.util.module_from_spec(spec)\n"
            + "sys.modules[spec.name] = module\n"
            + "spec.loader.exec_module(module)\n"
            + "target = pathlib.Path(sys.argv[1])\n"
            + "path = module.transaction_directory(target, 'probe-')\n"
            + "print(os.stat(target).st_dev == os.stat(path).st_dev)\n"
            + "shutil.rmtree(path)\n",
          target,
          join(repositoryRoot, "scripts/install_security_skills.py"),
        ],
        { cwd: repositoryRoot, encoding: "utf8" },
      );
      expect(probe.trim()).toBe("True");
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("rejects an active tool candidate in the staging root", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-staging-tool-"));
    const target = join(fixture, "target");
    const staging = join(fixture, "staging");
    const packRoot = join(fixture, "pack");
    mkdirSync(target);
    mkdirSync(staging);
    mkdirSync(packRoot);
    writeFileSync(join(staging, "npx"), "#!/bin/sh\nexit 0\n", { mode: 0o755 });
    try {
      const probe = execFileSync(
        "python3",
        [
          "-c",
          "import importlib.util, pathlib, sys\n"
            + "spec = importlib.util.spec_from_file_location('installer', sys.argv[4])\n"
            + "module = importlib.util.module_from_spec(spec)\n"
            + "sys.modules[spec.name] = module\n"
            + "spec.loader.exec_module(module)\n"
            + "try:\n"
            + "    module.resolve_active_binary('npx', sys.argv[2], tuple(pathlib.Path(x) for x in sys.argv[1:4]))\n"
            + "except module.InstallationError:\n"
            + "    print('rejected')\n",
          target,
          staging,
          packRoot,
          join(repositoryRoot, "scripts/install_security_skills.py"),
        ],
        { cwd: repositoryRoot, encoding: "utf8" },
      );
      expect(probe.trim()).toBe("rejected");
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("scrubs the inherited target variable before invoking the external CLI", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-env-"));
    const target = join(fixture, "target");
    mkdirSync(target);
    const log = join(fixture, "cli.log");
    const cli = writeConfiguredNpx(fixture, "fixture\n", { log });
    const pack = writePack(fixture, validLock());
    try {
      const result = runPackInstaller(pack, target, cli, {
        MY_WORKFLOW_TARGET: "/outside/target",
        GITHUB_TOKEN: "token",
        GH_TOKEN: "token",
        NPM_TOKEN: "token",
        AWS_SECRET_ACCESS_KEY: "secret",
      });
      expect(result.status).toBe(0);
      expect(readFileSync(log, "utf8")).not.toContain("/outside/target");
      expect(readFileSync(log, "utf8")).toContain("env=<missing>");
      expect(readFileSync(log, "utf8")).toContain("GITHUB_TOKEN=False");
      expect(readFileSync(log, "utf8")).toContain("GH_TOKEN=False");
      expect(readFileSync(log, "utf8")).toContain("NPM_TOKEN=False");
      expect(readFileSync(log, "utf8")).toContain("AWS_SECRET_ACCESS_KEY=False");
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

  it.each([
    ["sourceType", "local"],
    ["skillPath", "skills/attacker/SKILL.md"],
    ["ref", "0123456789012345678901234567890123456789"],
  ] as const)("rejects substituted %s before publishing", (field, value) => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-provenance-field-"));
    const target = join(fixture, "target");
    mkdirSync(target);
    const cli = writeFakeCli(fixture);
    const lock = validLock();
    (lock.skills as Record<string, Record<string, string>>)["security-review"][field] = value;
    const pack = writePack(fixture, lock);
    try {
      const result = runPackInstaller(pack, target, cli);
      expect(result.status).toBe(1);
      expect(result.stderr).toContain("Security skills unavailable");
      expect(existsSync(join(target, ".agents"))).toBe(false);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("rejects a changed CLI version before publishing any managed tree", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-cli-version-"));
    const target = join(fixture, "target");
    mkdirSync(target);
    const cli = writeFakeCli(fixture);
    const pack = writePack(fixture, validLock());
    const installer = join(pack, "scripts/install_security_skills.py");
    const changed = readFileSync(installer, "utf8").replace(
      'CLI_VERSION = "1.5.23"',
      'CLI_VERSION = "9.9.9"',
    );
    writeFileSync(installer, changed);
    try {
      const result = runPackInstaller(pack, target, cli);
      expect(result.status).toBe(1);
      expect(result.stderr).toContain("CLI version");
      expect(existsSync(join(target, ".agents"))).toBe(false);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("rejects a symlink anywhere in a staged skill before publication", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-staged-symlink-"));
    const target = join(fixture, "target");
    const external = mkdtempSync(join(tmpdir(), "my-workflow-staged-external-"));
    mkdirSync(target);
    const externalSentinel = join(external, "sentinel.txt");
    writeFileSync(externalSentinel, "do not touch\n");
    const cli = writeConfiguredNpx(fixture, "fixture\n", { symlinkTarget: externalSentinel });
    const pack = writePack(fixture, validLock());
    try {
      const result = runPackInstaller(pack, target, cli);
      expect(result.status).toBe(1);
      expect(result.stderr).toContain("symlink");
      expect(existsSync(join(target, ".agents"))).toBe(false);
      expect(readFileSync(externalSentinel, "utf8")).toBe("do not touch\n");
    } finally {
      rmSync(fixture, { recursive: true, force: true });
      rmSync(external, { recursive: true, force: true });
    }
  });

  it("rejects a special file anywhere in a staged skill before publication", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-staged-special-"));
    const target = join(fixture, "target");
    mkdirSync(target);
    const npx = writeConfiguredNpx(fixture, "fixture\n", { fifo: true });
    const pack = writePack(fixture, validLock());
    const consumerBytes = Buffer.from([7, 7, 7]);
    const lockBytes = Buffer.from('{"version":1,"skills":{"consumer":{"source":"local"}}}\n');
    writeFileSync(join(target, "consumer.bin"), consumerBytes);
    writeFileSync(join(target, "skills-lock.json"), lockBytes);
    try {
      const result = runPackInstaller(pack, target, npx);
      expect(result.status).toBe(1);
      expect(result.stderr).toContain("non-regular");
      expect(readFileSync(join(target, "consumer.bin"))).toEqual(consumerBytes);
      expect(readFileSync(join(target, "skills-lock.json"))).toEqual(lockBytes);
      expect(existsSync(join(target, ".agents"))).toBe(false);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it.each([".git", "node_modules"])(
    "rejects staged %s content even when the ignored payload matches the hash",
    (ignoredName) => {
      const fixture = mkdtempSync(join(tmpdir(), "my-workflow-staged-ignored-"));
      const target = join(fixture, "target");
      mkdirSync(target);
      const npx = writeConfiguredNpx(fixture, "fixture\n", { ignoredNames: [ignoredName] });
      const pack = writePack(fixture, validLock());
      const consumerBytes = Buffer.from([8, 8, 8]);
      const lockBytes = Buffer.from('{"version":1,"skills":{"consumer":{"source":"local"}}}\n');
      writeFileSync(join(target, "consumer.bin"), consumerBytes);
      writeFileSync(join(target, "skills-lock.json"), lockBytes);
      try {
        const result = runPackInstaller(pack, target, npx);
        expect(result.status).toBe(1);
        expect(result.stderr).toContain("forbidden entry");
        expect(readFileSync(join(target, "consumer.bin"))).toEqual(consumerBytes);
        expect(readFileSync(join(target, "skills-lock.json"))).toEqual(lockBytes);
        expect(existsSync(join(target, ".agents"))).toBe(false);
      } finally {
        rmSync(fixture, { recursive: true, force: true });
      }
    },
  );

  it("rejects hardlinked staged files without changing the external sentinel", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-staged-hardlink-"));
    const target = join(fixture, "target");
    mkdirSync(target);
    const externalSentinel = join(fixture, "consumer-sentinel.txt");
    writeFileSync(externalSentinel, "fixture\n");
    const npx = writeConfiguredNpx(fixture, "fixture\n", { hardlinkTarget: externalSentinel });
    const lock = validLock();
    for (const entry of Object.values(lock.skills)) {
      if (entry.sourceType === "github") entry.computedHash = hardlinkFixtureHash("fixture\n");
    }
    const pack = writePack(fixture, lock);
    try {
      const result = runPackInstaller(pack, target, npx);
      expect(result.status).toBe(1);
      expect(result.stderr).toContain("hardlinked file");
      expect(readFileSync(externalSentinel, "utf8")).toBe("fixture\n");
      expect(existsSync(join(target, ".agents"))).toBe(false);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("accepts an active mise-style external toolchain and passes exact pinned args", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-trusted-tools-"));
    const target = join(fixture, "target");
    const toolchain = join(fixture, "toolchain");
    const shims = join(toolchain, "shims");
    const versions = join(toolchain, "versions");
    const trustedGitMarker = join(fixture, "trusted-git.log");
    mkdirSync(target);
    mkdirSync(shims, { recursive: true });
    mkdirSync(versions, { recursive: true });
    const log = join(fixture, "trusted-npx.log");
    const npxTarget = writeConfiguredNpx(versions, "fixture\n", { log, invokeGit: true });
    const gitTarget = writeFakeGit(versions, trustedGitMarker);
    const npx = join(shims, "npx");
    const git = join(shims, "git");
    const hostile = join(fixture, "hostile");
    mkdirSync(hostile);
    writeFileSync(join(hostile, "npx"), "#!/bin/sh\nprintf hostile-npx > " + JSON.stringify(join(fixture, "hostile-npx.log")) + "\n", { mode: 0o755 });
    symlinkSync(npxTarget, npx);
    symlinkSync(gitTarget, git);
    const pack = writePack(fixture, validLock());
    try {
      const result = runPackInstaller(pack, target, npx, {
        PATH: [shims, hostile, process.env.PATH ?? ""].join(pathDelimiter),
        GITHUB_TOKEN: "secret",
      });
      expect(result.status).toBe(0);
      expect(readFileSync(trustedGitMarker, "utf8")).toBe("trusted-git\n");
      const lines = readFileSync(log, "utf8").trim().split("\n");
      expect(lines).toHaveLength(3);
      expect(lines.map((line) => line.split(" path=")[0])).toEqual(
        Object.entries(securitySkills).map(
          ([name, expected]) =>
            `--yes skills@1.5.23 add ${expected.source}#${expected.ref} --skill ${name} --agent universal --copy --yes`,
        ),
      );
      const recordedPath = lines[0].split(" path=")[1].split(" env=")[0];
      const pathParts = recordedPath.split(pathDelimiter);
      expect(pathParts.slice(1)).toEqual([
        shims,
        realpathSync(versions),
        "/opt/homebrew/bin",
        "/usr/local/bin",
        "/usr/bin",
        "/bin",
      ]);
      expect(new Set(pathParts).size).toBe(pathParts.length);
      expect(pathParts).not.toContain(hostile);
      expect(existsSync(join(fixture, "hostile-npx.log"))).toBe(false);
      expect(lines[0]).toContain("GITHUB_TOKEN=False");
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it.each(["target", "pack-root"])(
    "rejects an active npx candidate in the untrusted %s root",
    (location) => {
      const fixture = mkdtempSync(join(tmpdir(), "my-workflow-untrusted-tool-root-"));
      const target = join(fixture, "target");
      mkdirSync(target);
      const pack = writePack(fixture, validLock());
      const root = location === "target" ? target : pack;
      writeFileSync(join(root, "npx"), "#!/bin/sh\nexit 0\n", { mode: 0o755 });
      try {
        const result = runPackInstaller(pack, target, join(fixture, "missing-npx"), {
          PATH: root + pathDelimiter + (process.env.PATH ?? ""),
        });
        expect(result.status).toBe(1);
        expect(result.stderr).toContain("unsafe npx executable");
        expect(existsSync(join(target, ".agents"))).toBe(false);
      } finally {
        rmSync(fixture, { recursive: true, force: true });
      }
    },
  );

  it("rejects a git candidate in the target root even with an active external npx", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-untrusted-git-root-"));
    const target = join(fixture, "target");
    mkdirSync(target);
    const npx = writeConfiguredNpx(fixture, "fixture\n");
    writeFileSync(join(target, "git"), "#!/bin/sh\nexit 0\n", { mode: 0o755 });
    const pack = writePack(fixture, validLock());
    try {
      const result = runPackInstaller(pack, target, npx, {
        PATH: target + pathDelimiter + dirname(npx) + pathDelimiter + (process.env.PATH ?? ""),
      });
      expect(result.status).toBe(1);
      expect(result.stderr).toContain("unsafe git executable");
      expect(existsSync(join(target, ".agents"))).toBe(false);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("rejects a safe-looking shim resolving into the target root", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-untrusted-shim-"));
    const target = join(fixture, "target");
    const shims = join(fixture, "shims");
    mkdirSync(target);
    mkdirSync(shims);
    const targetNpx = join(target, "npx");
    writeFileSync(targetNpx, "#!/bin/sh\nexit 0\n", { mode: 0o755 });
    symlinkSync(targetNpx, join(shims, "npx"));
    const pack = writePack(fixture, validLock());
    try {
      const result = runPackInstaller(pack, target, join(fixture, "missing-npx"), {
        PATH: shims + pathDelimiter + (process.env.PATH ?? ""),
      });
      expect(result.status).toBe(1);
      expect(result.stderr).toContain("unsafe npx executable target");
      expect(existsSync(join(target, ".agents"))).toBe(false);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it("rejects a lexical tool candidate inside the target even when it resolves outside", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-lexical-tool-root-"));
    const target = join(fixture, "target");
    const external = join(fixture, "external");
    const bin = join(target, "bin");
    mkdirSync(bin, { recursive: true });
    mkdirSync(external);
    const externalNpx = writeConfiguredNpx(external, "fixture\n");
    symlinkSync(externalNpx, join(bin, "npx"));
    const pack = writePack(fixture, validLock());
    try {
      const result = runPackInstaller(pack, target, join(fixture, "missing-npx"), {
        PATH: bin + pathDelimiter + (process.env.PATH ?? ""),
      });
      expect(result.status).toBe(1);
      expect(result.stderr).toContain("unsafe npx executable location");
      expect(existsSync(join(target, ".agents"))).toBe(false);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });

  it.each(["broken", "directory", "non-executable"])(
    "rejects %s active npx candidates",
    (kind) => {
      const fixture = mkdtempSync(join(tmpdir(), "my-workflow-invalid-tool-"));
      const target = join(fixture, "target");
      const tools = join(fixture, "tools");
      mkdirSync(target);
      mkdirSync(tools);
      const candidate = join(tools, "npx");
      if (kind === "broken") symlinkSync(join(tools, "missing"), candidate);
      if (kind === "directory") mkdirSync(candidate);
      if (kind === "non-executable") writeFileSync(candidate, "#!/bin/sh\nexit 0\n");
      const pack = writePack(fixture, validLock());
      try {
        const result = runPackInstaller(pack, target, join(fixture, "missing-npx"), {
          PATH: tools + pathDelimiter + (process.env.PATH ?? ""),
        });
        expect(result.status).toBe(1);
        expect(result.stderr).toContain("invalid npx executable");
        expect(existsSync(join(target, ".agents"))).toBe(false);
      } finally {
        rmSync(fixture, { recursive: true, force: true });
      }
    },
  );

  it("rejects an unapproved CLI version in the target lock before invoking the CLI", () => {
    const fixture = mkdtempSync(join(tmpdir(), "my-workflow-lock-cli-version-"));
    const target = join(fixture, "target");
    mkdirSync(target);
    const cli = writeFakeCli(fixture);
    const lock = validLock();
    (lock.skills as Record<string, Record<string, string>>)["security-review"].cliVersion = "1.5.22";
    const pack = writePack(fixture, lock);
    try {
      const result = runPackInstaller(pack, target, cli);
      expect(result.status).toBe(1);
      expect(result.stderr).toContain("CLI version");
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
    const target = join(fixture, "target");
    mkdirSync(target);
    const cli = writeConfiguredNpx(fixture, "fixture\n", { sleep: 0.2 });
    const pack = writePack(fixture, validLock());
    const first = spawn(
      "python3",
      [join(pack, "scripts/install_security_skills.py"), target, "--yes"],
      {
        cwd: repositoryRoot,
        env: {
          ...process.env,
          PATH: fixture + (process.platform === "win32" ? ";" : ":") + (process.env.PATH ?? ""),
        },
        encoding: "utf8",
      },
    );
    await new Promise((resolve) => setTimeout(resolve, 60));
    const second = spawnSync(
      "python3",
      [join(pack, "scripts/install_security_skills.py"), target, "--yes"],
      {
        cwd: repositoryRoot,
        env: {
          ...process.env,
          PATH: fixture + (process.platform === "win32" ? ";" : ":") + (process.env.PATH ?? ""),
        },
        encoding: "utf8",
      },
    );
    const firstStatus = await new Promise<number>((resolve) => first.on("close", resolve));
    try {
      expect(second.status).toBe(1);
      expect(firstStatus).toBe(0);
      expect(existsSync(join(target, ".agents/skills/security-best-practices/SKILL.md"))).toBe(true);
    } finally {
      rmSync(fixture, { recursive: true, force: true });
    }
  });
});
