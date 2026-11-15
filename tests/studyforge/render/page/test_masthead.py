"""Mirror of `src/studyforge/render/page/masthead.py` (R12)."""

from __future__ import annotations

from studyforge.render.page.masthead import (
    CURRENT,
    SECTION_LIMIT,
    SELF,
    Masthead,
    brand,
    sections,
    top_level,
)
from studyforge.render.page.rail import RailContainer, RailGroup, RailUnit

BACKEND = RailGroup("Backend", key="backend")
FRONTEND = RailGroup("Frontend", key="frontend")

RAIL = (
    RailContainer("APIs", href="backend/apis.section.html", within=(BACKEND,)),
    RailContainer(
        "Storage",
        href="backend/storage.section.html",
        within=(BACKEND,),
        units=(RailUnit("Indexes", href="u.html", current=True),),
    ),
    RailContainer("Layout", href="frontend/layout.section.html", within=(FRONTEND,)),
)


def test_no_masthead_keeps_the_old_bar():
    assert brand(None) == ""
    assert sections(None) == ""


def test_the_brand_links_home_and_escapes_the_title():
    made = brand(Masthead("Graphs & <you>", "../index.html"))
    assert made == '<a href="../index.html" data-section="brand">Graphs &amp; &lt;you&gt;</a>'


def test_a_brand_with_no_title_is_not_drawn():
    assert brand(Masthead("", "index.html")) == ""


def test_a_brand_with_no_usable_home_links_to_the_content():
    assert f'href="{SELF}"' in brand(Masthead("Course", ""))


def test_a_group_is_one_entry_linked_to_its_first_page_and_marked_when_it_holds_this_page():
    assert top_level(RAIL) == (
        ("Backend", "backend/apis.section.html", True),
        ("Frontend", "frontend/layout.section.html", False),
    )


def test_the_sections_list_each_entry_and_mark_the_current_one():
    made = sections(Masthead("Course", "index.html", RAIL))
    assert made.startswith('<nav aria-label="Course sections" data-section="sections">')
    assert f'<li><a href="backend/apis.section.html"{CURRENT}>Backend</a></li>' in made
    assert '<li><a href="frontend/layout.section.html">Frontend</a></li>' in made


def test_one_section_is_not_worth_a_bar():
    assert sections(Masthead("Course", "index.html", RAIL[:2])) == ""


def test_more_sections_than_the_bar_holds_names_none():
    rail = tuple(
        RailContainer(f"Part {n}", href=f"p{n}.section.html") for n in range(SECTION_LIMIT + 1)
    )
    assert sections(Masthead("Course", "index.html", rail)) == ""
    assert sections(Masthead("Course", "index.html", rail[:SECTION_LIMIT])) != ""


def test_a_top_level_container_without_a_page_is_left_out_unless_it_is_this_page():
    rail = (
        RailContainer("Nowhere"),
        RailContainer("Here", current=True),
        RailContainer("There", href="there.section.html"),
    )
    assert top_level(rail) == (("Here", SELF, True), ("There", "there.section.html", False))
