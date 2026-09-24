"""`W326`: the rail's row span, read against the page skeleton it has to cover.

⛔ **SPLIT OUT OF `test_chrome.py` AT A SEAM, AND THE SEAM IS NAMED** (Ruling
261). That module's SUBJECT is `chrome.css` and the regions the tree emits; the
check below has no single subject — it is a claim about TWO artifacts agreeing,
the stylesheet's placement of the rail and the number of top-level positions
`page.html` puts in `<body>`. ⭐ Neither file can be read alone to answer it,
which is why it did not grow onto a module that answers for one of them.

## ⛔ What shipped, and why a number is written in a stylesheet at all

`W325` placed the rail at `grid-row: 1` — the MASTHEAD's row — and a grid row is
as tall as its tallest item, so the masthead's row became as tall as the whole
course list and every later element of the reading column began at the rail's
bottom edge. ⭐ **A reader opened a unit, saw the title, and then the height of
the rail in blank page.**

⚠️ **`1 / -1` IS NOT THE REPAIR, MEASURED.** A negative row line counts back from
the end of the EXPLICIT grid, and `chrome.css` declares columns only — every row
is implicit — so row line `-1` IS row line `1` and the placement collapses to the
one-row span that carries the defect. ⛔ Nothing in CSS spells *every implicit
row*, so the span is a stated number, and a stated number in a stylesheet is only
as good as what joins it to the thing it has to cover. This module is that join.
"""

from __future__ import annotations

import re

import pytest

from studyforge.render import templates
from tests.studyforge.render.pageassets.test_chrome import rule_for

#: The rail, spelled as `chrome.css` spells it.
RAIL = 'body > nav[aria-label="Containers"]'


def skeleton_body_positions() -> list[str]:
    """Every top-level position `page.html` puts inside `<body>`, in document order.

    ⭐ A position is an ELEMENT or a `${slot}`, counted at body depth only: the
    `<h1>` inside the masthead and the `${body}` inside `<main>` are their
    parent's business and can never be a grid row of their own. ⛔ Measured off
    the skeleton rather than listed here, for the reason `SKELETON_SLOTS` is
    asserted equal to it: a slot added to the page is how regions 5, 6, 7 and 10
    arrived, and not one of them arrived by anybody editing a test first.
    """
    markup = templates.template("page.html").template
    inside = markup.split("<body>", 1)[1].split("</body>", 1)[0]
    positions: list[str] = []
    depth = 0
    for token in re.finditer(r"<(/?)([a-zA-Z][a-zA-Z0-9-]*)[^>]*>|\$\{([a-zA-Z_]+)\}", inside):
        closing, tag, slot = token.group(1), token.group(2), token.group(3)
        if slot is not None:
            if depth == 0:
                positions.append(slot)
        elif closing:
            depth -= 1
        else:
            if depth == 0:
                positions.append(tag)
            depth += 1
    return positions


def rail_row_span(declarations: str) -> int | None:
    """How many rows `declarations` places the rail across, or `None` for no span.

    ⛔ `grid-row: 1 / -1` READS AS NO SPAN HERE, DELIBERATELY. It is the repair
    the office that measured the defect named, and it leaves the layout exactly
    as it was — so a reader who reaches for it again meets a red check rather
    than a page that still opens on blank.
    """
    found = re.search(r"grid-row:\s*1\s*/\s*span\s+(\d+)\s*;", declarations)
    return int(found.group(1)) if found else None


def test_the_rail_spans_every_row_the_page_skeleton_can_put_in_the_reading_column():
    # ⭐ The span is the skeleton's own count of top-level positions, so it covers
    # every row a page of this framework can have whatever that page carries —
    # and a slot added to `page.html` reds HERE rather than shipping a rail that
    # stops short of the page's last row and sizes it on the way past.
    positions = skeleton_body_positions()
    assert positions, "the skeleton puts nothing at body level, so this check judges nothing"
    placement = rule_for(RAIL)
    assert placement is not None, "nothing in the chrome part places the rail"
    span = rail_row_span(placement)
    assert span is not None, (
        "the rail is placed in a single grid row, so the masthead's row is as tall "
        f"as the whole course list: {placement}"
    )
    assert span == len(positions), (
        f"the rail spans {span} rows and `page.html` declares {len(positions)} top-level "
        f"positions ({positions}), so the span and the skeleton disagree"
    )


@pytest.mark.parametrize(
    "placement",
    ("grid-column: 1; grid-row: 1;", "grid-column: 1; grid-row: 1 / -1;"),
)
def test_that_check_refuses_both_placements_this_row_was_opened_over(placement):
    # ⛔ A check that has only ever seen the repaired file has not been
    # shown to notice the defect. ⚠️ BOTH literals here were shipped or proposed —
    # the first is what `W325` merged, the second is what was proposed to repair
    # it — and a real browser was asked which layout each produces before this
    # parametrisation was written. It is the same layout.
    assert rail_row_span(placement) is None


def test_the_skeletons_positions_are_read_and_not_a_list_kept_beside_it():
    # ⛔ The other half of the join, and it is what stops the count above going
    # stale in the quiet way: the positions are asserted to be the skeleton's
    # OWN, by name, so a slot renamed is a red check rather than a number that
    # still adds up. ⚠️ Every slot `page.html` declares at body level is a
    # placeholder of it — asserted as a subset, because `header`, `main` and
    # `script` are elements and are positions without being slots — and so is
    # the skip link, `a`, the first focusable element on every page (`W362`).
    slots = templates.placeholders("page.html")
    positions = set(skeleton_body_positions())
    assert positions & slots, "no position here is a slot of the skeleton, so this reads nothing"
    assert (positions - slots) <= {"a", "header", "main", "script"}, sorted(positions - slots)
