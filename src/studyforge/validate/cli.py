r"""The command line: one root in, one report out, an exit code a script reads.

**What it does.** Parses the arguments `studyforge validate` takes, runs the
checks, prints the report and returns the exit code.

**How you use it.** `main(argv) -> int`, and `python3 -m studyforge.validate`.
⭐ The dispatcher registers this same callable as the `validate` verb, so the
two cannot disagree about what the command does.

**Depends on.** `validate.run`, `validate.report`, and `argparse`.

⛔ **Exit codes are usable from a script** and mean one thing each: `0` the
archive is valid, `1` it is not, `2` the tool could not run at all. A script
that cannot tell "invalid" from "you gave me a directory that does not exist"
will treat one as the other, and CI will go green on a typo.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from studyforge.validate.report import INVALID, OK
from studyforge.validate.run import validate

#: The tool could not run — not a verdict about any archive. ⛔ Deliberately
#: distinct from `INVALID`: a missing directory is a mistake in the invocation,
#: and reporting it as "invalid" teaches an adapter author to distrust the one
#: signal they have.
UNUSABLE = 2


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser, so a test can read the interface."""
    parser = argparse.ArgumentParser(
        prog="studyforge validate",
        description=(
            "Decide whether a corpus's archive is valid. This is an adapter's "
            "definition of done: exit 0 means the archive is acceptable."
        ),
    )
    parser.add_argument("root", help="the corpus root — the directory holding corpus.json")
    return parser


def main(argv: list[str] | None = None, out=None) -> int:
    """Run the checks over one corpus root and print every finding."""
    import sys

    stream = sys.stdout if out is None else out
    arguments = build_parser().parse_args(argv)
    root = Path(arguments.root)
    if not root.is_dir():
        # ⛔ Names what was asked for and not the absolute path it resolved to
        # (R7): a report is the most-pasted artifact this tool produces.
        print(f"{arguments.root}: not a directory", file=stream)
        return UNUSABLE
    report = validate(root)
    for line in report.lines():
        print(line, file=stream)
    return report.exit_code if report.exit_code in (OK, INVALID) else INVALID
