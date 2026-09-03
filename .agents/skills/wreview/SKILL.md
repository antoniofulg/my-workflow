---
name: wreview
description: Review phase - deep review of branch diffs, working trees, or PRs. Enter with /wreview.
argument-hint: "[--pr N | --base <ref> | --staged | --worktree] [--files p1,p2] [--spec <path>] [--subagent native|claude-opus|grok|codex] [--max-cohort-files N] [--full] [--out <dir>] [--no-workflow]"
context: fork
agent: planner
background: false
---

# Review

Run this phase with review flags: $ARGUMENTS.

When $ARGUMENTS includes `--publish`, reject it: publishing needs the user's explicit go-ahead in the main session.

Read `.agents/skills/deep-review/SKILL.md` in full and follow it with these flags; never pass --publish.
