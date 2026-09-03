#!/usr/bin/env python3
"""Report what fraction of delivered work was reviewed, from git history alone.

  python3 tools/review-metrics.py [<rev-range>] [--json]

A delivery is a first-parent merge commit in the range. One carrying a
`Review-Signal` trailer is signalled; one carrying none is unsigned. `tier=direct`
and `tier=batch` are reviewed by design, never unreviewed.

The trailer grammar lives in `docs/guidelines/REVIEW-ROUNDS.md` and is enforced at
commit time by `check_commit.py`; this reader only aggregates what is already there,
so a range with no trailers reports zeros and exits 0.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

FORMAT = "%H%x09%(trailers:key=Review-Signal,valueonly)"
BY_DESIGN = ("direct", "batch")
SUMMED = ("slices", "verified", "findings", "fixed", "dismissed")


def deliveries(rev_range: str) -> list[tuple[str, str]]:
    """(sha, trailer) per first-parent merge. Unreadable range: usage error, exit 2."""
    proc = subprocess.run(
        ["git", "log", "-z", "--first-parent", "--merges", f"--format={FORMAT}", rev_range],
        capture_output=True,
        text=True,
    )
    if proc.returncode:
        # A repository with no commits at all has no deliveries; anything else is a bad range.
        unborn = subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"], capture_output=True)
        if unborn.returncode == 0:
            print(proc.stderr.strip(), file=sys.stderr)
            raise SystemExit(2)
        return []
    found = []
    for entry in proc.stdout.split("\0"):
        if entry.strip():
            sha, _, trailer = entry.partition("\t")
            found.append((sha, trailer))
    return found


def number(value: str) -> int:
    """A non-negative decimal integer, or 0. Matches check_commit.py's `^[0-9]+$`."""
    return int(value) if value.isascii() and value.isdigit() else 0


def report(rev_range: str) -> dict:
    # .split() on whitespace runs, exactly as check_commit.py parses the same line.
    totals = dict.fromkeys(SUMMED + ("killed", "injected"), 0)
    signalled = unsigned = by_design = 0
    tiers: dict[str, int] = {}
    for _, trailer in deliveries(rev_range):
        values = {}
        for field in trailer.split():
            key, sep, value = field.partition("=")
            if sep:
                values[key] = value
        tier = values.get("tier")
        if tier is None:
            unsigned += 1
            continue
        signalled += 1
        tiers[tier] = tiers.get(tier, 0) + 1
        by_design += tier in BY_DESIGN
        killed, _, injected = values.get("sensor", "").partition("/")
        totals["killed"] += number(killed)
        totals["injected"] += number(injected)
        for key in SUMMED:
            totals[key] += number(values.get(key, ""))

    return {
        "range": rev_range,
        "deliveries": signalled + unsigned,
        "signalled": signalled,
        "unsigned": unsigned,
        "reviewed_by_design": by_design,
        "reviewed_fraction": totals["verified"] / totals["slices"] if totals["slices"] else None,
        "surviving_mutants": totals["injected"] - totals["killed"],
        "tiers": dict(sorted(tiers.items())),
        **totals,
    }


def render(r: dict) -> str:
    fraction = r["reviewed_fraction"]
    lines = [
        f"Deliveries in {r['range']}: {r['deliveries']}"
        f" (signalled {r['signalled']}, unsigned {r['unsigned']})",
        f"Reviewed fraction: {r['verified']}/{r['slices']} slices verified"
        f" ({'n/a' if fraction is None else format(fraction, '.1%')})",
        f"Reviewed by design (tier=direct|batch): {r['reviewed_by_design']}",
        f"Findings: {r['findings']} (fixed {r['fixed']}, dismissed {r['dismissed']})",
        f"Surviving mutants: {r['surviving_mutants']}"
        f" (killed {r['killed']} of {r['injected']} injected)",
    ]
    return "\n".join(lines + [f"  tier={t}: {n}" for t, n in r["tiers"].items()])


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("rev_range", nargs="?", default="HEAD", help="range to read (default HEAD)")
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    args = parser.parse_args(argv)
    result = report(args.rev_range)
    print(json.dumps(result, indent=2) if args.json else render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
