"""A built site's large static file over a real socket: whole, revalidated, coded, concurrent.

⭐ The readings `serve.versions`, `serve.sending` and `routes.gated` exist for, taken on
the wire: a multi-megabyte index arrives byte for byte at its declared length whether
its verdict was just reached or was held, a matching validator is a `304`, gzip is sent
only to a client that accepts it, and requests are answered side by side.

⛔ **Concurrency is read without a clock**: the barrier route below answers only once
every request is inside it at the same time, so a server that answered one at a time
fails each request on the barrier's own timeout — the generous bound is a guard
against a hang, never the thing measured.
"""

from __future__ import annotations

import gzip
import http.client
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from studyforge.generate import write_site
from studyforge.serve import versions
from studyforge.serve.app import ServingServer
from studyforge.serve.response import json_response
from tests.studyforge.generate.corpora import FIXTURES
from tests.studyforge.serve.serving import FakeSource, fetch, running

INDEX = "/.studyforge/assets/search-index-0.js"
SMALL = "/small.css"

#: How many requests the barrier waits for, and how long it waits before failing them.
SIDE_BY_SIDE = 8
GUARD_SECONDS = 20


def an_index(size: int = 3 * 1024 * 1024) -> bytes:
    """A script holding one large string literal, as a sharded search index does."""
    chooser = random.Random(3)
    words = [
        "".join(chooser.choices("abcdefghijklmnop", k=chooser.randint(2, 9))) for _ in range(3000)
    ]
    text = " ".join(chooser.choices(words, k=size // 5))[:size]
    return f'window.studyforge.searchParts["search-index-0.js"]="{text}";\n'.encode()


@pytest.fixture
def site(tmp_path):
    root = tmp_path / "site"
    root.mkdir()
    write_site(FIXTURES / "depth1", root)
    (root / INDEX.lstrip("/")).write_bytes(an_index())
    (root / SMALL.lstrip("/")).write_bytes(b"main { margin: 0 auto; }\n")
    return root


@pytest.fixture
def settle_now(monkeypatch):
    """Treat every file as settled, so the second request is answered from a held verdict."""
    monkeypatch.setattr(versions, "SETTLE_NS", -(10**30))


@pytest.mark.parametrize("held", [False, True])
def test_a_large_asset_arrives_byte_for_byte_at_its_declared_length(site, monkeypatch, held):
    if held:
        monkeypatch.setattr(versions, "SETTLE_NS", -(10**30))
    expected = (site / INDEX.lstrip("/")).read_bytes()
    assert len(expected) >= 3 * 1024 * 1024
    with running(site, FakeSource()) as server:
        for _ in range(3):
            status, headers, body = fetch(server, INDEX)
            assert status == 200
            assert int(headers["content-length"]) == len(expected)
            assert body == expected
            assert "content-encoding" not in headers
        status, headers, body = fetch(server, INDEX, method="HEAD")
    assert (status, body) == (200, b"")
    assert int(headers["content-length"]) == len(expected)


def test_a_matching_validator_is_answered_304_with_no_body(site, settle_now):
    with running(site, FakeSource()) as server:
        _, headers, _ = fetch(server, INDEX)
        status, again, body = fetch(server, INDEX, {"If-None-Match": headers["etag"]})
        stale, _, _ = fetch(server, INDEX, {"If-None-Match": 'W/"other"'})
    assert (status, body) == (304, b"")
    assert again["etag"] == headers["etag"]
    assert again["cache-control"] == "no-cache"
    assert stale == 200


def test_gzip_is_sent_when_accepted_and_identity_when_not(site, settle_now):
    expected = (site / INDEX.lstrip("/")).read_bytes()
    with running(site, FakeSource()) as server:
        for _ in range(2):
            status, coded, body = fetch(server, INDEX, {"Accept-Encoding": "gzip"})
            assert (status, coded["content-encoding"]) == (200, "gzip")
            assert int(coded["content-length"]) == len(body) < len(expected)
            assert gzip.decompress(body) == expected
        _, plain, raw = fetch(server, INDEX, {"Accept-Encoding": "identity"})
        status, _, body = fetch(
            server, INDEX, {"If-None-Match": coded["etag"], "Accept-Encoding": "gzip"}
        )
    assert "content-encoding" not in plain and raw == expected
    assert coded["vary"] == plain["vary"] == "Accept-Encoding"
    assert coded["etag"] != plain["etag"]
    assert (status, body) == (304, b"")


def test_requests_are_answered_side_by_side_not_one_at_a_time(site):
    barrier = threading.Barrier(SIDE_BY_SIDE, timeout=GUARD_SECONDS)

    def together(request, rest):
        barrier.wait()
        return json_response(200, {"resource": "together"})

    with running(site, FakeSource(), namespaces={"together": together}) as server:
        with ThreadPoolExecutor(SIDE_BY_SIDE) as pool:
            answers = list(
                pool.map(lambda _: fetch(server, "/api/v1/together/x")[0], range(SIDE_BY_SIDE))
            )
    assert answers == [200] * SIDE_BY_SIDE


def test_a_client_slow_to_read_a_large_file_holds_up_no_one_else(site, settle_now):
    with running(site, FakeSource()) as server:
        address, port = server.server_address[:2]
        slow = http.client.HTTPConnection(address, port, timeout=GUARD_SECONDS)
        try:
            slow.request("GET", INDEX)
            reply = slow.getresponse()
            assert reply.status == 200
            started = time.monotonic()
            status, _, _ = fetch(server, SMALL)
            assert status == 200
            assert time.monotonic() - started < GUARD_SECONDS / 2
            assert len(reply.read()) == int(reply.getheader("Content-Length"))
        finally:
            slow.close()


def test_fifty_requests_at_once_are_all_answered(site, settle_now):
    assert ServingServer.request_queue_size >= 50
    with running(site, FakeSource()) as server:
        with ThreadPoolExecutor(50) as pool:
            answers = list(pool.map(lambda _: fetch(server, SMALL)[0], range(50)))
    assert answers == [200] * 50
