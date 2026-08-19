import { checkKnowledge, type KnowledgeFinding } from "./check.js";

const HEADINGS: Record<KnowledgeFinding["kind"], string> = {
  conformance: "conformance — OKF v0.2 requires a parseable frontmatter with a non-empty `type`",
  drift:
    "drift — the source moved on after the concept recorded it; re-read it and bump last_modified.\n  This compares committer dates, which a rebase moves, so an uncommitted edit does not show here\n  and a green run is not final. A source and the concept citing it are exempt while their last\n  change is the same commit; set last_modified to the day you commit rather than leaning on that.",
  naming: "naming — raw sources are named YYYY-MM-DD-<slug> so the directory sorts chronologically",
  gap: "gap — durable knowledge in .specs/ that no concept has harvested yet",
};

const rootDirectory = process.argv[2] ?? process.cwd();
const findings = checkKnowledge(rootDirectory);

if (findings.length === 0) {
  console.log(`knowledge: bundle is conformant, in sync and fully harvested in ${rootDirectory}`);
} else {
  for (const kind of ["conformance", "drift", "naming", "gap"] as const) {
    const group = findings.filter((finding) => finding.kind === kind);
    if (group.length === 0) continue;

    const write = group.some((finding) => finding.severity === "error")
      ? console.error
      : console.warn;
    write(`\nknowledge: ${HEADINGS[kind]}`);
    for (const finding of group) write(`  ${finding.file}: ${finding.message}`);
  }

  const errors = findings.filter((finding) => finding.severity === "error").length;
  const warnings = findings.length - errors;
  console.error(`\nknowledge: ${errors} error(s), ${warnings} warning(s)`);
  if (errors > 0) process.exitCode = 1;
}
