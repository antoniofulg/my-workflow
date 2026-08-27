import { spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { afterEach, describe, expect, it } from "bun:test";

const repositoryRoot = process.cwd();
const createdRoots: string[] = [];

function makeBundle(files: Record<string, string>): string {
  const root = mkdtempSync(join(tmpdir(), "okf-knowledge-cli-"));
  createdRoots.push(root);
  for (const [path, content] of Object.entries(files)) {
    const target = join(root, path);
    mkdirSync(dirname(target), { recursive: true });
    writeFileSync(target, content, "utf8");
  }
  return root;
}

function runKnowledgeScript(...args: string[]) {
  return spawnSync("npm", ["run", "--silent", "knowledge", "--", ...args], {
    cwd: repositoryRoot,
    encoding: "utf8",
  });
}

afterEach(() => {
  for (const root of createdRoots.splice(0)) {
    rmSync(root, { recursive: true, force: true });
  }
});

// Each dedicated knowledge case shells out to `npm run knowledge`, so it pays npm and tsx startup
// on top of the check itself. That is a couple of seconds alone during parallel
// load, well past the 5s default. The timeout is generous on purpose: a regression here should
// read as a failed assertion, never as a flaky clock.
describe("npm run knowledge", { timeout: 30_000 }, () => {
  it("keeps repository-bundle validation out of the full structural gate", () => {
    const manifest = JSON.parse(
      readFileSync(join(repositoryRoot, "package.json"), "utf8"),
    ) as { scripts?: { test?: string } };

    expect(manifest.scripts?.test).toContain("bun test");
    expect(manifest.scripts?.test).not.toContain("knowledge");
  });

  it("exits non-zero and names the offending concept when frontmatter is missing", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": '---\nokf_version: "0.2"\n---\n\n# Bundle\n',
      "knowledge/wiki/domain/sample-term.md": "# Sample Term\n",
    });

    const result = runKnowledgeScript(root);

    expect(result.status).not.toBe(0);
    expect(result.stderr).toContain("knowledge/wiki/domain/sample-term.md");
  });

  it("exits 0 when only gaps remain, since a gap is work to do rather than a defect", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": '---\nokf_version: "0.2"\n---\n\n# Bundle\n',
      ".specs/STATE.md": "### AD-001\n",
    });

    const result = runKnowledgeScript(root);

    expect(result.status).toBe(0);
    expect(`${result.stdout}${result.stderr}`).toContain("AD-001");
  });
});
