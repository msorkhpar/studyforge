"""Mirror of `src/studyforge/serve/routes/assets.py` (R12)."""

from __future__ import annotations

import os

import pytest

from studyforge.generate import write_site
from studyforge.serve.caching import weak_etag
from studyforge.serve.response import Request
from studyforge.serve.routes import assets as assets_module
from studyforge.serve.routes.assets import (
    ASSET_CACHE,
    DEFAULT_CONTENT_TYPE,
    MAX_PATH,
    nothing_private,
    resolve,
    route,
    serve,
)
from studyforge.serve.withheld import Marks, carries
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


@pytest.mark.parametrize(
    "path",
    [
        "/.studyforge/progress/progress.json",
        "/.studyforge/%70rogress/progress.json",
        "/.studyforge//progress/progress.json",
        "/.studyforge/progress/",
        "/.studyforge/assets/linked.json",
    ],
)
def test_the_readers_progress_record_is_never_served_by_any_spelling(site, path):
    record = site / ".studyforge" / "progress" / "progress.json"
    record.parent.mkdir()
    record.write_text('{"progress": 1}\n', encoding="utf-8")
    (record.parent / "index.html").write_text("<p>x</p>\n", encoding="utf-8")
    (site / ".studyforge" / "assets" / "linked.json").symlink_to(record)
    request = Request("GET", path, {})
    assert resolve(site, path) is None
    assert serve(site, request, path).status == 404
    assert route(site, nothing_private, request, path.lstrip("/")).status == 404


def test_a_private_file_is_404_and_the_default_names_nothing_private(site):
    clip = (site / ".studyforge" / "clip.mp3").resolve()
    request = Request("GET", "/api/v1/assets/.studyforge/clip.mp3", {})
    assert route(site, lambda path: path == clip, request, ".studyforge/clip.mp3").status == 404
    assert route(site, nothing_private, request, ".studyforge/clip.mp3").status == 200


def test_a_site_root_inside_a_corpus_generated_directory_never_serves_the_record(site):
    # ⛔ `SF-39/4`: served from the corpus's generated directory, the store sits at the
    # root's first level rather than its second, and no `private=` is passed here.
    generated = site / ".studyforge"
    record = generated / "progress" / "progress.json"
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text('{"progress": 1}\n', encoding="utf-8")
    control = generated / "elsewhere" / "progress.json"
    control.parent.mkdir(parents=True)
    control.write_text("{}\n", encoding="utf-8")
    for path in ("/progress/progress.json", "/%70rogress/progress.json", "/progress/"):
        assert assets_module.resolve(generated, path) is None, path
        assert get(generated, path).status == 404, path
    assert assets_module.resolve(generated, "/elsewhere/progress.json") == control.resolve()
    assert assets_module.in_a_progress_store(record.resolve())
    assert not assets_module.in_a_progress_store(control.resolve())


def test_a_generated_directory_beside_a_manifest_resolves_and_nowhere_else(site):
    # ⭐ `W230`, `SF-19b/2`: a root holding several corpora puts each one's generated
    # directory one level down. Beside a `corpus.json` it serves; the same tree with
    # no manifest beside it is refused, and the store inside it is refused either way.
    corpus, bare = site / "corpus", site / "bare"
    for where in (corpus, bare):
        (where / ".studyforge" / "assets").mkdir(parents=True)
        (where / ".studyforge" / "assets" / "page.css").write_text("p{}\n", encoding="utf-8")
        store = where / ".studyforge" / "progress"
        store.mkdir()
        (store / "progress.json").write_text("{}\n", encoding="utf-8")
        (store / "index.html").write_text("<p>x</p>\n", encoding="utf-8")
    (corpus / "corpus.json").write_text("{}\n", encoding="utf-8")
    assert (
        resolve(site, "/corpus/.studyforge/assets/page.css")
        == (corpus / ".studyforge" / "assets" / "page.css").resolve()
    )
    assert resolve(site, "/corpus/%2Estudyforge/assets/page.css") is not None
    assert resolve(site, "/bare/.studyforge/assets/page.css") is None
    assert resolve(site, "/corpus/.git/config") is None
    for path in (
        "/corpus/.studyforge/progress/progress.json",
        "/corpus/.studyforge/%70rogress/progress.json",
        "/corpus/.studyforge/progress/",
    ):
        assert resolve(site, path) is None, path
        assert get(site, path).status == 404, path


QUIZ_FILE = '{"questions": [{"id": "q-1", "options": [{"id": "a", "correct": true}]}]}\n'

#: What an instance serving that quiz knows of it: its question id.
SERVED = Marks(questions=frozenset({"q-1"}))


def served_quiz(body: bytes) -> bool:
    return carries(body, SERVED)


@pytest.mark.parametrize("name", ["quiz.json", "quiz.json~", "notes.txt"])
def test_a_file_carrying_a_served_quizs_key_is_refused_a_text_or_an_unknown_type(site, name):
    """⛔ The key's STRUCTURE beside a served question id, even with no sentence."""
    (site / name).write_text(QUIZ_FILE, encoding="utf-8")
    request = Request("GET", f"/{name}", {})
    assert serve(site, request, f"/{name}", withheld=served_quiz).status == 404


def test_the_default_withholds_nothing(site):
    """⭐ What a file may not carry is decided by the quizzes an instance serves."""
    (site / "quiz.json").write_text(QUIZ_FILE, encoding="utf-8")
    assert get(site, "/quiz.json").status == 200


def test_a_withheld_file_is_404_before_any_validator_is_honoured(site):
    (site / "quiz.json").write_text(QUIZ_FILE, encoding="utf-8")
    etag = weak_etag((site / "quiz.json").stat())
    request = Request("GET", "/quiz.json", {"If-None-Match": etag})
    assert serve(site, request, "/quiz.json", withheld=served_quiz).status == 404


def test_withheld_is_asked_of_the_bytes_and_a_sentence_it_names_is_refused(site):
    (site / "notes.md").write_text("The page says why.\n", encoding="utf-8")
    request = Request("GET", "/notes.md", {})
    assert serve(site, request, "/notes.md", withheld=lambda body: b"why" in body).status == 404
    assert serve(site, request, "/notes.md", withheld=lambda body: False).status == 200
    assert route(site, nothing_private, request, "notes.md", withheld=bool).status == 404


def test_media_is_never_read_for_a_key(site):
    asked = []
    request = Request("GET", "/.studyforge/clip.mp3", {})
    response = serve(site, request, "/.studyforge/clip.mp3", withheld=asked.append)
    assert (response.status, asked) == (200, [])
