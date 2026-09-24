"""The skill's command line: the arguments `python3 -m studyforge.skills.buildserve` takes.

**What it does.** Parses a corpus root, a required `--out`, an optional
`--voice`, `--service`, `--port` and `--narration` / `--no-narration` (`W460`: the
user's answer to whether the site speaks), and hands them to `build_and_serve`.

**How you use it.** `main(argv) -> int`, and `python3 -m studyforge.skills.buildserve`.
`build_parser()` returns the parser, so a test can read the interface.

**Depends on.** `skills.buildserve.run` and `argparse`.

⛔ **`--out` is required and has no default**, for the reason `studyforge build`
gives: where generated output belongs is the corpus owner's decision.
"""

from __future__ import annotations

import argparse

from studyforge.skills.buildserve.run import build_and_serve

#: How the skill is invoked. ⛔ Not a verb: `SF-40`'s table is the only minter of those.
PROG = "python3 -m studyforge.skills.buildserve"


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser, so a test can read the interface."""
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=(
            "Validate, optionally narrate, build and serve one corpus through the "
            "studyforge verbs, reporting what is missing and what still works."
        ),
    )
    parser.add_argument("root", help="the corpus root — the directory holding corpus.json")
    parser.add_argument(
        "--out",
        required=True,
        metavar="DIR",
        help="an existing directory the site is built into and served from; no default",
    )
    parser.add_argument("--voice", help="narrate first, in this voice")
    parser.add_argument("--service", metavar="URL", help="where the narration service answers")
    parser.add_argument("--port", type=int, help="the loopback port (0 picks a free one)")
    parser.add_argument(
        "--narration",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=(
            "the user's answer: voice the site, or leave narration out (--no-narration) "
            "with every clip kept on disk. Default: corpus.json's `narration`"
        ),
    )
    return parser


def main(argv: list[str] | None = None, out=None) -> int:
    """Run the skill once and return its exit code."""
    arguments = build_parser().parse_args(argv)
    return build_and_serve(
        arguments.root,
        arguments.out,
        voice=arguments.voice,
        service=arguments.service,
        port=arguments.port,
        narration=arguments.narration,
        stream=out,
    )
