"""Mirror of `tools/quality/board.py` (R12), and the instrument's three readings.

⛔ **Ruling 122: a clause naming an instrument is not final until its author has
RUN it, in BOTH directions, and recorded both readings.** ⭐ **Ruling 123 names
the three: LIVE, PLANTED and IMPOSSIBLE**, and all three are here as tests
rather than as a paragraph in a handoff, because a reading recorded in prose is
one nobody can re-take.

| Reading | What it asserts | Where |
|---|---|---|
| **live** | the real `BOARD.md` here is clean under **every** rule the check
  composes, the arms in the other modules included | `test_live_board_is_clean` |
| **planted** | each rule fires on a board built to break exactly it | the `test_planted_*` |
| **impossible** | a state the rule cannot reach reports nothing, and
  absence is not a pass | `test_impossible_*` |

## ⛔ What is NOT here, and it is a pointer rather than a deletion

⭐ **The three SIZE bounds are `test_bounds.py`'s**, and they moved there with the
code `W100`'s split took out of `tools/quality/board/__init__.py` — ⚠️ **Ruling 140's
plant and Ruling 149's negative control with them.** ⭐ **The observation table's four
rules are `test_contradiction.py`'s and `## Scheduled`'s is `test_scheduled.py`'s.**
⛔ **This module is the arm that stayed: the bijection, the states and the frames.**
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support import repository_root
from tools.quality.board import (
    BOARD,
    BOARD_NARRATIVE_CEILING,
    BOARD_ROW_CEILING,
    REGISTER_CLOSE,
    REGISTER_OPEN,
    ROW_FRAME,
    ROWS,
    RULE_DETAIL,
    RULE_DUPLICATE,
    RULE_FRAME,
    RULE_ORPHAN,
    RULE_STATE,
    STATES,
    board_state,
    check_board,
)

#: A minimal register: a header, a separator, one closed row and one live one.
#: ⛔ Written out rather than generated, so a reader can see what the check
#: reads without running it.
HEADER = "<!-- register -->\n| # | Row | Owner | State | Detail |\n|---|---|---|---|---|\n"
FOOTER = "<!-- /register -->\n"
CLOSED = "| W1 | a naming | PO | ✅ done — `abc1234` | [record](BOARD-ARCHIVE.md#w1) |\n"
LIVE = "| W2 | another naming | PO | `todo` | [rows/W2.md](rows/W2.md) |\n"


#: The frame every row file carries, and the fixtures carry it because the
#: live ones do — a fixture that skipped it would test a shape nothing ships.
def _row(name: str) -> str:
    return (
        f"# {name}\n\n⛔ **This file carries the ARGUMENT for board row `{name}` "
        f"and nothing else.**\n⭐ **Its naming, owner and state live once, in the "
        f"register in [`../BOARD.md`](../BOARD.md).**\n\nThe argument.\n"
    )


def _tree(tmp_path: Path, board: str, rows: tuple[str, ...] = ()) -> Path:
    (tmp_path / "docs" / "tasks").mkdir(parents=True, exist_ok=True)
    (tmp_path / BOARD).write_text(board, encoding="utf-8")
    if rows:
        (tmp_path / ROWS).mkdir()
        for name in rows:
            (tmp_path / ROWS / f"{name}.md").write_text(_row(name), encoding="utf-8")
    return tmp_path


def _rules(findings: list) -> list[str]:
    return sorted(finding.rule for finding in findings)


# --------------------------------------------------------------------------
# Reading 1 — LIVE
# --------------------------------------------------------------------------


def test_live_board_is_clean() -> None:
    """⭐ The real board in this repository passes every rule.

    ⛔ **This is the reading that makes the other two mean something.** A check
    proved only against fixtures is a check whose subject has never been
    measured — the shape `check_pointers` was scoped on, arriving here.
    """
    assert check_board(repository_root()) == []


def test_live_notice_names_both_ceilings_and_the_population() -> None:
    """⛔ Ruling 128: print the population in full before reducing it to a scalar."""
    line = board_state(repository_root())[0]
    assert line.startswith("board: ")
    assert "register rows" in line and "live" in line and "detail files" in line
    assert str(BOARD_NARRATIVE_CEILING) in line
    assert str(BOARD_ROW_CEILING) in line


def test_live_board_has_a_detail_file_for_every_live_row() -> None:
    """⭐ The bijection, stated as a number rather than as an absence."""
    line = board_state(repository_root())[0]
    live = int(line.split(" register rows, ")[1].split(" live")[0])
    files = int(line.split("live, ")[1].split(" detail files")[0])
    assert live == files


# --------------------------------------------------------------------------
# Reading 2 — PLANTED, one per rule
# --------------------------------------------------------------------------


def test_planted_live_row_with_no_detail_file(tmp_path: Path) -> None:
    root = _tree(tmp_path, HEADER + CLOSED + LIVE + FOOTER)
    assert _rules(check_board(root)) == [RULE_DETAIL]


def test_planted_detail_file_with_no_live_row(tmp_path: Path) -> None:
    root = _tree(tmp_path, HEADER + CLOSED + FOOTER, rows=("W1",))
    findings = check_board(root)
    assert _rules(findings) == [RULE_ORPHAN]
    assert "W1" in findings[0].message


def test_planted_duplicate_id(tmp_path: Path) -> None:
    root = _tree(tmp_path, HEADER + LIVE + LIVE + FOOTER, rows=("W2",))
    findings = check_board(root)
    assert _rules(findings) == [RULE_DUPLICATE]
    assert "ONE row" in findings[0].message


# ⛔ **THE THREE SIZE BOUNDS ARE `test_bounds.py`'s NOW**, and they MOVED with the code
# `W100`'s split took out of `tools/quality/board/__init__.py` — ⭐ **`board-narrative`,
# `board-row-width` and `board-size`, including Ruling 140's plant and Ruling 149's
# negative control.** ⚠️ **They were not copied: a reading with two homes is what this
# package's own instrument forbids one layer up.**


# --------------------------------------------------------------------------
# Reading 3 — IMPOSSIBLE
# --------------------------------------------------------------------------


def test_impossible_no_board_at_all(tmp_path: Path) -> None:
    """⛔ A tree with no board is CLEAN, and the notice says so out loud.

    ⚠️ **The floor runs over arbitrary roots** — a temp tree, a corpus
    repository — ⛔ **so a finding here would be asserting which repository you
    are in.** ⭐ **This is `check_knowledge_index`'s split, reused**: absence is
    reported through the notice channel and presence is enforced by a test that
    knows the answer should be yes.

    ⚠️ **`0 = 0` is not a pass** (Ruling 48), which is why the notice may not be
    silent — and it is not.
    """
    (tmp_path / "docs" / "tasks").mkdir(parents=True, exist_ok=True)
    assert check_board(tmp_path) == []
    assert "board: none" in board_state(tmp_path)[0]


def test_this_repository_has_a_board() -> None:
    """⛔ The enforcement half, and it lives here because only here is it true.

    ⭐ `test_impossible_no_board_at_all` says a missing board is not a floor
    failure anywhere; this says it is a build failure HERE.
    """
    assert (repository_root() / BOARD).is_file()
    assert (repository_root() / ROWS).is_dir()
    board = (repository_root() / BOARD).read_text(encoding="utf-8")
    assert REGISTER_OPEN in board and REGISTER_CLOSE in board


def test_a_W_shaped_table_outside_the_markers_is_not_the_register(tmp_path: Path) -> None:
    """⛔ The defect this check found in its own author, kept as a test.

    ⚠️ **An *In flight* table naming four rows was read as four DUPLICATE
    register rows** by the first version, which inferred the register from
    row shape. ⭐ **A board may hold many `W`-shaped tables; one of them
    says it is the register.**
    """
    elsewhere = "| W2 | in flight | Dev | none | +3 |\n"
    root = _tree(tmp_path, HEADER + LIVE + FOOTER + elsewhere, rows=("W2",))
    assert check_board(root) == []


def test_impossible_board_with_no_register_rows(tmp_path: Path) -> None:
    """⚠️ A board whose register is EMPTY is clean, and the notice says so.

    ⛔ **That is the honest answer and it is why the notice exists.** The rules
    here bound shape, not inhabitation — ⭐ **so the population is printed, and
    a reader who sees `0 register rows` knows the verdict is about nothing.**
    """
    root = _tree(tmp_path, HEADER + FOOTER)
    assert check_board(root) == []
    assert "0 register rows, 0 live" in board_state(root)[0]


@pytest.mark.parametrize("state", ["✅ done — `abc1234`", "done", "DONE at `abc1234`"])
def test_a_closed_row_never_wants_a_detail_file(tmp_path: Path, state: str) -> None:
    """⭐ The other direction of `board-detail`, and it is the one that regresses.

    ⛔ A rule that only fired on a missing file would let every closed row keep
    an editable argument, which is the state `BOARD-ARCHIVE.md` exists to
    prevent.
    """
    row = f"| W1 | a naming | PO | {state} | [record](BOARD-ARCHIVE.md#w1) |\n"
    assert check_board(_tree(tmp_path / "without", HEADER + row + FOOTER)) == []
    with_file = _tree(tmp_path / "with", HEADER + row + FOOTER, rows=("W1",))
    assert _rules(check_board(with_file)) == [RULE_ORPHAN]


def test_a_multi_id_row_is_one_row_and_one_file(tmp_path: Path) -> None:
    """⚠️ `W17 + W19` are one commit, ruled, and therefore one row.

    ⛔ **The first id owns the file and the rest ride with it**, so a register
    that carries them as one does not owe two files — and a check that demanded
    two would push the PO into splitting a row the CTO fused.
    """
    row = "| W17 + W19 | a naming | PO | `todo` | [rows/W17.md](rows/W17.md) |\n"
    assert check_board(_tree(tmp_path, HEADER + row + FOOTER, rows=("W17",))) == []


# --------------------------------------------------------------------------
# `board-frame` — the live-tree guarantee Ruling 180 would otherwise have cost
# --------------------------------------------------------------------------


def test_a_row_file_that_lost_its_frame_is_a_finding(tmp_path: Path) -> None:
    """⛔ The one live-tree property left after Ruling 180, and why it is that one.

    ⚠️ **`test_migration.py`'s subject is now the migration's OUTPUT ref**, which
    is right — a migration is a claim about refs — ⛔ **but it means nothing was
    left watching a live row file at all.**

    ⭐ **A frame survives every amendment**, because amending a row means adding
    to its argument and never removing its identity — ⛔ **so this is the one
    thing that can be required of a file the PO is told to edit freely.**
    """
    root = _tree(tmp_path, HEADER + LIVE + FOOTER, rows=("W2",))
    assert check_board(root) == []
    (root / ROWS / "W2.md").write_text("a fragment with no frame at all\n", encoding="utf-8")
    assert _rules(check_board(root)) == [RULE_FRAME]


def test_appending_to_a_row_file_is_always_clean(tmp_path: Path) -> None:
    """⭐ The contract's own action — *"editing it is the point"* — stays green.

    ⛔ **This is the assertion `CTO-46/1` was about.** ⚠️ A test that reddened on
    an ordinary amendment would be a gate people edit their way around, and
    *"a checker people rename fields around is a checker on its way to being
    switched off"* is this branch's own sentence.
    """
    root = _tree(tmp_path, HEADER + LIVE + FOOTER, rows=("W2",))
    path = root / ROWS / "W2.md"
    path.write_text(path.read_text(encoding="utf-8") + "\n⛔ **Re-scoped.**\n", encoding="utf-8")
    assert check_board(root) == []


def test_a_row_file_named_for_a_different_row_is_a_finding(tmp_path: Path) -> None:
    """⚠️ The frame names its own id, so a copied file cannot pass as a new one."""
    root = _tree(tmp_path, HEADER + LIVE + FOOTER, rows=("W2",))
    (root / ROWS / "W2.md").write_text(_row("W9"), encoding="utf-8")
    assert _rules(check_board(root)) == [RULE_FRAME]


# --------------------------------------------------------------------------
# ⛔ `CTO-47/4` — the `board-frame` message describes the PREDICATE
# --------------------------------------------------------------------------


def test_the_frame_finding_states_what_is_CHECKED_not_what_is_hoped(tmp_path: Path) -> None:
    """⛔ `CTO-47/4`: the predicate is two substrings; the message claimed more.

    ⚠️ **It said the file *"states which row it argues…"*** — ⛔ **which
    `startswith` and `in` cannot read.** ⭐ **The weak predicate is the RIGHT trade
    for amendment-proofness** — ⛔ **a message describing a check nobody wrote sends
    the next reader to debug the wrong claim.**
    """
    root = _tree(tmp_path, HEADER + LIVE + FOOTER, rows=("W2",))
    (root / ROWS / "W2.md").write_text("a fragment with no frame at all\n", encoding="utf-8")
    findings = check_board(root)
    assert _rules(findings) == [RULE_FRAME]
    message = findings[0].message
    assert "`# W2`" in message, "the message names the first substring"
    assert repr(ROW_FRAME) in message, "and the second one, verbatim"
    assert "TWO SUBSTRINGS" in message, "and says that is the whole of it"


# --------------------------------------------------------------------------
# ⛔ `CTO-47/5` — `board-state`'s FINDING path, which had no reading at all
# --------------------------------------------------------------------------


def test_live_no_register_row_on_this_board_is_board_state() -> None:
    """⭐ The LIVE reading. ⛔ `RULE_STATE` was the one code with no test of its path.

    ⚠️ **Ruling 152's reachability held, so this was a test gap, not a missing
    guard.** ⭐ The population is read out beside the verdict (Ruling 48).
    """
    root = repository_root()
    assert [f for f in check_board(root) if f.rule == RULE_STATE] == []
    assert int(board_state(root)[0].split("board: ")[1].split(" register")[0]) > 0


@pytest.mark.parametrize(
    "cell",
    [
        "after `W44` is done",
        "DONE-ish — merged `abc1234`",
        "→ folded into `SF-10`",
        "◐ spec text landed; the asserting test is owed",
    ],
)
def test_planted_a_state_cell_that_declares_nothing_is_board_state(
    tmp_path: Path, cell: str
) -> None:
    """⛔ The PLANTED reading, adversarial to the SEARCH TERM (Ruling 140).

    ⚠️ **Each wears the word the first `is_closed` searched for, in a form the
    clause did not picture** — including `W5`'s and `W16`'s real shapes, which
    declare nothing. ⭐ **`DONE-ish` came from the impossible plant.**
    """
    row = f"| W2 | a naming | PO | {cell} | [d](rows/W2.md) |\n"
    root = _tree(tmp_path, HEADER + row + FOOTER, rows=("W2",))
    findings = check_board(root)
    assert _rules(findings) == [RULE_STATE]
    assert "declares no state" in findings[0].message
    assert "W2" in findings[0].message


def test_the_cell_that_walked_out_of_the_register_is_LIVE_and_owes_a_FILE(
    tmp_path: Path,
) -> None:
    """⛔ The defect's own cell, and the finding the substring test silently lost.

    ⚠️ **`` `todo` — after `W44` is done ``** read as CLOSED: no detail file owed,
    out of the bijection, floor green. ⭐ **It DECLARES `todo`**, so the mention is
    ambiguous and the declaration is not.
    """
    row = "| W2 | a naming | PO | `todo` — after `W44` is done | [d](rows/W2.md) |\n"
    root = _tree(tmp_path, HEADER + row + FOOTER)
    rules = _rules(check_board(root))
    assert RULE_STATE not in rules, "it declares todo; only the mention is loose"
    assert rules == [RULE_DETAIL], "⛔ the finding a substring test lost in silence"


@pytest.mark.parametrize("declared", sorted(STATES))
def test_a_cell_that_DECLARES_a_state_is_never_board_state(tmp_path: Path, declared: str) -> None:
    """⭐ Every word of the closed vocabulary, derived rather than retyped.

    ⛔ **Parametrised over `STATES` itself**, so a word added to the vocabulary
    joins this population without the test being edited and an EMPTY vocabulary
    skips rather than passing (Ruling 48).
    """
    row = f"| W2 | a naming | PO | ⛔ **{declared}** — `abc1234` | [d](rows/W2.md) |\n"
    root = _tree(tmp_path, HEADER + row + FOOTER, rows=("W2",))
    assert RULE_STATE not in _rules(check_board(root))


def test_impossible_board_state_cannot_fire_on_an_EMPTY_register(tmp_path: Path) -> None:
    """⛔ The IMPOSSIBLE reading, and it DIFFERS from the pass by naming `0`.

    ⭐ A register with no rows has no cell to judge, so silence here is correct —
    ⚠️ **and `0 = 0` is not a pass**, which is why the population is read out of
    the notice in the same assertion.
    """
    root = _tree(tmp_path, HEADER + FOOTER)
    assert [f for f in check_board(root) if f.rule == RULE_STATE] == []
    assert "0 register rows, 0 live" in board_state(root)[0]
