r"""The command line: one corpus root in, its clips on disk, an exit code a script reads.

**What it does.** Parses the arguments `studyforge narrate` takes, builds the
one `NarrateClient`, runs `stage.narrate_corpus`, prints the report and returns
the exit code.

**How you use it.** `main(argv) -> int`, and `python3 -m studyforge.cli.narrate`.
⭐ The dispatcher registers this same callable as the `narrate` verb.

**Depends on.** `cli.narrate.stage`, `cli.narrate.report`, `narrate.client` for
the client and its one socket-opening transport, `validate.cli` for `UNUSABLE`,
and `argparse`.

## ⛔ `--voice` is REQUIRED and has NO DEFAULT

⚠️ **The manifest declares no voice, and `Conditions` refuses an unstated one on
purpose**: a record written under the service's default cannot say what its
clips were made under. ⭐ So the person running the command names it, exactly
as `studyforge build` makes them name `--out`. `--format` defaults to `mp3`,
the one format the service's contract offers; `--service` defaults to the
loopback address that component publishes.

⛔ **Order is `narrate` then `build`** (`E09` § W202 answer 3). A build never
synthesises; this is the only verb that probes the service or writes clips.

⛔ **No traceback for anything a person can cause by typing**: a missing root,
an unreadable corpus or record, and an absent service each print a sentence
and exit `2`. ⚠️ `PersonalDataLeak` is deliberately NOT caught (Ruling 58).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from studyforge.cli.narrate.report import exit_code, lines
from studyforge.cli.narrate.stage import narrate_corpus
from studyforge.narrate.client import NarrateClient, over_http
from studyforge.narrate.speakable import SpeakableError
from studyforge.narrate.synth import StateError
from studyforge.validate.cli import UNUSABLE

#: The one format `narrate-service`'s `consuming.json` offers (`api.formats`).
DEFAULT_FORMAT = "mp3"

#: Where `narrate-service` publishes itself: loopback only, never all interfaces.
DEFAULT_SERVICE = "http://127.0.0.1:8870"


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser, so a test can read the interface."""
    parser = argparse.ArgumentParser(
        prog="studyforge narrate",
        description=(
            "Synthesise one corpus's narration from a running narration service: "
            "clips are placed beside the material and recorded, and a re-run with "
            "nothing changed requests nothing. Run it before `studyforge build`."
        ),
    )
    parser.add_argument("root", help="the corpus root — the directory holding corpus.json")
    parser.add_argument(
        "--voice",
        required=True,
        help=(
            "the voice every clip is synthesised in. Required and with no default: "
            "the record must say what its clips were made under"
        ),
    )
    parser.add_argument(
        "--format",
        dest="fmt",
        default=DEFAULT_FORMAT,
        help=f"the audio format to ask for (default {DEFAULT_FORMAT})",
    )
    parser.add_argument(
        "--service",
        default=DEFAULT_SERVICE,
        metavar="URL",
        help=f"where the narration service answers (default {DEFAULT_SERVICE})",
    )
    return parser


def main(argv: list[str] | None = None, out=None) -> int:
    """Narrate one corpus and return an exit code."""
    import sys

    stream = sys.stdout if out is None else out
    arguments = build_parser().parse_args(argv)
    root = Path(arguments.root)
    if not root.is_dir():
        # ⛔ Names what was asked for, not the absolute path it resolved to (R7).
        print(f"{arguments.root}: not a directory", file=stream)
        return UNUSABLE
    try:
        client = NarrateClient(
            arguments.service, voice=arguments.voice, fmt=arguments.fmt, transport=over_http
        )
        narrated = narrate_corpus(root, client, voice=arguments.voice, fmt=arguments.fmt)
    except (ValueError, SpeakableError, StateError) as refusal:
        # ⭐ `BuildError` and the builder's `ContentError` are both `ValueError`s
        # and name the record rather than the path; so do `Conditions`' own.
        print(str(refusal), file=stream)
        return UNUSABLE
    for line in lines(narrated, arguments.root):
        print(line, file=stream)
    return exit_code(narrated)
