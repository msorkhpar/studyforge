"""Mirror of `tools/quality/board/observation.py` (R12) — the PARSER and its LOCATOR.

⛔ **The rules that judge these rows are `test_contradiction.py`'s**, which is the
`W96/3` seam split at by `W111`. ⭐ **This module asserts what the board DECLARED and
what the parser could READ of it** — and the new reading is the third case the old
locator could not distinguish: ⚠️ **a DECLARED block that did not parse, which used
to be indistinguishable from a board with nothing in flight.**
"""

from __future__ import annotations

import pytest

from tests.support import repository_root
from tools.quality.board.observation import (
    ABSENT,
    DELIMITED,
    INFLIGHT_CLOSE,
    INFLIGHT_OPEN,
    NONE_FOUND,
    NOT_STARTED,
    RAMP,
    STAND_INS,
    STARTED,
    asserted,
    observations,
    read,
)
from tools.quality.board.register import BOARD, STATES
from tools.tests.quality.board.support import (
    HEADER,
    RENAMED,
    THE_CHECKOUT_CELL,
    THREE_HUNDRED_AND_FIFTY,
    board,
)

# --------------------------------------------------------------------------
# Reading 1 — LIVE, and the board's own declaration is what answers
# --------------------------------------------------------------------------


def test_live_the_observation_population_is_INHABITED_and_DELIMITED() -> None:
    """⛔ Ruling 191(a): print the population BEFORE the verdict, and `0` is missing.

    ⭐ **Ruling 196(b)'s ramp has EXPIRED on this board** — the `<!-- inflight -->`
    markers landed in the PO's round-40 edit — ⚠️ **so the live reading asserts the
    DELIMITED locator rather than merely *some* locator**, which is what makes the
    ramp's removal visible instead of assumed.
    """
    text = (repository_root() / BOARD).read_text(encoding="utf-8")
    table = read(text)
    assert table.rows, f"⛔ born vacuous: no observation table on the live board — {table}"
    assert table.locator == DELIMITED
    assert table.declared >= 1
    assert table.unreadable == (), "⛔ a DECLARED block this parser cannot read is `W111`'s finding"
    assert observations(text) == list(table.rows)


def test_live_the_stand_in_is_named_rather_than_excluded_in_silence() -> None:
    """⛔ `CTO-49/4` and Ruling 185: an exemption narrows the POPULATION, by NAME.

    ⚠️ **`W73`'s carrier is a checkout in a repository this one does not own**, so
    no framework-side instrument can observe it without reading across the seam
    (R20, Ruling 151). ⭐ **`W111` is explicitly NOT a reason to drop it** — a refusal
    arm is a reason to RE-READ the exclusion list, never to widen the predicate.
    """
    text = (repository_root() / BOARD).read_text(encoding="utf-8")
    for name in STAND_INS:
        assert name not in [identifier for _n, identifier, _w in asserted(text)]


# --------------------------------------------------------------------------
# Reading 2 — PLANTED: the locator, and `W111`'s refusal
# --------------------------------------------------------------------------


def test_planted_a_DELIMITED_block_whose_header_DECLARES_NO_ROLE_is_UNREADABLE() -> None:
    """⛔ `W111`, and the CTO's round-50 plant is the founding reading.

    ⚠️ **PLANTED then: two column NAMES changed in the observation table header.**
    ⛔ **The reading was `observations (NONE FOUND …): 0 rows` on a GREEN floor** —
    three rules silently inapplicable, `corroborate: 0 of 0, exit 0` — ⭐ **so the
    instrument announced where it should have refused.**

    ⛔ **And the markers ALONE did not fix it**: inside them the roles are still
    taken from `_columns`, which returns `None` for a header declaring none of the
    three roles. ⭐ **The delimiter makes the refusal POSSIBLE; this is what makes it
    HAPPEN.**
    """
    text = board(THREE_HUNDRED_AND_FIFTY, delimited=True, header=RENAMED)
    table = read(text)
    assert table.declared == 1
    assert table.locator == DELIMITED, "⛔ the BOARD declared it, so the locator is delimited"
    assert table.rows == (), "the header declares no role, so no row could be read"
    assert len(table.unreadable) == 1
    assert text.split("\n")[table.unreadable[0] - 1].strip() == INFLIGHT_OPEN


def test_planted_the_SAME_renamed_header_OUTSIDE_the_markers_is_simply_not_a_table() -> None:
    """⛔ The refusal is about the DECLARATION, not about the bytes of the header.

    ⚠️ **An ordinary table whose header declares none of the roles is not an
    observation table and never was** — ⭐ which is why this is a fourth rule on the
    delimited case rather than a widening of the recogniser. ⛔ **Widening it would
    rebuild the inferred boundary that made `board-duplicate` fire on its own
    author.**
    """
    table = read(board(THREE_HUNDRED_AND_FIFTY, header=RENAMED))
    assert table.locator == NONE_FOUND
    assert (table.rows, table.unreadable, table.declared) == ((), (), 0)


def test_planted_a_board_that_DECLARES_A_BLOCK_and_closes_it_EMPTY_is_READ() -> None:
    """⭐ The third case, and it is the one that must stay a PASS.

    ⚠️ **Between waves the table is declared, its columns are declared, and it
    carries no row** — ⛔ **which is *nothing is in flight*, a real answer.** ⭐ **It
    must DIFFER from the unreadable case, or `W111`'s refusal would fire every time
    the PO closed a wave correctly** (Ruling 179).
    """
    table = read(board(delimited=True))
    assert table.declared == 1
    assert table.locator == DELIMITED
    assert (table.rows, table.unreadable) == ((), ())


def test_planted_an_UNCLOSED_block_is_still_judged_at_end_of_file() -> None:
    """⛔ A missing close marker must not make a DECLARED block vanish.

    ⚠️ **That would be the `NONE FOUND` answer to a declared table all over again**,
    reached by deleting one line instead of by renaming two columns.
    """
    text = f"# Board\n\n{INFLIGHT_OPEN}\n{RENAMED}| `W42` | Dev | x | 0 | in flight |\n"
    table = read(text)
    assert (table.declared, table.rows, len(table.unreadable)) == (1, (), 1)
    assert read(text.replace(RENAMED, HEADER)).unreadable == (), "a declared header reads"


def test_planted_the_RAMP_survives_only_for_a_board_with_NO_MARKER_AT_ALL() -> None:
    """⛔ `W111`'s record: the header branch is kept for a board with NO markers, and SAYS SO.

    ⭐ **The second form is the one to prefer if this instrument is ever pointed at a
    corpus repository's own board** (R10's arbitrary roots) — ⚠️ **but a board that
    HAS the delimiters and fails to declare its columns must not fall back to it, or
    the ramp is permanent.**
    """
    ramp = read(board(THREE_HUNDRED_AND_FIFTY))
    assert ramp.locator == RAMP
    assert len(ramp.rows) == 2
    assert all(not row.delimited for row in ramp.rows)
    marked = read(board(THREE_HUNDRED_AND_FIFTY, delimited=True))
    assert marked.locator == DELIMITED
    assert all(row.delimited for row in marked.rows)


def test_planted_a_DECLARED_board_does_not_read_a_table_OUTSIDE_its_markers() -> None:
    """⛔ The locator is chosen by the BOARD, not by what happened to parse.

    ⚠️ **The old parser scanned every table on the file and would have answered from
    a second one when the declared block was unreadable** — ⭐ **which is exactly how
    a ramp becomes permanent: it keeps working, so nobody notices the declaration
    failed.**
    """
    declared = board(THE_CHECKOUT_CELL, delimited=True, header=RENAMED)
    outside = declared + "\n" + HEADER + "| `W42` | Dev | none | 0 | in flight |\n"
    table = read(outside)
    assert table.rows == (), "⛔ the table outside the markers may not answer for the one inside"
    assert len(table.unreadable) == 1


#: ⛔ **What the board can AUTHOR, each as a `(header, row)` pair so the row
#: follows its own header.** ⚠️ **The first version of this population passed four
#: shapes and FAILED on the reordered one — and the fixture was wrong, not the
#: recogniser: it reordered the header and left the row in the old order, so
#: `state` read the checkout cell.** ⭐ **That is the plant contradicting its
#: author, and it is why a reordered column is tested as a PAIR.**
AUTHORABLE = [
    (
        "| Row | Owner | Checkout | Commits ahead | State |",
        "| `W42` | Dev | none | 0 | in flight |",
    ),
    (
        "| **Row** | **Owner** | **Checkout** | **Commits ahead** | **State** |",
        "| `W42` | Dev | none | 0 | **in flight** |",
    ),
    ("| Row | Owner | Checkout | Ahead | State |", "| `W42` | Dev | — | 0 | in-review |"),
    ("| Row | Owner | Checkout | Commits | Status |", "| `W42` | Dev | none | 0 | in-progress |"),
    (
        "| Row | Owner | State | Checkout | Commits ahead |",
        "| `W42` | Dev | in flight | none | 0 |",
    ),
    (
        "| Task | Owner | ⭐ Checkout | Commits ahead | State |",
        "| `W42` + `W43` | Dev | none | **+0** | ⏳ **in flight** — taken |",
    ),
]


@pytest.mark.parametrize(("header", "row"), AUTHORABLE)
def test_ruling_192_what_the_board_can_AUTHOR_is_a_SUBSET_of_what_this_RECOGNISES(
    header: str, row: str
) -> None:
    """⛔ Ruling 192: a census of what the tree EMITS owes the population it can AUTHOR.

    ⛔ **`authorable ⊆ recognisable`, never the equality** — ⚠️ **the shape the board
    writes and the recogniser cannot see is how `test_chrome.py` went blind to
    `nav[aria-label=…]`.** ⭐ **So the roles are read FROM THE HEADER**: emphasis, a
    renamed column, a reordered column and an emoji are all shapes this board
    authors elsewhere, and none of them moves the reading.

    ⛔ **This is also what `W111` must NOT become** — a rule pinning the column
    NAMES. ⭐ **Every one of these SIX headers is delimited here and reads `0`
    unreadable**, so the refusal fires on a header declaring NO role and never on one
    declaring them differently.
    """
    table = read(board(row + "\n", delimited=True, header=header + "\n|---|---|---|---|---|\n"))
    assert table.unreadable == (), (header, row)
    assert len(table.rows) == 1, (header, row)
    assert table.rows[0].started and not table.rows[0].observes_a_checkout


def test_a_cell_that_counts_NO_commits_is_not_a_cell_that_counts_ZERO() -> None:
    """⚠️ `—` declares no ahead observation; `0` declares one that refutes the row."""
    none = read(board("| `W42` | Dev | none | — | in flight |\n", delimited=True)).rows
    zero = read(board("| `W42` | Dev | none | 0 | in flight |\n", delimited=True)).rows
    assert none[0].commits is None
    assert zero[0].commits == 0


@pytest.mark.parametrize("absent", sorted(ABSENT - {""}))
def test_every_spelling_of_NO_CARRIER_reads_the_same_way(absent: str) -> None:
    """⛔ Ruling 140: the forbidden thing in a form the clause did not picture.

    ⚠️ **The clause pictured the word `none`.** ⭐ Every spelling of *no carrier*
    this board could reach for reads the same way, because the vocabulary is
    CLOSED and the cell is normalised before it is read.
    """
    row = f"| `W42` | Developer 2 | {absent} | 0 | in flight |\n"
    assert not read(board(row, delimited=True)).rows[0].observes_a_checkout


# --------------------------------------------------------------------------
# Reading 3 — IMPOSSIBLE, and each must DIFFER from the pass
# --------------------------------------------------------------------------


def test_impossible_a_board_with_no_observation_table_DIFFERS_from_every_other_answer() -> None:
    """⛔ `0 rows`, `NONE FOUND` and `UNREADABLE` are THREE answers, and silence is none.

    ⚠️ **A board whose observation table somebody deleted would otherwise read
    exactly like a board with nothing in flight** — ⭐ which is the false empty
    this project pays for twice over (check 3's own defect, `CTO-48/3`) — ⛔ **and
    `W111` adds the third: a DECLARED block that did not parse.**
    """
    readings = {
        "bare": read(board()),
        "declared and empty": read(board(delimited=True)),
        "declared and unreadable": read(board(delimited=True, header=RENAMED)),
        "ramp": read(board(THREE_HUNDRED_AND_FIFTY)),
    }
    assert readings["bare"].locator == NONE_FOUND
    assert readings["declared and empty"].locator == DELIMITED
    assert readings["ramp"].locator == RAMP
    signatures = {
        name: (table.locator, len(table.rows), len(table.unreadable))
        for name, table in readings.items()
    }
    assert len(set(signatures.values())) == len(signatures), signatures


def test_impossible_a_W_shaped_table_that_declares_no_OBSERVATION_columns() -> None:
    """⛔ The distant reading this must not move: `test_init.py`'s five-cell plant.

    ⚠️ **Ruling 190(b): adding a member to a derived population edits every
    distant test that iterates it.** ⭐ **The locator requires a HEADER that
    DECLARES a `Checkout` column and a commits-ahead column**, so an ordinary
    five-cell table — including the one `test_init.py` plants outside the register
    markers — is not an observation table and nothing here reads it.
    """
    ordinary = "| Order | Row | Why it is here | Placed |\n|---|---|---|---|\n"
    ordinary += "| 1 | `W96` | in flight, jumped `W74` | round 38 |\n"
    assert read(board() + ordinary).locator == NONE_FOUND


@pytest.mark.parametrize("declared", sorted(NOT_STARTED))
def test_a_row_declaring_an_UNSTARTED_state_is_read_and_is_not_started(declared: str) -> None:
    """⭐ The five excluded words, each excluded for a STATED reason."""
    row = f"| `W42` | Developer 2 | none | 0 | {declared} |\n"
    assert read(board(row, delimited=True)).rows[0].started is False


def test_the_two_sides_of_the_vocabulary_are_a_TOTAL_partition_of_STATES() -> None:
    """⛔ A closed set with a HOLE in it is the defect this row was nearly shipped with.

    ⭐ **Derived against `STATES` rather than listed**, so a tenth state word
    cannot join the board's vocabulary without somebody classifying it — ⚠️ and
    `NOT_STARTED` is DECLARED rather than subtracted, because a subtraction would
    have swallowed the new word in silence.
    """
    assert STARTED | NOT_STARTED == set(STATES)
    assert not STARTED & NOT_STARTED
    assert {word for word in STARTED if STATES[word]} == set(), "a started row is never closed"


def test_the_three_locator_names_are_DISTINCT_constants() -> None:
    """⛔ Ruling 196(b): the printed locator name is the whole of what keeps the ramp honest."""
    assert len({DELIMITED, RAMP, NONE_FOUND}) == 3
    assert INFLIGHT_OPEN != INFLIGHT_CLOSE
    assert INFLIGHT_CLOSE.startswith("<!-- /")
