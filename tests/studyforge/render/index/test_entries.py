"""Mirror of `src/studyforge/render/index/entries.py` (R12).

⭐ **The shapes the type refuses**, and the one it must not: declared absence.
"""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.render.index import Document, Item, PageError, Section
from tests.studyforge.render.index.indexes import A_HOME_PATH

A_UNIT = Item(key="a/unit-01", numbering="1", title="One", href="a/one.unit.html")


def a_section(**overrides) -> Section:
    """A minimal section, so a test names only what it is about."""
    return Section(**{"level": "module", "key": "a", "title": "A", "items": (A_UNIT,), **overrides})


def test_a_unit_with_a_page_reads_and_one_without_does_not():
    # ⛔ §7's three states, and the two a rendered row can be in. `href=None` is
    # DECLARED absence — a real, expected state — not a degraded link.
    assert A_UNIT.readable
    assert not Item(key="a/unit-02", numbering="2", title="Two").readable


@pytest.mark.parametrize(
    "field,value",
    [
        ("key", ""),
        ("key", None),
        ("key", "   "),
        ("title", ""),
        ("title", "  "),
        ("title", None),
        ("title", 7),
        ("numbering", 7),
        ("numbering", None),
        ("href", ""),
        ("href", "   "),
        ("href", 7),
    ],
)
def test_an_item_that_would_render_as_a_blank_row_is_refused(field, value):
    fields = {"key": "a/unit-01", "numbering": "1", "title": "One", "href": "x.html", field: value}
    with pytest.raises(PageError):
        Item(**fields)


def test_a_refusal_names_the_type_and_never_the_value():
    # ⛔ R7: a title is a corpus's own text, this runs over every unit in a
    # corpus, and the branch that fires is the one where the value is not a
    # title — so a path arrives here, and it must not reach a build log.
    leaked = PurePosixPath(A_HOME_PATH)
    with pytest.raises(PageError) as refused:
        Item(key="a/unit-01", numbering="1", title=leaked)
    assert "PurePosixPath" in str(refused.value)
    assert "jane" not in str(refused.value)
    with pytest.raises(PageError) as blank:
        Item(key="a/unit-01", numbering="1", title="   ")
    assert "an empty string" in str(blank.value)


def test_a_section_holds_subsections_or_units_and_never_both():
    # ⛔ A mixture is a container's units hanging one level too high: the index
    # renders short and nothing raises. `contents.Group` refuses the same shape
    # for the same reason, and this record can be built without going through it.
    with pytest.raises(PageError) as refused:
        Section(level="section", key="a", title="A", sections=(a_section(),), items=(A_UNIT,))
    assert "one level too high" in str(refused.value)


def test_a_deepest_section_with_no_units_is_legal_and_is_not_that():
    # ⚠️ A container that declares no units yet is listed with an empty
    # disclosure, because a tree that dropped it would be short by a container
    # with no way to find out.
    assert a_section(items=()).rows == 0


def test_rows_counts_what_opening_this_section_reveals():
    assert a_section().rows == 1
    assert Section(level="s", key="a", title="A", sections=(a_section(), a_section())).rows == 2


@pytest.mark.parametrize("value", ["", "  ", None, 7])
def test_a_section_with_no_summary_is_refused(value):
    with pytest.raises(PageError):
        a_section(title=value)


@pytest.mark.parametrize("value", [None, 7, ["module"]])
def test_a_level_that_is_not_the_corpus_own_word_is_refused(value):
    with pytest.raises(PageError):
        a_section(level=value)


@pytest.mark.parametrize("children", [[A_UNIT], (A_UNIT, "not an item"), {A_UNIT}])
def test_a_child_collection_that_is_not_a_tuple_of_the_one_type_is_refused(children):
    # ⛔ R10: an order that came out of a set or a directory walk differs between
    # machines, so the type refuses it rather than the renderer noticing later.
    with pytest.raises(PageError):
        a_section(items=children)


def test_a_document_states_its_own_depth_from_the_levels_the_corpus_declared():
    document = Document(title="A", levels=("section", "module"), sections=(a_section(),))
    assert document.depth == 2


@pytest.mark.parametrize(
    "field,value",
    [
        ("title", ""),
        ("title", None),
        ("levels", ()),
        ("levels", None),
        ("levels", ["module"]),
        ("sections", ()),
        ("sections", [a_section()]),
        ("sections", (A_UNIT,)),
    ],
)
def test_an_index_that_would_render_as_a_heading_and_nothing_else_is_refused(field, value):
    fields = {"title": "A", "levels": ("module",), "sections": (a_section(),), field: value}
    with pytest.raises(PageError):
        Document(**fields)


def test_an_index_with_no_sections_says_why_it_is_refused():
    with pytest.raises(PageError) as refused:
        Document(title="A", levels=("module",), sections=())
    assert "failed to load" in str(refused.value)
