"""Command-line entry point for the quality floor: `python3 -m tools.quality`.

**What it does.** Runs every check over a tree, prints the findings, and exits
1 if there were any. That exit code is the whole point of the module — it is
what turns the conventions into a build failure.

**How you use it.** `python3 -m tools.quality [--root PATH]`. `--root`
defaults to the current directory, which is expected to be the repository
root.

**Depends on.** `argparse` and `tools.quality`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.quality import format_findings, run_all


def main(argv: list[str] | None = None) -> int:
    """Run the floor over `--root` and return the process exit code."""
    parser = argparse.ArgumentParser(
        prog="python3 -m tools.quality",
        description="Fail the build on a module over the size ceiling (R11), a "
        "source module with no mirrored test (R12), a missing package "
        "contract (R17), or a style violation.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="repository root to check (default: the current directory)",
    )
    arguments = parser.parse_args(argv)

    findings = run_all(arguments.root)
    print(format_findings(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
