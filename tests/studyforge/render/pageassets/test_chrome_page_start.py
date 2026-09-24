"""`W333`: the page WITHOUT a rail starts where the page WITH one starts.

⛔ **SPLIT OUT AT A SEAM, AND THE SEAM IS THE SUBJECT** (Ruling 261, the move
`W326` and `W328` each made before it). `test_chrome.py` answers *which regions
`chrome.css` rules and where the column's one bound lives*;
`test_chrome_rail_rows.py` answers *does the rail's span cover the page
skeleton*; `test_chrome_viewport.py` answers *what the wide shape says about the
WINDOW*. ⭐ **Every clause below answers a fourth question and none of those
three**: *do the file's TWO page shapes agree about where a page begins* — which
is a claim about a pair of rules rather than about either one of them.

## ⛔ The defect, and it is two rules disagreeing

⚠️ `W328` made the two-column page flush left and wide; the one-column page —
the root index, whose own body IS the tree — kept the centred, measure-derived
cap the column section declares. ⛔ **Neither is wrong on its own. Together they
are a site whose layout moves when the reader clicks**, and that is `W328/7`.

## ⚠️ What a declaration can and cannot settle

⛔ **Nothing here is a geometry reading.** Where an element lands is what no
assertion over a stylesheet can see (`W98`). ⭐ **These are the joins**: that the
two shapes agree about the left margin, that the one-column page did NOT inherit
the two insets that belong to the rail, that the rule is conditioned on the same
region selector the rail's own rules name, and that all of it lives under the one
threshold this file declares. ⭐ **The browser arm is
`tests/visual/test_page_start.py` and it is where the pixels are read.**

## ⛔ `W328`'s and `W326`'s modules are re-taken, never edited

⚠️ Re-read against later rules, never rewritten: `test_chrome_viewport.py` and
`test_chrome_rail_rows.py` are run at this tip and not touched; the clauses here are
additions beside them.
"""

from __future__ import annotations

import re

import pytest

from tests.studyforge.render.pageassets.test_chrome import body, rules

#: The region whose presence tells the two shapes apart, spelled as `chrome.css`
#: spells it. ⛔ **Read back out of the file rather than trusted**:
#: `test_the_two_shapes_name_one_region_between_them` asserts this string is what
#: both shapes are conditioned on, so a renamed region reds a check here rather
#: than leaving one rule matching nothing.
REGION = 'nav[aria-label="Containers"]'

#: The page in its two-column shape, and the page in its one-column shape, as
#: selectors. ⛔ **The second is the whole of this row's product change.**
WITH_RAIL = f"body:has({REGION})"
WITHOUT_RAIL = f"body:not(:has({REGION}))"


def wide_part() -> str:
    """Everything `chrome.css` declares inside its one width threshold.

    ⛔ Read by brace-matching from the `@media` rule rather than by a regular
    expression over the whole file, for `test_chrome_viewport.wide_part`'s
    reason: a reading that swept up the narrow rules would answer about a layout
    nobody asked it about. ⚠️ Spelled again here rather than imported, because
    importing it would make this module's verdict depend on `W328`'s module
    staying unedited — and a clause that fails for a reason outside its own
    subject is not a clause.
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
    """The declarations the wide shape gives `selector`, asserted to exist exactly once."""
    found = [
        block.strip()
        for each, block in re.findall(r"([^{}]+)\{([^{}]*)\}", wide_part())
        if each.strip() == selector
    ]
    assert len(found) == 1, f"the wide shape carries {len(found)} rules for {selector}, not one"
    return found[0]


def left_margin_of(selector: str) -> str:
    """What the wide shape sets `selector`'s left margin to, asserted to set one."""
    declarations = wide_rule_for(selector)
    found = re.search(r"margin-left:\s*([^;]+);", declarations)
    assert found, f"the wide shape sets no left margin on {selector}: {declarations}"
    return found.group(1).strip()


# --- the settling clause, as a join between the two shapes ------------------


def test_the_two_page_shapes_agree_about_the_pages_left_margin():
    # ⛔ **The row in one declaration.** `W328` zeroed the left margin on the
    # two-column page; the one-column page kept `margin-left: auto` from the
    # column section, so on a wide screen the index floated in the middle of the
    # window while a unit page sat against its left edge. ⭐ **Asserted as a
    # COMPARISON between the two rules and never against a typed value**: a file
    # that moved both to some third margin still passes, and a file that moves
    # one of them reds.
    assert left_margin_of(WITHOUT_RAIL) == left_margin_of(WITH_RAIL), (
        "the two page shapes give the page different left margins, so the layout "
        "moves when a reader clicks from a page with no rail into one with a rail"
    )


def test_the_right_margin_is_left_alone_so_the_page_is_left_aligned_and_not_stretched():
    # ⚠️ **Flush left is `margin-left` GIVEN UP and `margin-right` KEPT.** Zeroing
    # both would pin the page to both edges, and the measure-derived cap above
    # would then never bite — a different layout wearing this row's name.
    declarations = wide_rule_for(WITHOUT_RAIL)
    assert not re.search(r"margin-right:\s*0\s*;", declarations), (
        "the one-column page zeroes its right margin too, so it is pinned to "
        f"both edges rather than aligned to one: {declarations}"
    )


# --- and what the one-column page did NOT take from the two-column one ------


@pytest.mark.parametrize(
    ("declaration", "why"),
    (
        (
            "padding-left",
            "the one-column page gives up its left gutter, so its masthead runs "
            "into the edge of the screen — the rail is what earns that inset, and "
            "this page has no rail",
        ),
        (
            "grid-template-columns",
            "the one-column page declares a second track, so the page that "
            "carries no rail reserves an empty column for one",
        ),
        (
            "display",
            "the one-column page is laid out as a grid, which is the two-column "
            "shape arriving on the page that has nothing to put in its first track",
        ),
        (
            "max-width",
            "the one-column page re-decides its own ceiling here, which is the "
            "reading measure question and is not this row's to answer",
        ),
    ),
)
def test_the_one_column_page_takes_only_the_margin_and_none_of_the_rest(declaration, why):
    # ⛔ **The refusal is the argument, so it is asserted rather than written in
    # prose.** Three shapes were open for the index and two of them are refused
    # here: giving it the rail's gutterless edge (its text would touch the
    # screen), and giving it the rail's empty track so its masthead lines up with
    # a unit page's (the index's own content would then jump by a rail's width as
    # the reader widened the window — this row's defect moved from the click to
    # the resize). ⚠️ `max-width` is refused for a different reason: the bound is
    # the open question the user owns, and a bound moved here would answer it.
    assert declaration not in wide_rule_for(WITHOUT_RAIL), why


# --- the join: one region tells the two shapes apart ------------------------


def test_the_two_shapes_name_one_region_between_them():
    # ⛔ **Both shapes are conditioned on the SAME spelling of the region**, so a
    # renamed `aria-label` reds this check rather than leaving the file with one
    # rule that matches every page and one that matches none. ⭐ That is the
    # failure mode a pair of complementary selectors has and a single selector
    # does not.
    conditioned = sorted(
        selector
        for selector, _ in rules()
        if ":has(" in selector and selector in (WITH_RAIL, WITHOUT_RAIL)
    )
    assert conditioned == sorted((WITH_RAIL, WITHOUT_RAIL)), (
        "the file does not carry exactly one rule for each of the two page "
        f"shapes, spelled against {REGION}: {conditioned}"
    )


def test_the_one_column_shape_is_asked_for_by_the_ABSENCE_of_the_region():
    # ⚠️ **Read the sense of the condition, not only that there is one.**
    # `test_chrome_viewport.py` asserts every rule that lays the page out names
    # `:has(` — which `:not(:has(…))` satisfies while meaning the opposite. ⛔ So
    # this asserts the sense: the rule that moves the one-column page is negated,
    # and the rule that lays out the two-column page is not.
    assert WITHOUT_RAIL.startswith("body:not(:has("), WITHOUT_RAIL
    assert not WITH_RAIL.startswith("body:not("), WITH_RAIL
    assert wide_rule_for(WITHOUT_RAIL), "the negated shape carries no rule at all"


# --- the narrow shape is untouched ------------------------------------------


def test_the_whole_of_this_row_lives_under_the_one_threshold_the_file_declares():
    # ⛔ **Below the threshold there is one shape and it must STAY one.** A page
    # narrower than its own cap already sits at the window's left edge, because
    # `margin-left: auto` resolves to zero when there is no room to centre in —
    # so a rule written outside the threshold would change nothing at a phone's
    # width and would silently un-centre the one-column page at the widths
    # between its cap and the threshold, which no clause here asked for.
    assert WITHOUT_RAIL not in body().replace(wide_part(), ""), (
        f"{WITHOUT_RAIL} is declared outside the width threshold, so the "
        "one-column page changes shape below it too"
    )


def test_the_narrow_shape_still_centres_the_page_it_has_room_to_centre():
    # ⚠️ **What this row removed above the threshold is still declared below
    # it**, and that is the clause rather than an accident: the column section's
    # `body` rule is what every page gets at every width, and a row that had
    # deleted `margin-left: auto` there would have changed the one shape the file
    # has below its threshold.
    column = [block for selector, block in rules() if selector == "body"]
    assert len(column) == 1, f"the column section carries {len(column)} rules for `body`, not one"
    assert re.search(r"margin-left:\s*auto\s*;", column[0]), (
        f"the column section no longer centres the page below the threshold: {column[0]}"
    )


# --- no token is minted -----------------------------------------------------


def test_this_row_mints_no_token_and_states_no_bound_of_its_own():
    # ⛔ Settling clause 4, and it survives `W388` stage 4 intact. ⭐ The rule
    # this row adds still declares ONE property. ⚠️ Its value is no longer the
    # constant `0` — the two-column page it has to agree with is centred under a
    # ceiling now, so the shared inset is half of whatever the window has past
    # that ceiling — but the ceiling is `palette.css`'s OWN token, READ here and
    # minted nowhere: a row that painted a `--something` of its own would be a
    # second place to reason about where a page starts.
    declarations = [each.strip() for each in wide_rule_for(WITHOUT_RAIL).split(";") if each.strip()]
    assert len(declarations) == 1 and declarations[0].startswith("margin-left:"), (
        f"the one-column page's wide rule declares more than the margin: {declarations}"
    )
    assert not re.search(r"--[a-z-]+\s*:", wide_rule_for(WITHOUT_RAIL)), (
        "this row paints a custom property of its own"
    )
    assert set(re.findall(r"var\((--[a-z-]+)\)", wide_rule_for(WITHOUT_RAIL))) <= {"--page-max"}, (
        "the one-column page reads a token other than the ceiling the "
        f"two-column page is bounded by: {wide_rule_for(WITHOUT_RAIL)}"
    )
