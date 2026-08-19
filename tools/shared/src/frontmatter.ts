import { parse as parseYaml } from "yaml";

/**
 * The result of reading a document's leading `---` delimited YAML block.
 *
 * Absence and malformation are different answers on purpose: a caller may tolerate a file
 * with no block at all while still refusing one whose block cannot be read.
 */
export type Frontmatter = {
  /** Whether the file opens with a `---` delimited block at all. */
  present: boolean;
  data: Record<string, unknown> | null;
  /** Why the block could not be turned into a mapping, when it could not. */
  error: string | null;
};

/**
 * Reads the frontmatter of a Markdown document.
 *
 * Three shapes fail, each with its own message: a block that is never closed, a block whose
 * YAML does not parse, and a block that parses to something other than a mapping. An empty
 * block is not a failure — it yields an empty mapping.
 */
export function readFrontmatter(source: string): Frontmatter {
  const lines = source.replace(/\r\n/g, "\n").split("\n");
  if (lines[0] !== "---") return { present: false, data: null, error: null };

  const closing = lines.indexOf("---", 1);
  if (closing === -1) {
    return { present: true, data: null, error: "the frontmatter block is never closed" };
  }

  let parsed: unknown;
  try {
    parsed = parseYaml(lines.slice(1, closing).join("\n"));
  } catch (cause) {
    const detail = cause instanceof Error ? cause.message.split("\n")[0] : String(cause);
    return { present: true, data: null, error: `unparseable YAML: ${detail}` };
  }

  if (parsed === null || parsed === undefined) return { present: true, data: {}, error: null };
  if (typeof parsed !== "object" || Array.isArray(parsed)) {
    return { present: true, data: null, error: "the frontmatter is not a YAML mapping" };
  }
  return { present: true, data: parsed as Record<string, unknown>, error: null };
}
