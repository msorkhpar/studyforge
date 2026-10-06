"""A language a block or a practice lacks is greyed, with the languages that carry it, in a browser.

⭐ **Every clause drives the real page**, on a corpus of four languages whose manifest says
`absent_language: grey`: a block that lacks a listed language shows that tab disabled and a
sentence naming the carriers, the keys reach a disabled tab without selecting it, an entry in two
of four languages is greyed with both named, and a practice card outside the mode is greyed,
does not open, and is stepped over by the workspace.

⛔ **Each clause is asserted both ways (R12).** A disabled tab selects nothing and an enabled one
does; a card outside the mode does not open and one inside does; the sentence is there for a block
that lacks a listed language and absent for one that has them all; a greyed block is never hidden.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from tests.studyforge.generate import four_corpus as four
from tests.visual import served
from tests.visual.four import (
    CARDS,
    PHONE,
    UNIT,
    WORKSPACE,
    built,
    choose,
    greyed,
    in_mode,
    read,
    served_from,
)
from tests.visual.page import NARROW, OpenPage

DUO = "document.querySelector('div[data-example=duo]"


@pytest.fixture(scope="module")
def origin(tmp_path_factory: pytest.TempPathFactory) -> Iterator[served.Served]:
    out = built(tmp_path_factory, "grey", four.declared(absent="grey", mixed=True), code=True)
    with served_from(out) as running:
        yield running


# --- a language a block lacks, greyed, with the languages that carry it ------------------------


def workspace(page: OpenPage) -> dict:
    """What the practice workspace shows: whether it is open, its address, its two ends."""
    return page.evaluate(WORKSPACE)  # type: ignore[return-value]


def test_a_block_that_lacks_listed_languages_shows_them_disabled_and_names_its_carriers(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    in_mode(open_page, origin, "all")
    duo = read(open_page)["duo"]
    assert duo["tabs"] == list(four.LANGS) and duo["disabled"] == ["cc", "dd"]
    assert duo["selected"] == ["aa"] and duo["panels"] == ["aa"] and duo["bar"] is True
    assert duo["note"] == "Available in: Aa, Bb."
    quad = read(open_page)["quad"]
    assert quad["note"] is None and quad["disabled"] == []
    open_page.capture(capture_dir / "greyed-tabs-desktop.png")
    open_page.evaluate(f"{DUO} [data-lang=cc]').click()")
    after = read(open_page)["duo"]
    assert after["selected"] == ["aa"] and after["panels"] == ["aa"], "a disabled tab selects none"
    open_page.evaluate(f"{DUO} [data-lang=bb]').click()")
    assert read(open_page)["duo"]["selected"] == ["bb"], "an enabled one does"
    described = open_page.evaluate(
        """
(() => {
  const t = document.querySelector('div[data-example=duo] [data-lang=cc]');
  const n = document.getElementById(t.getAttribute('aria-describedby'));
  return {note: n && n.textContent, controls: t.hasAttribute('aria-controls'),
          role: t.getAttribute('role')};
})()
"""
    )
    assert described == {"note": "Available in: Aa, Bb.", "controls": False, "role": "tab"}


def test_a_disabled_tab_stays_focusable_and_the_keys_reach_it_without_selecting_it(
    open_page: OpenPage, origin: served.Served
) -> None:
    in_mode(open_page, origin, "all")
    open_page.evaluate(f"{DUO} [aria-selected=true]').focus()")
    for key, focus, selected in (
        ("ArrowRight", "bb", "bb"),
        ("ArrowRight", "cc", "bb"),
        ("ArrowRight", "dd", "bb"),
        ("ArrowRight", "aa", "aa"),
        ("ArrowLeft", "dd", "aa"),
        ("Home", "aa", "aa"),
        ("End", "dd", "aa"),
    ):
        open_page.press(key)
        moved = read(open_page)["duo"]
        assert moved["focus"] == focus, key
        assert moved["selected"] == [selected], key
        assert moved["stops"] == [focus], f"{key}: one tab stop, on the focused tab"
    open_page.press("Enter")
    assert read(open_page)["duo"]["selected"] == ["aa"], "Enter on a disabled tab does nothing"


@pytest.mark.parametrize(
    ("mode", "disabled", "note"),
    [
        ("only-aa", ["aa"], "Available in: Cc."),
        ("only-bb", ["bb"], "Available in: Cc."),
        ("only-dd", ["dd"], "Available in: Cc."),
        ("only-cc", [], None),
    ],
)
def test_a_one_language_mode_that_the_block_lacks_still_shows_the_block_greyed_with_the_sentence(
    open_page: OpenPage,
    origin: served.Served,
    capture_dir: Path,
    mode: str,
    disabled: list[str],
    note: str | None,
) -> None:
    in_mode(open_page, origin, mode)
    solo = read(open_page)["solo"]
    assert solo["shown"] is True, "greyed, never hidden"
    assert solo["disabled"] == disabled and solo["note"] == note
    if disabled:
        assert solo["tabs"] == disabled and solo["bar"] is True and solo["panels"] == []
        assert solo["selected"] == [] and solo["stops"] == disabled
    else:
        assert solo["tabs"] == ["cc"] and solo["panels"] == ["cc"] and solo["bar"] is False
    open_page.capture(capture_dir / f"greyed-solo-{mode}.png")


def test_greyed_tabs_hold_at_phone_width(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    in_mode(open_page, origin, "all", size=PHONE)
    holds = open_page.evaluate(
        """
(() => {
  const e = document.querySelector('div[data-example="duo"]').getBoundingClientRect();
  const tabs = Array.from(document.querySelectorAll('div[data-example="duo"] [role=tab]'))
    .map(t => { const r = t.getBoundingClientRect(); return [r.left, r.right, r.height]; });
  const note = document.querySelector('div[data-example="duo"] [data-example-missing]')
    .getBoundingClientRect();
  return {width: window.innerWidth, page: document.documentElement.scrollWidth,
          left: e.left, right: e.right, tabs: tabs, note: [note.left, note.right]};
})()
"""
    )
    assert holds["page"] <= holds["width"] and len(holds["tabs"]) == 4
    for left, right, height in holds["tabs"]:
        assert left >= holds["left"] and right <= holds["right"] and height >= 44
    assert holds["note"][0] >= holds["left"] and holds["note"][1] <= holds["right"]
    open_page.capture(capture_dir / "greyed-tabs-phone-360.png")


def test_scripts_off_the_default_modes_block_names_its_carriers_and_a_full_block_names_none(
    open_page: OpenPage, origin: served.Served
) -> None:
    open_page.resize(*NARROW)
    open_page.open(f"{origin.origin}/{UNIT}", scripts=False)
    state = read(open_page)
    assert state["solo"]["note"] == "Available in: Cc." and state["solo"]["panels"] == []
    assert state["duo"]["note"] is None and state["duo"]["panels"] == ["aa"]
    assert state["quad"]["note"] is None


# --- an entry or a practice in some languages only, greyed -----------------------------------


ROWS = """
Array.from(document.querySelectorAll('nav[aria-label="Contents"] li[id]')).map(li => {
  const label = li.querySelector('[data-entry-label]');
  return {id: li.id, lang: li.getAttribute('data-entry-lang'),
          label: label && getComputedStyle(label).display !== 'none' ? label.textContent : null,
          shown: li.offsetHeight > 0, grey: getComputedStyle(li.querySelector('a')).color};
})
"""


@pytest.mark.parametrize(
    ("mode", "greyed"),
    [
        ("only-aa", {"demo/unit-04": "Cc, Dd"}),
        ("only-bb", {"demo/unit-04": "Cc, Dd"}),
        ("only-cc", {"demo/unit-03": "Aa, Bb"}),
        ("only-dd", {"demo/unit-03": "Aa, Bb"}),
    ],
)
def test_an_entry_in_two_of_four_languages_is_greyed_with_both_named_where_it_is_not_read(
    open_page: OpenPage, origin: served.Served, mode: str, greyed: dict[str, str]
) -> None:
    in_mode(open_page, origin, mode, "index.html")
    rows = {row["id"]: row for row in open_page.evaluate(ROWS)}  # type: ignore[union-attr]
    assert rows["demo/unit-01"]["lang"] is None
    assert rows["demo/unit-03"]["lang"] == "aa bb" and rows["demo/unit-04"]["lang"] == "cc dd"
    for ident, row in rows.items():
        assert row["shown"], f"{ident} is never hidden"
        assert row["label"] == greyed.get(ident), ident
    plain = rows["demo/unit-01"]["grey"]
    assert all(rows[ident]["grey"] != plain for ident in greyed)
    assert all(row["grey"] == plain for ident, row in rows.items() if ident not in greyed)


@pytest.mark.parametrize(
    ("mode", "greyed"),
    [
        ("only-aa", [False, True, False, True]),
        ("only-bb", [False, True, False, True]),
        ("only-cc", [True, False, False, True]),
        ("only-dd", [True, True, False, False]),
    ],
)
def test_a_practice_outside_the_modes_language_is_greyed_and_names_the_languages_that_carry_it(
    open_page: OpenPage,
    origin: served.Served,
    capture_dir: Path,
    mode: str,
    greyed: list[bool],
) -> None:
    in_mode(open_page, origin, mode, four.PAGES[5])
    cards = open_page.evaluate(CARDS)
    assert [card["greyed"] for card in cards] == greyed  # type: ignore[union-attr]
    plain = next(card["color"] for card in cards if not card["greyed"])  # type: ignore[union-attr]
    for card in cards:  # type: ignore[union-attr]
        assert (card["color"] != plain) is card["greyed"]
        assert (card["disabled"] == "true") is card["greyed"]
    if mode == "only-cc":
        assert cards[0]["note"] == "Available in: Aa, Bb."  # type: ignore[index]
    open_page.capture(capture_dir / f"greyed-practices-{mode}.png")


def test_a_greyed_practice_does_not_open_and_the_workspace_steps_over_it(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    in_mode(open_page, origin, "only-aa", four.PAGES[5])
    link = 'li[data-practice-card="%s"] a[data-practices-part=open]'
    open_page.evaluate(f"document.querySelector('{link % 's-practice-prose-2'}').click()")
    assert not workspace(open_page)["open"], "a greyed card does not open"
    open_page.evaluate(f"document.querySelector('{link % 's-practice-prose'}').click()")
    first = workspace(open_page)
    assert first["open"] is True and first["hash"] == "#s-practice-prose"
    assert first["previous"] is False and first["next"] is True
    open_page.capture(capture_dir / "greyed-practices-workspace-first.png")
    open_page.evaluate("document.querySelector('[data-workspace-act=next]').click()")
    second = workspace(open_page)
    assert second["hash"] == "#s-practice-prose-3", "Next passes over the greyed one"
    assert second["next"] is False and second["previous"] is True
    open_page.evaluate("document.querySelector('[data-workspace-act=previous]').click()")
    assert workspace(open_page)["hash"] == "#s-practice-prose"
    open_page.evaluate("document.querySelector('[data-workspace-act=close]').click()")
    assert not workspace(open_page)["open"]


def test_a_mode_change_greys_and_ungreys_the_cards_in_place(
    open_page: OpenPage, origin: served.Served
) -> None:
    in_mode(open_page, origin, "only-aa", four.PAGES[5])
    assert greyed(open_page) == [False, True, False, True]
    choose(open_page, "only-cc")
    assert greyed(open_page) == [True, False, False, True]
    choose(open_page, "all")
    assert greyed(open_page) == [False, False, False, False]
    open_page.evaluate(
        "document.querySelector('li[data-practice-card=\"s-practice-prose-2\"] a').click()"
    )
    assert workspace(open_page)["open"] is True


def test_a_practice_the_mode_lists_reads_in_its_own_language_whatever_the_modes_prose(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    in_mode(open_page, origin, "all", four.PAGES[5])
    open_page.evaluate(
        "document.querySelector('li[data-practice-card=\"s-practice-prose-2\"] a').click()"
    )
    seen = open_page.evaluate(
        """
(() => {
  const shown = id => { const e = document.getElementById(id);
    return !e.hidden && getComputedStyle(e).display !== 'none' && e.offsetHeight > 0; };
  return {section: shown('s-practice-prose-2'), other: shown('s-practice-prose'),
          panel: !!document.querySelector(
            'section[data-practice$="practice-prose-2"][data-workspace-open]')};
})()
"""
    )
    assert seen == {"section": True, "other": False, "panel": True}
    open_page.capture(capture_dir / "greyed-practices-listed-in-another-language.png")
    open_page.evaluate("document.querySelector('[data-workspace-act=close]').click()")
    shut = open_page.evaluate(
        "Array.from(document.querySelectorAll('main section[data-kind=practice]'))"
        ".filter(e => e.offsetHeight > 0).length"
    )
    assert shut == 0, "a closed practice stays closed in a mode that lists its language"


def test_scripts_off_a_practice_outside_the_default_mode_shows_neither_statement_nor_panel(
    open_page: OpenPage, origin: served.Served
) -> None:
    open_page.resize(*NARROW)
    open_page.open(f"{origin.origin}/{four.PAGES[5]}", scripts=False)
    visible = open_page.evaluate(
        "Array.from(document.querySelectorAll("
        "'main section[data-kind=practice], section[data-practice]'))"
        ".filter(e => getComputedStyle(e).display !== 'none')"
        ".map(e => e.getAttribute('data-lang'))"
    )
    assert visible == ["aa bb", "aa bb", "aa bb cc dd", "aa bb cc dd"]
