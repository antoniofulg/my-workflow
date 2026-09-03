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
    "wspecify": (("specify.md", "discuss.md"), 228 + 159 + 10 + 80),
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
TEMPLATE_ROLES = ("planner", "implementer", "verifier", "explorer", "deep-reviewer", "designer")
# Providers whose templates UT-006 scans.
SCANNED_PROVIDERS: tuple[str, ...] = ("claude", "codex", "cursor")

CLAUDE_PRELOAD = {
    "planner": ("workflow-spec-driven", "wspecify", "wtasks", "ponytail"),
    "implementer": ("wimplement", "ponytail"),
    "verifier": ("wverify",),
    "designer": ("wdesign", "ponytail"),
}
CLAUDE_NO_SKILL_TOOL = ("implementer", "explorer", "deep-reviewer")
READ_ONLY_TOOLS = "Read, Grep, Glob, Bash"

ROLE_PHASE_SKILLS = {
    "planner": ("wspecify", "wdesign", "wtasks"),
    "implementer": ("wimplement",),
    "verifier": ("wverify",),
    "designer": ("wdesign",),
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


# One-off Bun program: the repo's own frontmatter reader over every path given on argv.
BUN_STRICT_YAML = """
import { readFrontmatter } from "./tools/shared/src/frontmatter.ts";
for (const path of Bun.argv.slice(1)) {
  const parsed = readFrontmatter(await Bun.file(path).text());
  if (!parsed.present || parsed.error || !parsed.data) {
    console.error(`${path}: ${parsed.error ?? "no frontmatter mapping"}`);
    process.exit(1);
  }
}
"""


def strict_yaml_frontmatter(paths: list[str]) -> subprocess.CompletedProcess[str]:
    """Parse each path with the repo's Bun frontmatter reader. Exit 0 means strict YAML."""
    return subprocess.run(
        ["bun", "-e", BUN_STRICT_YAML, *paths], cwd=ROOT, text=True, capture_output=True
    )


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
        assert fields.get("context") == "fork", f"{name}: context is {fields.get('context')!r}"
        assert fields.get("agent") == agent, f"{name}: agent is {fields.get('agent')!r}"
        assert fields.get("background") == "false", f"{name}: background is {fields.get('background')!r}"
        assert fields.get("argument-hint") in ('"<feature-or-slice>"', "<feature-or-slice>"), f"{name}: argument-hint is {fields.get('argument-hint')!r}"
        lines = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8").splitlines()
        h1_index = next(i for i, line in enumerate(lines) if line.startswith("# "))
        first_body_line = next(line for line in lines[h1_index + 1:] if line.strip())
        assert "$ARGUMENTS" in first_body_line, f"{name}: first body line does not bind $ARGUMENTS: {first_body_line!r}"
    parsed = strict_yaml_frontmatter([f".agents/skills/{name}/SKILL.md" for name in PHASES])
    assert parsed.returncode == 0, f"frontmatter is not strict YAML: {parsed.stderr.strip()}"


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
    for name in ALL_W_SKILLS:
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


def heading_body(text: str, heading: str) -> str:
    """Lines after `heading` until the next heading of the same or higher level."""
    lines = text.splitlines()
    level = len(heading) - len(heading.lstrip("#"))
    collecting = False
    collected: list[str] = []
    for line in lines:
        if not collecting:
            if line.startswith(heading):
                collecting = True
            continue
        if line.startswith("#"):
            hashes = len(line) - len(line.lstrip("#"))
            if hashes <= level and line[hashes : hashes + 1] == " ":
                break
        collected.append(line)
    assert collecting, f"missing heading {heading!r}"
    return "\n".join(collected)


def first_line_with(body: str, needle: str) -> str:
    for line in body.splitlines():
        if needle in line:
            return line
    raise AssertionError(f"no line containing {needle!r}")


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


ENTRY_SKILLS = {
    "wreview": "planner",
    "wqa": "verifier",
}
ALL_W_SKILLS = ("wspecify", "wdesign", "wtasks", "wimplement", "wverify", "wreview", "wqa")
PHASE_NAMES = {
    "wspecify": "Specify",
    "wdesign": "Design",
    "wtasks": "Tasks",
    "wimplement": "Execute",
    "wverify": "Verify",
    "wreview": "Review",
    "wqa": "QA",
}


def test_entry_skills_contract() -> None:
    """UT-010: entry skills carry keys, agent mapping, line cap < 40, and tracked symlinks."""
    tracked = subprocess.run(
        ["git", "ls-files", ".claude/skills"], cwd=ROOT, text=True, capture_output=True, check=True
    ).stdout.split()
    for name, agent in ENTRY_SKILLS.items():
        skill_path = SKILLS / name / "SKILL.md"
        assert skill_path.is_file(), f"{name}/SKILL.md does not exist"
        fields = frontmatter(skill_path)
        assert fields.get("name") == name, f"{name}: frontmatter name is {fields.get('name')!r}"
        assert fields.get("context") == "fork", f"{name}: context is {fields.get('context')!r}"
        assert fields.get("agent") == agent, f"{name}: agent is {fields.get('agent')!r}"
        assert fields.get("background") == "false", f"{name}: background is {fields.get('background')!r}"
        assert "argument-hint" in fields, f"{name}: argument-hint missing"
        count = line_count(skill_path)
        assert count < 40, f"{name}/SKILL.md is {count} lines, must be < 40"
        link = ROOT / ".claude/skills" / name
        assert link.is_symlink(), f".claude/skills/{name} is not a symlink"
        assert link.readlink().as_posix() == f"../../.agents/skills/{name}", f"{name}: wrong link target"
        assert (link / "SKILL.md").is_file(), f".claude/skills/{name} does not resolve"
        assert f".claude/skills/{name}" in tracked, f".claude/skills/{name} is not tracked by git"
    parsed = strict_yaml_frontmatter([f".agents/skills/{name}/SKILL.md" for name in ENTRY_SKILLS])
    assert parsed.returncode == 0, f"entry skills frontmatter is not strict YAML: {parsed.stderr.strip()}"


def test_exactly_seven_user_invocable_w_skills() -> None:
    """UT-011: exactly seven user-invocable w* skills, each description starts with phase name and states argument."""
    w_skill_dirs = {p.name for p in SKILLS.glob("w*") if (p / "SKILL.md").is_file() and not p.name.startswith("workflow-")}
    assert w_skill_dirs == set(ALL_W_SKILLS), f"found w* skills: {sorted(w_skill_dirs)}, expected: {sorted(ALL_W_SKILLS)}"
    for name in ALL_W_SKILLS:
        fields = frontmatter(SKILLS / name / "SKILL.md")
        assert fields.get("disable-model-invocation") != "true", f"{name}: disable-model-invocation must not be true"
        description = fields.get("description", "")
        phase_prefix = PHASE_NAMES[name]
        assert description.startswith(f"{phase_prefix} phase") or description.startswith(f'"{phase_prefix} phase'), (
            f"{name}: description {description!r} does not start with {phase_prefix} phase"
        )
        assert "Argument:" in description, f"{name}: description does not state its argument: {description!r}"


# SID-01 / SID-02 AC clause -> assertion line (this group). SID-01 AC6 is in test_tlc_validators.py.
# SID-01 AC1 artifact wspecify / Impact step: L386; after dimensions sweep: L393; before user stories: L388
# SID-01 AC1 two explorers: L409; data and model dependencies: L410; pages/journeys/QA explorer: L411
# SID-01 AC1 journeys: L412; jobs: L413; events: L414; QA scenarios: L415
# SID-01 AC1 writes ## Impact: L416; affected features: L417; pages listing: L419; scenario ids: L420
# SID-01 AC2 per listed feature: L421; ubiquitous acceptance criterion: L422; behaviour is unchanged: L423
# SID-01 AC3 uiux.md step: L401; after ACs before closure: L403; screen added or changed: L426; follows UI-UX.md: L427
# SID-01 AC4 guideline exists: L506; names uiux.md: L509; written in Specify: L510
# SID-01 AC4 wdesign step 1: L484; load uiux.md: L487; when present (exists, load it): L488
# SID-01 AC5 rerun: L498; QA scenario ids: L500; named in ## Impact: L501; pass, fail, or untested: L502
# SID-01 AC5 EC1 none means no reruns: L503
# SID-01 AC7 spec-template.md ## Impact: L474; between Assumptions and User Stories: L476
# SID-02 AC1 at plan approval: L430 and L444; cite references/gap-hunt.md: L405 and L431; file exists: L406
# SID-02 AC1 Small-skip / Medium-Large-ask / Complex-recommend in SKILL.md: L432, L433, L434
# SID-02 AC1 Small-skip / Medium-Large-ask / Complex-recommend in gap-hunt.md: L445, L446, L447
# SID-02 AC2 When accepted: L439 and L451; two explorers: L452; unhappy paths: L453
# SID-02 AC2 current behaviour: L455; QA scenarios: L456; domain and data gaps: L457
# SID-02 AC2 numbered questions: L458; frontier rounds: L440 and L459; recommended answer: L460
# SID-02 AC3 acceptance criterion: L461; context.md decision: L462; never a note: L463
# SID-02 AC4 Autonomous: L435 and L448; only for Complex: L436 and L449; decisions.md: L438 and L450
# SID-02 EC2 finds nothing → one line and proceed: L437 and L464
def test_specify_carries_the_new_steps() -> None:
    """UT-002: Specify carries Impact, uiux.md, and gap-hunt steps, reference exists, <= 200 lines."""
    skill_path = SKILLS / "wspecify" / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")
    count = line_count(skill_path)
    assert count <= SKILL_LINE_CAP, f"wspecify/SKILL.md is {count} lines, cap is {SKILL_LINE_CAP}"

    impact_idx = text.find("Impact")
    user_stories_idx = text.find("User Stories")
    assert impact_idx != -1, "wspecify does not contain an Impact step"
    assert user_stories_idx != -1, "wspecify does not contain User Stories"
    assert impact_idx < user_stories_idx, "Impact step must appear before User Stories"
    sweep_idx = text.find("dimensions sweep")
    impact_heading_idx = text.find("### 2. Map Impact")
    assert sweep_idx != -1, "wspecify does not name the dimensions sweep"
    assert impact_heading_idx != -1, "wspecify missing the Impact step heading"
    assert sweep_idx < impact_heading_idx, "Impact step must appear after the dimensions sweep"

    ac_idx = text.find("Acceptance Criteria")
    uiux_idx = text.find("uiux.md")
    closure_idx = text.find("Closure Gate")
    if closure_idx == -1:
        closure_idx = text.find("closure gate")
    assert ac_idx != -1, "wspecify does not contain Acceptance Criteria"
    assert uiux_idx != -1, "wspecify does not contain uiux.md step"
    assert closure_idx != -1, "wspecify does not contain Closure Gate step"
    assert ac_idx < uiux_idx < closure_idx, "uiux.md step must be after Acceptance Criteria and before closure gate"

    assert "references/gap-hunt.md" in text, "wspecify does not cite references/gap-hunt.md"
    assert (SKILLS / "wspecify" / "references" / "gap-hunt.md").is_file(), "references/gap-hunt.md does not exist"

    impact_body = heading_body(text, "### 2. Map Impact")
    assert "two explorer" in impact_body.lower(), "Impact step does not dispatch two explorers"
    assert "Data and model dependencies" in impact_body, "Impact step missing the data/model explorer trace"
    assert "Pages, journeys, and QA scenarios" in impact_body, "Impact step missing the pages/journeys/QA explorer trace"
    assert "journeys" in impact_body, "Impact step missing journeys"
    assert "jobs" in impact_body, "Impact step missing jobs"
    assert "events" in impact_body, "Impact step missing events"
    assert "QA scenarios" in impact_body, "Impact step missing QA scenarios"
    assert "## Impact" in impact_body, "Impact step does not write a ## Impact section"
    assert "affected features" in impact_body, "Impact step does not list affected features"
    listing_line = first_line_with(impact_body, "## Impact")
    assert "pages" in listing_line.lower(), "Impact listing does not name pages"
    assert "scenario ids" in impact_body, "Impact step does not list scenario ids"
    assert "For each affected feature listed" in impact_body, "Impact step missing the per-listed-feature trigger"
    assert "ubiquitous acceptance criterion" in impact_body, "Impact step missing the ubiquitous no-regression AC"
    assert "behaviour is unchanged" in impact_body, "Impact step missing unchanged-behaviour wording"

    uiux_body = heading_body(text, "### 5. UI/UX Surface Map")
    assert "Only when a screen is added or changed" in uiux_body, "uiux.md step missing the screen-only gate"
    assert "docs/guidelines/UI-UX.md" in uiux_body, "uiux.md step does not follow docs/guidelines/UI-UX.md"

    gap_offer = heading_body(text, "### 7. Plan Approval")
    assert "plan approval" in gap_offer.lower(), "gap-hunt step is not at plan approval"
    assert "references/gap-hunt.md" in gap_offer, "plan-approval step does not cite references/gap-hunt.md"
    assert "**Small:** Skip the gap hunt" in gap_offer, "wspecify missing Small-skip gap-hunt sizing"
    assert "**Medium & Large:** Ask" in gap_offer, "wspecify missing Medium-and-Large-ask gap-hunt sizing"
    assert "**Complex:** Recommend the gap hunt" in gap_offer, "wspecify missing Complex-recommend gap-hunt sizing"
    assert "Autonomous" in gap_offer, "wspecify missing the autonomous gap-hunt trigger"
    assert "only for Complex" in gap_offer, "wspecify missing the autonomous-only-Complex gap-hunt rule"
    assert "one line and proceed" in gap_offer, "wspecify missing the one-line empty-hunt rule"
    assert "decisions.md" in gap_offer, "autonomous skip is not recorded in decisions.md"
    assert "When accepted" in gap_offer, "wspecify missing the human-accepts gap-hunt trigger"
    assert "frontier" in gap_offer.lower(), "wspecify missing frontier rounds at plan approval"

    hunt = (SKILLS / "wspecify" / "references" / "gap-hunt.md").read_text(encoding="utf-8")
    sizing = heading_body(hunt, "## Sizing & Invocation")
    assert "plan approval" in sizing.lower(), "gap-hunt.md sizing is not at plan approval"
    assert "**Small:** Skipped" in sizing, "gap-hunt.md missing Small-skip sizing"
    assert "**Medium & Large:** Asked" in sizing, "gap-hunt.md missing Medium-and-Large-ask sizing"
    assert "**Complex:** Recommended" in sizing, "gap-hunt.md missing Complex-recommend sizing"
    assert "Autonomous" in hunt, "gap-hunt.md missing the autonomous trigger"
    assert "only for Complex" in hunt, "gap-hunt.md missing the autonomous-only-Complex rule"
    assert "decisions.md" in hunt, "gap-hunt.md does not record the autonomous skip in decisions.md"
    assert "When accepted" in hunt, "gap-hunt.md missing the human-accepts trigger"
    assert "two explorer" in hunt.lower(), "gap-hunt.md does not dispatch two explorers"
    assert "Unhappy paths explorer" in hunt, "gap-hunt.md missing the unhappy-paths explorer"
    unhappy_line = first_line_with(hunt, "Unhappy paths")
    assert "behaviour" in unhappy_line, "unhappy-paths explorer missing current behaviour"
    assert "QA scenarios" in unhappy_line, "unhappy-paths explorer missing QA scenarios"
    assert "Domain & data gaps explorer" in hunt, "gap-hunt.md missing the domain/data explorer"
    assert "numbered questions" in hunt, "gap-hunt.md missing numbered questions"
    assert "frontier" in hunt.lower(), "gap-hunt.md missing frontier rounds"
    assert "recommended answer" in hunt, "gap-hunt.md missing frontier rounds with a recommended answer"
    assert "acceptance criterion" in hunt, "gap-hunt.md does not settle findings as acceptance criteria"
    assert "context.md" in hunt, "gap-hunt.md does not settle findings as context.md decisions"
    assert "Never leave a settled finding as an informal note" in hunt, "gap-hunt.md missing the never-a-note rule"
    assert "one line" in hunt, "gap-hunt.md missing the empty-hunt one-line rule"


def test_spec_template_carries_impact() -> None:
    """UT-003 (template half): spec-template carries ## Impact between Assumptions and User Stories."""
    template_text = (SKILLS / "wspecify" / "references" / "spec-template.md").read_text(encoding="utf-8")
    assumptions_idx = template_text.find("## Assumptions & Open Questions")
    impact_idx = template_text.find("## Impact")
    stories_idx = template_text.find("## User Stories")
    assert assumptions_idx != -1, "spec-template missing Assumptions & Open Questions"
    assert impact_idx != -1, "spec-template missing ## Impact"
    assert stories_idx != -1, "spec-template missing ## User Stories"
    assert assumptions_idx < impact_idx < stories_idx, "template must have ## Impact between Assumptions and User Stories"


def test_downstream_phases_wired_for_impact_and_designer() -> None:
    """UT-003 (downstream half): wdesign step 1 names uiux.md and designer dispatch; wverify names Impact scenario reruns; UI-UX.md says Specify."""
    wdesign_text = (SKILLS / "wdesign" / "SKILL.md").read_text(encoding="utf-8")
    assert line_count(SKILLS / "wdesign" / "SKILL.md") <= SKILL_LINE_CAP, "wdesign exceeds line cap"
    step1_idx = wdesign_text.find("### 1. Load Context")
    assert step1_idx != -1, "wdesign missing step 1"
    step1_end = wdesign_text.find("### 1.5", step1_idx) if "### 1.5" in wdesign_text else wdesign_text.find("### 2", step1_idx)
    step1_body = wdesign_text[step1_idx:step1_end]
    assert "uiux.md" in step1_body, "wdesign step 1 does not name uiux.md"
    assert "exists, load it" in step1_body, "wdesign step 1 does not load uiux.md when present"
    assert "designer" in step1_body, "wdesign step 1 does not name designer dispatch"
    assert "before internal design" in step1_body, "wdesign step 1 does not dispatch designer before internal design"
    assert "architecture half" in step1_body, "wdesign step 1 does not keep the architecture half with the planner"

    wverify_path = SKILLS / "wverify" / "SKILL.md"
    wverify_text = wverify_path.read_text(encoding="utf-8")
    assert line_count(wverify_path) <= SKILL_LINE_CAP, "wverify exceeds line cap"
    assert "Impact" in wverify_text, "wverify does not name Impact"
    assert "scenario" in wverify_text.lower(), "wverify does not name scenarios"
    assert "rerun" in wverify_text.lower(), "wverify does not name rerun"
    rerun_body = heading_body(wverify_text, "### 3.5.")
    assert "scenario ids" in rerun_body, "wverify rerun body does not name scenario ids"
    assert "## Impact" in rerun_body, "wverify rerun body does not name ## Impact"
    assert "pass, fail, or untested" in rerun_body, "wverify rerun body does not name pass, fail, or untested"
    assert "no reruns" in rerun_body, "wverify rerun body does not say none means no reruns"

    uiux_path = ROOT / "docs/guidelines/UI-UX.md"
    assert uiux_path.is_file(), "docs/guidelines/UI-UX.md does not exist"
    uiux_guideline = uiux_path.read_text(encoding="utf-8")
    assert line_count(uiux_path) < 120, "UI-UX.md exceeds 120 lines"
    assert "uiux.md" in uiux_guideline, "UI-UX.md does not name uiux.md"
    assert "written in Specify" in uiux_guideline, "UI-UX.md does not state written in Specify"


def test_designer_templates_and_preload() -> None:
    """UT-004: Designer templates and preload (SID-03 AC2)."""
    claude_path = TEMPLATES / "claude" / "designer.md"
    codex_path = TEMPLATES / "codex" / "designer.toml"
    cursor_path = TEMPLATES / "cursor" / "designer.md"

    assert claude_path.is_file(), "Claude designer template missing"
    assert codex_path.is_file(), "Codex designer template missing"
    assert cursor_path.is_file(), "Cursor designer template missing"

    claude_fields = frontmatter(claude_path)
    assert claude_fields.get("skills") == "[wdesign, ponytail]", f"Claude designer skills: {claude_fields.get('skills')!r}"
    assert "disallowedTools" not in claude_fields, "Claude designer must not set disallowedTools"
    assert claude_fields.get("model") == "inherit"
    assert claude_fields.get("effort") == "high"

    claude_text = claude_path.read_text(encoding="utf-8")
    assert "uiux.md" in claude_text
    assert "docs/design/" in claude_text
    assert "uiux-review.md" in claude_text
    assert "never write product code" in claude_text.lower() or "do not implement product code" in claude_text.lower()
    claude_load = heading_body(claude_text, "## Load")
    assert "spec.md" in claude_load, "Claude designer Load list missing spec.md"
    assert "UI-UX.md" in claude_load, "Claude designer Load list missing UI-UX.md"
    assert "FRONTEND.md" in claude_load, "Claude designer Load list missing FRONTEND.md"

    never_write_codex = (
        "You are the designer. Produce mockups and review notes for UI-bearing features. Never write product code."
    )
    never_write_cursor = (
        "You are the **designer**. Produce mockups and review notes for UI-bearing features. Never write product code."
    )
    codex_text = codex_path.read_text(encoding="utf-8")
    assert "wdesign" in codex_text
    assert never_write_codex in codex_text, "Codex designer body missing never-write-product-code"
    cursor_text = cursor_path.read_text(encoding="utf-8")
    assert "wdesign" in cursor_text
    assert never_write_cursor in cursor_text, "Cursor designer body missing never-write-product-code"


def test_agents_and_pack_name_designer() -> None:
    """UT-006: AGENTS.md and pack.md name the designer (SID-03 AC6)."""
    agents_path = ROOT / "AGENTS.md"
    agents_text = agents_path.read_text(encoding="utf-8")
    assert line_count(agents_path) <= AGENTS_LINE_CAP, f"AGENTS.md exceeds line cap {AGENTS_LINE_CAP}"
    assert "designer" in agents_text, "AGENTS.md does not name designer"

    pack_path = ROOT / "docs/workflow/pack.md"
    pack_text = pack_path.read_text(encoding="utf-8")
    assert "designer" in pack_text, "pack.md does not name designer"
    assert "five windows" in pack_text, "pack.md does not state five windows"


if __name__ == "__main__":
    tests = [function for name, function in sorted(globals().items()) if name.startswith("test_")]
    for function in tests:
        function()
    print(f"{len(tests)} passed, 0 failed")
