"""`W388` STAGE 3: the page uses the window it is opened in, at four widths.

⛔ **SPLIT OUT OF `test_reading_room.py` AT A SEAM, AND THE SEAM IS THE SUBJECT**
(Ruling 261). That module answers *is this a page somebody can read for hours* —
the palette's contrast bands, the theme control, the rail on the first page, the
transport across the content, the length of a line. ⭐ **Every clause here
answers one different question instead: does the page use the WINDOW**, read at
four widths rather than at the one wide viewport that module opens. ⚠️ The other
half of the reason is stated rather than implied: `test_reading_room.py` was
measured at 531 lines against R11's 600 before this stage, and R11's remedy is a
split at a named seam, never a trim.

## ⛔ The user's third reading, and it is quoted

> Still the paragraph texts are not using the full width for some reason.

⭐ **What they were looking at, measured on the tree this module was written
against:** at a 2560px window the page laid out 1760px wide — `--page-max` on
`body`, with `margin-left: 0` — so the rail, the reading column and the aside
were all packed into the left two thirds and the last 820px of the screen was
empty. ⛔ **At 1280 and 1440 the same tree was FINE**, which is why this module
reads four widths: a clause asserted at one wide viewport passed over the defect
the whole stage exists for.

## ⚠️ Why the ceiling did not simply go up

⛔ **A bigger number in the same place moves the defect one display along** and
answers nothing. ⭐ The repair moves the bound off the page and onto the reading
SURFACE — the element a wide table or a long line of code is actually in — so the
page spans the window at every width while the thing the ceiling was written to
protect is still protected. ⚠️ The surface's own bound is
`tests/visual/test_rail_fixed.py`'s and `tests/visual/test_rail.py`'s to read;
what is under test here is that nothing is packed left.
"""

from __future__ import annotations

import pytest

from tests.visual import site
from tests.visual.page import WIDE, OpenPage
from tests.visual.test_reading_room import (
    ABOUT,
    INDEX_PAGE,
    LONGEST_LINE,
    LONGEST_PROSE_LINE,
    OUTLINE,
    RAIL,
    SHORTEST_LINE,
    SURFACE,
    TOUCHING,
    UNIT_PAGE,
)

#: The four window widths this stage is settled at, in CSS pixels. ⛔ **1280 and
#: 1440 are here because the tree that shipped PASSED at both**: the ceiling it
#: carried was 1760px, so a reading taken at either one would have called the
#: packed-left page correct. ⭐ 1920 and 2560 are the two the user's own screen
#: sits between.
WIDTHS = (1280, 1440, 1920, 2560)

#: The page's height, taken from the harness's wide viewport so this module
#: cannot disagree with the rest of the suite about how tall a window is.
HEIGHT = WIDE[1]

#: The ceiling `chrome.css` carried on `body` before this stage, as a length the
#: browser resolves. ⭐ The control plants THIS, inline on `body`, which is the
#: defect itself rather than an impression of it.
SHIPPED_CEILING = "110rem"

#: Every box these clauses compare, plus the two scalars the arithmetic needs —
#: the window's own width and the gutter the layout sets. ⛔ The gutter is READ
#: OFF THE PAGE through a probe rather than written here as a number of pixels,
#: so a palette that changes it changes this reading with it.
BOXES = (
    """
(() => {
  const at = sel => { const el = document.querySelector(sel); if (!el) return null;
    const b = el.getBoundingClientRect();
    return {left: b.left, right: b.right, top: b.top, bottom: b.bottom, width: b.width}; };
  const probe = document.createElement('div');
  probe.style.cssText = 'width: var(--gutter); position: absolute; visibility: hidden';
  document.body.appendChild(probe);
  const gutter = probe.getBoundingClientRect().width;
  probe.remove();
  return {body: at('body'), rail: at('<rail>'), surface: at('<surface>'),
          aside: at('<outline>') || at('<about>'),
          gutter: gutter, window: window.innerWidth};
})()
""".replace("<rail>", RAIL)
    .replace("<surface>", SURFACE)
    .replace("<outline>", OUTLINE)
    .replace("<about>", ABOUT)
)


def packed_left(reading: dict) -> list[str]:
    """Every way this reading fails to use the window, named one by one.

    ⛔ **The user's sentence as arithmetic.** Four things have to hold together
    and any one of them alone has a passing shape that is not the repair: a page
    that spans the window with its aside still tucked in beside the prose, an
    aside at the right edge of a page that is itself short of the screen, or a
    reading column that stops growing while both edges are where they should be.

    ⚠️ A missing region is a complaint and never a silent pass — a page with no
    aside cannot be judged by clauses about where the aside is.
    """
    window, gutter = reading["window"], reading["gutter"]
    body, rail, surface, aside = (
        reading["body"],
        reading["rail"],
        reading["surface"],
        reading["aside"],
    )
    complaints = []
    if body is None or rail is None or surface is None or aside is None:
        return ["the reading is missing a region, so nothing here can be judged"]
    if body["width"] < window - TOUCHING:
        complaints.append(
            f"the page is {body['width']:.2f}px in a {window:.2f}px window, so "
            f"{window - body['width']:.2f}px of it is dead"
        )
    if rail["left"] > TOUCHING:
        complaints.append(f"the rail starts {rail['left']:.2f}px in from the window's left edge")
    if window - aside["right"] > gutter + TOUCHING:
        complaints.append(
            f"the aside ends {window - aside['right']:.2f}px short of the window's right "
            f"edge, against a gutter of {gutter:.2f}px"
        )
    if aside["left"] - surface["right"] > gutter + TOUCHING:
        complaints.append(
            f"the reading column ends {aside['left'] - surface['right']:.2f}px before the "
            f"aside, against a gutter of {gutter:.2f}px, so it is not taking the slack"
        )
    return complaints


def read(open_page: OpenPage, url: str, width: int) -> dict:
    """Open one page at one width and read its boxes back."""
    open_page.resize(width, HEIGHT)
    open_page.open(url)
    return dict(open_page.evaluate(BOXES))  # type: ignore[arg-type]


# --- the clause, at every width -------------------------------------------


@pytest.mark.parametrize("width", WIDTHS)
@pytest.mark.parametrize("case", (UNIT_PAGE, INDEX_PAGE))
def test_the_three_columns_span_the_window(
    open_page: OpenPage, built_site: site.Site, case: str, width: int
) -> None:
    """⛔ The stage in one reading: no dead strip, at any of the four widths."""
    complaints = packed_left(read(open_page, built_site.url(case), width))

    assert not complaints, f"at {width}px the {case} page: " + "; ".join(complaints)


@pytest.mark.parametrize("width", (1920, 2560))
def test_the_ceiling_that_shipped_is_caught_at_the_widths_it_shipped_wrong_at(
    open_page: OpenPage, built_site: site.Site, width: int
) -> None:
    """⭐ Both ways, with the bound this stage moved put back where it was.

    ⚠️ Planted inline on `body` rather than on a damaged tree, because what is
    under test is the laid-out page and not the stylesheet — and inline is the
    one place that beats the wide shape's own `max-width: none`.
    """
    open_page.resize(width, HEIGHT)
    open_page.open(built_site.url(UNIT_PAGE))
    open_page.evaluate(f"document.body.style.maxWidth = '{SHIPPED_CEILING}'")
    complaints = packed_left(dict(open_page.evaluate(BOXES)))  # type: ignore[arg-type]

    assert complaints, (
        f"at {width}px the ceiling that shipped leaves this reading with nothing to "
        "say, so it cannot tell the packed-left page from the repaired one"
    )


def test_the_reading_is_not_satisfied_by_a_narrow_window_it_happens_to_fill(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⛔ The other half of the control: the shipped ceiling PASSES at 1280.

    ⚠️ This is why `WIDTHS` has four entries and not one. A clause taken at a
    window narrower than the bound reads a page that fills it, and the defect is
    invisible — which is exactly how the shipped tree got its green readings.
    """
    open_page.resize(1280, HEIGHT)
    open_page.open(built_site.url(UNIT_PAGE))
    open_page.evaluate(f"document.body.style.maxWidth = '{SHIPPED_CEILING}'")

    assert not packed_left(dict(open_page.evaluate(BOXES))), (  # type: ignore[arg-type]
        "the shipped ceiling is already caught at 1280px, so the four widths above "
        "are not what makes this stage's reading work"
    )


# --- the cap, argued from the line it lays out at each of the four widths ---


#: A cap wide enough that the line runs past the band at every wide width.
#: ⭐ `--measure` stayed at `76ch` through this stage and that is a MEASURED
#: answer rather than an inherited one: in the pinned image it is the widest cap
#: whose longest laid-out line stays at or under `LONGEST_LINE`, and `77ch` lays
#: out 102. ⛔ The counts are recorded beside the declaration in `palette.css`;
#: this is the number on the other side of that argument.
#:
#: ⚠️ **The same cap lays out FEWER characters on an unpinned host browser than
#: in the image** — one step fewer, measured — so the band has to hold in both
#: and this control has to fail in both. `96ch` is well past either.
TOO_WIDE_A_CAP = "96ch"


@pytest.mark.parametrize("width", WIDTHS)
def test_a_line_of_prose_stays_inside_the_band_at_every_width(
    open_page: OpenPage, built_site: site.Site, width: int
) -> None:
    """⛔ The cap is ARGUED FROM CHARACTERS PER LINE, so it is read as characters.

    ⚠️ **At every width, not at one.** A cap is only visible above the window
    where the column reaches it: at 1280 the column is narrower than the cap and
    the line runs short of it, and the same declaration at 1920 is what decides
    whether the widened page is readable.
    """
    open_page.resize(width, HEIGHT)
    open_page.open(built_site.url(UNIT_PAGE))
    longest = int(open_page.evaluate(LONGEST_PROSE_LINE))  # type: ignore[arg-type]

    assert SHORTEST_LINE <= longest <= LONGEST_LINE, (
        f"a line of prose runs to {longest} characters at a {width}px window, "
        f"outside {SHORTEST_LINE}–{LONGEST_LINE}"
    )


@pytest.mark.parametrize("width", (1920, 2560))
def test_a_cap_wide_enough_to_hurt_the_reading_is_caught_by_the_same_count(
    open_page: OpenPage, built_site: site.Site, width: int
) -> None:
    """⭐ Both ways: the page widening is not licence for any cap at all."""
    open_page.resize(width, HEIGHT)
    open_page.open(built_site.url(UNIT_PAGE))
    open_page.evaluate(
        f"document.documentElement.style.setProperty('--measure', '{TOO_WIDE_A_CAP}')"
    )
    longest = int(open_page.evaluate(LONGEST_PROSE_LINE))  # type: ignore[arg-type]

    assert longest > LONGEST_LINE, (
        f"a {TOO_WIDE_A_CAP} column still lays out {longest} characters at a {width}px "
        "window, so this reading cannot tell a comfortable line from a punishing one"
    )


# --- the arithmetic itself, on planted readings ----------------------------


def sound(**changes: object) -> dict:
    """A reading of a page that uses its window, with `changes` applied to it."""
    reading = {
        "window": 2560.0,
        "gutter": 20.0,
        "body": {"left": 0.0, "right": 2560.0, "width": 2560.0},
        "rail": {"left": 0.0, "right": 272.0, "width": 272.0},
        "surface": {"left": 292.0, "right": 2264.0, "width": 1972.0},
        "aside": {"left": 2284.0, "right": 2540.0, "width": 256.0},
    }
    reading.update(changes)
    return reading


def test_a_reading_of_a_page_that_uses_its_window_has_no_complaints() -> None:
    assert packed_left(sound()) == []


@pytest.mark.parametrize(
    ("what", "changes"),
    (
        ("the page stops short", {"body": {"left": 0.0, "right": 1760.0, "width": 1760.0}}),
        ("the rail floats in", {"rail": {"left": 94.0, "right": 366.0, "width": 272.0}}),
        ("the aside is inboard", {"aside": {"left": 1484.0, "right": 1740.0, "width": 256.0}}),
        ("the column stops", {"surface": {"left": 292.0, "right": 1105.0, "width": 813.0}}),
        ("a region is missing", {"aside": None}),
    ),
)
def test_each_way_the_page_can_waste_its_window_is_caught_by_name(what: str, changes: dict) -> None:
    """⛔ One planted reading per complaint: a check that only ever fires on all
    four together would pass a page with three of them."""
    assert packed_left(sound(**changes)), what
