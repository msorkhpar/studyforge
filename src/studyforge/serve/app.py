r"""App wiring: the loopback server, the gate in front of every route, and the wire.

**What it does.** Binds `127.0.0.1` only, refuses every request `security.refusal`
refuses, dispatches `/api/v1/<namespace>/…` to the namespace registered under that
name, serves every other path from the static mount, and writes each `Response` —
security headers on all of them, a file's span sent by the kernel (`serve.sending`).

**How you use it.**

    server = make_server(site_root, CorpusContent(corpus), port=0)
    server.serve_forever()          # server.server_address is (host, port)

**Depends on.** `http.server`, `serve.security`, `serve.response`, `serve.routes`,
`serve.withheld`, `serve.versions` (one memo per server), `serve.sending`, and
`archive.scrub` for the log. ⛔ **No process-spawning library in this package** —
`tests/studyforge/serve/test_init.py` asserts that of every module, and the Docker
socket is never reachable from here (spec §8.3).

## ⭐ The seams later rows plug into

- **`namespaces=`** — `{name: route(request, rest)}` added beside `content` and
  `assets`. `state` and `run` are registered here. ⛔ A name
  that is already taken is refused, so a later namespace cannot quietly replace
  content's caching rule with its own.
- **`private=`** — a predicate over a resolved path; the progress store names the
  reader's record through it, and it answers `404` on both mounts. ⛔ So does a file
  carrying a quiz's key or sentence, read off `source` in every form.
- **`writers=`** — the registered namespaces that also answer `POST` (the
  `run` namespace: starting a process is an act, and a `GET` that acted would run a grader
  on a prefetch). ⛔ Content, assets and the static mount never do.
- **`client=`** — where the run namespace serves the page's execution client.
  ⭐ Handed to `routes.assets`, which inserts one script tag
  into an HTML page's BYTES as it answers it, so a BUILT page names no API, no
  origin and no client file (R8). ⛔ This module holds no spelling of that path
  and imports nothing from `routes.run` to learn one: `serve.instance` registers
  the namespace and passes the path, and importing the run route here would put
  `execute` — and a process library — into every import of `serve.app`.
- **`live=`** — where the live client is served: a second tag after the run client's.
- **`frames=`** — what this instance may EMBED, asked per response,
  because the editor's origin is a per-project host port. ⛔ Never widens
  `frame-ancestors`.
- **`bodies=`** — paths whose `POST` body reaches the route (`BodyRequest`); others' is dropped.
- `GET` and `HEAD` are answered everywhere; `POST` only under a writer; every other
  method, and a `POST` anywhere else, is `405` after the gate.

⛔ **An exception inside a route answers `500` with a fixed body** and logs only
its type: an exception's text is where an absolute path reaches a browser (R7).
"""

from __future__ import annotations

import select
import socket
import threading
from collections.abc import Callable, Collection, Mapping
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import BinaryIO
from urllib.parse import urlsplit

from studyforge.archive.scrub import scrub
from studyforge.serve.bodies import read
from studyforge.serve.response import (
    API_PREFIX,
    API_ROOT,
    API_VERSION,
    BODILESS,
    BodyRequest,
    Request,
    Response,
    error,
    json_response,
)
from studyforge.serve.routes import assets, content
from studyforge.serve.security import (
    ALLOWED_HOSTS,
    LOOPBACK,
    LOOPBACK_PEERS,
    PUBLISHED_BIND,
    SECURITY_HEADERS,
    refusal,
    require_loopback,
    response_headers,
)
from studyforge.serve.sending import MOVED, MOVED_STATUS, opened, send_span
from studyforge.serve.versions import Versions
from studyforge.serve.withheld import refused_by

#: What `studyforge serve` binds when it is not told otherwise.
DEFAULT_PORT = 8765

#: Seconds between two looks at a streaming client's socket for a hang-up.
HANGUP_POLL = 0.25

#: The largest other `POST` body drained before answering and dropped (no route is handed it),
#: and the largest a route registered in `bodies` is handed: a key and a few names.
MAX_DISCARDED = 64 * 1024
MAX_BODY = 8 * 1024

#: The namespaces this module owns, which nothing registered later may replace.
OWN_NAMESPACES = ("content", "assets")

Route = Callable[[Request, str], Response]

#: Where this instance's editors are, asked afresh per response.
Frames = Callable[[], Collection[str]]


class ServingServer(ThreadingHTTPServer):
    """A threading HTTP server that holds the site root, the namespaces and the log."""

    daemon_threads = True
    allow_reuse_address = True
    #: ⭐ The listen backlog: `socketserver`'s default of 5 drops a page's burst of asset
    #: connections, and a dropped connection waits out the client's retransmit timer.
    request_queue_size = 128

    def __init__(
        self,
        address: tuple[str, int],
        site_root: Path,
        source: content.ContentSource,
        namespaces: Mapping[str, Route] | None = None,
        private: assets.Private = assets.nothing_private,
        log: Callable[[str], None] | None = None,
        writers: Collection[str] = (),
        client: str | None = None,
        frames: Frames | None = None,
        published: bool = False,
        bodies: Collection[str] = (),
        live: str | None = None,
    ) -> None:
        """Validate everything, then bind; a refused argument never leaves a socket open."""
        require_loopback(address[0], published=published)
        self.peers = None if published else LOOPBACK_PEERS
        root = Path(site_root)
        if not root.is_dir():
            raise ValueError("the served root is not a directory")
        extra = dict(namespaces or {})
        taken = sorted(set(extra) & set(OWN_NAMESPACES))
        if taken:
            raise ValueError(f"namespace already registered: {', '.join(taken)}")
        stray = sorted(set(writers) - set(extra))
        if stray:
            raise ValueError(f"only a registered namespace may answer POST: {', '.join(stray)}")
        self.site_root = root
        self.frames = frames
        self.allowed_hosts = ALLOWED_HOSTS
        withheld = refused_by(source)
        self.memo = Versions()
        tags = {"client": client, "live": live, "withheld": withheld, "memo": self.memo}
        self.static = partial(assets.serve, root, private=private, **tags)
        self.namespaces: dict[str, Route] = {
            "content": partial(content.route, source),
            "assets": partial(assets.route, root, private, **tags),
            **extra,
        }
        self.writers, self.bodies = frozenset(writers), frozenset(bodies)
        self._log = log
        super().__init__(address, _Handler)

    def headers(self, host: str | None = None) -> tuple[tuple[str, str], ...]:
        """Return this response's security headers, the frame policy composed for `host`.

        ⛔ **Per response**: an editor comes and goes while this process serves.
        ⭐ A page reached at any accepted loopback name frames the editor, and a
        host outside them is given none.
        """
        if self.frames is None:
            return SECURITY_HEADERS
        return response_headers(self.frames(), host)

    def gate(self, peer: str, headers: Mapping[str, str], page: str | None = None) -> str | None:
        """Return `security.refusal`'s answer; `page` is a `GET`'s path."""
        return refusal(peer, headers, self.allowed_hosts, self.peers, path=page)

    def log(self, message: str) -> None:
        """Hand one scrubbed line to the caller's log, or drop it when there is none."""
        if self._log is not None:
            self._log(scrub(message))

    def handle_error(self, request: object, client_address: object) -> None:
        """Log a connection's failure by type only; the default prints a traceback (R7)."""
        import sys

        self.log(f"connection failed: {type(sys.exc_info()[1]).__name__}")

    def writer(self, path: str) -> str | None:
        """Return the writer namespace `path` is under, or `None`."""
        if not path.startswith(API_PREFIX + "/"):
            return None
        name = path[len(API_PREFIX) + 1 :].partition("/")[0]
        return name if name in self.writers else None

    def respond(self, request: Request) -> Response:
        """Dispatch one request that has already passed the gate."""
        path = request.path
        if path.rstrip("/") == API_ROOT:
            return json_response(200, {"resource": "api", "versions": [f"v{API_VERSION}"]})
        if path.rstrip("/") == API_PREFIX:
            return json_response(200, content.version_document(self.namespaces, OWN_NAMESPACES))
        if path.startswith(API_PREFIX + "/"):
            name, _, rest = path[len(API_PREFIX) + 1 :].partition("/")
            found = self.namespaces.get(name)
            return error(404, "no such endpoint") if found is None else found(request, rest)
        if path.startswith(API_ROOT + "/"):
            return error(404, "no such endpoint")
        return self.static(request, path)


def make_server(
    site_root: Path,
    source: content.ContentSource,
    port: int = DEFAULT_PORT,
    namespaces: Mapping[str, Route] | None = None,
    private: assets.Private = assets.nothing_private,
    log: Callable[[str], None] | None = None,
    writers: Collection[str] = (),
    client: str | None = None,
    frames: Frames | None = None,
    published: bool = False,
    bodies: Collection[str] = (),
    live: str | None = None,
) -> ServingServer:
    """Build a bound, not-yet-serving server on `127.0.0.1` (`published`: its container's)."""
    return ServingServer(
        (PUBLISHED_BIND if published else LOOPBACK, port),
        site_root,
        source,
        namespaces=namespaces,
        private=private,
        log=log,
        writers=writers,
        client=client,
        frames=frames,
        published=published,
        bodies=bodies,
        live=live,
    )


class _Handler(BaseHTTPRequestHandler):
    """The wire: gate, dispatch, write. Every byte a client receives leaves `_write`."""

    server: ServingServer
    server_version = "studyforge-serve"
    sys_version = ""
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: object) -> None:
        """Send one line per request to the server's scrubbed log."""
        self.server.log(f"{self.client_address[0]} {(format % args)[:400]}")

    def do_GET(self) -> None:
        """Answer a `GET` (and, through it, a `HEAD`)."""
        refused = self.server.gate(self.client_address[0], self.headers, urlsplit(self.path).path)
        if refused is not None:
            self._write(error(403, refused), close=True)
            return
        self._dispatch()

    do_HEAD = do_GET

    def do_POST(self) -> None:
        """Answer a `POST` under a writer namespace, after the gate; `405` anywhere else."""
        path = urlsplit(self.path).path
        refused = self.server.gate(self.client_address[0], self.headers)
        if refused is not None or self.server.writer(path) is None:
            self._unsupported()
            return
        taken = path in self.server.bodies
        body = read(self.headers, self.rfile, MAX_BODY if taken else MAX_DISCARDED)
        if body is None:
            self._write(error(413, "this request body is not accepted"), close=True)
            return
        self._dispatch(body if taken else None)

    def _dispatch(self, body: bytes | None = None) -> None:
        """Hand the request to its route; an exception is a fixed `500`."""
        path = urlsplit(self.path).path
        request = Request(self.command, path, self.headers)
        if body is not None:
            request = BodyRequest(self.command, path, self.headers, body)
        try:
            response = self.server.respond(request)
        except Exception as exc:
            self.server.log(f"route failed: {type(exc).__name__}")
            response = error(500, "internal error")
        self._write(response)

    def _unsupported(self) -> None:
        """Answer any other method `405`, after the same gate."""
        refused = self.server.gate(self.client_address[0], self.headers)
        answer = error(403, refused) if refused else error(405, "method not allowed")
        headers = answer.headers if refused else (*answer.headers, ("Allow", "GET, HEAD"))
        self._write(Response(answer.status, headers, answer.body), close=True)

    do_PUT = do_DELETE = do_PATCH = do_OPTIONS = _unsupported

    def _write(self, response: Response, close: bool = False) -> None:
        """Send the status, every header, and the body, the file's span, or the stream."""
        if response.stream is not None:
            self._write_stream(response)
            return
        handle, moved = opened(response) if self.command != "HEAD" else (None, False)
        if moved:
            response = error(MOVED_STATUS, MOVED)
        try:
            self._send(response, close, handle)
        finally:
            if handle is not None:
                handle.close()

    def _send(self, response: Response, close: bool, handle: BinaryIO | None) -> None:
        """Write the status, the headers, and the body or the open file's span."""
        self.send_response(response.status)
        for name, value in (*response.headers, *self.server.headers(self.headers.get("Host"))):
            self.send_header(name, value)
        if response.status not in BODILESS:
            self.send_header("Content-Length", str(response.length))
        if close:
            self.close_connection = True
            self.send_header("Connection", "close")
        self.end_headers()
        if self.command == "HEAD" or response.status in BODILESS:
            return
        if response.file is None:
            self.wfile.write(response.body)
            return
        if handle is not None and response.span is not None:
            if send_span(self.connection, handle, response.span[0], response.length):
                # Headers are out; dropping the connection is the only honest signal left.
                self.server.log("file answer cut short")
                self.close_connection = True

    def _write_stream(self, response: Response) -> None:
        """Send each chunk as it is produced; the body ends when the connection closes.

        ⛔ The stream is closed whatever happens — a client that hung up closes it,
        which is how a run the page abandoned is ended rather than left running.
        """
        stream = response.stream
        assert stream is not None
        done = threading.Event()
        ending = threading.Lock()
        watcher: threading.Thread | None = None
        try:
            self.send_response(response.status)
            for name, value in (*response.headers, *self.server.headers(self.headers.get("Host"))):
                self.send_header(name, value)
            self.send_header("Connection", "close")
            self.end_headers()
            self.close_connection = True
            if self.command == "HEAD":
                return
            cancel = getattr(stream, "cancel", None)
            if cancel is not None:
                watching = (done, ending, cancel)
                watcher = threading.Thread(target=self._watch, args=watching, daemon=True)
                watcher.start()
            for chunk in stream:
                self.wfile.write(chunk)
                self.wfile.flush()
        except OSError as exc:
            self.server.log(f"stream ended early: {type(exc).__name__}")
        finally:
            # ⛔ The watcher is JOINED before the stream is closed: a stream that ended on
            # its own must never be cancelled by a look taken as the socket closed.
            with ending:
                done.set()
            if watcher is not None:
                watcher.join()
            close = getattr(stream, "close", None)
            if close is not None:
                close()

    def _watch(
        self, done: threading.Event, ending: threading.Lock, cancel: Callable[[], object]
    ) -> None:
        """Call `cancel` if the client hangs up while the stream is still producing.

        ⚠️ A stream blocked waiting for its next chunk writes nothing, so a write can
        never discover the hang-up; the socket reading end-of-file is the only signal.
        """
        while not done.wait(HANGUP_POLL):
            try:
                readable, _, _ = select.select([self.connection], [], [], 0)
                hung_up = bool(readable) and self.connection.recv(1, socket.MSG_PEEK) == b""
            except OSError, ValueError:
                hung_up = True
            if hung_up:
                with ending:
                    if not done.is_set():
                        cancel()
                return
            if readable:
                return
