r"""The `serve` verb: the CLI stage that starts what `studyforge.serve` built.

**What it does.** Parses the arguments `studyforge serve` takes, reads the
corpus's declarations, checks that the built site holds every page the corpus
declares, binds `serve.app.make_server` on loopback and serves until it is
stopped. Serving the bytes is `studyforge.serve`'s; ⛔ this module is its
caller and never a second author of it.

**How you use it.**

    studyforge build <corpus-root> --out <directory>
    studyforge serve <corpus-root> --site <directory> [--port N]

`main(argv) -> int` is the callable the dispatcher registers. Ctrl-C (or
`SIGTERM`) stops it and exits `0`. ⚠️ `started=` hands the bound server to a
caller before serving begins, which is how a test stops the verb in-process.

**Depends on.** `serve.app` and `serve.routes.content` for the server,
`generate.declarations` for the corpus, `progress` for the store's one
spelling, `validate` for the exit codes, and `argparse`. ⛔ Nothing here knows
any source (R1).

## ⛔ The site is BUILT first, and it never needs this command

⭐ **R8: a built site opens over `file://` with no server.** A served origin
adds the API; it is never a prerequisite for reading. So this verb serves what
`studyforge build` wrote and writes nothing into it, and `--site` is required
with no default for the reason `build`'s `--out` is: where a build writes is
the corpus owner's decision. `tests/studyforge/cli/test_serve_floor.py` asserts
the floor rather than assuming it.

⛔ **Exit codes are `build`'s**: `0` served and stopped cleanly, `1` the corpus
declares a page the site does not hold (nothing is bound), `2` the tool could
not run — a missing directory, an unreadable corpus, a port it cannot listen on.

## ⛔ The Docker socket is never mounted into, or reachable from, this process

Spec §8.3. Not behind a flag, not "only locally": the parser offers no option
naming one, this module imports no Docker client and starts no process, and a
socket the environment points at is never connected to — each asserted, in
`tests/studyforge/cli/test_serve.py` and `test_serve_process.py`.

⚠️ **`private=` names the reader's progress store** (`SF-21`) by its resolved
path, so a `--site` that sits over the corpus's generated root still cannot
serve the record, which the static mount's own prefix check reads relative to
the site root and would not see.
"""

from __future__ import annotations

import argparse
import signal
import threading
from collections.abc import Callable
from pathlib import Path

from studyforge.generate import RAISES
from studyforge.generate.declarations import read_corpus
from studyforge.progress import store_dir
from studyforge.serve.app import DEFAULT_PORT, ServingServer, make_server
from studyforge.serve.routes.content import CorpusContent
from studyforge.validate.cli import UNUSABLE
from studyforge.validate.report import INVALID, OK

#: What an unbuilt page says. ⭐ It names the command that fixes it.
NOT_BUILT = "the corpus declares this page and the site holds no file there; build it first"

#: What a clean stop says.
STOPPED = "stopped"


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser, so a test can read the interface."""
    parser = argparse.ArgumentParser(
        prog="studyforge serve",
        description=(
            "Serve one corpus's built site on loopback, adding the content API. "
            "The site still opens without this command; stop it with Ctrl-C."
        ),
    )
    parser.add_argument("root", help="the corpus root — the directory holding corpus.json")
    parser.add_argument(
        "--site",
        required=True,
        metavar="DIR",
        help=(
            "the directory `studyforge build --out` wrote. Required and with no "
            "default: where generated output belongs is the corpus owner's decision"
        ),
    )
    parser.add_argument(
        "--port",
        type=_port,
        default=DEFAULT_PORT,
        help=f"the loopback port to listen on (default {DEFAULT_PORT}; 0 picks a free one)",
    )
    return parser


def main(
    argv: list[str] | None = None,
    out=None,
    *,
    started: Callable[[ServingServer], None] | None = None,
) -> int:
    """Serve one built site until stopped, and return an exit code."""
    import sys

    stream = sys.stdout if out is None else out

    def say(line: str) -> None:
        print(line, file=stream, flush=True)

    arguments = build_parser().parse_args(argv)
    root, site = Path(arguments.root), Path(arguments.site)
    for given, path in ((arguments.root, root), (arguments.site, site)):
        if not path.is_dir():
            # ⛔ What was asked for, never the absolute path it resolved to (R7).
            say(f"{given}: not a directory")
            return UNUSABLE
    try:
        corpus = read_corpus(root)
    except RAISES as refusal:
        say(str(refusal))
        return UNUSABLE
    unbuilt = _unbuilt(corpus, site)
    if unbuilt:
        for page in unbuilt:
            say(f"unbuilt {page}  {NOT_BUILT}")
        return INVALID
    try:
        server = make_server(
            site,
            CorpusContent(corpus),
            port=arguments.port,
            private=_inside(store_dir(root)),
            log=say,
        )
    except OSError as refusal:
        # ⚠️ `strerror` only: an `OSError`'s full text can carry a path (R7).
        reason = refusal.strerror or type(refusal).__name__
        say(f"port {arguments.port}: could not listen ({reason})")
        return UNUSABLE
    host, port = server.server_address[:2]
    say(f"serve http://{host}:{port}/  site {arguments.site}  corpus {arguments.root}")
    return _serve(server, say, started)


def _port(text: str) -> int:
    """Parse a TCP port, refusing one out of range here rather than at `bind`."""
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a port: {text}") from None
    if not 0 <= value <= 65535:
        raise argparse.ArgumentTypeError(f"not a port: {text}")
    return value


def _unbuilt(corpus: object, site: Path) -> list[str]:
    """Every page the corpus declares that the site holds no file for, sorted.

    ⭐ **The plan's own enumeration**: the footprint's `.html` files are exactly
    the pages a build writes (`generate/site.py`), and the root index is named
    beside them so a footprint that owns nothing still checks the one page a
    reader opens first.
    """
    pages = {corpus.shared.root_index} | {
        path for path in corpus.footprint.files if path.suffix == ".html"
    }
    return sorted(str(page) for page in pages if not (site / page).is_file())


def _inside(directory: Path) -> Callable[[Path], bool]:
    """Return a `private=` predicate: whether a resolved path is inside `directory`."""
    base = directory.resolve()
    return lambda path: Path(path).resolve().is_relative_to(base)


def _serve(
    server: ServingServer,
    say: Callable[[str], None],
    started: Callable[[ServingServer], None] | None,
) -> int:
    """Serve until shut down or interrupted; close the socket on every way out."""
    restore = _stop_on_terminate()
    try:
        if started is not None:
            started(server)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        restore()
        server.server_close()
    say(STOPPED)
    return OK


def _stop_on_terminate() -> Callable[[], None]:
    """Make `SIGTERM` stop the server as Ctrl-C does; return the undo.

    ⚠️ Only the main thread may install a handler, so a verb run from a test's
    thread keeps the process's own and is stopped through `started=` instead.
    """
    if threading.current_thread() is not threading.main_thread():
        return lambda: None
    previous = signal.getsignal(signal.SIGTERM)

    def interrupt(signum: int, frame: object) -> None:
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, interrupt)
    return lambda: signal.signal(signal.SIGTERM, previous)
