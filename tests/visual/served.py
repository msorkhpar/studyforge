"""A SERVED origin over a built tree, so the practice panel's controls exist to read.

**What it does.** Binds `studyforge.serve`'s own app on loopback over a tree
`site.build` already wrote, registers the `run` namespace the page's execution
client talks to, and hands back `http://` URLs into it. The serving process
inserts the run client into every HTML page it answers, exactly as it does for a
reader, so `window.studyforge.run.available()` is true and `practice.js` unhides
the panel's controls.

**How you use it.** `with served.serving(built_site) as origin:` then
`page.open(origin.url("depth2-unit-01"))`. `origin.runs` is the scripted far
side of the API: `runs.started` says a run is live, `runs.release` ends it, and
`runs.stopped` says whether Stop was pressed. `serving(..., windows=True)` also
answers the practice-editor route, so the panel builds real frames.

**Depends on.** `studyforge.serve.app`, `studyforge.serve.response` and
`studyforge.serve.routes.run` for the one spelling of the client's path, plus
`threading` and `contextlib`. ⛔ Nothing is imitated that the framework already
spells: the insertion, the headers, the loopback gate and the client file are
the real ones.

## ⛔ Why this exists, and it is not a convenience

⛔ **The practice panel's keyboard behaviour cannot be read over `file://`.**
Its controls ship `hidden` and are unhidden only where
`window.studyforge.run.available()` is true — which `run-client.js` answers from
`location.protocol`. ⭐ Over `file://` a check sees the panel with its controls
hidden and its offline note showing, and can assert its *structure* and never
its *behaviour*. ⚠️ *Full keyboard traversal of a unit page, including the
practice panel* needs a served origin.

⛔ **This does not retire `file://`, and nothing here may be read as doing so.**
R8's floor is a page opened by double-clicking it, every other clause in this
package is taken over `file://` deliberately, and `test_offline.py` is the check
that a page asks no origin for anything. ⭐ This is one MORE reading of the same
built bytes, taken where the reader who started the study server is.

## ⛔ What is real here, and what is a stand-in — said once, plainly

⭐ **Real:** the built page's bytes, `serve.app`'s static mount, the client
insertion in `serve.routes.assets`, the security gate, and `run-client.js`
itself — the file the run namespace serves, read from where the framework keeps
it. ⛔ **A stand-in:** what is BEHIND the API. `ScriptedRuns` answers the two
endpoints `run-client.js` calls with a scripted stream instead of starting a
process.

⚠️ **The seam is chosen and not convenient.** What this harness reads is the
PAGE — tab order, focus handoff, a live region — and the page talks to
`window.studyforge.run` and to nothing else (`practice.js`'s own first
paragraph). ⛔ A visual harness that started real processes, or a container,
would be measuring `execute` in a module whose subject is a keyboard; the real
route over a real runner is `tests/studyforge/serve/` and
`tests/studyforge/cli/test_serve_site_run.py`, and this never substitutes for
either.

## ⚠️ The tree served here is not a corpus, and the content namespace says so

`site.build` writes rendered pages, not an archive, so there is no corpus for
`routes.content` to read. ⭐ `_NoContent` declares nothing, which is the truth
about this tree; no page in it asks the content namespace for anything, and a
request that did would get the same `404` a key outside a real corpus gets.
"""

from __future__ import annotations

import contextlib
import re
import threading
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from studyforge.serve.app import ServingServer, make_server
from studyforge.serve.discovery import Discovered
from studyforge.serve.response import NO_STORE, TEXT_TYPE, Request, Response, error, json_response
from studyforge.serve.routes.run import (
    CLIENT,
    CLIENT_FILE,
    CLIENT_PATH,
    EDITOR,
    NAMESPACE,
    SCRIPT_TYPE,
    STOP,
)
from studyforge.serve.routes.runs import Runs
from tests.visual import site

#: What the scripted run writes before it waits. ⚠️ More than one line, because
#: the output region is a scrolling one and a single line never fills it.
SCRIPTED = ("Compiling the practice…", "Running the grader…", "1 test, 1 passed")

#: Seconds a scripted run waits to be released before it ends itself. ⛔ A bound
#: rather than a wait forever: a check that forgets to release must fail inside
#: the suite's own patience rather than hang the directory.
RELEASE_BOUND = 60.0

#: How a run ends, in the words `run-client.js` parses out of the last line.
EXIT_LINE = "--- exit {verdict} ---"

#: What a stopped run's verdict is, in the client's own vocabulary.
STOPPED = "stopped"

#: The fixture corpus whose subtree is served when a caller names none — the one
#: whose unit page carries a practice panel. ⛔ Derived from the built tree, not
#: typed: a page that moved corpora would red here rather than 404 quietly.
DEFAULT_CORPUS = site.corpus_of("depth2-unit-01")

#: What `serving(windows=True)` hands the panel as its two editor windows.
#:
#: ⛔ **`about:blank`, and the reason is this framework's own security posture
#: rather than convenience.** Every page this server answers carries
#: `frame-ancestors 'none'` and `X-Frame-Options: DENY` — correctly — so no page of the built tree
#: can be framed by
#: anything, including itself. ⭐ A blank document is SAME-ORIGIN with the page
#: that frames it, which is what lets a check mark the document INSIDE a frame
#: and read the mark back; a second real origin would be more lifelike and would
#: make that mark unreadable.
#:
#: ⭐ **Two DIFFERENT URLs**, because the whole of the two-window design is that
#: each window is told apart by its own URL and by nothing else.
#: ⚠️ **A stand-in for WHERE an editor is, and nothing more** — `ScriptedRuns`
#: starts no container, exactly as it starts no process. What a frame here can
#: establish is that it SURVIVES a transition, never what is inside one.
WINDOW_URLS = ("about:blank#main", "about:blank#test")

#: What this harness answers where a caller asked for no windows. ⛔ The real
#: route's own shape for *no editor over this practice*, so a panel reads the
#: absence the way it would on a machine with no editor running.
NO_WINDOWS = "no editor is running over this practice's own file"


class _NoContent:
    """A `ContentSource` over a tree that is not a corpus: it declares nothing."""

    def toc(self) -> str:
        """Return an empty contents document; nothing in this tree asks for one."""
        return ""

    def unit(self, key: str) -> str | None:  # noqa: ARG002 - the signature is the protocol
        """Return no material, because this tree holds an archive for no unit."""
        return None

    def declares(self, key: str) -> bool:  # noqa: ARG002 - the signature is the protocol
        """Say that no unit is declared here, which is what a rendered tree holds."""
        return False


class ScriptedRuns:
    """The far side of `studyforge.run`'s two endpoints, scripted rather than run.

    ⛔ **Nothing here starts a process**, and that is the whole reason a visual
    harness may register this namespace at all (spec §8.3 is about the serving
    process; this is the same posture in a test).

    ⭐ **A run is held open until it is released**, so a check can read the page
    MID-RUN — which is where the focus handoff lives: Stop exists only while a
    run is live, and a run that ended before the reading was taken would answer
    the question nobody asked.
    """

    def __init__(self) -> None:
        """Arm one scripted run; nothing is live until a page starts it."""
        #: Set once every scripted line has been flushed to the page.
        self.started = threading.Event()
        #: Set by a check, or by Stop, to let the run end.
        self.release = threading.Event()
        #: Whether Stop was pressed while the run was live.
        self.stopped = False
        #: Every path this namespace was asked for, in order.
        self.asked: list[str] = []
        #: Where this practice's two editor windows are, or `None` for no
        #: editor at all — which is what an ordinary origin here answers.
        self.windows: dict[str, dict[str, str]] | None = None
        #: ⭐ Where the index says each served corpus's editor is, by the
        #: `data-corpus` its pages carry — empty for no editor, which is what an
        #: ordinary origin here answers. ⛔ A page asks an editor's windows only
        #: of an editor the index names, so windows without this are never asked.
        self.editors: dict[str, dict[str, str]] = {}
        #: ⭐ What the SERVER says about the run just before the exit line, which
        #: is where `routes.runs.Outcome.record`'s own lines go and
        #: the only channel a built page has for a breakdown (R8).
        #: ⛔ Empty by default, so every check written before it reads the same
        #: stream it read before.
        self.said: tuple[str, ...] = ()

    def route(self, request: Request, rest: str) -> Response:
        """Answer one request under `/api/v1/run/`, the way the real route's shape does."""
        self.asked.append(f"{request.method} {rest}")
        if rest in ("", CLIENT):
            if request.method == "POST":
                return error(405, "the client is fetched, never posted to")
            if rest == CLIENT:
                headers = (("Content-Type", SCRIPT_TYPE), ("Cache-Control", NO_STORE))
                return Response(200, headers, CLIENT_FILE.read_bytes())
            index = {"resource": "run-index", "modes": ["run", "test"], EDITOR: self.editors}
            return json_response(200, index)
        if request.method != "POST":
            return error(405, "a run is started by POST")
        if rest == STOP:
            self.stopped = True
            self.release.set()
            return json_response(200, {"resource": "run-stop", "stopped": True})
        if rest.split("/")[1:2] == [EDITOR]:
            # ⛔ `<corpus>/editor/<practice>`, and the practice key carries its
            # own slashes — so the MODE is read at its fixed position rather
            # than by splitting the whole path into two.
            if self.windows is None:
                return error(404, NO_WINDOWS)
            return json_response(200, {"resource": "run-editor", **self.windows})
        headers = (("Content-Type", TEXT_TYPE), ("Cache-Control", NO_STORE))
        return Response(200, headers, stream=self._stream())

    def _stream(self) -> Iterator[bytes]:
        """Write every scripted line, wait to be released, then end with a verdict.

        ⚠️ `started` is set **between** two yields on purpose: the writer flushes
        each chunk before it asks for the next, so by the time this resumes the
        page has every scripted line. ⛔ A flag set before the first yield would
        be a check racing the socket.
        """
        for line in SCRIPTED:
            yield (line + "\n").encode("utf-8")
        self.started.set()
        self.release.wait(RELEASE_BOUND)
        # ⛔ BEFORE the exit line and AFTER the program's own output, which is
        # exactly where the real `Stream` yields what `Outcome.record` returns.
        for line in self.said:
            yield (line + "\n").encode("utf-8")
        verdict = STOPPED if self.stopped else "0"
        yield (EXIT_LINE.format(verdict=verdict) + "\n").encode("utf-8")


@dataclass
class Served:
    """One bound server over one corpus's subtree, and the URLs into it."""

    server: ServingServer
    built: site.Site
    corpus: str
    runs: ScriptedRuns
    log: list[str] = field(default_factory=list)

    @property
    def root(self) -> Path:
        """The directory this server answers from: one corpus's subtree."""
        return self.built.root / self.corpus

    @property
    def origin(self) -> str:
        """The origin this server is answering on, as a page would name it."""
        host, port = self.server.server_address[0], self.server.server_address[1]
        return f"http://{host}:{port}"

    def url(self, case: str, name: str | None = None) -> str:
        """The `http://` URL of one built page — the same bytes `site.url` names.

        ⛔ Refuses a page from another corpus's subtree rather than composing a
        URL that resolves to nothing: this server is rooted at one of them. ⭐ `name`
        reaches the same server by another loopback name (`localhost`).
        """
        where = site.corpus_of(case)
        if where != self.corpus:
            raise LookupError(f"{case} is in {where}, and this origin serves {self.corpus}")
        origin = self.origin if name is None else f"http://{name}:{self.server.server_address[1]}"
        return f"{origin}/{self.built.path(case).relative_to(self.root).as_posix()}"


def _corpora(root: Path) -> tuple[str, ...]:
    """Every `data-corpus` a page under `root` carries: the names a page asks the index for."""
    found: set[str] = set()
    for page in root.rglob("*.html"):
        found |= set(re.findall(r'data-corpus="([^"]+)"', page.read_text(encoding="utf-8")))
    return tuple(sorted(found))


@contextlib.contextmanager
def serving(
    built: site.Site,
    corpus: str = DEFAULT_CORPUS,
    *,
    windows: bool = False,
    editor: str | None = None,
    configured: bool = False,
) -> Iterator[Served]:
    """Serve one corpus's subtree of `built` on a free loopback port, then stop.

    ⛔ **The served root is ONE corpus's subtree, and that is the framework's
    own shape rather than a convenience.** `studyforge serve --site` serves one
    built corpus from its root; the static mount exposes the generated
    dot-directory at the served root or beside a `corpus.json`, and this
    harness's tree holds one subtree per fixture corpus with no manifest in it.
    ⚠️ Serving the whole tree answers `404` for every stylesheet and script on
    the page — ⭐ measured here first, which is why this argument exists.

    ⛔ **The run namespace is registered and `client=` is `run.CLIENT_PATH`**,
    the framework's one spelling of where the client lives — so the tag the
    static mount inserts and the path this namespace answers cannot come apart
    here any more than they can in a real instance.

    ⭐ **`windows=True` answers the practice-editor route with two real frames**
    and admits this origin to the `frame-src` the framework composes, so a panel
    that must not move an `iframe` has an `iframe` to not move. ⛔ Off
    by default: a frame is a focus scope of its own, and every traversal in this
    package counts stops.

    ⭐ **`editor=<origin>` answers the same route with that origin's `/main`
    and `/test`** and admits it to `frame-src` instead: a stand-in
    editor on ANOTHER origin, which is the only kind of frame whose own script
    can take focus the way a real workbench does.

    ⛔ **The run is released on the way out, before `shutdown()`.** A stream
    still waiting inside `RELEASE_BOUND` would hold `serve_forever`'s thread,
    and a harness that hangs on teardown is the same failure as one that
    never closes its tabs.
    """
    runs = ScriptedRuns()
    log: list[str] = []
    #: The origins this instance's `frame-src` admits, filled after the bind and
    #: read by the framework at RESPONSE time — which is the only order
    #: available, because the port is the kernel's answer to `port=0`.
    admitted: list[str] = []
    frames = lambda: tuple(admitted)  # noqa: E731 - read at response time, after the bind
    if configured and editor:
        frames = Runs(Discovered(built.root / corpus, (), ()), {}, declared=(editor,)).origins
    server = make_server(
        built.root / corpus,
        _NoContent(),
        port=0,
        namespaces={NAMESPACE: runs.route},
        writers=(NAMESPACE,),
        client=CLIENT_PATH,
        log=log.append,
        frames=frames,
    )
    held = Served(server=server, built=built, corpus=corpus, runs=runs, log=log)
    if windows or editor:
        # ⛔ **The real `frame-src` composer, not a header written by hand.**
        # `serve.security` is what decides whether this document may embed
        # anything at all, and a harness that bypassed it would be reading a
        # policy no instance sends.
        if not configured:
            admitted.append(editor or held.origin)
        main, test = (f"{editor}/main", f"{editor}/test") if editor else WINDOW_URLS
        runs.windows = {"main": {"url": main}, "test": {"url": test}}
        where = {"origin": editor or held.origin, "folder": "/work"}
        runs.editors = {name: dict(where) for name in _corpora(built.root / corpus)}
    thread = threading.Thread(target=held.server.serve_forever, daemon=True)
    thread.start()
    try:
        yield held
    finally:
        runs.release.set()
        held.server.shutdown()
        held.server.server_close()
        thread.join(timeout=20)
