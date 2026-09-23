"""Mirror of `src/studyforge/serve/routes/content.py` (R12)."""

from __future__ import annotations

import json

import pytest

from studyforge.contents.document import to_document
from studyforge.generate.declarations import read_corpus
from studyforge.serve.caching import strong_etag
from studyforge.serve.response import Request
from studyforge.serve.routes.content import (
    CONTENT_CACHE,
    GATED,
    NO_SUCH_CONTENT,
    NO_SUCH_UNIT,
    NOT_MATERIAL,
    UNRECOGNISED,
    CorpusContent,
    route,
)
from studyforge.unit.builder import build_unit
from studyforge.unit.builder import render as render_unit
from tests.studyforge.generate.corpora import BOTH, FIXTURES
from tests.studyforge.serve.routes.quizzing import PRACTICE_DOCUMENT, quiz_corpus, sentences
from tests.studyforge.serve.routes.quizzing import UNIT as QUIZ_UNIT
from tests.studyforge.serve.serving import LEAK, FakeSource, a_unit_text, retitled


def get(source, rest, **headers):
    return route(source, Request("GET", "/api/v1/content/" + rest, headers), rest)


def answer(response):
    return json.loads(response.body)


@pytest.mark.parametrize("name", BOTH)
def test_the_toc_is_the_corpus_contents_document_inside_the_envelope(name):
    corpus = read_corpus(FIXTURES / name)
    response = get(CorpusContent(corpus), "toc")
    assert response.status == 200
    assert answer(response)["resource"] == "toc"
    assert answer(response)["document"] == to_document(corpus.contents)


@pytest.mark.parametrize("name", BOTH)
def test_every_unit_with_material_is_served_as_its_built_document(name):
    corpus = read_corpus(FIXTURES / name)
    source = CorpusContent(corpus)
    assert corpus.units
    for unit in corpus.units:
        built = build_unit(unit.directory, declared_practices=unit.declared_practices)
        response = get(source, "units/" + unit.key)
        assert response.status == 200, unit.key
        assert answer(response)["key"] == unit.key
        assert answer(response)["document"] == json.loads(render_unit(built))


def test_the_validator_is_strong_over_the_bytes_and_asks_for_revalidation():
    response = get(CorpusContent(read_corpus(FIXTURES / "depth1")), "toc")
    assert response.header("ETag") == strong_etag(response.body)
    assert response.header("Cache-Control") == CONTENT_CACHE
    assert response.header("Content-Type").startswith("application/json")


def test_two_builds_of_one_corpus_agree_on_the_validator():
    first = get(CorpusContent(read_corpus(FIXTURES / "depth2")), "toc")
    second = get(CorpusContent(read_corpus(FIXTURES / "depth2")), "toc")
    assert first.header("ETag") == second.header("ETag")


def test_a_matching_validator_is_answered_304_with_no_body():
    key, text = a_unit_text()
    source = FakeSource(units={key: text})
    etag = get(source, "units/" + key).header("ETag")
    for header in (etag, f'"other", {etag}', "*"):
        response = get(source, "units/" + key, **{"If-None-Match": header})
        assert (response.status, response.body) == (304, b""), header
        assert response.header("ETag") == etag
        assert response.header("Cache-Control") == CONTENT_CACHE


def test_a_changed_document_is_not_answered_304_by_its_old_validator():
    key, text = a_unit_text()
    source = FakeSource(units={key: text})
    stale = get(source, "units/" + key).header("ETag")
    source.units[key] = retitled(text, "A different title")
    response = get(source, "units/" + key, **{"If-None-Match": stale})
    assert response.status == 200
    assert response.header("ETag") not in (None, stale)
    assert answer(response)["document"]["title"] == "A different title"


def test_an_unknown_key_and_a_declared_unit_without_material_are_two_different_404s():
    source = FakeSource(absent=("topic/unit-09",))
    absent = get(source, "units/topic/unit-09")
    unknown = get(source, "units/topic/unit-10")
    assert (absent.status, answer(absent)["error"]) == (404, NOT_MATERIAL)
    assert (unknown.status, answer(unknown)["error"]) == (404, NO_SUCH_UNIT)


def test_a_corpus_declares_its_units_and_nothing_else():
    corpus = read_corpus(FIXTURES / "depth1")
    source = CorpusContent(corpus)
    assert all(source.declares(unit.key) for unit in corpus.units)
    assert not source.declares("depth-one/unit-99")
    assert source.unit("depth-one/unit-99") is None


@pytest.mark.parametrize("rest", ["", "units", "toc/", "tocs", "../toc", "units/../../toc"])
def test_a_path_that_names_no_content_is_404(rest):
    response = get(CorpusContent(read_corpus(FIXTURES / "depth1")), rest)
    assert response.status == 404
    assert answer(response)["error"] in (NO_SUCH_CONTENT, NO_SUCH_UNIT)


def test_a_leaking_contents_document_is_refused_with_a_fixed_message():
    response = get(FakeSource(toc=json.dumps({"title": LEAK})), "toc")
    assert (response.status, answer(response)["error"]) == (500, GATED)
    assert LEAK.encode() not in response.body


def test_a_leaking_unit_document_is_refused_and_never_echoed():
    key, text = a_unit_text()
    response = get(FakeSource(units={key: retitled(text, LEAK)}), "units/" + key)
    assert response.status in (422, 500)
    assert LEAK.encode() not in response.body


@pytest.mark.parametrize("broken", ["not json", "[]", '{"api": 999}'])
def test_a_unit_document_this_build_does_not_recognise_is_422(broken):
    response = get(FakeSource(units={"k/unit-01": broken}), "units/k/unit-01")
    assert (response.status, answer(response)["error"]) == (422, UNRECOGNISED)


def test_a_quiz_is_served_without_its_key_and_the_source_still_holds_it(tmp_path):
    """⛔ `W452`: the route withholds; `CorpusContent.unit`, which the quiz route grades
    from, does not — the redaction is on the way out and nowhere else."""
    content = CorpusContent(read_corpus(quiz_corpus(tmp_path)))
    served = json.dumps(answer(get(content, f"units/{QUIZ_UNIT}"))["document"])
    held = content.unit(QUIZ_UNIT) or ""
    for sentence in sentences():
        assert sentence not in served
        assert sentence in held
    assert '"correct"' not in served
    assert '"correct": true' in held


def test_withheld_names_every_sentence_and_is_re_read_when_a_unit_file_moves(tmp_path):
    root = quiz_corpus(tmp_path)
    content = CorpusContent(read_corpus(root))
    assert content.withheld() == frozenset(sentences())
    practice = root / PRACTICE_DOCUMENT
    fresh = "A sentence the quiz gained while the instance was serving."
    practice.write_text(
        practice.read_text("utf-8").replace(sentences()[0], fresh), encoding="utf-8"
    )
    assert fresh in content.withheld()
    assert sentences()[0] not in content.withheld()


def test_a_corpus_with_no_quiz_withholds_no_sentence():
    assert CorpusContent(read_corpus(FIXTURES / "depth2")).withheld() == frozenset()
