r"""The live namespace: a reader's own key, one live-capable example or practice, one live run.

**What it does.** Answers under `/api/v1/live/`:

- `GET` (empty) → `live-index`: the corpora that declare live runs, each with the one host a live
  run may reach, the NAME of the variable the key is given under, the examples and practices that
  may run live, and whether the live runner answers now (`enabled`);
- `GET client.js` → the page's live client, `serve/assets/live-client.js`: the key field and the
  Live run controls, drawn where a page has a live-capable example or practice;
- `POST run` → starts ONE live run and streams its output as `text/plain`, ended by the same exit
  line a run ends with. The body is JSON, `{"corpus", "kind", "target", "key"}`; the key is its
  only way in and this module the ONE place it is read from a request.

**How you use it.** `serve.instance` builds `LiveRuns(runs, service)` and registers it under
`NAMESPACE` with `RUN_PATH` among `app`'s `bodies` and the namespace among its writers.

**Depends on.** `execute` for the live run (`live.start`) and its allowlist, `routes.runs` for the
one run slot and the stream, `routes.run` for a practice's workspace, `serve.security` for origin
checks. ⛔ Like `routes.run`, one of the few `serve` modules that import `execute`.

## ⛔ Nothing a client sends becomes a command, and the key is never anything else

⭐ **The command is READ, never received.** `kind` and `target` only SELECT: an example's argv is
the manifest's, a practice's is its record's `run_command`, and the live runner runs only what its
own allowlist (`allowed/live`, written here from those records) holds. ⭐ **The key is data**: it
is checked against one shape (`execute.live.valid_key`) and handed to the launcher, which puts it in
a framed field. ⛔ It is in no variable of this module's beyond the request's own, in no log
line, in no response body and in no error text: every refusal below is a constant that
names the shape.

## ⛔ Who may ask: the page's own origin, with a header a form cannot send

A cross-origin page cannot make this request without a CORS preflight this server never grants:
the body is `application/json`, the header `X-Studyforge-Live` is custom, and the `Origin` must be
this server's own (host and port) and the `Sec-Fetch-Site` same-origin where a browser sends one.
These stand on top of the gate every request already passes (`Host`, peer, cross-site refusal).

## ⭐ One live run at a time, and the reader sees it end

The slot is `Runs`'s own, so a graded run and a live run never overlap (a reader has one
workspace) and a second start is `409`. A live run ends with the run, a timeout or the page hanging
up, whichever comes first, and the stream's second net replaces the key, its URL-encoded and its
base64 forms in any line (the live runner's is the first).
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from pathlib import Path
from urllib.parse import urlsplit

from studyforge.execute import (
    LIVE_BAD_KEY,
    LIVE_MARKER,
    RunHandle,
    RunRefused,
    Service,
    ServiceProbe,
    redactions,
    start_live,
    valid_key,
    write_allowed,
)
from studyforge.archive.scrub import PersonalDataLeak, assert_clean
from studyforge.progress import RAISES as PROGRESS_RAISES
from studyforge.progress import parse_practice_key
from studyforge.serve.discovery import ServedCorpus
from studyforge.serve.response import (
    API_PREFIX,
    NO_STORE,
    TEXT_TYPE,
    Request,
    Response,
    error,
    json_response,
)
from studyforge.serve.routes import run
from studyforge.serve.routes.code import Unrecorded
from studyforge.serve.routes.runs import Live, Runs, Stream
from studyforge.unit.errors import ContentError

#: The name this namespace is registered under, and the paths in it.
NAMESPACE = "live"
RUN = "run"
CLIENT = "client.js"
CLIENT_FILE = Path(__file__).resolve().parent.parent / "assets" / "live-client.js"
SCRIPT_TYPE = "text/javascript; charset=utf-8"

#: ⭐ Where a page asks for the client and where it posts a run: this module's own spelling,
#: so the namespace that serves them and the pieces that name them cannot come apart.
CLIENT_PATH = f"{API_PREFIX}/{NAMESPACE}/{CLIENT}"
RUN_PATH = f"{API_PREFIX}/{NAMESPACE}/{RUN}"

#: The header a live request carries and what it must say. ⭐ Custom, so a form or a simple
#: cross-origin request cannot send it.
HEADER = "X-Studyforge-Live"
HEADER_VALUE = "1"

#: What a request's `kind` may be, and the keys its body carries.
EXAMPLE, PRACTICE = "example", "practice"
BODY_KEYS = frozenset({"corpus", "kind", "target", "key"})

NOT_STARTED = (
    "live runs are not started: bring the course up with the live profile (see EXECUTION.md)"
)
NOT_FROM_HERE = "a live run is asked for by this site's own page"
NOT_JSON = "a live run is asked for with a JSON body"
NOT_A_REQUEST = "the body is not a live run's request"
NO_SUCH_TARGET = "this corpus declares no such live run"
NO_COMMAND = "this practice's record names no command to run"
UNREADABLE = "the practice's record could not be read"
REFUSED = "the live runner refused this run"
BUSY = "a run is already live; stop it first"
NO_SUCH_RUN = "no such live endpoint"


class LiveRuns:
    """The live namespace as a route: the corpora that offer live runs, and the one launcher.

    ⭐ `start` is the seam a test replaces; the default is `execute.live.start`, which reaches the
    live runner's service. ⛔ Nothing here holds a key between requests.
    """

    #: ⭐ The page's live client path and the paths that carry a body, read back by
    #: `serve.instance` the way `client_for` reads the run client.
    client = CLIENT_PATH
    bodies = (RUN_PATH,)

    def __init__(
        self,
        runs: Runs,
        service: Service,
        *,
        start: Callable[..., RunHandle] = start_live,
        reachable: Callable[[], bool] | None = None,
    ) -> None:
        """Hold the instance's runs and where the live runner answers; write the allowlist."""
        self.runs = runs
        self.service = service
        self._start = start
        self._reachable = reachable or _answers(service)
        self.write_allowed()

    def declared(self) -> list[ServedCorpus]:
        """Return the served corpora that declare live runs."""
        return [
            corpus
            for corpus in self.runs.discovered.corpora
            if corpus.corpus.manifest.live is not None and corpus.source in self.runs.sources
        ]

    def write_allowed(self) -> None:
        """Write each declaring corpus's `allowed/live`, whole, from its own records.

        ⛔ Never from a request. ⭐ A corpus rebuilt while serving is read again at the next run.
        """
        for corpus in self.declared():
            write_allowed(corpus.root, self.entries(corpus), "live")

    def entries(self, corpus: ServedCorpus) -> list[tuple[str, list[str]]]:
        """Return `(cwd, argv)` for every live-capable example and practice of `corpus`."""
        live = corpus.corpus.manifest.live
        assert live is not None
        found = [(run_cwd(), list(example.command)) for example in live.examples]
        for key in live.practices:
            argv = practice_command(self.runs, corpus, key)
            if isinstance(argv, list):
                found.append((run_cwd(), argv))
        return found

    def __call__(self, request: Request, rest: str) -> Response:
        """Answer one request under the live namespace."""
        if rest in ("", CLIENT):
            if request.method == "POST":
                return error(405, "method not allowed")
            if rest == CLIENT:
                headers = (("Content-Type", SCRIPT_TYPE), ("Cache-Control", NO_STORE))
                return Response(200, headers, CLIENT_FILE.read_bytes())
            return json_response(200, self.index())
        if rest != RUN:
            return error(404, NO_SUCH_RUN)
        if request.method != "POST":
            return error(405, "a live run is started by POST")
        return self.post(request)

    def index(self) -> dict:
        """Return what this namespace offers: each declaring corpus's host, variable and targets."""
        corpora = {}
        for corpus in self.declared():
            live = corpus.corpus.manifest.live
            assert live is not None
            corpora[corpus.source] = {
                "host": live.host,
                "key_variable": live.key_variable,
                "examples": [example.path for example in live.examples],
                "practices": list(live.practices),
            }
        return {
            "resource": "live-index",
            "run": RUN_PATH,
            "client": CLIENT_PATH,
            "header": [HEADER, HEADER_VALUE],
            "enabled": self._reachable(),
            "corpora": corpora,
        }

    def post(self, request: Request) -> Response:
        """Start the live run a page asked for, or refuse it by a constant sentence."""
        refused = origin_refusal(request)
        if refused is not None:
            return error(403, refused)
        asked = asked_for(request)
        if isinstance(asked, Response):
            return asked
        corpus_name, kind, target, key = asked
        if not self._reachable():
            return error(503, NOT_STARTED)
        corpus = self.runs.discovered.by_source.get(corpus_name)
        found = self.resolve(corpus, kind, target)
        if isinstance(found, Response):
            return found
        assert corpus is not None
        self.write_allowed()
        try:
            live = self.runs.claim(
                lambda: Live(corpus.source, target, "live", self._start(self.service, found, key))
            )
        except RunRefused:
            return error(503, REFUSED)
        if live is None:
            return error(409, BUSY)
        headers = (("Content-Type", TEXT_TYPE), ("Cache-Control", NO_STORE))
        stream = Redacted(Stream(self.runs, live, Unrecorded(corpus, found)), key)
        return Response(200, headers, stream=stream)

    def resolve(self, corpus: ServedCorpus | None, kind: str, target: str) -> list[str] | Response:
        """Return the argv a declared live run starts: the manifest's or the practice's own."""
        live = None if corpus is None else corpus.corpus.manifest.live
        if corpus is None or live is None or corpus.source not in self.runs.sources:
            return error(404, NO_SUCH_TARGET)
        if kind == EXAMPLE:
            for example in live.examples:
                if example.path == target:
                    return list(example.command)
        elif kind == PRACTICE and target in live.practices:
            return practice_command(self.runs, corpus, target)
        return error(404, NO_SUCH_TARGET)


def practice_command(runs: Runs, corpus: ServedCorpus, key: str) -> list[str] | Response:
    """Return a practice's own `run_command`, or the refusal for why it has none."""
    try:
        address, ordinal, section = parse_practice_key(key, corpus.depth)
        source = runs.sources[corpus.source]
        workspace = run.workspace_of(source, address.unit_key(ordinal), section)
    except PROGRESS_RAISES, LookupError, ContentError, PersonalDataLeak:
        return error(422, UNREADABLE)
    argv = None if workspace is None else workspace.get("run_command")
    ok = isinstance(argv, list) and argv and all(isinstance(one, str) for one in argv)
    return list(argv) if ok else error(409, NO_COMMAND)


def run_cwd() -> str:
    """The directory every live run starts in: the corpus root, as a graded run's does."""
    return "."


def origin_refusal(request: Request) -> str | None:
    """Return why this request is not the page's own, or `None`.

    ⭐ The three things a cross-origin forger cannot supply: the JSON content type, the custom
    header, and an `Origin` that is this server's own host and port.
    """
    headers = request.headers
    if (headers.get(HEADER) or "").strip() != HEADER_VALUE:
        return NOT_FROM_HERE
    kind = (headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
    if kind != "application/json":
        return NOT_JSON
    origin = (headers.get("Origin") or "").strip()
    parts = urlsplit(origin)
    host = (headers.get("Host") or "").strip().lower()
    if parts.scheme != "http" or not host or parts.netloc.lower() != host or origin == "null":
        return NOT_FROM_HERE
    site = (headers.get("Sec-Fetch-Site") or "").strip().lower()
    if site and site != "same-origin":
        return NOT_FROM_HERE
    return None


def asked_for(request: Request) -> tuple[str, str, str, str] | Response:
    """Return `(corpus, kind, target, key)` from the body, or the refusal.

    ⭐ THE ONE READ OF THE KEY.

    ⛔ Every refusal is a constant: neither the body nor any part of it is quoted back.
    """
    try:
        document = json.loads(getattr(request, "body", b"").decode("utf-8"))
        assert_clean(document, "a live request")
    except UnicodeDecodeError, ValueError, PersonalDataLeak:
        return error(400, NOT_A_REQUEST)
    if not isinstance(document, dict) or set(document) != BODY_KEYS:
        return error(400, NOT_A_REQUEST)
    values = [document[name] for name in ("corpus", "kind", "target", "key")]
    if not all(isinstance(value, str) for value in values):
        return error(400, NOT_A_REQUEST)
    corpus, kind, target, key = values
    if not valid_key(key):
        return error(400, LIVE_BAD_KEY)
    return corpus, kind, target, key


def _answers(service: Service) -> Callable[[], bool]:
    """Return a cached `ping` of the live runner's service."""
    return ServiceProbe(service).up


class Redacted:
    """A live run's stream with the key, its URL-encoded and its base64 forms replaced.

    ⭐ The second net: the live runner replaces them before a byte leaves its container, and this
    does it again for a line that arrived by any other road. It forwards `cancel` and `close`, so
    a page that hung up still ends the run.
    """

    def __init__(self, inner: Stream, key: str) -> None:
        """Hold the stream and the forms to replace; the key itself is not kept."""
        self._inner = inner
        self._forms = redactions(key)

    def __iter__(self) -> Iterator[bytes]:
        """Return this stream."""
        return self

    def __next__(self) -> bytes:
        """Return the next chunk, every form of the key replaced."""
        chunk = next(self._inner)
        text = chunk.decode("utf-8", errors="replace")
        for form in self._forms:
            text = text.replace(form, LIVE_MARKER)
        return text.encode("utf-8")

    def cancel(self) -> None:
        """Stop the run from another thread: the page hung up."""
        self._inner.cancel()

    def close(self) -> None:
        """End the stream; an unfinished run is stopped."""
        self._inner.close()

    def __repr__(self) -> str:
        """Say what this is, never what it replaces."""
        return "Redacted(<stream>)"
