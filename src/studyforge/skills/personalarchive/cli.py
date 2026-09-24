"""The skill's command line: `python3 -m studyforge.skills.personalarchive export|import`.

**What it does.** Parses `export <corpus-root> <archive-file> --for owner|sharing` and
`import <archive-file> <corpus-root>`, and hands each one to the function that does it.

**How you use it.** `main(argv) -> int`, and `python3 -m studyforge.skills.personalarchive`.
`build_parser()` returns the parser, so a test can read the interface.

**Depends on.** this package's `export`, `restore` and `layout`, and `argparse`.

⛔ **`--for` is required and has no default.** Whether an archive carries progress is
the exporter's explicit choice, never a default that leaks (R7).
"""

from __future__ import annotations

import argparse

from studyforge.skills.personalarchive.export import export
from studyforge.skills.personalarchive.layout import KINDS
from studyforge.skills.personalarchive.restore import import_archive

#: How the skill is invoked. ⛔ Not a verb: the CLI's verb table is the only minter of those.
PROG = "python3 -m studyforge.skills.personalarchive"


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser, so a test can read the interface."""
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Export a corpus with or without its progress, or import one and merge it.",
    )
    commands = parser.add_subparsers(dest="command", required=True, metavar="{export,import}")
    out = commands.add_parser("export", help="write a corpus into a new archive file")
    out.add_argument("root", help="the corpus root, the directory holding corpus.json")
    out.add_argument("archive", help="the archive file to create; it must not exist")
    out.add_argument(
        "--for",
        dest="kind",
        required=True,
        choices=KINDS,
        help="owner carries your progress; sharing carries none. There is no default",
    )
    into = commands.add_parser("import", help="merge an archive file into a corpus root")
    into.add_argument("archive", help="the archive file to read")
    into.add_argument("root", help="an existing directory, empty or holding the same corpus")
    return parser


def main(argv: list[str] | None = None, out=None) -> int:
    """Run one export or import and return its exit code."""
    arguments = build_parser().parse_args(argv)
    if arguments.command == "export":
        return export(arguments.root, arguments.archive, kind=arguments.kind, stream=out)
    return import_archive(arguments.archive, arguments.root, stream=out)
