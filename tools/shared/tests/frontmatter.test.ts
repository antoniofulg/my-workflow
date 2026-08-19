import { describe, expect, it } from "vitest";
import { readFrontmatter } from "../src/frontmatter.js";

describe("frontmatter reader", () => {
  it("reports absence rather than an error when the document opens without a block", () => {
    expect(readFrontmatter("# Sample Term\n")).toEqual({
      present: false,
      data: null,
      error: null,
    });
  });

  it("returns the mapping of a well-formed block", () => {
    expect(readFrontmatter("---\ntype: Concept\ncount: 42\n---\n\n# Overview\n")).toEqual({
      present: true,
      data: { type: "Concept", count: 42 },
      error: null,
    });
  });

  it("reads an empty block as an empty mapping", () => {
    expect(readFrontmatter("---\n---\n")).toEqual({ present: true, data: {}, error: null });
  });

  it("reports a block that is never closed", () => {
    expect(readFrontmatter("---\ntype: Concept\n")).toEqual({
      present: true,
      data: null,
      error: "the frontmatter block is never closed",
    });
  });

  it("reports YAML that does not parse", () => {
    const result = readFrontmatter("---\ntype: Concept\n  bad: [unclosed\n---\n");

    expect(result.present).toBe(true);
    expect(result.data).toBeNull();
    expect(result.error).toContain("unparseable YAML");
  });

  it("reports a block that parses to something other than a mapping", () => {
    expect(readFrontmatter("---\n- one\n- two\n---\n")).toEqual({
      present: true,
      data: null,
      error: "the frontmatter is not a YAML mapping",
    });
  });

  it("reads a block delimited with carriage returns", () => {
    expect(readFrontmatter("---\r\ntype: Concept\r\n---\r\n")).toEqual({
      present: true,
      data: { type: "Concept" },
      error: null,
    });
  });
});
