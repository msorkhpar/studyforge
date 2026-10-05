"""A page somebody can read for hours, read in a real browser.

⛔ **The subject is a reading room**: colours a reader can read for hours
without strain, the containers rail on every page including the first, a
narration bar the width of the content whose buttons do not grow with it, and a
reading column that uses a wide window.

⭐ **Every clause here is a LIVE reading of a laid-out page**, taken through the
browser after the cascade, the media query and the custom properties have all
resolved — the class of defect no assertion over a stylesheet can see, and the
reason `tests/visual/` exists.

⛔ **Each clause is asserted BOTH WAYS (R12).** The arithmetic every clause uses
is a module-level function of a *reading*, and each one is handed a planted
reading — the palette that shipped, a button stretched to its row, the narrow
measure, an aside left in the column — which it must reject by name. ⚠️ A check
that has only ever seen the repaired page has not been shown to notice anything.

## ⛔ Why the band has a FLOOR as well as a ceiling

⚠️ **One band of 4.5:1–9.0:1 for every ink reads as too dim.** ⭐ The bands are
set from a reference page that reads comfortably for hours: its body ink
measures 12.14:1, its quieter ink 8.33:1 and its faintest 5.59:1, on a ground
that is neither white nor black. ⛔ So each ink has its own band around the
reading of the ink it corresponds to, the ceiling stays (near-black ink on
near-white paper is the other failure), and BOTH bounds are refuted here: a
planted 1:1 reading, a planted black-on-white reading, and a too-bright and a
too-dim palette.

## ⛔ The reader chooses the theme, and this module reads both of them

⭐ The palette carries a light and a dark theme, and the page offers the reader
the choice. The readings below drive the real control in a
real browser: choosing dark on a light system paints the dark ground and
survives a reload, and with nothing stored the system setting still wins.
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

#: `token -> (floor, ceiling)` for each ink that carries running text. ⛔ The
#: bounds are the reference page's three readings with room either side — see
#: this module's docstring — and NOT WCAG AA, whose floor alone admits a page
#: that reads as dim. ⚠️ Every bound is a contrast ratio and none of them is a
#: colour.
BANDS = {"--fg": (10.0, 14.0), "--fg-soft": (6.5, 10.0), "--muted": (4.5, 7.0)}

#: How long a line of running prose may be, in characters. ⛔ The measure is
#: *argued from line length in characters*: below this a wide window is
#: wasted, above it the eye loses the line it is tracking back to.
#:
#: ⚠️ **`LONGEST_LINE` and the `--measure` cap move together or not at all.**
#: ⛔ 110 is where tracking back to the start of the next line fails, and
#: `--measure` is COUNTED against it: `80ch` puts the first corpus's worst
#: paragraph at about 109 and `82ch` at about 112 (the counts are recorded in
#: `palette.css`). ⭐ So the bound picks the cap, rather than the cap moving the
#: bound.
SHORTEST_LINE = 75
LONGEST_LINE = 110

#: The region selectors this module reads, spelled as the stylesheets spell them.
RAIL = 'nav[aria-label="Containers"]'
OUTLINE = 'nav[aria-label="Outline"]'
ABOUT = 'section[aria-label="About this site"]'
SURFACE = "main#content"
PLAYER = "footer#player"

#: Every box this module compares, in one reading. ⛔ Border boxes in viewport
#: coordinates, named for what they are.
BOXES = (
    """
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
""".replace("<rail>", RAIL)
    .replace("<outline>", OUTLINE)
    .replace("<about>", ABOUT)
    .replace("<surface>", SURFACE)
    .replace("<player>", PLAYER)
)

#: The longest line of running prose on the page, in characters, measured by
#: laying one paragraph's text out a word at a time. ⛔ Not `--measure` read back
#: as a number: `ch` is the zero of the element's own face and the question is
#: how many characters of THIS prose fit on a line.
LONGEST_PROSE_LINE = """
(() => {
  const range = document.createRange();
  let longest = 0;
  for (const p of document.querySelectorAll('main p')) {
    /* ⛔ A paragraph with no boxes is not a line anybody reads, and it cannot be
       measured either: every range inside a `hidden` element reports the same
       zero rectangle, so the loop below never sees a line break and counts the
       WHOLE paragraph as one line: a hidden `<p>` in the practice panel would read
       as a line of a few hundred characters that no reader is shown. */
    if (!p.getClientRects().length) continue;
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
    """Which inks are outside the band named after them, as sentences.

    ⛔ One function for both bounds and for all three inks: a check that only
    ever asserted a floor passes a palette that is painful to read, and a check
    that only ever asserted a ceiling passes one too dim to read.
    """
    astray = []
    for token, ratio in sorted(ratios.items()):
        floor, ceiling = BANDS[token]
        if ratio < floor or ratio > ceiling:
            astray.append(f"{token} is {ratio:.2f}:1, outside {floor}:1–{ceiling}:1")
    return astray


def extreme(colour: str) -> bool:
    """Whether a resolved colour is pure black or pure white.

    ⛔ Text is never pure white on dark and never pure
    black on light — and it is a statement about the colour, not about a ratio.
    """
    channels = [int(part) for part in contrast.parse(colour)[:3]]
    return channels in ([0, 0, 0], [255, 255, 255])


def beside(one: dict, other: dict) -> bool:
    """Whether `one` is laid out beside `other` rather than above or below it."""
    return one["top"] < other["bottom"] - TOUCHING and other["top"] < one["bottom"] - TOUCHING


def column(*boxes: dict) -> dict:
    """The vertical extent the given boxes span together, as one box."""
    return {
        "top": min(box["top"] for box in boxes),
        "bottom": max(box["bottom"] for box in boxes),
    }


def grown(narrow: list[dict], wide: list[dict]) -> list[str]:
    """Which of the transport's controls are bigger in the wide window than the narrow one.

    ⛔ The clause in one sentence: the bar spans the content and the BUTTONS do
    not grow with it.
    """
    return [
        f"control {index} is {big['width']:.2f}px wide against {small['width']:.2f}px"
        for index, (small, big) in enumerate(zip(narrow, wide, strict=True))
        if big["width"] > small["width"] + TOUCHING or big["height"] > small["height"] + TOUCHING
    ]


def unpainted(controls: list[dict]) -> list[str]:
    """Which of the transport's controls have no box at all, as sentences.

    ⛔ **The zero-box blindness.** `grown`
    compares a control's box at one width against its box at another, and a
    `hidden` element reports `0 × 0` at EVERY width — so a transport that had
    stopped being revealed at all would satisfy *"the buttons did not grow"*
    for every control, at every width, forever. ⚠️ A population check that read
    `json.dumps(controls)` truthy would pass a list of zero boxes.

    ⭐ Asserted as a box and not as a `hidden` attribute: `content-visibility`,
    `display: none` on an ancestor and a zero-height clip all read the same to a
    reader, and only the box is the question this module asks.
    """
    return [
        f"control {index} has no box ({box['width']:.2f} x {box['height']:.2f})"
        for index, box in enumerate(controls)
        if box["width"] <= 0 or box["height"] <= 0
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
    """⛔ The contrast bands, measured through the browser in both themes.

    ⭐ The inks the page actually reads in — the body ink, the quieter one and
    the faintest — against the ground they sit on, as the browser resolved them.
    """
    open_page.resize(*WIDER)
    open_page.open(built_site.url(case), scheme=scheme)
    resolved = theme.resolve(open_page)
    ratios = {
        ink: contrast.ratio(contrast.parse(resolved[ink]), contrast.parse(resolved["--bg"]))
        for ink in BANDS
    }
    astray = outside_the_band(ratios)
    assert not astray, f"{case} in {scheme}: " + ", ".join(astray)


@pytest.mark.parametrize("scheme", SCHEMES)
def test_the_ink_is_never_pure_black_or_pure_white(
    open_page: OpenPage, built_site: site.Site, scheme: str
) -> None:
    """⛔ No pure black or pure white, asserted on the resolved colours themselves."""
    open_page.resize(*WIDER)
    open_page.open(built_site.url(UNIT_PAGE), scheme=scheme)
    resolved = theme.resolve(open_page)
    extremes = [token for token in ("--fg", "--fg-soft", "--bg") if extreme(resolved[token])]
    assert not extremes, f"{scheme}: {extremes} resolve to pure black or pure white"


def test_the_band_catches_a_reading_at_either_bound() -> None:
    """⛔ Both ways, and both bounds.

    ⭐ 15.3:1 is near-white chalk on a dark green board, 7.33:1 is a body ink
    that reads as dim, and 1:1 is the harness's own `contrast` damage. Each is
    caught by the same function, and the reference page's three readings are not.
    """
    assert outside_the_band({"--fg": 15.3}) == ["--fg is 15.30:1, outside 10.0:1–14.0:1"]
    assert outside_the_band({"--fg": 7.33}) == ["--fg is 7.33:1, outside 10.0:1–14.0:1"]
    assert outside_the_band({"--fg": 1.0}) == ["--fg is 1.00:1, outside 10.0:1–14.0:1"]
    assert outside_the_band({"--fg": 12.1, "--fg-soft": 8.3, "--muted": 5.6}) == []


def test_a_planted_pure_ink_is_caught() -> None:
    assert extreme("rgb(0, 0, 0)") and extreme("rgb(255, 255, 255)")
    assert not extreme("rgb(83, 78, 70)")


# --- clause 2: the rail is on the first page too -----------------------------


def test_the_first_page_carries_the_rail(open_page: OpenPage, built_site: site.Site) -> None:
    """⛔ The containers rail is on the first page too.

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
    # ⚠️ Beside the CONTENT COLUMN, which is the masthead and the list together
    # — not beside the list alone. The index's rail is as tall as the courses it
    # names, and the list starts below a masthead that now also carries the
    # theme control, so on a short corpus the two boxes need not overlap at all
    # while the rail is exactly where it belongs. ⛔ A reading that compared it
    # with the list alone would pass or fail on the height of a heading.
    column = {
        "top": reading["header"]["top"],
        "bottom": reading["surface"]["bottom"],
    }
    assert beside(reading["rail"], column)
    assert reading["rail"]["top"] <= reading["header"]["top"] + TOUCHING, (
        "the rail starts below the masthead rather than beside it"
    )


def test_the_rail_beside_reading_catches_a_rail_under_the_content() -> None:
    """⭐ The other way: a rail pushed below the column is not beside it."""
    column = {"top": 0.0, "bottom": 700.0}
    assert beside({"top": 0.0, "bottom": 151.0}, column)
    assert not beside({"top": 720.0, "bottom": 860.0}, column)


def test_the_rail_on_the_first_page_reaches_the_other_containers(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⭐ A menu that reaches nothing is not a containers rail."""
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
    """⛔ The narration bar is the width of the content."""
    assert spans_the_content(wide_unit), (
        f"the transport is {wide_unit['player']['width']:.2f}px wide beside a "
        f"{wide_unit['surface']['width']:.2f}px reading column, starting at "
        f"{wide_unit['player']['left']:.2f}px against a rail ending at "
        f"{wide_unit['rail']['right']:.2f}px"
    )


def test_the_transports_buttons_do_not_grow_with_it(
    open_page: OpenPage, built_site: site.Site, wide_unit: dict
) -> None:
    """⛔ The bar widens but its buttons do not grow: the same controls, both widths."""
    open_page.resize(*WIDE)
    open_page.open(built_site.url(UNIT_PAGE))
    narrow = dict(open_page.evaluate(BOXES))["controls"]  # type: ignore[index]

    assert narrow, "the page carries no transport controls, so this judges nothing"
    blind = unpainted(narrow) + unpainted(wide_unit["controls"])
    assert not blind, (
        "the transport's controls are not painted at one of these widths, so the "
        f"comparison below is between two empty boxes: {blind}"
    )
    bigger = grown(narrow, wide_unit["controls"])
    assert not bigger, "the transport's controls grow with its width: " + ", ".join(bigger)


def test_a_planted_stretched_control_is_caught() -> None:
    """⭐ Both ways: a button given the bar's own width fails the same function."""
    small = [{"width": 120.0, "height": 34.0}]
    stretched = [{"width": 980.0, "height": 34.0}]
    assert grown(small, stretched) == ["control 0 is 980.00px wide against 120.00px"]
    assert grown(small, small) == []


def test_a_planted_unpainted_control_is_caught() -> None:
    """⭐ Both ways: a zero box is named, and a real one is not."""
    assert unpainted([{"width": 0.0, "height": 0.0}]) == ["control 0 has no box (0.00 x 0.00)"]
    assert unpainted([{"width": 120.0, "height": 34.0}]) == []


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
    """⭐ Both ways, with the column cut back to a measure this module rejects.

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
    # ⚠️ Beside the COLUMN the page reads down — its header, then its content —
    # and not only beside the content: the outline starts at the column's top,
    # so a short one sits wholly beside the header, and it is still beside.
    assert beside(outline, column(wide_unit["header"], wide_unit["surface"]))


def test_the_first_pages_explanation_sits_beside_the_list(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⛔ A wide window uses its width for the secondary facts."""
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


# --- the masthead, the trail and a resting page --------------------------------


def test_nothing_is_lit_before_the_reader_starts_narration(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⛔ In the browser: a resting page shows no highlight."""
    open_page.resize(*WIDER)
    open_page.open(built_site.url(UNIT_PAGE))
    assert int(open_page.evaluate(SPEAKING)) == 0  # type: ignore[arg-type]


def test_pressing_play_is_what_lights_a_passage(open_page: OpenPage, built_site: site.Site) -> None:
    """⭐ The other way: the highlight exists and a press is what reaches it."""
    open_page.resize(*WIDER)
    open_page.open(built_site.url(UNIT_PAGE))
    open_page.evaluate("document.querySelector('#play').click()")
    assert int(open_page.evaluate(SPEAKING)) == 1  # type: ignore[arg-type]


def test_the_masthead_prints_no_bare_kind_label(open_page: OpenPage, built_site: site.Site) -> None:
    """⛔ Nothing under the title but the title and its trail."""
    open_page.resize(*WIDER)
    open_page.open(built_site.url(UNIT_PAGE))
    lines = open_page.evaluate(
        "Array.from(document.querySelectorAll('body > header > p')).map(p => p.textContent.trim())"
    )
    assert list(lines) == [], f"the masthead prints {lines} under the title"


def test_the_trail_names_each_level_once(open_page: OpenPage, built_site: site.Site) -> None:
    """⛔ Each level named once, read off the laid-out trail."""
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
    assert not unpainted(wide_unit["controls"]), (
        "the transport's controls are in the document and painted nowhere, so every "
        f"box this module reads off them is zero: {unpainted(wide_unit['controls'])}"
    )
