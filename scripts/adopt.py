#!/usr/bin/env python3
"""Copy this workflow pack into a target project. Stdlib only."""

from __future__ import annotations

import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

STENCIL = "<!-- product-stencil:"

WORKFLOW_GITIGNORE_ENTRIES = (
    ".my-workflow.toml",
    ".claude/agents/",
    ".codex/agents/",
    ".cursor/agents/",
    "!.deep-review/",
    ".deep-review/*",
    "!.deep-review/learnings.md",
    "graft/",
)

LEGACY_WORKFLOW_GITIGNORE_ENTRIES = (".specs/features/",)

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
    "tools/knowledge/src",
    "tools/qa_parallel_pilot.py",
    "tools/orca_assisted_probe.py",
    "tools/shared/src/frontmatter.ts",
    ".agents/skills/workflow-spec-driven",
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
COPY_MISSING_PATHS = [
    "docs/qa/README.md",
    "tools/ad-index.py",
    ".my-workflow.toml.example",
    "templates/agents",
]

OBSOLETE_MANAGED_PATHS = (
    ".agents/skills/tlc-spec-driven",
    ".claude/skills/tlc-spec-driven",
)


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


def remove_obsolete_managed_paths(dest: Path) -> None:
    for relative in OBSOLETE_MANAGED_PATHS:
        path = dest / relative
        if path.is_symlink() or path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)


def _reject_unsafe_destination(
    root: Path, destination: Path, kind: str, label: str
) -> None:
    """Reject redirects and non-regular nodes before adoption can write."""
    relative = destination.relative_to(root).as_posix()
    current = root
    for component in Path(relative).parts:
        current /= component
        if current.is_symlink():
            relation = "destination" if current == destination else "parent"
            die(
                f"refusing adoption: {label} {relation} {current} must not be a symlink"
            )
        if current != destination and current.exists() and not current.is_dir():
            die(f"refusing adoption: {label} parent {current} must be a directory")
    if not destination.exists():
        return
    if kind == "directory" and not destination.is_dir():
        die(f"refusing adoption: {label} destination {destination} must be a directory")
    if kind == "file" and not destination.is_file():
        die(f"refusing adoption: {label} destination {destination} must be a file")


def _source_nodes(source: Path) -> list[tuple[Path, str]]:
    nodes = [(source, "directory" if source.is_dir() else "file")]
    if not source.is_dir():
        return nodes
    for child in source.rglob("*"):
        if "__pycache__" in child.parts or child.suffix == ".pyc":
            continue
        nodes.append((child, "directory" if child.is_dir() else "file"))
    return nodes


def _preflight_adoption_destinations(src: Path, dest: Path, skip_agents: bool) -> None:
    """Validate every path adoption may write before the first mutation."""
    destinations: list[tuple[Path, str, str]] = []

    def add(relative: Path | str, kind: str, label: str) -> None:
        destinations.append((dest / relative, kind, label))

    for relative in (*COPY_PATHS, *COPY_MISSING_PATHS):
        source = src / relative
        if not source.exists():
            continue
        for source_node, kind in _source_nodes(source):
            node_relative = Path(relative) / source_node.relative_to(source)
            add(node_relative, kind, "managed destination")

    add(".gitignore", "file", "ignore file")
    add(".ignore", "file", "ignore file")
    add(".my-workflow.toml", "file", "local config")
    add(".claude/skills", "directory", "generated skills directory")
    if not skip_agents:
        add("AGENTS.md", "file", "AGENTS.md")
        add("CLAUDE.md", "file", "CLAUDE.md")

    # workflow_config.py renders one runtime packet for each shipped template.
    template_root = src / "templates/agents"
    if template_root.is_dir():
        for template in template_root.rglob("*"):
            if not template.is_file():
                continue
            provider = template.parent.name
            add(
                Path(f".{provider}/agents") / template.name,
                "file",
                "generated runtime",
            )

    for path, kind, label in destinations:
        _reject_unsafe_destination(dest, path, kind, label)

    # These are intentionally replaced managed pointers. Their parent path is protected
    # above; a directory here would make the unlink below fail after other writes.
    agents = dest / ".agents/skills"
    if agents.is_dir():
        for skill in agents.iterdir():
            if not skill.is_dir():
                continue
            pointer = dest / ".claude/skills" / skill.name
            if pointer.exists() and pointer.is_dir() and not pointer.is_symlink():
                die(
                    f"refusing adoption: generated skill pointer {pointer} must be a file or symlink"
                )


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


def remove_legacy_managed_ignore(
    dest: Path, filename: str, entries: tuple[str, ...]
) -> None:
    target = dest / filename
    if not target.exists():
        return
    lines = target.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = [line for line in lines if line.rstrip("\r\n") not in entries]
    if kept != lines:
        target.write_text("".join(kept), encoding="utf-8")


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
                ".agents/skills/workflow-spec-driven/scripts/... in the target Makefile"
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
    _preflight_adoption_destinations(src, dest, skip_agents)
    if not skip_agents:
        adopt_agents(src, dest)
    remove_obsolete_managed_paths(dest)
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
    remove_legacy_managed_ignore(
        dest, ".gitignore", LEGACY_WORKFLOW_GITIGNORE_ENTRIES
    )
    merge_ignore_file(dest, ".gitignore", WORKFLOW_GITIGNORE_ENTRIES)
    merge_ignore_file(dest, ".ignore", WORKFLOW_SEARCHIGNORE_ENTRIES)
    if not skip_agents:
        write_claude(dest)
    link_claude_skills(dest)
    resolver = dest / ".agents/skills/workflow-config/scripts/workflow_config.py"
    if resolver.is_file():
        result = subprocess.run(
            [sys.executable, str(resolver), "--root", str(dest), "--sync-agents"],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "unknown synchronization error"
            die(f"adoption could not synchronize agent metadata: {detail}")
        print(result.stdout.strip())
    print(f"adopted workflow into {dest}")
    installer = src / "scripts" / "install_security_skills.py"
    command = shlex.join(("python3", str(installer), str(dest), "--yes"))
    print("Security skills are external dependencies, not bundled skills.")
    print(f"After explicit authorization, run exactly: {command}")
    print("Until then, the SECURITY.md security gate remains uncovered.")


if __name__ == "__main__":
    main(sys.argv)
