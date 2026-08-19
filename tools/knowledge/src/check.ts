import { execFileSync } from "node:child_process";
import type { Dirent } from "node:fs";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { basename, dirname, join, relative, resolve, sep } from "node:path";
import { readFrontmatter } from "../../shared/src/frontmatter.js";

/**
 * What a finding is about.
 *
 * - `conformance`: the bundle breaks one of the three OKF v0.2 conformance rules.
 * - `drift`: a concept declares a repository source that changed after the concept recorded it.
 * - `gap`: durable knowledge accumulated in `.specs/` without a concept harvesting it.
 * - `naming`: a raw source that breaks the `YYYY-MM-DD-<slug>` convention.
 */
export type KnowledgeFindingKind = "conformance" | "drift" | "gap" | "naming";

export type KnowledgeFinding = {
  kind: KnowledgeFindingKind;
  /** `error` fails the check; `warning` is reported and tolerated. */
  severity: "error" | "warning";
  /** Offending file, relative to the scanned root, with forward slashes. */
  file: string;
  message: string;
};

export type CheckKnowledgeOptions = {
  /** Bundle directory, relative to the root. Defaults to `knowledge/wiki`. */
  bundle?: string;
  /** Raw source directory, relative to the root. Defaults to `knowledge/raw`. */
  raw?: string;
  /**
   * Resolves the last change date (`YYYY-MM-DD`) of a repository file, or null when unknown.
   * Defaults to the file's last git commit date.
   */
  sourceLastChanged?: (absolutePath: string) => string | null;
};

type GitChange = {
  commit: string;
  date: string;
};

/**
 * The bundle is `knowledge/wiki`, not `knowledge`. Everything inside it must conform, so the
 * untouched originals in `knowledge/raw` deliberately sit outside it (§11.1 admits no exception
 * for a markdown file without frontmatter).
 */
const DEFAULT_BUNDLE = join("knowledge", "wiki");
const DEFAULT_RAW = join("knowledge", "raw");
/** Everything in `raw/` sorts chronologically, so the ISO date leads the name. */
const RAW_ISO_PREFIX = /^\d{4}-\d{2}-\d{2}-\S/;
/** The `DD-MM-YYYY` form neither matches the rest of the bundle nor sorts correctly. */
const RAW_REVERSED_PREFIX = /^\d{2}-\d{2}-\d{4}-/;
/** Explains the directory itself rather than being a source. */
const RAW_EXEMPT = new Set(["README.md"]);
const SKIPPED_DIRECTORIES = new Set(["node_modules", ".git"]);
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;
const URI_SCHEME = /^[a-z][a-z0-9+.-]*:/i;
const STATE_PATH = join(".specs", "STATE.md");
const FEATURES_PATH = join(".specs", "features");

type SourceEntry = {
  id: string | null;
  resource: string | null;
  lastModified: string | null;
};

function toPosix(path: string): string {
  return path.split(sep).join("/");
}

function readSources(data: Record<string, unknown>): SourceEntry[] {
  const raw = data.sources;
  if (!Array.isArray(raw)) return [];
  const entries: SourceEntry[] = [];
  for (const item of raw) {
    if (typeof item !== "object" || item === null || Array.isArray(item)) continue;
    const entry = item as Record<string, unknown>;
    entries.push({
      id: typeof entry.id === "string" ? entry.id : null,
      resource: typeof entry.resource === "string" ? entry.resource : null,
      lastModified: typeof entry.last_modified === "string" ? entry.last_modified : null,
    });
  }
  return entries;
}

function listMarkdownFiles(directory: string): string[] {
  const files: string[] = [];
  let entries: Dirent[];
  try {
    entries = readdirSync(directory, { withFileTypes: true });
  } catch {
    return files;
  }
  for (const entry of entries) {
    if (SKIPPED_DIRECTORIES.has(entry.name)) continue;
    const full = join(directory, entry.name);
    if (entry.isDirectory()) files.push(...listMarkdownFiles(full));
    else if (entry.name.endsWith(".md")) files.push(full);
  }
  return files;
}

function listFiles(directory: string): string[] {
  const files: string[] = [];
  let entries: Dirent[];
  try {
    entries = readdirSync(directory, { withFileTypes: true });
  } catch {
    return files;
  }
  for (const entry of entries) {
    if (SKIPPED_DIRECTORIES.has(entry.name)) continue;
    const full = join(directory, entry.name);
    if (entry.isDirectory()) files.push(...listFiles(full));
    else files.push(full);
  }
  return files;
}

/**
 * Raw sources are named `YYYY-MM-DD-<slug>` so a flat directory sorts chronologically. They sit
 * outside the bundle and so have no OKF conformance to break — this is a house convention, and it
 * only warns.
 */
function checkRawNaming(rootDirectory: string, rawDirectory: string): KnowledgeFinding[] {
  const findings: KnowledgeFinding[] = [];
  for (const absoluteFile of listFiles(rawDirectory)) {
    const name = absoluteFile.slice(absoluteFile.lastIndexOf(sep) + 1);
    if (RAW_EXEMPT.has(name) || name.startsWith(".")) continue;
    if (RAW_ISO_PREFIX.test(name)) continue;

    const file = toPosix(relative(rootDirectory, absoluteFile));
    findings.push({
      kind: "naming",
      severity: "warning",
      file,
      message: RAW_REVERSED_PREFIX.test(name)
        ? "dated DD-MM-YYYY; the bundle dates everything ISO 8601, and DD-MM-YYYY does not sort"
        : "is not prefixed with its ISO date, expected YYYY-MM-DD-<slug>",
    });
  }
  return findings;
}

function gitLastChange(absolutePath: string): GitChange | null {
  try {
    const root = execFileSync("git", ["rev-parse", "--show-toplevel"], {
      cwd: dirname(absolutePath),
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
    const prefix = execFileSync("git", ["rev-parse", "--show-prefix"], {
      cwd: dirname(absolutePath),
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
    const path = toPosix(join(prefix, basename(absolutePath)));

    const blobAt = (revision: string): string | null => {
      try {
        return execFileSync("git", ["rev-parse", `${revision}:${path}`], {
          cwd: root,
          encoding: "utf8",
          stdio: ["ignore", "pipe", "ignore"],
        }).trim();
      } catch {
        return null;
      }
    };

    const lastChangeAt = (revision: string): GitChange | null => {
      const stdout = execFileSync(
        "git",
        ["log", "-1", "--format=%H%x00%cs%x00%P", revision, "--", path],
        {
          cwd: root,
          encoding: "utf8",
          stdio: ["ignore", "pipe", "ignore"],
        },
      );
      const [commit, date, parentList = ""] = stdout.trim().split("\0");
      if (commit === undefined || date === undefined || !ISO_DATE.test(date)) return null;

      const parents = parentList.split(" ").filter(Boolean);
      if (parents.length > 1) {
        const blob = blobAt(commit);
        const inherited = parents
          .filter((parent) => blob !== null && blobAt(parent) === blob)
          .map(lastChangeAt)
          .filter((change): change is GitChange => change !== null)
          .sort((left, right) => right.date.localeCompare(left.date));
        if (inherited[0] !== undefined) return inherited[0];
      }

      return { commit, date };
    };

    return lastChangeAt("HEAD");
  } catch {
    return null;
  }
}

/** §11.2 — every concept carries a non-empty `type`. */
function checkConcept(file: string, source: string): KnowledgeFinding[] {
  const { present, data, error } = readFrontmatter(source);
  const base = { kind: "conformance", severity: "error", file } as const;

  if (!present) return [{ ...base, message: "concept has no YAML frontmatter block" }];
  if (data === null) return [{ ...base, message: error ?? "unparseable frontmatter" }];

  const type = data.type;
  if (typeof type !== "string" || type.trim() === "") {
    return [{ ...base, message: "frontmatter has no non-empty `type`" }];
  }
  return [];
}

/** §8 — index files carry no frontmatter, except `okf_version` at the bundle root. */
function checkIndex(file: string, source: string, isBundleRoot: boolean): KnowledgeFinding[] {
  const { present, data, error } = readFrontmatter(source);
  if (!present) return [];

  const base = { kind: "conformance", severity: "error", file } as const;
  if (!isBundleRoot) {
    return [{ ...base, message: "only the bundle-root index.md may carry frontmatter" }];
  }
  if (data === null) return [{ ...base, message: error ?? "unparseable frontmatter" }];

  const extra = Object.keys(data).filter((key) => key !== "okf_version");
  if (extra.length > 0) {
    return [
      {
        ...base,
        message: `bundle-root index.md may only declare okf_version, found ${extra.join(", ")}`,
      },
    ];
  }
  return [];
}

/** §9 — date-grouped entries under ISO `## YYYY-MM-DD` headings, newest first. */
function checkLog(file: string, source: string): KnowledgeFinding[] {
  const findings: KnowledgeFinding[] = [];
  const base = { kind: "conformance", severity: "error", file } as const;

  if (readFrontmatter(source).present) {
    findings.push({ ...base, message: "log.md must not carry frontmatter" });
  }

  const dates: string[] = [];
  for (const line of source.replace(/\r\n/g, "\n").split("\n")) {
    if (!line.startsWith("## ")) continue;
    const heading = line.slice(3).trim();
    if (!ISO_DATE.test(heading)) {
      findings.push({ ...base, message: `date heading "${heading}" is not ISO 8601 YYYY-MM-DD` });
      continue;
    }
    dates.push(heading);
  }

  for (let index = 1; index < dates.length; index += 1) {
    const previous = dates[index - 1];
    const current = dates[index];
    if (previous !== undefined && current !== undefined && current > previous) {
      findings.push({
        ...base,
        message: `${current} appears after ${previous}; entries run newest first`,
      });
    }
  }
  return findings;
}

/**
 * A concept's recorded `last_modified` against what the repository says. `sources[].last_modified`
 * is a recency signal for the *source*, distinct from `generated.at`, which records when the
 * concept itself was written — so comparing the two detects a source that moved on without the
 * concept following it.
 */
function checkDrift(
  file: string,
  absoluteFile: string,
  rootDirectory: string,
  bundleDirectory: string,
  data: Record<string, unknown>,
  sourceLastChanged: (absolutePath: string, conceptPath: string) => string | null,
): KnowledgeFinding[] {
  const findings: KnowledgeFinding[] = [];

  for (const entry of readSources(data)) {
    const { resource, lastModified } = entry;
    // A scope descriptor or an external URL is not a path we can stat (§5.1, §6.2).
    if (resource === null || URI_SCHEME.test(resource)) continue;

    const absoluteSource = resource.startsWith("/")
      ? join(bundleDirectory, resource.slice(1))
      : resolve(dirname(absoluteFile), resource);

    // Only repository files are checkable; anything above the root is out of scope.
    const inside = relative(rootDirectory, absoluteSource);
    if (inside.startsWith("..") || inside === "") continue;

    if (!existsSync(absoluteSource)) {
      findings.push({
        kind: "drift",
        severity: "warning",
        file,
        message: `source "${resource}" does not exist`,
      });
      continue;
    }

    if (lastModified === null) continue;
    if (!ISO_DATE.test(lastModified)) {
      findings.push({
        kind: "conformance",
        severity: "error",
        file,
        message: `source "${resource}" has last_modified "${lastModified}", not YYYY-MM-DD`,
      });
      continue;
    }

    const changed = sourceLastChanged(absoluteSource, absoluteFile);
    if (changed !== null && changed > lastModified) {
      findings.push({
        kind: "drift",
        severity: "error",
        file,
        message: `source "${resource}" changed on ${changed}, concept records ${lastModified}`,
      });
    }
  }
  return findings;
}

/** Decisions and verified features that accumulated in `.specs/` without a concept harvesting them. */
function checkGaps(
  rootDirectory: string,
  harvestedIds: Set<string>,
  harvestedPaths: Set<string>,
): KnowledgeFinding[] {
  const findings: KnowledgeFinding[] = [];

  const statePath = join(rootDirectory, STATE_PATH);
  if (existsSync(statePath)) {
    const state = readFileSync(statePath, "utf8");
    for (const match of state.matchAll(/^### (AD-\d+)\s*$/gm)) {
      const label = match[1];
      if (label === undefined) continue;
      if (harvestedIds.has(`state-${label.toLowerCase()}`)) continue;
      findings.push({
        kind: "gap",
        severity: "warning",
        file: toPosix(STATE_PATH),
        message: `${label} has no concept; expected a source entry with id "state-${label.toLowerCase()}"`,
      });
    }
  }

  const featuresPath = join(rootDirectory, FEATURES_PATH);
  let features: Dirent[];
  try {
    features = readdirSync(featuresPath, { withFileTypes: true });
  } catch {
    return findings;
  }
  for (const feature of features) {
    if (!feature.isDirectory()) continue;
    const validation = join(FEATURES_PATH, feature.name, "validation.md");
    if (!existsSync(join(rootDirectory, validation))) continue;
    if (harvestedPaths.has(toPosix(validation))) continue;
    findings.push({
      kind: "gap",
      severity: "warning",
      file: toPosix(validation),
      message: `feature "${feature.name}" is verified but no concept cites its validation`,
    });
  }
  return findings;
}

/**
 * Checks the knowledge bundle for OKF v0.2 conformance, for concepts that drifted from the
 * repository sources they derive from, and for durable knowledge in `.specs/` that no concept has
 * harvested yet.
 */
export function checkKnowledge(
  rootDirectory: string,
  options: CheckKnowledgeOptions = {},
): KnowledgeFinding[] {
  const bundleDirectory = join(rootDirectory, options.bundle ?? DEFAULT_BUNDLE);
  const rawDirectory = join(rootDirectory, options.raw ?? DEFAULT_RAW);

  // Concepts cite the same handful of files over and over, and the default resolver spawns a git
  // process per call. Memoising keeps a bundle of any size at one lookup per distinct path.
  const cache = new Map<string, string | null>();
  const gitCache = new Map<string, GitChange | null>();
  const sourceLastChanged = (absolutePath: string, conceptPath: string): string | null => {
    if (options.sourceLastChanged !== undefined) {
      if (cache.has(absolutePath)) return cache.get(absolutePath) ?? null;
      const resolved = options.sourceLastChanged(absolutePath);
      cache.set(absolutePath, resolved);
      return resolved;
    }

    const lastChange = (path: string): GitChange | null => {
      if (gitCache.has(path)) return gitCache.get(path) ?? null;
      const resolved = gitLastChange(path);
      gitCache.set(path, resolved);
      return resolved;
    };
    const sourceChange = lastChange(absolutePath);
    const conceptChange = lastChange(conceptPath);
    if (sourceChange?.commit === conceptChange?.commit) return null;
    return sourceChange?.date ?? null;
  };

  const findings: KnowledgeFinding[] = [];
  const harvestedIds = new Set<string>();
  const harvestedPaths = new Set<string>();

  for (const absoluteFile of listMarkdownFiles(bundleDirectory)) {
    const file = toPosix(relative(rootDirectory, absoluteFile));
    const name = absoluteFile.slice(absoluteFile.lastIndexOf(sep) + 1);
    const source = readFileSync(absoluteFile, "utf8");

    if (name === "index.md") {
      const isBundleRoot = dirname(absoluteFile) === bundleDirectory;
      findings.push(...checkIndex(file, source, isBundleRoot));
      continue;
    }
    if (name === "log.md") {
      findings.push(...checkLog(file, source));
      continue;
    }

    const conformance = checkConcept(file, source);
    findings.push(...conformance);
    if (conformance.length > 0) continue;

    const data = readFrontmatter(source).data;
    if (data === null) continue;

    for (const entry of readSources(data)) {
      if (entry.resource === null || URI_SCHEME.test(entry.resource)) continue;
      const absoluteSource = entry.resource.startsWith("/")
        ? join(bundleDirectory, entry.resource.slice(1))
        : resolve(dirname(absoluteFile), entry.resource);
      const source = toPosix(relative(rootDirectory, absoluteSource));
      harvestedPaths.add(source);
      // An id only marks a decision harvested when it labels the ledger the decision lives in.
      // Without that pairing, any concept citing an unrelated source as "state-ad-001" would
      // silently close the gap for a decision nobody read.
      if (entry.id !== null && source === toPosix(STATE_PATH)) {
        harvestedIds.add(entry.id.toLowerCase());
      }
    }

    findings.push(
      ...checkDrift(file, absoluteFile, rootDirectory, bundleDirectory, data, sourceLastChanged),
    );
  }

  findings.push(...checkRawNaming(rootDirectory, rawDirectory));
  findings.push(...checkGaps(rootDirectory, harvestedIds, harvestedPaths));
  return findings;
}
