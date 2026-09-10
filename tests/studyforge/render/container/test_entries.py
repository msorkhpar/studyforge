"""Mirror of `src/studyforge/render/container/entries.py` (R12).

⭐ The two records and what they refuse — and, above all, that `href=None` and a
*refused* href are two different things reaching two different outcomes.
"""

from __future__ import annotations

import pytest

from studyforge.address import Address
from studyforge.render.container import Document, Item, PageError

ADDRESS = Address(("basics", "01-getting-started"))

#: ⛔ Synthetic, and assembled rather than written whole so the repository's own
#: personal-data sweep is not asked to make an exception for this file (R7).
POISON = "/" + "home/example/material/private-corpus"


def an_item(**overrides) -> Item:
    """A valid item, with one field replaced."""
    fields = {"numbering": "1.1", "title": "Your first class", "href": "unit-01-a.unit.html"}
    return Item(**{**fields, **overrides})


def a_document(**overrides) -> Document:
    """A valid container record, with one field replaced."""
    fields = {
        "address": ADDRESS,
        "title": "Getting Started",
        "variant": "java",
        "items": (an_item(),),
    }
    return Document(**{**fields, **overrides})


@pytest.mark.parametrize("title", ["", "   ", None, 7])
def test_an_item_with_no_usable_title_is_refused(title):
    with pytest.raises(PageError, match="titled"):
        an_item(title=title)


@pytest.mark.parametrize("numbering", [None, 7, 1.1])
def test_numbering_is_text_as_a_reader_sees_it(numbering):
    with pytest.raises(PageError, match="numbering"):
        an_item(numbering=numbering)


def test_numbering_may_be_empty_because_material_may_number_nothing():
    assert an_item(numbering="").numbering == ""


@pytest.mark.parametrize("href", ["", "   ", 7])
def test_an_empty_href_is_refused_because_absent_is_spelled_none(href):
    # ⛔ The distinction the module exists to keep: `None` says "no page was
    # generated"; `""` is an anchor that goes nowhere, and it is a fault.
    with pytest.raises(PageError, match="relative reference or is absent"):
        an_item(href=href)


def test_an_absent_href_is_the_normal_state_of_an_ungenerated_unit():
    item = an_item(href=None)
    assert item.readable is False
    assert an_item().readable is True


@pytest.mark.parametrize("title", ["", "  ", None])
def test_a_container_with_no_usable_title_is_refused(title):
    with pytest.raises(PageError, match="titled"):
        a_document(title=title)


@pytest.mark.parametrize("items", [(), None, [an_item()]])
def test_a_container_page_lists_at_least_one_unit_and_lists_items(items):
    with pytest.raises(PageError, match="lists at least one unit"):
        a_document(items=items)


def test_a_row_that_is_not_an_item_is_refused_rather_than_rendered():
    with pytest.raises(PageError, match="lists Items"):
        a_document(items=("Your first class",))


def test_the_readable_count_is_over_what_is_listed():
    document = a_document(items=(an_item(), an_item(href=None), an_item()))
    assert document.readable == 2
    assert len(document.items) == 3


@pytest.mark.parametrize(
    "build",
    [lambda: an_item(title=None), lambda: an_item(numbering=None), lambda: a_document(title=None)],
    ids=["title", "numbering", "document-title"],
)
def test_every_refusal_names_the_class_it_expected(build):
    # ⛔ R6: "invalid" is not a refusal, and `describe` names what arrived
    # without reproducing it — `None` is reported as "nothing".
    with pytest.raises(PageError) as raised:
        build()
    assert "nothing" in str(raised.value)


def test_a_poisoned_string_is_a_legal_title_and_reaches_no_refusal():
    # ⭐ Recorded rather than assumed. Nothing in this module refuses a string
    # for its CONTENT, so no refusal here can echo one; the R7 assertion that
    # bites is in `test_listing`, where a poisoned href is refused as rooted and
    # the message must not carry it.
    assert an_item(title=POISON, href=None).title == POISON
    assert a_document(title=POISON).title == POISON
