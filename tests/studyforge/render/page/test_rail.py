"""Mirror of `src/studyforge/render/page/rail.py` (R12).

⭐ **Every clause `W324` settles on is asserted BOTH WAYS here** — the region is
emitted and is not, a row is current and is not, a link is offered and is
dropped — because a rail that rendered nothing would satisfy half of them by
being absent.
"""

from __future__ import annotations

import re

import pytest

from studyforge.render.page import RailContainer, RailUnit, rail
from studyforge.render.pageassets import SURFACE_HOOKS

#: The region as a selector, exactly as `chrome.css` and the disposition table
#: spell it. ⛔ Read off the rendered markup rather than typed twice below.
LABEL = "Containers"

#: Two containers is the smallest corpus that has a crossing in it.
TWO = (
    RailContainer(
        title="Getting started",
        level="module",
        href="../basics/getting-started.section.html",
        current=True,
        units=(
            RailUnit(title="Your first class", numbering="1", current=True),
            RailUnit(title="Fields", numbering="2", href="unit-02.unit.html"),
        ),
    ),
    RailContainer(
        title="Going further",
        level="module",
        href="../advanced/going-further.section.html",
        units=(RailUnit(title="Composition", numbering="1", href="../advanced/unit-01.unit.html"),),
    ),
)


def hrefs(markup: str) -> list[str]:
    """Every anchor target the region offers, in document order."""
    return re.findall(r'<a href="([^"]*)"', markup)


def rows(markup: str) -> list[str]:
    """Every `<li ...>` opening tag, in document order."""
    return re.findall(r"<li[^>]*>", markup)


# --------------------------------------------------------------------------
# ⭐ Clause 4 — it degrades honestly for a corpus with ONE container
# --------------------------------------------------------------------------


def test_a_corpus_with_one_container_gets_no_rail_at_all():
    # ⛔ The clause: a rail listing one course is a list with no choice in it.
    assert rail((TWO[0],)) == ""


def test_no_containers_and_none_at_all_are_both_nothing():
    assert rail(()) == ""
    assert rail(None) == ""


def test_two_containers_DO_get_one_so_the_clause_above_is_not_emptiness():
    # ⛔ The other way round, and it is what stops the check above passing over a
    # renderer that emits nothing for every corpus.
    assert rail(TWO) != ""
    assert f'<nav aria-label="{LABEL}">' in rail(TWO)


# --------------------------------------------------------------------------
# ⭐ Clause 1 — the region reaches the OTHER containers, and their units
# --------------------------------------------------------------------------


def test_every_container_the_corpus_declares_has_a_row():
    markup = rail(TWO)
    for container in TWO:
        assert container.title in markup, container.title


def test_a_unit_of_another_container_is_linked_from_this_page():
    # ⛔ **The row's founding measurement inverted.** Before this region a unit
    # page carried three navs and not one href in any of them left its own
    # container; the crossing had to go back through the root index.
    found = hrefs(rail(TWO))
    assert "../advanced/unit-01.unit.html" in found, found
    assert "../advanced/going-further.section.html" in found, found


def test_the_container_page_and_every_unit_under_it_are_both_reachable():
    # ⭐ Both grains: a reader who wants the course lands on its page, a reader
    # who wants one lesson lands on the lesson.
    found = hrefs(rail(TWO))
    assert found.count("../advanced/going-further.section.html") == 1
    assert found.count("../advanced/unit-01.unit.html") == 1


# --------------------------------------------------------------------------
# ⭐ Clause 2 — it says where the reader is, in the markup
# --------------------------------------------------------------------------


def test_the_current_container_is_marked_current_and_the_others_are_not():
    markup = rail(TWO)
    current = [row for row in rows(markup) if 'aria-current="true"' in row]
    assert len(current) == 1, rows(markup)
    assert markup.index('aria-current="true"') < markup.index("Getting started")


def test_the_current_unit_is_marked_as_the_page_and_is_never_a_link():
    markup = rail(TWO)
    assert markup.count('aria-current="page"') == 1
    # ⛔ A page that links to itself is a way to get nowhere — the trail refuses
    # the same link for the same reason.
    assert "Your first class" in markup
    assert not [href for href in hrefs(markup) if "unit-01" in href and "advanced" not in href]


def test_a_rail_with_no_current_anything_marks_nothing():
    # ⛔ The other way: `current` is a fact a caller states, never one this
    # module infers from a position.
    plain = tuple(
        RailContainer(
            title=container.title,
            level=container.level,
            href=container.href,
            units=tuple(
                RailUnit(title=unit.title, numbering=unit.numbering, href=unit.href or "x.html")
                for unit in container.units
            ),
        )
        for container in TWO
    )
    assert "aria-current" not in rail(plain)


def test_the_current_container_opens_and_the_others_stay_closed():
    # ⚠️ Structure, not styling: `open` is what makes the reader's own course
    # visible on arrival, and the others one keystroke away.
    # ⚠️ Read inside the fold (`W362`): `rail.html` wraps the whole list in one
    # `<details open>` that the page script closes on a narrow screen, and that
    # outer one is not a container.
    markup = rail(TWO).split("<summary>Course contents</summary>", 1)[1]
    assert markup.count("<details open>") == 1
    assert markup.count("<details>") == len(TWO) - 1


# --------------------------------------------------------------------------
# ⭐ Clause 3 — it needs no script, and it needs no stylesheet either
# --------------------------------------------------------------------------


def test_the_region_carries_no_script_and_no_event_attribute():
    # ⛔ R8's floor is a double-clicked file. A rail whose links were revealed by
    # a handler would make the crossing depend on the one thing the floor lacks.
    markup = rail(TWO)
    assert "<script" not in markup
    assert not re.search(r"\son[a-z]+=", markup)


def test_the_disclosure_is_a_real_details_element():
    # ⭐ `<details>` opens, closes and takes keyboard focus with scripting off
    # entirely; a `div` with a handler does none of those things.
    markup = rail(TWO)
    assert "<details" in markup and "<summary>" in markup


def test_every_row_is_a_list_item_inside_the_regions_own_lists():
    markup = rail(TWO)
    assert markup.count("<li") == markup.count("</li>")
    assert markup.count("<ol>") == markup.count("</ol>")


# --------------------------------------------------------------------------
# ⭐ Ruling 164 here — a refused href drops the LINK and keeps the ROW
# --------------------------------------------------------------------------


@pytest.mark.parametrize("refused", ["javascript:alert(1)", "/rooted.html"])
def test_a_refused_href_loses_its_anchor_and_keeps_its_row(refused):
    # ⛔ A container dropped out of this list is a true statement about a
    # different corpus: the reader counts the courses and finds one fewer.
    markup = rail((RailContainer(title="Kept", href=refused), TWO[1]))
    assert "Kept" in markup
    assert refused not in markup
    assert f'{SURFACE_HOOKS["readable"]}="false"' in markup


def test_a_permitted_href_is_linked_so_the_refusal_above_is_not_the_rule():
    markup = rail((RailContainer(title="Kept", href="kept.section.html"), TWO[1]))
    assert "kept.section.html" in hrefs(markup)


def test_a_unit_with_no_page_on_this_machine_is_listed_and_not_linked():
    # ⚠️ §7's third state: declared, and not present. It is listed rather than
    # dropped and rather than pointing at a page nobody wrote.
    markup = rail(
        (
            RailContainer(
                title="Here",
                href="here.section.html",
                units=(RailUnit(title="Not built", numbering="1"),),
            ),
            TWO[1],
        )
    )
    assert "Not built" in markup
    assert f'{SURFACE_HOOKS["readable"]}="false"' in markup


def test_the_current_row_is_readable_even_though_it_carries_no_anchor():
    # ⛔ It is the most readable row on the page. Marking it "listed, not
    # openable" would be a false sentence rendered in italics.
    markup = rail(TWO)
    current = [row for row in rows(markup) if "aria-current" in row]
    assert current, rows(markup)
    for row in current:
        assert f'{SURFACE_HOOKS["readable"]}="true"' in row, row


# --------------------------------------------------------------------------
# ⭐ What this region must NOT do
# --------------------------------------------------------------------------


def test_the_rail_emits_no_id_so_a_container_pages_own_listing_keeps_its_keys():
    # ⛔ `read-mark.js` resolves a mark with `document.getElementById(key)`, and a
    # container page carries `id="<unit key>"` on every row of its own listing.
    # A rail that keyed its rows the same way would put two elements under one id.
    assert "id=" not in rail(TWO)


# --------------------------------------------------------------------------
# ⭐ `W368` — a unit row carries the key a read mark is stored under
# --------------------------------------------------------------------------

KEYED = (
    RailContainer(
        title="Getting started",
        href="a.section.html",
        units=(
            RailUnit(title="Your first class", key="basics/unit-01", current=True),
            RailUnit(title="Fields", href="u2.unit.html", key="basics/unit-02"),
        ),
    ),
    RailContainer(title="Going further", href="b.section.html"),
)


def test_a_unit_row_handed_a_key_carries_it_in_the_attribute_the_script_reads():
    markup = rail(KEYED)
    assert re.findall(r'data-unit="([^"]*)"', markup) == ["basics/unit-01", "basics/unit-02"]


def test_a_unit_row_handed_no_key_carries_none_so_the_rows_above_are_not_the_default():
    # ⛔ The other way round: `TWO` hands no key, and a key the rail made up
    # (from an href, a title, a position) would be a mark on the wrong unit.
    assert "data-unit" not in rail(TWO)


def test_a_container_row_never_carries_a_unit_key():
    # ⭐ Document order is container, its two units, the second container.
    keyed = [at for at, row in enumerate(rows(rail(KEYED))) if "data-unit" in row]
    assert keyed == [1, 2]


def test_a_key_is_escaped_as_an_attribute_value():
    hostile = (
        RailContainer(title="A", href="a.html", units=(RailUnit(title="U", key='a"b<c'),)),
        TWO[1],
    )
    markup = rail(hostile)
    assert 'data-unit="a&quot;b&lt;c"' in markup
    assert 'a"b' not in markup


def test_a_keyed_rail_still_emits_no_id():
    assert "id=" not in rail(KEYED).replace("data-unit=", "")


def test_a_title_carrying_markup_is_escaped_rather_than_emitted():
    markup = rail((RailContainer(title="<b>bold</b>", href="a.html"), TWO[1]))
    assert "<b>bold</b>" not in markup
    assert "&lt;b&gt;" in markup


def test_the_corpus_own_word_for_a_depth_is_carried_and_never_this_frameworks():
    # ⛔ R1: `level` is `manifest.levels[-1]`, and the rail says whatever it says.
    markup = rail(
        (RailContainer(title="A", level="chapter", href="a.html"), RailContainer(title="B"))
    )
    assert f'{SURFACE_HOOKS["kind"]}="{SURFACE_HOOKS["level"]}">chapter<' in markup


def test_a_container_that_names_no_level_gets_no_chip_and_no_stray_space():
    markup = rail((RailContainer(title="A", href="a.html"), RailContainer(title="B")))
    assert f'{SURFACE_HOOKS["level"]}"' not in markup
    assert '<summary><a href="a.html">A</a></summary>' in markup


def test_a_unit_that_numbers_nothing_gets_no_chip_either():
    markup = rail(
        (
            RailContainer(title="A", href="a.html", units=(RailUnit(title="U", href="u.html"),)),
            RailContainer(title="B"),
        )
    )
    assert f'{SURFACE_HOOKS["numbering"]}"' not in markup
    assert '<a href="u.html">U</a>' in markup


def test_the_same_rail_renders_to_the_same_bytes_every_time():
    # ⛔ R10: no clock, no set iteration, no filesystem.
    assert rail(TWO) == rail(TWO)


def test_a_container_declaring_no_units_yet_is_still_a_row():
    # ⚠️ An empty deepest group is legal and is not the same as an absent one.
    markup = rail((RailContainer(title="Empty", href="e.html"), TWO[1]))
    assert "Empty" in markup
