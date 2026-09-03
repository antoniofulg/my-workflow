"""Contract for the split phase skills. Run: python3 tools/test_phase_skills.py"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".agents/skills"
ROUTER = SKILLS / "workflow-spec-driven"

SKILL_LINE_CAP = 200
ROUTER_LINE_CAP = 150

# phase skill -> (router references it replaces, total-line budget for the phase tree)
PHASES: dict[str, tuple[tuple[str, ...], int]] = {
    "wspecify": (("specify.md", "discuss.md"), 228 + 159 + 10),
    "wdesign": (("design.md",), 193 + 10),
    "wtasks": (("tasks.md",), 443 + 10),
    "wimplement": (("implement.md",), 426 + 10),
    "wverify": (("validate.md",), 339 + 10),
}

SHARED_REFERENCES = {"code-analysis.md", "coding-principles.md", "lessons.md", "memory.md", "sub-agents.md"}

VALIDATOR_PREFIX = ".agents/skills/workflow-spec-driven/scripts/"
ROUTER_REFERENCE_PREFIX = ".agents/skills/workflow-spec-driven/references/"

SCRIPT_TOKEN = re.compile(r"[\w./-]*scripts/[\w-]+\.py")
REFERENCE_TOKEN = re.compile(r"[\w./-]*references/[\w.-]+\.md")
PHASE_REFERENCE = re.compile(r"references/(?:specify|discuss|design|tasks|implement|validate)\.md")
FORBIDDEN_ROUTER_HEADINGS = ("## Commands", "## Context Loading Strategy", "## Coordinator-assisted")

AGENTS_LINE_CAP = 134


def frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines and lines[0] == "---", f"{path} has no frontmatter"
    end = lines.index("---", 1)
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def phase_tree(name: str) -> list[Path]:
    skill = SKILLS / name
    return [skill / "SKILL.md", *sorted((skill / "references").glob("*.md"))]


def test_phase_skills_declare_scoped_frontmatter() -> None:
    for name in PHASES:
        fields = frontmatter(SKILLS / name / "SKILL.md")
        assert fields.get("name") == name, f"{name}: frontmatter name is {fields.get('name')!r}"
        assert fields.get("disable-model-invocation") == "true", f"{name}: not hidden from auto-invocation"


def test_phase_skill_line_cap() -> None:
    for name in PHASES:
        count = line_count(SKILLS / name / "SKILL.md")
        assert count <= SKILL_LINE_CAP, f"{name}/SKILL.md is {count} lines, cap is {SKILL_LINE_CAP}"


def test_router_line_cap() -> None:
    count = line_count(ROUTER / "SKILL.md")
    assert count <= ROUTER_LINE_CAP, f"router SKILL.md is {count} lines, cap is {ROUTER_LINE_CAP}"


def test_router_links_skills_not_references() -> None:
    lines = (ROUTER / "SKILL.md").read_text(encoding="utf-8").splitlines()
    stale = PHASE_REFERENCE.search("\n".join(lines))
    assert stale is None, f"router still links {stale.group(0) if stale else ''}"
    for line in lines:
        for heading in FORBIDDEN_ROUTER_HEADINGS:
            assert not line.startswith(heading), f"router still carries {heading}"
    start = next(index for index, line in enumerate(lines) if line.startswith("| Scope"))
    end = next(index for index in range(start, len(lines)) if not lines[index].startswith("|"))
    sizing = "\n".join(lines[start:end])
    for skill in ("wspecify", "wdesign", "wtasks", "wimplement"):
        assert skill in sizing, f"sizing table does not name {skill}"


def test_moved_references_are_gone_and_no_phase_grew() -> None:
    for name, (replaced, budget) in PHASES.items():
        for reference in replaced:
            assert not (ROUTER / "references" / reference).exists(), f"{reference} still in the router"
        total = sum(line_count(path) for path in phase_tree(name))
        assert total <= budget, f"{name} totals {total} lines, budget is {budget}"


def test_router_keeps_only_the_shared_references() -> None:
    kept = {path.name for path in (ROUTER / "references").glob("*.md")}
    assert kept == SHARED_REFERENCES, f"router references are {sorted(kept)}"


def test_claude_symlinks_resolve() -> None:
    tracked = subprocess.run(
        ["git", "ls-files", ".claude/skills"], cwd=ROOT, text=True, capture_output=True, check=True
    ).stdout.split()
    for name in PHASES:
        link = ROOT / ".claude/skills" / name
        assert link.is_symlink(), f".claude/skills/{name} is not a symlink"
        assert link.readlink().as_posix() == f"../../.agents/skills/{name}", f"{name}: wrong link target"
        assert (link / "SKILL.md").is_file(), f".claude/skills/{name} does not resolve"
        assert f".claude/skills/{name}" in tracked, f".claude/skills/{name} is not tracked by git"


def test_phase_skills_cite_validator_and_template_paths_that_exist() -> None:
    for name in PHASES:
        skill = SKILLS / name
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        for token in SCRIPT_TOKEN.findall(text):
            assert token.startswith(VALIDATOR_PREFIX), f"{name}: {token} is not a router validator path"
            assert (ROOT / token).is_file(), f"{name}: {token} does not exist"
        for token in REFERENCE_TOKEN.findall(text):
            if token.startswith(ROUTER_REFERENCE_PREFIX):
                assert (ROOT / token).is_file(), f"{name}: {token} does not exist"
                continue
            assert token.startswith("references/"), f"{name}: {token} is neither local nor a router reference"
            assert (skill / token).is_file(), f"{name}: {token} does not resolve inside the skill"


def test_docs_list_the_phase_skills() -> None:
    pack = (ROOT / "docs/workflow/pack.md").read_text(encoding="utf-8").splitlines()
    rows = [line for line in pack if line.startswith("| `")]
    for name in PHASES:
        assert any(line.startswith(f"| `{name}` |") for line in rows), f"pack.md has no row for {name}"
    roadmap = (ROOT / "docs/workflow/roadmap.md").read_text(encoding="utf-8")
    assert "under 200 lines" in roadmap, "roadmap.md does not state the phase SKILL.md cap"
    agents = line_count(ROOT / "AGENTS.md")
    assert agents <= AGENTS_LINE_CAP, f"AGENTS.md is {agents} lines, cap is {AGENTS_LINE_CAP}"


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
