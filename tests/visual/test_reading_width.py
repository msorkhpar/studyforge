"""`W388`: one shape that works on every display, read at five widths.

⛔ **SPLIT OUT OF `test_reading_room.py` AT A SEAM, AND THE SEAM IS THE SUBJECT**
(Ruling 261). That module answers *is this a page somebody can read for hours* —
the palette's contrast bands, the theme control, the rail on the first page, the
transport across the content, the length of a line. ⭐ **Every clause here
answers one different question instead: does the page use the WINDOW**, read at
five widths rather than at the one wide viewport that module opens. ⚠️ The other
half of the reason is stated rather than implied: `test_reading_room.py` was
measured at 531 lines against R11's 600 before this stage, and R11's remedy is a
split at a named seam, never a trim.

## ⛔ Three shapes, two of them read and rejected BY THE USER

> Still the paragraph texts are not using the full width for some reason.

⭐ **Stage 2's shape, measured:** the shell was ceilinged at `110rem` and PINNED
LEFT (`margin-left: 0`), so at 2560px the rail, the reading column and the aside
were packed into the left two thirds and the last 820px of the screen was empty.

> right now the width is too wide. Find a common ground for different displays.
> maybe if the display is too big having the menu and content in the middle by
> forcing a max width or something.

⭐ **Stage 3's shape:** the ceiling came off the shell entirely. That cured the
dead band and opened the opposite failure — the three tracks grew with the screen
with nothing to stop them, and the open room between a capped paragraph and the
outline grew with them.

⛔ **Stage 4's shape, and it is ONE shape rather than a rule per display:** the
shell is bounded at `--page-max` AND centred. Below the ceiling the margins
resolve to nothing and the page fills the window as stage 3's did; above it the
shell holds that width with EQUAL margins either side. ⚠️ **Equal is the whole
clause** — a dead band is spare room that is all on one side, so a shape whose
margins are equal at every width cannot have one.

## ⚠️ Why five widths and why the ceiling is read off the page

⛔ **A clause taken at one viewport settles nothing here**: the packed-left shape
was correct at 1280 and 1440 and wrong at 1920 and 2560, and the unbounded shape
is correct at every width below the ceiling and wrong above it. ⭐ 3840 joins the
four stage 3 used, because it is the width where an unbounded shell is most
obviously unbounded. ⛔ **The ceiling itself is read back through a probe on
`--page-max`**, never typed here: a palette that moves the ceiling moves every
clause in this module with it.
"""

from __future__ import annotations

import pytest

from tests.visual import site
from tests.visual.page import NARROW, WIDE, OpenPage
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

#: The five window widths this row is settled at, in CSS pixels. ⛔ **1280 and
#: 1440 are here because the pinned shape PASSED at both** — its ceiling was
#: 1760px, so a reading taken at either one would have called it correct. ⭐ 1920
#: and 2560 are the two the user's own screen sits between, and 3840 is where an
#: unbounded shell is most obviously unbounded.
WIDTHS = (1280, 1440, 1920, 2560, 3840)

#: The page's height, taken from the harness's wide viewport so this module
#: cannot disagree with the rest of the suite about how tall a window is.
HEIGHT = WIDE[1]

#: The two shapes the user read and rejected, as inline declarations on `body`.
#: ⛔ **Planted inline rather than on a damaged tree**, because what is under
#: test is the laid-out page and not the stylesheet — and inline is the one place
#: that beats the wide shape's own rule.
PINNED_LEFT = "document.body.style.maxWidth = '110rem'; document.body.style.marginLeft = '0px';"
UNBOUNDED = "document.body.style.maxWidth = 'none';"

#: Every box these clauses compare, plus the three scalars the arithmetic needs —
#: the window's own width, the gutter the layout sets and the ceiling the palette
#: declares. ⛔ The last two are READ OFF THE PAGE through a probe rather than
#: written here as numbers of pixels, so a palette that changes either changes
#: this reading with it.
BOXES = (
    """
(() => {
  const at = sel => { const el = document.querySelector(sel); if (!el) return null;
    const b = el.getBoundingClientRect();
    return {left: b.left, right: b.right, top: b.top, bottom: b.bottom, width: b.width}; };
  const resolve = token => {
    const probe = document.createElement('div');
    probe.style.cssText = 'width: ' + token + '; position: absolute; visibility: hidden';
    document.body.appendChild(probe);
    const width = probe.getBoundingClientRect().width;
    probe.remove();
    return width; };
  return {body: at('body'), rail: at('<rail>'), surface: at('<surface>'),
          aside: at('<outline>') || at('<about>'),
          gutter: resolve('var(--gutter)'), ceiling: resolve('var(--page-max)'),
          window: window.innerWidth};
})()
""".replace("<rail>", RAIL)
    .replace("<surface>", SURFACE)
    .replace("<outline>", OUTLINE)
    .replace("<about>", ABOUT)
)


def wasting_the_window(reading: dict) -> list[str]:
    """Every way this reading fails the stage's shape, named one by one.

    ⛔ **The user's two sentences as arithmetic.** Five things have to hold
    together and any one of them alone has a passing shape that is not the
    repair: a shell that centres but keeps growing, a shell that stops growing
    but keeps all its spare room on one side, a centred shell with its rail
    floating inside it, or one whose reading column stops short of the outline.

    ⚠️ A missing region is a complaint and never a silent pass — a page with no
    aside cannot be judged by clauses about where the aside is.
    """
    window, gutter, ceiling = reading["window"], reading["gutter"], reading["ceiling"]
    body, rail, surface, aside = (
        reading["body"],
        reading["rail"],
        reading["surface"],
        reading["aside"],
    )
    if body is None or rail is None or surface is None or aside is None:
        return ["the reading is missing a region, so nothing here can be judged"]
    if not ceiling > 0:
        return ["the palette declares no --page-max, so there is no shape to judge"]
    complaints = []
    wanted = min(window, ceiling)
    if abs(body["width"] - wanted) > TOUCHING:
        complaints.append(
            f"the shell is {body['width']:.2f}px in a {window:.2f}px window against a "
            f"ceiling of {ceiling:.2f}px, so it is neither filling the window nor "
            "holding the ceiling"
        )
    left, right = body["left"], window - body["right"]
    if abs(left - right) > TOUCHING:
        complaints.append(
            f"the shell has {left:.2f}px of room on its left and {right:.2f}px on its "
            "right, so the spare width is a dead band on one side rather than a margin"
        )
    if rail["left"] - body["left"] > TOUCHING:
        complaints.append(
            f"the rail starts {rail['left'] - body['left']:.2f}px in from the shell's "
            "own left edge, so the reader's menu is not the edge of the page"
        )
    if body["right"] - aside["right"] > gutter + TOUCHING:
        complaints.append(
            f"the aside ends {body['right'] - aside['right']:.2f}px short of the shell's "
            f"right edge, against a gutter of {gutter:.2f}px"
        )
    if aside["left"] - surface["right"] > gutter + TOUCHING:
        complaints.append(
            f"the reading column ends {aside['left'] - surface['right']:.2f}px before the "
            f"aside, against a gutter of {gutter:.2f}px, so it is not taking the slack"
        )
    return complaints


def read(open_page: OpenPage, url: str, width: int, plant: str = "") -> dict:
    """Open one page at one width, plant a shape on it, and read its boxes back."""
    open_page.resize(width, HEIGHT)
    open_page.open(url)
    if plant:
        open_page.evaluate(plant)
    return dict(open_page.evaluate(BOXES))  # type: ignore[arg-type]


# --- the clause, at every width -------------------------------------------


@pytest.mark.parametrize("width", WIDTHS)
@pytest.mark.parametrize("case", (UNIT_PAGE, INDEX_PAGE))
def test_the_shell_fills_the_window_or_centres_at_its_ceiling(
    open_page: OpenPage, built_site: site.Site, case: str, width: int
) -> None:
    """⛔ The stage in one reading: no dead band, at any of the five widths."""
    complaints = wasting_the_window(read(open_page, built_site.url(case), width))

    assert not complaints, f"at {width}px the {case} page: " + "; ".join(complaints)


@pytest.mark.parametrize("width", (1920, 2560, 3840))
def test_the_shape_the_user_read_as_a_dead_band_is_caught(
    open_page: OpenPage, built_site: site.Site, width: int
) -> None:
    """⭐ Both ways, with stage 2's pin put back on top of stage 4's ceiling.

    ⚠️ The ceiling alone was never the defect — the PIN was — so the control
    plants the pin and leaves the ceiling where this stage put it.
    """
    complaints = wasting_the_window(read(open_page, built_site.url(UNIT_PAGE), width, PINNED_LEFT))

    assert complaints, (
        f"at {width}px the left-pinned shell leaves this reading with nothing to say, "
        "so it cannot tell the shape the user rejected from the repaired one"
    )


@pytest.mark.parametrize("width", (1920, 2560, 3840))
def test_the_shape_the_user_read_as_too_wide_is_caught(
    open_page: OpenPage, built_site: site.Site, width: int
) -> None:
    """⭐ Both ways, the other rejected shape: the shell with its ceiling released.

    ⛔ **This is what stage 3 shipped**, and it passed every clause that stage
    wrote, because those clauses asked only whether the page spanned the window.
    ⚠️ A reading that cannot tell *centred at a ceiling* from *as wide as the
    glass* would let this stage ship the shape it was opened to replace.
    """
    complaints = wasting_the_window(read(open_page, built_site.url(UNIT_PAGE), width, UNBOUNDED))

    assert complaints, (
        f"at {width}px the unbounded shell leaves this reading with nothing to say, "
        "so this stage's shape and the one before it are the same clause"
    )


@pytest.mark.parametrize("plant", (PINNED_LEFT, UNBOUNDED))
def test_neither_rejected_shape_is_caught_at_a_window_it_happens_to_fit(
    open_page: OpenPage, built_site: site.Site, plant: str
) -> None:
    """⛔ The other half of the control: BOTH rejected shapes pass at 1280.

    ⚠️ This is why `WIDTHS` has five entries and not one. Below the ceiling the
    pinned shell, the unbounded shell and this stage's shell are the SAME
    LAYOUT — which is exactly how each shipped shape got its green readings.
    """
    assert not wasting_the_window(read(open_page, built_site.url(UNIT_PAGE), 1280, plant)), (
        "a rejected shape is already caught at 1280px, so the wide widths above "
        "are not what makes this stage's reading work"
    )


# --- the cap, argued from the line it lays out at each of the widths --------


#: A column with no cap left on it at all. ⛔ **Far past the bound on purpose.**
#: ⚠️ Neighbouring caps differ by one or two characters, and the SAME cap lays
#: out a different count on this host and in the pinned image (`W388` stage 3,
#: measured) — so a control a couple of characters over the bound would be red in
#: one environment and green in the other. ⭐ `200ch` is wider than the reading
#: column at every width here, so what it lays out is the column itself: about
#: 140 characters, in both.
AN_UNCAPPED_COLUMN = "200ch"


@pytest.mark.parametrize("width", WIDTHS)
def test_a_line_of_prose_stays_inside_the_band_at_every_width(
    open_page: OpenPage, built_site: site.Site, width: int
) -> None:
    """⛔ The cap is ARGUED FROM CHARACTERS PER LINE, so it is read as characters.

    ⚠️ **At every width, not at one.** A cap is only visible above the window
    where the column reaches it: at 1280 the column is narrower than the cap and
    the line runs short of it, and the same declaration at 1920 and above is what
    decides whether the widened page is readable.
    """
    open_page.resize(width, HEIGHT)
    open_page.open(built_site.url(UNIT_PAGE))
    longest = int(open_page.evaluate(LONGEST_PROSE_LINE))  # type: ignore[arg-type]

    assert SHORTEST_LINE <= longest <= LONGEST_LINE, (
        f"a line of prose runs to {longest} characters at a {width}px window, "
        f"outside {SHORTEST_LINE}–{LONGEST_LINE}"
    )


@pytest.mark.parametrize("width", (1920, 2560, 3840))
def test_a_column_with_no_cap_on_it_is_caught_by_the_same_count(
    open_page: OpenPage, built_site: site.Site, width: int
) -> None:
    """⭐ Both ways: the shell widening is not licence for any cap at all.

    ⚠️ **And the shell's ceiling is what makes this bounded rather than absurd.**
    With the ceiling released this reading would grow with the screen; held at
    `--page-max` the uncapped column is the surface, which is why the count here
    is about the same at all three widths instead of running away at the widest.
    """
    open_page.resize(width, HEIGHT)
    open_page.open(built_site.url(UNIT_PAGE))
    open_page.evaluate(
        f"document.documentElement.style.setProperty('--measure', '{AN_UNCAPPED_COLUMN}')"
    )
    longest = int(open_page.evaluate(LONGEST_PROSE_LINE))  # type: ignore[arg-type]

    assert longest > LONGEST_LINE, (
        f"an uncapped column still lays out {longest} characters at a {width}px "
        "window, so this reading cannot tell a comfortable line from a punishing one"
    )


# --- the arithmetic itself, on planted readings ----------------------------


def sound(**changes: object) -> dict:
    """A reading of this stage's shape at 2560, with `changes` applied to it.

    ⛔ The shell is 1760px — the ceiling — centred in a 2560px window, so there
    are 400px either side; the rail is on the shell's left edge and the aside one
    gutter in from its right.
    """
    reading = {
        "window": 2560.0,
        "gutter": 20.0,
        "ceiling": 1760.0,
        "body": {"left": 400.0, "right": 2160.0, "width": 1760.0},
        "rail": {"left": 400.0, "right": 672.0, "width": 272.0},
        "surface": {"left": 692.0, "right": 1864.0, "width": 1172.0},
        "aside": {"left": 1884.0, "right": 2140.0, "width": 256.0},
    }
    reading.update(changes)
    return reading


def test_a_reading_of_this_stages_shape_has_no_complaints() -> None:
    assert wasting_the_window(sound()) == []


def test_a_window_under_the_ceiling_is_the_shell_filling_it() -> None:
    """⛔ The other side of `min(window, ceiling)`: below the ceiling, no margins.

    ⚠️ A predicate that only ever knew the centred case would refuse the page
    every reader with a laptop actually sees.
    """
    assert (
        wasting_the_window(
            sound(
                window=1280.0,
                body={"left": 0.0, "right": 1280.0, "width": 1280.0},
                rail={"left": 0.0, "right": 272.0, "width": 272.0},
                surface={"left": 292.0, "right": 984.0, "width": 692.0},
                aside={"left": 1004.0, "right": 1260.0, "width": 256.0},
            )
        )
        == []
    )


@pytest.mark.parametrize(
    ("what", "changes"),
    (
        (
            "the shell is pinned left",
            {
                "body": {"left": 0.0, "right": 1760.0, "width": 1760.0},
                "rail": {"left": 0.0, "right": 272.0, "width": 272.0},
                "surface": {"left": 292.0, "right": 1464.0, "width": 1172.0},
                "aside": {"left": 1484.0, "right": 1740.0, "width": 256.0},
            },
        ),
        (
            "the shell is unbounded",
            {
                "body": {"left": 0.0, "right": 2560.0, "width": 2560.0},
                "rail": {"left": 0.0, "right": 272.0, "width": 272.0},
                "surface": {"left": 292.0, "right": 2264.0, "width": 1972.0},
                "aside": {"left": 2284.0, "right": 2540.0, "width": 256.0},
            },
        ),
        ("the shell stops short of its own ceiling", {"ceiling": 1920.0}),
        ("the rail floats in", {"rail": {"left": 494.0, "right": 766.0, "width": 272.0}}),
        ("the aside is inboard", {"aside": {"left": 1084.0, "right": 1340.0, "width": 256.0}}),
        ("the column stops", {"surface": {"left": 692.0, "right": 1505.0, "width": 813.0}}),
        ("a region is missing", {"aside": None}),
        ("the palette declares no ceiling", {"ceiling": 0.0}),
    ),
)
def test_each_way_the_page_can_waste_its_window_is_caught_by_name(what: str, changes: dict) -> None:
    """⛔ One planted reading per complaint: a check that only ever fired on all
    of them together would pass a page with all but one."""
    assert wasting_the_window(sound(**changes)), what


# --- `W447`: a code block in a disclosure is as wide as one in the flow ------


#: Every width the code-figure clause is read at: the five above, and the narrow
#: shape below the rail's threshold. ⛔ **The mismatch is invisible at 720, 1280
#: and 1440**, where the reading column is no wider than `--measure` — so a
#: reading taken only at the harness's default viewport would call the capped
#: disclosure correct, which is how it shipped. ⭐ The control below is read at
#: the three widths where the column is wider than the measure.
CODE_WIDTHS = (NARROW[0], *WIDTHS)

#: A worked solution, placed on the fixture page and opened, then both figures'
#: widths read back. ⛔ **No fixture corpus holds a code figure inside a
#: disclosure**, so the reading builds the practice template's own shape —
#: `details.disclosure > figure.code`, which `render/page/practice.py` emits as
#: *"Show a worked solution"* — out of the page's OWN disclosure and a copy of
#: the page's OWN flow figure. ⭐ What is under test is the stylesheet laying
#: that shape out, and every byte of the stylesheet is the built one.
SOLUTION_AND_FLOW = """
(() => {
  const flow = [...document.querySelectorAll('main figure.code')].find(f => !f.closest('details'));
  const disclosure = document.querySelector('main details.disclosure');
  if (!flow || !disclosure) return null;
  const solution = flow.cloneNode(true);
  disclosure.appendChild(solution);
  disclosure.open = true;
  return {solution: solution.getBoundingClientRect().width,
          flow: flow.getBoundingClientRect().width};
})()
"""

#: The rule `W447` removed, planted back as a page style: the disclosure held to
#: the prose measure, which is what the user read as a narrower solution.
MEASURED_DISCLOSURE = (
    "(() => { const s = document.createElement('style');"
    " s.textContent = 'details.disclosure { max-width: var(--measure); }';"
    " document.head.appendChild(s); })()"
)


def code_widths(open_page: OpenPage, url: str, width: int, plant: str = "") -> dict:
    """Open one page at one width, plant a rule on it, and read both figures."""
    open_page.resize(width, HEIGHT)
    open_page.open(url)
    if plant:
        open_page.evaluate(plant)
    reading = open_page.evaluate(SOLUTION_AND_FLOW)
    assert reading is not None, (
        "the fixture page has no flow code figure or no disclosure, so there is nothing to compare"
    )
    return dict(reading)  # type: ignore[arg-type]


@pytest.mark.parametrize("width", CODE_WIDTHS)
def test_a_code_block_in_a_disclosure_is_as_wide_as_one_in_the_flow(
    open_page: OpenPage, built_site: site.Site, width: int
) -> None:
    """⛔ The user's report as a reading: *"the size of code block … for the
    solution does not match with the rest of the code blocks"*."""
    reading = code_widths(open_page, built_site.url(UNIT_PAGE), width)

    assert abs(reading["solution"] - reading["flow"]) <= TOUCHING, (
        f"at {width}px a code figure inside a disclosure is {reading['solution']:.2f}px "
        f"wide and one in the flow is {reading['flow']:.2f}px"
    )


@pytest.mark.parametrize("width", (1920, 2560, 3840))
def test_a_disclosure_held_to_the_measure_is_caught(
    open_page: OpenPage, built_site: site.Site, width: int
) -> None:
    """⭐ Both ways: the shipped rule, planted back, is a mismatch this reads."""
    reading = code_widths(open_page, built_site.url(UNIT_PAGE), width, MEASURED_DISCLOSURE)

    assert reading["flow"] - reading["solution"] > TOUCHING, (
        f"at {width}px the measured disclosure reads {reading['solution']:.2f}px against "
        f"{reading['flow']:.2f}px, so this reading cannot see the defect the user reported"
    )
