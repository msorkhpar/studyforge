"""The languages of an entry: what a unit's sections say, and what a module's units add up to."""

from __future__ import annotations

from studyforge.generate.declarations import read_corpus
from studyforge.generate.entrylanguages import entry_languages, offer_of
from tests.studyforge.generate.entries_corpus import build, modes
from tests.studyforge.generate.test_modes_site import files
from tests.studyforge.validate.test_languages import READING

TOKENS = (b"data-entry-lang", b"data-entry-label", b"data-pager", b"data-outside", b"mode-outside")


def test_a_unit_is_tagged_with_the_languages_of_its_sections_and_a_common_one_is_not(tmp_path):
    built = build(tmp_path, "c", modes())
    found = entry_languages(read_corpus(built.parent / "c"))
    assert found == {
        "demo/unit-02": ("aa",),
        "demo/unit-03": ("bb",),
        "demo/unit-04": ("aa", "bb"),
        "other/unit-01": ("bb",),
        "other/unit-02": ("bb",),
        "other": ("bb",),
    }, "unit 1 has common prose, and with it the module `demo` is read in every mode"


def test_a_corpus_that_declares_no_modes_reads_no_unit_and_is_untagged(tmp_path):
    built = build(tmp_path, "c", {"corpus_api": 8, "languages": READING["languages"]})
    assert entry_languages(read_corpus(built.parent / "c")) == {}
    html = b"".join(path.read_bytes() for path in sorted(built.rglob("*.html")))
    assert not [word for word in TOKENS if word in html]


def test_the_offer_carries_the_tags_with_the_modes_that_read_each_and_whether_it_is_closed(
    tmp_path,
):
    for outside, closed in (("open", False), ("locked", True)):
        built = build(tmp_path, outside, modes(outside))
        offer = offer_of(read_corpus(built.parent / outside))
        tag = offer.tags["demo/unit-03"]
        assert tag.languages == ("bb",) and tag.label == "Bb"
        assert tag.readers == (("only-bb", "Bb"),)
        assert tag.locked is closed, "closed to the default mode only under locked"
        assert offer.tags["demo/unit-02"].locked is False, "the default mode reads it"
        assert offer.locks is closed
        assert "demo/unit-01" not in offer.tags


def test_a_corpus_without_modes_makes_no_offer(tmp_path):
    built = build(tmp_path, "c", {})
    assert offer_of(read_corpus(built.parent / "c")) is None
    assert files(built)
