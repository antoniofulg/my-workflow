"""Self-check for scripts/adopt.py. Run: python3 scripts/test_adopt.py"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adopt import STENCIL, main

ROOT = Path(__file__).resolve().parent.parent


def run(dest: Path) -> None:
    main(["adopt.py", str(dest)])


def test_fresh_and_refuse() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        run(tmp)
        agents = (tmp / "AGENTS.md").read_text(encoding="utf-8")
        assert STENCIL in agents
        claude = tmp / "CLAUDE.md"
        assert not claude.is_symlink()
        assert claude.read_text(encoding="utf-8") == "@AGENTS.md\n"
        assert (tmp / "docs/guidelines/GATES.md").is_file()
        assert (tmp / "tools/ad-index.py").is_file()
        assert (tmp / ".claude/skills/autonomous").is_symlink()
        assert (tmp / ".cursor/agents/planner.md").is_file()
        ignored = (tmp / ".gitignore").read_text(encoding="utf-8")
        for entry in (".deep-review/*", "!.deep-review/learnings.md", ".specs/features/"):
            assert ignored.splitlines().count(entry) == 1
        for path in (
            ".cursor/agents/explorer.md",
            ".claude/agents/explorer.md",
            ".codex/agents/explorer.toml",
        ):
            assert (tmp / path).is_file()

        (tmp / "AGENTS.md").write_text(
            "# Agent operating system\n\n## What this project is\n\nA shipped product.\n",
            encoding="utf-8",
        )
        try:
            run(tmp)
        except SystemExit as exc:
            assert exc.code == 1
        else:
            raise AssertionError("expected refuse on non-stencil product paragraph")
    finally:
        shutil.rmtree(tmp)


def test_agent_pins_survive_readopt() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        run(tmp)
        pin = tmp / ".cursor" / "agents" / "planner.md"
        pin.write_text("local-pin\n", encoding="utf-8")
        explorer = tmp / ".cursor" / "agents" / "explorer.md"
        explorer.unlink()
        run(tmp)
        assert pin.read_text(encoding="utf-8") == "local-pin\n"
        assert explorer.read_text(encoding="utf-8") == (
            ROOT / ".cursor" / "agents" / "explorer.md"
        ).read_text(encoding="utf-8")
        assert (tmp / "CLAUDE.md").read_text(encoding="utf-8") == "@AGENTS.md\n"
    finally:
        shutil.rmtree(tmp)


def test_gitignore_rules_merge_without_overwrite() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        (tmp / ".gitignore").write_text("consumer-cache/\n", encoding="utf-8")
        run(tmp)
        ignored = (tmp / ".gitignore").read_text(encoding="utf-8")
        assert "consumer-cache/\n" in ignored
        for entry in (".deep-review/*", "!.deep-review/learnings.md", ".specs/features/"):
            assert ignored.splitlines().count(entry) == 1

        (tmp / ".gitignore").write_text(
            "consumer-cache/\n"
            "!.deep-review/learnings.md\n"
            ".deep-review/*\n"
            ".specs/features/\n"
            "consumer-output/\n",
            encoding="utf-8",
        )
        run(tmp)
        ignored = (tmp / ".gitignore").read_text(encoding="utf-8")
        assert "consumer-cache/\n" in ignored
        assert "consumer-output/\n" in ignored
        assert ignored.splitlines()[-3:] == [
            ".deep-review/*",
            "!.deep-review/learnings.md",
            ".specs/features/",
        ]
    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    test_fresh_and_refuse()
    test_agent_pins_survive_readopt()
    test_gitignore_rules_merge_without_overwrite()
    print("ok")
