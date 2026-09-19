"""`W388` stage 2 in a real browser: the reader's own choice of theme.

⛔ **THE USER, 2026-09-19:** *"have the both dark and light themes in studyforge
as well"*. `palette.css` has carried both since `W362` and has guarded
`[data-theme="light"]` and `[data-theme="dark"]` since then; until this row
nothing on the page wrote either, so a reader whose machine said light could not
read the dark page at all.

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

# --- the reader chooses the theme (the user, 2026-09-19) ---------------------

#: The control, its buttons, and the one attribute the palette guards on.
THEME_CONTROL = '[data-section="theme"]'
THEME_BUTTON = '[data-theme-choice="%s"]'
CHOSEN = "document.documentElement.getAttribute('data-theme')"

#: What the control looks like to a reader and to assistive technology, in one
#: reading. ⛔ `hidden` is read off the property, not the attribute: the script
#: unhides it by assigning the property.
CONTROL_READING = """
(() => {
  const group = document.querySelector('<control>');
  if (!group) return null;
  const buttons = Array.from(group.querySelectorAll('button'));
  const box = group.getBoundingClientRect();
  return {
    name: group.getAttribute('aria-label'),
    role: group.getAttribute('role'),
    hidden: group.hidden,
    width: box.width,
    height: box.height,
    pressed: buttons.filter(b => b.getAttribute('aria-pressed') === 'true')
                    .map(b => b.getAttribute('data-theme-choice')),
    choices: buttons.map(b => b.getAttribute('data-theme-choice')),
    words: buttons.map(b => b.textContent.trim())
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
    open_page.evaluate("localStorage.clear()")
    open_page.open(built_site.url(UNIT_PAGE), scheme="light")
    yield open_page
    open_page.evaluate("localStorage.clear()")


@pytest.mark.parametrize("case", (UNIT_PAGE, INDEX_PAGE))
def test_the_theme_control_is_on_every_page_kind(
    no_choice: OpenPage, built_site: site.Site, case: str
) -> None:
    """⛔ The user's clause: both themes are reachable, from wherever they are."""
    no_choice.open(built_site.url(case), scheme="light")
    reading = no_choice.evaluate(CONTROL_READING)
    assert reading is not None, f"{case} carries no theme control"
    assert reading["hidden"] is False and reading["width"] > 0 and reading["height"] > 0
    assert reading["role"] == "group" and reading["name"]
    assert reading["choices"] == ["system", "light", "dark"]
    assert all(reading["words"]), reading["words"]
    assert reading["pressed"] == ["system"], reading["pressed"]


def test_the_control_takes_keyboard_focus_like_every_other_control(no_choice: OpenPage) -> None:
    """⛔ A control the keyboard cannot reach is not a control."""
    focused = no_choice.evaluate(
        "(() => { const b = document.querySelector('" + (THEME_BUTTON % "dark") + "');"
        " b.focus(); return document.activeElement === b; })()"
    )
    assert focused is True


def test_choosing_dark_on_a_light_system_paints_the_dark_ground(no_choice: OpenPage) -> None:
    """⛔ The clause itself, in a browser whose system says light."""
    before = darkness(no_choice)
    no_choice.evaluate(f"document.querySelector('{THEME_BUTTON % 'dark'}').click()")
    assert no_choice.evaluate(CHOSEN) == "dark"
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
    no_choice.evaluate(f"document.querySelector('{THEME_BUTTON % 'dark'}').click()")
    chosen = darkness(no_choice)
    no_choice.open(built_site.url(INDEX_PAGE), scheme="light")
    assert no_choice.evaluate(CHOSEN) == "dark"
    assert darkness(no_choice) == chosen
    assert no_choice.evaluate(CONTROL_READING)["pressed"] == ["dark"]


def test_with_nothing_stored_the_system_setting_still_wins(
    no_choice: OpenPage, built_site: site.Site
) -> None:
    """⭐ The other way: no record, and the two systems paint two pages."""
    assert no_choice.evaluate(CHOSEN) is None
    light = darkness(no_choice)
    no_choice.open(built_site.url(UNIT_PAGE), scheme="dark")
    assert no_choice.evaluate(CHOSEN) is None
    assert darkness(no_choice) < light


def test_choosing_system_again_hands_the_page_back_to_the_system(
    no_choice: OpenPage, built_site: site.Site
) -> None:
    """⭐ The other way for the third state: it is not a synonym for light."""
    no_choice.evaluate(f"document.querySelector('{THEME_BUTTON % 'light'}').click()")
    no_choice.open(built_site.url(UNIT_PAGE), scheme="dark")
    assert no_choice.evaluate(CHOSEN) == "light"
    forced = darkness(no_choice)
    no_choice.evaluate(f"document.querySelector('{THEME_BUTTON % 'system'}').click()")
    assert no_choice.evaluate(CHOSEN) is None
    assert darkness(no_choice) < forced


def test_the_browser_chrome_colour_follows_the_chosen_theme(no_choice: OpenPage) -> None:
    """⛔ *"the `theme-color` pair must stay honest for whichever theme is showing"*."""
    system = no_choice.evaluate(LIVE_THEME_COLOUR)
    assert len(system) == 1, system
    no_choice.evaluate(f"document.querySelector('{THEME_BUTTON % 'dark'}').click()")
    forced = no_choice.evaluate(LIVE_THEME_COLOUR)
    assert len(forced) == 1 and forced != system, (system, forced)
    no_choice.evaluate(f"document.querySelector('{THEME_BUTTON % 'system'}').click()")
    assert no_choice.evaluate(LIVE_THEME_COLOUR) == system


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
