"""Mirror of `src/studyforge/corpus/placement/names.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.corpus.placement import (
    CONTAINER_SUFFIX,
    UNIT_SUFFIX,
    PlacementError,
    container_page_name,
    is_container_page,
    is_unit_page,
    label_of,
    unit_page_name,
    unit_stem,
)
from studyforge.corpus.placement.names import ROOT_INDEX_FILENAME

TITLE = "Introduction to the Streams API"


def test_a_generated_page_is_never_called_index_html():
    # ⛔ §5. A scan reads names, and `index.html` is neither unique in a
    # listing nor distinguishable from the root index — and under `sibling`,
    # where twenty units share a directory, it cannot be written twice.
    assert unit_page_name(7, TITLE) != ROOT_INDEX_FILENAME
    assert container_page_name(("Basics", "Streams API")) != ROOT_INDEX_FILENAME


def test_the_name_is_the_label_and_the_title():
    assert unit_page_name(7, TITLE) == "unit-07-introduction-to-the-streams-api.unit.html"


def test_the_default_label_is_the_units_own_ordinal_and_not_its_source_filename():
    # ⭐ The derivation SF-31's golden was waiting on, stated as a test.
    # ⛔ From identity, never from the filename: `README_4.4.1.md`,
    # `01-what-a-triple-is.md` and `1.md` are three corpora's three
    # conventions, and a framework that read any of them would carry a parser
    # per corpus (R1).
    assert unit_stem(7, TITLE).startswith("unit-07-")


def test_a_corpus_that_records_its_own_numbering_gets_it_verbatim():
    # ⭐ The seam. The day an adapter records `4.4.1`, §5's worked example is
    # reproduced exactly and this module does not change.
    assert unit_page_name(7, TITLE, label="4.4.1") == (
        "4.4.1-introduction-to-the-streams-api.unit.html"
    )


def test_every_artifact_of_one_unit_shares_a_stem():
    # ⭐ So a reader sees them grouped in a listing, and a rename is one
    # decision rather than five.
    stem = unit_stem(3, "Fields and constructors")
    assert unit_page_name(3, "Fields and constructors") == stem + UNIT_SUFFIX


def test_the_ordinal_is_zero_padded_so_ten_units_sort_correctly():
    assert unit_stem(9, "A")[:8] == "unit-09-"
    assert unit_stem(10, "A")[:8] == "unit-10-"


@pytest.mark.parametrize("ordinal", [0, -1, 1.0, True, None, "1"])
def test_an_ordinal_that_is_not_one_is_refused(ordinal):
    with pytest.raises(ValueError, match="ordinal"):
        unit_stem(ordinal, TITLE)


@pytest.mark.parametrize("title", ["", "   ", "...", "///"])
def test_a_title_that_slugifies_to_nothing_is_refused_and_blamed_on_the_corpus(title):
    # ⛔ R6, and it says whose defect it is: titles are the corpus's.
    with pytest.raises(PlacementError, match="corpus defect"):
        unit_stem(1, title)


@pytest.mark.parametrize("label", ["", "  ", "a/b", "a b", "a\tb", 7, None if False else "\n"])
def test_a_label_that_could_not_be_a_filename_is_refused(label):
    with pytest.raises(PlacementError, match="label"):
        label_of(1, label)


def test_a_label_need_not_be_a_slug_because_it_is_presentation():
    # ⚠️ `4.4.1` is not a slug and must not have to be — it is the corpus's
    # own numbering, and rewriting it would make the page's name disagree with
    # the material's own table of contents.
    assert label_of(1, "4.4.1") == "4.4.1"


def test_a_container_page_is_named_from_its_deepest_title():
    # ⚠️ Not the joined address: the directory already says where it is, and
    # repeating it makes the deepest level unreadable in a listing.
    assert container_page_name(("Basics", "Streams API")) == "streams-api" + CONTAINER_SUFFIX


@pytest.mark.parametrize("titles", [(), ("",), ("...",)])
def test_a_container_with_no_usable_title_is_refused(titles):
    with pytest.raises(PlacementError):
        container_page_name(titles)


def test_the_two_suffixes_are_what_a_scan_globs_for():
    # ⛔ Load-bearing: they are what tells a unit page from a container page
    # and both from the root index, without opening a file.
    assert is_unit_page(unit_page_name(1, TITLE))
    assert not is_container_page(unit_page_name(1, TITLE))
    assert is_container_page(container_page_name(("A",)))
    assert not is_unit_page(container_page_name(("A",)))
    assert not is_unit_page(ROOT_INDEX_FILENAME)
    assert not is_container_page(ROOT_INDEX_FILENAME)


def test_naming_is_deterministic():
    # ⛔ R10: no clock, no hash, no filesystem order.
    assert unit_page_name(7, TITLE) == unit_page_name(7, TITLE)
