"""Mirror of `src/studyforge/serve/routes/assets.py` (R12)."""

from __future__ import annotations

import os

import pytest

from studyforge.generate import write_site
from studyforge.serve.caching import weak_etag
from studyforge.serve.response import Request
from studyforge.serve.routes.assets import (
    ASSET_CACHE,
    DEFAULT_CONTENT_TYPE,
    MAX_PATH,
    nothing_private,
    resolve,
    route,
    serve,
)
from tests.studyforge.generate.corpora import FIXTURES
from tests.studyforge.serve.serving import LEAK

CLIP = bytes(range(256)) * 4


@pytest.fixture
def site(tmp_path):
    root = tmp_path / "site"
    root.mkdir()
    write_site(FIXTURES / "depth1", root)
    (root / ".studyforge" / "clip.mp3").write_bytes(CLIP)
    return root


def get(root, path, **headers):
    return serve(root, Request("GET", path, headers), path)


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/", "index.html"),
        ("/index.html", "index.html"),
        ("/.studyforge/assets/page.css", ".studyforge/assets/page.css"),
        ("/.studyforge//assets/page.css", ".studyforge/assets/page.css"),
        ("/%2Estudyforge/assets/page.css", ".studyforge/assets/page.css"),
    ],
)
def test_a_built_path_resolves_to_its_file(site, path, expected):
    assert resolve(site, path) == (site / expected).resolve()


@pytest.mark.parametrize(
    "path",
    [
        "/../site/index.html",
        "/%2e%2e/site/index.html",
        "/.studyforge%2fassets/page.css",
        "/.studyforge/.hidden",
        "/.git/config",
        "/nested/.studyforge/x",
        "/index.html%00",
        "/%5c..%5cindex.html",
        "/%ff",
        "index.html",
        "/" + "a" * MAX_PATH,
        "/missing.html",
        "/nested",
        "/.studyforge",
    ],
)
def test_every_traversal_and_every_hidden_name_resolves_to_nothing(site, path):
    for planted in (site / ".studyforge" / ".hidden", site / ".git" / "config"):
        planted.parent.mkdir(parents=True, exist_ok=True)
        planted.write_text("x", encoding="utf-8")
    (site / "nested" / ".studyforge").mkdir(parents=True)
    (site / "nested" / ".studyforge" / "x").write_text("x", encoding="utf-8")
    assert resolve(site, path) is None


def test_a_symlink_out_of_the_root_resolves_to_nothing(tmp_path, site):
    secret = tmp_path / "secret.txt"
    secret.write_text("outside", encoding="utf-8")
    (site / "link.txt").symlink_to(secret)
    (site / "inside.txt").symlink_to(site / "index.html")
    assert resolve(site, "/link.txt") is None
    assert resolve(site, "/inside.txt") == (site / "index.html").resolve()


def test_a_built_page_is_served_whole_with_a_weak_validator(site):
    response = get(site, "/index.html")
    assert response.status == 200
    assert response.body == (site / "index.html").read_bytes()
    assert response.header("ETag") == weak_etag((site / "index.html").stat())
    assert response.header("ETag").startswith("W/")
    assert response.header("Cache-Control") == ASSET_CACHE
    assert response.header("Content-Type").startswith("text/html")


def test_a_matching_validator_is_304_and_a_changed_file_is_not(site):
    page = site / "index.html"
    etag = get(site, "/index.html").header("ETag")
    fresh = get(site, "/index.html", **{"If-None-Match": etag})
    assert (fresh.status, fresh.body, fresh.header("ETag")) == (304, b"", etag)
    page.write_bytes(page.read_bytes() + b"<!-- changed -->")
    os.utime(page, ns=(10**18, 10**18))
    stale = get(site, "/index.html", **{"If-None-Match": etag})
    assert stale.status == 200
    assert stale.header("ETag") != etag


def test_a_binary_asset_without_a_range_is_the_whole_file(site):
    response = get(site, "/.studyforge/clip.mp3")
    assert (response.status, response.span, response.length) == (200, (0, 1023), 1024)
    assert response.header("Accept-Ranges") == "bytes"
    assert response.header("Content-Type") == "audio/mpeg"


@pytest.mark.parametrize(
    ("header", "span"),
    [
        ("bytes=0-9", (0, 9)),
        ("bytes=1000-", (1000, 1023)),
        ("bytes=-24", (1000, 1023)),
        ("bytes=1020-5000", (1020, 1023)),
        ("bytes=512-512", (512, 512)),
    ],
)
def test_a_satisfiable_range_is_206_with_its_exact_arithmetic(site, header, span):
    response = get(site, "/.studyforge/clip.mp3", Range=header)
    first, last = span
    assert (response.status, response.span) == (206, span)
    assert response.length == last - first + 1
    assert response.header("Content-Range") == f"bytes {first}-{last}/1024"


@pytest.mark.parametrize(
    "header", ["bytes=1024-", "bytes=1024-2000", "bytes=5-1", "bytes=-0", "bytes=x-"]
)
def test_an_unsatisfiable_range_is_416_naming_the_length(site, header):
    response = get(site, "/.studyforge/clip.mp3", Range=header)
    assert response.status == 416
    assert response.header("Content-Range") == "bytes */1024"
    assert response.file is None


def test_if_range_with_a_weak_validator_sends_the_whole_file(site):
    etag = get(site, "/.studyforge/clip.mp3").header("ETag")
    response = get(site, "/.studyforge/clip.mp3", Range="bytes=0-9", **{"If-Range": etag})
    assert (response.status, response.span) == (200, (0, 1023))


def test_an_empty_asset_is_whole_without_a_range_and_416_with_one(site):
    (site / "empty.mp3").write_bytes(b"")
    assert (get(site, "/empty.mp3").status, get(site, "/empty.mp3").length) == (200, 0)
    assert get(site, "/empty.mp3", Range="bytes=0-").status == 416


def test_text_ignores_a_range_and_is_answered_whole(site):
    response = get(site, "/index.html", Range="bytes=0-4")
    assert response.status == 200
    assert response.body == (site / "index.html").read_bytes()
    assert response.header("Accept-Ranges") == "none"


def test_text_carrying_personal_data_is_refused_and_never_echoed(site):
    (site / "notes.txt").write_text(f"see {LEAK}\n", encoding="utf-8")
    response = get(site, "/notes.txt")
    assert response.status == 500
    assert LEAK.encode() not in response.body


def test_an_unknown_extension_is_opaque_bytes(site):
    (site / "data.bin").write_bytes(b"\x00\x01")
    assert get(site, "/data.bin").header("Content-Type") == DEFAULT_CONTENT_TYPE


def test_a_private_file_is_404_and_the_default_names_nothing_private(site):
    clip = (site / ".studyforge" / "clip.mp3").resolve()
    request = Request("GET", "/api/v1/assets/.studyforge/clip.mp3", {})
    assert route(site, lambda path: path == clip, request, ".studyforge/clip.mp3").status == 404
    assert route(site, nothing_private, request, ".studyforge/clip.mp3").status == 200
