import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { checkKnowledge, type KnowledgeFinding } from "../src/check.js";

const createdRoots: string[] = [];

function makeBundle(files: Record<string, string>): string {
  const root = mkdtempSync(join(tmpdir(), "okf-knowledge-"));
  createdRoots.push(root);
  for (const [path, content] of Object.entries(files)) {
    const target = join(root, path);
    mkdirSync(dirname(target), { recursive: true });
    writeFileSync(target, content, "utf8");
  }
  return root;
}

/** Pins the "source last changed" clock so drift is asserted without a git repository. */
function frozenClock(date: string) {
  return () => date;
}

/**
 * `committerDate` defaults to `date` because the two coincide outside a rebase. Passing them apart
 * is how a rewritten history is reproduced: the author date is the one freshness reads.
 */
function git(root: string, args: string[], date: string, committerDate: string = date): void {
  execFileSync("git", args, {
    cwd: root,
    env: {
      ...process.env,
      GIT_AUTHOR_DATE: `${date}T12:00:00-03:00`,
      GIT_COMMITTER_DATE: `${committerDate}T12:00:00-03:00`,
    },
    stdio: "ignore",
  });
}

const ROOT_INDEX = '---\nokf_version: "0.2"\n---\n\n# Knowledge Bundle\n';
const LOG = "# Update log\n\n## 2026-08-08\n\n* **Initialization**: Created the bundle.\n";

function kinds(findings: KnowledgeFinding[]): string[] {
  return findings.map((finding) => finding.kind);
}

afterEach(() => {
  for (const root of createdRoots.splice(0)) {
    rmSync(root, { recursive: true, force: true });
  }
});

describe("OKF v0.2 conformance", () => {
  it("accepts a bundle whose only concept carries just a type", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/log.md": LOG,
      "knowledge/wiki/domain/sample-term.md": "---\ntype: Concept\n---\n\n# Overview\n",
    });

    expect(checkKnowledge(root)).toEqual([]);
  });

  it("flags a concept with no frontmatter block", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/domain/sample-term.md": "# Sample Term\n",
    });

    const findings = checkKnowledge(root);

    expect(findings).toHaveLength(1);
    expect(findings[0]?.kind).toBe("conformance");
    expect(findings[0]?.file).toBe("knowledge/wiki/domain/sample-term.md");
    expect(findings[0]?.message).toContain("no YAML frontmatter");
  });

  it("flags a concept whose frontmatter has no non-empty type", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/domain/a.md": "---\ntype: ''\ntitle: A\n---\n",
      "knowledge/wiki/domain/b.md": "---\ntitle: B\n---\n",
    });

    const findings = checkKnowledge(root);

    expect(findings).toHaveLength(2);
    expect(findings.every((finding) => finding.message.includes("`type`"))).toBe(true);
  });

  it("flags unparseable frontmatter", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/domain/a.md": "---\ntype: Concept\n  bad: [unclosed\n---\n",
    });

    const findings = checkKnowledge(root);

    expect(findings).toHaveLength(1);
    expect(findings[0]?.message).toContain("unparseable YAML");
  });

  it("tolerates unknown types and extra frontmatter keys", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/domain/a.md": "---\ntype: Something Nobody Registered\nwhatever: 42\n---\n",
    });

    expect(checkKnowledge(root)).toEqual([]);
  });

  it("never scans what sits outside the bundle", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      // The operating schema documents the bundle rather than belonging to it.
      "knowledge/AGENTS.md": "# Operating schema\n\nNo frontmatter here on purpose.\n",
      // Untouched originals stay raw markdown; §11.1 would reject them inside the bundle.
      "knowledge/raw/2026-08-02-brainstorm.md": "# Brainstorm\n\nA transcript, verbatim.\n",
    });

    expect(checkKnowledge(root)).toEqual([]);
  });

  it("accepts a concept sourced from an untouched original in raw/", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/raw/2026-08-02-brainstorm.md": "# Brainstorm\n",
      "knowledge/wiki/research/sample-note.md": [
        "---",
        "type: Research Note",
        "sources:",
        "  - id: brainstorm",
        "    resource: ../../raw/2026-08-02-brainstorm.md",
        "    last_modified: 2026-08-08",
        "---",
        "",
      ].join("\n"),
    });

    expect(checkKnowledge(root, { sourceLastChanged: frozenClock("2026-08-08") })).toEqual([]);
  });

  it("allows okf_version at the bundle root but rejects any other key there", () => {
    const clean = makeBundle({ "knowledge/wiki/index.md": ROOT_INDEX });
    expect(checkKnowledge(clean)).toEqual([]);

    const dirty = makeBundle({
      "knowledge/wiki/index.md": '---\nokf_version: "0.2"\ntype: Index\n---\n',
    });
    const findings = checkKnowledge(dirty);

    expect(findings).toHaveLength(1);
    expect(findings[0]?.message).toContain("only declare okf_version");
  });

  it("rejects frontmatter in a subdirectory index", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/domain/index.md": "---\ntype: Index\n---\n\n# Domain\n",
    });

    const findings = checkKnowledge(root);

    expect(findings).toHaveLength(1);
    expect(findings[0]?.file).toBe("knowledge/wiki/domain/index.md");
    expect(findings[0]?.message).toContain("only the bundle-root index.md");
  });

  it("rejects a log heading that is not an ISO date, and dates out of newest-first order", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/log.md": "# Update log\n\n## August 8\n\n## 2026-08-01\n\n## 2026-08-08\n",
    });

    const messages = checkKnowledge(root).map((finding) => finding.message);

    expect(messages).toContain('date heading "August 8" is not ISO 8601 YYYY-MM-DD');
    expect(messages).toContain("2026-08-08 appears after 2026-08-01; entries run newest first");
  });
});

describe("drift against repository sources", () => {
  const concept = (lastModified: string) =>
    [
      "---",
      "type: Decision",
      "sources:",
      "  - id: state-ad-001",
      "    resource: ../../../.specs/STATE.md",
      `    last_modified: ${lastModified}`,
      "---",
      "",
      "# Overview",
      "",
    ].join("\n");

  it("flags a concept whose source changed after the recorded date", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/decisions/ad-001.md": concept("2026-08-01"),
      ".specs/STATE.md": "### AD-001\n",
    });

    const findings = checkKnowledge(root, { sourceLastChanged: frozenClock("2026-08-08") });

    expect(kinds(findings)).toEqual(["drift"]);
    expect(findings[0]?.severity).toBe("error");
    expect(findings[0]?.message).toContain("changed on 2026-08-08, concept records 2026-08-01");
  });

  it("stays quiet when the concept is at least as recent as its source", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/decisions/ad-001.md": concept("2026-08-08"),
      ".specs/STATE.md": "### AD-001\n",
    });

    expect(checkKnowledge(root, { sourceLastChanged: frozenClock("2026-08-08") })).toEqual([]);
  });

  it("stays quiet when a squash commit carries the source and its concept together", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/research/source.md": [
        "---",
        "type: Research Note",
        "sources:",
        "  - id: source",
        "    resource: ../../../docs/source.md",
        "    last_modified: 2026-08-08",
        "---",
        "",
      ].join("\n"),
      "docs/source.md": "# Source\n",
    });
    git(root, ["init", "-b", "main"], "2026-08-09");
    git(root, ["config", "user.name", "Knowledge Test"], "2026-08-09");
    git(root, ["config", "user.email", "knowledge@example.test"], "2026-08-09");
    git(root, ["add", "."], "2026-08-09");
    git(root, ["commit", "-m", "squash source and concept"], "2026-08-09");

    expect(checkKnowledge(root)).toEqual([]);
  });

  it("stays quiet when a rebase rewrote the source committer date but not its author date", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "docs/source.md": "# Source\n",
    });
    git(root, ["init", "-b", "main"], "2026-08-01");
    git(root, ["config", "user.name", "Knowledge Test"], "2026-08-01");
    git(root, ["config", "user.email", "knowledge@example.test"], "2026-08-01");
    git(root, ["add", "."], "2026-08-01");
    git(root, ["commit", "-m", "source"], "2026-08-01", "2026-08-20");

    mkdirSync(join(root, "knowledge/wiki/research"), { recursive: true });
    writeFileSync(
      join(root, "knowledge/wiki/research/source.md"),
      [
        "---",
        "type: Research Note",
        "sources:",
        "  - id: source",
        "    resource: ../../../docs/source.md",
        "    last_modified: 2026-08-08",
        "---",
        "",
      ].join("\n"),
      "utf8",
    );
    git(root, ["add", "."], "2026-08-08");
    git(root, ["commit", "-m", "harvest source"], "2026-08-08");

    expect(checkKnowledge(root)).toEqual([]);
  });

  it("does not advance a source date when a merge keeps a parent blob", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/research/source.md": [
        "---",
        "type: Research Note",
        "sources:",
        "  - id: source",
        "    resource: ../../../docs/source.md",
        "    last_modified: 2026-08-01",
        "---",
        "",
      ].join("\n"),
      "docs/source.md": "# Source\n",
    });
    git(root, ["init", "-b", "main"], "2026-08-01");
    git(root, ["config", "user.name", "Knowledge Test"], "2026-08-01");
    git(root, ["config", "user.email", "knowledge@example.test"], "2026-08-01");
    git(root, ["add", "."], "2026-08-01");
    git(root, ["commit", "-m", "base"], "2026-08-01");
    git(root, ["switch", "-c", "source-mode"], "2026-08-02");
    writeFileSync(join(root, "branch.txt"), "branch\n", "utf8");
    git(root, ["add", "."], "2026-08-02");
    git(root, ["commit", "-m", "branch"], "2026-08-02");
    git(root, ["switch", "main"], "2026-08-03");
    writeFileSync(join(root, "main.txt"), "main\n", "utf8");
    git(root, ["add", "."], "2026-08-03");
    git(root, ["commit", "-m", "main"], "2026-08-03");
    git(root, ["merge", "--no-commit", "--no-ff", "source-mode"], "2026-08-04");
    git(root, ["update-index", "--chmod=+x", "docs/source.md"], "2026-08-04");
    git(root, ["commit", "-m", "merge"], "2026-08-04");

    expect(checkKnowledge(root)).toEqual([]);
  });

  it("counts a merge resolution whose source blob differs from every parent", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/research/source.md": [
        "---",
        "type: Research Note",
        "sources:",
        "  - id: source",
        "    resource: ../../../docs/source.md",
        "    last_modified: 2026-08-03",
        "---",
        "",
      ].join("\n"),
      "docs/source.md": "# Source\n\nbase\n",
    });
    git(root, ["init", "-b", "main"], "2026-08-01");
    git(root, ["config", "user.name", "Knowledge Test"], "2026-08-01");
    git(root, ["config", "user.email", "knowledge@example.test"], "2026-08-01");
    git(root, ["add", "."], "2026-08-01");
    git(root, ["commit", "-m", "base"], "2026-08-01");
    git(root, ["switch", "-c", "source"], "2026-08-02");
    writeFileSync(join(root, "docs/source.md"), "# Source\n\nbranch\n", "utf8");
    git(root, ["add", "."], "2026-08-02");
    git(root, ["commit", "-m", "source"], "2026-08-02");
    git(root, ["switch", "main"], "2026-08-03");
    writeFileSync(join(root, "main.txt"), "main\n", "utf8");
    git(root, ["add", "."], "2026-08-03");
    git(root, ["commit", "-m", "main"], "2026-08-03");
    git(root, ["merge", "--no-commit", "--no-ff", "source"], "2026-08-04");
    writeFileSync(join(root, "docs/source.md"), "# Source\n\nresolved\n", "utf8");
    git(root, ["add", "docs/source.md"], "2026-08-04");
    git(root, ["commit", "-m", "merge"], "2026-08-04");

    const findings = checkKnowledge(root);

    expect(kinds(findings)).toEqual(["drift"]);
    expect(findings[0]?.message).toContain("changed on 2026-08-04, concept records 2026-08-03");
  }, 15_000);

  it("warns instead of failing when a declared source does not exist", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/decisions/ad-001.md": concept("2026-08-08"),
    });

    const findings = checkKnowledge(root, { sourceLastChanged: frozenClock("2026-08-08") });

    expect(findings).toHaveLength(1);
    expect(findings[0]?.kind).toBe("drift");
    expect(findings[0]?.severity).toBe("warning");
    expect(findings[0]?.message).toContain("does not exist");
  });

  it("ignores external URLs and scope descriptors, which are not paths", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/research/market.md": [
        "---",
        "type: Research Note",
        "sources:",
        "  - id: ibge",
        "    resource: https://example.com/research",
        "    last_modified: 2026-01-01",
        "---",
        "",
      ].join("\n"),
    });

    expect(checkKnowledge(root, { sourceLastChanged: frozenClock("2026-08-08") })).toEqual([]);
  });

  it("rejects a last_modified that is not YYYY-MM-DD", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/decisions/ad-001.md": concept("08/08/2026"),
      ".specs/STATE.md": "### AD-001\n",
    });

    const findings = checkKnowledge(root, { sourceLastChanged: frozenClock("2026-08-08") });

    expect(kinds(findings)).toEqual(["conformance"]);
    expect(findings[0]?.message).toContain("not YYYY-MM-DD");
  });

  it("resolves a bundle-absolute source against the bundle root", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/references/interview.md": "---\ntype: Source Summary\n---\n",
      "knowledge/wiki/research/pain.md": [
        "---",
        "type: Research Note",
        "sources:",
        "  - id: interview",
        "    resource: /references/interview.md",
        "    last_modified: 2026-08-01",
        "---",
        "",
      ].join("\n"),
    });

    const findings = checkKnowledge(root, { sourceLastChanged: frozenClock("2026-08-08") });

    expect(kinds(findings)).toEqual(["drift"]);
    expect(findings[0]?.message).toContain("/references/interview.md");
  });
});

describe("raw source naming", () => {
  it("accepts an ISO-dated source and ignores the directory README", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/raw/README.md": "# Raw sources\n",
      "knowledge/raw/2026-08-02-interview-notes.md": "# Interview\n",
      "knowledge/raw/2026-07-15-guia-de-marca.pdf": "%PDF\n",
    });

    expect(checkKnowledge(root)).toEqual([]);
  });

  it("warns about an undated source", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/raw/brainstorm.md": "# Brainstorm\n",
    });

    const findings = checkKnowledge(root);

    expect(kinds(findings)).toEqual(["naming"]);
    expect(findings[0]?.severity).toBe("warning");
    expect(findings[0]?.message).toContain("YYYY-MM-DD-<slug>");
  });

  it("names DD-MM-YYYY specifically, since it is the mistake worth explaining", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/raw/23-01-2026-brainstorm.md": "# Brainstorm\n",
    });

    const findings = checkKnowledge(root);

    expect(kinds(findings)).toEqual(["naming"]);
    expect(findings[0]?.message).toContain("does not sort");
  });
});

describe("gaps in what has been harvested", () => {
  it("reports every AD-NNN with no concept citing it", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      ".specs/STATE.md":
        "# STATE\n\n### AD-001\n- **Decision**: a\n\n### AD-002\n- **Decision**: b\n",
    });

    const findings = checkKnowledge(root);

    expect(kinds(findings)).toEqual(["gap", "gap"]);
    expect(findings.every((finding) => finding.severity === "warning")).toBe(true);
    expect(findings[0]?.message).toContain("AD-001");
    expect(findings[1]?.message).toContain("AD-002");
  });

  it("counts an AD as harvested once a concept carries its source id", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/decisions/ad-001.md": [
        "---",
        "type: Decision",
        "sources:",
        "  - id: state-ad-001",
        "    resource: ../../../.specs/STATE.md",
        "---",
        "",
      ].join("\n"),
      ".specs/STATE.md": "### AD-001\n\n### AD-002\n",
    });

    const findings = checkKnowledge(root);

    expect(findings).toHaveLength(1);
    expect(findings[0]?.message).toContain("AD-002");
  });

  it("fails when two ledger headings share an AD-NNN label", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      ".specs/STATE.md": "### AD-060\n\n### AD-060\n",
    });

    const findings = checkKnowledge(root);

    expect(findings).toEqual([
      expect.objectContaining({
        kind: "gap",
        severity: "warning",
        file: ".specs/STATE.md",
        message: expect.stringContaining("AD-060"),
      }),
      expect.objectContaining({
        kind: "conformance",
        severity: "error",
        file: ".specs/STATE.md",
        message: "AD-060 appears more than once",
      }),
    ]);
  });

  it("fails when two spine headings share an AD-N label", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "docs/architecture/ARCHITECTURE-SPINE.md": "### AD-3 — one\n\n### AD-3 — two\n",
    });

    const findings = checkKnowledge(root);

    expect(findings).toEqual([
      expect.objectContaining({
        kind: "conformance",
        severity: "error",
        file: "docs/architecture/ARCHITECTURE-SPINE.md",
        message: "AD-3 appears more than once",
      }),
    ]);
  });

  it("ignores a matching id that labels a source other than the ledger", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/raw/2026-08-02-notes.md": "# Notes\n",
      "knowledge/wiki/research/note.md": [
        "---",
        "type: Research Note",
        "sources:",
        "  - id: state-ad-001",
        "    resource: ../../raw/2026-08-02-notes.md",
        "---",
        "",
      ].join("\n"),
      ".specs/STATE.md": "### AD-001\n",
    });

    const findings = checkKnowledge(root);

    expect(kinds(findings)).toEqual(["gap"]);
    expect(findings[0]?.message).toContain("AD-001");
  });

  it("reports a verified feature that no concept cites", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      ".specs/features/sample-feature/validation.md": "# Validation\n",
    });

    const findings = checkKnowledge(root);

    expect(kinds(findings)).toEqual(["gap"]);
    expect(findings[0]?.file).toBe(".specs/features/sample-feature/validation.md");
  });

  it("stays quiet once a concept cites the feature validation", () => {
    const root = makeBundle({
      "knowledge/wiki/index.md": ROOT_INDEX,
      "knowledge/wiki/product/sample-requirement.md": [
        "---",
        "type: Requirement",
        "sources:",
        "  - id: landing-validation",
        "    resource: ../../../.specs/features/sample-feature/validation.md",
        "    last_modified: 2026-08-08",
        "---",
        "",
      ].join("\n"),
      ".specs/features/sample-feature/validation.md": "# Validation\n",
    });

    expect(checkKnowledge(root, { sourceLastChanged: frozenClock("2026-08-08") })).toEqual([]);
  });

  it("reports nothing about .specs when the project has none", () => {
    const root = makeBundle({ "knowledge/wiki/index.md": ROOT_INDEX });

    expect(checkKnowledge(root)).toEqual([]);
  });
});
