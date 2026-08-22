#!/usr/bin/env python3
"""Copy this workflow pack into a target project. Stdlib only."""

from __future__ import annotations

import re
import shlex
import shutil
import sys
from pathlib import Path

STENCIL = "<!-- product-stencil:"

WORKFLOW_GITIGNORE_ENTRIES = (
    ".deep-review/*",
    "!.deep-review/learnings.md",
    ".specs/features/",
    "graft/",
)

WORKFLOW_SEARCHIGNORE_ENTRIES = (
    "!graft/",
    "graft/.cache/",
    "graft/.graph/",
)

WORKFLOW_DOCS = [
    "docs/workflow/README.md",
    "docs/workflow/decisions.md",
    "docs/workflow/guidelines.md",
    "docs/workflow/loop.md",
    "docs/workflow/purpose.md",
    "docs/workflow/reviews.md",
]

COPY_PATHS = [
    "docs/guidelines",
    *WORKFLOW_DOCS,
    "knowledge/AGENTS.md",
    "knowledge/raw/README.md",
    "knowledge/wiki",
    "tools/knowledge",
    "tools/shared/src/frontmatter.ts",
    "tools/shared/tests/frontmatter.test.ts",
    ".agents/skills/tlc-spec-driven",
    ".agents/skills/deep-review",
    ".agents/skills/ponytail",
    ".agents/skills/ponytail-audit",
    ".agents/skills/ponytail-debt",
    ".agents/skills/ponytail-gain",
    ".agents/skills/ponytail-help",
    ".agents/skills/ponytail-review",
    ".agents/skills/qa-plan",
    ".agents/skills/qa-execute",
    ".agents/skills/autonomous",
    ".agents/skills/workflow-config",
]

# The profile is a template. A consuming project's existing profile is product-owned and must
# survive re-adoption.
COPY_MISSING_PATHS = ["docs/qa/README.md", "tools/ad-index.py"]

AGENT_PATHS = [
    ".cursor/agents",
    ".claude/agents",
    ".codex/agents",
]


GLOBAL_CLAUDE_ROOT = re.compile(
    r"(?:\$\(HOME\)|\$\{HOME\}|\$HOME|~)/\.claude(?:/|$)"
)


def die(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def copy_tree(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(
            src,
            dest,
            symlinks=True,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def copy_missing(src: Path, dest: Path) -> None:
    if src.is_dir():
        if not dest.exists():
            copy_tree(src, dest)
            return
        if not dest.is_dir():
            return
        for child in src.iterdir():
            copy_missing(child, dest / child.name)
        return
    if dest.exists() or dest.is_symlink():
        return
    copy_tree(src, dest)


def product_section(text: str) -> str:
    start = text.find("## What this project is")
    if start < 0:
        return ""
    rest = text[start:]
    nxt = rest.find("\n## ", 1)
    return rest if nxt < 0 else rest[:nxt]


def adopt_agents(src: Path, dest: Path) -> None:
    incoming = (src / "AGENTS.md").read_text(encoding="utf-8")
    target = dest / "AGENTS.md"
    if not target.exists():
        target.write_text(incoming, encoding="utf-8")
        return
    existing = target.read_text(encoding="utf-8")
    section = product_section(existing)
    if section and STENCIL not in section:
        die(
            f"refusing to overwrite {target}: What this project is is not the stencil. "
            "Merge the loop by hand."
        )
    target.write_text(incoming, encoding="utf-8")


def write_claude(dest: Path) -> None:
    link = dest / "CLAUDE.md"
    if link.exists() or link.is_symlink():
        link.unlink()
    link.write_text("@AGENTS.md\n", encoding="utf-8")


def copy_agents(src: Path, dest: Path) -> None:
    for rel in AGENT_PATHS:
        origin = src / rel
        target = dest / rel
        if not origin.exists():
            continue
        copy_missing(origin, target)


def remove_source_only_pack_link(dest: Path) -> None:
    tour = dest / "docs/workflow/README.md"
    pack = dest / "docs/workflow/pack.md"
    if not tour.is_file() or pack.exists() or pack.is_symlink():
        return
    lines = tour.read_text(encoding="utf-8").splitlines(keepends=True)
    filtered = [line for line in lines if "(pack.md)" not in line]
    if filtered != lines:
        tour.write_text("".join(filtered), encoding="utf-8")


def merge_ignore_file(dest: Path, filename: str, entries: tuple[str, ...]) -> None:
    target = dest / filename
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    lines = existing.splitlines()
    managed = [line for line in lines if line in entries]
    if managed == list(entries):
        return

    kept = [line for line in lines if line not in entries]
    merged = "\n".join(kept).rstrip()
    if merged:
        merged += "\n"
    merged += "\n".join(entries) + "\n"
    target.write_text(merged, encoding="utf-8")


def link_claude_skills(dest: Path) -> None:
    claude_skills = dest / ".claude" / "skills"
    claude_skills.mkdir(parents=True, exist_ok=True)
    agents = dest / ".agents" / "skills"
    if not agents.is_dir():
        return
    for skill in agents.iterdir():
        if not skill.is_dir():
            continue
        pointer = claude_skills / skill.name
        if pointer.exists() or pointer.is_symlink():
            pointer.unlink()
        pointer.symlink_to(Path("../../.agents/skills") / skill.name)


def reject_global_tlc_paths(dest: Path) -> None:
    makefile = dest / "Makefile"
    if not makefile.is_file():
        return
    for line_number, line in enumerate(
        makefile.read_text(encoding="utf-8").splitlines(), start=1
    ):
        match = GLOBAL_CLAUDE_ROOT.search(line)
        if match:
            die(
                f"refusing adoption: {makefile}:{line_number} uses machine-global "
                f"TLC path {match.group(0)!r}; use "
                ".agents/skills/tlc-spec-driven/scripts/... in the target Makefile"
            )


def main(argv: list[str]) -> None:
    args = argv[1:]
    skip_agents = args[:1] == ["--skip-agents"]
    if skip_agents:
        args = args[1:]
    if len(args) != 1:
        die("usage: adopt.py [--skip-agents] <target-directory>")
    dest = Path(args[0]).resolve()
    src = Path(__file__).resolve().parent.parent
    if not dest.is_dir():
        die(f"not a directory: {dest}")
    reject_global_tlc_paths(dest)
    if not skip_agents:
        adopt_agents(src, dest)
    for rel in COPY_PATHS:
        origin = src / rel
        if not origin.exists():
            continue
        copy_tree(origin, dest / rel)
    remove_source_only_pack_link(dest)
    for rel in COPY_MISSING_PATHS:
        origin = src / rel
        if not origin.exists():
            continue
        copy_missing(origin, dest / rel)
    copy_agents(src, dest)
    merge_ignore_file(dest, ".gitignore", WORKFLOW_GITIGNORE_ENTRIES)
    merge_ignore_file(dest, ".ignore", WORKFLOW_SEARCHIGNORE_ENTRIES)
    if not skip_agents:
        write_claude(dest)
    link_claude_skills(dest)
    print(f"adopted workflow into {dest}")
    installer = src / "scripts" / "install_security_skills.py"
    command = shlex.join(("python3", str(installer), str(dest), "--yes"))
    print("Security skills are external dependencies, not bundled skills.")
    print(f"After explicit authorization, run exactly: {command}")
    print("Until then, the SECURITY.md security gate remains uncovered.")


if __name__ == "__main__":
    main(sys.argv)
