r"""The command line: one root in, one site on disk, an exit code a script reads.

**What it does.** Parses the arguments `studyforge build` takes, calls
`generate.write_site`, prints what was written and what was refused, and
returns the exit code.

**How you use it.** `main(argv) -> int`, and `python3 -m studyforge.cli.site`.
⭐ The dispatcher registers this same callable as the `build` verb, so the two
cannot disagree about what the command does.

**Depends on.** `generate.write_site`, `cli.site.report`, `validate.cli` for
`UNUSABLE`, and `argparse`.

## ⛔ `--out` is REQUIRED and has NO DEFAULT

⚠️ **Where a build writes is an open decision and this command does not answer
it.** `generate.write_site` takes `into` as a required argument for that
reason, and a default here would answer by convention what nobody has ruled —
inside the corpus, beside it, or somewhere a caller names. ⭐ **Requiring the
flag defers the decision to the person running the command**, which is the only
form of "unanswered" a command can actually have.

⛔ **Exit codes are usable from a script** and mean one thing each: `0` the
whole site was written, `1` something that is not this build's own output
already existed and was left alone (R3), `2` the tool could not run at all.
⚠️ The third is `validate`'s own, imported rather than respelled. ⭐ **A rebuild
that replaced only its own previous answer exits `0`** — otherwise *edit a
lesson, build again* would be a failure to every script that ran it.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from studyforge.cli.site.report import exit_code, lines
from studyforge.generate import BuildError, write_site
from studyforge.validate.cli import UNUSABLE


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser, so a test can read the interface."""
    parser = argparse.ArgumentParser(
        prog="studyforge build",
        description=(
            "Write one corpus's study site into a directory you name. A rebuild "
            "replaces this build's own previous output and nothing else: any other "
            "file already there is reported by name, not overwritten."
        ),
    )
    parser.add_argument("root", help="the corpus root — the directory holding corpus.json")
    parser.add_argument(
        "--out",
        required=True,
        metavar="DIR",
        help=(
            "the directory the site is written into. Required and with no default: "
            "where generated output belongs is the corpus owner's decision"
        ),
    )
    return parser


def main(argv: list[str] | None = None, out=None) -> int:
    """Build one corpus into the named directory and return an exit code."""
    import sys

    stream = sys.stdout if out is None else out
    arguments = build_parser().parse_args(argv)
    root = Path(arguments.root)
    if not root.is_dir():
        # ⛔ Names what was asked for and not the absolute path it resolved to
        # (R7), and refuses BEFORE anything is created under `--out`: a typo in
        # the corpus root must not leave a directory tree behind to clean up.
        print(f"{arguments.root}: not a directory", file=stream)
        return UNUSABLE
    try:
        written = write_site(root, Path(arguments.out))
    except BuildError as refusal:
        # ⛔ The message alone, with no path prepended: a `BuildError` already
        # names the record it refused, and a prefix naming the corpus root
        # would misattribute a refusal about `--out` to the corpus.
        print(str(refusal), file=stream)
        return UNUSABLE
    for line in lines(written, arguments.root, arguments.out):
        print(line, file=stream)
    return exit_code(written)
