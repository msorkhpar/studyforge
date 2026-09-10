"""Mirror of `tools/quality/board.py` (R12), and the instrument's three readings.

⛔ **Ruling 122: a clause naming an instrument is not final until its author has
RUN it, in BOTH directions, and recorded both readings.** ⭐ **Ruling 123 names
the three: LIVE, PLANTED and IMPOSSIBLE**, and all three are here as tests
rather than as a paragraph in a handoff, because a reading recorded in prose is
one nobody can re-take.

| Reading | What it asserts | Where |
|---|---|---|
| **live** | the real `BOARD.md` here is clean under all five rules |
  `test_live_board_is_clean` |
| **planted** | each rule fires on a board built to break exactly it | the five `test_planted_*` |
| **impossible** | a state the rule cannot reach reports nothing, and
  absence is not a pass | `test_impossible_*` |

## ⚠️ The plant is adversarial to the SEARCH TERM, not to the subject (Ruling 140)

⛔ **A narrative governor's evasion is not more prose; it is prose written as a
table**, so that a byte count scoped to non-table lines reads it as rows.
⭐ **`test_planted_narrative_disguised_as_a_table` is that exact move**, and it
is the reading that decides whether the pair of bounds has a gap.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support import repository_root
from tools.quality.board import (
    BOARD,
    BOARD_FRAME,
    BOARD_NARRATIVE_CEILING,
    BOARD_PER_ROW,
    BOARD_ROW_CEILING,
    REGISTER_CLOSE,
    REGISTER_OPEN,
    ROWS,
    RULE_DETAIL,
    RULE_DUPLICATE,
    RULE_FRAME,
    RULE_NARRATIVE,
    RULE_ORPHAN,
    RULE_SIZE,
    RULE_WIDTH,
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


def test_planted_narrative(tmp_path: Path) -> None:
    prose = "x" * (BOARD_NARRATIVE_CEILING + 1) + "\n"
    root = _tree(tmp_path, prose + HEADER + CLOSED + FOOTER)
    assert _rules(check_board(root)) == [RULE_NARRATIVE]


def test_planted_narrative_disguised_as_a_table(tmp_path: Path) -> None:
    """⛔ Ruling 140 — the plant is adversarial to the SEARCH TERM.

    ⚠️ A round's narrative written as `| … |` lines contributes **zero** to the
    narrative count. ⭐ **`board-row-width` is what closes that gap**, and this
    is the reading that proves the two bounds have none between them.
    """
    fat = "| " + "x" * (BOARD_ROW_CEILING + 1) + " |\n"
    root = _tree(tmp_path, HEADER + CLOSED + FOOTER + fat)
    rules = _rules(check_board(root))
    assert RULE_NARRATIVE not in rules, "the narrative bound is blind to this, by construction"
    assert rules == [RULE_WIDTH]


def test_planted_narrative_as_MANY_SHORT_table_rows(tmp_path: Path) -> None:
    """⛔ The plant that GOT THROUGH, and the reason `board-size` exists.

    ⚠️ **Run against the first two bounds before this module shipped: 320 lines
    of round 33's narrative, one line per table row, moved the narrative
    reading by ZERO and tripped the width rule ONCE.** ⭐ Neither bound sees
    text that is short per line and enormous in total.

    ⛔ **`board-size` does, because the evasion raises the numerator and leaves
    the denominator alone.**
    """
    prose = "".join(f"| a line of a round's reasoning, number {n} |\n" for n in range(400))
    root = _tree(tmp_path, HEADER + CLOSED + FOOTER + prose)
    rules = _rules(check_board(root))
    assert RULE_NARRATIVE not in rules
    assert RULE_WIDTH not in rules
    assert rules == [RULE_SIZE]


def test_more_rows_can_never_trip_the_size_bound(tmp_path: Path) -> None:
    """⭐ Ruling 149's failure mode, asserted absent rather than argued absent.

    ⛔ **The line-count governor it retired *"alarmed seven times while the
    property improved seven times"*.** ⚠️ **A ratio cannot do that only if a row
    raises the allowance by MORE than a row costs** — so that is what is
    measured here, at a row width well over this board's live mean of 170 B.
    """
    row = "| W{n} | " + "n" * (BOARD_PER_ROW - 60) + " | PO | `todo` | [d](rows/W{n}.md) |\n"
    many = "".join(row.format(n=100 + i) for i in range(400))
    root = _tree(tmp_path, HEADER + many + FOOTER, rows=tuple(f"W{100 + i}" for i in range(400)))
    assert RULE_SIZE not in _rules(check_board(root))


def test_the_size_bound_allows_the_frame_and_says_so(tmp_path: Path) -> None:
    """⚠️ A board with NO rows still gets `BOARD_FRAME`, and nothing more."""
    root = _tree(tmp_path, HEADER + FOOTER + "x" * (BOARD_FRAME + 1))
    assert _rules(check_board(root)) == [RULE_NARRATIVE, RULE_SIZE]


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
