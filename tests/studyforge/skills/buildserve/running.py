"""Shared by the skill's tests: the skill on a thread, a copied fixture, a narration service.

⛔ Every corpus copy and every site lives in a directory the harness mints. A fixture
is copied before anything narrates it, because narration writes beside the material.
⭐ The narration service is `cli/narrate`'s own recording fake behind a real loopback
HTTP server, so the skill's `narrate` step goes over the wire like a person's.
"""

from __future__ import annotations

import contextlib
import io
import re
import shutil
import socket
import threading
from collections.abc import Iterator
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from studyforge.corpus.manifest import MANIFEST_FILENAME, load
from studyforge.narrate.wire import Sent
from studyforge.skills.buildserve import build_and_serve
from tests.fixture_checks import FIXTURES, VALID
from tests.studyforge.cli.narrate.service import FakeService

#: How a built page names a clip, relative to the page.
AUDIO = re.compile(r'\baudio="([^"]+)"')

#: The framework's fixture corpora, split on the manifest's own flag.
EXERCISED = tuple(name for name in VALID if load(FIXTURES / name / MANIFEST_FILENAME).exercises)
UNEXERCISED = tuple(name for name in VALID if name not in EXERCISED)


def copied(name: str, where: Path) -> Path:
    """A copy of one fixture under `where`, safe to narrate into."""
    root = where / f"corpus-{name}"
    shutil.copytree(FIXTURES / name, root)
    return root


def directory(where: Path, name: str = "site") -> Path:
    """An existing, empty directory under `where` — what `--out` must name."""
    made = where / name
    made.mkdir()
    return made


def dead_service() -> str:
    """A loopback URL nothing listens on: bound, read and closed."""
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    return f"http://127.0.0.1:{port}"


@dataclass
class Running:
    """The skill on a thread: the server it started, what it printed, its exit code."""

    server: object
    out: io.StringIO
    code: list[int]

    def said(self) -> str:
        return self.out.getvalue()


@contextlib.contextmanager
def skill_running(root: Path, out: Path, **options) -> Iterator[Running]:
    """Run the skill until the block ends, then stop the server it started."""
    stream, ready, held, code = io.StringIO(), threading.Event(), [], []

    def started(server: object) -> None:
        held.append(server)
        ready.set()

    def target() -> None:
        try:
            options.update(port=0, stream=stream, started=started)
            code.append(build_and_serve(root, out, **options))
        finally:
            ready.set()

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    assert ready.wait(120), "the skill neither started serving nor returned"
    assert held, f"the skill returned {code} without serving:\n{stream.getvalue()}"
    try:
        yield Running(held[0], stream, code)
    finally:
        held[0].shutdown()
        thread.join(timeout=30)


def run_once(root: Path, out: Path, **options) -> tuple[int, str]:
    """Run the skill to its end; a server it starts is shut down at once."""
    stream = io.StringIO()

    def started(server) -> None:
        threading.Thread(target=server.shutdown, daemon=True).start()

    code = build_and_serve(root, out, port=0, stream=stream, started=started, **options)
    return code, stream.getvalue()


def partials(said: str) -> list[str]:
    """The name of every partial state printed, in order."""
    return [line.split()[1] for line in said.splitlines() if line.startswith("partial ")]


def steps(said: str) -> list[str]:
    """Every `step <verb> exit <code>` line, in order."""
    return [line for line in said.splitlines() if line.startswith("step ")]


def reported_by_build(said: str) -> set[str]:
    """Every path `studyforge build`'s own report says it wrote or replaced."""
    return {
        line.split()[1] for line in said.splitlines() if line.startswith(("wrote ", "replace "))
    }


def files_under(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def audio_references(site: Path) -> list[str]:
    """Every clip a built page names, as a path under the site, sorted."""
    return sorted(
        (page.parent / reference).relative_to(site).as_posix()
        for page in site.rglob("*.html")
        for reference in AUDIO.findall(page.read_text(encoding="utf-8"))
    )


@contextlib.contextmanager
def narration_service() -> Iterator[tuple[str, FakeService]]:
    """The recording fake narration service on loopback; yields its URL and the fake."""
    fake = FakeService()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self._answer("GET")

        def do_POST(self) -> None:
            self._answer("POST")

        def _answer(self, method: str) -> None:
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else None
            url = f"http://127.0.0.1{self.path}"
            received = fake(Sent(method, url, body, self.headers.get("Accept", ""), 10.0))
            self.send_response(received.status)
            self.send_header("Content-Type", received.media_type)
            self.send_header("Content-Length", str(len(received.body)))
            self.end_headers()
            self.wfile.write(received.body)

        def log_message(self, format: str, *args: object) -> None:
            return None

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}", fake
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)
