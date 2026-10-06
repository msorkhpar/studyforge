"""The search index a whole site build writes, over corpora of different shapes.

⭐ Every shape builds, writes a precompiled index that loads under `node`, finds its pages by
their titles, and never finds what is not prose. ⚠️ Without `node` the same build succeeds, warns
once, and writes the records and the part that builds them, as a build always did.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from studyforge.archive.scrub import assert_clean
from studyforge.generate import write_site
from studyforge.render.pageassets import search as searchindex
from tests.studyforge.exercise.quiz.mock_corpus import built_files, mock_corpus
from tests.studyforge.generate.test_example_site import BOTH, WITH
from tests.studyforge.generate.test_section_language import build
from tests.studyforge.render.pageassets.test_search import index_json, needs_node, round_trip
from tests.support import repository_root

FIXTURES = repository_root() / "tests" / "fixtures"
ASSETS = ".studyforge/assets/"


def search_files(out: Path) -> dict[str, str]:
    """The search files a build wrote, by name in the shared asset directory."""
    directory = out / ASSETS
    return {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(directory.iterdir())
        if path.name.startswith(("search-", "minisearch"))
    }


def fixture(name):
    def built(tmp_path: Path) -> Path:
        out = tmp_path / name
        out.mkdir()
        write_site(FIXTURES / name, out)
        return out

    return built


def examples(tmp_path: Path) -> Path:
    return build(tmp_path, "examples", WITH, BOTH)


def mock(tmp_path: Path) -> Path:
    return mock_corpus(tmp_path / "mock")


#: ⭐ A plain corpus, one at greater depth, one with two units on one source, one with practices,
#: one with an example in two languages, and one with a mock exam.
SHAPES = {
    "depth1": fixture("depth1"),
    "depth2": fixture("depth2"),
    "shared-origin": fixture("shared-origin"),
    "runnable": fixture("runnable"),
    "examples": examples,
    "mock": mock,
}

TITLE = re.compile(r"<title>([^<]+)</title>")


@needs_node
@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_every_shape_writes_a_precompiled_index_that_loads_and_finds_its_pages(tmp_path, shape):
    out = SHAPES[shape](tmp_path)
    found = search_files(out)
    assert searchindex.BUILD_NAME not in found
    manifest = json.loads(found[searchindex.INDEX_NAME][len(searchindex.GLOBAL) : -2])
    assert manifest["version"] == searchindex.PRECOMPILED_VERSION
    pages = sorted((out / ASSETS).joinpath(page).resolve() for page in manifest["pages"])
    assert pages and all(page.is_file() for page in pages)
    # A word of each indexed page's title finds that page.
    words = {}
    for page in pages:
        title = TITLE.search(page.read_text(encoding="utf-8")).group(1)
        words[str(page)] = max(re.findall(r"[A-Za-z]{4,}", title), key=len)
    loaded = round_trip(found, tmp_path / "trip", sorted(set(words.values())))
    for page, word in words.items():
        hits = loaded["results"][word]
        hit_pages = {
            str((out / ASSETS).joinpath(loaded["pages"][int(h["id"].split(".")[0])]).resolve())
            for h in hits
        }
        assert page in hit_pages, (shape, word)
    for name, body in found.items():
        assert len(body.encode("utf-8")) < 4 * 1024 * 1024, name


@needs_node
def test_an_example_its_code_and_its_output_are_not_found(tmp_path):
    found = search_files(examples(tmp_path))
    results = round_trip(found, tmp_path / "trip", ["printed", "words"])["results"]
    assert results["printed"] == [], "the example's printed output is not prose"
    assert results["words"], "the prose beside it is"


@needs_node
def test_the_page_a_mock_exam_is_on_is_not_indexed(tmp_path):
    out = mock(tmp_path)
    files = built_files(out)
    exam = [p for p, b in files.items() if p.endswith(".html") and b"data-practice-mock" in b]
    assert len(exam) == 1
    manifest = json.loads(search_files(out)[searchindex.INDEX_NAME][len(searchindex.GLOBAL) : -2])
    assert not [p for p in manifest["pages"] if p.endswith(Path(exam[0]).name)]


REDACTION = {
    "type": "para",
    "text": "Redact `Bearer` followed by 16 or more characters.",
}


@needs_node
def test_prose_about_a_secret_shape_is_scrubbed_from_a_built_index_that_still_loads(tmp_path):
    from tests.studyforge.validate.test_languages import document

    doc = document(ordinal=1, blocks=[REDACTION])
    found = search_files(build(tmp_path, "redaction", [doc], {}))
    for name, body in found.items():
        if name.startswith("search-index"):
            assert_clean(body, name)
    serialised = index_json(found)
    assert "followed" not in serialised
    results = round_trip(found, tmp_path / "trip", ["redact", "followed"])["results"]
    assert results["redact"], "the index loads and finds the prose around the shape"
    assert results["followed"] == [], "the scrubbed words are gone"


def test_without_node_a_site_builds_warns_once_and_writes_the_records(tmp_path, capfd):
    out = tmp_path / "out"
    out.mkdir()
    write_site(FIXTURES / "depth1", out, node=None)
    err = capfd.readouterr().err
    assert err.count("studyforge: warning:") == 1
    assert searchindex.warn("node was not found") in err
    found = search_files(out)
    assert sorted(found) == sorted(
        [searchindex.INDEX_NAME, searchindex.LIBRARY_NAME, searchindex.BUILD_NAME]
    )
    body = found[searchindex.INDEX_NAME]
    assert json.loads(body[len(searchindex.GLOBAL) : -2])["version"] == searchindex.VERSION


@needs_node
def test_with_node_a_site_writes_the_files_it_always_wrote(tmp_path, capfd):
    out = tmp_path / "out"
    out.mkdir()
    written = write_site(FIXTURES / "depth1", out)
    assert capfd.readouterr().err == ""
    names = sorted(str(p).rsplit("/", 1)[-1] for p in written.assets)
    assert names == ["minisearch.js", "page.css", "page.js", "search-index.js"]
