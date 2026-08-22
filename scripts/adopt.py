#!/usr/bin/env python3
"""Copy this workflow pack into a target project. Stdlib only."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

STENCIL = "<!-- product-stencil:"

WORKFLOW_GITIGNORE_ENTRIES = (
    ".deep-review/*",
    "!.deep-review/learnings.md",
    ".specs/features/",
)

COPY_PATHS = [
    "docs/guidelines",
    "docs/workflow",
    "knowledge/AGENTS.md",
    "knowledge/raw/README.md",
    "knowledge/wiki",
    "tools/knowledge",
    "tools/shared/src/frontmatter.ts",
    "tools/shared/tests/frontmatter.test.ts",
    "tools/ad-index.py",
    ".agents/skills/tlc-spec-driven",
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
COPY_MISSING_PATHS = ["docs/qa/README.md"]

AGENT_PATHS = [
    ".cursor/agents",
    ".claude/agents",
    ".codex/agents",
]


def die(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def copy_tree(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest, symlinks=True)
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


def merge_gitignore(dest: Path) -> None:
    target = dest / ".gitignore"
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    lines = existing.splitlines()
    managed = [line for line in lines if line in WORKFLOW_GITIGNORE_ENTRIES]
    if managed == list(WORKFLOW_GITIGNORE_ENTRIES):
        return

    kept = [line for line in lines if line not in WORKFLOW_GITIGNORE_ENTRIES]
    merged = "\n".join(kept).rstrip()
    if merged:
        merged += "\n"
    merged += "\n".join(WORKFLOW_GITIGNORE_ENTRIES) + "\n"
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


def main(argv: list[str]) -> None:
    if len(argv) != 2:
        die("usage: adopt.py <target-directory>")
    dest = Path(argv[1]).resolve()
    src = Path(__file__).resolve().parent.parent
    if not dest.is_dir():
        die(f"not a directory: {dest}")
    adopt_agents(src, dest)
    for rel in COPY_PATHS:
        origin = src / rel
        if not origin.exists():
            continue
        copy_tree(origin, dest / rel)
    for rel in COPY_MISSING_PATHS:
        origin = src / rel
        if not origin.exists():
            continue
        copy_missing(origin, dest / rel)
    copy_agents(src, dest)
    merge_gitignore(dest)
    write_claude(dest)
    link_claude_skills(dest)
    print(f"adopted workflow into {dest}")


if __name__ == "__main__":
    main(sys.argv)
