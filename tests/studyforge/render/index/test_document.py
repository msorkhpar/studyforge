"""Mirror of `src/studyforge/render/index/document.py` (R12).

⭐ **The skeleton's slots, the ones this page passes empty by NAME, and the
identity block it does not carry.** ⭐ Since `W388` it fills two more: the rail,
and its explanation in the aside slot.
"""

from __future__ import annotations

import pytest

from studyforge.render import templates
from studyforge.render.index import EMPTY_SLOTS, SKELETON, PageError, compose
from studyforge.render.index import document as page_document
from tests.studyforge.render.index.indexes import case, cases

#: The slots this page fills with something. ⛔ Stated here so the sum below is
#: an assertion about the skeleton rather than a restatement of the module.
FILLED_SLOTS = ("body", "heading", "outline", "rail", "script", "stylesheet", "title")


def test_the_skeleton_is_the_unit_pages_own_and_no_template_was_added():
    # ⭐ The rendering design asks this page to share the unit page's palette and type stack by
    # importing them rather than restating them; sharing the skeleton is that
    # ruling taken as far as it goes.
    assert SKELETON == "page.html"
    assert SKELETON in templates.names()


def test_every_slot_of_the_skeleton_is_either_filled_or_empty_by_name():
    # ⛔ `templates.fill` refuses a placeholder with no value AND a value with no
    # placeholder, so the day the skeleton gains or drops a slot this fails by
    # name instead of quietly losing a region.
    slots = templates.placeholders(SKELETON)
    assert set(EMPTY_SLOTS) | set(FILLED_SLOTS) == slots
    assert set(EMPTY_SLOTS) & set(FILLED_SLOTS) == set()
    assert len(EMPTY_SLOTS) + len(FILLED_SLOTS) == len(slots)


def test_the_empty_regions_are_exactly_empty_and_leave_no_stray_line():
    page = case("depth1").render().decode("utf-8")
    assert "\n\n" not in page
    assert page.endswith("</html>\n")
    assert page.count("</html>") == 1


def test_the_page_carries_the_corpus_own_title_in_both_places_it_appears():
    built = case("depth2")
    page = built.render().decode("utf-8")
    assert f"<title>{built.contents.title}</title>" in page
    assert f"<h1>{built.contents.title}</h1>" in page


def test_a_title_the_corpus_wrote_is_escaped_on_its_way_into_the_head():
    from studyforge.render.index import Document, Item, Placement, Section, render
    from tests.studyforge.render.index.indexes import placement_for

    document = Document(
        title="A & B <script>",
        levels=("module",),
        sections=(
            Section(
                level="module",
                key="a",
                title="A",
                items=(Item(key="a/unit-01", numbering="1", title="One"),),
            ),
        ),
    )
    page = render(document, placement_for("depth1")).decode("utf-8")
    assert "<title>A &amp; B &lt;script&gt;</title>" in page
    # ⚠️ Since `W388` stage 2 the skeleton carries a `<script>` of its own in
    # the head — the boot that applies the reader's theme before the first
    # paint — so the check is that the corpus's own one did not survive: the
    # only opening tag on the page is the boot's, and it is the skeleton's.
    assert page.count("<script>") == 1
    # ⚠️ Since `W388` stage 5 the boot reads `sessionStorage` and never
    # `localStorage`: binding the durable store in the `<head>` cost a reader
    # their marks, measured. The tell is the boot's own, whatever area it reads.
    assert "data-theme" in page.split("<script>")[1].split("</script>")[0]
    assert isinstance(placement_for("depth1"), Placement)


def test_the_masthead_has_no_second_line_and_that_is_a_decision():
    # ⚠️ A `meta` line would be this framework's sentence about a corpus, and
    # there is no corpus datum to put there the tree does not already say (R1).
    assert "meta" in EMPTY_SLOTS
    # ⚠️ Read inside the masthead: since `W362` the index's BODY opens with a
    # paragraph about the site, which is not a second line of the masthead.
    page = case("depth1").render().decode("utf-8")
    masthead = page.split("<header>", 1)[1].split("</header>", 1)[0]
    assert "<h1>" in masthead
    assert masthead.count("<p>") == 0


def test_a_skeleton_this_module_cannot_fill_raises_this_packages_own_error(monkeypatch):
    # ⛔ Re-typed, not re-worded: a caller rendering a whole site catches one
    # family for every kind of page.
    monkeypatch.setattr(page_document, "SKELETON", "section.html")
    with pytest.raises(PageError) as refused:
        compose(case("depth1").document, case("depth1").placement)
    assert "cannot be composed" in str(refused.value)


def test_composing_twice_gives_the_same_text(monkeypatch):
    for built in cases():
        assert compose(built.document, built.placement) == compose(built.document, built.placement)


def test_the_body_opens_with_what_the_site_is_then_progress_then_up_next():
    # ⭐ `W362`, the plan's §6: the reader's first need on the index is what this
    # is and where to pick up, before the tree. ⭐ `W388`: what the site is now
    # sits in the aside slot, just ahead of `main`, so a wide window puts it
    # beside the list — and the order in the document is unchanged.
    page = case("depth2").render().decode("utf-8")
    body = page.split("</header>", 1)[1]
    assert body.index('<section aria-label="About this site">') < body.index("<main")
    order = [
        body.index('<section aria-label="About this site">'),
        body.index('<section aria-label="Progress" hidden>'),
        body.index('<nav aria-label="Up next">'),
        body.index('<form role="search"'),
        body.index('<nav aria-label="Contents">'),
    ]
    assert order == sorted(order)


def test_the_index_does_not_guess_where_the_material_comes_from():
    # ⛔ The register's D5: that column is the corpus's fact and waits for
    # `W363`'s manifest data; the framework never invents it.
    page = case("depth1").render().decode("utf-8")
    assert "How to use it" in page and "How it is ordered" in page
    assert "Where it comes from" not in page


# --- the rail on the first page (`W388`) ---------------------------------------


def _two_containers():
    from studyforge.render.page import RailContainer, RailUnit

    return (
        RailContainer("First course", href="a.section.html", units=(RailUnit("One", href="u1"),)),
        RailContainer("Second course", href="b.section.html"),
    )


def test_the_first_page_carries_the_rail_it_is_handed():
    # ⛔ The user's words: "keep left menu even in the first page".
    built = case("depth2")
    page = compose(built.document, built.placement, _two_containers())
    assert '<nav aria-label="Containers">' in page
    assert page.index('<nav aria-label="Containers">') < page.index("<main")
    assert 'href="b.section.html"' in page


def test_a_first_page_handed_no_rail_carries_none():
    # ⭐ The other way: the region is the caller's to give, never invented here.
    built = case("depth2")
    assert '<nav aria-label="Containers">' not in compose(built.document, built.placement)
    assert '<nav aria-label="Containers">' not in compose(
        built.document, built.placement, _two_containers()[:1]
    )
