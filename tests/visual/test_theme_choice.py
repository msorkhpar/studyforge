"""The reader's own choice of theme, in a real browser.

⛔ **Both a light and a dark theme, chosen by the reader.** `palette.css` carries
both and guards `[data-theme="light"]` and `[data-theme="dark"]`; the page's
control writes one of them, so a reader whose machine says light can still read
the dark page.

⭐ **Every clause here drives the REAL control in a real browser**, over
`file://` with no server, because that is the only place the answer is worth
having: a stored choice, a reload, a system that says the opposite, and scripting
turned off entirely.

⛔ **Each clause is asserted BOTH WAYS (R12):** choosing dark on a light system
paints the dark ground and survives a reload — and with nothing stored the system
setting still wins, choosing *system* again hands the page back, and with scripts
off the control is not shown at all.

⚠️ **The browser PROFILE outlives the tab**, so every reading here clears the
store before and after itself. A choice left behind would be the starting state
of the next reading, which is the one way this module could pass while the
feature did nothing.

## ⛔ What this module does NOT read, and where that is read instead

The page must not FLASH the wrong theme, which means the stored choice is applied
before the first paint — by a synchronous boot in `<head>`, because a deferred
part of the bundle runs after the page is painted. ⚠️ A browser reading taken
after `load` cannot tell a boot from a late repaint, so the ordering is asserted
where it is visible: `tests/studyforge/render/pageassets/test_theme.py` holds the
boot in the head, ahead of everything, and holds its spelling of the store's key
equal to the store's own.
"""

from __future__ import annotations

import json
from collections.abc import Iterator

import pytest

from tests.visual import contrast, site, theme
from tests.visual.page import WIDE, OpenPage

#: ⛔ Imported rather than restated: the theme a reader CHOOSES is held to the
#: same band as the one their system gives them, by the same function.
from tests.visual.test_reading_room import BANDS, outside_the_band

#: The corpus whose build carries both page kinds this module opens.
CORPUS = "depth2"
UNIT_PAGE = f"{CORPUS}-unit-01"
INDEX_PAGE = f"{CORPUS}-index"

#: A window with room for the wide shape, spelled as `test_reading_room` spells
#: it so the two modules cannot disagree about which layout they are judging.
WIDER = (1600, WIDE[1])

# --- the reader chooses the theme ---------------------------------------------

#: The control, its buttons, and the one attribute the palette guards on.
THEME_CONTROL = '[data-section="theme"]'
#: ⭐ One icon button in the top bar: pressing it chooses the theme the page is NOT showing.
PRESS = f"document.querySelector('{THEME_CONTROL}').click()"
CHOSEN = "document.documentElement.getAttribute('data-theme')"

#: What the control looks like to a reader and to assistive technology, in one
#: reading. ⛔ `hidden` is read off the property, not the attribute: the script
#: unhides it by assigning the property.
CONTROL_READING = """
(() => {
  const button = document.querySelector('<control>');
  if (!button) return null;
  const box = button.getBoundingClientRect();
  return {
    name: button.getAttribute('aria-label'),
    tag: button.tagName,
    hidden: button.hidden,
    width: box.width,
    height: box.height,
    icons: Array.from(button.querySelectorAll('svg'))
                .filter(i => getComputedStyle(i).display !== 'none')
                .map(i => i.getAttribute('data-icon'))
  };
})()
""".replace("<control>", THEME_CONTROL)

#: Which of the two `theme-color` elements the browser is actually applying.
LIVE_THEME_COLOUR = """
Array.from(document.querySelectorAll('meta[name="theme-color"]'))
  .filter(m => !m.media || matchMedia(m.media).matches)
  .map(m => m.content)
"""


def darkness(page: OpenPage) -> float:
    """How dark the page's ground is, as its luminance — lower is darker."""
    return contrast.luminance(contrast.parse(theme.resolve(page)["--bg"]))


@pytest.fixture
def no_choice(open_page: OpenPage, built_site: site.Site) -> Iterator[OpenPage]:
    """A tab whose reader has chosen nothing, and leaves nothing behind.

    ⛔ The browser profile outlives the tab, so a choice stored by one reading
    would be the starting state of the next — which is the one way this module
    could pass while the feature did nothing.
    """
    open_page.resize(*WIDER)
    open_page.open(built_site.url(UNIT_PAGE), scheme="light")
    open_page.evaluate("localStorage.clear(); sessionStorage.clear()")
    open_page.open(built_site.url(UNIT_PAGE), scheme="light")
    yield open_page
    open_page.evaluate("localStorage.clear(); sessionStorage.clear()")


@pytest.mark.parametrize("case", (UNIT_PAGE, INDEX_PAGE))
def test_the_theme_control_is_on_every_page_kind(
    no_choice: OpenPage, built_site: site.Site, case: str
) -> None:
    """⛔ Both themes are reachable, from wherever the reader is."""
    no_choice.open(built_site.url(case), scheme="light")
    reading = no_choice.evaluate(CONTROL_READING)
    assert reading is not None, f"{case} carries no theme control"
    assert reading["hidden"] is False and reading["width"] > 0 and reading["height"] > 0
    assert reading["tag"] == "BUTTON" and reading["name"]
    assert reading["icons"] == ["sun"], reading["icons"]


def test_the_control_takes_keyboard_focus_like_every_other_control(no_choice: OpenPage) -> None:
    """⛔ A control the keyboard cannot reach is not a control."""
    focused = no_choice.evaluate(
        "(() => { const b = document.querySelector('" + THEME_CONTROL + "');"
        " b.focus(); return document.activeElement === b; })()"
    )
    assert focused is True


def test_choosing_dark_on_a_light_system_paints_the_dark_ground(no_choice: OpenPage) -> None:
    """⛔ The clause itself, in a browser whose system says light."""
    before = darkness(no_choice)
    no_choice.evaluate(PRESS)
    assert no_choice.evaluate(CHOSEN) == "dark"
    assert no_choice.evaluate(CONTROL_READING)["icons"] == ["moon"]
    after = darkness(no_choice)
    assert after < before, f"the ground did not darken: {before} then {after}"
    astray = outside_the_band(
        {
            ink: contrast.ratio(
                contrast.parse(theme.resolve(no_choice)[ink]),
                contrast.parse(theme.resolve(no_choice)["--bg"]),
            )
            for ink in BANDS
        }
    )
    assert not astray, "the chosen theme is outside the band: " + ", ".join(astray)


def test_the_choice_survives_a_reload_on_a_light_system(
    no_choice: OpenPage, built_site: site.Site
) -> None:
    """⛔ *"remembers the reader's choice"* — read after a fresh navigation."""
    no_choice.evaluate(PRESS)
    chosen = darkness(no_choice)
    no_choice.open(built_site.url(INDEX_PAGE), scheme="light")
    assert no_choice.evaluate(CHOSEN) == "dark"
    assert darkness(no_choice) == chosen
    assert no_choice.evaluate(CONTROL_READING)["icons"] == ["moon"]


def test_with_nothing_stored_the_system_setting_still_wins(
    no_choice: OpenPage, built_site: site.Site
) -> None:
    """⭐ The other way: no record, and the two systems paint two pages."""
    assert no_choice.evaluate(CHOSEN) is None
    light = darkness(no_choice)
    no_choice.open(built_site.url(UNIT_PAGE), scheme="dark")
    assert no_choice.evaluate(CHOSEN) is None
    assert darkness(no_choice) < light


def test_a_press_on_a_dark_system_chooses_light_and_keeps_it_against_the_system(
    no_choice: OpenPage, built_site: site.Site
) -> None:
    """⭐ The other way: the press chooses the theme the page is not showing, whatever it
    follows.
    """
    no_choice.open(built_site.url(UNIT_PAGE), scheme="dark")
    assert no_choice.evaluate(CONTROL_READING)["icons"] == ["moon"]
    dark = darkness(no_choice)
    no_choice.evaluate(PRESS)
    assert no_choice.evaluate(CHOSEN) == "light"
    assert darkness(no_choice) > dark
    no_choice.open(built_site.url(UNIT_PAGE), scheme="dark")
    assert no_choice.evaluate(CHOSEN) == "light"
    assert no_choice.evaluate(CONTROL_READING)["icons"] == ["sun"]


def test_the_browser_chrome_colour_follows_the_chosen_theme(no_choice: OpenPage) -> None:
    """⛔ *"the `theme-color` pair must stay honest for whichever theme is showing"*."""
    system = no_choice.evaluate(LIVE_THEME_COLOUR)
    assert len(system) == 1, system
    no_choice.evaluate(PRESS)
    forced = no_choice.evaluate(LIVE_THEME_COLOUR)
    assert len(forced) == 1 and forced != system, (system, forced)


def test_with_scripts_off_the_control_is_not_shown_and_the_system_still_decides(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⭐ The other way, and R8's floor: nothing about the page needs the script.

    ⛔ The control ships `hidden` in the markup and the page script is what
    reveals it, so a reader with scripting off is shown a page that follows
    their system rather than a control that could not do anything.
    """
    open_page.resize(*WIDER)
    open_page.open(built_site.url(UNIT_PAGE), scheme="dark", scripts=False)
    reading = open_page.evaluate(CONTROL_READING)
    assert reading is not None and reading["hidden"] is True
    assert open_page.evaluate(CHOSEN) is None
    dark = darkness(open_page)
    open_page.open(built_site.url(UNIT_PAGE), scheme="light", scripts=False)
    assert darkness(open_page) > dark


# --- what the head boot may touch, read in the browser ------------------------


#: The key the store composes for the head boot's cache, and the expression that
#: reads it back. ⛔ Spelled once here because this module reads it from OUTSIDE
#: the page; the join between the store's composition and the boot's literal is
#: `test_theme.py`'s, against both source files.
BOOT_CACHE = "sessionStorage.getItem('studyforge.boot.theme.v1')"

#: ⛔ **An ORDERING instrument, and it is the point of this section.** It
#: replaces each storage accessor with one that records `document.readyState`
#: the FIRST time that area's property is read — and delegates, so nothing about
#: the page changes and no area is bound by the instrument itself. ⚠️ Installed
#: through `Page.addScriptToEvaluateOnNewDocument`, which runs before the
#: document's own first script, because a reading taken after the head has run
#: cannot say when the head ran.
WATCH_FIRST_TOUCH = """
(() => {
  for (const area of ['localStorage', 'sessionStorage']) {
    const own = Object.getOwnPropertyDescriptor(Window.prototype, area);
    Object.defineProperty(window, area, {
      configurable: true,
      get() {
        if (!window.__firstTouch) { window.__firstTouch = {}; }
        if (!(area in window.__firstTouch)) {
          window.__firstTouch[area] = document.readyState;
        }
        return own.get.call(this);
      },
    });
  }
})()
"""

FIRST_TOUCH = "JSON.stringify(window.__firstTouch || {})"


def test_choosing_a_theme_caches_it_where_the_head_boot_can_read_it(
    no_choice: OpenPage,
) -> None:
    """⛔ The cache the boot reads, kept in step with each press.

    ⭐ The durable answer stays in the display record; this is the one string
    the boot may act on, and an absent cache is how *system* is said, because an
    absent cache and a stored word must not be two answers to one question.
    """
    assert no_choice.evaluate(BOOT_CACHE) is None
    no_choice.evaluate(PRESS)
    assert no_choice.evaluate(BOOT_CACHE) == "dark"
    no_choice.evaluate(PRESS)
    assert no_choice.evaluate(BOOT_CACHE) == "light"


def test_the_head_never_binds_the_store_the_readers_marks_live_in(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⛔ **The head never binds `localStorage`, read as an ORDER rather than a delay.**

    ⚠️ **The defect this exists for.** A boot that reads the display record out
    of `localStorage` in the `<head>` binds that area at the earliest moment a
    document can. A document that binds it before the previous page's write has
    been committed keeps a snapshot WITHOUT that write, for its whole life; the
    reader then presses *Mark as read* and the record is rewritten from the
    stale set, destroying the earlier mark — under load, often.

    ⭐ **So the clause is about WHEN, and it is exact.** `document.readyState`
    is `loading` while the parser is in the head and `interactive` by the time a
    deferred script runs, so the two moments are told apart by name and not by a
    duration. ⚠️ The `sessionStorage` reading is the other way in the same
    breath: that area IS touched while loading — by the boot — so a reading that
    simply never saw a first touch could not pass this.
    """
    open_page.browser.call(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": WATCH_FIRST_TOUCH},
        session=open_page.session,
    )
    open_page.resize(*WIDER)
    open_page.open(built_site.url(UNIT_PAGE), scheme="light")
    touched = json.loads(str(open_page.evaluate(FIRST_TOUCH)))

    assert "loading" in touched.values(), (
        "no storage area at all was read while the head was parsing, so there "
        f"is no boot here and this reading is vacuous: {touched}"
    )
    assert touched.get("localStorage") is not None, (
        f"nothing read the durable store on this page at all: {touched}"
    )
    assert touched["localStorage"] != "loading", (
        "the durable store the reader's marks live in is bound while the head "
        "is still parsing, which is the ordering that loses a reader's marks: "
        f"{touched}"
    )
    assert touched.get("sessionStorage") == "loading", (
        "the area read in the head is not the boot cache, so the flash the boot "
        f"exists to prevent is back: {touched}"
    )
