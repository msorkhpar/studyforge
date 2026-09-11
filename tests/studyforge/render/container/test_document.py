"""Mirror of `src/studyforge/render/container/document.py` (R12).

⭐ The page's format: which slots exist, which are deliberately empty, and the
one place the conditional newline lives.
"""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.address import Address
from studyforge.corpus.placement import ContainerLocations, CorpusLocations
from studyforge.corpus.placement import identity as identity_block
from studyforge.render import templates
from studyforge.render.container import Document, Item, Link, Links, PageError, Placement, compose
from studyforge.render.container import document as document_module

ADDRESS = Address(("basics", "01-getting-started"))


def a_placement(corpus: str = "demo") -> Placement:
    """A placement for a container page, with no corpus behind it."""
    return Placement(
        corpus=corpus,
        container=ContainerLocations(
            page=PurePosixPath("basics/01-getting-started/getting-started.section.html")
        ),
        shared=CorpusLocations(
            root_index=PurePosixPath("index.html"),
            assets=PurePosixPath(".studyforge/assets"),
            archive=PurePosixPath(".studyforge/archive"),
            site_cache=PurePosixPath(".studyforge/site.json"),
        ),
    )


def a_document(**overrides) -> Document:
    """A valid container record, with one field replaced."""
    fields = {
        "address": ADDRESS,
        "title": "Getting Started",
        "variant": "java",
        "items": (Item("1.1", "Your first class", "unit-01-a.unit.html"),),
        "level": "module",
        "note": None,
    }
    return Document(**{**fields, **overrides})


def test_every_skeleton_slot_is_filled_and_none_is_invented():
    # ⛔ `templates.fill` is exact in BOTH directions, so this is what catches a
    # slot the skeleton dropped — the failure that otherwise takes a region off
    # the page with nothing raised.
    filled = set(templates.placeholders(document_module.SKELETON))
    assert set(document_module.EMPTY_SLOTS) <= filled
    compose(a_document(), a_placement())


def test_the_empty_slots_are_the_ones_a_container_page_has_no_answer_for():
    # ⚠️ Named, so their absence is a decision rather than an oversight: a
    # container page's own contents ARE the unit list, it declares no practices,
    # and narration is a unit's.
    # ⭐ `breadcrumb` joined them when `SF-15` added the slot, and it is the one
    # of the five that is a GAP rather than an absence — a container page has
    # ancestors to name. That it is empty here is `SF-27`'s row (`SF-15/2`), and
    # the point of the by-name form is that the skeleton's growth could not be
    # silent: this assertion is what went red.
    # ⭐ **And it went red a second time, as designed**: `SF-30` added `mark`, and
    # a read mark is a UNIT's — a container is read by reading what is under it.
    # ⚠️ The marks themselves DO reach this page, as a state on the rows, which is
    # why each row now carries the unit key a mark is filed under.
    assert document_module.EMPTY_SLOTS == (
        "breadcrumb",
        "mark",
        "outline",
        "pending",
        "player",
    )


def test_the_page_ends_in_exactly_one_newline():
    page = compose(a_document(), a_placement())
    assert page.endswith("</html>\n")
    assert not page.endswith("\n\n")


def test_the_identity_block_says_container_and_addresses_no_unit():
    page = compose(a_document(), a_placement())
    found = identity_block.parse(page, ADDRESS.depth, "a page")
    assert found.kind == document_module.KIND == "container"
    assert found.unit is None


def test_a_variant_that_is_not_a_slug_is_refused_as_this_package_s_error():
    # ⛔ Re-typed, not re-worded: `placement` owns what an identity may say, and
    # a caller rendering a site catches one family.
    with pytest.raises(PageError, match="cannot identify itself"):
        compose(a_document(variant="Not A Slug"), a_placement())


def test_the_identity_refusal_does_not_reproduce_what_it_refused():
    poison = "/" + "home/example/material/private-corpus"
    with pytest.raises(PageError) as raised:
        compose(a_document(variant=poison), a_placement())
    assert poison not in str(raised.value)


def test_the_masthead_names_the_level_then_the_address_then_the_variant():
    # ⚠️ `level` is the CORPUS's word for this depth (`levels[-1]`), never this
    # framework's own (R1).
    assert document_module.meta(a_document()) == (
        "<p>module · basics · 01-getting-started · java</p>"
    )


def test_a_corpus_that_names_no_level_still_gets_a_masthead():
    assert document_module.meta(a_document(level="")) == "<p>basics · 01-getting-started · java</p>"


def test_the_masthead_escapes_what_the_corpus_wrote():
    assert "&lt;b&gt;" in document_module.meta(a_document(level="<b>"))


@pytest.mark.parametrize("said", [None, "", "   ", 7])
def test_a_container_that_says_nothing_about_itself_gets_no_note(said):
    assert document_module.note(a_document(note=said)) == ""


def test_the_note_is_the_corpus_s_own_sentence_rendered_as_prose():
    rendered = document_module.note(a_document(note="What `this` module is."))
    assert rendered == "<p>What <code>this</code> module is.</p>"


def test_the_note_sits_above_the_unit_list():
    page = compose(a_document(note="What this module is."), a_placement())
    assert page.index("What this module is.") < page.index('aria-label="Units"')


def test_an_optional_region_is_exactly_empty_or_its_markup_and_one_newline():
    assert document_module._region("") == ""
    assert document_module._region("<p>x</p>") == "<p>x</p>\n"


def test_the_page_without_a_note_and_the_page_with_one_differ_only_by_that_region():
    without = compose(a_document(), a_placement())
    with_note = compose(a_document(note="A sentence."), a_placement())
    assert with_note.replace("<p>A sentence.</p>\n", "") == without


def test_the_bar_is_absent_when_nothing_knows_the_reading_order():
    assert 'aria-label="Between units"' not in compose(a_document(), a_placement())


def test_the_bar_carries_every_slot_it_is_given():
    page = compose(
        a_document(),
        a_placement(),
        Links(
            previous=Link("../../advanced/going-further.section.html", "Going Further"),
            index=Link("../../index.html", "Depth Two Demo"),
            next=Link("../02-going-further/going-further.section.html", "Going Further"),
        ),
    )
    for relation in ("prev", "up", "next"):
        assert f'rel="{relation}"' in page


def test_a_bare_same_directory_neighbour_survives_the_bar_s_gate():
    # ⛔ `W57`'s fix, asserted from this page rather than inherited. Under
    # `sibling` two containers of one parent share a directory, so the
    # commonest neighbour href of all is a bare filename — the shape that had
    # no entry in the old `SAFE_SCHEMES` and dropped 6 of 13 slots silently
    # (`SF-13/1`).
    page = compose(
        a_document(),
        a_placement(),
        Links(next=Link("going-further.section.html", "Going Further")),
    )
    assert 'rel="next" href="going-further.section.html"' in page


def test_composing_twice_gives_identical_text():
    assert compose(a_document(), a_placement()) == compose(a_document(), a_placement())
