"""A two-language example is one block with a tab per language, following the reading mode.

⭐ **Every clause drives the real page in the headless browser**, with a corpus of two
languages and four modes: the reader's first tab, which tabs exist, what a block that is
a compiler message looks like, that code draws no ligature, that a phone's width holds,
and that the keyboard and the roles are the WAI-ARIA tabs pattern.

⛔ **Each clause is asserted both ways (R12).** A mixed mode shows both tabs and opens the
mode's first language; a one-language mode shows its own tab only and hides an example with
nothing in it; scripts off still holds every panel under a label.

## What this module does NOT read

The index, the rail and the practice list of a mode; they are other rows' clauses.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from tests.studyforge.generate.test_section_language import build
from tests.studyforge.validate.test_languages import READING, document
from tests.visual import served, site
from tests.visual.page import NARROW, WIDE, OpenPage

MODES = [
    {
        "id": "only-aa",
        "label": "Aa",
        "summary": "Aa only",
        "prose": "aa",
        "tabs": ["aa"],
        "practices": ["aa"],
    },
    {
        "id": "only-bb",
        "label": "Bb",
        "summary": "Bb only",
        "prose": "bb",
        "tabs": ["bb"],
        "practices": ["bb"],
    },
    {
        "id": "both",
        "label": "Aa with Bb",
        "summary": "Aa first",
        "prose": "aa",
        "tabs": ["aa", "bb"],
        "practices": ["aa", "bb"],
    },
    {
        "id": "swap",
        "label": "Bb with Aa",
        "summary": "Bb first",
        "prose": "bb",
        "tabs": ["bb", "aa"],
        "practices": ["bb", "aa"],
    },
]
DECLARED = {**READING, "modes": MODES, "default_mode": "both"}


def fence(lang: str, text: str) -> dict:
    return {"type": "code", "lang": lang, "text": text}


BLOCKS = [
    {"type": "para", "text": "Common words."},
    {
        "type": "example",
        "id": "pair",
        "tabs": [{"lang": "aa", "span": 2}, {"lang": "bb", "span": 2}],
        "blocks": [
            fence("aa", "if (a != b) go() -> done"),
            fence("text", "aa printed"),
            fence("bb", "if b != a then go -> done"),
            fence("text", "bb printed"),
        ],
    },
    {
        "type": "example",
        "id": "aa-error",
        "output": "compiler",
        "tabs": [{"lang": "aa", "span": 2}],
        "blocks": [fence("aa", "val x: Int = null"), fence("text", "error: null cannot be Int")],
    },
    {
        "type": "example",
        "id": "bb-warning",
        "output": "warning",
        "tabs": [{"lang": "bb", "span": 2}],
        "blocks": [fence("bb", "var unused = 1"), fence("text", "warning: unused")],
    },
]
UNIT = ".studyforge/demo/units/unit-01/unit-01-unit-1.unit.html"
SWITCH = '[data-section="mode"]'

#: One reading of every example: its tabs, which is open, and which panels show.
STATE = """
Array.from(document.querySelectorAll('div[data-example]')).map(e => {
  const shown = el => getComputedStyle(el).display !== 'none';
  const tabs = Array.from(e.querySelectorAll('[role="tab"]')).filter(shown);
  const bar = e.querySelector('[role="tablist"]');
  return {
    id: e.getAttribute('data-example'),
    shown: shown(e),
    tabs: tabs.map(t => t.getAttribute('data-lang')),
    selected: tabs.filter(t => t.getAttribute('aria-selected') === 'true')
      .map(t => t.getAttribute('data-lang')),
    bar: !!bar && shown(bar),
    panels: Array.from(e.querySelectorAll('[role="tabpanel"]')).filter(shown)
      .map(p => p.getAttribute('data-lang')),
    labels: Array.from(e.querySelectorAll('[data-example-label]')).filter(shown).length
  };
})
"""
CLEAR = "(() => { try { localStorage.clear(); sessionStorage.clear(); } catch (e) {} })()"


@pytest.fixture(scope="module")
def modal(tmp_path_factory: pytest.TempPathFactory) -> Path:
    documents = [document(ordinal=1, blocks=BLOCKS)]
    return build(tmp_path_factory.mktemp("example-site"), "m", documents, DECLARED)


@pytest.fixture(scope="module")
def origin(modal: Path) -> Iterator[served.Served]:
    with served.serving(site.Site(modal.parent), corpus=modal.name) as running:
        yield running


def read(page: OpenPage) -> dict:
    return {state["id"]: state for state in page.evaluate(STATE)}  # type: ignore[union-attr]


def in_mode(page: OpenPage, origin: served.Served, mode: str, size=WIDE) -> dict:
    page.resize(*size)
    page.open(f"{origin.origin}/{UNIT}")
    page.evaluate(CLEAR)
    page.open(f"{origin.origin}/{UNIT}")
    page.evaluate(f"document.querySelector('{SWITCH} [data-mode-choice=\"{mode}\"]').click()")
    return read(page)


def test_a_mixed_mode_offers_both_tabs_and_opens_the_first_languages(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    state = in_mode(open_page, origin, "both")
    pair = state["pair"]
    assert pair["tabs"] == ["aa", "bb"] and pair["selected"] == ["aa"]
    assert pair["bar"] is True and pair["panels"] == ["aa"] and pair["labels"] == 0
    open_page.capture(capture_dir / "example-mixed-first-tab.png")
    open_page.evaluate("document.querySelector('[role=tab][data-lang=bb]').click()")
    after = read(open_page)
    assert after["pair"]["selected"] == ["bb"] and after["pair"]["panels"] == ["bb"]
    open_page.capture(capture_dir / "example-mixed-second-tab.png")
    assert after["aa-error"] == state["aa-error"], "a click changes that block only"


def test_the_modes_order_decides_which_language_opens_first(
    open_page: OpenPage, origin: served.Served
) -> None:
    pair = in_mode(open_page, origin, "swap")["pair"]
    assert pair["tabs"] == ["bb", "aa"] and pair["selected"] == ["bb"]
    again = in_mode(open_page, origin, "both")["pair"]
    assert again["tabs"] == ["aa", "bb"] and again["selected"] == ["aa"]


def test_a_click_is_not_remembered_the_mode_is(open_page: OpenPage, origin: served.Served) -> None:
    in_mode(open_page, origin, "both")
    open_page.evaluate("document.querySelector('[role=tab][data-lang=bb]').click()")
    open_page.open(f"{origin.origin}/{UNIT}")
    assert read(open_page)["pair"]["selected"] == ["aa"]


@pytest.mark.parametrize(
    ("mode", "language", "hidden"),
    [("only-aa", "aa", "bb-warning"), ("only-bb", "bb", "aa-error")],
)
def test_a_one_language_mode_shows_its_own_tab_only_and_hides_an_example_with_nothing_in_it(
    open_page: OpenPage,
    origin: served.Served,
    capture_dir: Path,
    mode: str,
    language: str,
    hidden: str,
) -> None:
    state = in_mode(open_page, origin, mode)
    assert state["pair"]["tabs"] == [language] and state["pair"]["panels"] == [language]
    assert state["pair"]["bar"] is False
    assert state[hidden]["shown"] is False
    shown = [name for name, one in state.items() if one["shown"]]
    assert hidden not in shown and "pair" in shown and len(shown) == 2
    open_page.capture(capture_dir / f"example-{mode}.png")


def test_a_compiler_message_and_a_warning_are_flagged_and_bordered_apart_from_the_rest(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    in_mode(open_page, origin, "both")
    seen = open_page.evaluate(
        """
(() => {
  const read = id => {
    const e = document.querySelector('div[data-example="' + id + '"]');
    const flag = e.querySelector('[data-example-flag]');
    const s = getComputedStyle(e);
    return {style: s.borderTopStyle, width: s.borderTopWidth, color: s.borderTopColor,
            flag: flag ? flag.textContent : null,
            flagShown: flag ? getComputedStyle(flag).display !== 'none' : false};
  };
  return {plain: read('pair'), error: read('aa-error'), warning: read('bb-warning')};
})()
"""
    )
    assert seen["error"]["flag"] == "Does not compile, on purpose" and seen["error"]["flagShown"]
    assert seen["warning"]["flag"] == "Compiles with a warning, on purpose"
    assert seen["plain"]["flag"] is None
    plain, error, warning = (seen[k] for k in ("plain", "error", "warning"))
    assert (error["style"], error["width"]) != (plain["style"], plain["width"])
    assert error["color"] != plain["color"]
    assert warning["style"] == "dashed" and error["style"] == "solid"
    open_page.capture(capture_dir / "example-compiler-error-and-warning.png")


def test_code_draws_no_ligature(open_page: OpenPage, origin: served.Served) -> None:
    in_mode(open_page, origin, "both")
    drawn = open_page.evaluate(
        """
(() => {
  const c = document.querySelector('div[data-example="pair"] [role=tabpanel] code');
  const s = getComputedStyle(c);
  return {ligatures: s.fontVariantLigatures, features: s.fontFeatureSettings,
          text: c.textContent};
})()
"""
    )
    assert "!=" in drawn["text"] and "->" in drawn["text"]
    assert drawn["ligatures"] == "none" and '"liga" 0' in drawn["features"]


def test_a_phone_width_holds_the_block_and_its_tabs(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    in_mode(open_page, origin, "both", size=(360, 740))
    holds = open_page.evaluate(
        """
(() => {
  const e = document.querySelector('div[data-example="pair"]').getBoundingClientRect();
  const tabs = Array.from(document.querySelectorAll('div[data-example="pair"] [role=tab]'))
    .map(t => {
      const r = t.getBoundingClientRect();
      return [r.left, r.right, r.height, r.width];
    });
  return {width: window.innerWidth, page: document.documentElement.scrollWidth,
          left: e.left, right: e.right, tabs: tabs};
})()
"""
    )
    assert holds["page"] <= holds["width"], "no horizontal scroll of the page"
    assert holds["left"] >= 0 and holds["right"] <= holds["width"]
    for left, right, height, width in holds["tabs"]:
        assert left >= 0 and right <= holds["width"] and height >= 44 and width >= 44
    open_page.capture(capture_dir / "example-phone-360.png")


def test_the_keyboard_moves_between_tabs_with_roving_tabindex_and_wraps(
    open_page: OpenPage, origin: served.Served
) -> None:
    in_mode(open_page, origin, "both")
    probe = """
(() => {
  const e = document.querySelector('div[data-example="pair"]');
  const tabs = Array.from(e.querySelectorAll('[role=tab]'));
  const on = document.activeElement;
  return {focus: on && on.getAttribute && on.getAttribute('data-lang'),
          role: on && on.getAttribute && on.getAttribute('role'),
          selected: tabs.filter(t => t.getAttribute('aria-selected') === 'true')
            .map(t => t.getAttribute('data-lang')),
          indexes: tabs.map(t => t.getAttribute('tabindex')),
          list: e.querySelector('[role=tablist]').getAttribute('aria-label'),
          controls: tabs.map(t => !!document.getElementById(t.getAttribute('aria-controls'))),
          labelled: Array.from(e.querySelectorAll('[role=tabpanel]'))
            .map(p => document.getElementById(p.getAttribute('aria-labelledby')) !== null),
          panelFocusable: Array.from(e.querySelectorAll('[role=tabpanel]'))
            .map(p => p.tabIndex)};
})()
"""
    open_page.evaluate("document.querySelector('[role=tab][aria-selected=true]').focus()")
    state = open_page.evaluate(probe)
    assert state["focus"] == "aa" and state["role"] == "tab" and state["selected"] == ["aa"]
    assert state["indexes"] == ["0", "-1"], "exactly one tab is in the tab order"
    assert state["list"] == "Language" and all(state["controls"]) and all(state["labelled"])
    assert state["panelFocusable"] == [0, 0]
    for key, expected in (
        ("ArrowRight", "bb"),
        ("ArrowRight", "aa"),
        ("ArrowLeft", "bb"),
        ("Home", "aa"),
        ("End", "bb"),
    ):
        open_page.press(key)
        moved = open_page.evaluate(probe)
        assert moved["focus"] == expected and moved["selected"] == [expected], key
        assert sorted(moved["indexes"]) == ["-1", "0"]


def test_scripts_off_every_panel_is_present_under_a_label_in_the_default_modes_order(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    open_page.resize(*NARROW)
    open_page.open(f"{origin.origin}/{UNIT}", scripts=False)
    state = read(open_page)
    assert state["pair"]["panels"] == ["aa", "bb"] and state["pair"]["labels"] == 2
    assert state["pair"]["bar"] is False, "the tab bar ships hidden until the script shows it"
    assert state["aa-error"]["panels"] == ["aa"] and state["bb-warning"]["panels"] == ["bb"], (
        "the default mode lists both, so each one-language example reads"
    )
    open_page.capture(capture_dir / "example-scripts-off.png")


def test_a_corpus_with_no_modes_draws_the_panels_and_no_tab_bar(
    open_page: OpenPage, tmp_path_factory: pytest.TempPathFactory
) -> None:
    languages_only = {"corpus_api": 8, "languages": READING["languages"]}
    documents = [document(ordinal=1, blocks=BLOCKS)]
    out = build(tmp_path_factory.mktemp("plain-example"), "p", documents, languages_only)
    with served.serving(site.Site(out.parent), corpus=out.name) as running:
        open_page.resize(*WIDE)
        open_page.open(f"{running.origin}/{UNIT}")
        state = read(open_page)
    assert state["pair"]["panels"] == ["aa", "bb"] and state["pair"]["bar"] is False
    assert not (out / ".studyforge" / "assets" / "modes.css").exists()
