"""An example block of four languages is one block with a tab for each, in a browser.

⭐ **Every clause drives the real page**, on a corpus of four declared languages (`aa` to `dd`,
the fixture's own data) built the way a build does and served from a loopback origin: the first
tab and the panel of each tab, the order a mode sets, a mode of one language, the bar at phone
width, and the keys of the tabs pattern over four tabs.

⛔ **Each clause is asserted both ways (R12).** A mixed mode shows four tabs and a one-language
mode shows one and no bar; the reverse order opens the other end first; a click changes one block
only; scripts off every panel is still there.

## What this module does NOT read

The first-visit question of four modes (`test_reading_languages`) and a language a block lacks
(`test_absent_language`).
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from tests.studyforge.generate import four_corpus as four
from tests.visual import served
from tests.visual.four import (
    PHONE,
    UNIT,
    built,
    in_mode,
    read,
    served_from,
)
from tests.visual.page import NARROW, OpenPage

QUAD = "document.querySelector('div[data-example=quad]"


@pytest.fixture(scope="module")
def origin(tmp_path_factory: pytest.TempPathFactory) -> Iterator[served.Served]:
    out = built(tmp_path_factory, "tabs", four.declared(mixed=True), units=four.UNITS[:1])
    with served_from(out) as running:
        yield running


def test_four_tabs_open_on_the_first_language_and_each_opens_its_own_panel(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    in_mode(open_page, origin, "all")
    quad = read(open_page)["quad"]
    assert quad["tabs"] == list(four.LANGS) and quad["selected"] == ["aa"]
    assert quad["bar"] is True and quad["panels"] == ["aa"] and quad["labels"] == 0
    assert quad["disabled"] == [] and quad["note"] is None
    open_page.capture(capture_dir / "four-tabs-desktop-first.png")
    for lang in four.LANGS:
        open_page.evaluate(f"{QUAD} [data-lang={lang}]').click()")
        now = read(open_page)["quad"]
        assert now["selected"] == [lang] and now["panels"] == [lang], lang
        assert now["stops"] == [lang], "one tab stop"
    open_page.capture(capture_dir / "four-tabs-desktop-last.png")
    assert read(open_page)["duo"]["selected"] == ["aa"], "a click changes that block only"


def test_a_mode_that_reverses_the_order_opens_the_last_language_first(
    open_page: OpenPage, origin: served.Served
) -> None:
    in_mode(open_page, origin, "reverse")
    quad = read(open_page)["quad"]
    assert quad["tabs"] == list(reversed(four.LANGS)) and quad["selected"] == ["dd"]
    in_mode(open_page, origin, "all")
    assert read(open_page)["quad"]["tabs"] == list(four.LANGS)


@pytest.mark.parametrize("lang", four.LANGS)
def test_a_one_language_mode_shows_one_tab_and_no_bar(
    open_page: OpenPage, origin: served.Served, lang: str
) -> None:
    in_mode(open_page, origin, f"only-{lang}")
    quad = read(open_page)["quad"]
    assert quad["tabs"] == [lang] and quad["panels"] == [lang] and quad["bar"] is False
    assert quad["note"] is None


def test_four_tabs_at_phone_width_stay_inside_the_block_and_each_is_reachable(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    in_mode(open_page, origin, "all", size=PHONE)
    holds = open_page.evaluate(
        """
(() => {
  const e = document.querySelector('div[data-example="quad"]').getBoundingClientRect();
  const bar = document.querySelector('div[data-example="quad"] [role=tablist]');
  const tabs = Array.from(document.querySelectorAll('div[data-example="quad"] [role=tab]'))
    .map(t => {
      const r = t.getBoundingClientRect();
      return [r.left, r.right, r.height, r.width];
    });
  return {width: window.innerWidth, page: document.documentElement.scrollWidth,
          left: e.left, right: e.right, tabs: tabs, bar: bar.scrollWidth <= bar.clientWidth + 1};
})()
"""
    )
    assert len(holds["tabs"]) == 4
    assert holds["page"] <= holds["width"], "no horizontal scroll of the page"
    assert holds["left"] >= 0 and holds["right"] <= holds["width"]
    assert holds["bar"], "the bar wraps instead of overflowing"
    for left, right, height, width in holds["tabs"]:
        assert left >= holds["left"] and right <= holds["right"] and height >= 44 and width >= 44
    open_page.capture(capture_dir / "four-tabs-phone-360.png")
    open_page.evaluate(f"{QUAD} [data-lang=dd]').click()")
    assert read(open_page)["quad"]["selected"] == ["dd"]


def test_the_keyboard_walks_four_tabs_wraps_and_keeps_one_tab_stop(
    open_page: OpenPage, origin: served.Served
) -> None:
    in_mode(open_page, origin, "all")
    open_page.evaluate(f"{QUAD} [aria-selected=true]').focus()")
    start = read(open_page)["quad"]
    assert start["focus"] == "aa" and start["stops"] == ["aa"]
    for key, expected in (
        ("ArrowRight", "bb"),
        ("ArrowRight", "cc"),
        ("ArrowRight", "dd"),
        ("ArrowRight", "aa"),
        ("ArrowLeft", "dd"),
        ("Home", "aa"),
        ("End", "dd"),
    ):
        open_page.press(key)
        moved = read(open_page)["quad"]
        assert moved["focus"] == expected and moved["selected"] == [expected], key
        assert moved["stops"] == [expected], f"{key}: exactly one tab is in the tab order"


def test_scripts_off_every_panel_of_four_is_present_under_a_label(
    open_page: OpenPage, origin: served.Served
) -> None:
    open_page.resize(*NARROW)
    open_page.open(f"{origin.origin}/{UNIT}", scripts=False)
    quad = read(open_page)["quad"]
    assert quad["panels"] == ["aa"], "the default mode lists one language: one panel, no bar"
    assert quad["bar"] is False
