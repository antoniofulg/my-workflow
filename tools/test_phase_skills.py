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

# phase skill -> the agent whose preload its description must name (PSK-01 AC1)
PRELOADING_AGENT = {
    "wspecify": "planner",
    "wdesign": "planner",
    "wtasks": "planner",
    "wimplement": "implementer",
    "wverify": "verifier",
}

SHARED_REFERENCES = {"code-analysis.md", "coding-principles.md", "lessons.md", "memory.md", "sub-agents.md"}

VALIDATOR_PREFIX = ".agents/skills/workflow-spec-driven/scripts/"
ROUTER_REFERENCE_PREFIX = ".agents/skills/workflow-spec-driven/references/"

SCRIPT_TOKEN = re.compile(r"[\w./-]*scripts/[\w-]+\.py")
REFERENCE_TOKEN = re.compile(r"[\w./-]*references/[\w.-]+\.md")
PHASE_REFERENCE = re.compile(r"references/(?:specify|discuss|design|tasks|implement|validate)\.md")
FORBIDDEN_ROUTER_HEADINGS = ("## Commands", "## Context Loading Strategy", "## Coordinator-assisted")

AGENTS_LINE_CAP = 134

TEMPLATES = ROOT / "templates/agents"
TEMPLATE_ROLES = ("planner", "implementer", "verifier", "explorer", "deep-reviewer")
# Providers whose templates UT-006 scans.
SCANNED_PROVIDERS: tuple[str, ...] = ("claude", "codex", "cursor")

CLAUDE_PRELOAD = {
    "planner": ("workflow-spec-driven", "wspecify", "wtasks", "ponytail"),
    "implementer": ("wimplement", "ponytail"),
    "verifier": ("wverify",),
}
CLAUDE_NO_SKILL_TOOL = ("implementer", "explorer", "deep-reviewer")
READ_ONLY_TOOLS = "Read, Grep, Glob, Bash"

ROLE_PHASE_SKILLS = {
    "planner": ("wspecify", "wdesign", "wtasks"),
    "implementer": ("wimplement",),
    "verifier": ("wverify",),
}
# Reference filenames a load line must never name; the first three are gone from the pack entirely.
REFERENCE_FILENAMES = {"specify.md", "discuss.md", "design.md", "tasks.md", "implement.md", "validate.md"}
REMOVED_REFERENCES = ("specify.md", "implement.md", "validate.md")
LOAD_HEADINGS = ("## Load", "## Do not load")
MD_TOKEN = re.compile(r"[\w./-]+\.md")
SKILL_MENTION = re.compile(r"[Ss]kills?\s+`?([a-z][\w-]*)`?")


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
        assert "disable-model-invocation" not in fields, f"{name}: the flag blocks `skills:` preload"
        description = fields.get("description", "")
        agent = PRELOADING_AGENT[name]
        assert agent in description, f"{name}: description does not name the {agent} agent"
        assert f"/{name}" in description, f"{name}: description does not name the /{name} entry"


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
        entry = (skill / "SKILL.md").read_text(encoding="utf-8")
        for reference in sorted((skill / "references").glob("*.md")):
            token = f"references/{reference.name}"
            assert token in entry, f"{name}/SKILL.md does not name {token}"
        for path in phase_tree(name):
            text = path.read_text(encoding="utf-8")
            for token in SCRIPT_TOKEN.findall(text):
                assert token.startswith(VALIDATOR_PREFIX), f"{path}: {token} is not a router validator path"
                assert (ROOT / token).is_file(), f"{path}: {token} does not exist"
            for token in REFERENCE_TOKEN.findall(text):
                if token.startswith(ROUTER_REFERENCE_PREFIX):
                    assert (ROOT / token).is_file(), f"{path}: {token} does not exist"
                    continue
                assert token.startswith("references/"), f"{path}: {token} is neither local nor a router reference"
                assert (skill / token).is_file(), f"{path}: {token} does not resolve inside the skill"


def test_docs_list_the_phase_skills() -> None:
    pack = (ROOT / "docs/workflow/pack.md").read_text(encoding="utf-8").splitlines()
    rows = [line for line in pack if line.startswith("| `")]
    for name in PHASES:
        assert any(line.startswith(f"| `{name}` |") for line in rows), f"pack.md has no row for {name}"
    roadmap = (ROOT / "docs/workflow/roadmap.md").read_text(encoding="utf-8")
    assert "under 200 lines" in roadmap, "roadmap.md does not state the phase SKILL.md cap"
    agents = line_count(ROOT / "AGENTS.md")
    assert agents <= AGENTS_LINE_CAP, f"AGENTS.md is {agents} lines, cap is {AGENTS_LINE_CAP}"


def template_path(provider: str, role: str) -> Path:
    return TEMPLATES / provider / (f"{role}.toml" if provider == "codex" else f"{role}.md")


def load_lines(text: str) -> list[str]:
    """Lines under a `## Load` or `## Do not load` heading."""
    lines: list[str] = []
    inside = False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.startswith(LOAD_HEADINGS)
            continue
        if inside:
            lines.append(line)
    return lines


def test_claude_templates_declare_preload_and_tool_scope() -> None:
    for role in TEMPLATE_ROLES:
        path = template_path("claude", role)
        fields = frontmatter(path)
        expected = CLAUDE_PRELOAD.get(role)
        if expected is None:
            assert "skills" not in fields, f"{role}: preloads {fields.get('skills')!r}, expected none"
        else:
            assert fields.get("skills") == "[" + ", ".join(expected) + "]", f"{role}: skills are {fields.get('skills')!r}"
            for name in expected:
                assert (SKILLS / name / "SKILL.md").is_file(), f"{role}: preloads missing skill {name}"
        if role in CLAUDE_NO_SKILL_TOOL:
            assert fields.get("disallowedTools") == "Skill", f"{role}: disallowedTools is {fields.get('disallowedTools')!r}"
        else:
            assert "disallowedTools" not in fields, f"{role}: must not set disallowedTools"
    for role in ("explorer", "deep-reviewer"):
        fields = frontmatter(template_path("claude", role))
        assert fields.get("tools") == READ_ONLY_TOOLS, f"{role}: tools are {fields.get('tools')!r}"


def test_template_load_lines_name_skills_and_existing_paths() -> None:
    for provider in SCANNED_PROVIDERS:
        for role in TEMPLATE_ROLES:
            path = template_path(provider, role)
            text = path.read_text(encoding="utf-8")
            label = path.relative_to(ROOT).as_posix()
            for removed in REMOVED_REFERENCES:
                assert removed not in text, f"{label} still names the removed reference {removed}"
            for name in ROLE_PHASE_SKILLS.get(role, ()):
                assert name in text, f"{label} does not name its phase skill {name}"
            for line in load_lines(text):
                for token in MD_TOKEN.findall(line):
                    assert token not in REFERENCE_FILENAMES, f"{label} loads reference file {token}"
                    if "/" in token:
                        assert (ROOT / token).exists(), f"{label} loads missing path {token}"
                for name in SKILL_MENTION.findall(line):
                    assert (SKILLS / name / "SKILL.md").is_file(), f"{label} loads unknown skill {name}"


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
