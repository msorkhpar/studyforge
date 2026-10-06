r"""The `exercises` verb: say which authored units went stale, and remove them when asked.

**What it does.** `stale` lists every authored unit whose coverage report no
longer describes it, each with why (`skills.exercises.REASONS`) and the
practice counterpart that goes with it, then a total line. ⭐ **It changes
nothing** unless `--remove` is given, and then it removes exactly the listed
folders, only when git could restore them (`skills.exercises.remove_stale`).

**How you use it.**

    studyforge exercises stale <corpus-root>
    studyforge exercises stale <corpus-root> --remove

`main(argv) -> int` is the callable the dispatcher registers.

**Depends on.** `skills.exercises` for the reading and the removal,
`archive.scrub` for R7 so a printed line names no home, `exitcodes` and
`validate.report` for the exit codes, and `argparse`.

⛔ **Exit codes are usable from a script**: `0` nothing is stale; `1` at least
one unit is stale, each named — with `--remove` too, since every page they
were authored from is still owed a pass; `2` the root is not a directory, a
report carries personal data, or a removal was refused and nothing was
removed.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from studyforge.archive.scrub import PersonalDataLeak, scrub
from studyforge.exitcodes import UNUSABLE
from studyforge.skills.exercises import AuthoringError, remove_stale, stale_units
from studyforge.validate.report import INVALID, OK

#: What a corpus with nothing stale says.
CLEAN = "stale: none; every authored unit still describes its page, its test files and its plan"


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser, so a test can read the interface."""
    parser = argparse.ArgumentParser(
        prog="studyforge exercises",
        description="Read and tend a corpus's authored exercises.",
    )
    actions = parser.add_subparsers(dest="action", required=True, metavar="ACTION")
    stale = actions.add_parser(
        "stale",
        help="list every authored unit that went stale, changing nothing",
        description=(
            "List every authored unit whose page, test files, plan or contract version "
            "moved since it was authored, with the practice folder that goes with it."
        ),
    )
    stale.add_argument("root", help="the corpus root, the directory holding corpus.json")
    stale.add_argument(
        "--remove",
        action="store_true",
        help=(
            "remove exactly the listed folders, only when the corpus is a git work tree "
            "with nothing staged and every file in them tracked and unmodified"
        ),
    )
    return parser


def main(argv: list[str] | None = None, out=None) -> int:
    """List the corpus's stale units, remove them when asked, and return an exit code."""
    import sys

    stream = sys.stdout if out is None else out
    arguments = build_parser().parse_args(argv)
    root = Path(arguments.root)
    if not root.is_dir():
        print(scrub(f"{arguments.root}: not a directory"), file=stream, flush=True)
        return UNUSABLE
    try:
        found = stale_units(root)
        removed = remove_stale(root, found) if arguments.remove else ()
    except (AuthoringError, PersonalDataLeak) as refused:
        print(scrub(str(refused)), file=stream, flush=True)
        return UNUSABLE
    for one in found:
        print(f"stale  {one.unit}: {one.says}", file=stream)
        print(f"       with {one.practice}", file=stream)
    for folder in removed:
        print(f"removed  {folder}", file=stream)
    if not found:
        print(CLEAN, file=stream, flush=True)
        return OK
    total = f"{len(found)} authored unit(s) are stale"
    tail = "removed; author their pages again" if removed else "nothing was changed"
    print(f"{total}: {tail}", file=stream, flush=True)
    return INVALID
