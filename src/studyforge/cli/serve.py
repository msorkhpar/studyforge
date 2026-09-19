r"""The `serve` verb: the CLI stage that starts what `studyforge.serve` built.

**What it does.** Parses the arguments `studyforge serve` takes, finds every
corpus under the root it is given (`serve.discovery`), checks that each holds
every page it declares, binds `serve.instance` on loopback and serves until it is
stopped. Given `--site`, it serves that one built directory for the one corpus
at the root instead — with Run and Submit, as the root form has them (`W371`). Serving the bytes is `studyforge.serve`'s; ⛔ this module is
its caller and never a second author of it.

**How you use it.**

    studyforge build <corpus-root> --out <corpus-root>     # built in place, per corpus
    studyforge serve <root> [--port N]                     # every corpus under <root>

    studyforge build <corpus-root> --out <directory>
    studyforge serve <corpus-root> --site <directory> [--port N]

`main(argv) -> int` is the callable the dispatcher registers. Ctrl-C (or
`SIGTERM`) stops it and exits `0`. ⚠️ `started=` hands the bound server to a
caller before serving begins, which is how a test stops the verb in-process.

**Depends on.** `serve.instance` and `serve.discovery` for a root,
`serve.app`, `serve.routes.content`, `serve.routes.run` and `.runs`, and
`corpus.discovery`'s scan for `--site`, `generate.declarations` for
the corpus, `progress` for the store's one spelling, `validate` for the exit
codes, and `argparse`. ⛔ Nothing here knows any source (R1).

## ⛔ With no `--site`, NO CONFIGURED PATH (`W230`)

⭐ **The root is the only input**: every `corpus.json` under it is a corpus, each
is served from where it sits, and one instance answers them all — content, state
and pages. ⛔ There is no list of mounts to give it: the manifests on disk are
the list. Tested in `tests/studyforge/cli/test_serve_root.py`.

⚠️ **`--site` stays, as an override for ONE corpus built somewhere else.** `build`
takes `--out` with no default, so a site can live outside its corpus, and only a
named directory reaches that. It names one directory for one corpus and adds no
mount beside the root's.

## ⛔ `--site` answers Run and Submit (`W371`, closing `SF-22/2`)

⭐ **The `run` namespace is registered in both forms**, as the one writer: the
build-and-serve skill always serves `--site`, and a site served for an exercised
corpus that offered no execution was reported `toolchain` although the root form
ran it. A run's command is read from the corpus's unit documents and its outcome
is recorded in the corpus's own progress store; ⛔ nothing is written into the
site, and no discovery cache is written into the corpus root. Tested in
`tests/studyforge/cli/test_serve_site_run.py`.

## ⛔ The site is BUILT first, and it never needs this command

⭐ **R8: a built site opens over `file://` with no server.** A served origin
adds the API; it is never a prerequisite for reading. So this verb serves what
`studyforge build` wrote and writes nothing into it, and `--site` has no default
for the reason `build`'s `--out` is: where a build writes is the corpus owner's
decision. `tests/studyforge/cli/test_serve_floor.py` asserts the floor rather
than assuming it.

⛔ **Exit codes are `build`'s**: `0` served and stopped cleanly, `1` a corpus
declares a page nobody built (each named; nothing is bound), `2` the tool could
not run — a missing directory, no servable corpus, an unreadable corpus, a port
it cannot listen on.

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
from functools import partial
from pathlib import Path, PurePosixPath

from studyforge.archive.scrub import scrub
from studyforge.corpus.discovery import assemble
from studyforge.corpus.discovery import scan_sha256 as digest_of
from studyforge.generate import RAISES
from studyforge.generate.declarations import read_corpus
from studyforge.progress import store_dir
from studyforge.serve import RAISES as REFUSED
from studyforge.serve.app import DEFAULT_PORT, ServingServer, make_server
from studyforge.serve.discovery import Discovered, ServedCorpus, discover
from studyforge.serve.instance import instance_of
from studyforge.serve.routes import run, runs
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
            "Serve every built corpus under a root on loopback, adding the API. "
            "The site still opens without this command; stop it with Ctrl-C."
        ),
    )
    parser.add_argument(
        "root",
        help=(
            "a directory; every corpus.json under it is served where it sits. "
            "With --site, the corpus root — the directory holding corpus.json"
        ),
    )
    parser.add_argument(
        "--site",
        default=None,
        metavar="DIR",
        help=(
            "serve only this corpus, from the directory `studyforge build --out` wrote. "
            "No default: where generated output belongs is the corpus owner's decision"
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
    if arguments.site is None:
        return _serve_root(arguments, say, started)
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
    content = CorpusContent(corpus)
    execution = _execution(corpus, root, content)
    try:
        server = make_server(
            site,
            content,
            port=arguments.port,
            namespaces=execution,
            private=_inside(store_dir(root)),
            log=say,
            writers=tuple(execution),
        )
    except OSError as refusal:
        return _could_not_listen(arguments.port, refusal, say)
    host, port = server.server_address[:2]
    say(f"serve http://{host}:{port}/  site {arguments.site}  corpus {arguments.root}")
    return _serve(server, say, started)


def _serve_root(
    arguments: argparse.Namespace,
    say: Callable[[str], None],
    started: Callable[[ServingServer], None] | None,
) -> int:
    """Serve every corpus discovered under the root, with no configured path (`W230`)."""
    if not Path(arguments.root).is_dir():
        say(f"{arguments.root}: not a directory")
        return UNUSABLE
    try:
        discovered = discover(arguments.root)
    except REFUSED as refusal:
        say(str(refusal))
        return UNUSABLE
    report = [scrub(line) for line in discovered.report]
    unbuilt = sorted(
        (served.relative / page).as_posix()
        for served in discovered.corpora
        for page in _unbuilt(served.corpus, served.root)
    )
    if unbuilt:
        for line in (*report, *(f"unbuilt {page}  {NOT_BUILT}" for page in unbuilt)):
            say(line)
        return INVALID
    try:
        server = instance_of(discovered, port=arguments.port, log=say)
    except OSError as refusal:
        return _could_not_listen(arguments.port, refusal, say)
    host, port = server.server_address[:2]
    # ⭐ The listening line is FIRST, as in the `--site` form: a caller reads the port off it.
    say(f"serve http://{host}:{port}/  root {arguments.root}")
    for served in discovered.corpora:
        index = served.href(served.corpus.shared.root_index)
        say(f"corpus {served.source} http://{host}:{port}{index}")
    for line in report:
        say(line)
    return _serve(server, say, started)


def _could_not_listen(port: int, refusal: OSError, say: Callable[[str], None]) -> int:
    """Report a port the server could not bind, and return `2`."""
    # ⚠️ `strerror` only: an `OSError`'s full text can carry a path (R7).
    reason = refusal.strerror or type(refusal).__name__
    say(f"port {port}: could not listen ({reason})")
    return UNUSABLE


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


def _execution(corpus: object, root: Path, content: CorpusContent) -> dict:
    """Return the run namespace over the one corpus `--site` serves (`W371`).

    ⭐ Every namespace returned is a writer — `run` is the one — so the caller
    registers exactly these as writers and spells none of its own.

    ⭐ **The root form's wiring, over one corpus**: `serve.instance.instance_of`
    registers `run` over every corpus a discovery found, and this registers it
    over the corpus at `root`, whose unit documents `content` reads. A run's
    command is read from those documents and its outcome is recorded in the
    corpus's own progress store — never in the site.

    ⛔ **No cache is judged, so nothing is written into the corpus root**: the
    scan here only gives the served corpus its startup reading, and `--site`
    serves a site that may sit anywhere, over a corpus it must not touch.
    """
    depths = {corpus.manifest.source: corpus.manifest.depth}
    startup = assemble(root, depths)
    served = ServedCorpus(corpus, root, PurePosixPath("."), startup, digest_of(startup.site))
    live = runs.Runs(Discovered(root, (served,), ()), {served.source: content})
    return {run.NAMESPACE: partial(run.route, live)}


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
