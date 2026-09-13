r"""The command line: one root in, one site on disk, an exit code a script reads.

**What it does.** Parses the arguments `studyforge build` takes, calls
`generate.write_site`, prints what was written and what was refused, and
returns the exit code.

**How you use it.** `main(argv) -> int`, and `python3 -m studyforge.cli.site`.
⭐ The dispatcher registers this same callable as the `build` verb, so the two
cannot disagree about what the command does.

**Depends on.** `generate.write_site` and its `RAISES`, `cli.site.report`,
`validate.cli` for `UNUSABLE`, and `argparse`.

## ⛔ `--out` is REQUIRED and has NO DEFAULT

⚠️ **Where a build writes is an open decision and this command does not answer
it.** `generate.write_site` takes `into` as a required argument for that
reason, and a default here would answer by convention what nobody has ruled —
inside the corpus, beside it, or somewhere a caller names. ⭐ **Requiring the
flag defers the decision to the person running the command**, which is the only
form of "unanswered" a command can actually have.

⛔ **Exit codes are usable from a script** and mean one thing each: `0` the
whole site was written, `1` a path was refused — something that is not this
build's own output already existed and was left alone (R3), or the plan found
a path two artifacts claim and nothing was written (`W254`) — `2` the tool
could not run at all.
⚠️ The third is `validate`'s own, imported rather than respelled. ⭐ **A rebuild
that replaced only its own previous answer exits `0`** — otherwise *edit a
lesson, build again* would be a failure to every script that ran it.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from studyforge.cli.plan import plan_for
from studyforge.cli.site.report import exit_code, lines
from studyforge.generate import RAISES, write_site
from studyforge.validate.cli import UNUSABLE
from studyforge.validate.paths import RULE_DUPLICATE_PATH
from studyforge.validate.report import INVALID


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
    claimed = [r for r in plan_for(root).refusals if r.rule == RULE_DUPLICATE_PATH]
    if claimed:
        # ⛔ `W254`, clause 3: refused from the plan BEFORE anything is written,
        # naming both claimants, never resolved by whichever is written last.
        for refusal in claimed:
            print(refusal.line(), file=stream)
        print(
            f"build refused: {len(claimed)} path(s) are claimed by two artifacts, "
            f"so nothing was written",
            file=stream,
        )
        return INVALID
    try:
        written = write_site(root, Path(arguments.out))
    except RAISES as refusal:
        # ⛔ **The package's own tuple, never a list retyped here** (`W212`).
        # Catching `BuildError` alone let `PersonalDataLeak` out as a traceback
        # naming absolute paths (R7). ⛔ The message alone, with no path
        # prepended: each refusal already names the record it refused, and a
        # prefix naming the corpus root would misattribute one about `--out`.
        print(str(refusal), file=stream)
        return UNUSABLE
    for line in lines(written, arguments.root, arguments.out):
        print(line, file=stream)
    return exit_code(written)
