"""Command-line entry point for the product floor: `python3 -m tests.floor`.

**What it does.** Runs every product check over a tree, prints the notices and the findings,
and exits 1 if there were any findings. That exit code is the whole point: it turns the
product's rules into a build failure on a checkout with nothing but the product in it.

**How you use it.** `python3 -m tests.floor [--root PATH]`, from the repository root. `--root`
defaults to the current directory.

**Depends on.** `argparse` and `tests.floor` — the standard library.

⛔ **The floor is not the suite.** Format and lint are enforced in `tests/test_repository.py`,
and the rest of the product's behaviour by `python3 -m pytest`; the last line says so, below
the verdict, because a qualifier above the line it qualifies is one a reader has scrolled past.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tests.floor import format_findings, run_all, run_notices

#: The gate this run is NOT, printed below the verdict on every run, clean or not.
SCOPE = (
    "scope: the product floor only — `python3 -m pytest` is a SEPARATE gate and can be RED "
    "at this same ref (format and lint are enforced in tests/test_repository.py)"
)


def main(argv: list[str] | None = None) -> int:
    """Run the product floor over `--root` and return the process exit code."""
    parser = argparse.ArgumentParser(
        prog="python3 -m tests.floor",
        description="Fail on personal data (R7), a module over the size ceiling (R11), a "
        "module with no mirrored test (R12), a missing contract (R17), a corpus named in "
        "framework source (R1), an undeclared package surface, or a style violation.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="repository root to check (default: the current directory)",
    )
    arguments = parser.parse_args(argv)

    for line in run_notices(arguments.root):
        print(line)
    findings = run_all(arguments.root)
    print(format_findings(findings))
    print(SCOPE)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
