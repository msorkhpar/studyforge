"""Mirror of `tools/quality/board/contradiction.py` (R12) — Ruling 189(b)'s three readings.

⛔ **The PLANTED readings here are not invented: they are the MEASURED FAILURES,
replayed from their own bytes** — the population is in
`tools/tests/quality/board/support.py`, quoted with the ref each was taken at
(Ruling 97's standing rule).

⭐ **And a FOURTH rule, which is a REFUSAL rather than a contradiction** (`W111`):
⛔ **a `<!-- inflight -->` block the board DECLARED and the parser could not read.**
⚠️ **Its founding reading is the CTO's round-50 plant — two renamed column names,
`NONE FOUND, 0 rows`, three rules silently inapplicable, and the floor clean.**
"""

from __future__ import annotations

import pytest

from tests.support import repository_root
from tools.quality.board import (
    BOARD,
    RULE_DISAGREEMENT,
    RULE_INFLIGHT,
    RULE_UNOBSERVED,
    RULE_UNREADABLE,
    check_board,
)
from tools.quality.board.contradiction import (
    TERMINAL,
    locator_reading,
    observation_findings,
    observation_reading,
)
from tools.quality.board.observation import NOT_STARTED, STAND_INS, STARTED, read
from tools.tests.quality.board.support import (
    BIDIRECTIONAL,
    PLANT,
    RENAMED,
    THE_CHECKOUT_CELL,
    THREE_HUNDRED_AND_FIFTY,
    board,
    plant_a_contradiction,
    rules,
)

# --------------------------------------------------------------------------
# Reading 1 — LIVE, and the population is printed before any verdict
# --------------------------------------------------------------------------


def test_live_no_row_on_this_board_contradicts_itself() -> None:
    """⭐ The one-row contradiction is ABSENT on the live board, against a live population.

    ⛔ **Only `board-inflight` is asserted clean here, and the narrowness is
    deliberate**: a test that asserted *every* rule clean on the live tree would
    be pinning today's board, and the day the PO corrects a cell the test would
    go red for the tree being RIGHT (Ruling 190's shape). ⭐ `check_board`'s own
    live reading is `test_init.py`'s, which is where a board defect belongs.

    ⚠️ **THIS ARM IS VACUOUS AT ZERO STARTED ROWS AND IS NO LONGER SKIPPED FOR
    IT** (`W188`) — ⭐ the guard that makes the silence mean something is the next
    test, which runs at EVERY population including zero.
    """
    text = (repository_root() / BOARD).read_text(encoding="utf-8")
    assert [f for f in observation_findings(text) if f.rule == RULE_INFLIGHT] == []


def test_live_the_contradiction_rule_is_ARMED_at_WHATEVER_population() -> None:
    """⛔ `W188`: the moved exit code, so a pass needs BOTH the silence and the guard.

    ⚠️ **MEASURED at `35bf14e`, and it is why this test exists:** the live board's
    observation table carried rows and **`0` of them declaring a started state** —
    ⛔ **the state a register leaves at the END OF EVERY WAVE once it has closed
    everything** — so the arm above `pytest.skip`ped, and the live contradiction
    check was DISARMED at the exact moment the board is rewritten most heavily,
    re-arming only when the next wave dispatched.

    ⛔ **THE CURE IS NOT `assert the population is non-empty`.** ⚠️ `W147` measured
    that twice, once per table: `assert table.rows` and `assert schedule.rows`
    each went RED on a CORRECT board — a round that closes the last row and
    honestly records *nothing is in flight* — which is `W119`'s class. ⭐ **An
    empty in-flight table genuinely owes no contradiction check; what it does NOT
    excuse is a green that cannot tell an empty board from a broken reader.** So
    the contradiction is spliced into the LIVE board's own bytes and the rule
    must speak.

    ⭐ **Form-independent by construction**: the planted row is laid out from the
    board's OWN declaring header, so the register renaming, reordering or ADDING
    a column cannot silently defuse this guard — ⛔ and a declared block with no
    readable header raises instead of passing, because that is
    `board-unreadable`'s subject and is asserted on its own two tests down.
    """
    text = (repository_root() / BOARD).read_text(encoding="utf-8")
    planted = observation_findings(plant_a_contradiction(text))
    found = [f for f in planted if f.rule == RULE_INFLIGHT]
    assert len(found) == 1, (
        f"⛔ a started row naming no checkout and counting 0 ahead was spliced into "
        f"this board's own `<!-- inflight -->` block and `{RULE_INFLIGHT}` did not fire "
        f"exactly once. ⭐ Live population: {observation_reading(text)}"
    )
    assert PLANT in found[0].message, (
        "⛔ the finding must name the PLANTED row, or the guard is borrowing its pass "
        "from a real row of the live board"
    )


UNDECLARED = "declaring NO state this vocabulary carries"


def test_live_the_reading_TELLS_A_CLOSED_WAVE_APART_FROM_AN_UNREADABLE_STATE_CELL() -> None:
    """⛔ `W188`, the SIBLING: `0 declaring a started state` had two causes and named neither.

    ⚠️ **MEASURED at `35bf14e`: every row of the live observation table read
    `declared = None`** — the register writes `MERGED` in the State cell and the
    closed vocabulary carries `done`. ⛔ **So the reading that made the check skip
    was not *the wave is closed*; it was *no cell was understood*, and the two
    printed the same number.**

    ⭐ **The count is DERIVED here, never pinned** (Ruling 186): the register owns
    the board's form and the day it writes `done` this reads `0` without an edit.
    ⛔ **And it is PRINTED, NOT FLAGGED** — the register table asserts
    `undeclared == []` live (`test_register.py`) and the scheduled table asserts a
    state on every row (`test_scheduled.py`); ⚠️ **the observation table is the one
    of the three with NO such arm, and adding one today would go RED for the board
    being in a state its OWNER chose.** ⭐ That flag is the register's to ask for;
    the reading is this package's to owe.
    """
    text = (repository_root() / BOARD).read_text(encoding="utf-8")
    undeclared = sum(1 for row in read(text).rows if row.declared is None)
    assert f"{undeclared} {UNDECLARED}" in observation_reading(text)


def test_the_UNDECLARED_count_is_asserted_in_BOTH_directions() -> None:
    """⛔ R12: a cell the vocabulary carries must NOT be counted, and one it does not MUST be."""
    known = board("| `W42` | Dev | none | 0 | in flight |\n", delimited=True)
    unknown = board("| `W42` | Dev | none | 0 | ✅ **MERGED** `430363b` |\n", delimited=True)
    assert f"0 {UNDECLARED}" in observation_reading(known)
    assert f"1 {UNDECLARED}" in observation_reading(unknown)
    assert observation_findings(unknown) == [], (
        "⛔ PRINTED, NOT FLAGGED (Ruling 179) — a cell outside the vocabulary is the "
        "register's form to choose, and a rule firing on it would fire on correct work"
    )


def test_live_the_reading_NAMES_the_locator_the_blocks_and_the_stand_in() -> None:
    """⛔ Ruling 196(b): the printed locator name is not optional, and `W111` adds two counts.

    ⭐ **`CTO-49/4` and Ruling 185: an exemption narrows the POPULATION, by NAME** —
    ⚠️ **and `W111` is explicitly NOT a reason to drop it**, so the stand-in's name
    stays in the line every floor run prints.
    """
    reading = observation_reading((repository_root() / BOARD).read_text(encoding="utf-8"))
    assert "delimited" in reading
    assert "blocks declared, 0 unreadable" in reading
    assert "NONE FOUND" not in reading
    for name in STAND_INS:
        assert name in reading


def test_live_the_board_has_NO_UNREADABLE_block() -> None:
    """⭐ The live half of `W111`'s refusal, asserted where a board defect belongs."""
    text = (repository_root() / BOARD).read_text(encoding="utf-8")
    assert [f for f in observation_findings(text) if f.rule == RULE_UNREADABLE] == []


# --------------------------------------------------------------------------
# Reading 2 — PLANTED: the measured failures, from their own bytes
# --------------------------------------------------------------------------


def test_planted_a_DECLARED_BLOCK_THAT_DID_NOT_READ_is_a_FINDING(capsys: object) -> None:
    """⛔ `W111`: the plant that read `NONE FOUND, 0 rows` on a GREEN floor now fails.

    ⚠️ **MEASURED by the CTO at round 50, quoted at its reading:**

    ```text
    PLANTED: two column NAMES changed in the observation table header
      -> observations (NONE FOUND …): 0 rows     three rules silently inapplicable
      -> quality floor: clean, exit 0            corroborate: 0 of 0, exit 0
    ```

    ⭐ **It announced where it should have REFUSED**, and the markers alone did not
    change that: inside them the roles are still read from the header.
    """
    del capsys
    text = board(THREE_HUNDRED_AND_FIFTY, delimited=True, header=RENAMED)
    findings = observation_findings(text)
    assert rules(findings) == [RULE_UNREADABLE]
    assert findings[0].path == BOARD
    assert "DECLARED block that did not read is a FINDING" in findings[0].message
    assert "`W111`" in findings[0].message
    assert "rename, reorder, emphasise or prefix the columns freely" in findings[0].message
    assert "UNREADABLE at line" in observation_reading(text)


def test_planted_the_350_COMMIT_case_fires_on_both_rows() -> None:
    """⛔ `cae114e^`: two rows declaring a started state with `none` and `0`.

    ⭐ **Every git instrument read CORRECTLY for 350 commits** — `worktree list`
    saw no checkout because the work had FINISHED, and `--no-merged` saw nothing
    because it had MERGED — ⚠️ **and the board printed `Checkout: none` beside a
    started state the whole time.** ⛔ **Read DOWN A COLUMN, every instrument was
    right; read ACROSS THE ROW, the board refutes itself.**
    """
    findings = observation_findings(board(THREE_HUNDRED_AND_FIFTY, delimited=True))
    assert rules(findings) == [RULE_INFLIGHT, RULE_INFLIGHT]
    assert "W14" in findings[0].message and "W18" in findings[0].message
    assert "W27" in findings[1].message, "⛔ the `◐ in-review @ …` idiom declares in-review"
    assert all("CONTRADICTION PRINTED ON ONE ROW" in f.message for f in findings)


def test_planted_a_started_REGISTER_cell_that_no_observation_row_names() -> None:
    """⛔ The ABSENT half of the bidirectional failure, SYNTHESISED (Ruling 191(b)).

    ⚠️ **The live population is empty today**, because this board's recent practice
    leaves a dispatched row's register cell at `` `todo` `` — ⛔ **which is itself
    the departure that let `W95`'s staleness live in one table only.** ⭐ **Measured
    at `cae114e^` and `679a6c5^`, the register declared `in flight` for every
    dispatched row of rounds 37 and 38**, so this shape is the board's own and not
    a hypothetical.
    """
    register = "| W42 | a naming | Developer 2 | in flight — `fix/W42` | [d](rows/W42.md) |\n"
    findings = observation_findings(board(THE_CHECKOUT_CELL, register, delimited=True))
    assert rules(findings) == [RULE_UNOBSERVED]
    assert "W42" in findings[0].message
    assert "NO observation row" in findings[0].message


def test_planted_the_two_tables_of_ONE_FILE_disagree() -> None:
    """⛔ STARTED against FINISHED, which cannot both be true of one row.

    ⚠️ **This is the shape the board reaches the moment a row is closed in the
    register and the observation table is not re-taken** — ⭐ the 350-commit case's
    sibling, and the one cross-table pairing no convention explains.
    """
    register = "| W95 | a naming | Developer 2 | ✅ done — `cfe0e0c` | [record](a.md#w95) |\n"
    findings = observation_findings(board(THE_CHECKOUT_CELL, register, delimited=True))
    assert rules(findings) == [RULE_DISAGREEMENT]
    assert "W95" in findings[0].message and "done" in findings[0].message


def test_a_started_row_whose_register_cell_reads_todo_is_PRINTED_and_NOT_FLAGGED() -> None:
    """⛔ Ruling 179, and the plant that CONTRADICTED this rule's first predicate.

    ⚠️ **The first version of `board-disagreement` fired on any started-against-not-
    started pairing, and its first live reading hit `W95` — a row the PO had just
    dispatched correctly.** ⭐ **Measured at `7559398`: this board dispatches a row
    by naming it in the observation table and leaving its register cell at
    `` `todo` ``**, so the rule as first written flagged the convention rather than
    a defect.
    """
    register = "| W95 | a naming | Developer 2 | `todo` — before `SF-16` | [d](rows/W95.md) |\n"
    text = board(THE_CHECKOUT_CELL, register, delimited=True)
    assert observation_findings(text) == []
    assert "started here and `todo` in the register" in observation_reading(text)
    assert "Ruling 179): W95" in observation_reading(text)


def test_planted_the_CHECKOUT_CELL_case_is_a_PASS_and_that_is_the_constraint() -> None:
    """⭐ `7559398`: a checkout and `0` ahead is CORROBORATED, not a finding.

    ⛔ **This is the reading that stops the predicate being `ahead > 0`.** ⚠️ **A
    branch with no commit is not in `--no-merged` BY CONSTRUCTION** (Ruling 130),
    so a just-dispatched row passes on the `Checkout` cell alone — ⛔ **and a rule
    that flagged it would fire on two correct rows in its first wave**, which is
    Ruling 179's measured cost.
    """
    assert observation_findings(board(THE_CHECKOUT_CELL, delimited=True)) == []
    assert observation_findings(board(BIDIRECTIONAL, delimited=True)) == [], (
        "⛔ both cells CLAIM a checkout; a cell that LIES is corroborate.py's subject"
    )


@pytest.mark.parametrize("declared", sorted(STARTED))
def test_planted_EVERY_started_word_is_in_the_population(declared: str) -> None:
    """⛔ Ruling 48: parametrised over the DERIVATION, so an empty set SKIPS.

    ⭐ **`in-progress` is in this population and that is a DECISION**, not an
    oversight: the three words that mean *started and not finished* are admitted
    and ⚠️ **leaving one out would be the defect this row exists to close — a
    closed set with a hole in it.**
    """
    if not STARTED:
        pytest.skip("the started vocabulary is empty, so there is no population to read")
    row = f"| `W42` | Developer 2 | none | 0 | ⏳ **{declared}** — taken |\n"
    assert rules(observation_findings(board(row, delimited=True))) == [RULE_INFLIGHT]


def test_a_cell_that_counts_NO_commits_gets_a_DIFFERENT_MESSAGE_from_one_counting_zero() -> None:
    """⛔ *The board offered no reading* and *the board offered one that refutes it* differ."""
    none = observation_findings(board("| `W42` | Dev | none | — | in flight |\n", delimited=True))
    zero = observation_findings(board("| `W42` | Dev | none | 0 | in flight |\n", delimited=True))
    assert rules(none) == rules(zero) == [RULE_INFLIGHT]
    assert "counts no commit at all" in none[0].message
    assert "counts 0 commits ahead" in zero[0].message


# --------------------------------------------------------------------------
# Reading 3 — IMPOSSIBLE, and each must DIFFER from the pass
# --------------------------------------------------------------------------


def test_impossible_a_DECLARED_EMPTY_block_is_SILENT_and_DIFFERS_from_an_unreadable_one() -> None:
    """⛔ `W111` must not fire on a wave the PO closed correctly (Ruling 179).

    ⭐ **A declared block whose columns are declared and which carries no row is
    *nothing is in flight*** — ⚠️ **and its reading must DIFFER from the unreadable
    one, or the refusal would be a notice nobody reads twice.**
    """
    empty = board(delimited=True)
    unreadable = board(delimited=True, header=RENAMED)
    assert observation_findings(empty) == []
    assert rules(observation_findings(unreadable)) == [RULE_UNREADABLE]
    assert locator_reading(read(empty)) != locator_reading(read(unreadable))
    assert "0 unreadable" in locator_reading(read(empty))


def test_impossible_a_board_with_NO_MARKER_is_the_RAMP_and_is_not_a_finding() -> None:
    """⛔ R10's arbitrary roots: the floor runs over trees that are not this board.

    ⭐ **A board with no `<!-- inflight -->` block at all is the Ruling 196(b) ramp**,
    reported by the locator and NOT flagged — ⚠️ **because `check_board` must not fail
    a corpus repository for being a corpus repository.**
    """
    assert observation_findings(board(THREE_HUNDRED_AND_FIFTY)) != []
    assert rules(observation_findings(board(THREE_HUNDRED_AND_FIFTY))) == [
        RULE_INFLIGHT,
        RULE_INFLIGHT,
    ], "⛔ the RAMP still judges the rows it read; only the locator changed"
    assert observation_findings(board()) == []
    assert "Ruling 196(b) ramp" in locator_reading(read(board()))


@pytest.mark.parametrize("declared", sorted(NOT_STARTED))
def test_impossible_a_row_declaring_an_UNSTARTED_state_owes_no_carrier(declared: str) -> None:
    """⭐ The five excluded words, each excluded for a STATED reason."""
    row = f"| `W42` | Developer 2 | none | 0 | {declared} |\n"
    assert observation_findings(board(row, delimited=True)) == []


def test_TERMINAL_is_a_STRICT_SUBSET_of_NOT_STARTED_and_excludes_todo() -> None:
    """⚠️ `todo` is deliberately NOT terminal, and the reason is measured (Ruling 179)."""
    assert TERMINAL < NOT_STARTED
    assert "todo" not in TERMINAL
    assert "blocked" not in TERMINAL, (
        "blocked owes a named unblocking condition, which IS a carrier"
    )


def test_check_board_carries_the_FOUR_rules_and_the_messages_name_their_ruling() -> None:
    """⭐ The wiring, asserted rather than assumed: the rules reach the floor's check."""
    assert "189(b)" in (check_board.__doc__ or "")
    text = board(THREE_HUNDRED_AND_FIFTY, delimited=True)
    assert {f.rule for f in observation_findings(text)} == {RULE_INFLIGHT}
    assert all(f.path == BOARD for f in observation_findings(text))
    assert {RULE_INFLIGHT, RULE_UNOBSERVED, RULE_DISAGREEMENT, RULE_UNREADABLE} == {
        f"board-{name}" for name in ("inflight", "unobserved", "disagreement", "unreadable")
    }
