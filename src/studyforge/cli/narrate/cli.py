r"""The command line: one corpus root in, its clips on disk, an exit code a script reads.

**What it does.** Parses the arguments `studyforge narrate` takes, builds the
one `NarrateClient`, runs `stage.narrate_corpus`, prints the report and returns
the exit code.

**How you use it.** `main(argv) -> int`, and `python3 -m studyforge.cli.narrate`.
`--prune` in place of `--voice` runs `prune.prune_corpus` instead; `--pack` and
`--publish` run `release.pack_command` and `release.publish_command`.
⭐ The dispatcher registers this same callable as the `narrate` verb.

**Depends on.** `cli.narrate.stage`, `cli.narrate.prune`, `cli.narrate.release`,
`cli.narrate.report`, `narrate.client` for
the client, `narrate.wire` for its one socket-opening transport, `validate.cli` for `UNUSABLE`,
and `argparse`.

## ⛔ `--voice` is REQUIRED and has NO DEFAULT

⚠️ **The manifest declares no voice, and `Conditions` refuses an unstated one on
purpose**: a record written under the service's default cannot say what its
clips were made under. ⭐ So the person running the command names it, exactly
as `studyforge build` makes them name `--out`. `--format` defaults to `mp3`,
the one format the service's contract offers; `--service` defaults to the
loopback address that component publishes.

## ⛔ `--prune` is its own request, and EXCLUSIVE with `--voice`

⭐ One of the two is required and the parser refuses both, so a run that
synthesises cannot prune and a prune cannot synthesise (R3: narration deletes
nothing except through an explicit prune). ⛔ **The prune branch builds no
client**, so it can make no request.

## ⛔ `--pack` and `--publish` are requests of their own, and build no client

⭐ Four requests, exactly one per run: `--voice`, `--prune`, `--pack`,
`--publish`. The two release requests read the record and the disk, never the
service. ⛔ `--publish` is a dry run and nothing else: it prints the `gh`
command that uploads, and the owner runs it. This verb publishes nothing.

⛔ **Order is `narrate` then `build`** (a build only copies clips). A build never
synthesises; this is the only verb that probes the service or writes clips.

⛔ **No traceback for anything a person can cause by typing**: a missing root,
an unreadable corpus or record, and an absent service each print a sentence
and exit `2`. ⚠️ `PersonalDataLeak` is deliberately NOT caught.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from studyforge.cli.narrate.prune import prune_corpus
from studyforge.cli.narrate.release import pack_command, publish_command
from studyforge.cli.narrate.report import exit_code, lines, prune_exit_code, prune_lines
from studyforge.cli.narrate.stage import narrate_corpus
from studyforge.narrate.release import DEFAULT_TAG
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
    request = parser.add_mutually_exclusive_group(required=True)
    request.add_argument(
        "--voice",
        help=(
            "the voice every clip is synthesised in. Required to narrate and with no "
            "default: the record must say what its clips were made under"
        ),
    )
    request.add_argument(
        "--prune",
        action="store_true",
        help=(
            "narrate nothing: delete the clips of record entries this corpus no longer "
            "produces, over a walk of the whole corpus. Requests nothing from any service"
        ),
    )
    request.add_argument(
        "--pack",
        metavar="DIR",
        help=(
            "narrate nothing: pack the clips the record locates into release volumes and a "
            "SHA256SUMS in DIR, outside the corpus, and write the restore scripts into "
            "the corpus"
        ),
    )
    request.add_argument(
        "--publish",
        metavar="DIR",
        help=(
            "a dry run: check the volumes a pack wrote in DIR and print the one gh command "
            "that publishes them as a GitHub release of the checkout's origin. Uploads "
            "nothing; you run that command yourself, with your own login"
        ),
    )
    parser.add_argument(
        "--tag",
        default=DEFAULT_TAG,
        help=f"the release tag, with --pack and --publish (default {DEFAULT_TAG})",
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
    if arguments.pack is not None or arguments.publish is not None:
        report, code = _release(arguments)
        for line in report:
            print(line, file=stream)
        return code
    try:
        if arguments.prune:
            # ⛔ No client on this branch: a prune makes no request.
            pruned = prune_corpus(root)
            report, code = prune_lines(pruned, arguments.root), prune_exit_code(pruned)
        else:
            # ⛔ Imported HERE and never at module level: the
            # dispatcher imports every verb, so a module-level import put the HTTP
            # client in every `studyforge.cli.*` import, `cli/plan` included.
            from studyforge.narrate.client import NarrateClient
            from studyforge.narrate.wire import over_http

            client = NarrateClient(
                arguments.service, voice=arguments.voice, fmt=arguments.fmt, transport=over_http
            )
            narrated = narrate_corpus(root, client, voice=arguments.voice, fmt=arguments.fmt)
            report, code = lines(narrated, arguments.root), exit_code(narrated)
    except (ValueError, SpeakableError, StateError) as refusal:
        # ⭐ `BuildError` and the builder's `ContentError` are both `ValueError`s
        # and name the record rather than the path; so do `Conditions`' own.
        print(str(refusal), file=stream)
        return UNUSABLE
    for line in report:
        print(line, file=stream)
    return code


def _release(arguments: argparse.Namespace) -> tuple[list[str], int]:
    """Run `--pack` or `--publish`. ⛔ Neither builds a client, so neither reaches the service."""
    if arguments.pack is not None:
        return pack_command(arguments.root, arguments.pack, arguments.tag)
    return publish_command(arguments.root, arguments.publish, arguments.tag)
