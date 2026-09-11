"""Mirror of `tools/quality/board/bounds.py` (R12) — the three bounds, each planted alone.

⛔ **These readings MOVED here from `test_init.py` with the code they measure** (`W100`'s
split), and they moved rather than being copied: ⭐ **a fixture or a reading with two homes
is the defect this package's own instrument exists to forbid, one layer up.**

⚠️ **They also got SHARPER in the move.** ⛔ **They used to run through `check_board`, so
each had to build a register whose bijection was satisfied** — row files on disk, 400 of
them in one case — ⭐ **where `size_findings(text)` is a pure function of the board's TEXT
and can be asked the question directly.** ⚠️ **The composition is asserted separately and
once**, below, because *the arm works* and *the arm is wired in* are two claims.
"""

from __future__ import annotations

from pathlib import Path

from tools.quality.board import (
    BOARD,
    BOARD_FRAME,
    BOARD_NARRATIVE_CEILING,
    BOARD_PER_ROW,
    BOARD_ROW_CEILING,
    RULE_NARRATIVE,
    RULE_SIZE,
    RULE_WIDTH,
    check_board,
)
from tools.quality.board.bounds import size_findings
from tools.quality.report import Finding

from .support import REGISTER, REGISTER_END, rules

#: One closed register row, so the register is INHABITED: ⛔ `board-size`'s denominator is
#: the ids the register names, and a bound measured against an empty register would be
#: measuring the frame alone.
CLOSED = "| W1 | a naming | PO | ✅ done — `abc1234` | [record](BOARD-ARCHIVE.md#w1) |\n"


def _board(extra: str = "", register: str = CLOSED) -> str:
    """A board carrying `register` and then `extra`, with nothing else in it."""
    return f"# Board\n\n{REGISTER}{register}{REGISTER_END}{extra}"


def test_planted_narrative() -> None:
    """⛔ Prose outside every table, one byte over the ceiling."""
    prose = "x" * (BOARD_NARRATIVE_CEILING + 1) + "\n"
    findings = size_findings(_board(prose))
    assert rules(findings) == [RULE_NARRATIVE]
    assert str(BOARD_NARRATIVE_CEILING) in findings[0].message


def test_planted_narrative_disguised_as_a_table() -> None:
    """⛔ Ruling 140 — the plant is adversarial to the SEARCH TERM.

    ⚠️ A round's narrative written as `| … |` lines contributes **zero** to the narrative
    count. ⭐ **`board-row-width` is what closes that gap**, and this is the reading that
    proves the two bounds have none between them.
    """
    fat = "| " + "x" * (BOARD_ROW_CEILING + 1) + " |\n"
    found = rules(size_findings(_board(fat)))
    assert RULE_NARRATIVE not in found, "the narrative bound is blind to this, by construction"
    assert found == [RULE_WIDTH]


def test_planted_narrative_as_MANY_SHORT_table_rows() -> None:
    """⛔ The plant that GOT THROUGH, and the reason `board-size` exists.

    ⚠️ **Run against the first two bounds before this module shipped: 320 lines of round
    33's narrative, one line per table row, moved the narrative reading by ZERO and
    tripped the width rule ONCE.** ⭐ Neither bound sees text that is short per line and
    enormous in total.

    ⛔ **`board-size` does, because the evasion raises the numerator and leaves the
    denominator alone.**
    """
    prose = "".join(f"| a line of a round's reasoning, number {n} |\n" for n in range(400))
    found = rules(size_findings(_board(prose)))
    assert RULE_NARRATIVE not in found
    assert RULE_WIDTH not in found
    assert found == [RULE_SIZE]


def test_more_rows_can_never_trip_the_size_bound() -> None:
    """⭐ Ruling 149's failure mode, asserted absent rather than argued absent.

    ⛔ **The line-count governor it retired *"alarmed seven times while the property
    improved seven times"*.** ⚠️ **A ratio cannot do that only if a row raises the
    allowance by MORE than a row costs** — so that is what is measured here, at a row
    width well over this board's live mean of 170 B.
    """
    row = "| W{n} | " + "n" * (BOARD_PER_ROW - 60) + " | PO | `todo` | [d](rows/W{n}.md) |\n"
    many = "".join(row.format(n=100 + i) for i in range(400))
    assert RULE_SIZE not in rules(size_findings(_board(register=many)))


def test_the_size_bound_allows_the_frame_and_says_so() -> None:
    """⚠️ A board with NO register row still gets `BOARD_FRAME`, and nothing more."""
    found = size_findings(_board("x" * (BOARD_FRAME + 1), register=""))
    assert rules(found) == [RULE_NARRATIVE, RULE_SIZE]
    assert f"{BOARD_FRAME} of frame plus {BOARD_PER_ROW} for each of 0 register rows" in (
        next(finding.message for finding in found if finding.rule == RULE_SIZE)
    )


def test_the_denominator_is_the_IDS_the_register_NAMES_and_not_the_rows_it_carries() -> None:
    """⛔ `W17 + W19` are ONE register row naming TWO ids, and the allowance follows the IDS.

    ⚠️ **The arm used to be handed a count computed by `check_board`'s own loop**, and a
    second reading of one population is two readings that can disagree — ⭐ **so it
    derives the set itself, and this is the row that would have caught a drift.**
    """
    two = "| W17 + W19 | one commit, two ids | PO | `todo` | [d](rows/W17.md) |\n"
    over = BOARD_FRAME + 2 * BOARD_PER_ROW + 1
    findings = size_findings(_board("x" * over, register=two))
    assert "for each of 2 register rows" in (
        next(finding.message for finding in findings if finding.rule == RULE_SIZE)
    )


def test_the_bounds_arm_is_WIRED_INTO_check_board(tmp_path: Path) -> None:
    """⭐ *The arm works* and *the arm is called* are two claims, and this is the second.

    ⛔ **Asserted through the real entry point over a real tree**, because the split moved
    the code out of `check_board`'s own body and a `findings.extend` that was never added
    would leave every reading above green and the floor blind.
    """
    (tmp_path / "docs" / "tasks").mkdir(parents=True)
    (tmp_path / BOARD).write_text(_board("x" * (BOARD_NARRATIVE_CEILING + 1)), encoding="utf-8")
    found: list[Finding] = check_board(tmp_path)
    assert RULE_NARRATIVE in rules(found)
