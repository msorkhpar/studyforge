"""`W328`: the wide layout read against the WINDOW it is opened in.

⛔ **SPLIT OUT OF `test_chrome.py` AT A SEAM, AND THE SEAM IS THE SUBJECT**
(Ruling 261, and the same move `W326` made one row earlier). That module answers
*which regions `chrome.css` rules and where the column's one bound lives*;
`test_chrome_rail_rows.py` answers *does the rail's row span cover the page
skeleton*. ⭐ **The clauses below answer neither: every one of them is a claim
about the VIEWPORT** — the edge of it the rail sits on, the scroll of it the rail
survives, the height of it the rail is bounded by, and the share of it the
reading column now takes. ⚠️ **The ceiling is the other half of the reason and it
is stated rather than implied**: `test_chrome.py` was measured at 537 lines
against a 600 ceiling before this row, and R11's remedy is a split at a named
seam, never a trim.

## ⛔ The row is a user requirement, and it is quoted

> the left panel shou go all the way to the left side and be fixed. the context
> panel should be dynamic using more content of the page than longer scroll than
> needed.

⭐ **Two clauses, and they are kept separate here for the reason the brief keeps
them separate**: a rail pinned to the edge of a page that is still centred inside
a constant is only half of it, and a column that grew while the rail still
floated 94px in from the screen is the other half.

## ⚠️ What a declaration can and cannot settle

⛔ **Nothing here is a geometry reading.** Which side of the screen an element
lands on is exactly what no assertion over a stylesheet can see — that is `W98`'s
argument and it has not changed. ⭐ **These are the joins**: that both
declarations of a two-declaration decision are present, that the bound is the
palette's own token rather than a number typed twice, and that the wide shape is
still asked for by the page that carries the region. The browser arm is
`tests/visual/test_rail_fixed.py` and it is where the pixels are read.
"""

from __future__ import annotations

import re

import pytest

from tests.studyforge.render.pageassets.test_chrome import body, rules

#: The rail, spelled as `chrome.css` spells it.
RAIL = 'body > nav[aria-label="Containers"]'

#: The page in its two-column shape, spelled as `chrome.css` spells it.
WIDE_PAGE = 'body:has(nav[aria-label="Containers"])'

#: The reading surface inside that shape. ⚠️ Stage 3 ceilinged this element and
#: `W388` stage 4 took that bound away again — the shell carries the one ceiling
#: — so the selector is kept here to assert the wide shape does NOT rule it.
SURFACE = 'body:has(nav[aria-label="Containers"]) > main'


def wide_part() -> str:
    """Everything `chrome.css` declares inside its one width threshold.

    ⛔ Read by brace-matching from the `@media` rule rather than by a regular
    expression over the whole file: the clauses below are about what the WIDE
    shape says, and a reading that swept up the narrow rules would answer about
    a layout nobody asked it about.
    """
    text = body()
    start = re.search(r"@media\s*\(min-width:[^)]*\)\s*\{", text)
    assert start, "the chrome part declares no width threshold, so there is no wide shape"
    depth, index = 1, start.end()
    while depth and index < len(text):
        depth += {"{": 1, "}": -1}.get(text[index], 0)
        index += 1
    assert depth == 0, "the width threshold is never closed"
    return text[start.end() : index - 1]


def wide_rule_for(selector: str) -> str:
    """The declarations the wide shape gives `selector`, asserted to exist."""
    found = [
        block.strip()
        for each, block in re.findall(r"([^{}]+)\{([^{}]*)\}", wide_part())
        if each.strip() == selector
    ]
    assert len(found) == 1, f"the wide shape carries {len(found)} rules for {selector}, not one"
    return found[0]


# --- clause 1: flush against the viewport's left edge -----------------------


def test_the_wide_page_centres_its_shell_instead_of_pinning_it_to_one_edge():
    # ⛔ **`W388` STAGE 4 REVERSES THIS CLAUSE, and the reversal is the row.**
    # `W326` zeroed the left margin so the rail would sit on the window's left
    # edge; with a ceiling above it that is a page pinned LEFT, and the user read
    # the result on their own window as *"the paragraph texts are not using the
    # full width"* — every spare pixel was on one side. ⭐ The shell is centred
    # now: the inset is HALF of whatever the window has past the ceiling, and the
    # `max(0px, …)` floor is what keeps the rail on the window's own edge at
    # every width below it. ⚠️ Written out rather than left to `margin-inline:
    # auto` because the page with NO rail has to take the same inset and is
    # bounded by something else — `test_chrome_page_start.py` holds the two
    # equal. ⛔ Where the rail sits INSIDE the shell is the gutter clause below
    # and `test_reading_width.py`'s geometry, not this one.
    declarations = wide_rule_for(WIDE_PAGE)
    found = re.search(r"margin-left:\s*([^;]+);", declarations)
    assert found, f"the wide page sets no left margin at all: {declarations}"
    inset = found.group(1).strip()
    assert inset != "0", (
        "the wide page still pins itself to the left edge, which is the shape "
        f"the user read as a dead band down the right: {declarations}"
    )
    assert inset.startswith("max(0px,") and "var(--page-max)" in inset and "/ 2" in inset, (
        "the shell's left inset is not half of what the window has past the "
        f"palette's own ceiling, floored at nothing: {inset!r}"
    )


def test_the_wide_page_gives_up_the_left_gutter_as_well_as_the_left_margin():
    # ⚠️ **Two different insets, and zeroing one leaves the other.**
    # `reading.css` puts `padding: 0 var(--gutter)` on every `body`, which is
    # inside `body`'s own box under `box-sizing: border-box` — so a page with no
    # left margin still starts its first track one gutter in. ⭐ The RIGHT gutter
    # is deliberately untouched: the reading column keeps its air.
    declarations = wide_rule_for(WIDE_PAGE)
    assert re.search(r"padding-left:\s*0\s*;", declarations), (
        f"the wide page keeps its left gutter, so the rail is inset by one: {declarations}"
    )
    assert not re.search(r"padding(-right)?:\s*0[\s;]", declarations), (
        "the wide page zeroes its right gutter too, so the reading column runs "
        f"into the edge of the screen: {declarations}"
    )


# --- clause 1: and fixed ----------------------------------------------------


def test_the_rail_is_stuck_to_the_top_of_the_window_and_names_the_edge_it_sticks_to():
    # ⛔ **`position: sticky` with no inset does nothing at all** — an offset is
    # what tells it which edge to stop at — so the two are asserted together.
    # ⚠️ Sticky and not `fixed`: a fixed rail leaves the grid, and the reading
    # column would lay out underneath it rather than beside it.
    declarations = wide_rule_for(RAIL)
    assert re.search(r"position:\s*sticky\s*;", declarations), (
        f"the rail scrolls away with the page: {declarations}"
    )
    assert re.search(r"\btop:\s*0\s*;", declarations), (
        f"the rail is sticky against no edge, which is a no-op: {declarations}"
    )
    assert not re.search(r"position:\s*fixed\s*;", declarations), (
        "a fixed rail leaves the grid, so the reading column no longer clears it"
    )


def test_the_sticky_rail_still_spans_the_rows_that_give_it_somewhere_to_travel():
    # ⛔ **`W326`'s span is what makes this row possible and the join is asserted
    # rather than remembered.** A grid item's containing block is its grid AREA,
    # and sticky cannot travel outside its containing block — so a rail placed in
    # one row would stick within that row and move by nothing. ⭐ `W325/3` said
    # exactly that, and it is DATED by the span rather than refuted.
    # ⚠️ `test_chrome_rail_rows.py` owns the span's NUMBER; this owns the fact
    # that the two declarations are in the same rule.
    declarations = wide_rule_for(RAIL)
    assert re.search(r"grid-row:\s*1\s*/\s*span\s+\d+\s*;", declarations), (
        "the sticky rail is placed in a single grid row, so it has nowhere to "
        f"travel and does not move: {declarations}"
    )


# --- clause 1: a rail taller than the window scrolls itself -----------------


@pytest.mark.parametrize(
    ("declaration", "without_it"),
    (
        (r"max-height:\s*100vh\s*;", "the rail runs off the bottom of the window"),
        (r"overflow-y:\s*auto\s*;", "the part of the rail past the fold is unreachable"),
    ),
)
def test_a_rail_taller_than_the_window_scrolls_itself(declaration, without_it):
    # ⛔ **ONE DECISION, TWO DECLARATIONS, AND NEITHER IS ANY USE ALONE.** The
    # height without the overflow CLIPS the course list; the overflow without the
    # height never applies, because nothing bounds the box. ⚠️ A rail that no
    # longer scrolls with the page is exactly the thing that makes this
    # mandatory: before this row a reader reached the last container by scrolling
    # the page, and there is no page scroll to reach it with now.
    declarations = wide_rule_for(RAIL)
    assert re.search(declaration, declarations), f"{without_it}: {declarations}"


def test_the_rail_keeps_a_place_in_its_area_rather_than_being_stretched_down_it():
    # ⚠️ `align-self: start` and `max-height` are NOT the same declaration said
    # twice: the first says where in its area the rail sits, the second says how
    # much of the window it may take. ⛔ A rail without the first draws its border
    # to the foot of the page with the course list stranded at the top of it.
    assert re.search(r"align-self:\s*start\s*;", wide_rule_for(RAIL))


def test_the_rail_meets_the_edge_with_neither_a_border_nor_a_rounded_corner_on_it():
    # ⭐ The region is a CARD everywhere else — `border: 1px solid var(--rule)`
    # and a 10px radius — and a bordered, rounded edge sitting at x=0 reads as a
    # card touching the screen rather than as a rail running down it. ⛔ Only the
    # two LEFT corners are squared, by their logical names, so the number `10px`
    # is not written a second time to be kept in step with the first.
    declarations = wide_rule_for(RAIL)
    assert re.search(r"border-left:\s*0\s*;", declarations), declarations
    assert re.search(r"border-start-start-radius:\s*0\s*;", declarations), declarations
    assert re.search(r"border-end-start-radius:\s*0\s*;", declarations), declarations
    assert "10px" not in declarations, (
        "the radius is restated here, so the card's own corner and this one have "
        f"to be kept in step by hand: {declarations}"
    )


# --- clause 2: the reading column is a function of the viewport -------------


def test_the_reading_columns_track_is_a_share_of_the_viewport_and_not_a_constant():
    # ⛔ **The user's second clause, and the defect it names.** The track shipped
    # as `minmax(0, calc(var(--measure) + 2 * var(--gutter)))` — a constant — so
    # the page resolved one width and centred itself inside any screen wider than
    # it. ⭐ `1fr` is what is LEFT of the viewport once the rail and the gutters
    # are taken off it, which is a function of the window and not of the face.
    # ⚠️ `minmax(0, …)` stays: it is what keeps a wide code block from pushing
    # the track past its share.
    track = wide_rule_for(WIDE_PAGE)
    found = re.search(r"grid-template-columns:\s*([^;]+);", track)
    assert found, f"the wide page declares no tracks: {track}"
    columns = found.group(1)
    assert "var(--rail)" in columns, f"the rail track is not the palette's own token: {columns}"
    assert re.search(r"minmax\(\s*0\s*,\s*1fr\s*\)", columns), (
        f"the reading column is a stated width rather than a share of the window: {columns}"
    )
    assert "var(--measure)" not in columns, (
        "the reading column is still sized by the prose measure, so it is the "
        f"same width on a laptop and on a desktop: {columns}"
    )


def test_the_wide_page_is_ceilinged_at_the_palettes_own_token():
    # ⛔ **`W388` stage 4: the ceiling is back on the shell**, because a shell
    # that centres has to have something to centre at. Stage 3 released it
    # (`none`) and bounded `> main` instead, which cured the pin and opened the
    # other failure — the three tracks grew with the screen without limit and
    # the user read *"the width is too wide"*.
    #
    # ⚠️ **The TOKEN is asserted, not a number.** A literal here would be a
    # second place to change the ceiling and the argument for its value —
    # measured from the first corpus's own code blocks — lives beside the
    # declaration in `palette.css`.
    declarations = wide_rule_for(WIDE_PAGE)
    found = re.search(r"max-width:\s*([^;]+);", declarations)
    assert found, (
        "the wide page states no max-width at all, so it grows with any screen "
        f"and only the narrow shape's own bound is left to disagree: {declarations}"
    )
    bound = found.group(1).strip()
    assert bound == "var(--page-max)", (
        f"the shell's ceiling is not the palette's own token, unmixed: {bound!r}"
    )


def test_the_reading_surface_declares_no_second_ceiling_of_its_own():
    # ⛔ **ONE CEILING, IN ONE PLACE.** Stage 3's bound on
    # `body:has(…) > main` was the whole ceiling while the shell was released;
    # with the shell held at `--page-max` the surface is always the shell less
    # the rail, the aside and three gutters, so the same token repeated there
    # could never bite. ⚠️ A declaration that cannot bite is worse than none: it
    # is a second place a reader would go to move the ceiling, and moving it
    # there would do nothing.
    ruled = [selector.strip() for selector, _ in re.findall(r"([^{}]+)\{([^{}]*)\}", wide_part())]
    assert SURFACE not in ruled, (
        f"the wide shape still rules {SURFACE}, so there are two ceilings to find"
    )
    assert len(re.findall(r"max-width:", wide_part())) == 1, (
        "the wide shape declares more than one max-width, so the page's ceiling "
        f"is not the only one a reader has to reason about: {wide_part()}"
    )


def test_the_running_measure_is_still_the_only_thing_bounding_prose():
    # ⚠️ **"Use more of the page" is NOT "remove the measure from prose."** The
    # measure is a COUNTED number with a bound above it (`palette.css`, and
    # since `W388` stage 4 it is `80ch` laying about 105 characters); a column
    # with no cap at all lays 230 on a wide screen. ⭐ What widened is the
    # half `reading.css` calls *"scanned rather than read"* — the figure, the
    # table and the code block — and that is a consequence of the track, not a
    # rule written here. ⛔ So the wide shape must not mention the measure at all.
    assert "var(--measure)" not in wide_part(), (
        "the wide shape re-decides the prose measure, which `reading.css` owns"
    )


def test_the_whole_of_this_row_lives_under_the_one_threshold_the_file_declares():
    # ⛔ **The narrow shape is not touched by any of it**, and that is a clause
    # rather than an accident: a phone gets the card above the reading surface,
    # a page with its gutters, and no sticky anything. ⚠️ The browser arm reads
    # the threshold back out of this file, so a second one here would leave it
    # judging one of two layouts twice — asserted in `test_chrome.py`, from the
    # other side. This asserts the other half: every declaration this row added
    # is inside it.
    outside = body().replace(wide_part(), "")
    for declaration in ("position: sticky", "max-height: 100vh", "overflow-y: auto", "1fr"):
        assert declaration not in outside, (
            f"{declaration!r} is declared outside the width threshold, so the "
            "narrow page gets the wide shape's behaviour"
        )


def test_the_wide_shape_is_still_asked_for_by_the_page_that_carries_the_region():
    # ⛔ Re-taken rather than assumed. The root index carries no
    # rail — its own body IS the tree — so a wide shape declared unconditionally
    # would give that page an empty `17rem` column down its left AND, now, strip
    # the left gutter off a page that has nothing to put there.
    # ⚠️ The inset test is anchored on the terminating `;` deliberately:
    # `margin-left: 0.4rem` on the nested lists starts with the same characters,
    # and a substring match would read the outline's indent as a page layout.
    laid_out = [
        selector
        for selector, block in rules()
        if "grid-template" in block or re.search(r"(margin|padding)-left:\s*0\s*;", block)
    ]
    assert laid_out, "nothing in this part lays the page out at all"
    assert all(":has(" in selector for selector in laid_out), (
        f"the wide shape is declared for pages that carry no rail: {laid_out}"
    )
