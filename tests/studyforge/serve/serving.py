"""Shared by the serve tests: a server on an ephemeral loopback port, and a stand-in source.

⭐ Every test that touches a socket binds `127.0.0.1` port `0` through `running`,
so the kernel picks a free port and no two tests can collide on one.
"""

from __future__ import annotations

import contextlib
import http.client
import json
import threading
from collections.abc import Iterator
from pathlib import Path

from studyforge.generate.declarations import read_corpus
from studyforge.serve.app import ServingServer, make_server
from studyforge.unit.builder import build_unit
from studyforge.unit.builder import render as render_unit
from tests.studyforge.generate.corpora import FIXTURES

#: A home path built at run time, so no file in the tree carries the shape.
LEAK = "/" + "home" + "/jane-doe/notes"


@contextlib.contextmanager
def running(site_root: Path, source: object, **options: object) -> Iterator[ServingServer]:
    """Serve on `127.0.0.1:0` in a thread for the duration of the block."""
    server = make_server(site_root, source, port=0, **options)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def fetch(
    server: ServingServer,
    path: str,
    headers: dict[str, str] | None = None,
    method: str = "GET",
    host: str | None = None,
) -> tuple[int, dict[str, str], bytes]:
    """Send one request over a real connection; return status, lower-cased headers, body."""
    address, port = server.server_address[:2]
    connection = http.client.HTTPConnection(address, port, timeout=10)
    try:
        connection.putrequest(method, path, skip_host=host is not None, skip_accept_encoding=True)
        if host is not None:
            connection.putheader("Host", host)
        for name, value in (headers or {}).items():
            connection.putheader(name, value)
        connection.endheaders()
        reply = connection.getresponse()
        body = reply.read()
        return reply.status, {k.lower(): v for k, v in reply.getheaders()}, body
    finally:
        connection.close()


class FakeSource:
    """A `ContentSource` whose documents a test can change between two requests."""

    def __init__(self, toc: str = "{}\n", units: dict | None = None, absent: tuple = ()):
        self.toc_text = toc
        self.units = dict(units or {})
        self.absent = set(absent)

    def toc(self) -> str:
        return self.toc_text

    def unit(self, key: str) -> str | None:
        return self.units.get(key)

    def declares(self, key: str) -> bool:
        return key in self.units or key in self.absent


def a_unit_text(name: str = "depth1") -> tuple[str, str]:
    """Return `(key, text)` of the first unit a fixture corpus really builds."""
    source = read_corpus(FIXTURES / name).units[0]
    document = build_unit(source.directory, declared_practices=source.declared_practices)
    return source.key, render_unit(document)


def retitled(text: str, title: str) -> str:
    """Return a unit document's text with one value changed and its key order kept."""
    document = json.loads(text)
    document["title"] = title
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"
