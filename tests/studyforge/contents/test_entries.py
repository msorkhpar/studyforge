"""Mirror of `src/studyforge/contents/entries.py` (R12)."""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.address import Address
from studyforge.contents import ContentsError
from studyforge.contents.entries import (
    ENTRY_KEYS,
    GROUP_CHILD_KEY,
    GROUP_KEYS,
    UNIT_CHILD_KEY,
    Contents,
    Entry,
    Group,
)


def an_entry(**overrides) -> Entry:
    base = {
        "address": Address.of("basics", "01-getting-started"),
        "ordinal": 1,
        "title": "Your first class",
        "numbering": "1",
        "page": PurePosixPath("basics/01-getting-started/unit-01-your-first-class.unit.html"),
        "practices": 1,
    }
    return Entry(**{**base, **overrides})


def a_group(**overrides) -> Group:
    base = {"level": "module", "segment": "01-getting-started", "key": "b/01", "title": "Getting"}
    return Group(**{**base, **overrides})


def test_an_entrys_key_is_the_one_address_composes():
    # ⛔ Not spelled here: `Address.unit_key` is the one composer, because
    # these strings are matched by equality across surfaces that never meet.
    entry = an_entry()
    assert entry.key == entry.address.unit_key(entry.ordinal)
    assert entry.key == "basics/01-getting-started/unit-01"


def test_an_entry_is_written_in_a_stated_key_order():
    # ⛔ R10: the order is the tuple's, never a dict's or a sort's.
    assert tuple(an_entry().document) == ENTRY_KEYS


def test_an_entrys_page_is_written_as_a_posix_string():
    assert an_entry().document["page"].endswith(".unit.html")
    assert "\\" not in an_entry().document["page"]


def test_a_group_holding_both_kinds_of_child_is_refused():
    # ⛔ The half-built tree: a container's units hanging one level too high
    # renders a short index with nothing raised.
    with pytest.raises(ContentsError) as raised:
        a_group(groups=(a_group(),), entries=(an_entry(),))
    assert "one or the other" in str(raised.value)


def test_a_group_with_neither_child_is_a_container_that_declares_no_units():
    # ⭐ Legal, and not the same thing as the refusal above: it is written as
    # an empty unit list, so a reader sees "nothing here" rather than nothing.
    assert a_group().document[UNIT_CHILD_KEY] == []


def test_a_group_names_which_kind_of_child_it_has():
    assert GROUP_CHILD_KEY in a_group(groups=(a_group(),)).document
    assert UNIT_CHILD_KEY not in a_group(groups=(a_group(),)).document
    assert UNIT_CHILD_KEY in a_group(entries=(an_entry(),)).document


def test_a_groups_shared_keys_come_first_and_in_a_stated_order():
    written = tuple(a_group(entries=(an_entry(),)).document)
    assert written[: len(GROUP_KEYS)] == GROUP_KEYS
    assert written[-1] == UNIT_CHILD_KEY


def test_a_corpuss_depth_is_len_levels_and_nothing_else():
    # ⛔ Depth 1 is the common case, not the degenerate one.
    assert Contents("demo", "Demo", ("course",)).depth == 1
    assert Contents("demo", "Demo", ("section", "module")).depth == 2


def test_contents_write_their_groups_in_the_order_they_hold_them():
    first = a_group(segment="a", key="a", entries=())
    second = a_group(segment="b", key="b", entries=())
    written = Contents("demo", "Demo", ("course",), (first, second)).document
    assert [group["segment"] for group in written] == ["a", "b"]
