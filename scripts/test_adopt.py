"""Self-check for scripts/adopt.py. Run: python3 scripts/test_adopt.py"""

from __future__ import annotations

import shutil
import subprocess
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
        config = tmp / ".my-workflow.toml"
        sentinel = "# consumer-owned\n[deep_review]\ncadence = 'feature'\n"
        config.write_text(sentinel, encoding="utf-8")
        run(tmp)
        assert config.read_text(encoding="utf-8") == sentinel
        agents = (tmp / "AGENTS.md").read_text(encoding="utf-8")
        assert STENCIL in agents
        claude = tmp / "CLAUDE.md"
        assert not claude.is_symlink()
        assert claude.read_text(encoding="utf-8") == "@AGENTS.md\n"
        assert (tmp / "docs/guidelines/GATES.md").is_file()
        assert (tmp / "tools/ad-index.py").is_file()
        assert (tmp / ".agents/skills/qa-plan/SKILL.md").is_file()
        assert (tmp / ".agents/skills/qa-execute/SKILL.md").is_file()
        workflow_skill = tmp / ".agents/skills/workflow-config/SKILL.md"
        workflow_resolver = tmp / ".agents/skills/workflow-config/scripts/workflow_config.py"
        assert workflow_skill.is_file()
        assert workflow_resolver.is_file()
        assert workflow_resolver.read_bytes() == (
            ROOT / ".agents/skills/workflow-config/scripts/workflow_config.py"
        ).read_bytes()
        assert (tmp / "docs/qa/README.md").is_file()
        assert (tmp / ".claude/skills/autonomous").is_symlink()
        assert (tmp / ".claude/skills/qa-plan").is_symlink()
        assert (tmp / ".claude/skills/qa-execute").is_symlink()
        assert (tmp / ".cursor/agents/planner.md").is_file()
        ignored = (tmp / ".gitignore").read_text(encoding="utf-8")
        for entry in (
            ".deep-review/*",
            "!.deep-review/learnings.md",
            ".specs/features/",
            "graft/",
        ):
            assert ignored.splitlines().count(entry) == 1
        search_ignored = (tmp / ".ignore").read_text(encoding="utf-8")
        for entry in ("!graft/", "graft/.cache/", "graft/.graph/"):
            assert search_ignored.splitlines().count(entry) == 1
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
        profile = tmp / "docs/qa/README.md"
        profile.write_text("consumer-owned profile\n", encoding="utf-8")
        run(tmp)
        assert profile.read_text(encoding="utf-8") == "consumer-owned profile\n"
    finally:
        shutil.rmtree(tmp)


def test_gitignore_rules_merge_without_overwrite() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        (tmp / ".gitignore").write_text("consumer-cache/\n", encoding="utf-8")
        run(tmp)
        ignored = (tmp / ".gitignore").read_text(encoding="utf-8")
        assert "consumer-cache/\n" in ignored
        for entry in (
            ".deep-review/*",
            "!.deep-review/learnings.md",
            ".specs/features/",
            "graft/",
        ):
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
        assert ignored.splitlines()[-4:] == [
            ".deep-review/*",
            "!.deep-review/learnings.md",
            ".specs/features/",
            "graft/",
        ]
    finally:
        shutil.rmtree(tmp)


def test_graft_ignore_contract_and_search_visibility() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        (tmp / ".gitignore").write_text("consumer-cache/\n", encoding="utf-8")
        (tmp / ".ignore").write_text("consumer-search-cache/\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(tmp)], check=True)
        run(tmp)

        ignored = (tmp / ".gitignore").read_text(encoding="utf-8")
        assert "consumer-cache/\n" in ignored
        assert ignored.splitlines().count("graft/") == 1
        search_ignored = (tmp / ".ignore").read_text(encoding="utf-8")
        assert "consumer-search-cache/\n" in search_ignored
        for entry in ("!graft/", "graft/.cache/", "graft/.graph/"):
            assert search_ignored.splitlines().count(entry) == 1

        (tmp / "graft/.cache").mkdir(parents=True)
        (tmp / "graft/.graph").mkdir(parents=True)
        (tmp / "graft/.cache/index.json").write_text("cache\n", encoding="utf-8")
        (tmp / "graft/.graph/wiring.json").write_text("graph\n", encoding="utf-8")
        card = tmp / "graft/cards/adoption.md"
        card.parent.mkdir(parents=True)
        card.write_text("generated adoption card\n", encoding="utf-8")

        for path in ("graft/.cache/index.json", "graft/.graph/wiring.json"):
            result = subprocess.run(
                ["git", "-C", str(tmp), "check-ignore", "-q", "--", path],
                check=False,
            )
            assert result.returncode == 0, path

        search = subprocess.run(
            ["rg", "--files", "--hidden", "--no-ignore-parent"],
            cwd=tmp,
            check=True,
            capture_output=True,
            text=True,
        )
        assert "graft/cards/adoption.md" in search.stdout
        assert "graft/.cache/index.json" not in search.stdout
        assert "graft/.graph/wiring.json" not in search.stdout
    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    test_fresh_and_refuse()
    test_agent_pins_survive_readopt()
    test_gitignore_rules_merge_without_overwrite()
    test_graft_ignore_contract_and_search_visibility()
    print("ok")
