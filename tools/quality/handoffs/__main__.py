"""The marker's repository sweep, as a command: `python3 -m tools.quality.handoffs`.

**What it does.** Prints `sweep.sweep`'s triage list — every line under the
handoff directory holding a marker, labelled — or `sweep.pattern_sites`' census,
or the shipped vocabulary. ⛔ Exit `2` when the population read is EMPTY, `1`
when `--patterns` finds a weak pattern, `0` otherwise.

**How you use it.**

    python3 -m tools.quality.handoffs                # the triage list, before a wave
    python3 -m tools.quality.handoffs --marker local
    python3 -m tools.quality.handoffs --patterns     # typed patterns, exit 1 on weak
    python3 -m tools.quality.handoffs --vocabulary   # Ruling 193's authority

**Depends on.** `argparse`, `sys`, and `sweep`. ⚠️ **The command lives here and
not in `sweep.py`** because the floor imports `sweep` for its check, and
`python3 -m` on a module already imported warns and runs it twice (measured).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.quality.handoffs import HANDOFF_DIR
from tools.quality.handoffs.contract import FINDING_MARKERS, MARKER_STRUCTURAL
from tools.quality.handoffs.sweep import (
    COMMAND,
    CONVENTIONS_DIR,
    NAMES,
    WEAK,
    pattern_sites,
    sweep,
    sweep_report,
)


def main(argv: list[str] | None = None) -> int:
    """Print the triage list, the pattern census or the vocabulary; return the exit code."""
    parser = argparse.ArgumentParser(prog=COMMAND, description="The marker's repository sweep.")
    parser.add_argument("--root", default=".", help="repository root (default: .)")
    parser.add_argument("--marker", choices=sorted(NAMES), default=MARKER_STRUCTURAL.strip("`[]"))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--patterns", action="store_true", help="census typed marker patterns")
    mode.add_argument("--vocabulary", action="store_true", help="print the shipped markers")
    arguments = parser.parse_args(argv)
    root = Path(arguments.root)
    if arguments.vocabulary:
        print("\n".join(FINDING_MARKERS))
        return 0
    if arguments.patterns:
        sites = pattern_sites(root)
        print(f"marker patterns in {CONVENTIONS_DIR}: {len(sites)} typed")
        print("\n".join(f"{s.document}:{s.number}: {s.form}: {s.text}" for s in sites))
        return 1 if any(site.form == WEAK for site in sites) else 0
    reading = sweep(root, NAMES[arguments.marker])
    print("\n".join(sweep_report(reading)))
    if reading.documents == 0:
        print(f"marker sweep: EMPTY population — nothing under {HANDOFF_DIR} was read")
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover - the CLI's one line
    sys.exit(main())
