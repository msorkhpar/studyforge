"""A local stand-in for a release host, so a restore is read with no network at all.

**What it does.** Serves one release directory on `127.0.0.1` the two ways a
release host does: the public download address
(`/<owner>/<repo>/releases/download/<tag>/<name>`), and the API a private
repository needs (`/repos/<owner>/<repo>/releases/tags/<tag>` for the asset
list, `/repos/<owner>/<repo>/releases/assets/<id>` for one asset, which
redirects to where its bytes are stored). Every request is recorded, headers
included, so a test reads what the script SENT.

**How you use it.**

    with StandIn(release_dir, private=True) as host:
        env["NARRATION_API_URL"] = host.api
        ...
    host.requests    # [(method, path, headers)]

**Depends on.** `http.server` and `threading`. ⛔ Binds loopback only, on a
port the kernel picks, and serves nothing outside `release`.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

#: The repository and tag the stand-in answers for. Placeholders, never an account.
OWNER_REPO = "example-owner/example-course"
TAG = "narration-1.0.0"

#: The only token a private stand-in accepts. ⛔ A test value, and no real one's shape.
TOKEN = "stand-in-token-for-tests"

#: The first asset id the API hands out.
FIRST_ID = 7001


class StandIn:
    """One release directory served on loopback, public or private."""

    def __init__(self, release: Path, *, private: bool = False, owner_repo: str = OWNER_REPO):
        self.release = Path(release)
        self.private = private
        self.owner_repo = owner_repo
        self.requests: list[tuple[str, str, dict[str, str]]] = []
        names = sorted(path.name for path in self.release.iterdir() if path.is_file())
        self.ids = {name: FIRST_ID + index for index, name in enumerate(names)}
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def origin(self) -> str:
        """The stand-in's own base address."""
        host, port = self._server.server_address[:2]
        return f"http://{host}:{port}"

    @property
    def api(self) -> str:
        """What `NARRATION_API_URL` is set to."""
        return self.origin

    def base_url(self, tag: str = TAG) -> str:
        """What `NARRATION_BASE_URL` is set to for a public release."""
        return f"{self.origin}/{self.owner_repo}/releases/download/{tag}"

    def __enter__(self) -> StandIn:
        self._thread.start()
        return self

    def __exit__(self, *_exc) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join()

    def _handler(self):
        stand_in = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args) -> None:
                """Say nothing: the requests are recorded, not logged."""

            def do_GET(self) -> None:
                """Answer one GET the way a release host would."""
                stand_in.requests.append(("GET", self.path, dict(self.headers.items())))
                status, headers, body = stand_in.answer(self.path, dict(self.headers.items()))
                self.send_response(status)
                for key, value in headers.items():
                    self.send_header(key, value)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        return Handler

    def answer(self, path: str, headers: dict[str, str]) -> tuple[int, dict[str, str], bytes]:
        """Return `(status, headers, body)` for one request path."""
        api = f"/repos/{self.owner_repo}/releases/"
        public = f"/{self.owner_repo}/releases/download/{TAG}/"
        authorised = headers.get("Authorization") == f"Bearer {TOKEN}"
        if path.startswith(api + "tags/"):
            if not authorised or path != f"{api}tags/{TAG}":
                return 404, {}, b'{"message": "Not Found"}'
            assets = [{"name": name, "id": ident} for name, ident in self.ids.items()]
            return (
                200,
                {"Content-Type": "application/json"},
                json.dumps({"assets": assets}).encode(),
            )
        if path.startswith(api + "assets/"):
            ident = path.removeprefix(api + "assets/")
            if not authorised or not ident.isdigit():
                return 404, {}, b'{"message": "Not Found"}'
            if headers.get("Accept") != "application/octet-stream":
                return 200, {"Content-Type": "application/json"}, b'{"id": 0}'
            return 302, {"Location": f"/storage/{ident}"}, b""
        if path.startswith("/storage/"):
            name = self._named(int(path.removeprefix("/storage/") or 0))
            return self._file(name)
        if path.startswith(public) and not self.private:
            return self._file(path.removeprefix(public))
        return 404, {}, b"Not Found"

    def _named(self, ident: int) -> str | None:
        """Return the asset name an id stands for, or None."""
        return next((name for name, known in self.ids.items() if known == ident), None)

    def _file(self, name: str | None) -> tuple[int, dict[str, str], bytes]:
        """Return one release file, or a 404 for anything that is not one."""
        if name is None or name not in self.ids:
            return 404, {}, b"Not Found"
        body = (self.release / name).read_bytes()
        return 200, {"Content-Type": "application/octet-stream"}, body
