"""What the chrome part PAINTS, and the vocabulary it is not allowed to invent.

⛔ **SPLIT OUT OF `test_chrome.py` AT A SEAM, AND THE SEAM IS THE SUBJECT**
(R11). That module
answers *which regions this part rules and where the column's one bound lives*;
every clause below answers a different question — **is this region legible
without colour, which palette tokens does this part answer for, and does it
define any colour of its own**. ⭐ None of them reads a region table and none of
them reads a layout; they read the part's paint.

⚠️ **The size ceiling is the other half of the reason.** ⭐ **R11's remedy for a
module at its ceiling is a split at a named seam, never a trim.**

## ⭐ The helpers are IMPORTED from `test_chrome`, not re-derived

⚠️ `body()` and `declarations_reaching()` read the four files `CHROME_PARTS`
names, and that tuple is the definition of *the part read as one*. ⛔ A second
spelling of it here would be a second answer to *which files are the chrome
part*, and the day a fifth file joined it one of the two would go quietly stale
— which is exactly the listed-population defect this family of modules refuses. The
sibling modules `test_chrome_rail_rows.py` and `test_chrome_viewport.py` import
the same helpers for the same reason.
"""

from __future__ import annotations

import re

import pytest

from tests.studyforge.render.pageassets.test_chrome import body, declarations_reaching

#: Properties that tell a region apart from body text WITHOUT a colour. ⛔ A bar
#: told apart by colour alone is invisible to a reader who cannot see it.
NON_COLOUR_CUES = (
    "border-top",
    "display",
    "font-family",
    "font-size",
    "font-weight",
    "letter-spacing",
    "padding-top",
    "text-transform",
)

#: Four tokens defined in `palette.css` that no other part paints. ⭐ They are
#: this part's.
ONCE_OWNERLESS = ("--accent-soft", "--practice", "--practice-soft", "--surface-2")


# --- note (c): the bar is legible without reference to colour ---------------


def test_the_between_units_bar_is_told_apart_from_body_text_without_colour():
    # ⛔ The between-units bar must not be indistinguishable from body text.
    found = declarations_reaching('nav[aria-label="Between units"]')
    assert found, "the bar carries no declaration at all"
    cues = sorted(cue for cue in NON_COLOUR_CUES if re.search(rf"\b{cue}\s*:", found))
    assert len(cues) >= 3, (
        f"the bar is told apart by {cues}, which is not enough without colour — "
        f"a bar nobody can see is not a bar that passed"
    )


def test_the_bars_own_colour_is_not_what_carries_it():
    # ⭐ The control for the check above, run negatively: strip every colour
    # declaration and the cues must survive. A rule that said only `color:` would
    # pass the count above if `color` were ever added to the cue list.
    assert not any(cue in ("color", "background") for cue in NON_COLOUR_CUES)


# --- The four tokens no other part paints -----------------------------------


@pytest.mark.parametrize("token", ONCE_OWNERLESS)
def test_each_once_ownerless_palette_token_is_painted_here(token):
    # ⛔ A colour token defined in `palette.css` and painted by no stylesheet is
    # dead. ⭐ These are painted here, and
    # `test_the_unpainted_rows_are_derived_from_the_stylesheets_not_believed`
    # makes the ledger say which ground each one is read against.
    assert f"var({token})" in body(), f"{token} is still ownerless"


def test_this_part_defines_no_colour_and_no_measure_of_its_own():
    # ⚠️ `test_palette` asserts the first half over every authored part; this is
    # the same claim at this file, plus the half about measures — `palette.css`
    # calls itself the shared vocabulary for *"every colour, measure and font"*.
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(", body()), "a colour outside the palette"
    assert "--" not in body().split("var(")[0], "a token is DEFINED here rather than used"
