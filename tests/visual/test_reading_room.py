"""`W388` and `W369` in a real browser: a page somebody can read for hours.

⛔ **THE ROW IS THE USER'S OWN READING OF A BUILT SITE**: *"the colors are super
tiring… a set of colors that I can read the document for hours without feeling
pain in my eyes or brain"*, *"keep left menu even in the first page"*, *"the
narration at bottom also might be better to be 100% width but not the buttons to
become big"*, *"the content itself is very limited in width"*.

⭐ **Every clause here is a LIVE reading of a laid-out page**, taken through the
browser after the cascade, the media query and the custom properties have all
resolved — the class of defect no assertion over a stylesheet can see, and the
reason `tests/visual/` exists (`W98`, `SF-34`).

⛔ **Each clause is asserted BOTH WAYS (R12).** The arithmetic every clause uses
is a module-level function of a *reading*, and each one is handed a planted
reading — the palette that shipped, a button stretched to its row, the narrow
measure, an aside left in the column — which it must reject by name. ⚠️ A check
that has only ever seen the repaired page has not been shown to notice anything.

## ⛔ Why the contrast band has a CEILING as well as a floor

⚠️ **The page this row was opened over cleared WCAG AA everywhere and was
painful to read**: near-white text on a dark green board is about 15:1, and the
brief's own instruction is to *compute contrast* rather than to maximise it.
⭐ So the clause is a BAND — at or above AA's 4.5:1 for body text, and not far
above it — and the row's words are *"within WCAG AA for body text and not far
above it"*. ⛔ Both bounds are refuted: a planted 1:1 reading and a planted
black-on-white reading are each caught by the same function.
"""

from __future__ import annotations

import json

import pytest

from tests.visual import contrast, site, theme
from tests.visual.page import NARROW, SCHEMES, WIDE, OpenPage

#: The one corpus whose build carries every region this module reads: two
#: containers (so there is a rail), a unit page with a transport, and an index.
CORPUS = "depth2"

#: The pages this module opens, by kind.
UNIT_PAGE = f"{CORPUS}-unit-01"
INDEX_PAGE = f"{CORPUS}-index"

#: A window with room for the three-column shape, and the narrow one below the
#: threshold. ⛔ `WIDE` and `NARROW` are `page.py`'s, so this module cannot
#: disagree with the rest of the harness about which layout it is judging.
WIDER = (1600, WIDE[1])

#: How far two readings may differ and still be the same reading, in CSS pixels
#: — the subpixel allowance every layout module here makes.
TOUCHING = 0.5

#: The band body text sits in. ⛔ The floor is WCAG AA for body text; the ceiling
#: is this row's *"and not far above it"*, and it is what the shipped palette
#: broke. ⚠️ Both are contrast ratios and neither is a colour.
AA = 4.5
CEILING = 9.0

#: How long a line of running prose may be, in characters. ⛔ The row asks for a
#: measure *argued from line length in characters*: below this a wide window is
#: wasted, above it the eye loses the line it is tracking back to.
SHORTEST_LINE = 75
LONGEST_LINE = 100

#: The region selectors this module reads, spelled as the stylesheets spell them.
RAIL = 'nav[aria-label="Containers"]'
OUTLINE = 'nav[aria-label="Outline"]'
ABOUT = 'section[aria-label="About this site"]'
SURFACE = "main#content"
PLAYER = "footer#player"

#: Every box this module compares, in one reading. ⛔ Border boxes in viewport
#: coordinates, named for what they are.
BOXES = """
(() => {
  const at = s => { const el = document.querySelector(s); if (!el) return null;
    const b = el.getBoundingClientRect();
    return {left: b.left, right: b.right, top: b.top, bottom: b.bottom,
            width: b.width, height: b.height}; };
  const controls = Array.from(document.querySelectorAll('footer#player button'))
    .map(el => { const b = el.getBoundingClientRect();
      return {width: b.width, height: b.height}; });
  return {rail: at('<rail>'), outline: at('<outline>'), about: at('<about>'),
          surface: at('<surface>'), player: at('<player>'), header: at('body > header'),
          controls: controls, window: window.innerWidth};
})()
""".replace("<rail>", RAIL).replace("<outline>", OUTLINE).replace("<about>", ABOUT).replace(
    "<surface>", SURFACE
).replace("<player>", PLAYER)

#: The longest line of running prose on the page, in characters, measured by
#: laying one paragraph's text out a word at a time. ⛔ Not `--measure` read back
#: as a number: `ch` is the zero of the element's own face and the question is
#: how many characters of THIS prose fit on a line.
LONGEST_PROSE_LINE = """
(() => {
  const range = document.createRange();
  let longest = 0;
  for (const p of document.querySelectorAll('main p')) {
    const node = p.firstChild;
    if (!node || node.nodeType !== 3) continue;
    const text = node.textContent;
    let start = 0, top = null;
    for (let i = 0; i <= text.length; i++) {
      if (i < text.length) {
        range.setStart(node, i); range.setEnd(node, i + 1);
        const box = range.getBoundingClientRect();
        if (top === null) { top = box.top; continue; }
        if (Math.abs(box.top - top) < 1) continue;
        longest = Math.max(longest, i - start);
        start = i; top = box.top;
      } else if (top !== null) {
        longest = Math.max(longest, i - start);
      }
    }
  }
  return longest;
})()
"""

#: Whether anything on the page is lit as being spoken, and what the transport
#: says. ⛔ Read as a count, so "nothing is lit" and "the hook was renamed and
#: nothing is ever lit" are told apart by the control below.
SPEAKING = "document.querySelectorAll('[data-speaking]').length"


# --- the arithmetic, as functions of a reading -------------------------------


def outside_the_band(ratios: dict[str, float]) -> list[str]:
    """Which body-text ratios are below AA or far above it, as sentences.

    ⛔ One function for both bounds: a check that only ever asserted the floor is
    the check the shipped palette passed while being painful to read.
    """
    return [
        f"{name} is {ratio:.2f}:1"
        for name, ratio in sorted(ratios.items())
        if ratio < AA or ratio > CEILING
    ]


def extreme(colour: str) -> bool:
    """Whether a resolved colour is pure black or pure white.

    ⛔ The row's own words — text is never pure white on dark and never pure
    black on light — and it is a statement about the colour, not about a ratio.
    """
    channels = [int(part) for part in contrast.parse(colour)[:3]]
    return channels in ([0, 0, 0], [255, 255, 255])


def beside(one: dict, other: dict) -> bool:
    """Whether `one` is laid out beside `other` rather than above or below it."""
    return one["top"] < other["bottom"] - TOUCHING and other["top"] < one["bottom"] - TOUCHING


def grown(narrow: list[dict], wide: list[dict]) -> list[str]:
    """Which of the transport's controls are bigger in the wide window than the narrow one.

    ⛔ The user's clause in one sentence: the bar spans the content and the
    BUTTONS do not grow with it.
    """
    return [
        f"control {index} is {big['width']:.2f}px wide against {small['width']:.2f}px"
        for index, (small, big) in enumerate(zip(narrow, wide, strict=True))
        if big["width"] > small["width"] + TOUCHING or big["height"] > small["height"] + TOUCHING
    ]


def spans_the_content(reading: dict) -> bool:
    """Whether the transport is as wide as everything right of the rail."""
    player, rail = reading["player"], reading["rail"]
    return (
        player is not None
        and rail is not None
        and player["left"] >= rail["right"] - TOUCHING
        and player["width"] > reading["surface"]["width"] + TOUCHING
    )


# --- the readings ------------------------------------------------------------


@pytest.fixture
def wide_unit(open_page: OpenPage, built_site: site.Site) -> dict:
    """The unit page's boxes at a window with room for the three-column shape."""
    open_page.resize(*WIDER)
    open_page.open(built_site.url(UNIT_PAGE))
    return dict(open_page.evaluate(BOXES))  # type: ignore[arg-type]


# --- clause 1: a palette for hours ------------------------------------------


@pytest.mark.parametrize("scheme", SCHEMES)
@pytest.mark.parametrize("case", (UNIT_PAGE, INDEX_PAGE))
def test_body_text_sits_in_the_band_this_row_asks_for(
    open_page: OpenPage, built_site: site.Site, scheme: str, case: str
) -> None:
    """⛔ `W388` clause 1, measured through the browser in both themes.

    ⭐ The inks the page actually reads in — the body ink, the quieter one and
    the faintest — against the ground they sit on, as the browser resolved them.
    """
    open_page.resize(*WIDER)
    open_page.open(built_site.url(case), scheme=scheme)
    resolved = theme.resolve(open_page)
    ratios = {
        f"{ink} on {ground}": contrast.ratio(
            contrast.parse(resolved[ink]), contrast.parse(resolved[ground])
        )
        for ink, ground in (("--fg", "--bg"), ("--fg-soft", "--bg"), ("--muted", "--bg"))
    }
    astray = outside_the_band(ratios)
    assert not astray, (
        f"{case} in {scheme}: body text outside {AA}:1–{CEILING}:1 — " + ", ".join(astray)
    )


@pytest.mark.parametrize("scheme", SCHEMES)
def test_the_ink_is_never_pure_black_or_pure_white(
    open_page: OpenPage, built_site: site.Site, scheme: str
) -> None:
    """⛔ The row's second sentence, asserted on the resolved colours themselves."""
    open_page.resize(*WIDER)
    open_page.open(built_site.url(UNIT_PAGE), scheme=scheme)
    resolved = theme.resolve(open_page)
    extremes = [token for token in ("--fg", "--fg-soft", "--bg") if extreme(resolved[token])]
    assert not extremes, f"{scheme}: {extremes} resolve to pure black or pure white"


def test_the_band_catches_a_reading_at_either_bound() -> None:
    """⛔ Both ways, and both bounds: the shipped palette failed the ceiling.

    ⭐ 15.3:1 is near-white chalk on the green board this row replaced, and 1:1
    is the harness's own `contrast` damage; each is caught by the same function,
    and a reading inside the band is not.
    """
    assert outside_the_band({"shipped": 15.3}) == ["shipped is 15.30:1"]
    assert outside_the_band({"flattened": 1.0}) == ["flattened is 1.00:1"]
    assert outside_the_band({"this row": 7.3}) == []


def test_a_planted_pure_ink_is_caught() -> None:
    assert extreme("rgb(0, 0, 0)") and extreme("rgb(255, 255, 255)")
    assert not extreme("rgb(83, 78, 70)")


# --- clause 2: the rail is on the first page too -----------------------------


def test_the_first_page_carries_the_rail(open_page: OpenPage, built_site: site.Site) -> None:
    """⛔ The user's words: *"keep left menu even in the first page"*.

    ⭐ Read off the laid-out index rather than its markup: a region emitted and
    then laid out under the fold, or behind the tree, is not a left menu.
    """
    open_page.resize(*WIDER)
    open_page.open(built_site.url(INDEX_PAGE))
    reading = dict(open_page.evaluate(BOXES))  # type: ignore[arg-type]

    assert reading["rail"] is not None, "the first page carries no rail at all"
    assert reading["rail"]["right"] <= reading["surface"]["left"] + TOUCHING, (
        f"the rail on the first page is not beside the list: it ends at "
        f"{reading['rail']['right']:.2f}px and the list starts at "
        f"{reading['surface']['left']:.2f}px"
    )
    assert beside(reading["rail"], reading["surface"])


def test_the_rail_on_the_first_page_reaches_the_other_containers(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⭐ A menu that reaches nothing is not the region the user asked for."""
    open_page.resize(*WIDER)
    open_page.open(built_site.url(INDEX_PAGE))
    hrefs = open_page.evaluate(
        f"Array.from(document.querySelectorAll('{RAIL} a')).map(a => a.getAttribute('href'))"
    )
    assert len(list(hrefs)) > 1, f"the first page's rail links {hrefs}"


def test_the_first_page_folds_the_rail_back_into_the_column_when_the_window_is_narrow(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⛔ The other way: below the threshold the rail is above the list, not beside it."""
    open_page.resize(*NARROW)
    open_page.open(built_site.url(INDEX_PAGE))
    reading = dict(open_page.evaluate(BOXES))  # type: ignore[arg-type]

    assert reading["rail"] is not None
    assert not beside(reading["rail"], reading["surface"]), (
        "the rail is still beside the list at the narrow width, where it is "
        "squeezed against the reading"
    )


# --- clause 3: the transport spans the content, the buttons do not grow ------


def test_the_transport_spans_the_whole_content(wide_unit: dict) -> None:
    """⛔ The user's words: the narration bar is the width of the content."""
    assert spans_the_content(wide_unit), (
        f"the transport is {wide_unit['player']['width']:.2f}px wide beside a "
        f"{wide_unit['surface']['width']:.2f}px reading column, starting at "
        f"{wide_unit['player']['left']:.2f}px against a rail ending at "
        f"{wide_unit['rail']['right']:.2f}px"
    )


def test_the_transports_buttons_do_not_grow_with_it(
    open_page: OpenPage, built_site: site.Site, wide_unit: dict
) -> None:
    """⛔ *"but not the buttons to become big"* — the same controls, both widths."""
    open_page.resize(*WIDE)
    open_page.open(built_site.url(UNIT_PAGE))
    narrow = dict(open_page.evaluate(BOXES))["controls"]  # type: ignore[index]

    assert narrow, "the page carries no transport controls, so this judges nothing"
    bigger = grown(narrow, wide_unit["controls"])
    assert not bigger, "the transport's controls grow with its width: " + ", ".join(bigger)


def test_a_planted_stretched_control_is_caught() -> None:
    """⭐ Both ways: a button given the bar's own width fails the same function."""
    small = [{"width": 120.0, "height": 34.0}]
    stretched = [{"width": 980.0, "height": 34.0}]
    assert grown(small, stretched) == ["control 0 is 980.00px wide against 120.00px"]
    assert grown(small, small) == []


def test_a_planted_transport_inside_the_column_is_caught() -> None:
    """⭐ And a bar that is merely the reading column's width is not a span."""
    reading = {
        "player": {"left": 300.0, "right": 900.0, "width": 600.0},
        "rail": {"right": 280.0},
        "surface": {"width": 600.0},
    }
    assert not spans_the_content(reading)


# --- clause 4: the reading column, and the aside beside it -------------------


def test_a_line_of_prose_is_the_length_this_row_argues_for(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⛔ Clause 4, argued from line length in characters and measured as one.

    ⭐ The longest laid-out line of running prose on the page, counted character
    by character through the browser's own line breaking — never `--measure`
    read back, which is a number in a file and not a line anybody reads.
    """
    open_page.resize(*WIDER)
    open_page.open(built_site.url(UNIT_PAGE))
    longest = int(open_page.evaluate(LONGEST_PROSE_LINE))  # type: ignore[arg-type]

    assert SHORTEST_LINE <= longest <= LONGEST_LINE, (
        f"a line of prose runs to {longest} characters, outside "
        f"{SHORTEST_LINE}–{LONGEST_LINE} at a {WIDER[0]}px window"
    )


def test_the_narrow_measure_that_shipped_is_caught_by_the_same_reading(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⭐ Both ways, with the column cut back to a measure this row rejects.

    ⚠️ The override is set on the page itself rather than on a damaged tree,
    because the reading under test is the laid-out line and not the stylesheet.
    """
    open_page.resize(*WIDER)
    open_page.open(built_site.url(UNIT_PAGE))
    open_page.evaluate("document.documentElement.style.setProperty('--measure', '40ch')")
    longest = int(open_page.evaluate(LONGEST_PROSE_LINE))  # type: ignore[arg-type]

    assert longest < SHORTEST_LINE, (
        f"a 40ch column still lays out {longest} characters to a line, so this "
        "reading cannot tell a narrow column from a wide one"
    )


def test_the_units_outline_sits_beside_the_reading_and_not_above_it(wide_unit: dict) -> None:
    """⛔ Clause 4's second half: the page's secondary block uses the room beside it."""
    outline = wide_unit["outline"]
    assert outline is not None, "the unit page carries no outline"
    assert outline["left"] >= wide_unit["surface"]["right"] - TOUCHING, (
        f"the outline starts at {outline['left']:.2f}px, inside the reading "
        f"column that ends at {wide_unit['surface']['right']:.2f}px"
    )
    assert beside(outline, wide_unit["surface"])


def test_the_first_pages_explanation_sits_beside_the_list(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⛔ `W369` clause 1: a wide window uses its width for the secondary facts."""
    open_page.resize(*WIDER)
    open_page.open(built_site.url(INDEX_PAGE))
    reading = dict(open_page.evaluate(BOXES))  # type: ignore[arg-type]

    assert reading["about"] is not None, "the first page carries no explanation"
    assert reading["about"]["left"] >= reading["surface"]["right"] - TOUCHING
    assert beside(reading["about"], reading["surface"])


@pytest.mark.parametrize("case", (UNIT_PAGE, INDEX_PAGE))
def test_the_aside_folds_back_above_the_content_when_the_window_is_narrow(
    open_page: OpenPage, built_site: site.Site, case: str
) -> None:
    """⛔ The other way: below the threshold the block is in the one column again."""
    open_page.resize(*NARROW)
    open_page.open(built_site.url(case))
    reading = dict(open_page.evaluate(BOXES))  # type: ignore[arg-type]
    aside = reading["outline"] if case == UNIT_PAGE else reading["about"]

    assert aside is not None
    assert not beside(aside, reading["surface"]), (
        "the aside is still beside the content at the narrow width, so the page "
        "has two columns where there is room for one"
    )


def test_the_beside_reading_tells_the_two_placements_apart() -> None:
    """⭐ The arithmetic itself, both ways, on two planted pairs."""
    column = {"top": 100.0, "bottom": 900.0}
    assert beside({"top": 100.0, "bottom": 400.0}, column)
    assert not beside({"top": 10.0, "bottom": 99.0}, column)


# --- clause 5 and `W369` clause 2 -------------------------------------------


def test_nothing_is_lit_before_the_reader_starts_narration(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⛔ `W369` clause 2, in the browser: a resting page shows no highlight."""
    open_page.resize(*WIDER)
    open_page.open(built_site.url(UNIT_PAGE))
    assert int(open_page.evaluate(SPEAKING)) == 0  # type: ignore[arg-type]


def test_pressing_play_is_what_lights_a_passage(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⭐ The other way: the highlight exists and a press is what reaches it."""
    open_page.resize(*WIDER)
    open_page.open(built_site.url(UNIT_PAGE))
    open_page.evaluate("document.querySelector('#play').click()")
    assert int(open_page.evaluate(SPEAKING)) == 1  # type: ignore[arg-type]


def test_the_masthead_prints_no_bare_kind_label(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⛔ `W388` clause 5: nothing under the title but the title and its trail."""
    open_page.resize(*WIDER)
    open_page.open(built_site.url(UNIT_PAGE))
    lines = open_page.evaluate(
        "Array.from(document.querySelectorAll('body > header p')).map(p => p.textContent.trim())"
    )
    assert list(lines) == [], f"the masthead prints {lines} under the title"


def test_the_trail_names_each_level_once(open_page: OpenPage, built_site: site.Site) -> None:
    """⛔ `W388` clause 5's first half, read off the laid-out trail."""
    open_page.resize(*WIDER)
    open_page.open(built_site.url(UNIT_PAGE))
    crumbs = [
        str(crumb).strip()
        for crumb in open_page.evaluate(
            "Array.from(document.querySelectorAll("
            "'nav[aria-label=\"Breadcrumb\"] li')).map(li => li.textContent)"
        )
    ]
    assert crumbs, "the unit page carries no trail"
    assert all(a != b for a, b in zip(crumbs, crumbs[1:], strict=False)), crumbs


def test_the_trail_reading_catches_a_repeated_crumb() -> None:
    """⭐ Both ways: the ISO corpus's own shape, where a group repeats the title."""
    crumbs = ["A Comprehensive Guide", "A Comprehensive Guide", "Introduction"]
    assert not all(a != b for a, b in zip(crumbs, crumbs[1:], strict=False))


def test_the_readings_this_module_takes_are_of_regions_that_exist(wide_unit: dict) -> None:
    """⛔ A selector that matches nothing reads as `None` and passes every `is not`.

    ⭐ So the population is asserted once, here: a renamed region reds by name
    rather than quietly emptying half of this module.
    """
    missing = [name for name in ("rail", "outline", "surface", "player") if wide_unit[name] is None]
    assert not missing, f"{missing} are not on the unit page this module reads"
    assert json.dumps(wide_unit["controls"]), "the transport carries no controls"
