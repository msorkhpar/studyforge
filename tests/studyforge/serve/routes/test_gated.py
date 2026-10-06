"""Mirror of `src/studyforge/serve/routes/gated.py` (R12): gated text, judged once per version."""

from __future__ import annotations

import gzip

import pytest

from studyforge.serve import versions
from studyforge.serve.caching import gzip_etag
from studyforge.serve.response import Request
from studyforge.serve.routes.gated import MIN_GZIP_BYTES, VARY, Served, answer
from studyforge.serve.versions import Judged, Versions
from tests.studyforge.serve.serving import LEAK

SCRIPT = "text/javascript; charset=utf-8"
ETAG = 'W/"1-2"'
TEXT = b"window.studyforge = {};\n" * 200


@pytest.fixture
def settle_now(monkeypatch):
    monkeypatch.setattr(versions, "SETTLE_NS", -(10**30))


def ask(path, memo=None, served=None, **headers):
    judged = Judged(path, path.stat(), memo or Versions())
    request = Request("GET", "/" + path.name, headers)
    return answer(judged, request, SCRIPT, ETAG, served or Served())


@pytest.fixture
def script(tmp_path):
    path = tmp_path / "index.js"
    path.write_bytes(TEXT)
    return path


def test_identity_when_gzip_is_not_accepted(script):
    for headers in ({}, {"Accept-Encoding": "identity"}, {"Accept-Encoding": "gzip;q=0"}):
        response = ask(script, **headers)
        assert response.status == 200
        assert response.header("Content-Encoding") is None
        assert response.header("ETag") == ETAG
        assert response.body == TEXT
        assert response.header("Vary") == VARY[1]


def test_gzip_when_it_is_accepted(script):
    response = ask(script, **{"Accept-Encoding": "br, gzip"})
    assert response.status == 200
    assert response.header("Content-Encoding") == "gzip"
    assert response.header("ETag") == gzip_etag(ETAG)
    assert response.header("Vary") == VARY[1]
    assert gzip.decompress(response.body) == TEXT
    assert response.length == len(response.body) < len(TEXT)


def test_a_body_too_small_to_code_is_sent_as_it_is(tmp_path):
    path = tmp_path / "tiny.js"
    path.write_bytes(b"x" * (MIN_GZIP_BYTES - 1))
    response = ask(path, **{"Accept-Encoding": "gzip"})
    assert response.header("Content-Encoding") is None


def test_a_matching_validator_is_a_304_for_the_representation_it_names(script):
    assert ask(script, **{"If-None-Match": ETAG}).status == 304
    coded = {"Accept-Encoding": "gzip"}
    assert ask(script, **coded, **{"If-None-Match": ETAG}).status == 200
    response = ask(script, **coded, **{"If-None-Match": gzip_etag(ETAG)})
    assert (response.status, response.body) == (304, b"")
    assert response.header("Vary") == VARY[1]


def test_a_settled_file_is_streamed_from_its_held_verdict(script, settle_now):
    memo = Versions()
    first = ask(script, memo)
    assert first.body == TEXT and first.file is None
    held = ask(script, memo)
    assert held.file == script and held.span == (0, len(TEXT) - 1)
    assert held.version == versions.version_of(script.stat())


def test_a_page_with_a_client_is_sent_from_its_bytes(tmp_path, settle_now):
    page = tmp_path / "index.html"
    page.write_bytes(b"<html><head></head><body></body></html>")
    memo = Versions()
    for _ in range(2):
        response = ask(page, memo, Served(client="/api/v1/run/client.js"))
        assert b'<script src="/api/v1/run/client.js" defer></script></head>' in response.body


def test_a_leak_is_refused_and_stays_refused(tmp_path, settle_now):
    path = tmp_path / "leak.js"
    path.write_text(f"const where = '{LEAK}';\n", encoding="utf-8")
    memo = Versions()
    for _ in range(2):
        response = ask(path, memo)
        assert (response.status, response.body) == (500, b"asset failed the gate\n")


def test_a_held_clean_verdict_does_not_survive_a_rewrite(script, settle_now):
    memo = Versions()
    assert ask(script, memo).status == 200
    script.write_text(f"const where = '{LEAK}';\n", encoding="utf-8")
    assert ask(script, memo).status == 500


def test_text_over_the_limit_is_refused_and_source_over_it_is_streamed_unread(script):
    refused = ask(script, served=Served(limit=16))
    assert (refused.status, refused.body) == (500, b"text too large to gate\n")
    source = ask(script, served=Served(source=True, limit=16))
    assert source.status == 200 and source.file == script


#: A sample address on a real-looking domain, built at run time so no file carries the shape.
SAMPLE_ADDRESS = "admin" + "@" + "company.com"


def test_a_source_file_keeps_its_sample_data(tmp_path):
    path = tmp_path / "Main.java"
    path.write_text(f'String who = "{SAMPLE_ADDRESS}";\n', encoding="utf-8")
    assert ask(path, served=Served(source=True)).status == 200
    assert ask(path).status == 500
