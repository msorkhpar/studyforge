"""Mirror of `src/studyforge/serve/addressing.py` (R12).

⭐ **E05 SF-19b: "N-segment addresses route correctly at depth 1 and depth 2."** Every
unit of both FND-04 fixtures is located under its own corpus at that corpus's depth,
and refused under the other corpus, whose depth it does not have.
"""

from __future__ import annotations

import json

import pytest

from studyforge.generate.declarations import read_corpus
from studyforge.serve.addressing import CORPORA, CorporaContent, locate
from studyforge.serve.routes.content import CorpusContent
from tests.studyforge.generate.corpora import BOTH, FIXTURES
from tests.studyforge.serve.serving import FakeSource


def corpora():
    return {name: read_corpus(FIXTURES / name) for name in BOTH}


def depths():
    return {corpus.manifest.source: corpus.manifest.depth for corpus in corpora().values()}


def test_the_two_fixtures_really_are_depth_one_and_depth_two():
    assert sorted(depths().values()) == [1, 2]


@pytest.mark.parametrize("name", BOTH)
def test_every_unit_is_located_at_its_own_corpus_depth(name):
    corpus = corpora()[name]
    source = corpus.manifest.source
    assert corpus.units
    for unit in corpus.units:
        located = locate(f"{source}/{unit.key}", depths())
        assert located is not None, unit.key
        assert (located.corpus, located.key) == (source, unit.key)
        assert located.address.depth == corpus.manifest.depth
        assert located.path == f"{source}/{unit.key}"


@pytest.mark.parametrize("name", BOTH)
def test_a_unit_key_is_not_located_under_the_corpus_whose_depth_it_does_not_have(name):
    found = corpora()
    other = next(corpus for key, corpus in found.items() if key != name)
    for unit in found[name].units:
        assert locate(f"{other.manifest.source}/{unit.key}", depths()) is None, unit.key


def test_a_segment_too_many_or_too_few_is_never_truncated_or_padded_to_fit():
    found = corpora()
    one, two = (found[name].manifest.source for name in BOTH)
    first_one, first_two = found["depth1"].units[0].key, found["depth2"].units[0].key
    head, _, unit = first_two.rpartition("/")
    assert locate(f"{one}/extra/{first_one}", depths()) is None
    assert locate(f"{two}/{head.split('/')[0]}/{unit}", depths()) is None
    assert locate(f"{two}/{head}/extra/{unit}", depths()) is None


@pytest.mark.parametrize(
    "spelling",
    [
        "",
        "{one}",
        "{one}/",
        "/{one}/{key}",
        "{one}/{key}/",
        "{one}/{upper}",
        "{one}/{unpadded}",
        "{one}/{overpadded}",
        "{one}/{encoded}",
        "{one}/../{key}",
        "nobody/{key}",
        "{one}/{container}",
    ],
)
def test_every_other_spelling_is_not_located(spelling):
    corpus = corpora()["depth1"]
    key = corpus.units[0].key
    container, _, unit = key.rpartition("/")
    path = spelling.format(
        one=corpus.manifest.source,
        key=key,
        upper=key.upper(),
        unpadded=f"{container}/unit-{int(unit.split('-')[1])}",
        overpadded=f"{container}/unit-0{unit.split('-')[1]}",
        encoded=key.replace("/", "%2f"),
        container=container,
    )
    assert locate(path, depths()) is None, path


def test_a_non_string_is_not_located():
    assert locate(None, depths()) is None


def both_content():
    found = corpora().values()
    sources = {corpus.manifest.source: CorpusContent(corpus) for corpus in found}
    return found, CorporaContent(sources, depths())


def test_the_contents_document_lists_every_corpus_in_source_order():
    found, source = both_content()
    listed = json.loads(source.toc())[CORPORA]
    ordered = sorted(found, key=lambda corpus: corpus.manifest.source)
    assert [entry["corpus"] for entry in listed] == [c.manifest.source for c in ordered]
    for entry, corpus in zip(listed, ordered, strict=True):
        assert entry["contents"] == json.loads(CorpusContent(corpus).toc())


def test_a_unit_is_served_by_its_corpus_qualified_key_and_by_no_other_spelling():
    found, source = both_content()
    for corpus in found:
        name = corpus.manifest.source
        for unit in corpus.units:
            own = CorpusContent(corpus).unit(unit.key)
            assert own is not None
            assert source.unit(f"{name}/{unit.key}") == own
            assert source.declares(f"{name}/{unit.key}")
            assert source.unit(unit.key) is None
            assert not source.declares(unit.key)


def test_a_corpus_with_a_source_and_no_depth_is_refused():
    with pytest.raises(ValueError, match="both a content source and a depth"):
        CorporaContent({"lonely": FakeSource()}, {})
