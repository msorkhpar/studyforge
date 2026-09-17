"""Mirror of `tools/quality/ids.py` (R12) — ⛔ the grammar, asserted in BOTH spellings.

⛔ **Asserting only the form that already works is how this defect survived being
written down** (`W192`): the board used `+`, the handoff reader split on `,`, and
each was the other's undeclared form. ⭐ **So every spelling here is asserted
against EVERY reader of a multi-id cell, in one test, because the property the row
buys is AGREEMENT and no single-instrument test can hold it.**

⚠️ **The undeclared joiner is asserted too, and in the direction that matters:**
⛔ a form this grammar does not declare must never make a reader take the LAST id,
which is the defect one spelling further out that `W192` names as the thing this
must not become.
"""

from __future__ import annotations

import pytest

from tools.quality.board.observation import INFLIGHT_CLOSE, INFLIGHT_OPEN, observations
from tools.quality.board.register import identifiers
from tools.quality.handoffs import TASK_HANDOFF, declared_kind
from tools.quality.ids import ROW_ID, is_row_id, order, parts, row_ids

#: ⭐ The two spellings the grammar DECLARES, and the whole of it.
DECLARED = ["`W14` + `W18`", "`W14`, `W18`"]

#: ⛔ **The measured defect, at `35bf14e` and re-measured at `19c7224`**: this
#: spelling parsed as ONE id and took the LAST, so a cell naming two rows observed
#: the wrong one with no notice and exit `0`.
THE_COMMA_FORM = "`W14`, `W18`"


def inflight(subject: str) -> str:
    """A board whose DELIMITED observation table carries one row, with `subject`."""
    return (
        f"# board\n\n{INFLIGHT_OPEN}\n"
        "| Row | Owner | Checkout | Commits ahead | State |\n"
        "|---|---|---|---|---|\n"
        f"| {subject} | Developer 1 | `wt/dev1`, `fix/x` | 2 | in flight |\n"
        f"{INFLIGHT_CLOSE}\n"
    )


def kind(declaration: str) -> str:
    """A task handoff declaring `declaration` on its `**Kind:**` line."""
    return f"# t — handoff\n\n**Kind:** task handoff — {declaration}\n"


# --- the whole of `W192`: every reader of a multi-id cell reads the SAME ids ---


@pytest.mark.parametrize("cell", DECLARED)
def test_every_instrument_that_reads_a_multi_id_cell_reads_THE_SAME_TWO(cell):
    """⛔ Three readers, one grammar — the disagreement CLOSED rather than documented."""
    assert row_ids(cell) == ["W14", "W18"]
    assert identifiers(cell) == ["W14", "W18"]
    assert [row.ids for row in observations(inflight(cell))] == [("W14", "W18")]
    assert declared_kind(kind(cell)) == (TASK_HANDOFF, ["W14", "W18"], 3)


def test_and_the_two_declared_spellings_are_INDISTINGUISHABLE_to_every_one_of_them():
    """⭐ Ruling 124's form: the same two ids, named two ways, must not read apart."""
    first, second = DECLARED
    assert identifiers(first) == identifiers(second)
    assert observations(inflight(first))[0].ids == observations(inflight(second))[0].ids
    assert declared_kind(kind(first))[1] == declared_kind(kind(second))[1]


def test_the_comma_form_no_longer_takes_the_LAST_id():
    """⛔ The defect itself, at its own bytes: ONE id, and it was the LAST."""
    assert row_ids(THE_COMMA_FORM) != ["W18"]
    assert row_ids(THE_COMMA_FORM) == ["W14", "W18"]


# --- the grammar itself -------------------------------------------------------


def test_the_order_the_cell_writes_them_in_is_the_order_they_come_back_in():
    assert row_ids("`W18`, `W14`") == ["W18", "W14"]


def test_markup_is_not_part_of_an_id():
    assert row_ids("**W17** + `W19`") == ["W17", "W19"]
    assert parts("**ARCH**") == ["ARCH"]


def test_a_cell_naming_no_id_names_none():
    # ⛔ The header and the separator of every register table, which is what
    # makes *names an id* the test for whether a table row is a register row.
    assert row_ids("# | Row | Owner") == []
    assert row_ids("|---|---|") == []


# --- the undeclared joiner, in the direction that matters ---------------------


def test_an_UNDECLARED_joiner_never_makes_A_READER_TAKE_THE_LAST():
    """⛔ `W192`'s *what it must not become*: the same defect one spelling further out.

    ⭐ **The board's readers name EVERY id in such a cell** — the grammar reads
    more than it declares and never less — ⚠️ **and the direction is chosen: an
    id that is READ can be judged, and an id silently dropped cannot.**
    """
    assert row_ids("`W20` and `W21`") == ["W20", "W21"]
    assert observations(inflight("`W20` and `W21`"))[0].ids == ("W20", "W21")


def test_and_the_handoff_reader_REFUSES_that_part_BY_NAME_rather_than_splitting_it():
    """⭐ The other half: every part of a `**Kind:**` line CLAIMS to be a task id."""
    kinds, ids, _line = declared_kind(kind("W20 and W21"))
    assert (kinds, ids) == (TASK_HANDOFF, ["W20 and W21"])


def test_parts_KEEPS_what_row_ids_drops_so_a_refusal_can_name_it():
    assert parts("W20 and W21") == ["W20 and W21"]
    assert row_ids("NS-03") == [] and parts("NS-03") == ["NS-03"]


# --- `W181`: the SHAPE, stated where it is parsed ----------------------------


@pytest.mark.parametrize("planted", ["W20a", "w20", "W", "W-20", "WW20", "", "W 20", "N20"])
def test_the_parser_can_NEVER_return_an_id_outside_the_declared_shape(planted):
    """⛔ `W181`'s second clause: `int(id[1:])` downstream is safe BY A STATED PROPERTY.

    ⭐ **Asserted over planted garbage rather than over the live register**, because
    a live population that happens to be clean certifies nothing about the parser.
    """
    assert all(ROW_ID.fullmatch(found) for found in row_ids(planted))
    assert not is_row_id(planted)
    assert order(planted) is None


def test_and_a_real_row_id_orders_by_its_number():
    assert is_row_id("W181") and order("W181") == 181
    assert all(ROW_ID.fullmatch(found) for found in row_ids("W181, W192"))


def test_order_RETURNS_rather_than_RAISES_which_is_the_whole_of_W181():
    # ⛔ `int("20a")` raises, and it raised inside a FLOOR CHECK — so this is a
    # return value and never an exception, however the id was spelled.
    assert order("W20a") is None
    assert order("") is None
