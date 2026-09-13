r"""App wiring: the loopback server, the gate in front of every route, and the wire.

**What it does.** Binds `127.0.0.1` only, refuses every request `security.refusal`
refuses, dispatches `/api/v1/<namespace>/…` to the namespace registered under that
name, serves every other path from the static mount, and writes each `Response` —
security headers on all of them, a file streamed span by span.

**How you use it.**

    server = make_server(site_root, CorpusContent(corpus), port=0)
    server.serve_forever()          # server.server_address is (host, port)

**Depends on.** `http.server`, `serve.security`, `serve.response`, `serve.routes`,
and `archive.scrub` for the log line. ⛔ **No process-spawning library, anywhere in
this package** — `tests/studyforge/serve/test_init.py` asserts that of every module,
and the Docker socket is never reachable from here (spec §8.3).

## ⭐ The seams later rows plug into

- **`namespaces=`** — `{name: route(request, rest)}` added beside `content` and
  `assets`. `SF-19b` registers `state` here and `SF-22` registers `run`. ⛔ A name
  that is already taken is refused, so a later namespace cannot quietly replace
  content's caching rule with its own.
- **`private=`** — a predicate over a resolved path; `SF-21`'s store names the
  reader's record through it, and it answers `404` on both mounts.
- Only `GET` and `HEAD` are answered; every other method is `405` after the gate.
  ⚠️ A namespace that needs a write widens `_Handler`'s verbs in its own row.

⛔ **An exception inside a route answers `500` with a fixed body** and logs only
its type: an exception's text is where an absolute path reaches a browser (R7).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from studyforge.archive.scrub import scrub
from studyforge.serve.response import (
    API_PREFIX,
    API_ROOT,
    API_VERSION,
    BODILESS,
    Request,
    Response,
    error,
    json_response,
)
from studyforge.serve.routes import assets, content
from studyforge.serve.security import ALLOWED_HOSTS, SECURITY_HEADERS, refusal, require_loopback

#: What `studyforge serve` binds when it is not told otherwise.
DEFAULT_PORT = 8765

#: Streaming chunk for a file body.
CHUNK = 64 * 1024

#: The namespaces this row owns, which nothing registered later may replace.
OWN_NAMESPACES = ("content", "assets")

Route = Callable[[Request, str], Response]


class ServingServer(ThreadingHTTPServer):
    """A threading HTTP server that holds the site root, the namespaces and the log."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        address: tuple[str, int],
        site_root: Path,
        source: content.ContentSource,
        namespaces: Mapping[str, Route] | None = None,
        private: assets.Private = assets.nothing_private,
        log: Callable[[str], None] | None = None,
    ) -> None:
        """Validate everything, then bind; a refused argument never leaves a socket open."""
        require_loopback(address[0])
        root = Path(site_root)
        if not root.is_dir():
            raise ValueError("the served root is not a directory")
        extra = dict(namespaces or {})
        taken = sorted(set(extra) & set(OWN_NAMESPACES))
        if taken:
            raise ValueError(f"namespace already registered: {', '.join(taken)}")
        self.site_root = root
        self.private = private
        self.allowed_hosts = ALLOWED_HOSTS
        self.namespaces: dict[str, Route] = {
            "content": partial(content.route, source),
            "assets": partial(assets.route, root, private),
            **extra,
        }
        self._log = log
        super().__init__(address, _Handler)

    def log(self, message: str) -> None:
        """Hand one scrubbed line to the caller's log, or drop it when there is none."""
        if self._log is not None:
            self._log(scrub(message))

    def handle_error(self, request: object, client_address: object) -> None:
        """Log a connection's failure by type only; the default prints a traceback (R7)."""
        import sys

        self.log(f"connection failed: {type(sys.exc_info()[1]).__name__}")

    def respond(self, request: Request) -> Response:
        """Dispatch one request that has already passed the gate."""
        path = request.path
        if path.rstrip("/") == API_ROOT:
            return json_response(200, {"resource": "api", "versions": [f"v{API_VERSION}"]})
        if path.rstrip("/") == API_PREFIX:
            return json_response(200, _version_document(self.namespaces))
        if path.startswith(API_PREFIX + "/"):
            name, _, rest = path[len(API_PREFIX) + 1 :].partition("/")
            found = self.namespaces.get(name)
            return error(404, "no such endpoint") if found is None else found(request, rest)
        if path.startswith(API_ROOT + "/"):
            return error(404, "no such endpoint")
        return assets.serve(self.site_root, request, path, self.private)


def make_server(
    site_root: Path,
    source: content.ContentSource,
    port: int = DEFAULT_PORT,
    namespaces: Mapping[str, Route] | None = None,
    private: assets.Private = assets.nothing_private,
    log: Callable[[str], None] | None = None,
) -> ServingServer:
    """Build a bound, not-yet-serving server on `127.0.0.1`; `port=0` picks a free one."""
    return ServingServer(
        ("127.0.0.1", port), site_root, source, namespaces=namespaces, private=private, log=log
    )


def _version_document(namespaces: Mapping[str, Route]) -> dict:
    """Return what `/api/v1` says: the namespaces served and which of them cache."""
    return {
        "resource": "api-version",
        "namespaces": sorted(namespaces),
        "cacheable": [f"{API_PREFIX}/{name}/" for name in OWN_NAMESPACES],
        "endpoints": {
            "toc": f"{API_PREFIX}/content/{content.TOC}",
            "unit": f"{API_PREFIX}/content/{content.UNITS}{{key}}",
            "asset": f"{API_PREFIX}/assets/{{path}}",
        },
    }


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
        refused = refusal(self.client_address[0], self.headers, self.server.allowed_hosts)
        if refused is not None:
            self._write(error(403, refused), close=True)
            return
        request = Request(self.command, urlsplit(self.path).path, self.headers)
        try:
            response = self.server.respond(request)
        except Exception as exc:
            self.server.log(f"route failed: {type(exc).__name__}")
            response = error(500, "internal error")
        self._write(response)

    do_HEAD = do_GET

    def _unsupported(self) -> None:
        """Answer any other method `405`, after the same gate."""
        refused = refusal(self.client_address[0], self.headers, self.server.allowed_hosts)
        answer = error(403, refused) if refused else error(405, "method not allowed")
        headers = answer.headers if refused else (*answer.headers, ("Allow", "GET, HEAD"))
        self._write(Response(answer.status, headers, answer.body), close=True)

    do_POST = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = _unsupported

    def _write(self, response: Response, close: bool = False) -> None:
        """Send the status, every header, and the body or the file's span."""
        self.send_response(response.status)
        for name, value in (*response.headers, *SECURITY_HEADERS):
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
        self._stream(response)

    def _stream(self, response: Response) -> None:
        """Stream the inclusive span of a file without holding it in memory."""
        if response.span is None or response.file is None:
            return
        first, _ = response.span
        remaining = response.length
        try:
            with response.file.open("rb") as handle:
                handle.seek(first)
                while remaining > 0:
                    chunk = handle.read(min(CHUNK, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        except OSError as exc:
            self.server.log(f"read failed mid-response: {type(exc).__name__}")
        if remaining:
            # Headers are already out; dropping the connection is the only honest
            # signal left that the body is short.
            self.close_connection = True
